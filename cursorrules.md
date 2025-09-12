你现在是资深 Python/Async 工程师与 MCP 专家。请基于 **FastMCP（Python）** 为我从零实现一个可运行的「FastMCP API 服务框架」。严格按照以下需求交付代码与文件。

## 目标
- 基于 **fastmcp** 实现一个 MCP Server，支持 **SSE/HTTP** 传输，默认监听 **:8010**，SSE 路径 **/sse**。
- 采用**插件化架构**（plugins 目录），每个插件独立封装业务逻辑；主服务统一注册工具。
- 提供一个**天气插件**（weather），并附带一个**客户端示例**调用 `get_weather`。
- 完整可运行：`python app/run.py` 启动；`python app/weather_client.py` 测试。
- 配套工程化：`requirements.txt`、`.env.example`、`README.md`、基本单测、lint/格式化配置。

## 目录结构（必须与此一致）
app/
├── plugins/
│   ├── init.py
│   ├── base.py
│   └── weather/
│       ├── init.py
│       └── plugin.py
├── run.py
└── weather_client.py
requirements.txt
README.md
.env.example
pyproject.toml   # black/isort/ruff 配置
tests/
└── test_weather.py
## 关键技术与约束
- Python 3.10+
- 依赖：`fastmcp`、`httpx`、`pydantic`、`python-dotenv`、`uvloop`（Linux/mac 可选）、测试用 `pytest`、格式化 `black isort ruff`
- 异步优先：插件内对外部请求使用 `httpx.AsyncClient`
- 统一日志：标准库 `logging`，INFO 级别，带请求 trace id（简单 uuid4）
- 配置：从环境变量读取（支持 `.env`），如 `WEATHER_API_BASE`、`WEATHER_API_KEY`（可用 open-meteo 无 Key 方案作为默认；若提供 KEY 则走有 Key 的供应商）
- 错误处理：插件方法内用 try/except，抛出带错误码/信息的 MCP 友好异常；主服务打印关键信息

## 业务需求
### 插件基类（`app/plugins/base.py`）
- `BasePlugin`：
  - 属性：`name: str`
  - 方法：`tools()`（返回要注册到 MCP 的 **工具函数列表**）
  - 工具函数应支持 docstring（描述）、参数注解与 pydantic 校验（如有）
  - 提供简单的 `json_ok(data)` 与 `json_err(code, message, detail=None)` 帮助函数

### 天气插件（`app/plugins/weather/plugin.py` + `__init__.py`）
- 类：`WeatherPlugin(BasePlugin)`
- 工具：`get_weather(city: str) -> dict`
  - 输入：城市名（必填）
  - 处理：
    1. 使用地理编码服务把 `city` 转为 `(lat, lon)`（优先 open-meteo 的 geocoding，无需 key；或使用 Nominatim，带 UA 并限流）
    2. 调用天气服务获取当前天气：温度（°C）、风速、天气代码/描述、观测时间
  - 输出：`{"city": "...", "lat": ..., "lon": ..., "temperature_c": 27.1, "windspeed": 3.4, "observed_at": "...", "provider": "open-meteo"}`
  - 错误：返回 `json_err("GEO_FAIL", "...")` 或 `json_err("WEATHER_FAIL", "...")`
- `__init__.py` 中实例化并导出 `weather_plugin`

### 主服务器（`app/run.py`）
- 创建 MCP Server（使用 fastmcp 的装饰器或对象 API）
- 发现并注册插件工具：从 `plugins` 包中导入 `weather_plugin`，遍历其 `tools()` 注册
- 开启 **SSE** 服务（路径 `/sse`，端口 8010）；可选同时提供 stdio 启动方式（命令行参数切换）
- 打印已注册工具清单

### 客户端示例（`app/weather_client.py`）
- 使用 `fastmcp.Client` 连接 `http://localhost:8010/sse`
- 调用 `get_weather`，参数：`{"city": "beijing"}`，打印结果
- 演示错误处理（try/except）

## 工程文件
### `requirements.txt`
列出：`fastmcp`, `httpx`, `pydantic`, `python-dotenv`, `uvloop; platform_system!="Windows"`, `pytest`, `black`, `isort`, `ruff`

### `.env.example`

