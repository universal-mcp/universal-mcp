from pydantic import BaseModel, Field
from typing import Callable
import inspect
from loguru import logger
from universal_mcp.exceptions import ToolError
from universal_mcp.tools.func_metadata import func_metadata, FuncMetadata


class Tool(BaseModel):
    """Internal tool registration info."""

    fn: Callable[..., any] = Field(exclude=True)
    name: str = Field(description="Name of the tool")
    description: str = Field(description="Description of what the tool does")
    parameters: dict[str, any] = Field(description="JSON schema for tool parameters")
    fn_metadata: FuncMetadata = Field(
        description="Metadata about the function including a pydantic model for tool"
        " arguments"
    )
    is_async: bool = Field(description="Whether the tool is async")

    @classmethod
    def from_function(
        cls,
        fn: Callable[..., any],
        name: str | None = None,
        description: str | None = None,
    ) -> "Tool":
        """Create a Tool from a function."""

        func_name = name or fn.__name__

        if func_name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")

        func_doc = description or fn.__doc__ or ""
        is_async = inspect.iscoroutinefunction(fn)

        func_arg_metadata = func_metadata(fn)
        parameters = func_arg_metadata.arg_model.model_json_schema()

        return cls(
            fn=fn,
            name=func_name,
            description=func_doc,
            parameters=parameters,
            fn_metadata=func_arg_metadata,
            is_async=is_async,
        )

    def validate_arguments(self, arguments: dict[str, any]) -> dict[str, any]:
        """Validate the arguments against the tool's parameters."""
        return self.fn_metadata.pre_parse_json(arguments)

    async def run(
        self,
        arguments: dict[str, any],
    ) -> any:
        """Run the tool with arguments."""
        try:
            return await self.fn_metadata.call_fn_with_arg_validation(
                self.fn, self.is_async, arguments
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

    def add_tool(self, fn: Callable[..., any]) -> Tool:
        """Add a tool to the server."""
        tool = Tool.from_function(fn)
        existing = self._tools.get(tool.name)
        if existing:
            if self.warn_on_duplicate_tools:
                logger.warning(f"Tool already exists: {tool.name}")
            return existing
        self._tools[tool.name] = tool
        return tool

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, any],
    ) -> any:
        """Call a tool by name with arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")

        return await tool.run(arguments)
