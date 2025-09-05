import asyncio
from typing import Annotated, Any

from langchain_core.messages import AIMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from loguru import logger
from typing_extensions import TypedDict

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.react import ReactAgent
from universal_mcp.agents.shared.tool_node import build_tool_node_graph
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import AgentrToolConfig, ToolConfig


class State(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    apps_with_tools: AgentrToolConfig


class AutoAgent(BaseAgent):
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
        self.app_registry = registry
        self.llm = load_chat_model(model)

    async def _build_graph(self):
        graph_builder = StateGraph(State)

        graph_builder.add_node("tool_finder", self._tool_finder_node)
        graph_builder.add_node("executor", self._executor_node)
        graph_builder.add_node("no_tools_executor", self._no_tools_node)

        graph_builder.add_edge(START, "tool_finder")
        graph_builder.add_conditional_edges(
            "tool_finder",
            self._should_continue,
            {
                "continue": "executor",
                "end": "no_tools_executor",
            },
        )
        graph_builder.add_edge("executor", END)
        graph_builder.add_edge("no_tools_executor", END)

        return graph_builder.compile(checkpointer=self.memory)

    async def _tool_finder_node(self, state: State) -> dict[str, Any]:
        """Runs the tool finder subgraph to identify necessary tools."""
        task = state["messages"][-1].content
        logger.info(f"Running tool finder for task: {task}")
        tool_finder_graph = build_tool_node_graph(self.llm, self.app_registry)
        tool_finder_state = await tool_finder_graph.ainvoke({"task": task, "messages": state["messages"]})

        if not tool_finder_state.get("apps_required"):
            logger.info("Tool finder determined no apps are required.")
            return {"apps_with_tools": AgentrToolConfig(agentrServers={})}

        apps_with_tools = tool_finder_state.get("apps_with_tools", AgentrToolConfig(agentrServers={}))
        logger.info(f"Tool finder identified apps and tools: {apps_with_tools}")
        return {"apps_with_tools": apps_with_tools, "task": task}

    def _should_continue(self, state: State) -> str:
        """Determines whether to continue to the executor or end."""
        if state.get("apps_with_tools") and state["apps_with_tools"].agentrServers:
            return "continue"
        return "end"

    async def _executor_node(self, state: State) -> dict[str, Any]:
        """Executes the task with the identified tools."""
        tool_config = state["apps_with_tools"]

        logger.info(f"Preparing executor with tools: {tool_config}")
        agent = ReactAgent(
            name="react-executor",
            instructions=self.instructions,
            model=self.model,
            registry=self.app_registry,
            tools=ToolConfig(agentrServers=tool_config.agentrServers),
        )

        await agent.ainit()
        react_graph = agent._graph
        logger.info("Invoking ReAct agent with tools.")
        # We invoke the agent to make it run the tool
        response = await react_graph.ainvoke({"messages": state["messages"]})

        final_message = AIMessage(content=response["messages"][-1].content)
        return {"messages": [final_message]}

    async def _no_tools_node(self, state: State) -> dict[str, Any]:
        """Handles tasks that don't require tools by invoking the LLM directly."""
        logger.info("No tools required. Invoking LLM directly.")
        response = await self.llm.ainvoke(state["messages"])
        return {"messages": [response]}

    @property
    def graph(self):
        return self._graph


async def main():
    from universal_mcp.agentr.registry import AgentrRegistry

    registry = AgentrRegistry()
    agent = AutoAgent(
        name="auto-agent",
        instructions="You are a helpful assistant.",
        model="gemini/gemini-2.5-flash",
        registry=registry,
    )
    from rich.console import Console

    console = Console()
    console.print("Starting agent...", style="yellow")
    async for event in agent.stream(user_input="Send an email to manoj@agentr.dev'", thread_id="xyz"):
        console.print(event.content, style="red")


if __name__ == "__main__":
    asyncio.run(main())
