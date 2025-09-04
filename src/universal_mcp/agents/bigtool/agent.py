from langgraph.checkpoint.base import BaseCheckpointSaver

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.bigtool.graph import create_agent
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.logger import logger


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
        logger.info(f"BigToolAgent '{self.name}' initialized with model '{self.model}'.")

    async def _build_graph(self):
        """Build the bigtool agent graph using the existing create_agent function."""
        logger.info(f"Building graph for BigToolAgent '{self.name}'...")
        try:
            graph_builder = create_agent(self.registry, self.instructions)
            
            compiled_graph = graph_builder.compile(checkpointer=self.memory)
            logger.info("Graph built and compiled successfully.")
            return compiled_graph
        except Exception as e:
            logger.error(f"Error building graph for BigToolAgent '{self.name}': {e}")
            raise
    
    @property
    def graph(self):
        return self._graph
