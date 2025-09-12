#!/usr/bin/env python3
"""
Test weather tool via WebSocket connection.
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherWebSocketClient:
    """WebSocket client for testing weather tool."""
    
    def __init__(self, base_url: str = "ws://192.168.0.101:8010", token: str = "ZSuniiTmsyBBgdtllks"):
        self.base_url = base_url
        self.token = token
        self.tool_websocket = None
        self.robot_websocket = None
    
    async def connect_tool_endpoint(self):
        """Connect to tool WebSocket endpoint."""
        tool_url = f"{self.base_url}/mcp_endpoint/mcp/?token={self.token}"
        try:
            self.tool_websocket = await websockets.connect(tool_url)
            logger.info("✅ Connected to tool WebSocket endpoint")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to tool endpoint: {e}")
            return False
    
    async def connect_robot_endpoint(self):
        """Connect to robot WebSocket endpoint."""
        robot_url = f"{self.base_url}/mcp_endpoint/call/?token={self.token}"
        try:
            self.robot_websocket = await websockets.connect(robot_url)
            logger.info("✅ Connected to robot WebSocket endpoint")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to robot endpoint: {e}")
            return False
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools via tool endpoint."""
        if not self.tool_websocket:
            raise RuntimeError("Tool WebSocket not connected")
        
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        await self.tool_websocket.send(json.dumps(message))
        logger.info(f"📤 Sent tools/list request to tool endpoint: {json.dumps(message, indent=2)}")
        
        try:
            # 增加超时时间到30秒
            response = await asyncio.wait_for(self.tool_websocket.recv(), timeout=30.0)
            logger.info(f"📥 Received response from tool endpoint: {response}")
            return json.loads(response)
        except asyncio.TimeoutError:
            logger.warning("⚠️  Tool endpoint response timeout after 30 seconds")
            return {"error": "timeout"}
        except Exception as e:
            logger.error(f"❌ Error receiving response: {e}")
            return {"error": str(e)}
    
    async def call_weather_tool(self, city: str) -> Dict[str, Any]:
        """Call weather tool via tool endpoint."""
        if not self.tool_websocket:
            raise RuntimeError("Tool WebSocket not connected")
        
        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {
                    "city": city
                }
            }
        }
        
        await self.tool_websocket.send(json.dumps(message))
        logger.info(f"📤 Sent weather request for city: {city}")
        logger.info(f"📤 Message details: {json.dumps(message, indent=2)}")
        
        try:
            response = await asyncio.wait_for(self.tool_websocket.recv(), timeout=30.0)
            logger.info(f"📥 Received weather response: {response}")
            return json.loads(response)
        except asyncio.TimeoutError:
            logger.warning("⚠️  Weather tool response timeout after 30 seconds")
            return {"error": "timeout"}
        except Exception as e:
            logger.error(f"❌ Error receiving weather response: {e}")
            return {"error": str(e)}
    
    async def disconnect(self):
        """Disconnect from WebSocket endpoints."""
        if self.tool_websocket:
            await self.tool_websocket.close()
            logger.info("🔌 Disconnected from tool endpoint")
        
        if self.robot_websocket:
            await self.robot_websocket.close()
            logger.info("🔌 Disconnected from robot endpoint")


async def test_weather_via_websocket():
    """Test weather tool via WebSocket."""
    client = WeatherWebSocketClient()
    
    try:
        # Connect to both endpoints
        logger.info("🚀 Starting weather WebSocket test...")
        logger.info(f"🔗 Connecting to: {client.base_url}")
        
        tool_connected = await client.connect_tool_endpoint()
        robot_connected = await client.connect_robot_endpoint()
        
        if not tool_connected or not robot_connected:
            logger.error("❌ Failed to connect to required endpoints")
            logger.error(f"Tool connected: {tool_connected}, Robot connected: {robot_connected}")
            return
        
        # List available tools
        logger.info("\n📋 Listing available tools...")
        tools_response = await client.list_tools()
        logger.info(f"Tools response: {json.dumps(tools_response, indent=2)}")
        
        # 检查工具列表是否成功
        if "error" in tools_response:
            logger.error(f"❌ Failed to get tools list: {tools_response['error']}")
            return
        
        # 检查是否有天气工具
        if "result" in tools_response and "tools" in tools_response["result"]:
            tools = tools_response["result"]["tools"]
            weather_tools = [t for t in tools if "weather" in t.get("name", "").lower()]
            logger.info(f"🌤️  Found {len(weather_tools)} weather-related tools: {[t['name'] for t in weather_tools]}")
        
        # Test weather tool with different cities
        test_cities = ["Beijing", "Shanghai", "Tokyo", "New York"]
        
        for city in test_cities:
            logger.info(f"\n🌤️  Testing weather for {city}...")
            weather_response = await client.call_weather_tool(city)
            logger.info(f"Weather response for {city}: {json.dumps(weather_response, indent=2)}")
            
            # 检查响应是否成功
            if "error" in weather_response:
                logger.warning(f"⚠️  Weather request failed for {city}: {weather_response['error']}")
            else:
                logger.info(f"✅ Weather request successful for {city}")
            
            # Wait a bit between requests
            await asyncio.sleep(1)
    
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    finally:
        await client.disconnect()
        logger.info("🏁 Test completed")


if __name__ == "__main__":
    asyncio.run(test_weather_via_websocket())
