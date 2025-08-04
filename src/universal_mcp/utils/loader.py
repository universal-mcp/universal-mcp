from universal_mcp.applications import app_from_slug
from universal_mcp.integrations.integration import AgentRIntegration
from universal_mcp.tools.manager import ToolManager


def load_tools(tool_names: list[str], tool_manager: ToolManager):
    # Group all tools by app_name, tools
    tools_by_app = {}
    for tool_name in tool_names:
        app_name = tool_name.split("_")[0]
        if app_name not in tools_by_app:
            tools_by_app[app_name] = []
        tools_by_app[app_name].append(tool_name)

    for app_name, tools in tools_by_app.items():
        app = app_from_slug(app_name)
        integration = AgentRIntegration(name=app_name)
        app_instance = app(integration=integration)
        tool_manager.register_tools_from_app(app_instance, tool_names=tools)
    return tool_manager
