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
                integration = AgentRIntegration(name=f"{app_name}", api_key=api_key)
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
                    # logger.debug(f"Added tool: {tool_name} to the list.")

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


async def call_model_node(state: AgentState, config: RunnableConfig):
    """Invokes the LLM, fetching and binding tools dynamically."""
    logger.debug("Entering call_model_node...")
    messages = state['messages']
    # tools = state.get('tools') # <--- REMOVE THIS LINE

    # --- ADD TOOL FETCHING LOGIC HERE ---
    logger.debug("Fetching tools within call_model_node...")
    tools = await _fetch_tools_for_request(config)
    # --- END OF ADDED LOGIC ---

    if tools:
        logger.debug(f"Binding {len(tools)} tools to LLM call.")
        llm_with_tools = llm.bind_tools(tools)
    else:
        logger.debug("No tools fetched or available. Calling LLM without tools.")
        llm_with_tools = llm # Use the original LLM

    logger.debug(f"Calling LLM with {len(messages)} messages.")
    response = await llm_with_tools.ainvoke(messages, config=config)
    logger.debug(f"LLM response received: type={type(response)}, content={response.content[:100]}..., tool_calls={response.tool_calls}")

    # Return ONLY the messages. Do NOT return the fetched tools.
    return {"messages": [response]}

async def tool_executor_node(state: AgentState, config: RunnableConfig) -> dict:
    """Executes tools selected by the LLM, fetching tools dynamically."""
    logger.debug("Entering tool_executor_node...")
    last_message = state['messages'][-1]

    # --- Check if the last message is an AIMessage with tool_calls ---
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        logger.warning("tool_executor_node called without AIMessage or tool calls in last message.")
        # Decide how to handle this: maybe return empty messages or raise an error?
        # Returning empty avoids breaking the loop if somehow called incorrectly.
        return {"messages": []}

    # --- Fetch Tools ---
    logger.debug("Fetching tools within tool_executor_node...")
    try:
        tools = await _fetch_tools_for_request(config) # Use the config passed to the node
    except Exception as fetch_err:
         logger.error(f"Failed to fetch tools in tool_executor_node: {fetch_err}", exc_info=True)
         # Create error messages for all requested calls since tools couldn't be loaded
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
        logger.error("tool_executor_node: No tools found after fetch attempt.")
        # Create error messages for all requested calls
        tool_messages = []
        for tool_call in last_message.tool_calls:
             tool_messages.append(
                 ToolMessage(
                     content=f"Error: Tool '{tool_call['name']}' execution failed. No tools available for this request.",
                     tool_call_id=tool_call['id'],
                 )
             )
        return {"messages": tool_messages}

    # --- Instantiate ToolNode ---
    tool_executor = ToolNode(tools=tools)

    # --- Execute Tools ---
    logger.debug(f"Executing tool calls from AIMessage: {last_message.tool_calls}")
    response_messages = []
    try:
        # Invoke the ToolNode with the AIMessage containing the tool_calls.
        result = await tool_executor.ainvoke(last_message.tool_calls)
        
        # Handle the dict with 'messages' key structure that ToolNode is returning
        if isinstance(result, dict) and 'messages' in result:
            # Extract the messages from the dict
            logger.debug(f"ToolNode returned a dict with 'messages' key. Extracting messages.")
            if isinstance(result['messages'], list):
                response_messages = result['messages']
            else:
                # Handle unexpected case where 'messages' isn't a list
                response_messages = [result['messages']] if result['messages'] else []
        elif isinstance(result, list):
            # Result is already a list
            response_messages = result
        elif isinstance(result, ToolMessage):
            # Single ToolMessage case
            response_messages = [result]
        else:
            # Unexpected return type - log and create fallback message
            logger.error(f"ToolNode returned unexpected type: {type(result)}. Data: {result}")
            # Get the first tool call ID for the error message
            first_call_id = last_message.tool_calls[0]['id']
            response_messages = [ToolMessage(
                content=f"Error: Unexpected response type {type(result)} from tool executor.",
                tool_call_id=first_call_id
            )]

        logger.debug(f"Tool execution finished. Returning {len(response_messages)} tool messages.")

    # Catch specific errors if needed (like NotAuthorizedError)
    except NotAuthorizedError as e:
         logger.warning(f"Authorization error during tool execution: {e.message}")
         # ToolNode invocation might fail entirely here. We need error messages
         # for all the calls that were *supposed* to run.
         response_messages = []
         for tool_call in last_message.tool_calls:
              response_messages.append(ToolMessage(content=f"Authorization Error: {e.message}", tool_call_id=tool_call['id']))

    except Exception as e:
        # This catches the "No message found in input" or any other error during ainvoke
        logger.error(f"Unexpected error during tool execution via ToolNode.ainvoke: {e}", exc_info=True)
        # Create error messages for all requested calls
        response_messages = []
        for tool_call in last_message.tool_calls:
             response_messages.append(
                 ToolMessage(
                     content=f"Error executing tool '{tool_call['name']}': {type(e).__name__} - {e}. Check service logs.",
                     tool_call_id=tool_call['id']
                 )
             )

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
    logger.info("Creating agent graph (dynamic tools per node)...") # Updated comment
    workflow = StateGraph(AgentState)

    # Add nodes
    # workflow.add_node("fetch_tools", fetch_tools_node) # <--- REMOVE THIS LINE
    workflow.add_node("call_model", call_model_node)
    # Make sure tool_executor_node receives config by passing the function directly
    workflow.add_node("execute_tools", tool_executor_node) # Use the function directly

    # Define edges
    workflow.set_entry_point("call_model") # <--- CHANGE ENTRY POINT
    # workflow.add_edge("fetch_tools", "call_model") # <--- REMOVE THIS LINE

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
