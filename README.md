# ZsunMcp API Service Framework

ZsunMcp是基于 **FastMCP** 的插件化 MCP Server 框架，支持 **Websocket/SSE/HTTP** 传输，采用模块化架构设计。

## 🚀 特性

- **插件化架构**: 每个插件独立封装业务逻辑，易于扩展和维护
- **多种传输方式**: 支持 SSE (Server-Sent Events)、stdio 和 WebSocket 传输
- **WebSocket兼容**: 与 mcp-endpoint-server 保持兼容的 WebSocket 实现
- **JSON-RPC 2.0**: 标准化的 JSON-RPC 2.0 协议支持
- **异步优先**: 基于 asyncio 的高性能异步处理
- **统一日志**: 标准化的日志记录，支持请求追踪
- **环境配置**: 支持 `.env` 文件和环境变量配置
- **完整测试**: 包含单元测试和集成测试
- **代码质量**: 集成 black、isort、ruff 等代码格式化工具

## 📁 项目结构

```
app/
├── plugins/                    # 插件目录
│   ├── __init__.py
│   ├── base.py                 # 插件基类
│   └── weather/                # 天气插件
│       ├── __init__.py
│       └── plugin.py
├── core/                       # 核心组件
│   ├── __init__.py
│   └── connection_manager.py   # WebSocket连接管理
├── handlers/                   # 处理器
│   ├── __init__.py
│   └── websocket_handler.py    # WebSocket消息处理
├── utils/                      # 工具类
│   ├── __init__.py
│   └── jsonrpc.py             # JSON-RPC 2.0协议
├── run.py                      # 主服务器
├── config.py                   # 配置管理
├── weather_client.py           # 客户端示例
└── websocket_client_test.py    # WebSocket测试客户端
requirements.txt                # 依赖配置
env.example                     # 环境变量示例
pyproject.toml                  # 项目配置
tests/                          # 测试目录
└── test_weather.py
```

## 🛠️ 安装

### 环境要求

- Python 3.10+
- pip 或 poetry


## 对接xinnan-xiaozhi-server

### 1. 配置MCP端点
在参数字典 → 参数管理中找到 `server.mcp_endpoint`，设置参数值为：
```
http://192.168.0.126:7100/mcp_endpoint/health?key=d997b2566104484d80923ca484dd5a73
```

### 2. 配置认证Token
在智能体管理的意图识别中，找到WebSocket连接地址：
```
ws://192.168.0.126:7100/mcp_endpoint/mcp/?token=v%2BGNdYhqHQJ1drrKS6JJ3W12I2tAWMmimVUgyDHs%2FpFuup38CTerac1ML7TeIgmI
```

**重要说明：**
- URL中的 `%2B` 是URL编码的 `+` 号
- URL中的 `%2F` 是URL编码的 `/` 号
- 需要将token解码后写入 `.env` 文件

**操作步骤：**
1. 从URL中提取token：`v%2BGNdYhqHQJ1drrKS6JJ3W12I2tAWMmimVUgyDHs%2FpFuup38CTerac1ML7TeIgmI`
2. URL解码后得到：`v+GNdYhqHQJ1drrKS6JJ3W12I2tAWMmimVUgyDHs/pFuup38CTerac1ML7TeIgmI`
3. 在 `app/.env` 文件中添加：
   ```
   SERVER_KEY="v+GNdYhqHQJ1drrKS6JJ3W12I2tAWMmimVUgyDHs/pFuup38CTerac1ML7TeIgmI"
   ```
4. 如果 `app/.env` 文件不存在，请先创建该文件

## 🚀 快速开始

### 启动服务器

```bash
docker compose up -d
```

### WebSocket 端点

当使用 WebSocket 传输时，服务器提供以下端点：

- **工具端端点**: `ws://host:port/mcp_endpoint/mcp/?token=your_token`
- **小智端端点**: `ws://host:port/mcp_endpoint/call/?token=your_token`
- **健康检查**: `http://host:port/mcp_endpoint/health`

### 环境变量配置

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8010
DEBUG=false
SERVER_KEY=your_secret_key

# WebSocket配置
ENABLE_CORS=true
ALLOWED_ORIGINS=*

# 日志配置
LOG_LEVEL=INFO

# 天气插件配置
WEATHER_API_BASE=https://api.openweathermap.org/data/2.5
WEATHER_API_KEY=your_api_key
```

## 🔌 WebSocket 兼容性

本项目已实现与 [mcp-endpoint-server](https://github.com/xinnan-tech/mcp-endpoint-server) 的 WebSocket 兼容性：

### 主要特性

1. **双端点架构**: 支持工具端和小智端的独立 WebSocket 连接
2. **JSON-RPC 2.0**: 使用标准 JSON-RPC 2.0 协议进行消息交换
3. **消息转发**: 在工具端和小智端之间自动转发消息
4. **连接管理**: 智能管理 WebSocket 连接和 UUID 映射
5. **错误处理**: 完善的错误处理和 JSON-RPC 错误响应

### 协议兼容性

- **消息格式**: 完全兼容 JSON-RPC 2.0 标准
- **端点路径**: 使用相同的端点路径结构
- **认证机制**: 支持 token 认证（可扩展）
- **错误代码**: 使用标准的 JSON-RPC 错误代码

### 使用示例

```python
# 连接到工具端
import websockets
import json

async def connect_tool():
    uri = "ws://localhost:8010/mcp_endpoint/?token=default_key_123456"
    async with websockets.connect(uri) as websocket:
        # 发送天气查询请求
        request = {
            "jsonrpc": "2.0",
            "method": "get_weather",
            "params": {"city": "Beijing"},
            "id": 1
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        print(json.loads(response))
```

# 连接到自定义服务器
python app/weather_client.py --server http://localhost:8080/sse
```

## 📖 使用说明

### 服务器端点

- **SSE 端点**: `http://localhost:8010/sse`
- **HTTP 端点**: `http://localhost:8010/` (如果支持)

### 可用工具

#### get_weather

获取指定城市的天气信息。

**参数**:
- `city` (string): 城市名称

**返回**:
```json
{
  "status": "success",
  "data": {
    "city": "beijing",
    "lat": 39.9042,
    "lon": 116.4074,
    "temperature_c": 25.5,
    "windspeed": 3.2,
    "weather_code": 0,
    "weather_description": "Clear sky",
    "observed_at": "2024-01-01T12:00:00",
    "provider": "open-meteo"
  }
}
```

### 插件开发

#### 创建新插件

1. 在 `app/plugins/` 下创建插件目录
2. 继承 `BasePlugin` 类
3. 实现 `tools()` 方法
4. 在 `app/plugins/__init__.py` 中注册插件

示例：

```python
from app.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("my_plugin")
    
    def tools(self):
        return [self.my_tool]
    
    async def my_tool(self, param: str) -> dict:
        """我的工具函数."""
        return self.json_ok({"result": f"处理参数: {param}"})
```

## 🔧 配置

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务器绑定主机 |
| `PORT` | `8010` | 服务器绑定端口 |
| `TRANSPORT` | `sse` | 传输方式 (sse/stdio) |
| `WEATHER_API_BASE` | `https://api.open-meteo.com/v1` | 天气 API 基础 URL |
| `GEOCODING_API_BASE` | `https://geocoding-api.open-meteo.com/v1` | 地理编码 API 基础 URL |
| `WEATHER_API_KEY` | - | 天气 API 密钥（可选） |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 天气 API 配置

默认使用 Open-Meteo API（无需密钥），支持以下配置：

- **Open-Meteo** (默认): 免费，无需密钥
- **OpenWeatherMap**: 需要 API 密钥

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_weather.py

# 运行集成测试（需要网络连接）
pytest -m integration

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 🔍 代码质量

```bash
# 代码格式化
black app/ tests/
isort app/ tests/

# 代码检查
ruff check app/ tests/

# 类型检查
mypy app/

# 运行所有检查
black app/ tests/ && isort app/ tests/ && ruff check app/ tests/ && mypy app/
```

## 📊 性能优化

- 使用 `uvloop` 提升异步性能（Linux/macOS）
- HTTP 客户端连接池复用
- 异步处理所有 I/O 操作
- 插件懒加载机制

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 使用不同端口
   python app/run.py --port 8080
   ```

2. **网络连接问题**
   ```bash
   # 检查防火墙设置
   # 确保端口 8010 可访问
   ```

3. **依赖安装问题**
   ```bash
   # 升级 pip
   pip install --upgrade pip
   
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

### 日志调试

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python app/run.py
```

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastMCP](https://github.com/fastmcp/fastmcp) - MCP 框架
- [Open-Meteo](https://OpenWeatherMap.org/) - 免费天气 API
- [Pydantic](https://pydantic.dev/) - 数据验证
- [httpx](https://www.python-httpx.org/) - HTTP 客户端

