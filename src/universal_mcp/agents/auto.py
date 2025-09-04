import asyncio
import datetime
from typing import Annotated, Any

from langchain_core.messages import AIMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from loguru import logger
from typing_extensions import TypedDict

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.tool_node import ToolFinderAgent
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.registry import ToolRegistry


class State(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    apps_with_tools: dict[str, list[str]]


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
        self.tool_finder = ToolFinderAgent(self.llm, self.app_registry)

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
        tool_finder_state = await self.tool_finder.run(task)

        if not tool_finder_state.get("apps_required"):
            logger.info("Tool finder determined no apps are required.")
            return {"apps_with_tools": {}}

        apps_with_tools = tool_finder_state.get("apps_with_tools", {})
        logger.info(f"Tool finder identified apps and tools: {apps_with_tools}")
        return {"apps_with_tools": apps_with_tools, "task": task}

    def _should_continue(self, state: State) -> str:
        """Determines whether to continue to the executor or end."""
        if state.get("apps_with_tools"):
            return "continue"
        return "end"

    async def _executor_node(self, state: State) -> dict[str, Any]:
        """Executes the task with the identified tools."""
        apps_with_tools = state["apps_with_tools"]
        # Flatten the list of tools from all apps
        # Tool name is app__tool
        # where app is the app id and tool is the tool name
        tool_names = [f"{app}__{tool}" for app, tools in apps_with_tools.items() for tool in tools]

        logger.info(f"Preparing executor with tools: {', '.join(tool_names)}")
        agent = await self._get_react_agent(tool_names)

        logger.info("Invoking ReAct agent with tools.")
        # We invoke the agent to make it run the tool
        response = await agent.ainvoke({"messages": state["messages"]})
        print(f"Response: {response}")

        final_message = AIMessage(content=response["messages"][-1].content)
        return {"messages": [final_message]}

    async def _no_tools_node(self, state: State) -> dict[str, Any]:
        """Handles tasks that don't require tools by invoking the LLM directly."""
        logger.info("No tools required. Invoking LLM directly.")
        response = await self.llm.ainvoke(state["messages"])
        return {"messages": [response]}

    async def _get_react_agent(self, tool_names: list[str]):
        """Creates a ReAct agent with a specific set of tools."""
        tools = await self.app_registry.export_tools(tool_names, format=ToolFormat.LANGCHAIN)
        logger.debug(f"Creating ReAct agent with {len(tools)} tools.")

        current_time = datetime.datetime.now()
        utc_time = datetime.datetime.now(datetime.UTC)
        timezone_info = f"Current local time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} | UTC time: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}"

        agent = create_react_agent(
            self.llm,
            tools=tools,
            prompt=f"You are a helpful assistant. Use the provided tools to complete the task. Current time information: {timezone_info}. User instructions: {self.instructions}. After calling a tool, confirm the action is complete and include the results from the tool call in your final response.",
        )
        return agent

    @property
    def graph(self):
        return self._graph

    # async def stream(self, user_input: str,thread_id: str = uuid4()):
    #     """Streams the agent's response for a given user input."""
    #     await self.ainit()
    #     async for chunk in self.graph.astream(
    #         {"messages": [HumanMessage(content=user_input)]},
    #         config={"configurable": {"thread_id": thread_id}},
    #     ):
    #         # The output of the graph is a dictionary with the final state
    #         # We are interested in the 'messages' key
    #         final_messages = chunk.get("messages", [])
    #         if final_messages:
    #             # The last message is the one we want to stream
    #             ai_message = final_messages[-1]
    #             if isinstance(ai_message, AIMessageChunk):
    #                 yield ai_message
    #             else:
    #                 # If it's a full message, wrap it in a chunk for consistency
    #                 yield AIMessageChunk(content=str(ai_message.content))


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
