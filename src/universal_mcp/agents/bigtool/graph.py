from datetime import UTC, datetime
import json
from typing import Literal, TypedDict, cast

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command, RetryPolicy

from universal_mcp.agents.bigtool.state import State
from universal_mcp.agents.bigtool.context import Context
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat

from .utils import get_message_text, load_chat_model
from .prompts import SELECT_TOOL_PROMPT




def create_agent(tool_registry: ToolRegistry, instructions: str = ""):

    @tool
    async def retrieve_tools(task_query: str) -> list[str]:
        """Retrieve tools for a given task.
        Task query should be atomic (doable with a single tool).
        For tasks requiring multiple tools, call this tool multiple times for each subtask."""
        tools_list = await tool_registry.search_tools(task_query, limit=10)
        tool_candidates = [f"{tool['id']}: {tool['description']}" for tool in tools_list]

        class ToolSelectionOutput(TypedDict):
            tool_names: list[str]

        model = load_chat_model("anthropic/claude-4-sonnet-20250514")
        
        response = await model.with_structured_output(
            schema=ToolSelectionOutput, method="json_mode"
        ).ainvoke(SELECT_TOOL_PROMPT.format(tool_candidates="\n - ".join(tool_candidates), task=task_query))

        selected_tool_names = cast(ToolSelectionOutput, response)["tool_names"]
        return selected_tool_names
    
    async def call_model(state: State, runtime: Runtime[Context]) -> Command[Literal["select_tools", "call_tools"]]:
        app_ids = await tool_registry.list_all_apps()
        connections = tool_registry.client.list_my_connections()
        connection_ids = set([connection["app_id"] for connection in connections])
        connected_apps = [app["id"] for app in app_ids if app["id"] in connection_ids]
        unconnected_apps = [app["id"] for app in app_ids if app["id"] not in connection_ids]
        app_id_descriptions = "These are the apps connected to the user's account:\n" + "\n".join(
            [f"{app}" for app in connected_apps]
        )
        if unconnected_apps:
            app_id_descriptions += "\n\nOther (not connected) apps: " + "\n".join(
                [f"{app}" for app in unconnected_apps]
            )
        system_message = runtime.context.system_prompt.format(
            system_time=datetime.now(tz=UTC).isoformat(),
            app_ids=app_id_descriptions
        )
        messages = [{"role": "system", "content": system_message}, *state["messages"]]
        
        # Load tools from tool registry
        selected_tools = await tool_registry.export_tools(tools=state["selected_tool_ids"], format=ToolFormat.LANGCHAIN)

        model = load_chat_model(runtime.context.model)
        model_with_tools = model.bind_tools([retrieve_tools, *selected_tools], tool_choice="auto")
        response = cast(AIMessage, model_with_tools.invoke(messages))

        if response.tool_calls:
            if len(response.tool_calls) > 1:
                raise Exception("Not possible in Claude with llm.bind_tools(tools=tools, tool_choice='auto')")
            tool_call = response.tool_calls[0]
            if tool_call["name"] == retrieve_tools.name:
                return Command(
                    goto="select_tools",
                    update={"messages": [response]}
                )
            elif tool_call["name"] not in state["selected_tool_ids"]:
                try:
                    await tool_registry.export_tools([tool_call["name"]], ToolFormat.LANGCHAIN)
                    return Command(goto="call_tools", update={"messages": [response]})
                except Exception as e:
                    raise Exception(f"Unexpected tool call: {tool_call['name']}. Available tools: {state["selected_tool_ids"]}")
            # We are only validating that the tool name is correct
            # if arguements are incorrect it should be handled in the ToolNode
            return Command(goto="call_tools", update={"messages": [response]})
        else:
            return Command(update={"messages": [response]})
        
    async def select_tools(state: State, runtime: Runtime[Context]) -> Command[Literal["call_model"]]:
        tool_call = state["messages"][-1].tool_calls[0]
        selected_tool_names = await retrieve_tools.ainvoke(input=tool_call['args'])
        tool_msg = ToolMessage(f"Available tools: {selected_tool_names}", tool_call_id=tool_call["id"])
        return Command(goto="call_model", update={"messages": [tool_msg], "selected_tool_ids": selected_tool_names})
    
    async def call_tools(state: State) -> Command[Literal["call_model"]]:
        outputs = []
        recent_tool_ids = []
        for tool_call in state["messages"][-1].tool_calls:
            try:
                await tool_registry.export_tools([tool_call["name"]], ToolFormat.LANGCHAIN)
                tool_result = await tool_registry.call_tool(tool_call["name"], tool_call["args"])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
                recent_tool_ids.append(tool_call["name"])
            except Exception as e:
                outputs.append(
                    ToolMessage(
                        content=json.dumps("Error: " + str(e)),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
        return Command(goto="call_model", update={"messages": outputs, "selected_tool_ids": recent_tool_ids})
    
    builder = StateGraph(State, context_schema=Context)

    builder.add_node(call_model)
    builder.add_node(select_tools)
    builder.add_node(call_tools)
    builder.set_entry_point("call_model")
    return builder