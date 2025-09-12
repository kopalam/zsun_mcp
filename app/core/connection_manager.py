"""
WebSocket连接管理器
管理工具端和小智端的WebSocket连接，与mcp-endpoint-server保持兼容
"""

import json
import uuid
from typing import Dict, Optional, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 工具端连接: agent_id -> websocket
        self.tool_connections: Dict[str, WebSocket] = {}
        
        # 小智端连接: connection_uuid -> (agent_id, websocket)
        self.robot_connections: Dict[str, tuple[str, WebSocket]] = {}
        
        # JSON-RPC ID映射: original_id -> (connection_uuid, transformed_id)
        self.id_mapping: Dict[str, tuple[str, str]] = {}

    async def register_tool_connection(self, agent_id: str, websocket: WebSocket) -> bool:
        """注册工具端连接"""
        try:
            # 如果已存在连接，先关闭旧连接
            if agent_id in self.tool_connections:
                old_websocket = self.tool_connections[agent_id]
                try:
                    await old_websocket.close()
                except Exception as e:
                    logger.warning(f"关闭旧工具端连接时出错: {e}")
            
            self.tool_connections[agent_id] = websocket
            logger.info(f"工具端连接已注册: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"注册工具端连接失败: {e}")
            return False

    async def unregister_tool_connection(self, agent_id: str) -> bool:
        """注销工具端连接"""
        try:
            if agent_id in self.tool_connections:
                del self.tool_connections[agent_id]
                logger.info(f"工具端连接已注销: {agent_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"注销工具端连接失败: {e}")
            return False

    async def register_robot_connection(self, agent_id: str, websocket: WebSocket) -> str:
        """注册小智端连接并返回UUID"""
        try:
            connection_uuid = str(uuid.uuid4())
            self.robot_connections[connection_uuid] = (agent_id, websocket)
            logger.info(f"小智端连接已注册: {agent_id} (UUID: {connection_uuid})")
            return connection_uuid
        except Exception as e:
            logger.error(f"注册小智端连接失败: {e}")
            return ""

    async def unregister_robot_connection(self, connection_uuid: str) -> bool:
        """注销小智端连接"""
        try:
            if connection_uuid in self.robot_connections:
                agent_id, _ = self.robot_connections[connection_uuid]
                del self.robot_connections[connection_uuid]
                
                # 清理相关的ID映射
                self._cleanup_id_mapping(connection_uuid)
                
                logger.info(f"小智端连接已注销: {agent_id} (UUID: {connection_uuid})")
                return True
            return False
        except Exception as e:
            logger.error(f"注销小智端连接失败: {e}")
            return False

    def is_tool_connected(self, agent_id: str) -> bool:
        """检查工具端是否已连接"""
        return agent_id in self.tool_connections

    async def forward_to_tool(self, agent_id: str, message: str) -> bool:
        """转发消息给工具端"""
        try:
            if agent_id not in self.tool_connections:
                logger.warning(f"工具端未连接: {agent_id}")
                return False
            
            websocket = self.tool_connections[agent_id]
            await websocket.send_text(message)
            logger.debug(f"消息已转发给工具端: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"转发消息给工具端失败: {e}")
            return False

    async def forward_to_robot_by_uuid(self, connection_uuid: str, message: str) -> bool:
        """根据UUID转发消息给小智端"""
        try:
            if connection_uuid not in self.robot_connections:
                logger.warning(f"小智端连接不存在: {connection_uuid}")
                return False
            
            _, websocket = self.robot_connections[connection_uuid]
            await websocket.send_text(message)
            logger.debug(f"消息已转发给小智端: {connection_uuid}")
            return True
        except Exception as e:
            logger.error(f"转发消息给小智端失败: {e}")
            return False

    def transform_jsonrpc_message(self, message_data: dict, connection_uuid: str) -> dict:
        """转换JSON-RPC消息ID以支持多连接"""
        try:
            if "id" not in message_data or message_data["id"] is None:
                return message_data
            
            original_id = str(message_data["id"])
            transformed_id = f"{connection_uuid}:{original_id}"
            
            # 保存ID映射
            self.id_mapping[transformed_id] = (connection_uuid, original_id)
            
            # 创建新的消息数据
            transformed_message = message_data.copy()
            transformed_message["id"] = transformed_id
            
            logger.debug(f"JSON-RPC ID已转换: {original_id} -> {transformed_id}")
            return transformed_message
        except Exception as e:
            logger.error(f"转换JSON-RPC消息失败: {e}")
            return message_data

    def restore_jsonrpc_message(self, message_data: dict) -> tuple[Optional[str], dict]:
        """还原JSON-RPC消息ID并获取目标连接UUID"""
        try:
            if "id" not in message_data or message_data["id"] is None:
                return None, message_data
            
            transformed_id = str(message_data["id"])
            
            if transformed_id not in self.id_mapping:
                logger.warning(f"未找到ID映射: {transformed_id}")
                return None, message_data
            
            connection_uuid, original_id = self.id_mapping[transformed_id]
            
            # 创建还原的消息数据
            restored_message = message_data.copy()
            restored_message["id"] = original_id
            
            # 清理ID映射
            del self.id_mapping[transformed_id]
            
            logger.debug(f"JSON-RPC ID已还原: {transformed_id} -> {original_id}")
            return connection_uuid, restored_message
        except Exception as e:
            logger.error(f"还原JSON-RPC消息失败: {e}")
            return None, message_data

    def _cleanup_id_mapping(self, connection_uuid: str):
        """清理指定连接的ID映射"""
        try:
            keys_to_remove = []
            for transformed_id, (uuid, _) in self.id_mapping.items():
                if uuid == connection_uuid:
                    keys_to_remove.append(transformed_id)
            
            for key in keys_to_remove:
                del self.id_mapping[key]
            
            if keys_to_remove:
                logger.debug(f"已清理 {len(keys_to_remove)} 个ID映射: {connection_uuid}")
        except Exception as e:
            logger.error(f"清理ID映射失败: {e}")

    def get_connection_stats(self) -> dict:
        """获取连接统计信息"""
        return {
            "tool_connections": len(self.tool_connections),
            "robot_connections": len(self.robot_connections),
            "id_mappings": len(self.id_mapping),
            "tool_agents": list(self.tool_connections.keys()),
            "robot_uuids": list(self.robot_connections.keys())
        }


# 全局连接管理器实例
connection_manager = ConnectionManager()
