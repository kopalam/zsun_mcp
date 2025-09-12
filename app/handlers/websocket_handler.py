"""
WebSocket处理器
处理工具端和小智端的WebSocket连接，与mcp-endpoint-server保持兼容
"""

import json
import logging
from typing import Optional, Union
from core.connection_manager import connection_manager
from utils.jsonrpc import (
    JSONRPCProtocol,
    create_tool_not_connected_error,
    create_forward_failed_error,
)

# 自定义JSON编码器来处理TextContent对象
class MCPJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """WebSocket处理器"""

    def __init__(self, mcp_server=None):
        self.mcp_server = mcp_server

    async def _handle_tool_message(self, agent_id: str, message: str):
        """处理工具端消息"""
        try:
            # 解析消息
            logger.info(f"收到工具端消息: {agent_id} - {message}")

            # 尝试解析JSON-RPC消息
            try:
                message_data = json.loads(message)
                
                # 检查是否是MCP协议请求
                logger.info(f"检查MCP请求: method={message_data.get('method')}, jsonrpc={message_data.get('jsonrpc')}")
                is_mcp = self._is_mcp_request(message_data)
                logger.info(f"MCP请求检查结果: {is_mcp}")
                
                if is_mcp:
                    logger.info("检测到MCP协议请求，直接处理")
                    # 直接处理MCP协议请求
                    response = await self._handle_mcp_request(message_data)
                    if response:
                        logger.info(f"发送MCP响应: {response}")
                        # 发送响应给工具端
                        await connection_manager.forward_to_tool(
                            agent_id, json.dumps(response, ensure_ascii=False, cls=MCPJSONEncoder)
                        )
                    return
                
                # 还原JSON-RPC ID并获取目标连接UUID
                connection_uuid, restored_message = (
                    connection_manager.restore_jsonrpc_message(message_data)
                )

                if connection_uuid:
                    # 有特定的目标连接，发送给该连接
                    success = await connection_manager.forward_to_robot_by_uuid(
                        connection_uuid, json.dumps(restored_message, ensure_ascii=False)
                    )
                    if not success:
                        logger.error(f"转发消息给特定小智端连接失败: {connection_uuid}")
                else:
                    logger.error(f"没有特定目标，无法转发消息")
            except json.JSONDecodeError:
                # 如果不是JSON格式，按原来的方式处理
                logger.error(f"由于消息不是JSON格式，已忽略: {message}")

        except json.JSONDecodeError:
            logger.error(f"工具端消息格式错误: {message}")
        except Exception as e:
            logger.error(f"处理工具端消息时发生错误: {e}")

    async def _handle_robot_message(
        self, agent_id: str, message: str, connection_uuid: str
    ):
        """处理小智端消息"""
        try:
            # 解析消息
            logger.debug(
                f"收到小智端消息: {agent_id} (UUID: {connection_uuid}) - {message}"
            )

            # 尝试解析JSON-RPC消息以获取id
            request_id = None
            transformed_message = message
            try:
                message_data = json.loads(message)
                request_id = message_data.get("id")

                # 转换JSON-RPC ID
                transformed_message_data = connection_manager.transform_jsonrpc_message(
                    message_data, connection_uuid
                )
                transformed_message = json.dumps(
                    transformed_message_data, ensure_ascii=False
                )

                logger.debug(
                    f"转换后的消息ID: {message_data.get('id')} -> {transformed_message_data.get('id')}"
                )

            except json.JSONDecodeError:
                logger.warning(f"小智端消息不是有效的JSON格式: {message}")
                # 如果消息不是JSON格式，仍然检查工具端连接状态

            # 检查是否有对应的工具端连接
            if not connection_manager.is_tool_connected(agent_id):
                logger.warning(f"工具端未连接: {agent_id}")
                # 发送JSON-RPC格式的错误消息给小智端
                error_message = create_tool_not_connected_error(request_id, agent_id)
                await connection_manager.forward_to_robot_by_uuid(
                    connection_uuid, error_message
                )
                return

            # 转发转换后的消息给工具端
            success = await connection_manager.forward_to_tool(
                agent_id, transformed_message
            )
            if not success:
                logger.error(f"转发消息给工具端失败: {agent_id}")
                # 发送JSON-RPC格式的错误消息给小智端
                error_message = create_forward_failed_error(request_id, agent_id)
                await connection_manager.forward_to_robot_by_uuid(
                    connection_uuid, error_message
                )

        except json.JSONDecodeError:
            logger.error(f"小智端消息格式错误: {message}")
        except Exception as e:
            logger.error(f"处理小智端消息时发生错误: {e}")

    def _is_mcp_request(self, message_data: dict) -> bool:
        """检查是否是MCP协议请求"""
        logger.info(f"检查MCP请求详情: {message_data}")
        
        if not isinstance(message_data, dict):
            logger.info("不是字典类型")
            return False
        
        # 检查JSON-RPC格式
        jsonrpc = message_data.get("jsonrpc")
        if jsonrpc != "2.0":
            logger.info(f"JSON-RPC版本不匹配: {jsonrpc}")
            return False
        
        method = message_data.get("method")
        if not method:
            logger.info("没有method字段")
            return False
        
        # 检查是否是MCP协议方法
        mcp_methods = [
            "tools/list",
            "tools/call", 
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get",
            "initialize",
            "notifications/initialized"
        ]
        
        is_mcp_method = method in mcp_methods
        logger.info(f"方法 {method} 是MCP方法: {is_mcp_method}")
        return is_mcp_method

    async def _handle_mcp_request(self, message_data: dict) -> Optional[dict]:
        """处理MCP协议请求"""
        if not self.mcp_server:
            logger.error("MCP服务器未初始化")
            return None
        
        try:
            method = message_data.get("method")
            request_id = message_data.get("id")
            params = message_data.get("params", {})
            
            logger.info(f"处理MCP请求: {method}")
            
            if method == "tools/list":
                # 获取工具列表
                logger.info("开始获取工具列表...")
                tools = await self.mcp_server._list_tools()
                logger.info(f"获取到 {len(tools)} 个工具")
                
                # 调试：检查工具管理器中的工具
                tool_manager_tools = await self.mcp_server._tool_manager.get_tools()
                logger.info(f"工具管理器中有 {len(tool_manager_tools)} 个工具: {list(tool_manager_tools.keys())}")
                
                mcp_tools = []
                for tool in tools:
                    mcp_tool = {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.parameters
                    }
                    mcp_tools.append(mcp_tool)
                    logger.info(f"工具: {tool.name} - {tool.description}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": mcp_tools
                    }
                }
            
            elif method == "tools/call":
                # 调用工具
                logger.info(f"处理工具调用请求: {method}")
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                logger.info(f"工具名称: {tool_name}, 参数: {arguments}")
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": {"detail": "Missing tool name"}
                        }
                    }
                
                try:
                    # 创建并设置上下文
                    from fastmcp.server.context import Context
                    context = Context(self.mcp_server)
                    
                    async with context:
                        result = await self.mcp_server._call_tool(tool_name, arguments)
                        mcp_result = result.to_mcp_result()
                    
                    # 处理MCP结果格式
                    if isinstance(mcp_result, tuple):
                        content, structured_content = mcp_result
                        # 将TextContent对象转换为可序列化的格式
                        serializable_content = []
                        if content:
                            for item in content:
                                if hasattr(item, 'model_dump'):
                                    serializable_content.append(item.model_dump())
                                elif hasattr(item, 'to_dict'):
                                    serializable_content.append(item.to_dict())
                                else:
                                    serializable_content.append(item)
                        response_result = {"content": serializable_content}
                        if structured_content:
                            response_result["structuredContent"] = structured_content
                    else:
                        # 处理单个结果
                        if hasattr(mcp_result, 'model_dump'):
                            response_result = {"content": [mcp_result.model_dump()]}
                        elif hasattr(mcp_result, 'to_dict'):
                            response_result = {"content": [mcp_result.to_dict()]}
                        else:
                            response_result = {"content": [mcp_result]}
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": response_result
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": str(e)}
                        }
                    }
            
            else:
                # 其他方法暂不支持
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": {"method": method}
                    }
                }
                
        except Exception as e:
            logger.error(f"处理MCP请求时发生错误: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"detail": str(e)}
                }
            }


# 全局WebSocket处理器实例
websocket_handler = WebSocketHandler()
