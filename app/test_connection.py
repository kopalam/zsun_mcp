#!/usr/bin/env python3
"""
简单的连接测试脚本
"""

import asyncio
import json
from fastmcp import Client

async def test_basic_connection():
    """测试基本连接"""
    print("🔍 测试基本连接...")
    
    try:
        async with Client("http://localhost:8010/sse") as client:
            print("✅ 客户端连接成功")
            
            # 测试简单的工具调用
            print("🔧 测试工具调用...")
            result = await client.call_tool("list_user_tasks", {
                "user_uuid": "demo_user_001"
            })
            
            print(f"📋 调用结果类型: {type(result)}")
            if isinstance(result, list):
                result = result[0]
            if hasattr(result, 'text'):
                result = result.text
            
            print(f"📄 结果内容: {result}")
            
            try:
                result_dict = json.loads(result)
                print("✅ JSON解析成功")
                print(f"📊 响应结构: {list(result_dict.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_event_loop():
    """测试事件循环"""
    print("\n🔄 测试事件循环...")
    
    try:
        # 检查当前事件循环
        loop = asyncio.get_running_loop()
        print(f"✅ 当前事件循环: {loop}")
        print(f"   循环状态: {'运行中' if not loop.is_closed() else '已关闭'}")
        
        # 创建新的事件循环（如果需要）
        if loop.is_closed():
            print("⚠️  事件循环已关闭，尝试创建新的...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print("✅ 新事件循环创建成功")
        
    except RuntimeError as e:
        print(f"❌ 事件循环错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

async def main():
    """主函数"""
    print("🚀 FastMCP 连接测试")
    print("=" * 40)
    
    # 测试事件循环
    await test_event_loop()
    
    # 测试连接
    await test_basic_connection()
    
    print("\n" + "=" * 40)
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 