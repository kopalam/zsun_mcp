import asyncio
import json
from typing import Any, Dict
from fastmcp import Client
from fastmcp.exceptions import FastMCPError

class FastMCPClient:
    def __init__(self, url: str = "http://localhost:8010"):
        self.url = url
        self.client = None

    async def connect(self):
        """连接到 FastMCP 服务器"""
        self.client = Client(self.url)
        await self.client.__aenter__()

    async def disconnect(self):
        """断开与服务器的连接"""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def list_tools(self) -> Dict[str, Any]:
        """获取可用的工具列表"""
        try:
            return await self.client.list_tools()
        except FastMCPError as e:
            print(f"获取工具列表失败: {e}")
            return {}

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """调用指定的工具"""
        try:
            result = await self.client.call_tool(tool_name, params)
            return result.text
        except FastMCPError as e:
            print(f"调用工具 {tool_name} 失败: {e}")
            return ""

async def main():
    # 创建客户端实例
    client = FastMCPClient()

    try:
        # 连接到服务器
        await client.connect()

        # 获取工具列表
        tools = await client.list_tools()
        print("可用的工具:")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")

        # 调用各种工具
        print("\n调用工具示例:")

        # 问候工具
        result = await client.call_tool("hello", {"name": "张三"})
        print(f"问候结果: {result}")

        # 计算工具
        result = await client.call_tool("add", {"a": 10, "b": 20})
        print(f"加法结果: {result}")

        result = await client.call_tool("subtract", {"a": 30, "b": 15})
        print(f"减法结果: {result}")

        # 天气工具
        result = await client.call_tool("get_weather", {"city": "上海"})
        print(f"天气结果: {result}")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 断开连接
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 