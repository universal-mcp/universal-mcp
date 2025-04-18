from __future__ import annotations as _annotations

import inspect
from collections.abc import Callable
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel, Field

from universal_mcp.applications.application import Application
from universal_mcp.exceptions import ToolError
from universal_mcp.utils.docstring_parser import parse_docstring

from .func_metadata import FuncMetadata


def convert_tool_to_mcp_tool(
    tool: Tool,
):
    from mcp.server.fastmcp.server import MCPTool
    return MCPTool(
        name=tool.name,
        description=tool.description or "",
        inputSchema=tool.parameters,
    )

# MODIFY THIS FUNCTION:
def convert_tool_to_langchain_tool(
    tool: Tool,
):
    """Convert a Tool object to a LangChain StructuredTool.

    NOTE: this tool can be executed only in a context of an active MCP client session.

    Args:
        tool: Tool object to convert

    Returns:
        a LangChain StructuredTool
    """
    from langchain_core.tools import StructuredTool,ToolException # Keep import inside if preferred, or move top

    async def call_tool(
        **arguments: dict[str, any], # arguments received here are validated by StructuredTool
    ):
        # tool.run already handles validation via fn_metadata.call_fn_with_arg_validation
        # It should be able to handle the validated/coerced types from StructuredTool
        try:
            call_tool_result = await tool.run(arguments)
            return call_tool_result
        except ToolError as e:
             # Langchain expects ToolException for controlled errors
             raise ToolException(f"Error running tool '{tool.name}': {e}") from e
        except Exception as e:
            # Catch unexpected errors
            raise ToolException(f"Unexpected error in tool '{tool.name}': {e}") from e


    return StructuredTool(
        name=tool.name,
        description=tool.description or f"Tool named {tool.name}.", # Provide fallback description
        coroutine=call_tool,
        args_schema=tool.fn_metadata.arg_model, # <<< --- ADD THIS LINE
        # handle_tool_error=True, # Optional: Consider adding error handling config
        # return_direct=False,    # Optional: Default is usually fine
        # response_format="content", # This field might not be valid for StructuredTool, check LangChain docs if needed. Let's remove for now.
    )

class Tool(BaseModel):
    """Internal tool registration info."""

    fn: Callable[..., Any] = Field(exclude=True)
    name: str = Field(description="Name of the tool")
    description: str = Field(
        description="Summary line from the tool's docstring"
    )
    args_description: dict[str, str] = Field(
        default_factory=dict, description="Descriptions of arguments from the docstring"
    )
    returns_description: str = Field(
        default="", description="Description of the return value from the docstring"
    )
    raises_description: dict[str, str] = Field(
        default_factory=dict, description="Descriptions of exceptions raised from the docstring"
    )
    tags: list[str] = Field(
        default_factory=list, description="Tags for categorizing the tool"
        )
    parameters: dict[str, Any] = Field(description="JSON schema for tool parameters")
    fn_metadata: FuncMetadata = Field(
        description="Metadata about the function including a pydantic model for tool"
        " arguments"
    )
    is_async: bool = Field(description="Whether the tool is async")

    @classmethod
    def from_function(
        cls,
        fn: Callable[..., Any],
        name: str | None = None,
    ) -> Tool:
        """Create a Tool from a function."""

        func_name = name or fn.__name__

        if func_name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")

        raw_doc = inspect.getdoc(fn)
        parsed_doc = parse_docstring(raw_doc)
        
        is_async = inspect.iscoroutinefunction(fn)

        func_arg_metadata = FuncMetadata.func_metadata(
            fn,
        )
        parameters = func_arg_metadata.arg_model.model_json_schema()

        return cls(
            fn=fn,
            name=func_name,
            description=parsed_doc["summary"],
            args_description=parsed_doc["args"],
            returns_description=parsed_doc["returns"],
            raises_description=parsed_doc["raises"],
            tags=parsed_doc["tags"],
            parameters=parameters,
            fn_metadata=func_arg_metadata,
            is_async=is_async,
        )

    async def run(
        self,
        arguments: dict[str, Any],
        context = None,
    ) -> Any:
        """Run the tool with arguments."""
        try:
            return await self.fn_metadata.call_fn_with_arg_validation(
                self.fn,
                self.is_async,
                arguments,
                None
            )
        except Exception as e:
            raise ToolError(f"Error executing tool {self.name}: {e}") from e
        
class ToolManager:
    """Manages FastMCP tools."""

    def __init__(self, warn_on_duplicate_tools: bool = True):
        self._tools: dict[str, Tool] = {}
        self.warn_on_duplicate_tools = warn_on_duplicate_tools

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name."""
        return self._tools.get(name)

    def list_tools(self, format: Literal["mcp", "langchain"] = "mcp") -> list[Tool]:
        """List all registered tools."""
        if format == "mcp":
            return [convert_tool_to_mcp_tool(tool) for tool in self._tools.values()]
        elif format == "langchain":
            return [convert_tool_to_langchain_tool(tool) for tool in self._tools.values()]
        else:
            raise ValueError(f"Invalid format: {format}")

    # Modified add_tool to accept name override explicitly
    def add_tool(self, fn: Callable[..., Any] | Tool, name: str | None = None) -> Tool: # Changed any to Any
        """Add a tool to the server, allowing name override."""
        # Create the Tool object using the provided name if available
        if isinstance(fn, Tool):
            tool = fn
        else:
            tool = Tool.from_function(fn, name=name)
        existing = self._tools.get(tool.name)
        if existing:
            if self.warn_on_duplicate_tools:
                # Check if it's the *exact* same function object being added again
                if existing.fn is not tool.fn:
                     logger.warning(f"Tool name '{tool.name}' conflicts with an existing tool. Skipping addition of new function.")
                else:
                     logger.debug(f"Tool '{tool.name}' with the same function already exists.")
            return existing # Return the existing tool if name conflicts

        logger.debug(f"Adding tool: {tool.name}")
        self._tools[tool.name] = tool
        return tool

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any], # Changed any to Any
        context = None,
    ) -> Any: # Changed any to Any
        """Call a tool by name with arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")

        return await tool.run(arguments)

    def get_tools_by_tags(self, tags: list[str]) -> list[Tool]:
        """Get tools by tags."""
        return [tool for tool in self._tools.values() if any(tag in tool.tags for tag in tags)]
    
    def register_tools_from_app(self, app: Application, tools: list[str] | None = None, tags: list[str] | None = None) -> None:
        """Register tools from an application instance, applying filters if provided."""
        # Ensure filters are lists for easier handling, default to empty if None
        tools_filter = tools or []
        tags_filter = tags or []

        # Call list_tools() correctly - it returns a list of *callable functions/methods*
        # from the specific Application instance (e.g., GithubApp instance)
        try:
            # list_tools in Application subclasses should not take arguments
            available_tool_functions = app.list_tools()
        except TypeError as e:
            logger.error(f"Error calling list_tools for app '{app.name}'. Does its list_tools method accept arguments? It shouldn't. Error: {e}")
            return # Stop processing this app if list_tools is wrong

        if not isinstance(available_tool_functions, list):
             logger.error(f"App '{app.name}' list_tools() did not return a list. Skipping registration.")
             return

        # Iterate over the actual function/method objects returned by app.list_tools()
        for tool_func in available_tool_functions:
            if not callable(tool_func):
                logger.warning(f"Item returned by {app.name}.list_tools() is not callable: {tool_func}. Skipping.")
                continue

            # Create the Tool metadata object from the function/method
            # This parses docstrings, gets signature, etc.
            try:
                # tool_func is the loop variable, representing the function itself (e.g., GithubApp.star_repository)
                tool_instance = Tool.from_function(tool_func)
            except Exception as e:
                 logger.error(f"Failed to create Tool object from function '{getattr(tool_func, '__name__', 'unknown')}' in app '{app.name}': {e}")
                 continue # Skip this tool if metadata creation fails

            # --- Modify the Tool instance before registration ---

            # 1. Prefix the name with the app name
            original_name = tool_instance.name # Get the name derived from the function
            prefixed_name = f"{app.name}_{original_name}"
            tool_instance.name = prefixed_name # Update the name on the Tool instance

            # 2. Add the app name itself as a tag for categorization/filtering
            # Use setdefault to avoid adding if already present (though unlikely here)
            if app.name not in tool_instance.tags:
                 tool_instance.tags.append(app.name)

            # --- Filtering logic (using the *modified* tool_instance) ---
            should_register = True

            # Apply 'tools' filter first (list of specific tool names to include)
            if tools_filter: # Check if the tools filter list is not empty
                should_register = tool_instance.name in tools_filter
            # Only apply 'tags' filter if 'tools' filter wasn't provided or didn't exclude the tool
            elif tags_filter and should_register: # Check if the tag filter list is not empty
                # Check if *any* specified tag exists in the tool's combined tags
                should_register = any(tag in tool_instance.tags for tag in tags_filter)
            # If both filters are empty, should_register remains True

            # --- Add the tool if it passed the filters ---
            if should_register:
                # Pass the fully configured Tool *instance* to add_tool
                self.add_tool(tool_instance)