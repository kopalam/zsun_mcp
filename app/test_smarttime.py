#!/usr/bin/env python3
"""
SmartTime 系统测试脚本

测试更新后的数据库结构和插件功能
"""

import asyncio
import json
from datetime import datetime, timedelta
from plugins.smart import smart_processor, task_plugin, plan_plugin

async def test_task_creation():
    """测试任务创建"""
    print("=== 测试任务创建 ===")
    
    # 创建任务数据
    task_data = {
        "intent": "add_schedule",
        "uuid": "test_user_12345",
        "title": "测试任务 - 完成项目文档",
        "description": "编写项目技术文档，包括API设计和数据库设计",
        "source_type": "agent",
        "status": "todo",
        "priority": "high",
        "estimated_duration": 120,
        "deadline": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
        "tags": "项目,文档,工作",
        "parent_task_id": None,
        "agent_origin": "TestAgent"
    }
    
    # 处理任务创建
    result = await smart_processor.process_agent_json(json.dumps(task_data))
    result_dict = json.loads(result)
    
    print(f"任务创建结果: {result_dict['success']}")
    print(f"消息: {result_dict['message']}")
    
    if result_dict['success']:
        task_id = result_dict['data']['task_id']
        print(f"创建的任务ID: {task_id}")
        return task_id
    else:
        print(f"错误: {result_dict['error']}")
        return None

async def test_plan_creation(task_id=None):
    """测试计划创建"""
    print("\n=== 测试计划创建 ===")
    
    # 创建计划数据
    plan_data = {
        "intent": "plan_time",
        "uuid": "test_user_12345",
        "title": "测试计划 - 项目文档编写时间",
        "description": "明天下午2点到4点专门用于编写项目文档",
        "start_time": (datetime.now() + timedelta(days=1, hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": (datetime.now() + timedelta(days=1, hours=16)).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": task_id,
        "is_all_day": False,
        "tags": "项目,文档,工作",
        "repeat_rule": None,
        "repeat_end_date": None,
        "reminder_minutes": 15,
        "reminder_type": "push",
        "status": "scheduled",
        "plan_source": "agent",
        "agent_origin": "TestAgent",
        "pomodoro_count": 0
    }
    
    # 处理计划创建
    result = await smart_processor.process_agent_json(json.dumps(plan_data))
    result_dict = json.loads(result)
    
    print(f"计划创建结果: {result_dict['success']}")
    print(f"消息: {result_dict['message']}")
    
    if result_dict['success']:
        plan_id = result_dict['data']['plan_id']
        print(f"创建的计划ID: {plan_id}")
        return plan_id
    else:
        print(f"错误: {result_dict['error']}")
        return None

async def test_list_operations():
    """测试列表查询操作"""
    print("\n=== 测试列表查询操作 ===")
    
    # 获取任务列表
    tasks_result = await task_plugin.list_tasks("test_user_12345")
    tasks_dict = json.loads(tasks_result)
    
    print(f"任务列表查询结果: {tasks_dict['success']}")
    print(f"任务数量: {tasks_dict['data']['total']}")
    
    # 获取计划列表
    plans_result = await plan_plugin.list_plans("test_user_12345")
    plans_dict = json.loads(plans_result)
    
    print(f"计划列表查询结果: {plans_dict['success']}")
    print(f"计划数量: {plans_dict['data']['total']}")
    
    # 获取即将到来的计划
    upcoming_result = await plan_plugin.get_upcoming_plans("test_user_12345", 48)
    upcoming_dict = json.loads(upcoming_result)
    
    print(f"即将到来的计划查询结果: {upcoming_dict['success']}")
    print(f"即将到来的计划数量: {upcoming_dict['data']['total']}")

async def test_update_operations(task_id, plan_id):
    """测试更新操作"""
    print("\n=== 测试更新操作 ===")
    
    if task_id:
        # 更新任务
        task_updates = {
            "status": "in_progress",
            "priority": "high",
            "description": "更新后的任务描述 - 正在编写项目技术文档"
        }
        
        update_result = await task_plugin.update_task(str(task_id), json.dumps(task_updates))
        update_dict = json.loads(update_result)
        
        print(f"任务更新结果: {update_dict['success']}")
        print(f"更新消息: {update_dict['message']}")
    
    if plan_id:
        # 更新计划
        plan_updates = {
            "status": "in_progress",
            "actual_start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reminder_minutes": 30
        }
        
        update_result = await plan_plugin.update_plan(str(plan_id), json.dumps(plan_updates))
        update_dict = json.loads(update_result)
        
        print(f"计划更新结果: {update_dict['success']}")
        print(f"更新消息: {update_dict['message']}")

async def test_get_operations(task_id, plan_id):
    """测试获取详情操作"""
    print("\n=== 测试获取详情操作 ===")
    
    if task_id:
        # 获取任务详情
        task_result = await task_plugin.get_task(str(task_id))
        task_dict = json.loads(task_result)
        
        print(f"任务详情查询结果: {task_dict['success']}")
        if task_dict['success']:
            task_data = task_dict['data']['task']
            print(f"任务标题: {task_data['title']}")
            print(f"任务状态: {task_data['status']}")
            print(f"任务优先级: {task_data['priority']}")
    
    if plan_id:
        # 获取计划详情
        plan_result = await plan_plugin.get_plan(str(plan_id))
        plan_dict = json.loads(plan_result)
        
        print(f"计划详情查询结果: {plan_dict['success']}")
        if plan_dict['success']:
            plan_data = plan_dict['data']['plan']
            print(f"计划标题: {plan_data['title']}")
            print(f"计划状态: {plan_data['status']}")
            print(f"开始时间: {plan_data['start_time']}")

async def main():
    """主测试函数"""
    print("🚀 开始测试 SmartTime 系统")
    print("=" * 50)
    
    try:
        # 测试任务创建
        task_id = await test_task_creation()
        
        # 测试计划创建
        plan_id = await test_plan_creation(task_id)
        
        # 测试列表查询
        await test_list_operations()
        
        # 测试更新操作
        await test_update_operations(task_id, plan_id)
        
        # 测试获取详情
        await test_get_operations(task_id, plan_id)
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 