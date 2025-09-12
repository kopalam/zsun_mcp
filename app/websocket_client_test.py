#!/usr/bin/env python3
"""
WebSocket客户端测试工具
用于测试FastMCP WebSocket服务器的功能
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket客户端测试工具"""

    def __init__(self, host: str = "localhost", port: int = 8010, token: str = "default_key_123456"):
        self.host = host
        self.port = port
        self.token = token
        self.websocket = None

    async def connect_tool_endpoint(self):
        """连接到工具端WebSocket端点"""
        uri = f"ws://{self.host}:{self.port}/mcp_endpoint/mcp/?token={self.token}"
        logger.info(f"连接到工具端端点: {uri}")
        
        try:
            self.websocket = await websockets.connect(uri)
            logger.info("工具端连接已建立")
            return True
        except Exception as e:
            logger.error(f"连接工具端失败: {e}")
            return False

    async def connect_robot_endpoint(self):
        """连接到小智端WebSocket端点"""
        uri = f"ws://{self.host}:{self.port}/mcp_endpoint/call/?token={self.token}"
        logger.info(f"连接到小智端端点: {uri}")
        
        try:
            self.websocket = await websockets.connect(uri)
            logger.info("小智端连接已建立")
            return True
        except Exception as e:
            logger.error(f"连接小智端失败: {e}")
            return False

    async def send_message(self, message: Dict[str, Any]):
        """发送消息"""
        if not self.websocket:
            logger.error("WebSocket未连接")
            return False
        
        try:
            message_str = json.dumps(message, ensure_ascii=False)
            await self.websocket.send(message_str)
            logger.info(f"消息已发送: {message_str}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def receive_message(self):
        """接收消息"""
        if not self.websocket:
            logger.error("WebSocket未连接")
            return None
        
        try:
            message = await self.websocket.recv()
            logger.info(f"收到消息: {message}")
            return json.loads(message)
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return None

    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            logger.info("连接已关闭")


async def test_weather_tool():
    """测试天气工具功能"""
    logger.info("=== 测试天气工具功能 ===")
    
    # 创建客户端
    client = WebSocketClient()
    
    try:
        # 连接到工具端
        if not await client.connect_tool_endpoint():
            return
        
        # 发送天气查询请求
        weather_request = {
            "jsonrpc": "2.0",
            "method": "get_weather",
            "params": {"city": "Beijing"},
            "id": 1
        }
        
        await client.send_message(weather_request)
        
        # 等待响应
        response = await client.receive_message()
        if response:
            logger.info(f"天气查询响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        logger.error(f"测试天气工具失败: {e}")
    finally:
        await client.close()


async def test_robot_endpoint():
    """测试小智端端点"""
    logger.info("=== 测试小智端端点 ===")
    
    # 创建客户端
    client = WebSocketClient()
    
    try:
        # 连接到小智端
        if not await client.connect_robot_endpoint():
            return
        
        # 发送测试消息
        test_request = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"message": "Hello from robot endpoint"},
            "id": 1
        }
        
        await client.send_message(test_request)
        
        # 等待响应
        response = await client.receive_message()
        if response:
            logger.info(f"小智端响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        logger.error(f"测试小智端失败: {e}")
    finally:
        await client.close()


async def test_health_check():
    """测试健康检查端点"""
    logger.info("=== 测试健康检查端点 ===")
    
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://localhost:8010/mcp_endpoint/health"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"健康检查响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    logger.error(f"健康检查失败: {response.status}")
    except Exception as e:
        logger.error(f"健康检查请求失败: {e}")


async def main():
    """主测试函数"""
    logger.info("开始WebSocket客户端测试")
    
    # 测试健康检查
    await test_health_check()
    
    # 等待一下让服务器启动
    await asyncio.sleep(1)
    
    # 测试天气工具
    await test_weather_tool()
    
    # 等待一下
    await asyncio.sleep(1)
    
    # 测试小智端端点
    await test_robot_endpoint()
    
    logger.info("WebSocket客户端测试完成")


if __name__ == "__main__":
    asyncio.run(main())
