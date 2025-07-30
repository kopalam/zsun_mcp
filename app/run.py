from fastmcp import FastMCP
from plugins.weather import weather_plugin
from plugins.smart import task_plugin, plan_plugin, smart_processor

main_mcp = FastMCP("Main Service")

# 注册插件
main_mcp.tool(weather_plugin.get_weather, name="get_weather")
main_mcp.tool(weather_plugin.get_weather_forecast, name="get_weather_forecast")
main_mcp.tool(smart_processor.process_agent_json, name="process_agent_intent")
main_mcp.tool(smart_processor.get_task_info, name="get_task_info")
main_mcp.tool(smart_processor.get_plan_info, name="get_plan_info")
main_mcp.tool(smart_processor.list_user_tasks, name="list_user_tasks")
main_mcp.tool(smart_processor.list_user_plans, name="list_user_plans")
main_mcp.tool(smart_processor.get_upcoming_plans, name="get_upcoming_plans")
main_mcp.tool(smart_processor.update_task, name="update_task")
main_mcp.tool(smart_processor.update_plan, name="update_plan")
main_mcp.tool(smart_processor.delete_task, name="delete_task")
main_mcp.tool(smart_processor.delete_plan, name="delete_plan")
main_mcp.tool(smart_processor.check_duplicate_task, name="check_duplicate_task")

if __name__ == "__main__":
    main_mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8010
    ) 