from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.tools import load_mcp_tools
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat


class ReactAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        registry: ToolRegistry | None = None,
        max_iterations: int = 10,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.llm = load_chat_model(model)
        self.tools = tools
        self.max_iterations = max_iterations
        self.registry = registry

    async def _build_graph(self):
        if self.tools:
            config = self.tools.model_dump(exclude_none=True)
            if config.get("agentrServers") and not self.registry:
                raise ValueError("Agentr servers are configured but no registry is provided")
            agentr_tools = (
                await self.registry.export_tools(self.tools, ToolFormat.LANGCHAIN)
                if config.get("agentrServers")
                else []
            )
            logger.debug(agentr_tools)
            mcp_tools = await load_mcp_tools(config["mcpServers"]) if config.get("mcpServers") else []
            logger.debug(mcp_tools)
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
        system_message = f"""You are {self.name}.

You have access to various tools that can help you answer questions and complete tasks. When you need to use a tool:

1. Think about what information you need
2. Call the appropriate tool with the right parameters
3. Use the tool results to provide a comprehensive answer

Always explain your reasoning and be thorough in your responses. If you need to use multiple tools to answer a question completely, do so.

{self.instructions}
"""
        return system_message


if __name__ == "__main__":
    import asyncio

    agent = ReactAgent(
        "Universal React Agent",
        instructions="",
        model="azure/gpt-4o",
        tools=ToolConfig(agentrServers={"google-mail": {"tools": ["send_email"]}}),
        registry=AgentrRegistry(),
    )
    result = asyncio.run(
        agent.invoke(user_input="Send an email with the subject 'testing react agent' to manoj@agentr.dev")
    )
    logger.info(result["messages"][-1].content)
