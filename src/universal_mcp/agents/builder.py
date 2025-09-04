import asyncio
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.shared.agent_node import Agent, generate_agent
from universal_mcp.agents.shared.tool_node import ToolFinderAgent
from universal_mcp.types import ToolConfig


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    generated_agent: Agent
    tool_config: ToolConfig


def build_graph():
    model = load_chat_model("gemini/gemini-2.5-pro")

    async def create_agent(state: State):
        generated_agent = await generate_agent(model, state["messages"][-1].content)
        return {"generated_agent": generated_agent}

    async def create_tool_config(state: State):
        tool_config = await ToolFinderAgent(model, state["generated_agent"])
        return {"tool_config": tool_config}

    builder = StateGraph(State)
    builder.add_node("create_agent", create_agent)
    builder.add_node("create_tool_config", create_tool_config)
    builder.add_edge(START, "create_agent")
    builder.add_edge("create_agent", "create_tool_config")
    builder.add_edge("create_tool_config", END)
    return builder.compile()


async def main():
    graph = build_graph()
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content="Send a daily email to manoj@agentr.dev with daily agenda of the day")]}
    )
    print(f"Agent: {result['generated_agent'].model_dump_json(indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
