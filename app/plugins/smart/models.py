from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    """任务状态枚举"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"

class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskSourceType(str, Enum):
    """任务来源类型枚举"""
    MANUAL = "manual"
    VOICE = "voice"
    AGENT = "agent"
    IMPORT = "import"

class PlanStatus(str, Enum):
    """计划状态枚举"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"

class ReminderType(str, Enum):
    """提醒类型枚举"""
    PUSH = "push"
    NONE = "none"

class PlanSource(str, Enum):
    """计划来源枚举"""
    MANUAL = "manual"
    AGENT = "agent"
    IMPORT = "import"
    SYSTEM = "system"

class Task(BaseModel):
    """任务数据模型"""
    id: Optional[int] = None
    uuid: str = Field(..., description="用户唯一标识")
    title: str = Field(..., description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    source_type: TaskSourceType = Field(TaskSourceType.MANUAL, description="任务创建来源")
    status: TaskStatus = Field(TaskStatus.TODO, description="任务状态")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="优先级")
    estimated_duration: Optional[int] = Field(None, description="预估耗时（分钟）")
    deadline: Optional[datetime] = Field(None, description="截止时间")
    tags: Optional[str] = Field(None, description="任务标签（逗号分隔）")
    parent_task_id: Optional[int] = Field(None, description="父任务ID")
    agent_origin: Optional[str] = Field(None, description="由哪个Agent创建")
    is_recurring_template: bool = Field(False, description="是否为重复任务的模板")
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    is_deleted: bool = Field(False, description="是否已删除")

    def dict(self, **kwargs):
        """自定义字典转换，处理 datetime 序列化"""
        data = super().dict(**kwargs)
        # 将 datetime 对象转换为 ISO 格式字符串
        for field in ['deadline', 'created_time', 'updated_time']:
            if field in data and data[field] is not None:
                if isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
        return data

class Plan(BaseModel):
    """计划数据模型"""
    id: Optional[int] = None
    uuid: str = Field(..., description="用户唯一标识")
    task_id: Optional[int] = Field(None, description="关联的任务ID")
    start_time: datetime = Field(..., description="计划开始时间")
    end_time: datetime = Field(..., description="计划结束时间")
    is_all_day: bool = Field(False, description="是否为全天事件")
    title: Optional[str] = Field(None, description="计划标题")
    description: Optional[str] = Field(None, description="可选说明")
    tags: Optional[str] = Field(None, description="标签")
    repeat_rule: Optional[str] = Field(None, description="重复规则")
    repeat_end_date: Optional[date] = Field(None, description="重复截止时间")
    reminder_minutes: int = Field(10, description="提前提醒时间（分钟）")
    reminder_type: ReminderType = Field(ReminderType.PUSH, description="提醒类型")
    status: PlanStatus = Field(PlanStatus.SCHEDULED, description="计划执行状态")
    actual_start_time: Optional[datetime] = Field(None, description="实际开始时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    completion_time: Optional[datetime] = Field(None, description="标记完成的时间")
    plan_source: PlanSource = Field(PlanSource.AGENT, description="生成来源")
    agent_origin: Optional[str] = Field(None, description="触发该计划的Agent名")
    pomodoro_count: int = Field(0, description="完成的番茄钟次数")
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    is_deleted: bool = Field(False, description="是否已删除")

    def dict(self, **kwargs):
        """自定义字典转换，处理 datetime 序列化"""
        data = super().dict(**kwargs)
        # 将 datetime 对象转换为 ISO 格式字符串
        datetime_fields = ['start_time', 'end_time', 'actual_start_time', 'actual_end_time', 
                          'completion_time', 'created_time', 'updated_time']
        for field in datetime_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
        # 处理 date 对象
        if 'repeat_end_date' in data and data['repeat_end_date'] is not None:
            if isinstance(data['repeat_end_date'], date):
                data['repeat_end_date'] = data['repeat_end_date'].isoformat()
        return data

class AgentIntent(BaseModel):
    """Agent意图数据模型"""
    intent: str = Field(..., description="意图类型：add_schedule 或 plan_time")
    uuid: str = Field(..., description="用户唯一标识")
    
    # 任务相关字段
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="描述")
    source_type: Optional[str] = Field("agent", description="任务创建来源")
    status: Optional[str] = Field("todo", description="任务状态")
    priority: Optional[str] = Field("medium", description="优先级")
    estimated_duration: Optional[int] = Field(None, description="预估耗时（分钟）")
    deadline: Optional[str] = Field(None, description="截止时间")
    tags: Optional[str] = Field(None, description="标签")
    parent_task_id: Optional[int] = Field(None, description="父任务ID")
    agent_origin: Optional[str] = Field(None, description="Agent来源")
    
    # 计划相关字段
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    task_id: Optional[int] = Field(None, description="关联任务ID")
    is_all_day: Optional[bool] = Field(False, description="是否全天")
    repeat_rule: Optional[str] = Field(None, description="重复规则")
    repeat_end_date: Optional[str] = Field(None, description="重复截止时间")
    reminder_minutes: Optional[int] = Field(10, description="提醒时间")
    reminder_type: Optional[str] = Field("push", description="提醒类型")
    plan_source: Optional[str] = Field("agent", description="计划来源")
    actual_start_time: Optional[str] = Field(None, description="实际开始时间")
    actual_end_time: Optional[str] = Field(None, description="实际结束时间")
    completion_time: Optional[str] = Field(None, description="完成时间")
    pomodoro_count: Optional[int] = Field(0, description="番茄钟次数")

class ProcessingResult(BaseModel):
    """处理结果数据模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="处理消息")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据")
    error: Optional[str] = Field(None, description="错误信息") 