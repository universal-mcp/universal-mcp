import asyncio

from dotenv import load_dotenv
from langsmith import Client, aevaluate

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.meta_agent import MetaAgent

import asyncio
import functools
from typing import Any

from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.tools.tools import Tool

async def search_apps(registry: AgentrRegistry, query: str) -> list[dict[str, Any]]:
    """
    Searches for available applications based on a user's task or query.
    Use this tool first to discover which apps can help with a specific goal.
    Always use the most popular app from the search results.

    Args:
        query (str): A natural language description of the task (e.g., "send an email", "list my files").

    Returns:
        List[Dict[str, Any]]: A list of applications that match the query, including their 'id', 'name', and 'description'.
    """
    print(f"DEBUG: Searching for apps with query: {query}")
    return await registry.search_apps(query=query, limit=10)


async def search_tools(registry: AgentrRegistry, app_id: str, query: str) -> list[dict[str, Any]]:
    """
    Searches for specific tools within a given application.
    Use this tool after you have identified a relevant app with 'search_apps'.

    Args:
        app_id (str): The ID of the application to search within (e.g., 'google-mail').
        query (str): A natural language description of the specific action to perform (e.g., "send an email").

    Returns:
        List[Dict[str, Any]]: A list of tools within the app that match the query.
    """
    print(f"DEBUG: Searching for tools in app '{app_id}' with query: {query}")
    return await registry.search_tools(query=query, app_id=app_id, limit=10)


async def get_tool_info(registry: AgentrRegistry, tool_id: str) -> dict[str, Any]:
    """
    Retrieves the detailed schema and description for a specific tool.
    You MUST use this tool to understand the required parameters and their format before calling 'call_tool'.

    Args:
        tool_id (str): The full ID of the tool, in the format 'app_id__tool_name' (e.g., 'google-mail__send_email').

    Returns:
        Dict[str, Any]: The detailed JSON schema for the tool's parameters and its description.
    """
    print(f"DEBUG: Getting info for tool: {tool_id}")
    temp_manager = registry.tool_manager
    temp_manager.clear_tools()
    await registry.export_tools([tool_id], format="native")
    tool = temp_manager.get_tool(tool_id)
    if not tool:
        return {"error": f"Tool with ID '{tool_id}' not found."}

    return {
        "name": tool.name,
        "description": tool.description,
        "parameters_schema": tool.parameters,
        "output_schema": tool.output_schema,
    }


async def call_tool(registry: AgentrRegistry, tool_id: str, arguments: dict[str, Any]) -> Any:
    """
    Executes a tool with the specified arguments.
    This is the final step. Only call this after using 'get_tool_info' to understand the required arguments.

    Args:
        tool_id (str): The full ID of the tool to execute (e.g., 'google-mail__send_email').
        arguments (Dict[str, Any]): A dictionary of arguments that matches the tool's parameter schema.

    Returns:
        Any: The result of the tool's execution.
    """
    print(f"DEBUG: Calling tool '{tool_id}' with arguments: {arguments}")
    result = await registry.call_tool(tool_name=tool_id, tool_args=arguments)

    # print(result)

    return result


registry = AgentrRegistry()


partial_tools = [
    functools.partial(search_apps, registry),
    functools.partial(search_tools, registry),
    functools.partial(get_tool_info, registry),
    functools.partial(call_tool, registry),
]

from universal_mcp.tools.adapters import convert_tool_to_langchain_tool

langchain_tools = [
    convert_tool_to_langchain_tool(Tool.from_function(pt, name=pt.func.__name__)) for pt in partial_tools
]

load_dotenv()
async def target_function1(inputs: dict):
    agent = await MetaAgent(
        name="bigtool2",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
        tools=langchain_tools
    )._build_graph()
    result = await agent.ainvoke(inputs, config = {"recursion_limit": 30}, context={ "model": "anthropic/claude-4-sonnet-20250514"})
    return result


# async def target_function2(inputs: dict):
#     agent = AutoAgent(
#         name="autoagent",
#         instructions="You are a helpful assistant that can use tools to help the user.",
#         model="anthropic/claude-4-sonnet-20250514",
#         tool_registry=AgentrRegistry(api_key = "dev-key-f911a713-a9ac-4d51-a9ce-44e3bf0b48db"), #insert 
#     )
#     result = await agent.invoke(inputs["user_input"])
#     return result

if __name__ == "__main__":
    client = Client()
    dataset_name = "metaagent-actual-runs"
#     asyncio.run(aevaluate(
#     target_function1,
#     data=client.list_examples(
#         dataset_name=dataset_name,example_ids=["5425de13-58b0-44b3-802f-9e5e6b2e3a0c", "56bcf12f-2608-4ad7-8538-507ff0e22df1", "79ecefe9-3a13-428e-bdda-f3cc1eb03578", "c0a2e3cf-9bea-4cf3-90be-7ab8945094b3", "a73827d5-2c77-4d8b-a486-93b0e8ce6713"]
#     ),
#     evaluators=[],
#     experiment_prefix ="test-1-errors"
# ))

    asyncio.run(aevaluate(
    target_function1,
    data=client.list_examples(
        dataset_name=dataset_name
    ),
    evaluators=[],
    experiment_prefix ="metaaegnt test 2",
    ))