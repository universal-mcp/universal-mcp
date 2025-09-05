import asyncio
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.shared.agent_node import Agent, generate_agent
from universal_mcp.agents.shared.tool_node import build_tool_node_graph
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig


class BuilderState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    generated_agent: Agent | None
    tool_config: ToolConfig | None


class BuilderAgent(BaseAgent):
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
        self.llm: BaseChatModel = load_chat_model(model)

    async def _create_agent(self, state: BuilderState):
        last_message = state["messages"][-1]
        generated_agent = await generate_agent(self.llm, last_message.content)
        return {"generated_agent": generated_agent}

    async def _create_tool_config(self, state: BuilderState):
        last_message = state["messages"][-1]
        tool_finder_graph = build_tool_node_graph(self.llm, self.registry)
        tool_config = await tool_finder_graph.ainvoke({"task": last_message.content, "messages": [last_message]})
        tool_config = tool_config.get("apps_with_tools", {})
        return {"tool_config": tool_config}

    async def _build_graph(self):
        builder = StateGraph(BuilderState)
        builder.add_node("create_agent", self._create_agent)
        builder.add_node("create_tool_config", self._create_tool_config)
        builder.add_edge(START, "create_agent")
        builder.add_edge("create_agent", "create_tool_config")
        builder.add_edge("create_tool_config", END)
        return builder.compile()


async def main():
    from universal_mcp.agentr.registry import AgentrRegistry

    registry = AgentrRegistry()
    agent = BuilderAgent(
        name="Builder Agent",
        instructions="You are a builder agent that creates other agents.",
        model="gemini/gemini-1.5-pro",
        registry=registry,
    )
    result = await agent.invoke(
        "Send a daily email to manoj@agentr.dev with daily agenda of the day",
    )
    print(f"Agent: {result['generated_agent'].model_dump_json(indent=2)}")
    print(f"Tool Config: {result['tool_config']}")


if __name__ == "__main__":
    asyncio.run(main())
