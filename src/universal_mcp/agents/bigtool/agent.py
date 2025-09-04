from langgraph.checkpoint.base import BaseCheckpointSaver

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.bigtool.graph import build_graph
from universal_mcp.agents.bigtool.prompts import SYSTEM_PROMPT
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.logger import logger
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
        # Combine the base system prompt with agent-specific instructions
        full_instructions = f"{SYSTEM_PROMPT}\n\n**User Instructions:**\n{instructions}"
        super().__init__(name, full_instructions, model, memory, **kwargs)

        self.registry = registry
        self.llm = load_chat_model(self.model)
        self.tool_selection_llm = load_chat_model("gemini/gemini-2.0-flash-001")

        logger.info(f"BigToolAgent '{self.name}' initialized with model '{self.model}'.")

    async def _build_graph(self):
        """Build the bigtool agent graph using the existing create_agent function."""
        logger.info(f"Building graph for BigToolAgent '{self.name}'...")
        try:
            graph_builder = build_graph(
                tool_registry=self.registry,
                llm=self.llm,
                tool_selection_llm=self.tool_selection_llm,
            )

            compiled_graph = graph_builder.compile(checkpointer=self.memory)
            logger.info("Graph built and compiled successfully.")
            return compiled_graph
        except Exception as e:
            logger.error(f"Error building graph for BigToolAgent '{self.name}': {e}")
            raise

    @property
    def graph(self):
        return self._graph
