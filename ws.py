import asyncio
import json
import websockets
import socket

BASE_URI = "ws://120.25.63.187:10095"
# 尝试不同的路径
PATHS = ["", "/ws", "/realtime", "/websocket", "/socket", "/api/ws", "/api/realtime"]

async def test_connection():
    """测试基本网络连接"""
    try:
        # 解析主机和端口
        host = "120.25.63.187"
        port = 10095
        
        # 测试 TCP 连接
        print(f"正在测试连接到 {host}:{port}...")
        reader, writer = await asyncio.open_connection(host, port)
        print("✓ TCP 连接成功")
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as e:
        print(f"✗ TCP 连接失败: {e}")
        return False

async def test_websocket_connection(uri, method_name, method_params):
    """测试特定的 WebSocket 连接"""
    try:
        print(f"  尝试 {method_name}: {method_params}")
        async with websockets.connect(uri, **method_params) as ws:
            print(f"  ✓ WebSocket 连接成功! ({uri})")
            
            # 发送配置消息
            config_msg = {
                "signal": "start",
                "nbest": 1,
                "enable_timestamp": True,
                "chunk_size": 5,
                "chunk_size_padding": 1,
                "sample_rate": 16000,
                "audio_format": "pcm",
                "itn": True
            }
            
            print("  发送配置消息...")
            await ws.send(json.dumps(config_msg))
            
            print("  发送结束信号...")
            await ws.send(json.dumps({"signal": "end"}))
            
            # 接收消息
            print("  等待服务器响应...")
            try:
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
                    print("  <<", msg)
            except asyncio.TimeoutError:
                print("  接收超时，连接正常但无更多消息")
            except Exception as e:
                print(f"  接收消息时出错: {e}")
            
            return True  # 成功连接
            
    except websockets.exceptions.InvalidMessage as e:
        print(f"  ✗ 无效消息: {e}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"  ✗ 连接关闭: {e}")
    except Exception as e:
        print(f"  ✗ 其他错误: {e}")
    
    return False

async def main():
    # 首先测试基本连接
    if not await test_connection():
        print("无法建立基本网络连接，请检查服务器是否运行")
        return
    
    print(f"正在尝试 WebSocket 连接到 {BASE_URI}...")
    
    # 尝试不同的路径和连接方式
    connection_methods = [
        {"subprotocols": ["binary"]},
        {"subprotocols": None},
        {}  # 无额外参数
    ]
    
    success = False
    
    for path in PATHS:
        uri = BASE_URI + path
        print(f"\n测试路径: {uri}")
        
        for method in connection_methods:
            if await test_websocket_connection(uri, "连接方法", method):
                success = True
                break
        
        if success:
            break
    
    if not success:
        print("\n所有路径和连接方法都失败了")
        print("\n可能的原因:")
        print("1. 服务器不是 WebSocket 服务器")
        print("2. 需要特定的认证或头部信息")
        print("3. 服务器需要特定的协议版本")
        print("4. 服务器可能只支持特定的子协议")
        
        # 尝试检查服务器返回的内容
        print("\n尝试检查服务器响应...")
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://120.25.63.187:10095") as response:
                    print(f"HTTP 响应状态: {response.status}")
                    print(f"响应头: {dict(response.headers)}")
                    text = await response.text()
                    print(f"响应内容: {text[:200]}...")
        except Exception as e:
            print(f"无法获取 HTTP 响应: {e}")

if __name__ == "__main__":
    asyncio.run(main())