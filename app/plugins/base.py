from fastmcp import FastMCP
from typing import Optional

class BasePlugin:
    """插件基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.mcp = FastMCP(name)
        self._register_tools()
    
    def _register_tools(self):
        """注册工具，子类需要实现此方法"""
        pass
    
    async def get_tools(self) -> list:
        """获取插件提供的工具列表"""
        return await self.mcp.get_tools() 