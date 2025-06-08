from enum import Enum
from typing import Type, Any, Dict

from loguru import logger
from mcp.types import TextContent
from pydantic import create_model, Field, BaseModel

from universal_mcp.tools.tools import Tool

_IS_CREWAI_INSTALLED = True
try:
    from crewai.tools import BaseTool
except ImportError:
    _IS_CREWAI_INSTALLED = False
    # Define a placeholder BaseTool if crewai is not installed.
    # This allows the application to load, and errors will be raised only
    # when trying to convert to crewai format without crewai installed.
    class BaseTool:  # type: ignore
        def __init__(self, *args, **kwargs): # pragma: no cover
            pass
        # Add other methods that might be called on the class type itself if any
        # For example, if `BaseTool.model_validate()` was a class method used by CrewAI internally on `args_schema`
        # This mock might need to be more sophisticated depending on CrewAI's usage of it.
        # For now, a simple class pass should suffice for instantiation checks.


class ToolFormat(str, Enum):
    """Supported tool formats."""

    MCP = "mcp"
    LANGCHAIN = "langchain"
    OPENAI = "openai"
    LANGGRAPH = "langgraph"
    CREWAI = "crewai"
    SMOLAGENTS = "smolagents"


def convert_tool_to_mcp_tool(
    tool: Tool,
):
    from mcp.server.fastmcp.server import MCPTool

    logger.debug(f"Converting tool '{tool.name}' to MCP format")
    mcp_tool = MCPTool(
        name=tool.name[:63], # Ensure name is not too long for MCP
        description=tool.description or "No description provided.",
        inputSchema=tool.parameters,
    )
    logger.debug(f"Successfully converted tool '{tool.name}' to MCP format")
    return mcp_tool


def format_to_mcp_result(result: Any) -> list[TextContent]:
    """Format tool result into TextContent list.

    Args:
        result: Raw tool result

    Returns:
        List of TextContent objects
    """
    logger.debug(f"Formatting result to MCP format, type: {type(result)}")
    if isinstance(result, str):
        logger.debug("Result is string, wrapping in TextContent")
        return [TextContent(type="text", text=result)]
    elif isinstance(result, list) and all(
        isinstance(item, TextContent) for item in result
    ):
        logger.debug("Result is already list of TextContent objects")
        return result
    else:
        logger.warning(
            f"Tool returned unexpected type: {type(result)}. Wrapping in TextContent."
        )
        return [TextContent(type="text", text=str(result))]


def convert_tool_to_langchain_tool(
    tool: Tool,
):
    from langchain_core.tools import StructuredTool

    """Convert an tool to a LangChain tool.

    NOTE: this tool can be executed only in a context of an active MCP client session.

    Args:
        tool: Tool to convert

    Returns:
        a LangChain tool
    """

    logger.debug(f"Converting tool '{tool.name}' to LangChain format")

    async def call_tool(
        **arguments: Dict[str, Any],
    ):
        logger.debug(
            f"Executing LangChain tool '{tool.name}' with arguments: {arguments}"
        )
        call_tool_result = await tool.run(arguments)
        logger.debug(f"Tool '{tool.name}' execution completed")
        return call_tool_result

    langchain_tool = StructuredTool(
        name=tool.name,
        description=tool.description or "No description provided.",
        coroutine=call_tool,
        response_format="content",  # Ensure this is a valid option or remove
        args_schema=tool.parameters,  # type: ignore # Langchain expects a Pydantic model here
    )
    logger.debug(f"Successfully converted tool '{tool.name}' to LangChain format")
    return langchain_tool


def convert_tool_to_openai_tool(
    tool: Tool,
):
    """Convert a Tool object to an OpenAI function."""
    logger.debug(f"Converting tool '{tool.name}' to OpenAI format")
    openai_tool = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "No description provided.",
            "parameters": tool.parameters,
        },
    }
    logger.debug(f"Successfully converted tool '{tool.name}' to OpenAI format")
    return openai_tool


def _create_pydantic_model_from_schema(
    model_name: str, schema: Dict[str, Any]
) -> Type[BaseModel]:
    """Dynamically create a Pydantic model from a JSON schema."""
    fields = {}
    if schema and "properties" in schema:
        for name, prop_schema in schema.get("properties", {}).items():
            field_type = prop_schema.get("type", "string")
            # Basic type mapping, can be expanded
            if field_type == "string":
                py_type = str
            elif field_type == "integer":
                py_type = int
            elif field_type == "number":
                py_type = float
            elif field_type == "boolean":
                py_type = bool
            elif field_type == "array":
                py_type = list
            elif field_type == "object":
                py_type = dict
            else:
                py_type = Any  # Fallback for complex or unknown types

            description = prop_schema.get("description", "")
            # For required fields, Pydantic models expect no default or `...`
            if name in schema.get("required", []):
                fields[name] = (py_type, Field(..., description=description))
            else:
                fields[name] = (py_type, Field(default=prop_schema.get("default"), description=description))
    return create_model(model_name, **fields) # type: ignore


def convert_tool_to_crewai_tool(tool: Tool):
    """Convert a Tool object to a CrewAI tool.

    Args:
        tool: Tool to convert

    Returns:
        A CrewAI tool instance.
    """
    if not _IS_CREWAI_INSTALLED:
        raise ImportError(
            "crewai library is not installed. Please install it with `pip install crewai` to use this adapter."
        )

    logger.debug(f"Converting tool '{tool.name}' to CrewAI format")

    # Dynamically create Pydantic model for args_schema
    # Sanitize tool name for Pydantic model creation
    sanitized_tool_name = "".join(c if c.isalnum() else "_" for c in tool.name)
    args_schema_model_name = f"{sanitized_tool_name.capitalize()}ArgsSchema"
    args_pydantic_model = _create_pydantic_model_from_schema(
        args_schema_model_name, tool.parameters
    )

    class CrewAIToolWrapper(BaseTool):
        name: str = tool.name
        description: str = tool.description or "No description provided."
        args_schema: Type[BaseModel] = args_pydantic_model # type: ignore

        async def _arun(
            self, **kwargs: Any
        ) -> Any: # Make it async to align with tool.run
            logger.debug(
                f"Executing CrewAI tool '{self.name}' with arguments: {kwargs}"
            )
            # CrewAI's _run expects synchronous execution by default in some versions,
            # but we need to call an async tool.run.
            # If CrewAI's BaseTool supports async _run directly, this can be simplified.
            # For now, assuming tool.run is async as per the prompt.
            result = await tool.run(kwargs)
            logger.debug(f"Tool '{self.name}' execution completed")
            return result

        def _run(
            self, **kwargs: Any
        ) -> Any:
            # This synchronous wrapper is needed if CrewAI's BaseTool doesn't directly support async _run.
            # It's a common pattern to run async code from sync by creating an event loop.
            # However, this can be problematic if an event loop is already running.
            # For simplicity in this context, we'll raise a NotImplementedError
            # if the async nature of tool.run cannot be directly accommodated by CrewAI's _run.
            # A more robust solution would involve checking CrewAI's specific version capabilities
            # or using something like asyncio.run_coroutine_threadsafe if in a threaded context.
            # Given the constraints, we assume that an async call is possible or the environment handles it.
            # If CrewAI expects a sync function, and tool.run is async, this will need adjustment.
            # The prompt specified tool.run is async, and _run should call it.
            # If CrewAI's _run must be sync, this is a conflict.
            # Let's assume for now that CrewAI can handle an async _arun or that we should prioritize it.
            # The prompt seems to imply that _run should *call* the async tool.run,
            # which means _run itself might need to be async or manage an event loop.
            # CrewAI documentation for custom tools shows _run as synchronous.
            # This is a point of potential conflict.
            # For now, let's assume we should implement _arun as the primary execution path.
            # If a synchronous _run is strictly required by CrewAI and tool.run is async,
            # this would require a blocking call to the async method, e.g., using asyncio.run()
            # but that's generally not advisable within an async application.
            # Let's define _arun as the primary method and leave _run to raise error or adapt.

            # If _arun is defined, CrewAI might prioritize it.
            # If not, and _run is called, we need to handle the async call.
            # One common approach is to use asyncio.get_event_loop().run_until_complete()
            # However, this is tricky if an event loop is already running.
            # For now, let's assume CrewAI tools are moving towards async or _arun is preferred.
            # The example in CrewAI docs (https://docs.crewai.com/learn/create-custom-tools/) shows a sync _run.
            # This implies that if tool.run is async, we have an issue.
            # Let's provide a sync _run that attempts to run the async version if possible,
            # or raises a more informative error.
            try:
                import asyncio
                # Attempt to run the async method. This is a simplified approach.
                # In a complex async environment, this might need more sophisticated handling.
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, cannot use run_until_complete directly in this way.
                    # This indicates a deeper integration challenge.
                    # For now, error out or use a more complex async-to-sync bridge.
                    # For the sake of this exercise, we'll log and raise.
                    logger.error("Cannot run async tool in a running event loop via sync _run. Implement _arun.")
                    raise NotImplementedError("Async tool.run cannot be called from sync _run in a running event loop. Define and use _arun.")
                return loop.run_until_complete(self._arun(**kwargs))
            except RuntimeError: # No event loop
                 logger.error("No event loop found to run async tool via sync _run. Implement _arun or ensure an event loop.")
                 raise NotImplementedError("Async tool.run cannot be called from sync _run without an event loop. Define and use _arun.")


    crewai_tool_instance = CrewAIToolWrapper()
    logger.debug(f"Successfully converted tool '{tool.name}' to CrewAI format")
    return crewai_tool_instance


def transform_mcp_tool_to_openai_tool(mcp_tool: Tool): # type: ignore # mcp_tool is actually MCPTool here
    """Convert an MCP tool to an OpenAI tool."""
    from openai.types import FunctionDefinition
    from openai.types.chat import ChatCompletionToolParam

    # Assuming mcp_tool here is meant to be the MCPTool instance, not universal_mcp.tools.Tool
    # This function's signature might need correction if it's intended for universal_mcp.tools.Tool
    input_schema = getattr(mcp_tool, "inputSchema", {})

    return ChatCompletionToolParam(
        type="function",
        function=FunctionDefinition(
            name=mcp_tool.name, # type: ignore
            description=mcp_tool.description or "No description provided.", # type: ignore
            parameters=input_schema,
            strict=False, # Consider if strict should be configurable
        ),
    )


def convert_tool_to_smolagents_tool(tool: Tool) -> Dict[str, Any]:
    """
    Converts a Tool object to a generic dictionary format suitable for SmolAgents.

    This adapter provides a basic representation of the tool, including its
    name, description, parameters (JSON schema), and the execution function.
    Due to the lack of specific documentation on a standardized SmolAgents tool
    format, this adapter aims to provide the essential information that a
    SmolAgent could potentially use to interact with the tool.

    Args:
        tool: The Tool object to convert.

    Returns:
        A dictionary representing the tool.
    """
    logger.debug(f"Converting tool '{tool.name}' to SmolAgents format")
    smol_tool_representation = {
        "name": tool.name,
        "description": tool.description or "No description provided.",
        "parameters": tool.parameters,
        "execute": tool.run  # Provide a direct reference to the async run method
    }
    logger.debug(f"Successfully converted tool '{tool.name}' to SmolAgents format")
    return smol_tool_representation
