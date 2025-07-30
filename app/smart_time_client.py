#!/usr/bin/env python3
"""
SmartTime 客户端使用示例

展示如何使用更新后的 SmartTime 系统
"""

import asyncio
import json
from datetime import datetime, timedelta
from fastmcp import Client

async def example_task_management(client):
    """任务管理示例"""
    print("📋 任务管理示例")
    print("-" * 30)
    
    # 1. 创建任务
    task_data = {
        "intent": "add_schedule",
        "uuid": "demo_user_001",
        "title": "完成项目需求分析",
        "description": "分析用户需求，编写需求文档，与产品经理确认功能点",
        "source_type": "agent",
        "status": "todo",
        "priority": "high",
        "estimated_duration": 180,
        "deadline": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "tags": "项目,需求分析,文档",
        "parent_task_id": None,
        "agent_origin": "PlanningAgent"
    }
    
    print("1. 创建任务...")
    result = await client.call_tool("process_agent_intent", {
        "json_data": json.dumps(task_data)
    })
    if isinstance(result, list):
        result = result[0]
    if hasattr(result, 'text'):
        result = result.text
    result_dict = json.loads(result)
    
    if result_dict['success']:
        task_id = result_dict['data']['task_id']
        print(f"✅ 任务创建成功，ID: {task_id}")
        
        # 2. 获取任务详情
        print("\n2. 获取任务详情...")
        task_info = await client.call_tool("get_task_info", {"task_id": str(task_id)})
        if isinstance(task_info, list):
            task_info = task_info[0]
        if hasattr(task_info, 'text'):
            task_info = task_info.text
        task_info_dict = json.loads(task_info)
        
        if task_info_dict['success']:
            task = task_info_dict['data']['task']
            print(f"✅ 任务标题: {task['title']}")
            print(f"   状态: {task['status']}")
            print(f"   优先级: {task['priority']}")
            print(f"   截止时间: {task['deadline']}")
        
        # 3. 更新任务状态
        print("\n3. 更新任务状态...")
        update_data = {
            "status": "in_progress",
            "description": "正在分析用户需求，已完成初步调研"
        }
        
        update_result = await client.call_tool("update_task", {
            "task_id": str(task_id),
            "updates": json.dumps(update_data)
        })
        if isinstance(update_result, list):
            update_result = update_result[0]
        if hasattr(update_result, 'text'):
            update_result = update_result.text
        update_dict = json.loads(update_result)
        
        if update_dict['success']:
            print("✅ 任务状态更新成功")
        
        return task_id
    else:
        print(f"❌ 任务创建失败: {result_dict['error']}")
        return None

async def example_plan_management(client, task_id=None):
    """计划管理示例"""
    print("\n📅 计划管理示例")
    print("-" * 30)
    
    # 1. 创建计划
    plan_data = {
        "intent": "plan_time",
        "uuid": "demo_user_001",
        "title": "需求分析会议",
        "description": "与产品经理和开发团队讨论需求分析结果",
        "start_time": (datetime.now() + timedelta(days=2, hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": (datetime.now() + timedelta(days=2, hours=16)).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": task_id,
        "is_all_day": False,
        "tags": "会议,需求分析,团队协作",
        "repeat_rule": None,
        "repeat_end_date": None,
        "reminder_minutes": 30,
        "reminder_type": "push",
        "status": "scheduled",
        "plan_source": "agent",
        "agent_origin": "PlanningAgent",
        "pomodoro_count": 0
    }
    
    print("1. 创建计划...")
    result = await client.call_tool("process_agent_intent", {
        "json_data": json.dumps(plan_data)
    })
    if isinstance(result, list):
        result = result[0]
    if hasattr(result, 'text'):
        result = result.text
    result_dict = json.loads(result)
    
    if result_dict['success']:
        plan_id = result_dict['data']['plan_id']
        print(f"✅ 计划创建成功，ID: {plan_id}")
        
        # 2. 获取计划详情
        print("\n2. 获取计划详情...")
        plan_info = await client.call_tool("get_plan_info", {"plan_id": str(plan_id)})
        if isinstance(plan_info, list):
            plan_info = plan_info[0]
        if hasattr(plan_info, 'text'):
            plan_info = plan_info.text
        plan_info_dict = json.loads(plan_info)
        
        if plan_info_dict['success']:
            plan = plan_info_dict['data']['plan']
            print(f"✅ 计划标题: {plan['title']}")
            print(f"   开始时间: {plan['start_time']}")
            print(f"   结束时间: {plan['end_time']}")
            print(f"   状态: {plan['status']}")
            print(f"   提醒时间: {plan['reminder_minutes']}分钟前")
        
        # 3. 更新计划状态
        print("\n3. 更新计划状态...")
        update_data = {
            "status": "in_progress",
            "actual_start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        update_result = await client.call_tool("update_plan", {
            "plan_id": str(plan_id),
            "updates": json.dumps(update_data)
        })
        if isinstance(update_result, list):
            update_result = update_result[0]
        if hasattr(update_result, 'text'):
            update_result = update_result.text
        update_dict = json.loads(update_result)
        
        if update_dict['success']:
            print("✅ 计划状态更新成功")
        
        return plan_id
    else:
        print(f"❌ 计划创建失败: {result_dict['error']}")
        return None

async def example_list_operations(client):
    """列表查询示例"""
    print("\n📊 列表查询示例")
    print("-" * 30)
    
    # 1. 获取用户任务列表
    print("1. 获取用户任务列表...")
    tasks_result = await client.call_tool("list_user_tasks", {
        "user_uuid": "demo_user_001"
    })
    if isinstance(tasks_result, list):
        tasks_result = tasks_result[0]
    if hasattr(tasks_result, 'text'):
        tasks_result = tasks_result.text
    tasks_dict = json.loads(tasks_result)
    
    if tasks_dict['success']:
        tasks = tasks_dict['data']['tasks']
        print(f"✅ 找到 {len(tasks)} 个任务")
        for i, task in enumerate(tasks[:3], 1):  # 只显示前3个
            print(f"   {i}. {task['title']} ({task['status']})")
    
    # 2. 获取用户计划列表
    print("\n2. 获取用户计划列表...")
    plans_result = await client.call_tool("list_user_plans", {
        "user_uuid": "demo_user_001"
    })
    if isinstance(plans_result, list):
        plans_result = plans_result[0]
    if hasattr(plans_result, 'text'):
        plans_result = plans_result.text
    plans_dict = json.loads(plans_result)
    
    if plans_dict['success']:
        plans = plans_dict['data']['plans']
        print(f"✅ 找到 {len(plans)} 个计划")
        for i, plan in enumerate(plans[:3], 1):  # 只显示前3个
            print(f"   {i}. {plan['title']} ({plan['status']})")
    
    # 3. 获取即将到来的计划
    print("\n3. 获取即将到来的计划...")
    upcoming_result = await client.call_tool("get_upcoming_plans", {
        "user_uuid": "demo_user_001",
        "hours": 72  # 未来3天
    })
    if isinstance(upcoming_result, list):
        upcoming_result = upcoming_result[0]
    if hasattr(upcoming_result, 'text'):
        upcoming_result = upcoming_result.text
    upcoming_dict = json.loads(upcoming_result)
    
    if upcoming_dict['success']:
        upcoming_plans = upcoming_dict['data']['plans']
        print(f"✅ 未来72小时内有 {len(upcoming_plans)} 个计划")
        for i, plan in enumerate(upcoming_plans[:3], 1):  # 只显示前3个
            print(f"   {i}. {plan['title']} - {plan['start_time']}")

async def example_agent_integration(client):
    """Agent集成示例"""
    print("\n🤖 Agent集成示例")
    print("-" * 30)
    
    # 模拟Agent输出的复杂JSON数据
    agent_output = {
        "intent": "add_schedule",
        "uuid": "demo_user_001",
        "title": "准备技术分享",
        "description": "准备下周三的技术分享内容，主题是'微服务架构设计'",
        "source_type": "agent",
        "status": "todo",
        "priority": "medium",
        "estimated_duration": 240,
        "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
        "tags": "技术分享,微服务,架构",
        "parent_task_id": None,
        "agent_origin": "SmartAssistant"
    }
    
    print("处理Agent输出...")
    result = await client.call_tool("process_agent_intent", {
        "json_data": json.dumps(agent_output)
    })
    if isinstance(result, list):
        result = result[0]
    if hasattr(result, 'text'):
        result = result.text
    result_dict = json.loads(result)
    
    if result_dict['success']:
        print("✅ Agent意图处理成功")
        print(f"   创建的任务ID: {result_dict['data']['task_id']}")
        print(f"   意图类型: {result_dict['data']['intent']}")
    else:
        print(f"❌ Agent意图处理失败: {result_dict['error']}")

async def main():
    """主函数"""
    print("🚀 SmartTime 客户端使用示例")
    print("=" * 50)
    
    try:
        # 使用单个客户端连接
        async with Client("http://localhost:8010/sse") as client:
            # 任务管理示例
            task_id = await example_task_management(client)
            
            # 计划管理示例
            plan_id = await example_plan_management(client, task_id)
            
            # 列表查询示例
            await example_list_operations(client)
            
            # Agent集成示例
            await example_agent_integration(client)
        
        print("\n" + "=" * 50)
        print("✅ 所有示例执行完成！")
        print("\n💡 提示:")
        print("   - 确保服务器正在运行 (python app/run.py)")
        print("   - 检查数据库连接配置")
        print("   - 查看日志了解详细执行情况")
        
    except Exception as e:
        print(f"\n❌ 示例执行过程中出现错误: {e}")
        print("\n🔧 故障排除:")
        print("   1. 确保服务器正在运行")
        print("   2. 检查网络连接")
        print("   3. 验证数据库配置")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行示例
    asyncio.run(main()) 