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
    async def retrieve_tools(query: str) -> list[str]:
        """Retrieve tools using a search query. Use multiple times if you require tools for different tasks."""
        tools = await tool_registry.search_tools(query)
        return tools

    @tool()
    async def ask_user(question: str) -> str:
        """Ask the user a question. Use this tool to ask the user for any missing information for performing a task, or when you have multiple apps to choose from for performing a task."""
        full_question = question
        return f"ASKING_USER: {full_question}"

    async def call_model(
        state: State,
        runtime: Runtime[Context],
    ):
        system_prompt = runtime.context.system_prompt if runtime.context.system_prompt else SYSTEM_PROMPT
        system_prompt = system_prompt.format(system_time=datetime.now(tz=UTC).isoformat())

        messages = [{"role": "system", "content": system_prompt + "\n" + instructions}, *state["messages"]]
        model = load_chat_model(runtime.context.model)
        # Load tools from tool registry
        loaded_tools = await tool_registry.export_tools(tools=state["selected_tool_ids"], format=ToolFormat.LANGCHAIN)
        model_with_tools = model.bind_tools([retrieve_tools, ask_user, *loaded_tools], tool_choice="auto")
        response = cast(AIMessage, model_with_tools.invoke(messages))
        return {"messages": [response]}

    # Define the conditional edge that determines whether to continue or not
    def should_continue(state: State):
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return END
        # Otherwise if there is, we continue
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
            if tool_call["name"] == retrieve_tools.name:
                tool_result = await retrieve_tools.ainvoke(tool_call["args"])
                tool_ids = [tool["id"] for tool in tool_result]
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
            elif tool_call["name"] == ask_user.name:
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
            else:
                tool_result = await tool_registry.call_tool(tool_call["name"], tool_call["args"])
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
    builder.add_conditional_edges("agent", should_continue)
    builder.add_conditional_edges("tools", tool_router)

    return builder
