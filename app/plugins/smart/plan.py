import json
from datetime import datetime, date
from typing import Dict, Any, Optional
from ..base import BasePlugin
from .models import Plan, AgentIntent, ProcessingResult, PlanStatus, ReminderType, PlanSource
from database import db_manager

class PlanPlugin(BasePlugin):
    """计划管理插件"""
    
    def __init__(self):
        super().__init__("Plan Management Service")
    
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
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
    
    def _parse_status(self, status_str: str) -> PlanStatus:
        """解析状态"""
        try:
            return PlanStatus(status_str.lower())
        except ValueError:
            return PlanStatus.SCHEDULED
    
    def _parse_reminder_type(self, reminder_type_str: str) -> ReminderType:
        """解析提醒类型"""
        try:
            return ReminderType(reminder_type_str.lower())
        except ValueError:
            return ReminderType.PUSH
    
    def _parse_plan_source(self, plan_source_str: str) -> PlanSource:
        """解析计划来源"""
        try:
            return PlanSource(plan_source_str.lower())
        except ValueError:
            return PlanSource.AGENT
    
    def _dict_to_plan(self, row: tuple) -> Plan:
        """将数据库行转换为Plan对象"""
        return Plan(
            id=row[0],
            uuid=row[1],
            task_id=row[2],
            start_time=row[3],
            end_time=row[4],
            is_all_day=bool(row[5]),
            title=row[6],
            description=row[7],
            tags=row[8],
            repeat_rule=row[9],
            repeat_end_date=row[10],
            reminder_minutes=row[11],
            reminder_type=ReminderType(row[12]),
            status=PlanStatus(row[13]),
            actual_start_time=row[14],
            actual_end_time=row[15],
            completion_time=row[16],
            plan_source=PlanSource(row[17]),    
            agent_origin=row[18],
            pomodoro_count=row[19],
            created_time=row[20],
            updated_time=row[21],
            is_deleted=bool(row[22])
        )
    
    async def create_plan(self, intent_data: AgentIntent) -> ProcessingResult:
        """创建计划
        
        Args:
            intent_data: Agent意图数据
            
        Returns:
            处理结果
        """
        try:
            # 解析时间
            start_time = self._parse_datetime(intent_data.start_time)
            end_time = self._parse_datetime(intent_data.end_time)
            repeat_end_date = self._parse_date(intent_data.repeat_end_date)
            actual_start_time = self._parse_datetime(intent_data.actual_start_time)
            actual_end_time = self._parse_datetime(intent_data.actual_end_time)
            completion_time = self._parse_datetime(intent_data.completion_time)
            
            if not start_time or not end_time:
                return ProcessingResult(
                    success=False,
                    message="创建计划失败",
                    error="开始时间和结束时间不能为空"
                )
            
            if start_time >= end_time:
                return ProcessingResult(
                    success=False,
                    message="创建计划失败",
                    error="开始时间必须早于结束时间"
                )
            
            # 插入数据库
            query = """
                INSERT INTO plugin_smart_plans (
                    uuid, task_id, start_time, end_time, is_all_day, title,
                    description, tags, repeat_rule, repeat_end_date,
                    reminder_minutes, reminder_type, status, actual_start_time,
                    actual_end_time, completion_time, plan_source, agent_origin,
                    pomodoro_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                intent_data.uuid,
                intent_data.task_id,
                start_time,
                end_time,
                intent_data.is_all_day or False,
                intent_data.title,
                intent_data.description,
                intent_data.tags,
                intent_data.repeat_rule,
                repeat_end_date,
                intent_data.reminder_minutes or 10,
                self._parse_reminder_type(intent_data.reminder_type or "push").value,
                self._parse_status(intent_data.status or "scheduled").value,
                actual_start_time,
                actual_end_time,
                completion_time,
                self._parse_plan_source(intent_data.plan_source or "agent").value,
                intent_data.agent_origin,
                intent_data.pomodoro_count or 0
            )
            
            result = await db_manager.execute_update(query, params)
            
            # 获取创建的计划ID
            plan_id = result
            
            # 获取创建的计划
            plan = await self._get_plan_by_id(plan_id)
            
            return ProcessingResult(
                success=True,
                message=f"计划 '{plan.title or '未命名计划'}' 创建成功",
                data={
                    "plan_id": plan_id,
                    "plan": plan.dict(),
                    "intent": intent_data.intent
                }
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                message="创建计划失败",
                error=str(e)
            )
    
    async def _get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """根据ID获取计划"""
        query = "SELECT * FROM plugin_smart_plans WHERE id = %s AND is_deleted = 0"
        result = await db_manager.execute_query(query, (plan_id,))
        
        if result:
            return self._dict_to_plan(result[0])
        return None
    
    async def get_plan(self, plan_id: str) -> str:
        """获取计划详情
        
        Args:
            plan_id: 计划ID
            
        Returns:
            计划信息JSON字符串
        """
        try:
            plan = await self._get_plan_by_id(int(plan_id))
            
            if not plan:
                result = ProcessingResult(
                    success=False,
                    message="计划不存在",
                    error="Plan not found"
                )
            else:
                result = ProcessingResult(
                    success=True,
                    message="获取计划成功",
                    data={"plan": plan.dict()}
                )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="获取计划失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def update_plan(self, plan_id: str, updates: str) -> str:
        """更新计划
        
        Args:
            plan_id: 计划ID
            updates: 更新字段JSON字符串
            
        Returns:
            更新结果JSON字符串
        """
        try:
            plan = await self._get_plan_by_id(int(plan_id))
            if not plan:
                result = ProcessingResult(
                    success=False,
                    message="计划不存在",
                    error="Plan not found"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
            updates_dict = json.loads(updates)
            
            # 构建更新SQL
            set_clauses = []
            params = []
            
            for key, value in updates_dict.items():
                if hasattr(plan, key):
                    if key == "status" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_status(value).value)
                    elif key == "reminder_type" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_reminder_type(value).value)
                    elif key == "plan_source" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_plan_source(value).value)
                    elif key in ["start_time", "end_time", "actual_start_time", "actual_end_time", "completion_time"] and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_datetime(value))
                    elif key == "repeat_end_date" and value:
                        set_clauses.append(f"{key} = %s")
                        params.append(self._parse_date(value))
                    else:
                        set_clauses.append(f"{key} = %s")
                        params.append(value)
            
            if set_clauses:
                params.append(int(plan_id))
                query = f"UPDATE plugin_smart_plans SET {', '.join(set_clauses)} WHERE id = %s"
                await db_manager.execute_update(query, tuple(params))
                
                # 获取更新后的计划
                updated_plan = await self._get_plan_by_id(int(plan_id))
                
                result = ProcessingResult(
                    success=True,
                    message=f"计划 '{updated_plan.title or '未命名计划'}' 更新成功",
                    data={"plan": updated_plan.dict()}
                )
            else:
                result = ProcessingResult(
                    success=True,
                    message="没有需要更新的字段",
                    data={"plan": plan.dict()}
                )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="更新计划失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def delete_plan(self, plan_id: str) -> str:
        """删除计划（软删除）
        
        Args:
            plan_id: 计划ID
            
        Returns:
            删除结果JSON字符串
        """
        try:
            plan = await self._get_plan_by_id(int(plan_id))
            if not plan:
                result = ProcessingResult(
                    success=False,
                    message="计划不存在",
                    error="Plan not found"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
            query = "UPDATE plugin_smart_plans SET is_deleted = 1 WHERE id = %s"
            await db_manager.execute_update(query, (int(plan_id),))
            
            result = ProcessingResult(
                success=True,
                message=f"计划 '{plan.title or '未命名计划'}' 删除成功",
                data={"deleted_plan_id": plan_id}
            )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="删除计划失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def list_plans(self, user_uuid: str, status: str = None, 
                        start_date: str = None, end_date: str = None) -> str:
        """获取用户计划列表
        
        Args:
            user_uuid: 用户唯一标识
            status: 计划状态过滤（可选）
            start_date: 开始日期过滤（可选）
            end_date: 结束日期过滤（可选）
            
        Returns:
            计划列表JSON字符串
        """
        try:
            # 构建查询条件
            conditions = ["uuid = %s", "is_deleted = 0"]
            params = [user_uuid]
            
            if status:
                conditions.append("status = %s")
                params.append(self._parse_status(status).value)
            
            if start_date:
                start_datetime = self._parse_datetime(start_date)
                if start_datetime:
                    conditions.append("start_time >= %s")
                    params.append(start_datetime)
            
            if end_date:
                end_datetime = self._parse_datetime(end_date)
                if end_datetime:
                    conditions.append("end_time <= %s")
                    params.append(end_datetime)
            
            where_clause = " AND ".join(conditions)
            query = f"SELECT * FROM plugin_smart_plans WHERE {where_clause} ORDER BY start_time"
            
            result_rows = await db_manager.execute_query(query, tuple(params))
            plans = [self._dict_to_plan(row) for row in result_rows]
            
            result = ProcessingResult(
                success=True,
                message=f"获取到 {len(plans)} 个计划",
                data={
                    "plans": [plan.dict() for plan in plans],
                    "total": len(plans)
                }
            )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="获取计划列表失败",
                error=str(e)
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def get_upcoming_plans(self, user_uuid: str, hours: int = 24) -> str:
        """获取即将到来的计划
        
        Args:
            user_uuid: 用户唯一标识
            hours: 未来小时数
            
        Returns:
            即将到来的计划JSON字符串
        """
        try:
            now = datetime.now()
            future_time = now.replace(hour=now.hour + hours)
            
            query = """
                SELECT * FROM plugin_smart_plans 
                WHERE uuid = %s 
                AND start_time >= %s 
                AND start_time <= %s 
                AND status = %s 
                AND is_deleted = 0
                ORDER BY start_time
            """
            
            params = (
                user_uuid,
                now,
                future_time,
                PlanStatus.SCHEDULED.value
            )
            
            result_rows = await db_manager.execute_query(query, params)
            upcoming_plans = [self._dict_to_plan(row) for row in result_rows]
            
            result = ProcessingResult(
                success=True,
                message=f"获取到 {len(upcoming_plans)} 个即将到来的计划",
                data={
                    "plans": [plan.dict() for plan in upcoming_plans],
                    "total": len(upcoming_plans),
                    "time_range": f"未来{hours}小时"
                }
            )
            
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
        except Exception as e:
            result = ProcessingResult(
                success=False,
                message="获取即将到来的计划失败",
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
        if intent_data.intent == "plan_time":
            return await self.create_plan(intent_data)
        else:
            return ProcessingResult(
                success=False,
                message="不支持的计划意图类型",
                error=f"Unsupported plan intent: {intent_data.intent}"
            ) 