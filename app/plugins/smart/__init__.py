from .task import TaskPlugin
from .plan import PlanPlugin
from .processor import SmartTimeProcessor

# 创建插件实例
task_plugin = TaskPlugin()
plan_plugin = PlanPlugin()
smart_processor = SmartTimeProcessor()

# 导出插件实例
__all__ = ['task_plugin', 'plan_plugin', 'smart_processor'] 