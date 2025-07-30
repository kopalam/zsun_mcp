"""
智能时间管理系统使用示例

本文件包含Agent输出JSON的示例和系统使用方法
"""

# Agent输出JSON示例

# 1. 安排计划（插入 plan）
PLAN_EXAMPLE = {
    "intent": "plan_time",
    "title": "撰写MVP项目计划书",
    "description": "明天下午三点到四点完成项目的MVP项目计划书，请准备好相关资料和工具。",
    "start_time": "2025-07-13 15:00:00",
    "end_time": "2025-07-13 16:00:00",
    "task_id": None,
    "is_all_day": False,
    "tags": "项目计划,工作",
    "reminder_minutes": 10,
    "reminder_type": "push",
    "status": "scheduled",
    "plan_source": "agent",
    "agent_origin": "PlanningAgent",
    "uuid": "user_12345"
}

# 2. 添加任务（插入 task）
TASK_EXAMPLE = {
    "intent": "add_schedule",
    "title": "与甘总面谈",
    "description": "与甘总约了下周四到公司面谈，时间为下午两点。请提前准备相关资料并准时参加。",
    "source_type": "agent",
    "status": "todo",
    "priority": "medium",
    "estimated_duration": 60,
    "deadline": "2025-07-18 14:00:00",
    "tags": "会议,工作",
    "parent_task_id": None,
    "agent_origin": "ScheduleAgent",
    "uuid": "user_12345"
}

# 3. 高优先级任务示例
HIGH_PRIORITY_TASK = {
    "intent": "add_schedule",
    "title": "紧急修复生产环境bug",
    "description": "生产环境出现严重bug，需要立即修复。",
    "source_type": "agent",
    "status": "todo",
    "priority": "urgent",
    "estimated_duration": 120,
    "deadline": "2025-07-12 18:00:00",
    "tags": "紧急,修复,bug",
    "parent_task_id": None,
    "agent_origin": "EmergencyAgent",
    "uuid": "user_12345"
}

# 4. 全天计划示例
ALL_DAY_PLAN = {
    "intent": "plan_time",
    "title": "团队建设活动",
    "description": "全公司团队建设活动，包括户外拓展和聚餐。",
    "start_time": "2025-07-20 00:00:00",
    "end_time": "2025-07-20 23:59:59",
    "task_id": None,
    "is_all_day": True,
    "tags": "团队建设,活动",
    "reminder_minutes": 60,
    "reminder_type": "push",
    "status": "scheduled",
    "plan_source": "agent",
    "agent_origin": "HRAgent",
    "uuid": "user_12345"
}

# 使用示例代码

async def example_usage():
    """使用示例"""
    import json
    from app.plugins.smart import smart_processor
    
    # 1. 处理Agent意图 - 创建任务
    task_json = json.dumps(TASK_EXAMPLE)
    result = await smart_processor.process_agent_json(task_json)
    print("创建任务结果:", result.dict())
    
    # 2. 处理Agent意图 - 创建计划
    plan_json = json.dumps(PLAN_EXAMPLE)
    result = await smart_processor.process_agent_json(plan_json)
    print("创建计划结果:", result.dict())
    
    # 3. 获取用户任务列表
    result = await smart_processor.list_user_tasks("user_12345")
    print("用户任务列表:", result.dict())
    
    # 4. 获取用户计划列表
    result = await smart_processor.list_user_plans("user_12345")
    print("用户计划列表:", result.dict())
    
    # 5. 获取即将到来的计划
    result = await smart_processor.get_upcoming_plans("user_12345", hours=48)
    print("即将到来的计划:", result.dict())

# MCP工具使用示例

async def mcp_tool_examples():
    """MCP工具使用示例"""
    from app.mcp_smart_time import smart_time_mcp
    
    # 1. 处理Agent意图
    task_json = json.dumps(TASK_EXAMPLE)
    result = await smart_time_mcp.process_agent_intent(task_json)
    print("MCP处理任务结果:", result)
    
    # 2. 获取任务列表
    result = await smart_time_mcp.list_user_tasks("user_12345")
    print("MCP获取任务列表:", result)
    
    # 3. 获取计划列表
    result = await smart_time_mcp.list_user_plans("user_12345")
    print("MCP获取计划列表:", result)

if __name__ == "__main__":
    import asyncio
    
    # 运行示例
    asyncio.run(example_usage())
    asyncio.run(mcp_tool_examples()) 