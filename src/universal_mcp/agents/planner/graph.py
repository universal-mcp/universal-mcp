from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from loguru import logger

from universal_mcp.agents.shared.tool_node import build_tool_node_graph

from .state import State


def build_graph(llm, registry, instructions, model, executor_agent_cls):
    """Build the graph for the planner agent."""
    graph_builder = StateGraph(State)

    async def _tool_finder_node(state: State) -> dict[str, Any]:
        """Runs the tool finder subgraph to identify necessary tools."""
        task = state["messages"][-1].content
        logger.info(f"Running tool finder for task: {task}")
        tool_finder_graph = build_tool_node_graph(llm, registry)
        tool_finder_state = await tool_finder_graph.ainvoke({"task": task, "messages": state["messages"]})

        if not tool_finder_state.get("apps_required"):
            logger.info("Tool finder determined no apps are required.")
            return {"apps_with_tools": {}}

        apps_with_tools = tool_finder_state.get("apps_with_tools", {})
        logger.info(f"Tool finder identified apps and tools: {apps_with_tools}")
        return {"apps_with_tools": apps_with_tools, "task": task}

    def _should_continue(state: State) -> str:
        """Determines whether to continue to the executor or end."""
        if state.get("apps_with_tools"):
            return "continue"
        return "end"

    async def _executor_node(state: State) -> dict[str, Any]:
        """Executes the task with the identified tools."""
        tool_config = state["apps_with_tools"]

        logger.info(f"Preparing executor with tools: {tool_config}")
        agent = executor_agent_cls(
            name="executor-agent",
            instructions=instructions,
            model=model,
            registry=registry,
            tools=tool_config,
        )

        await agent.ainit()
        react_graph = agent._graph
        logger.info("Invoking executor agent with tools.")
        # We invoke the agent to make it run the tool
        response = await react_graph.ainvoke({"messages": state["messages"]})

        final_message = AIMessage(content=response["messages"][-1].content)
        return {"messages": [final_message]}

    async def _no_tools_node(state: State) -> dict[str, Any]:
        """Handles tasks that don't require tools by invoking the LLM directly."""
        logger.info("No tools required. Invoking LLM directly.")
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}

    graph_builder.add_node("tool_finder", _tool_finder_node)
    graph_builder.add_node("executor", _executor_node)
    graph_builder.add_node("no_tools_executor", _no_tools_node)

    graph_builder.add_edge(START, "tool_finder")
    graph_builder.add_conditional_edges(
        "tool_finder",
        _should_continue,
        {
            "continue": "executor",
            "end": "no_tools_executor",
        },
    )
    graph_builder.add_edge("executor", END)
    graph_builder.add_edge("no_tools_executor", END)

    return graph_builder
