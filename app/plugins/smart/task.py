import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..base import BasePlugin
from .models import Task, AgentIntent, ProcessingResult, TaskStatus, TaskPriority, TaskSourceType
from database import db_manager
import traceback
from database import db_manager, TaskORM
from sqlalchemy.future import select
from sqlalchemy import cast, String

class TaskPlugin(BasePlugin):
    """任务管理插件"""
    
    def __init__(self):
        super().__init__("Task Management Service")
    
    def _register_tools(self):
        """注册工具"""
        pass
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not datetime_str:
            return None
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
    
    def _parse_priority(self, priority_str: str) -> TaskPriority:
        """解析优先级"""
        try:
            return TaskPriority(priority_str.lower())
        except ValueError:
            return TaskPriority.MEDIUM
    
    def _parse_status(self, status_str: str) -> TaskStatus:
        """解析状态"""
        try:
            return TaskStatus(status_str.lower())
        except ValueError:
            return TaskStatus.TODO
    
    def _parse_source_type(self, source_type_str: str) -> TaskSourceType:
        """解析来源类型"""
        try:
            return TaskSourceType(source_type_str.lower())
        except ValueError:
            return TaskSourceType.AGENT
    
    def _dict_to_task(self, row: tuple) -> Task:
        """将数据库行转换为Task对象"""
        return Task(
            id=row[0],
            uuid=row[1],
            title=row[2],
            description=row[3],
            source_type=TaskSourceType(row[4]),
            status=TaskStatus(row[5]),
            priority=TaskPriority(row[6]),
            estimated_duration=row[7],
            deadline=row[8],
            tags=row[9],
            parent_task_id=row[10],
            agent_origin=row[11],
            is_recurring_template=bool(row[12]),
            created_time=row[13],
            updated_time=row[14],
            is_deleted=bool(row[15])
        )
    
    async def create_task(self, intent_data: AgentIntent) -> ProcessingResult:
        """创建任务
        Args:
            intent_data: Agent意图数据
        Returns:
            处理结果
        """
        try:
            from database import db_manager, TaskORM
            # 解析截止时间
            deadline = self._parse_datetime(intent_data.deadline)
            async with db_manager.get_session() as session:
                new_task = TaskORM(
                    uuid=intent_data.uuid,
                    title=intent_data.title,
                    description=intent_data.description,
                    source_type=self._parse_source_type(intent_data.source_type or "agent").value,
                    status=self._parse_status(intent_data.status or "todo").value,
                    priority=self._parse_priority(intent_data.priority or "medium").value,
                    estimated_duration=intent_data.estimated_duration,
                    deadline=deadline,
                    tags=intent_data.tags,
                    parent_task_id=intent_data.parent_task_id,
                    agent_origin=intent_data.agent_origin,
                    is_recurring_template=False,
                    created_time=datetime.now(),
                    updated_time=datetime.now()
                )
                session.add(new_task)
                await session.commit()
                await session.refresh(new_task)
                # 获取创建的任务
                task = self._dict_to_task((new_task.id, new_task.uuid, new_task.title, new_task.description, new_task.source_type, new_task.status, new_task.priority, new_task.estimated_duration, new_task.deadline, new_task.tags, new_task.parent_task_id, new_task.agent_origin, new_task.is_recurring_template, new_task.created_time, new_task.updated_time, new_task.is_deleted))
                return ProcessingResult(
                    success=True,
                    message=f"任务 '{task.title}' 创建成功",
                    data={
                        "task_id": new_task.id,
                        "task": task.dict(),
                        "intent": intent_data.intent
                    }
                )
        except Exception as e:
            print("创建任务异常:", e)
            print(traceback.format_exc())
            return ProcessingResult(
                success=False,
                message="创建任务失败",
                error=str(e)
            )
    
    async def _get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        query = "SELECT * FROM plugin_smart_tasks WHERE id = %s AND is_deleted = 0"
        result = await db_manager.execute_query(query, (task_id,))
        
        if result:
            return self._dict_to_task(result[0])
        return None
    
    async def get_task(self, task_id: str) -> str:
        """获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息JSON字符串
        """
        try:
            task = await self._get_task_by_id(int(task_id))
            
            if not task:
                result = ProcessingResult(
                    success=False,
                    message="任务不存在",
                    error="Task not found"
                )
            else:
                result = ProcessingResult(
                    success=True,
                    message="获取任务成功",
                    data={"task": task.dict()}
                )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="获取任务失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def update_task(self, task_id: str, updates: str) -> str:
        """更新任务
        
        Args:
            task_id: 任务ID
            updates: 更新字段JSON字符串
            
        Returns:
            更新结果JSON字符串
        """
        try:
            task = await self._get_task_by_id(int(task_id))
            if not task:
                result = ProcessingResult(
                    success=False,
                    message="任务不存在",
                    error="Task not found"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
            updates_dict = json.loads(updates)
            
            # 构建更新SQL
            set_clauses = []
            params = []
            
            for key, value in updates_dict.items():
                if hasattr(task, key):
                    if key == "priority" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_priority(value).value)
                    elif key == "status" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_status(value).value)
                    elif key == "source_type" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_source_type(value).value)
                    elif key == "deadline" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_datetime(value))
                    else:
                        set_clauses.append(f"{key} = %s")
                        params.append(value)
            
            if set_clauses:
                params.append(int(task_id))
                query = f"UPDATE plugin_smart_tasks SET {', '.join(set_clauses)} WHERE id = %s"
                await db_manager.execute_update(query, tuple(params))
                
                # 获取更新后的任务
                updated_task = await self._get_task_by_id(int(task_id))
                
                result = ProcessingResult(
                    success=True,
                    message=f"任务 '{updated_task.title}' 更新成功",
                    data={"task": updated_task.dict()}
                )
            else:
                result = ProcessingResult(
                    success=True,
                    message="没有需要更新的字段",
                    data={"task": task.dict()}
                )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="更新任务失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def delete_task(self, task_id: str) -> str:
        """删除任务（软删除）
        
        Args:
            task_id: 任务ID
            
        Returns:
            删除结果JSON字符串
        """
        try:
            task = await self._get_task_by_id(int(task_id))
            if not task:
                result = ProcessingResult(
                    success=False,
                    message="任务不存在",
                    error="Task not found"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
            query = "UPDATE plugin_smart_tasks SET is_deleted = 1 WHERE id = %s"
            await db_manager.execute_update(query, (int(task_id),))
            
            result = ProcessingResult(
                success=True,
                message=f"任务 '{task.title}' 删除成功",
                data={"deleted_task_id": task_id}
            )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="删除任务失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def list_tasks(self, user_uuid: str, status: str = None) -> str:
        """获取用户任务列表
        
        Args:
            user_uuid: 用户唯一标识
            status: 任务状态过滤（可选）
            
        Returns:
            任务列表JSON字符串
        """
        try:
            if status:
                query = "SELECT * FROM plugin_smart_tasks WHERE uuid = %s AND status = %s AND is_deleted = 0 ORDER BY created_time DESC"
                params = (user_uuid, self._parse_status(status).value)
            else:
                query = "SELECT * FROM plugin_smart_tasks WHERE uuid = %s AND is_deleted = 0 ORDER BY created_time DESC"
                params = (user_uuid,)
            
            result_rows = await db_manager.execute_query(query, params)
            tasks = [self._dict_to_task(row) for row in result_rows]
            
            result = ProcessingResult(
                success=True,
                message=f"获取到 {len(tasks)} 个任务",
                data={
                    "tasks": [task.dict() for task in tasks],
                    "total": len(tasks)
                }
            )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="获取任务列表失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def process_agent_intent(self, intent_data: AgentIntent) -> ProcessingResult:
        """处理Agent意图
        
        Args:
            intent_data: Agent意图数据
            
        Returns:
            处理结果
        """
        if intent_data.intent == "add_schedule":
            return await self.create_task(intent_data)
        else:
            return ProcessingResult(
                success=False,
                message="不支持的任务意图类型",
                error=f"Unsupported task intent: {intent_data.intent}"
            ) 

    async def find_duplicate_tasks(self, uuid: str, deadline: str, estimated_duration: int) -> list[Task]:
        """
        查找重复任务
        """
        deadline_dt = datetime.fromisoformat(deadline)  # deadline: '2025-07-17T15:00:00'
        async with db_manager.get_session() as session:
            stmt = select(TaskORM).where(
                TaskORM.uuid == uuid,
                TaskORM.deadline == deadline_dt,
                TaskORM.is_deleted == 0
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()
            print(f"11111---{uuid},{deadline},{estimated_duration}")

            print(f"排重结果{tasks}")
            # 你可以根据需要将 TaskORM 转为 Pydantic Task
            return [self._dict_to_task((t.id, t.uuid, t.title, t.description, t.source_type, t.status, t.priority, t.estimated_duration, t.deadline, t.tags, t.parent_task_id, t.agent_origin, t.is_recurring_template, t.created_time, t.updated_time, t.is_deleted)) for t in tasks]