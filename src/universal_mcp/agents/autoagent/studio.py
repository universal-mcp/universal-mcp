from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import create_agent
from universal_mcp.tools import ToolManager


tool_registry = AgentrRegistry()
tool_manager = ToolManager()


graph = create_agent(tool_registry, tool_manager, instructions="You are a helpful assistant that can use tools to help the user. If a task requires multiple steps, you should perform separate different searches for different actions.")







