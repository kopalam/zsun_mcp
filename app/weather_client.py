import asyncio
from fastmcp import Client
from fastmcp.exceptions import FastMCPError
from mcp.shared.exceptions import McpError
from typing import Optional, Dict, Any

class WeatherClient:
    """天气服务客户端"""
    
    def __init__(self, server_url: str = "http://localhost:8010/sse"):
        self.server_url = server_url
        self._client: Optional[Client] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self._client = Client(self.server_url)
        await self._client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def call_tool_with_retry(self, tool_name: str, params: dict, max_retries: int = 3) -> str:
        """调用工具，带重试机制"""
        if not self._client:
            raise RuntimeError("客户端未连接，请使用 async with 语句")
            
        current_client = self._client
        for attempt in range(max_retries):
            try:
                result = await current_client.call_tool(tool_name, params)
                return str(result)
            except (McpError, FastMCPError) as e:
                if "Session terminated" in str(e):
                    print("会话已终止，正在重新连接...")
                    # 重新创建客户端并连接
                    new_client = Client(self.server_url)
                    await new_client.__aenter__()
                    # 更新当前客户端
                    current_client = new_client
                    self._client = new_client
                    # 重试当前操作
                    continue
                elif attempt < max_retries - 1:
                    print(f"调用失败，正在重试... (错误: {str(e)})")
                    await asyncio.sleep(2)
                else:
                    raise Exception(f"调用工具 {tool_name} 失败: {str(e)}")
    
    async def get_weather(self, city: str) -> str:
        """获取指定城市的天气信息
        
        Args:
            city: 城市名称，例如：beijing、shanghai、guangzhou等
            
        Returns:
            格式化的天气信息字符串
        """
        return await self.call_tool_with_retry("get_weather", {"city": city})
    
    async def get_weather_forecast(self, city: str, days: int = 3) -> str:
        """获取指定城市的天气预报
        
        Args:
            city: 城市名称，例如：beijing、shanghai、guangzhou等
            days: 预报天数（1-5天）
            
        Returns:
            格式化的天气预报信息字符串
        """
        return await self.call_tool_with_retry("get_weather_forecast", {
            "city": city,
            "days": days
        })

async def main():
    try:
        # 使用 async with 确保正确的连接管理
        async with WeatherClient() as client:
            print("成功连接到服务器")
            
            # 获取当前天气
            print("\n获取北京当前天气:")
            result = await client.get_weather("beijing")
            print(result)

            # 获取天气预报
            print("\n获取上海未来3天天气预报:")
            result = await client.get_weather_forecast("shanghai", days=3)
            print(result)

    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 