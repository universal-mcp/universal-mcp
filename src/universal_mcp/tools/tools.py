from __future__ import annotations as _annotations

import inspect
from collections.abc import Callable
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from universal_mcp.exceptions import ToolError
from universal_mcp.utils.docstring_parser import parse_docstring

from .func_metadata import FuncMetadata


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

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    # Modified add_tool to accept name override explicitly
    def add_tool(self, fn: Callable[..., Any], name: str | None = None) -> Tool: # Changed any to Any
        """Add a tool to the server, allowing name override."""
        # Create the Tool object using the provided name if available
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
