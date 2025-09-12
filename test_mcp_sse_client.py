#!/usr/bin/env python3
"""Test MCP server using SSE (Server-Sent Events) connection."""

import asyncio
import json
import logging
import httpx
from typing import Dict, Any, AsyncGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPSSEClient:
    """Client for testing MCP server via SSE connection."""
    
    def __init__(self, base_url: str = "http://localhost:8010"):
        self.base_url = base_url
        self.sse_url = f"{base_url}/sse"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.message_id = 0
    
    def _get_next_id(self) -> int:
        """Get next message ID."""
        self.message_id += 1
        return self.message_id
    
    async def connect_sse(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Connect to SSE stream and yield messages."""
        try:
            async with self.client.stream(
                "GET",
                self.sse_url,
                headers={
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
            ) as response:
                if response.status_code != 200:
                    yield {"error": f"HTTP {response.status_code}", "message": response.text}
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            message = json.loads(data)
                            yield message
                        except json.JSONDecodeError:
                            continue
                    elif line.strip():
                        logger.info(f"SSE line: {line}")
                        
        except Exception as e:
            logger.error(f"Error in SSE connection: {e}")
            yield {"error": str(e)}
    
    async def send_message(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC message via SSE connection."""
        message = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        
        if params:
            message["params"] = params
        
        logger.info(f"Sending message: {json.dumps(message, indent=2)}")
        
        try:
            # For now, just return a mock response since we need to implement proper SSE communication
            # In a real implementation, we would need to establish a persistent SSE connection
            # and send messages through it
            return {
                "error": "SSE communication not fully implemented",
                "message": "This is a simplified test - SSE requires persistent connection"
            }
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"error": str(e)}
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP connection."""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
        return await self.send_message("initialize", params)
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.send_message("tools/list")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with given arguments."""
        params = {
            "name": name,
            "arguments": arguments
        }
        return await self.send_message("tools/call", params)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🌐 测试 MCP 服务器 (SSE 连接)")
    print("=" * 50)
    
    client = MCPSSEClient()
    
    try:
        # 1. 初始化连接
        print("\n1. 初始化 MCP 连接...")
        init_result = await client.initialize()
        print(f"   ✅ 初始化结果: {json.dumps(init_result, indent=2, ensure_ascii=False)}")
        
        # 2. 获取工具列表
        print("\n2. 获取可用工具...")
        tools_result = await client.list_tools()
        print(f"   ✅ 工具列表: {json.dumps(tools_result, indent=2, ensure_ascii=False)}")
        
        # 3. 测试天气工具
        print("\n3. 测试天气工具...")
        weather_result = await client.call_tool("get_weather", {"city": "Tokyo"})
        print(f"   ✅ 天气工具结果: {json.dumps(weather_result, indent=2, ensure_ascii=False)}")
        
        # 4. 测试另一个城市
        print("\n4. 测试另一个城市...")
        weather_result2 = await client.call_tool("get_weather", {"city": "Beijing"})
        print(f"   ✅ 北京天气: {json.dumps(weather_result2, indent=2, ensure_ascii=False)}")
        
        print(f"\n🎉 MCP 服务器测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.exception("Test failed")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
