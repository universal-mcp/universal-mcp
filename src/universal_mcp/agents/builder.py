import asyncio
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.shared.tool_node import build_tool_node_graph
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig


class Agent(BaseModel):
    """Agent that can be created by the builder."""

    name: str = Field(description="Name of the agent.")
    description: str = Field(description="A small description of the agent.")
    expertise: str = Field(description="The expertise of the agent.")
    instructions: str = Field(description="The instructions for the agent to follow.")
    schedule: str | None = Field(description="The cron expression for the agent to run on.", default=None)


class BuilderState(TypedDict):
    user_task: str
    generated_agent: Agent | None
    tool_config: ToolConfig | None
    messages: Annotated[Sequence[BaseMessage], add_messages]


AGENT_BUILDER_INSTRUCTIONS = """
You are an agent builder. Your goal is to create an agent that can accomplish the user's task.
Your will be given a task and you need to generate an agent that can accomplish the task.
The agent should have a name, role, instructions, and a model.
- The name should be a short and descriptive name for the agent.
- The description should be a small description of the agent. For example, research a stock and write a buy sell analysis report.
- The expertise should be the expertise of the agent. For example, GTM Expert, SEO Expert, etc.
- The instructions should be a detailed description of what the agent should do. This should include the input, the output, and the tool usage. The agent will be provided a set of tools, you can use that to give a more accurate response.
- The model should be the model to use for the agent.
- The reasoning should be a detailed explanation of why you are creating this agent with these parameters.
- If the user specifies a schedule, you should also provide a cron expression for the agent to run on. The schedule should be in a proper cron expression and nothing more.
"""


async def generate_agent(llm: BaseChatModel, task: str, old_agent: Agent | None = None) -> Agent:
    """Generates an agent from a task, optionally modifying an existing one."""
    prompt_parts = [AGENT_BUILDER_INSTRUCTIONS]
    if old_agent:
        prompt_parts.append(
            "\nThe user wants to modify the following agent design. "
            "Incorporate their feedback into a new design.\n\n"
            f"{old_agent.model_dump_json(indent=2)}"
        )
    else:
        prompt_parts.append(f"\n\n**Task:** {task}")

    prompt = "\n".join(prompt_parts)
    structured_llm = llm.with_structured_output(Agent)
    agent = await structured_llm.ainvoke(prompt)
    return agent


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
        task = last_message.content
        agent = state.get("generated_agent")

        yield {
            "messages": [
                AIMessage(
                    content="Thinking... I will now design an agent to handle your request.",
                )
            ],
        }
        generated_agent = await generate_agent(self.llm, task, agent)
        yield {
            "user_task": task,
            "generated_agent": generated_agent,
            "messages": [AIMessage(content=("I've designed an agent to help you with your task."))],
        }

    async def _create_tool_config(self, state: BuilderState):
        task = state["user_task"]
        yield {
            "messages": [
                AIMessage(
                    content="Great! Now, I will select the appropriate tools for this agent. This may take a moment.",
                )
            ]
        }
        tool_finder_graph = build_tool_node_graph(self.llm, self.registry)
        tool_config = await tool_finder_graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        tool_config = tool_config.get("apps_with_tools", {})
        yield {
            "tool_config": tool_config,
            "messages": [AIMessage(content="I have selected the necessary tools for the agent. The agent is ready!")],
        }

    async def _build_graph(self):
        builder = StateGraph(BuilderState)
        builder.add_node("create_agent", self._create_agent)
        builder.add_node("create_tool_config", self._create_tool_config)

        builder.add_edge(START, "create_agent")
        builder.add_edge("create_agent", "create_tool_config")
        builder.add_edge("create_tool_config", END)
        return builder.compile(checkpointer=self.memory)


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
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
