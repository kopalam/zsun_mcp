# WebSocket 兼容性说明

本文档详细说明了 FastMCP API 框架与 [mcp-endpoint-server](https://github.com/xinnan-tech/mcp-endpoint-server) 的 WebSocket 兼容性实现。

## 🎯 兼容性目标

实现与 mcp-endpoint-server 完全兼容的 WebSocket 通信协议，支持：
- 双端点架构（工具端 + 小智端）
- JSON-RPC 2.0 标准协议
- 消息转发机制
- 连接管理和 UUID 映射
- 错误处理和响应格式

## 🏗️ 架构设计

### 核心组件

1. **ConnectionManager** (`app/core/connection_manager.py`)
   - 管理 WebSocket 连接
   - 处理连接注册和注销
   - 维护 UUID 映射关系
   - 提供消息转发功能

2. **WebSocketHandler** (`app/handlers/websocket_handler.py`)
   - 处理 WebSocket 消息
   - 实现 JSON-RPC 消息转换
   - 管理消息转发逻辑

3. **JSONRPCProtocol** (`app/utils/jsonrpc.py`)
   - JSON-RPC 2.0 协议实现
   - 消息格式化和解析
   - 错误响应生成

4. **BasePlugin** (`app/plugins/base.py`)
   - 扩展支持 JSON-RPC 响应格式
   - 保持向后兼容性

## 🔌 WebSocket 端点

### 工具端端点
```
ws://host:port/mcp_endpoint/mcp/?token=your_token
```

### 小智端端点
```
ws://host:port/mcp_endpoint/call/?token=your_token
```

### 健康检查端点
```
http://host:port/mcp_endpoint/health
```

## 📋 协议规范

### JSON-RPC 2.0 消息格式

#### 请求消息
```json
{
  "jsonrpc": "2.0",
  "method": "method_name",
  "params": {...},
  "id": "request_id"
}
```

#### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {...},
  "id": "request_id"
}
```

#### 错误响应
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {...}
  },
  "id": "request_id"
}
```

### 错误代码

| 代码 | 名称 | 说明 |
|------|------|------|
| -32700 | Parse error | JSON 解析错误 |
| -32600 | Invalid Request | 无效请求 |
| -32601 | Method not found | 方法未找到 |
| -32602 | Invalid params | 无效参数 |
| -32603 | Internal error | 内部错误 |
| -32001 | Tool not connected | 工具端未连接 |
| -32002 | Forward failed | 转发失败 |
| -32003 | Connection error | 连接错误 |
| -32004 | Authentication error | 认证错误 |

## 🔄 消息转发机制

### ID 转换流程

1. **小智端 → 工具端**
   ```
   原始ID: "123"
   转换后: "uuid:123"
   ```

2. **工具端 → 小智端**
   ```
   转换后ID: "uuid:123"
   还原为: "123"
   ```

### 转发逻辑

1. 小智端发送消息时，系统自动转换消息ID
2. 消息转发给对应的工具端连接
3. 工具端响应时，系统还原消息ID
4. 响应转发回原始的小智端连接

## 🛠️ 使用方法

### 启动 WebSocket 服务器

```bash
python app/run.py --transport websocket --host 0.0.0.0 --port 8010
```

### 环境变量配置

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8010
SERVER_KEY=your_secret_key

# WebSocket配置
ENABLE_CORS=true
ALLOWED_ORIGINS=*

# 日志配置
LOG_LEVEL=INFO
```

### 客户端连接示例

#### Python 客户端
```python
import asyncio
import websockets
import json

async def test_websocket():
    # 连接到工具端
    uri = "ws://localhost:8010/mcp_endpoint/mcp/?token=default_key_123456"
    async with websockets.connect(uri) as websocket:
        # 发送请求
        request = {
            "jsonrpc": "2.0",
            "method": "get_weather",
            "params": {"city": "Beijing"},
            "id": 1
        }
        await websocket.send(json.dumps(request))
        
        # 接收响应
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(test_websocket())
```

#### JavaScript 客户端
```javascript
const ws = new WebSocket('ws://localhost:8010/mcp_endpoint/mcp/?token=default_key_123456');

ws.onopen = function() {
    const request = {
        jsonrpc: "2.0",
        method: "get_weather",
        params: {city: "Beijing"},
        id: 1
    };
    ws.send(JSON.stringify(request));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log(response);
};
```

## 🧪 测试

### 运行测试客户端

```bash
python app/websocket_client_test.py
```

### 测试内容

1. **健康检查测试**: 验证服务器状态
2. **工具端连接测试**: 测试工具端 WebSocket 连接
3. **小智端连接测试**: 测试小智端 WebSocket 连接
4. **消息转发测试**: 验证消息转发功能
5. **错误处理测试**: 测试错误响应格式

## 🔧 扩展开发

### 添加新的插件

1. 继承 `BasePlugin` 类
2. 实现 `tools()` 方法
3. 使用 `jsonrpc_ok()` 和 `jsonrpc_err()` 方法返回响应
4. 在 `app/plugins/__init__.py` 中注册插件

### 自定义认证

修改 `FastMCPAPIServer.validate_token_and_get_agent_id()` 方法实现自定义认证逻辑。

### 添加中间件

在 `run_websocket()` 方法中添加 FastAPI 中间件。

## 📊 性能优化

1. **连接池管理**: 复用 WebSocket 连接
2. **消息缓存**: 缓存频繁访问的数据
3. **异步处理**: 使用 asyncio 提高并发性能
4. **日志优化**: 合理设置日志级别

## 🐛 故障排除

### 常见问题

1. **连接失败**: 检查 token 和端点 URL
2. **消息格式错误**: 确保使用 JSON-RPC 2.0 格式
3. **转发失败**: 检查工具端连接状态
4. **认证失败**: 验证 SERVER_KEY 配置

### 调试技巧

1. 启用详细日志: `LOG_LEVEL=DEBUG`
2. 使用测试客户端验证功能
3. 检查网络连接和防火墙设置
4. 验证 JSON 消息格式

## 📚 参考资料

- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)
- [WebSocket RFC](https://tools.ietf.org/html/rfc6455)
- [mcp-endpoint-server 项目](https://github.com/xinnan-tech/mcp-endpoint-server)
- [FastAPI WebSocket 文档](https://fastapi.tiangolo.com/advanced/websockets/)
