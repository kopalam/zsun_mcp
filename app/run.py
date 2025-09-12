"""Main FastMCP API service framework server."""

import argparse
import asyncio
import logging
import os
import sys
import json
import signal
from typing import Any, Dict
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Try to import uvloop for better performance
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

from plugins import weather_plugin
from core.connection_manager import connection_manager
from handlers.websocket_handler import websocket_handler
from utils.jsonrpc import JSONRPCProtocol

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FastMCPAPIServer:
    """Main FastMCP API server that manages plugins and provides MCP services."""

    def __init__(self, host: str = "0.0.0.0", port: int = 7100):
        """Initialize the server.
        
        Args:
            host: Host to bind the server to.
            port: Port to bind the server to.
        """
        self.host = host
        self.port = port
        self.app = FastMCP("FastMCP API Server")
        self.plugins = []
        self.server_key = os.getenv("SERVER_KEY", "default_key_123456")
        logger.info(f"Server key: {self.server_key}")
        # Register plugins
        self._register_plugins()
        
        # 初始化WebSocket处理器并传递MCP服务器
        websocket_handler.mcp_server = self.app

    def _register_plugins(self):
        """Register all available plugins with the MCP server."""
        logger.info("Registering plugins...")
        
        # Register weather plugin
        self._register_plugin(weather_plugin)
        
        logger.info(f"Registered {len(self.plugins)} plugins")

    def _register_plugin(self, plugin):
        """Register a single plugin with the MCP server.
        
        Args:
            plugin: Plugin instance to register.
        """
        try:
            # Check if plugin uses MCPMixin
            from fastmcp.contrib.mcp_mixin import MCPMixin
            if isinstance(plugin, MCPMixin):
                # Use MCPMixin registration
                plugin.register_tools(self.app)
                registered_count = len(plugin._get_methods_to_register("_mcp_tool_registration"))
                logger.info(f"Registered {registered_count} tools from MCPMixin plugin: {plugin.name}")
            else:
                # Use traditional tools() method
                tools = plugin.tools()
                registered_count = 0
                
                for tool in tools:
                    # Register the tool with the MCP server
                    self.app.tool(tool)
                    registered_count += 1
                    logger.info(f"Registered tool: {tool.__name__} from plugin: {plugin.name}")
            
            self.plugins.append(plugin)
            logger.info(f"Successfully registered plugin '{plugin.name}' with {registered_count} tools")
            
        except Exception as e:
            logger.error(f"Failed to register plugin '{plugin.name}': {str(e)}")

    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about the server and registered tools.
        
        Returns:
            Dictionary containing server information.
        """
        try:
            tools = await self.app.get_tools()
            resources = await self.app.get_resources()
            
            return {
                "server_name": "FastMCP API Server",
                "version": "1.0.0",
                "host": self.host,
                "port": self.port,
                "plugins": [plugin.name for plugin in self.plugins],
                "tools": list(tools.keys()),
                "resources": list(resources.keys()),
                "tool_count": len(tools),
                "resource_count": len(resources)
            }
        except Exception as e:
            logger.error(f"Error getting server info: {str(e)}")
            return {"error": str(e)}

    async def print_server_info(self):
        """Print server information to console."""
        info = await self.get_server_info()
        
        print("\n" + "="*60)
        print("FastMCP API Server Information")
        print("="*60)
        print(f"Server: {info.get('server_name', 'Unknown')}")
        print(f"Version: {info.get('version', 'Unknown')}")
        print(f"Host: {info.get('host', 'Unknown')}")
        print(f"Port: {info.get('port', 'Unknown')}")
        print(f"Plugins: {', '.join(info.get('plugins', []))}")
        print(f"Tools: {info.get('tool_count', 0)}")
        print(f"Resources: {info.get('resource_count', 0)}")
        
        if info.get('tools'):
            print("\nRegistered Tools:")
            for tool_name in info['tools']:
                print(f"  - {tool_name}")
        
        if info.get('resources'):
            print("\nRegistered Resources:")
            for resource_uri in info['resources']:
                print(f"  - {resource_uri}")
        
        print("="*60)
        print(f"Server starting on http://{self.host}:{self.port}")
        print(f"SSE endpoint: http://{self.host}:{self.port}/sse")
        print("="*60 + "\n")

    def run_sse(self):
        """Run the server with SSE transport."""
        logger.info(f"Starting FastMCP server with SSE transport on {self.host}:{self.port}")
        
        # Print server information
        asyncio.run(self.print_server_info())
        
        # Start the server
        self.app.run(host=self.host, port=self.port, transport="sse")

    def run_stdio(self):
        """Run the server with stdio transport."""
        logger.info("Starting FastMCP server with stdio transport")
        
        # Print server information
        asyncio.run(self.print_server_info())
        
        # Start the server
        self.app.run(transport="stdio")

    def run_websocket(self):
        """Run the server with WebSocket transport."""
        logger.info(f"Starting FastMCP server with WebSocket transport on {self.host}:{self.port}")
        
        # Print server information
        asyncio.run(self.print_server_info())
        
        # Create FastAPI app with WebSocket endpoints
        app = FastAPI(title="FastMCP WebSocket Server")
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add WebSocket endpoints - 支持MCP协议标准路径
        @app.websocket("/mcp_endpoint/mcp/")
        async def websocket_tool_endpoint(websocket: WebSocket):
            await self.websocket_tool_endpoint(websocket)
        
        @app.websocket("/mcp_endpoint/call/")
        async def websocket_robot_endpoint(websocket: WebSocket):
            await self.websocket_robot_endpoint(websocket)
        
        # Add MCP protocol endpoint - 符合MCP 2024-11-05协议标准
        @app.websocket("/mcp_endpoint/protocol/")
        async def websocket_mcp_protocol_endpoint(websocket: WebSocket):
            await self.websocket_mcp_protocol_endpoint(websocket)
        
        # Add health check endpoint
        @app.get("/mcp_endpoint/health")
        async def health_check():
            stats = connection_manager.get_connection_stats()
            response = JSONRPCProtocol.create_success_response(
                result={"status": "success", "connections": stats}
            )
            return JSONRPCProtocol.to_dict(response)
        
        # Add root endpoint
        @app.get("/")
        async def root():
            return {"message": "FastMCP WebSocket Server", "version": "1.0.0"}
        
        # Start the server
        import uvicorn
        uvicorn.run(app, host=self.host, port=self.port)

    def run_dual_transport(self):
        """Run the server with both SSE and WebSocket transport."""
        logger.info(f"Starting FastMCP server with dual transport (SSE + WebSocket) on {self.host}:{self.port}")
        
        # Print server information
        asyncio.run(self.print_server_info())
        
        # Import required modules
        from starlette.routing import Route, WebSocketRoute
        from fastmcp.server.http import create_sse_app
        
        # Create custom routes for WebSocket and health check
        custom_routes = [
            WebSocketRoute("/mcp_endpoint/mcp/", self.websocket_tool_endpoint),
            WebSocketRoute("/mcp_endpoint/call/", self.websocket_robot_endpoint),
            Route("/mcp_endpoint/health", self.health_check_endpoint, methods=["GET"]),
            Route("/", self.root_endpoint, methods=["GET"]),
        ]
        
        # Create the FastMCP SSE app with custom routes
        sse_app = create_sse_app(
            server=self.app,
            message_path="/messages/",
            sse_path="/sse",
            routes=custom_routes
        )
        
        # Start the server with uvicorn
        import uvicorn
        uvicorn.run(sse_app, host=self.host, port=self.port)
    
    async def health_check_endpoint(self, request):
        """Health check endpoint for dual transport."""
        from starlette.responses import JSONResponse
        stats = connection_manager.get_connection_stats()
        response = JSONRPCProtocol.create_success_response(
            result={"status": "success", "transports": ["sse", "websocket"], "connections": stats}
        )
        return JSONResponse(JSONRPCProtocol.to_dict(response))
    
    async def root_endpoint(self, request):
        """Root endpoint for dual transport."""
        from starlette.responses import JSONResponse
        return JSONResponse({"message": "FastMCP Dual Transport Server", "version": "1.0.0", "transports": ["sse", "websocket"]})

    async def cleanup(self):
        """Cleanup resources when shutting down."""
        logger.info("Cleaning up server resources...")
        
        for plugin in self.plugins:
            if hasattr(plugin, 'close'):
                try:
                    await plugin.close()
                except Exception as e:
                    logger.error(f"Error closing plugin {plugin.name}: {str(e)}")
        
        logger.info("Server cleanup completed")

    async def validate_token_and_get_agent_id(self, websocket: WebSocket) -> str:
        """验证token并获取agentId的公共方法"""
        token = websocket.query_params.get("token")
        if not token:
            logger.error("缺少token参数")
            await websocket.close(code=1008, reason="缺少token参数")
            return None

        # 简单的token验证（实际项目中应该使用更安全的加密方式）
        try:
            # 处理URL编码问题：将空格转换回加号
            # 在URL中，+会被解释为空格，所以我们需要将其转换回来
            decoded_token = token.replace(' ', '+')
            
            if decoded_token == self.server_key:
                return "default_agent"
            else:
                logger.error(f"token验证失败: {token} (decoded: {decoded_token})-------------{self.server_key}")
                await websocket.close(code=1008, reason="token验证失败")
                return None
        except Exception as e:
            logger.error(f"token验证异常: {e}")
            await websocket.close(code=1008, reason="token验证异常")
            return None

    async def websocket_tool_endpoint(self, websocket: WebSocket):
        """工具端WebSocket端点"""
        logger.info("🔌 WebSocket工具端端点被调用")
        await websocket.accept()
        logger.info("✅ WebSocket连接已接受")

        # 获取agentId参数
        agent_id = await self.validate_token_and_get_agent_id(websocket)
        if not agent_id:
            logger.error("❌ 无法获取agentId，关闭连接")
            return

        try:
            # 注册连接
            await connection_manager.register_tool_connection(agent_id, websocket)
            logger.info(f"工具端连接已建立: {agent_id}")

            # 处理消息
            while True:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"工具端收到原始消息: {message}")
                    await websocket_handler._handle_tool_message(agent_id, message, websocket)
                except WebSocketDisconnect:
                    logger.info("🔌 WebSocket连接断开")
                    break
                except Exception as e:
                    logger.error(f"处理工具端消息时发生错误: {e}")
                    import traceback
                    logger.error(f"异常详情: {traceback.format_exc()}")
                    break

        except Exception as e:
            logger.error(f"处理工具端连接时发生错误: {e}")
        finally:
            await connection_manager.unregister_tool_connection(agent_id)
            logger.info(f"工具端连接已关闭: {agent_id}")

    async def websocket_robot_endpoint(self, websocket: WebSocket):
        """小智端WebSocket端点"""
        await websocket.accept()

        # 获取agentId参数
        agent_id = await self.validate_token_and_get_agent_id(websocket)
        if not agent_id:
            return

        try:
            # 注册连接并获取UUID
            connection_uuid = await connection_manager.register_robot_connection(
                agent_id, websocket
            )
            logger.info(f"小智端连接已建立: {agent_id} (UUID: {connection_uuid})")

            # 处理消息
            while True:
                try:
                    message = await websocket.receive_text()
                    await websocket_handler._handle_robot_message(
                        agent_id, message, connection_uuid, websocket
                    )
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"处理小智端消息时发生错误: {e}")
                    break

        except Exception as e:
            logger.error(f"处理小智端连接时发生错误: {e}")
        finally:
            await connection_manager.unregister_robot_connection(connection_uuid)
            logger.info(f"小智端连接已关闭: {agent_id} (UUID: {connection_uuid})")

    async def websocket_mcp_protocol_endpoint(self, websocket: WebSocket):
        """MCP协议WebSocket端点 - 符合MCP 2024-11-05协议标准"""
        logger.info("🔌 MCP协议WebSocket端点被调用")
        await websocket.accept()
        logger.info("✅ MCP协议WebSocket连接已接受")

        try:
            # 处理MCP协议消息，支持10秒超时
            while True:
                try:
                    # 设置10秒超时接收消息
                    message = await asyncio.wait_for(
                        websocket.receive_text(), 
                        timeout=10.0
                    )
                    logger.info(f"收到MCP协议消息: {message}")
                    
                    # 解析JSON-RPC消息
                    try:
                        message_data = json.loads(message)
                    except json.JSONDecodeError as e:
                        logger.error(f"MCP协议消息JSON解析失败: {e}")
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": "Parse error"
                            }
                        }
                        await websocket.send_text(json.dumps(error_response))
                        continue
                    
                    # 处理MCP请求，设置10秒超时
                    try:
                        response = await asyncio.wait_for(
                            websocket_handler._handle_mcp_request(message_data),
                            timeout=10.0
                        )
                        
                        # 发送响应（如果有的话）
                        if response is not None:
                            logger.info(f"发送MCP协议响应: {json.dumps(response, ensure_ascii=False)}")
                            await websocket.send_text(json.dumps(response, ensure_ascii=False))
                        else:
                            logger.info("MCP协议请求不需要响应（通知类型）")
                            
                    except asyncio.TimeoutError:
                        logger.error("MCP请求处理超时（10秒）")
                        # 发送超时错误响应
                        timeout_response = {
                            "jsonrpc": "2.0",
                            "id": message_data.get("id"),
                            "error": {
                                "code": -32603,
                                "message": "Internal error",
                                "data": {"detail": "Request timeout after 10 seconds"}
                            }
                        }
                        await websocket.send_text(json.dumps(timeout_response, ensure_ascii=False))
                        
                except asyncio.TimeoutError:
                    logger.warning("WebSocket消息接收超时（10秒），保持连接")
                    continue
                except WebSocketDisconnect:
                    logger.info("MCP协议WebSocket连接已断开")
                    break
                except Exception as e:
                    logger.error(f"处理MCP协议消息时发生错误: {e}")
                    # 发送错误响应
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message_data.get("id") if 'message_data' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": str(e)}
                        }
                    }
                    await websocket.send_text(json.dumps(error_response))
                    
        except Exception as e:
            logger.error(f"处理MCP协议连接时发生错误: {e}")
        finally:
            logger.info("MCP协议WebSocket连接已关闭")


def main():
    """Main entry point for the FastMCP API server."""
    parser = argparse.ArgumentParser(description="FastMCP API Server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio", "websocket", "dual"],
        default="sse",
        help="Transport method to use (default: sse)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7100,
        help="Port to bind the server to (default: 7100)"
    )
    
    args = parser.parse_args()
    
    # Use uvloop on non-Windows platforms for better performance
    if sys.platform != "win32" and UVLOOP_AVAILABLE:
        try:
            uvloop.install()
            logger.info("Using uvloop for better async performance")
        except Exception as e:
            logger.warning(f"Failed to install uvloop: {e}, using default event loop")
    elif not UVLOOP_AVAILABLE:
        logger.info("uvloop not available, using default event loop")
    
    # Create and run server
    server = FastMCPAPIServer(host=args.host, port=args.port)
    
    try:
        if args.transport == "websocket":
            server.run_websocket()
        elif args.transport == "sse":
            server.run_sse()
        elif args.transport == "dual":
            server.run_dual_transport()
        else:
            server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        asyncio.run(server.cleanup())


if __name__ == "__main__":
    main()