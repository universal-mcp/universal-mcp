# --- START OF FILE react.py ---

import asyncio
import operator
import os
from contextlib import asynccontextmanager
from typing import Annotated, Sequence, TypedDict, List, Optional

import httpx # To call AgentR API
from langchain.tools import StructuredTool, BaseTool # To wrap fetched functions
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AnyMessage,
    SystemMessage # Added for potential initial prompt
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from universal_mcp.applications import app_from_name
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.config import AppConfig # Need this to parse API response

# Logger for debugging
from loguru import logger
import sys

# Configure Loguru
logger.remove() # Remove default handler
logger.add(sys.stderr, level="DEBUG") # Log DEBUG and above to stderr

# --- Define AgentR Configuration ---
AGENTR_BASE_URL = os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")

# --- Define the State for the Graph ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], operator.add]
    tools: Optional[List[BaseTool]] # Hold the dynamically fetched tools for this request


# --- Helper Function to Fetch and Prepare Tools ---
async def _fetch_tools_for_request(config: RunnableConfig) -> List[BaseTool]:
    """
    Fetches available applications and their tools for the given API key.
    """
    logger.debug("Entering _fetch_tools_for_request...")
    fetched_tools: List[BaseTool] = []
    api_key = config.get("configurable", {}).get("api_key")

    if not api_key:
        logger.warning("API Key missing in RunnableConfig. Cannot fetch tools.")
        # Return empty list, LLM won't have tools bound.
        # Alternatively, could raise an error earlier in the flow.
        return []

    logger.debug(f"Fetching apps from {AGENTR_BASE_URL} using API Key.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTR_BASE_URL}/api/apps/", # Assuming same endpoint as AgentRServer
                headers={"X-API-KEY": api_key},
                timeout=15.0 # Add a reasonable timeout
            )
            response.raise_for_status() # Raise HTTP errors
            apps_data = response.json()
            logger.debug(f"Received {len(apps_data)} app definitions from AgentR API.")

        # Validate and parse app configurations
        app_configs = [AppConfig.model_validate(app_data) for app_data in apps_data]

        # Instantiate apps and collect tools
        for app_config in app_configs:
            app_name = app_config.name
            logger.debug(f"Processing app: {app_name}")
            try:
                # Create integration specifically for this app instance
                integration = AgentRIntegration(name=f"dynamic_{app_name}", api_key=api_key)
                AppClass = app_from_name(app_name)
                app_instance = AppClass(integration=integration)

                # Get tool functions from the app instance
                tool_functions = app_instance.list_tools()
                logger.debug(f"Found {len(tool_functions)} tool functions in {app_name}.")

                for tool_func in tool_functions:
                    tool_name = f"{app_name}_{tool_func.__name__}"
                    tool_description = tool_func.__doc__ or f"Tool from application {app_name}."

                    # Wrap the function using StructuredTool.from_function
                    # This automatically infers the schema from type hints.
                    # Use the app_instance method directly so 'self' is bound.
                    bound_method = getattr(app_instance, tool_func.__name__)
                    langchain_tool = StructuredTool.from_function(
                        func=bound_method, # Use the bound method from the instance
                        name=tool_name,
                        description=tool_description,
                        # Optionally add args_schema if needed and not inferred perfectly
                        # handle_tool_error=True # Can add robust error handling
                    )
                    fetched_tools.append(langchain_tool)
                    logger.debug(f"Added tool: {tool_name} to the list.")

            except ImportError:
                logger.error(f"Could not import or find application class for '{app_name}'. Skipping.")
            except Exception as e:
                logger.error(f"Error processing application '{app_name}': {e}", exc_info=True)

    except httpx.RequestError as e:
        logger.error(f"HTTP Request error fetching apps from AgentR: {e}")
        # Decide how to handle this - fail request or proceed without tools?
        # For now, proceed without tools.
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status error fetching apps from AgentR: {e.response.status_code} - {e.response.text}")
        if e.response.status_code in [401, 403]:
             logger.warning("Authorization error fetching apps. Check API Key.")
        return [] # Proceed without tools on error
    except Exception as e:
        logger.error(f"Unexpected error fetching or processing tools: {e}", exc_info=True)
        return [] # Proceed without tools on error

    logger.info(f"Successfully prepared {len(fetched_tools)} tools for this request.")
    return fetched_tools


# --- Define Graph Nodes ---

async def fetch_tools_node(state: AgentState, config: RunnableConfig) -> dict:
    """Fetches tools based on config and adds them to the state."""
    logger.debug("Entering fetch_tools_node...")
    tools = await _fetch_tools_for_request(config)
    return {"tools": tools}

async def call_model_node(state: AgentState, config: RunnableConfig):
    """Invokes the LLM with fetched tools bound."""
    logger.debug("Entering call_model_node...")
    messages = state['messages']
    tools = state.get('tools') # Get tools fetched by the previous node

    if tools:
        logger.debug(f"Binding {len(tools)} tools to LLM call.")
        # Bind the tool schemas to the LLM
        llm_with_tools = llm.bind_tools(tools)
    else:
        logger.debug("No tools fetched or available. Calling LLM without tools.")
        llm_with_tools = llm # Use the original LLM

    logger.debug(f"Calling LLM with {len(messages)} messages.")
    # system_prompt = "You are a helpful assistant. Use the provided tools when necessary."
    # messages_with_prompt = [SystemMessage(content=system_prompt)] + list(messages) # Optionally add system prompt

    response = await llm_with_tools.ainvoke(messages, config=config) # Pass message list directly
    logger.debug(f"LLM response received: type={type(response)}, content={response.content[:100]}..., tool_calls={response.tool_calls}")

    # Return the response to be added to the message list
    return {"messages": [response]}

async def tool_executor_node(state: AgentState) -> dict:
    """Executes tools selected by the LLM."""
    logger.debug("Entering tool_executor_node...")
    last_message = state['messages'][-1]
    tools = state.get('tools') # Get the actual tool objects

    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        logger.warning("tool_executor_node called without tool calls in last message.")
        return {"messages": []}

    if not tools:
        logger.error("tool_executor_node called but no tools found in state.")
        # Create error messages for all requested calls
        tool_messages = []
        for tool_call in last_message.tool_calls:
             tool_messages.append(
                 ToolMessage(
                     content=f"Error: Tool '{tool_call['name']}' execution failed. Tools could not be loaded for this request.",
                     tool_call_id=tool_call['id'],
                 )
             )
        return {"messages": tool_messages}

    # Instantiate ToolExecutor with the fetched tools
    tool_executor = ToolNode(tools=tools)

    logger.debug(f"Executing tool calls: {last_message.tool_calls}")
    # The executor returns ToolMessages or raises errors
    # Use tool_executor.batch for concurrent execution if desired
    response_messages = []
    try:
        # We need to map tool call IDs to the ToolExecutor invocation if using batch
        # Simplest is often iterating and calling invoke one by one
        for tool_call in last_message.tool_calls:
             # ToolExecutor needs the call structured as {"type": tool_call["name"], "args": tool_call["args"], "id": tool_call["id"]}
             # Or simply pass the ToolCall object from the AIMessage
             logger.debug(f"Invoking tool: {tool_call['name']} with id {tool_call['id']}")
             # LangChain's ToolExecutor expects ToolCall objects directly now
             tool_message = await tool_executor.ainvoke(tool_call) # Pass the ToolCall dict
             response_messages.append(tool_message)
             logger.debug(f"Tool {tool_call['name']} ({tool_call['id']}) executed successfully.")

    # Catch potential NotAuthorizedError if the integration check fails *during* execution
    except NotAuthorizedError as e:
         logger.warning(f"Authorization error during tool execution: {e.message}")
         # Find which tool call failed if possible, or return a general error
         # For simplicity, append a generic error message, though ideally it maps to the specific failed call
         # Creating a ToolMessage requires a tool_call_id. This part is tricky if batch fails.
         # Let's assume the failure relates to the last attempted call for now.
         failed_call_id = last_message.tool_calls[-1]['id'] # Approximation
         response_messages.append(ToolMessage(content=f"Authorization Error: {e.message}", tool_call_id=failed_call_id))

    except Exception as e:
        logger.error(f"Unexpected error during tool execution: {e}", exc_info=True)
        # Append a generic error ToolMessage
        failed_call_id = last_message.tool_calls[-1]['id'] # Approximation
        response_messages.append(
            ToolMessage(
                content=f"Error executing tool: {type(e).__name__}. Check service logs.",
                tool_call_id=failed_call_id
            )
        )

    logger.debug(f"Tool execution finished. Returning {len(response_messages)} tool messages.")
    return {"messages": response_messages}


# --- Define LLM ---
llm = ChatAnthropic(model="claude-3-5-sonnet-latest")

# --- Define Conditional Edge Logic ---
def should_continue(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logger.debug("LLM requested tool calls. Routing to tool_executor_node.")
        return "use_tools"
    else:
        logger.debug("LLM did not request tool calls. Routing to END.")
        return "end"

# --- Create the Agent Graph ---
@asynccontextmanager
async def create_agent():
    logger.info("Creating agent graph (fetch-first approach)...")
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("fetch_tools", fetch_tools_node)
    workflow.add_node("call_model", call_model_node)
    workflow.add_node("execute_tools", tool_executor_node)

    # Define edges
    workflow.set_entry_point("fetch_tools") # Start by fetching tools
    workflow.add_edge("fetch_tools", "call_model") # After fetching, call the model

    # Conditional edge from model to tools or end
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "use_tools": "execute_tools",
            "end": END,
        },
    )

    # Edge from tools back to model
    workflow.add_edge("execute_tools", "call_model")

    # Compile the graph
    agent = workflow.compile()
    logger.info("Agent graph compiled successfully.")
    yield agent

# --- Main function for testing ---
async def main():
    test_api_key = os.getenv("AGENTR_API_KEY")
    if not test_api_key:
        print("Please set the AGENTR_API_KEY environment variable for testing.")
        return

    async with create_agent() as agent:
        print("Welcome to the dynamic agent (fetch-first)!")
        messages: List[AnyMessage] = [] # Ensure type hint consistency
        thread_id = f"thread_{os.urandom(4).hex()}" # Example thread ID

        while True:
            human_input = input("Enter your message (or 'exit'): ")
            if human_input.lower() in ["exit", "quit", "q"]:
                break
            messages.append(HumanMessage(content=human_input))

            # Prepare config with API key for testing
            config = RunnableConfig(
                configurable={
                    "thread_id": thread_id, # Include thread_id if checkpointer is used later
                    "api_key": test_api_key,
                }
            )
            logger.debug(f"Invoking agent with config: {config}")

            try:
                # Use stream_events for detailed view
                async for event in agent.astream_events({"messages": messages}, config=config, version="v2"):
                    kind = event["event"]
                    name = event.get("name", "")
                    tags = event.get("tags", [])

                    logger.trace(f"Event: {kind} | Name: {name} | Tags: {tags} | Data: {event['data']}")

                    if kind == "on_chat_model_stream":
                        chunk = event["data"].get("chunk")
                        if chunk and hasattr(chunk, "content"):
                            print(chunk.content, end="", flush=True)
                    elif kind == "on_tool_end":
                        print(f"\n<<< Tool Result ({event['name']}) >>>")
                        # Tool output is often nested, check data structure
                        tool_output = event["data"].get("output")
                        if isinstance(tool_output, list) and tool_output and isinstance(tool_output[0], ToolMessage):
                            # Output might be a list containing the ToolMessage
                             print(tool_output[0].content)
                        elif isinstance(tool_output, ToolMessage):
                             print(tool_output.content)
                        else:
                             # Fallback if structure is different
                             print(tool_output)
                        print("<<< End Tool Result >>>")


                    # Update message history based on the final state of the graph run
                    # Note: 'on_graph_end' event's data might not directly contain the final state in all versions.
                    # It's safer to rely on the agent state *after* the stream completes or handle state updates from node ends.
                    # For this testing loop, we'll update `messages` *after* the loop finishes based on the final returned state.

                # Get the final state after streaming completes
                # Note: astream_events doesn't directly return the final state easily like ainvoke.
                # For robust history, better to use `agent.ainvoke` or manage state updates carefully from events.
                # Let's call ainvoke to get the final state for the next turn in this simple test loop.
                final_state = await agent.ainvoke({"messages": messages}, config=config)
                messages = final_state['messages'] # Update message list for next turn

                # Print final AI response after all streaming/tool calls
                if messages and isinstance(messages[-1], AIMessage):
                    print("\n--- Final AI Message ---")
                    print(messages[-1].content)
                    if messages[-1].tool_calls:
                         print("\n(Agent requested further tools - loop will continue)")
                    print("------")
                elif messages and isinstance(messages[-1], ToolMessage):
                    # This case shouldn't usually be the *very* last message if the graph loops back to call_model
                    print("\n(Last message was a tool result - loop should continue to model)")


            except Exception as e:
                logger.error(f"An error occurred during agent invocation: {e}", exc_info=True)
                print(f"\nERROR: {e}")
                break


if __name__ == "__main__":
    asyncio.run(main())

# --- END OF FILE react.py ---