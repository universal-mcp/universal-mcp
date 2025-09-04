import asyncio
import functools
from typing import Any, Dict, List

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver 
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.tools.tools import Tool


async def search_apps(registry: AgentrRegistry, query: str) -> List[Dict[str, Any]]:
    """
    Searches for available applications based on a user's task or query.
    Use this tool first to discover which apps can help with a specific goal.
    You should always use the most popular app from the search results.
    Args:
        query (str): A natural language description of the task (e.g., "send an email", "list my files").

    Returns:
        List[Dict[str, Any]]: A list of applications that match the query, including their 'id', 'name', and 'description'.
    """
    print(f"DEBUG: Searching for apps with query: {query}")
    return await registry.search_apps(query=query, limit=10)


async def search_tools(registry: AgentrRegistry, app_id: str, query: str) -> List[Dict[str, Any]]:
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


async def get_tool_info(registry: AgentrRegistry, tool_id: str) -> Dict[str, Any]:
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
        "output_schema": tool.output_schema
    }


async def call_tool(registry: AgentrRegistry, tool_id: str, arguments: Dict[str, Any]) -> Any:
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
    return await registry.call_tool(tool_name=tool_id, tool_args=arguments)


class MetaAgent(BaseAgent):
    """
    A custom agent that uses meta-tools to discover and orchestrate other tools.
    This agent inherits from the SDK's BaseAgent and uses langgraph's
    create_react_agent for its core logic.
    """

    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        tools: List[BaseTool],
        memory: BaseCheckpointSaver | None = None,
        **kwargs,
    ):
        """
        Initializes the MetaAgent.
        """
        super().__init__(name, instructions, model, memory, **kwargs)
        self.llm = load_chat_model(model)
        self.tools = tools
        self.system_prompt = instructions # Store the detailed instructions

    async def _build_graph(self):
        """
        Builds the executable agent graph using langgraph's create_react_agent.
        This method is required by the BaseAgent class.
        """
        return create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=self.system_prompt,
            checkpointer=self.memory,
        )

async def main():
    """
    Initializes and runs the Tool Orchestrator Agent.
    """
    print("Initializing Tool Orchestrator Agent...")

    try:
        registry = AgentrRegistry()
        await registry.list_connected_apps()
        print("AgentrRegistry initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize AgentrRegistry. Is your AGENTR__API_KEY set correctly? Error: {e}")
        return

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

    system_prompt = """You are a highly intelligent tool orchestrator agent. Your primary goal is to accomplish user tasks by finding and using the correct tools available in the platform.

You must follow a strict four-step process:

1.  **SEARCH APPS**: When the user gives you a task, your first step is to use the `search_apps` tool to find the most relevant application. For example, if the user says "send an email," search for "email."

2.  **SEARCH TOOLS**: Once you have identified a suitable app (e.g., 'google-mail'), use its `app_id` with the `search_tools` tool to find the specific tool for the action required (e.g., search for "send email" within the 'google-mail' app).

3.  **GET TOOL INFO**: You have now found a specific tool (e.g., 'google-mail__send_email'). Before you can use it, you MUST call `get_tool_info` with the tool's full ID. This will give you the exact `parameters_schema` you need to use. You cannot skip this step.

4.  **CALL TOOL**: Now that you have the correct parameters from the schema, you can finally execute the task by using the `call_tool` function. Make sure the 'arguments' you provide is a JSON object that perfectly matches the schema from the previous step.

Always think step-by-step and explain your reasoning. Do not try to guess tool names or parameters. Follow the process.
"""

    memory = MemorySaver()

    agent = MetaAgent(
        name="Tool Orchestrator Agent",
        instructions=system_prompt,
        model="azure/gpt-4.1",
        tools=langchain_tools,
        memory=memory,
    )

    print("Agent is ready. You can now chat with it.")
    await agent.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())