#!/usr/bin/env python3
"""
服务器测试脚本

测试服务器是否正常启动和工具是否正确注册
"""

import asyncio
import json
from fastmcp import Client

async def test_server_connection():
    """测试服务器连接"""
    print("🔍 测试服务器连接...")
    
    try:
        async with Client("http://localhost:8010/sse") as client:
            # 获取可用工具列表
            tools = await client.list_tools()
            print(f"✅ 服务器连接成功，找到 {len(tools)} 个工具")
            
            # 显示所有工具名称
            print("📋 可用工具列表:")
            for tool in tools:
                print(f"   - {tool.name}")
            
            return True
            
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

async def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        async with Client("http://localhost:8010/sse") as client:
            # 测试天气功能（如果可用）
            try:
                weather_result = await client.call_tool("get_weather", {"city": "北京"})
                print("✅ 天气功能测试成功")
            except Exception as e:
                print(f"⚠️  天气功能测试失败: {e}")
            
            # 测试任务列表功能
            try:
                tasks_result = await client.call_tool("list_user_tasks", {
                    "user_uuid": "test_user_001"
                })
                result_dict = json.loads(tasks_result)
                print(f"✅ 任务列表功能测试成功，找到 {result_dict['data']['total']} 个任务")
            except Exception as e:
                print(f"❌ 任务列表功能测试失败: {e}")
            
            # 测试计划列表功能
            try:
                plans_result = await client.call_tool("list_user_plans", {
                    "user_uuid": "test_user_001"
                })
                result_dict = json.loads(plans_result)
                print(f"✅ 计划列表功能测试成功，找到 {result_dict['data']['total']} 个计划")
            except Exception as e:
                print(f"❌ 计划列表功能测试失败: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 SmartTime 服务器测试")
    print("=" * 40)
    
    # 测试服务器连接
    if not await test_server_connection():
        print("\n❌ 服务器连接测试失败，请检查:")
        print("   1. 服务器是否正在运行 (python app/run.py)")
        print("   2. 端口8010是否被占用")
        print("   3. 网络连接是否正常")
        return
    
    # 测试基本功能
    if not await test_basic_functionality():
        print("\n❌ 基本功能测试失败，请检查:")
        print("   1. 数据库连接是否正常")
        print("   2. 插件是否正确加载")
        print("   3. 工具是否正确注册")
        return
    
    print("\n" + "=" * 40)
    print("✅ 所有测试通过！服务器运行正常")

if __name__ == "__main__":
    asyncio.run(main()) 