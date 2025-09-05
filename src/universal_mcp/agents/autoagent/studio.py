import asyncio

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import build_graph
from universal_mcp.tools import ToolManager

tool_registry = AgentrRegistry()
tool_manager = ToolManager()


async def main():
    instructions = """
    You are a helpful assistant that can use tools to help the user. If a task requires multiple steps, you should perform separate different searches for different actions. Prefer completing one action before searching for another.
    """
    graph = await build_graph(tool_registry, instructions=instructions)
    return graph


graph = asyncio.run(main())
