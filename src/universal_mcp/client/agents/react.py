from langgraph.prebuilt import create_react_agent
from loguru import logger

from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import get_llm
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.manager import ToolManager
from universal_mcp.utils.agentr import AgentrRegistry


class ReactAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str, max_iterations: int = 10, tools: list[str] = None):
        super().__init__(name, instructions, model)
        self.llm = get_llm(model)
        self.max_iterations = max_iterations
        self.tool_manager = ToolManager()
        registry = AgentrRegistry()
        self.tool_manager = registry.load_tools(tools, self.tool_manager)
        logger.debug(f"Initialized ReactAgent: name={name}, model={model}")
        self._graph = self._build_graph()

    @property
    def graph(self):
        return self._graph

    def _build_graph(self):
        tools = self.tool_manager.list_tools(format=ToolFormat.LANGCHAIN) if self.tool_manager else []
        return create_react_agent(
            self.llm,
            tools,
            prompt=self._build_system_message(),
            checkpointer=self.memory,
        )

    def _build_system_message(self) -> str:
        system_message = f"""You are {self.name}. {self.instructions}

You have access to various tools that can help you answer questions and complete tasks. When you need to use a tool:

1. Think about what information you need
2. Call the appropriate tool with the right parameters
3. Use the tool results to provide a comprehensive answer

Always explain your reasoning and be thorough in your responses. If you need to use multiple tools to answer a question completely, do so."""
        return system_message


if __name__ == "__main__":
    import asyncio

    agent = ReactAgent(
        "Universal React Agent", "You are a helpful assistant", "gpt-4.1", tools=["google-mail_send_email"]
    )
    asyncio.run(agent.run_interactive())
