from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.base import BaseAgent
from universal_mcp.tools.manager import ToolManager
from universal_mcp.tools.registry import ToolRegistry

from universal_mcp.agents.autoagent.graph import create_agent


class AutoAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        tool_registry: ToolRegistry | None = None,
        tool_manager: ToolManager | None = None,
    ):
        super().__init__(name, instructions, model, tool_registry)
        self.tool_registry = tool_registry or AgentrRegistry()
        self.tool_manager = tool_manager or ToolManager()
        self.model = model
        self.name = name
        self.instructions = instructions
        self._graph = self._build_graph()

    def _build_graph(self):
        builder = create_agent(self.tool_registry, self.tool_manager, self.instructions)
        return builder.compile()

    @property
    def graph(self):
        return self._graph


__all__ = ["AutoAgent"]
