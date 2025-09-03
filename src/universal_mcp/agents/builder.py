import asyncio
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.llm import load_chat_model

registry = AgentrRegistry()

# class BuilderToolConfig(BaseModel):
#     servers: list[str] = Field(description="List of apps and tools that the agent needs to execute the task")


class Agent(BaseModel):
    name: str = Field(description="The name of the agent")
    description: str = Field(description="A small paragraph description of the agent")
    expertise: str = Field(description="Agents expertise. Growth expert, SEO expert, etc")
    instructions: str = Field(description="The instructions for the agent")
    schedule: str = Field(
        description="The schedule for the agent in crontab syntax (e.g., '0 9 * * *' for daily at 9 AM)"
    )


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    generated_agent: Agent


def build_graph():
    model = load_chat_model("gemini/gemini-2.5-pro")

    system_prompt = """You are an AI assistant that creates autonomous agents based on user requests.

Your task is to analyze the user's request and create a structured agent definition that includes:
- A clear name for the agent
- A concise description of what the agent does
- The agent's area of expertise
- Detailed instructions for executing the task
- A cron schedule for when the agent should run
- A list of apps/services the agent will need to use

Be specific and actionable in your agent definitions. Consider the user's intent and create agents that can effectively accomplish their goals."""

    async def _create_agent(state: State):
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        generated_agent = await model.with_structured_output(Agent).ainvoke(messages)
        return {"generated_agent": generated_agent}

    builder = StateGraph(State)
    builder.add_node("create_agent", _create_agent)
    builder.add_edge(START, "create_agent")
    builder.add_edge("create_agent", END)
    return builder.compile()


async def main():
    graph = build_graph()
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content="Send a daily email to manoj@agentr.dev with daily agenda of the day")]}
    )
    print(f"Agent: {result['generated_agent'].model_dump_json(indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
