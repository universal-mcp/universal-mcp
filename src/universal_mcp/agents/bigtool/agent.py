from langgraph.checkpoint.base import BaseCheckpointSaver

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.bigtool.graph import create_agent
from universal_mcp.tools.registry import ToolRegistry


class BigToolAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        registry: ToolRegistry,
        memory: BaseCheckpointSaver | None = None,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.registry = registry

    async def _build_graph(self):
        """Build the bigtool agent graph using the existing create_agent function."""
        # Create the graph using the existing create_agent function
        graph_builder = create_agent(self.registry, self.instructions)
        
        # Compile the graph with memory if provided
        return graph_builder.compile(checkpointer=self.memory)
    
    @property
    def graph(self):
        return self._graph
