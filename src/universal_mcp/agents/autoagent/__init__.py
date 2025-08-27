from langgraph.checkpoint.base import BaseCheckpointSaver

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent.graph import build_graph
from universal_mcp.agents.base import BaseAgent
from universal_mcp.tools.registry import ToolRegistry


class AutoAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tool_registry: ToolRegistry | None = None,
    ):
        super().__init__(name, instructions, model, memory)
        self.tool_registry = tool_registry or AgentrRegistry()
        self.model = model
        self.name = name
        self.instructions = instructions

    async def _build_graph(self):
        builder = await build_graph(self.tool_registry, self.instructions)
        return builder.compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


__all__ = ["AutoAgent"]
