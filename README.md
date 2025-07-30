# FastMCP API 服务框架

FastMCP API 是一个基于 FastMCP 的服务框架，提供了一套完整的插件系统，用于构建和扩展 MCP 服务。

## 项目结构

```
app/
├── plugins/              # 插件目录
│   ├── __init__.py      # 插件包初始化
│   ├── base.py          # 插件基类
│   └── weather/         # 天气插件
│       ├── __init__.py  # 插件实例
│       └── plugin.py    # 插件实现
├── run.py               # 主服务器
└── weather_client.py    # 客户端示例
```

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
python app/run.py
```

### 测试客户端

```bash
python app/weather_client.py
```

## 插件开发指南

### 插件架构

FastMCP API 采用插件化架构，每个插件都是一个独立的模块，可以方便地扩展和集成。

#### 插件基类

所有插件都继承自 `BasePlugin` 类，它提供了基本的插件功能：

```python
from plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("My Plugin")
        # 插件初始化代码
```

#### 插件实现

插件实现文件（如 `plugin.py`）包含插件的核心业务逻辑：

```python
class WeatherPlugin(BasePlugin):
    def __init__(self):
        super().__init__("Weather Service")
        self.API_KEY = "your_api_key"
    
    async def get_weather(self, city: str) -> str:
        # 实现天气获取逻辑
        pass
```

#### 插件实例

插件实例文件（如 `__init__.py`）创建并导出插件实例：

```python
from .plugin import WeatherPlugin

# 创建插件实例
weather_plugin = WeatherPlugin()

# 导出插件实例
__all__ = ['weather_plugin']
```

### 创建新插件

1. 在 `plugins` 目录下创建新的插件目录
2. 创建 `plugin.py` 实现插件功能
3. 创建 `__init__.py` 导出插件实例
4. 在主服务器中注册插件工具

示例：
```python
# plugins/news/plugin.py
from ..base import BasePlugin

class NewsPlugin(BasePlugin):
    def __init__(self):
        super().__init__("News Service")
    
    async def get_news(self, category: str) -> str:
        # 实现新闻获取逻辑
        pass

# plugins/news/__init__.py
from .plugin import NewsPlugin
news_plugin = NewsPlugin()
__all__ = ['news_plugin']

# run.py
from plugins.news import news_plugin
main_mcp.tool(news_plugin.get_news, name="get_news")
```

### 插件开发规范

1. **职责分离**：
   - 插件实现（plugin.py）负责业务逻辑
   - 插件实例（__init__.py）负责实例化
   - 主服务器负责工具注册

2. **命名规范**：
   - 插件目录使用小写字母
   - 插件类名使用驼峰命名
   - 工具函数名使用小写字母加下划线

3. **错误处理**：
   - 使用 try-except 处理异常
   - 返回有意义的错误信息
   - 记录关键错误日志

4. **文档规范**：
   - 为所有类和方法添加文档字符串
   - 说明参数类型和返回值
   - 提供使用示例

## 客户端开发

### 基本用法

```python
from fastmcp import Client

async with Client("http://localhost:8010/sse") as client:
    result = await client.call_tool("get_weather", {"city": "beijing"})
    print(result)
```

### 错误处理

```python
try:
    result = await client.call_tool("get_weather", {"city": "beijing"})
except Exception as e:
    print(f"调用失败: {str(e)}")
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t fastmcp-api .

# 运行容器
docker run -p 8010:8010 fastmcp-api
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 