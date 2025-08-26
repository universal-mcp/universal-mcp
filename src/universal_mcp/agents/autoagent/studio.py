from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import create_agent
from universal_mcp.tools import ToolManager

tool_registry = AgentrRegistry()
tool_manager = ToolManager()



apps = tool_registry.client.list_all_apps()
names = [app["name"] for app in apps]

instructions = """
You are a helpful assistant that can use tools to help the user. If a task requires multiple steps, you should perform separate different searches for different actions.
These are the list of applications you can use to help the user:
{names}
"""
graph = create_agent(tool_registry, tool_manager, instructions=instructions)







