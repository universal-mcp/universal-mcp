import asyncio
import operator
import os
from contextlib import asynccontextmanager
from typing import Annotated, Sequence, TypedDict, List, Optional

import httpx
from langchain.tools import StructuredTool, BaseTool
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AnyMessage,
    SystemMessage
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from universal_mcp.applications import app_from_name
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.config import AppConfig


AGENTR_BASE_URL = os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")

class AgentState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], operator.add]


async def _fetch_tools_for_request(config: RunnableConfig) -> List[BaseTool]:
    fetched_tools: List[BaseTool] = []
    api_key = config.get("configurable", {}).get("api_key")

    if not api_key:
        return []

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTR_BASE_URL}/api/apps/",
                headers={"X-API-KEY": api_key},
                timeout=15.0
            )
            response.raise_for_status()
            apps_data = response.json()

        app_configs = [AppConfig.model_validate(app_data) for app_data in apps_data]

        for app_config in app_configs:
            app_name = app_config.name
            try:
                integration = AgentRIntegration(name=f"{app_name}", api_key=api_key)
                AppClass = app_from_name(app_name)
                app_instance = AppClass(integration=integration)

                tool_functions = app_instance.list_tools()

                for tool_func in tool_functions:
                    tool_name = f"{app_name}_{tool_func.__name__}"
                    tool_description = tool_func.__doc__ or f"Tool from application {app_name}."

                    bound_method = getattr(app_instance, tool_func.__name__)
                    langchain_tool = StructuredTool.from_function(
                        func=bound_method,
                        name=tool_name,
                        description=tool_description,
                    )
                    fetched_tools.append(langchain_tool)

            except ImportError:
                # Handle or log error if needed in production
                pass
            except Exception as e:
                # Handle or log error if needed in production
                pass

    except httpx.RequestError as e:
        # Handle or log error if needed in production
        return []
    except httpx.HTTPStatusError as e:
        # Handle or log error if needed in production
        return []
    except Exception as e:
        # Handle or log error if needed in production
        return []

    return fetched_tools


async def call_model_node(state: AgentState, config: RunnableConfig):
    messages = state['messages']
    tools = await _fetch_tools_for_request(config)

    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm

    response = await llm_with_tools.ainvoke(messages, config=config)

    return {"messages": [response]}

async def tool_executor_node(state: AgentState, config: RunnableConfig) -> dict:
    last_message = state['messages'][-1]

    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"messages": []}

    try:
        tools = await _fetch_tools_for_request(config)
    except Exception as fetch_err:
         tool_messages = []
         for tool_call in last_message.tool_calls:
             tool_messages.append(
                 ToolMessage(
                     content=f"Error: Tool execution failed. Could not load tools. Fetch error: {fetch_err}",
                     tool_call_id=tool_call['id'],
                 )
             )
         return {"messages": tool_messages}


    if not tools:
        tool_messages = []
        for tool_call in last_message.tool_calls:
             tool_messages.append(
                 ToolMessage(
                     content=f"Error: Tool '{tool_call['name']}' execution failed. No tools available for this request.",
                     tool_call_id=tool_call['id'],
                 )
             )
        return {"messages": tool_messages}

    tool_executor = ToolNode(tools=tools)

    response_messages = []
    try:
        result = await tool_executor.ainvoke(last_message.tool_calls)

        if isinstance(result, dict) and 'messages' in result:
            if isinstance(result['messages'], list):
                response_messages = result['messages']
            else:
                response_messages = [result['messages']] if result['messages'] else []
        elif isinstance(result, list):
            response_messages = result
        elif isinstance(result, ToolMessage):
            response_messages = [result]
        else:
            first_call_id = last_message.tool_calls[0]['id']
            response_messages = [ToolMessage(
                content=f"Error: Unexpected response type {type(result)} from tool executor.",
                tool_call_id=first_call_id
            )]

    except NotAuthorizedError as e:
         response_messages = []
         for tool_call in last_message.tool_calls:
              response_messages.append(ToolMessage(content=f"Authorization Error: {e.message}", tool_call_id=tool_call['id']))

    except Exception as e:
        response_messages = []
        for tool_call in last_message.tool_calls:
             response_messages.append(
                 ToolMessage(
                     content=f"Error executing tool '{tool_call['name']}': {type(e).__name__} - {e}. Check service logs.",
                     tool_call_id=tool_call['id']
                 )
             )

    return {"messages": response_messages}

llm = ChatAnthropic(model="claude-3-5-sonnet-latest")

def should_continue(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "use_tools"
    else:
        return "end"

@asynccontextmanager
async def create_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("call_model", call_model_node)
    workflow.add_node("execute_tools", tool_executor_node)

    workflow.set_entry_point("call_model")

    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "use_tools": "execute_tools",
            "end": END,
        },
    )

    workflow.add_edge("execute_tools", "call_model")

    agent = workflow.compile()
    yield agent

async def main():
    test_api_key = os.getenv("AGENTR_API_KEY")
    if not test_api_key:
        print("Please set the AGENTR_API_KEY environment variable for testing.")
        return

    async with create_agent() as agent:
        print("Welcome to the dynamic agent!")
        messages: List[AnyMessage] = []
        thread_id = f"thread_{os.urandom(4).hex()}"

        while True:
            human_input = input("Enter your message (or 'exit'): ")
            if human_input.lower() in ["exit", "quit", "q"]:
                break
            messages.append(HumanMessage(content=human_input))

            config = RunnableConfig(
                configurable={
                    "thread_id": thread_id,
                    "api_key": test_api_key,
                }
            )

            try:
                async for event in agent.astream_events({"messages": messages}, config=config, version="v2"):
                    kind = event["event"]

                    if kind == "on_chat_model_stream":
                        chunk = event["data"].get("chunk")
                        if chunk and hasattr(chunk, "content"):
                            print(chunk.content, end="", flush=True)
                    elif kind == "on_tool_end":
                        print(f"\n<<< Tool Result ({event['name']}) >>>")
                        tool_output = event["data"].get("output")
                        if isinstance(tool_output, list) and tool_output and isinstance(tool_output[0], ToolMessage):
                             print(tool_output[0].content)
                        elif isinstance(tool_output, ToolMessage):
                             print(tool_output.content)
                        else:
                             print(tool_output)
                        print("<<< End Tool Result >>>")

                final_state = await agent.ainvoke({"messages": messages}, config=config)
                messages = final_state['messages']

                if messages and isinstance(messages[-1], AIMessage):
                    print("\n--- Final AI Message ---")
                    print(messages[-1].content)
                    if messages[-1].tool_calls:
                         print("\n(Agent requested further tools - loop will continue)")
                    print("------")
                elif messages and isinstance(messages[-1], ToolMessage):
                    print("\n(Last message was a tool result - loop should continue to model)")


            except Exception as e:
                print(f"\nERROR: {e}")
                # Log error properly if needed for production
                break


if __name__ == "__main__":
    asyncio.run(main())