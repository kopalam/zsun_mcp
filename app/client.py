import asyncio
from fastmcp import Client

async def main():
    # 连接到 FastMCP 服务器
    async with Client("http://localhost:8010") as client:
        # 获取可用的工具列表
        tools = await client.list_tools()
        print("可用的工具:", tools)

        # 调用问候工具
        result = await client.call_tool("hello", {"name": "张三"})
        print("问候结果:", result.text)

        # 调用加法工具
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print("加法结果:", result.text)

        # 调用天气工具
        result = await client.call_tool("get_weather", {"city": "北京"})
        print("天气结果:", result.text)

if __name__ == "__main__":
    asyncio.run(main()) 