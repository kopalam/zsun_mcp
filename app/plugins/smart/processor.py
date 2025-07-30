import json
import logging
from typing import Dict, Any, Optional
from .models import AgentIntent, ProcessingResult
from .task import TaskPlugin
from .plan import PlanPlugin
import traceback

logger = logging.getLogger(__name__)

class SmartTimeProcessor:
    """智能时间管理处理器"""
    
    def __init__(self):
        self.task_plugin = TaskPlugin()
        self.plan_plugin = PlanPlugin()
        
        # 意图路由映射
        self.intent_handlers = {
            "add_schedule": self._handle_task_intent,
            "plan_time": self._handle_plan_intent,
        }
    
    async def process_agent_json(self, json_data: str) -> str:
        """处理Agent输出的JSON数据
        
        Args:
            json_data: Agent输出的JSON字符串
            
        Returns:
            处理结果JSON字符串
        """
        try:
            # 解析JSON数据
            data = json.loads(json_data)
            
            # 验证必要字段
            if "intent" not in data:
                result = ProcessingResult(
                    success=False,
                    message="处理失败",
                    error="缺少必要字段: intent"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
            if "uuid" not in data:
                result = ProcessingResult(
                    success=False,
                    message="处理失败",
                    error="缺少必要字段: uuid"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            
            # 创建AgentIntent对象
            intent_data = AgentIntent(**data)
            
            # 路由到对应的处理器
            handler = self.intent_handlers.get(intent_data.intent)
            if handler:
                result = await handler(intent_data)
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
            else:
                result = ProcessingResult(
                    success=False,
                    message="处理失败",
                    error=f"不支持的意图类型: {intent_data.intent}"
                )
                return json.dumps(result.dict(), ensure_ascii=False, indent=2)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            result = ProcessingResult(
                success=False,
                message="处理失败",
                error=f"JSON格式错误: {str(e)}"
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"处理Agent意图失败: {e}")
            logger.error(traceback.format_exc())
            result = ProcessingResult(
                success=False,
                message="处理失败",
                error=str(e),
                # 可选：返回traceback
                # "traceback": traceback.format_exc()
            )
            return json.dumps(result.dict(), ensure_ascii=False, indent=2)
    
    async def _handle_task_intent(self, intent_data: AgentIntent) -> ProcessingResult:
        """处理任务相关意图
        
        Args:
            intent_data: Agent意图数据
            
        Returns:
            处理结果
        """
        logger.info(f"处理任务意图: {intent_data.intent}")
        return await self.task_plugin.process_agent_intent(intent_data)
    
    async def _handle_plan_intent(self, intent_data: AgentIntent) -> ProcessingResult:
        """处理计划相关意图
        
        Args:
            intent_data: Agent意图数据
            
        Returns:
            处理结果
        """
        logger.info(f"处理计划意图: {intent_data.intent}")
        return await self.plan_plugin.process_agent_intent(intent_data)
    
    async def get_task_info(self, task_id: str) -> str:
        """获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            处理结果JSON字符串
        """
        return await self.task_plugin.get_task(task_id)
    
    async def get_plan_info(self, plan_id: str) -> str:
        """获取计划信息
        
        Args:
            plan_id: 计划ID
            
        Returns:
            处理结果JSON字符串
        """
        return await self.plan_plugin.get_plan(plan_id)
    
    async def list_user_tasks(self, user_uuid: str, status: Optional[str] = None) -> str:
        """获取用户任务列表
        
        Args:
            user_uuid: 用户唯一标识
            status: 任务状态过滤
            
        Returns:
            处理结果JSON字符串
        """
        return await self.task_plugin.list_tasks(user_uuid, status)
    
    async def list_user_plans(self, user_uuid: str, status: Optional[str] = None,
                             start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """获取用户计划列表
        
        Args:
            user_uuid: 用户唯一标识
            status: 计划状态过滤
            start_date: 开始日期过滤
            end_date: 结束日期过滤
            
        Returns:
            处理结果JSON字符串
        """
        return await self.plan_plugin.list_plans(user_uuid, status, start_date, end_date)
    
    async def get_upcoming_plans(self, user_uuid: str, hours: int = 24) -> str:
        """获取即将到来的计划
        
        Args:
            user_uuid: 用户唯一标识
            hours: 未来小时数
            
        Returns:
            处理结果JSON字符串
        """
        return await self.plan_plugin.get_upcoming_plans(user_uuid, hours)
    
    async def update_task(self, task_id: str, updates: str) -> str:
        """更新任务
        
        Args:
            task_id: 任务ID
            updates: 更新字段JSON字符串
            
        Returns:
            处理结果JSON字符串
        """
        return await self.task_plugin.update_task(task_id, updates)
    
    async def update_plan(self, plan_id: str, updates: str) -> str:
        """更新计划
        
        Args:
            plan_id: 计划ID
            updates: 更新字段JSON字符串
            
        Returns:
            处理结果JSON字符串
        """
        return await self.plan_plugin.update_plan(plan_id, updates)
    
    async def delete_task(self, task_id: str) -> str:
        """删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            处理结果JSON字符串
        """
        return await self.task_plugin.delete_task(task_id)
    
    async def delete_plan(self, plan_id: str) -> str:
        """删除计划
        
        Args:
            plan_id: 计划ID
            
        Returns:
            处理结果JSON字符串
        """
        return await self.plan_plugin.delete_plan(plan_id) 
    
    async def check_duplicate_task(self, uuid: str, deadline: str, estimated_duration: int) -> str:
        """
        检查重复任务
        """
        tasks = await self.task_plugin.find_duplicate_tasks(uuid, deadline, estimated_duration)
        return json.dumps({
            "success": True,
            "message": "查重成功",
            "data": {"tasks": [task.dict() for task in tasks]}
        }, ensure_ascii=False, indent=2) 