from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Literal, cast

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from langgraph.types import Command

from universal_mcp.agents.llm import load_chat_model

from .context import Context
from .state import State
from .tools import get_default_retrieval_tool, get_store_arg


def _format_selected_tools(
    selected_tools: dict, tool_registry: dict[str, BaseTool]
) -> tuple[list[ToolMessage], list[str]]:
    tool_messages = []
    tool_ids = []
    for tool_call_id, batch in selected_tools.items():
        tool_names = []
        for result in batch:
            if isinstance(tool_registry[result], BaseTool):
                tool_names.append(tool_registry[result].name)
            else:
                tool_names.append(tool_registry[result].__name__)
        tool_messages.append(ToolMessage(f"Available tools: {tool_names}", tool_call_id=tool_call_id))
        tool_ids.extend(batch)

    return tool_messages, tool_ids


def create_agent(
    tool_registry: dict[str, BaseTool],
    *,
    limit: int = 2,
    filter: dict[str, Any] | None = None,
    namespace_prefix: tuple[str, ...] = ("tools",),
    retrieve_tools_function: Callable | None = None,
    retrieve_tools_coroutine: Callable | None = None,
):
    if retrieve_tools_function is None and retrieve_tools_coroutine is None:
        retrieve_tools_function, retrieve_tools_coroutine = get_default_retrieval_tool(
            namespace_prefix, limit=limit, filter=filter
        )
    retrieve_tools = StructuredTool.from_function(func=retrieve_tools_function, coroutine=retrieve_tools_coroutine)
    # If needed, get argument name to inject Store
    store_arg = get_store_arg(retrieve_tools)

    async def call_model(state: State, runtime: Runtime[Context]) -> Command[Literal["select_tools", "tools"]]:
        system_message = runtime.context.system_prompt.format(system_time=datetime.now(tz=UTC).isoformat())
        messages = [{"role": "system", "content": system_message}, *state["messages"]]
        selected_tools = [tool_registry[id] for id in state["selected_tool_ids"]]
        model = load_chat_model(runtime.context.model)
        model_with_tools = model.bind_tools([retrieve_tools, *selected_tools], tool_choice="auto")
        response = cast(AIMessage, model_with_tools.invoke(messages))

        if response.tool_calls:
            if len(response.tool_calls) > 1:
                raise Exception("Not possible in Claude with llm.bind_tools(tools=tools, tool_choice='auto')")
            tool_call = response.tool_calls[0]
            valid_tool_names = [t.name for t in selected_tools]
            if tool_call["name"] == retrieve_tools.name:
                return Command(
                    goto="select_tools",
                    update={"messages": [response], "tool_args": tool_call["args"], "tool_call_id": tool_call["id"]},
                )
            elif tool_call["name"] not in valid_tool_names:
                available_tools = [t.name for t in selected_tools]
                raise Exception(f"Unexpected tool call: {tool_call['name']}. Available tools: {available_tools}")
            # We are only validating that the tool name is correct
            # if arguements are incorrect it should be handled in the ToolNode
            return Command(goto="tools", update={"messages": [response]})
        else:
            return Command(update={"messages": [response]})

    async def select_tools(state: State, runtime: Runtime[Context]) -> Command[Literal["call_model"]]:
        kwargs = {**state["tool_args"]}
        if store_arg:
            kwargs[store_arg] = runtime.store
        result = retrieve_tools.invoke(kwargs)
        tool_messages, tool_ids = _format_selected_tools({state["tool_call_id"]: result}, tool_registry)
        return Command(goto="call_model", update={"messages": tool_messages, "selected_tool_ids": tool_ids})

    tool_node = ToolNode([tool for tool in tool_registry.values()])

    builder = StateGraph(State, context_schema=Context)

    builder.add_node(call_model)
    builder.add_node("tools", tool_node)
    builder.add_node(select_tools)

    builder.set_entry_point("call_model")

    builder.add_edge("tools", "call_model")

    return builder
