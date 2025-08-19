from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.tools import load_agentr_tools, load_mcp_tools
from universal_mcp.types import ToolConfig


class ReactAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        max_iterations: int = 10,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.tools = tools
        self.max_iterations = max_iterations

    async def _build_graph(self):
        if self.tools:
            config = self.tools.model_dump(exclude_none=True)
            agentr_tools = await load_agentr_tools(config["agentrServers"]) if config.get("agentrServers") else []
            mcp_tools = await load_mcp_tools(config["mcpServers"]) if config.get("mcpServers") else []
            tools = agentr_tools + mcp_tools
        else:
            tools = []
        logger.debug(f"Initialized ReactAgent: name={self.name}, model={self.model}")
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
        "Universal React Agent",
        instructions="",
        model="gpt-4o",
        tools=ToolConfig(agentrServers={"google-mail": {"tools": ["send_email"]}}),
    )
    result = asyncio.run(agent.run(user_input="Send an email with the subject 'Hello' to john.doe@example.com"))
    print(result["messages"][-1].content)
