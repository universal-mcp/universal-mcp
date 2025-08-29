import json
from datetime import UTC, datetime
from typing import cast

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from universal_mcp.agents.autoagent.context import Context
from universal_mcp.agents.autoagent.prompts import SYSTEM_PROMPT
from universal_mcp.agents.autoagent.state import State
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat


async def build_graph(tool_registry: ToolRegistry, instructions: str = ""):
    @tool()
    async def search_tools(query: str, app_ids: list[str] | None = None) -> list[str]:
        """Retrieve tools using a search query and app id. Use multiple times if you require tools for different tasks."""
        tools_list = []
        if app_ids is not None:
            for app_id in app_ids:
                tools_list.extend(await tool_registry.search_tools(query, limit=10, app_id=app_id))
        else:
            tools_list = await tool_registry.search_tools(query, limit=10)
        tools_list = [f"{tool['id']}: {tool['description']}" for tool in tools_list]
        return tools_list

    @tool()
    async def ask_user(question: str) -> str:
        """Ask the user a question. Use this tool to ask the user for any missing information for performing a task, or when you have multiple apps to choose from for performing a task."""
        full_question = question
        return f"ASKING_USER: {full_question}"
    
    @tool()
    async def load_tools(tools: list[str]) -> list[str]:
        """Choose the tools you want to use by passing their tool ids.  Loads the tools for the chosen tools and returns the tool ids."""
        return tools
    

    async def call_model(
        state: State,
        runtime: Runtime[Context],
    ):
        system_prompt = runtime.context.system_prompt if runtime.context.system_prompt else SYSTEM_PROMPT
        app_ids = await tool_registry.list_all_apps()
        app_id_descriptions = "\n".join([f"{app['id']}: {app['description']}" for app in app_ids])
        print(app_id_descriptions)
        system_prompt = system_prompt.format(system_time=datetime.now(tz=UTC).isoformat(), app_ids=app_id_descriptions)
        
        messages = [{"role": "system", "content": system_prompt + "\n" + instructions}, *state["messages"]]
        model = load_chat_model(runtime.context.model)
        # Load tools from tool registry
        loaded_tools = await tool_registry.export_tools(tools=state["selected_tool_ids"], format=ToolFormat.LANGCHAIN)
        model_with_tools = model.bind_tools([search_tools, ask_user, load_tools, *loaded_tools], tool_choice="auto")
        response_raw = model_with_tools.invoke(messages)
        token_usage = state.get("token_usage", {})
        for key in ["input_tokens", "output_tokens", "total_tokens"]:
            if key in token_usage:
                token_usage[key] += response_raw.usage_metadata[key]
            else:
                token_usage[key] = response_raw.usage_metadata[key]
        print(response_raw.usage_metadata)
        print(token_usage)
        response = cast(AIMessage, response_raw) 
        return {"messages": [response], "token_usage": token_usage}

    # Define the conditional edge that determines whether to continue or not
    def should_continue(state: State):
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return END
        else:
            return "tools"

    def tool_router(state: State):
        last_message = state["messages"][-1]
        if isinstance(last_message, ToolMessage):
            return "agent"
        else:
            return END

    async def tool_node(state: State):
        outputs = []
        tool_ids = state["selected_tool_ids"]
        for tool_call in state["messages"][-1].tool_calls:
            if tool_call["name"] == ask_user.name:
                outputs.append(
                    ToolMessage(
                        content=json.dumps(
                            "The user has been asked the question, and the run will wait for the user's response."
                        ),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
                ai_message = AIMessage(content=tool_call["args"]["question"])
                outputs.append(ai_message)
            elif tool_call["name"] == search_tools.name:
                tools = await search_tools.ainvoke(tool_call["args"])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tools)+"\n\nUse the load_tools tool to load the tools you want to use.",
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
                
            elif tool_call["name"] == load_tools.name:
                tool_ids = await load_tools.ainvoke(tool_call["args"])
                print(tool_ids)
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_ids),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
            else:
                await tool_registry.export_tools([tool_call["name"]], ToolFormat.LANGCHAIN)
                try:
                    tool_result = await tool_registry.call_tool(tool_call["name"], tool_call["args"])
                    outputs.append(
                        ToolMessage(
                            content=json.dumps(tool_result),
                            name=tool_call["name"],
                                tool_call_id=tool_call["id"],
                            )
                        )
                except Exception as e:
                    outputs.append(
                        ToolMessage(
                            content=json.dumps("Error: "+str(e)),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
        return {"messages": outputs, "selected_tool_ids": tool_ids}

                



    builder = StateGraph(State, context_schema=Context)

    builder.add_node("agent", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    builder.add_conditional_edges("tools", tool_router)

    return builder
