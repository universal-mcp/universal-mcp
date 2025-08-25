import json
from datetime import UTC, datetime
from typing import cast

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from universal_mcp.agents.llm import load_chat_model
from universal_mcp.tools.manager import ToolManager
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat

from .context import Context
from .prompts import SYSTEM_PROMPT
from .state import State


def create_agent(tool_registry: ToolRegistry, tool_manager: ToolManager):
    retrieve_tools = StructuredTool.from_function(func=tool_registry.search_tools)

    def call_model(
        state: State,
        runtime: Runtime[Context],
    ):
        system_prompt = runtime.context.system_prompt if runtime.context.system_prompt else SYSTEM_PROMPT
        system_prompt = system_prompt.format(system_time=datetime.now(tz=UTC).isoformat())
        messages = [{"role": "system", "content": system_prompt}, *state["messages"]]
        model = load_chat_model(runtime.context.model)
        # Load tools from tool registry
        tool_manager.clear_tools()
        tool_registry.load_tools(tools=state["selected_tool_ids"], tool_manager=tool_manager)
        loaded_tools = tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
        model_with_tools = model.bind_tools([retrieve_tools, *loaded_tools], tool_choice="auto")
        response = cast(AIMessage, model_with_tools.invoke(messages))
        return {"messages": [response]}

    # Define the conditional edge that determines whether to continue or not
    def should_continue(state: State):
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            print("No tool calls")
            return "end"
        # Otherwise if there is, we continue
        else:
            return "continue"

    async def tool_node(state: State):
        outputs = []
        tool_ids = state["selected_tool_ids"]
        for tool_call in state["messages"][-1].tool_calls:
            if tool_call["name"] == retrieve_tools.name:  # Handle retrieve tools separately
                tool_result = retrieve_tools.invoke(tool_call["args"])
                tool_ids = [tool["id"] for tool in tool_result]
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
            else:
                tool_result = await tool_manager.call_tool(tool_call["name"], tool_call["args"])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
        return {"messages": outputs, "selected_tool_ids": tool_ids}

    builder = StateGraph(State, context_schema=Context)

    builder.add_node("agent", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_edge("tools", "agent")
    builder.add_edge("agent", "tools")
    builder.add_conditional_edges(
        "agent",
        should_continue,
        {"continue": "tools", "end": END},
    )

    return builder
