# FastMCP API 插件开发指南

本指南将详细介绍如何为 FastMCP API 服务框架开发自定义插件。

## 目录

- [插件架构概述](#插件架构概述)
- [基础插件类](#基础插件类)
- [创建新插件](#创建新插件)
- [插件注册](#插件注册)
- [工具函数开发](#工具函数开发)
- [错误处理](#错误处理)
- [配置管理](#配置管理)
- [测试插件](#测试插件)
- [最佳实践](#最佳实践)
- [示例插件](#示例插件)

## 插件架构概述

FastMCP API 采用插件化架构，每个插件都是一个独立的模块，可以包含多个工具函数。插件通过继承 `BasePlugin` 基类来实现标准化接口。

### 核心组件

- **BasePlugin**: 所有插件的基类，定义了标准接口
- **工具函数**: 插件提供的具体功能，通过 MCP 协议暴露给客户端
- **插件管理器**: 负责插件的注册、加载和管理

## 基础插件类

所有插件都必须继承 `BasePlugin` 类：

```python
from app.plugins.base import BasePlugin
from typing import List, Callable

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("my_plugin")
    
    def tools(self) -> List[Callable]:
        """返回插件提供的工具函数列表"""
        return [self.my_tool_function]
    
    async def my_tool_function(self, param: str) -> dict:
        """工具函数实现"""
        # 实现具体功能
        return self.json_ok({"result": "success"})
```

### BasePlugin 提供的方法

- `json_ok(data)`: 创建成功响应
- `json_err(code, message, detail=None)`: 创建错误响应

## 创建新插件

### 1. 创建插件目录结构

```
app/plugins/
├── my_plugin/
│   ├── __init__.py
│   └── plugin.py
└── __init__.py
```

### 2. 实现插件类

创建 `app/plugins/my_plugin/plugin.py`：

```python
"""我的自定义插件实现"""

import logging
from typing import Any, Dict, List, Callable
from pydantic import BaseModel, Field

from ..base import BasePlugin

logger = logging.getLogger(__name__)

class MyRequest(BaseModel):
    """请求参数验证模型"""
    param1: str = Field(..., description="参数1的描述")
    param2: int = Field(default=0, description="参数2的描述")

class MyPlugin(BasePlugin):
    """我的自定义插件"""

    def __init__(self):
        super().__init__("my_plugin")
        # 初始化插件特定的配置
        self.config = self._load_config()

    def tools(self) -> List[Callable]:
        """返回插件提供的工具函数列表"""
        return [
            self.my_tool_1,
            self.my_tool_2
        ]

    async def my_tool_1(self, param1: str, param2: int = 0) -> Dict[str, Any]:
        """第一个工具函数
        
        Args:
            param1: 必需参数
            param2: 可选参数，默认为0
            
        Returns:
            包含结果的字典
        """
        try:
            # 验证输入参数
            request = MyRequest(param1=param1, param2=param2)
            
            # 实现具体功能
            result = await self._process_data(request.param1, request.param2)
            
            logger.info(f"工具1执行成功: {param1}")
            return self.json_ok(result)
            
        except Exception as e:
            logger.error(f"工具1执行失败: {str(e)}")
            return self.json_err("PROCESSING_ERROR", f"处理失败: {str(e)}")

    async def my_tool_2(self, query: str) -> Dict[str, Any]:
        """第二个工具函数"""
        try:
            # 实现功能
            result = await self._search_data(query)
            return self.json_ok(result)
            
        except Exception as e:
            logger.error(f"工具2执行失败: {str(e)}")
            return self.json_err("SEARCH_ERROR", f"搜索失败: {str(e)}")

    async def _process_data(self, param1: str, param2: int) -> Dict[str, Any]:
        """内部数据处理方法"""
        # 实现具体的数据处理逻辑
        return {
            "processed_param1": param1.upper(),
            "processed_param2": param2 * 2,
            "timestamp": "2024-01-01T00:00:00Z"
        }

    async def _search_data(self, query: str) -> Dict[str, Any]:
        """内部数据搜索方法"""
        # 实现具体的搜索逻辑
        return {
            "query": query,
            "results": ["结果1", "结果2", "结果3"],
            "count": 3
        }

    def _load_config(self) -> Dict[str, Any]:
        """加载插件配置"""
        import os
        return {
            "api_key": os.getenv("MY_PLUGIN_API_KEY"),
            "base_url": os.getenv("MY_PLUGIN_BASE_URL", "https://api.example.com"),
            "timeout": int(os.getenv("MY_PLUGIN_TIMEOUT", "30"))
        }
```

### 3. 创建插件实例

创建 `app/plugins/my_plugin/__init__.py`：

```python
"""我的自定义插件模块"""

from .plugin import MyPlugin

# 创建插件实例
my_plugin = MyPlugin()

__all__ = ["my_plugin"]
```

### 4. 更新插件注册

修改 `app/plugins/__init__.py`：

```python
"""插件包初始化"""

from .weather import weather_plugin
from .my_plugin import my_plugin

__all__ = ["weather_plugin", "my_plugin"]
```

### 5. 在主应用中注册插件

修改 `app/run.py` 中的 `_register_plugins` 方法：

```python
def _register_plugins(self):
    """注册所有可用的插件"""
    logger.info("注册插件...")
    
    # 注册天气插件
    self._register_plugin(weather_plugin)
    
    # 注册我的自定义插件
    self._register_plugin(my_plugin)
    
    logger.info(f"已注册 {len(self.plugins)} 个插件")
```

## 工具函数开发

### 函数签名要求

工具函数必须满足以下要求：

1. **异步函数**: 使用 `async def` 定义
2. **类型注解**: 为所有参数和返回值提供类型注解
3. **文档字符串**: 提供清晰的函数说明和参数描述
4. **错误处理**: 使用 try-catch 包装，返回标准错误格式

### 参数验证

使用 Pydantic 模型进行参数验证：

```python
from pydantic import BaseModel, Field, validator

class WeatherRequest(BaseModel):
    city: str = Field(..., description="城市名称", min_length=1, max_length=100)
    units: str = Field(default="metric", description="温度单位")
    
    @validator('units')
    def validate_units(cls, v):
        if v not in ['metric', 'imperial', 'kelvin']:
            raise ValueError('单位必须是 metric, imperial 或 kelvin')
        return v
```

### 返回值格式

所有工具函数都应返回标准格式的字典：

**成功响应**:
```python
{
    "status": "success",
    "data": {
        # 实际数据
    }
}
```

**错误响应**:
```python
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "detail": "可选的详细错误信息"
    }
}
```

## 错误处理

### 标准错误代码

建议使用以下错误代码分类：

- `VALIDATION_ERROR`: 参数验证失败
- `API_ERROR`: 外部API调用失败
- `NETWORK_ERROR`: 网络连接问题
- `AUTH_ERROR`: 认证失败
- `RATE_LIMIT_ERROR`: 请求频率限制
- `UNKNOWN_ERROR`: 未知错误

### 错误处理示例

```python
async def my_tool(self, param: str) -> Dict[str, Any]:
    try:
        # 参数验证
        if not param or not param.strip():
            return self.json_err("VALIDATION_ERROR", "参数不能为空")
        
        # 业务逻辑
        result = await self._process(param)
        return self.json_ok(result)
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP错误: {str(e)}")
        return self.json_err("API_ERROR", f"API调用失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        return self.json_err("UNKNOWN_ERROR", f"处理失败: {str(e)}")
```

## 配置管理

### 环境变量配置

插件配置通过环境变量管理：

```python
import os

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("my_plugin")
        self.api_key = os.getenv("MY_PLUGIN_API_KEY")
        self.base_url = os.getenv("MY_PLUGIN_BASE_URL", "https://api.example.com")
        self.timeout = int(os.getenv("MY_PLUGIN_TIMEOUT", "30"))
        
        if not self.api_key:
            logger.warning("MY_PLUGIN_API_KEY 未设置，某些功能可能不可用")
```

### 配置文件支持

对于复杂配置，可以支持配置文件：

```python
import json
from pathlib import Path

def _load_config_file(self) -> Dict[str, Any]:
    """从配置文件加载配置"""
    config_path = Path("config/my_plugin.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}
```

## 测试插件

### 单元测试

创建测试文件 `tests/test_my_plugin.py`：

```python
import pytest
import asyncio
from app.plugins.my_plugin import MyPlugin

class TestMyPlugin:
    @pytest.fixture
    def plugin(self):
        return MyPlugin()
    
    @pytest.mark.asyncio
    async def test_my_tool_1_success(self, plugin):
        """测试工具1成功场景"""
        result = await plugin.my_tool_1("test", 10)
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["processed_param1"] == "TEST"
        assert result["data"]["processed_param2"] == 20
    
    @pytest.mark.asyncio
    async def test_my_tool_1_validation_error(self, plugin):
        """测试工具1参数验证错误"""
        result = await plugin.my_tool_1("", -1)
        
        assert result["status"] == "error"
        assert result["error"]["code"] == "VALIDATION_ERROR"
```

### 集成测试

```python
import pytest
from app.run import FastMCPAPIServer

@pytest.mark.asyncio
async def test_plugin_integration():
    """测试插件集成"""
    server = FastMCPAPIServer()
    
    # 检查插件是否正确注册
    assert len(server.plugins) > 0
    
    # 检查工具是否正确注册
    tools = await server.app.get_tools()
    assert "my_tool_1" in tools
    assert "my_tool_2" in tools
```

## 最佳实践

### 1. 代码组织

- 将插件逻辑分解为小的、可测试的方法
- 使用私有方法（前缀 `_`）处理内部逻辑
- 保持工具函数简洁，复杂逻辑提取到私有方法

### 2. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

async def my_tool(self, param: str) -> Dict[str, Any]:
    logger.info(f"开始处理请求: {param}")
    
    try:
        result = await self._process(param)
        logger.info(f"处理成功: {param}")
        return self.json_ok(result)
    except Exception as e:
        logger.error(f"处理失败: {param}, 错误: {str(e)}")
        return self.json_err("PROCESSING_ERROR", str(e))
```

### 3. 资源管理

对于需要清理资源的插件（如HTTP客户端），实现 `close` 方法：

```python
async def close(self):
    """清理资源"""
    if hasattr(self, 'http_client'):
        await self.http_client.aclose()
```

### 4. 性能优化

- 使用连接池复用HTTP连接
- 实现适当的缓存机制
- 避免在工具函数中进行阻塞操作

### 5. 安全性

- 验证所有输入参数
- 不要在日志中记录敏感信息
- 使用环境变量管理API密钥
- 实现适当的错误处理，避免信息泄露

## 示例插件

### 完整的天气插件示例

参考 `app/plugins/weather/plugin.py` 了解完整的插件实现，包括：

- 异步HTTP客户端使用
- 外部API集成
- 错误处理和重试机制
- 数据转换和格式化
- 配置管理

### 插件开发检查清单

- [ ] 继承 `BasePlugin` 基类
- [ ] 实现 `tools()` 方法返回工具函数列表
- [ ] 为所有工具函数提供类型注解
- [ ] 添加详细的文档字符串
- [ ] 实现适当的错误处理
- [ ] 使用 Pydantic 进行参数验证
- [ ] 添加日志记录
- [ ] 编写单元测试
- [ ] 更新插件注册
- [ ] 创建插件实例文件

## 故障排除

### 常见问题

1. **插件未注册**: 检查 `__init__.py` 文件是否正确导入和导出插件实例
2. **工具函数未显示**: 确保工具函数在 `tools()` 方法中返回
3. **类型注解错误**: 确保所有参数和返回值都有正确的类型注解
4. **异步函数错误**: 确保工具函数使用 `async def` 定义

### 调试技巧

1. 启用详细日志记录
2. 使用 `print` 语句调试（生产环境前移除）
3. 检查 MCP 客户端连接状态
4. 验证环境变量配置

通过遵循本指南，您可以轻松地为 FastMCP API 服务框架开发功能强大、稳定可靠的插件。