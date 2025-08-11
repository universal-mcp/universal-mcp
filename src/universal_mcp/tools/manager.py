from collections.abc import Callable
from typing import Any

from loguru import logger

from universal_mcp.analytics import analytics
from universal_mcp.applications.application import BaseApplication
from universal_mcp.exceptions import ToolNotFoundError
from universal_mcp.tools.adapters import (
    convert_tool_to_langchain_tool,
    convert_tool_to_mcp_tool,
    convert_tool_to_openai_tool,
)
from universal_mcp.tools.tools import Tool
from universal_mcp.types import ToolFormat

# Constants
DEFAULT_IMPORTANT_TAG = "important"
TOOL_NAME_SEPARATOR = "_"
DEFAULT_APP_NAME = "common"


def _get_app_and_tool_name(tool_name: str) -> tuple[str, str]:
    """Get the app name from a tool name."""
    if TOOL_NAME_SEPARATOR in tool_name:
        app_name = tool_name.split(TOOL_NAME_SEPARATOR, 1)[0]
        tool_name_without_app_name = tool_name.split(TOOL_NAME_SEPARATOR, 1)[1]
    else:
        app_name = DEFAULT_APP_NAME
        tool_name_without_app_name = tool_name
    return app_name, tool_name_without_app_name


def _filter_by_name(tools: list[Tool], tool_names: list[str] | None) -> list[Tool]:
    """Filter tools by name using simple string matching.

    Args:
        tools: List of tools to filter.
        tool_names: List of tool names to match against.

    Returns:
        Filtered list of tools.
    """
    if not tool_names:
        return tools

    logger.debug(f"Filtering tools by names: {tool_names}")
    # Convert names to lowercase for case-insensitive matching
    tool_names = [name.lower() for name in tool_names]
    filtered_tools = []
    for tool in tools:
        for tool_name in tool_names:
            if tool_name in tool.name.lower():
                filtered_tools.append(tool)
                logger.debug(f"Tool '{tool.name}' matched name filter")
                break

    return filtered_tools


def _filter_by_tags(tools: list[Tool], tags: list[str] | None) -> list[Tool]:
    """Filter tools by tags with improved matching logic.

    Args:
        tools: List of tools to filter.
        tags: List of tags to match against.

    Returns:
        Filtered list of tools.
    """
    if not tags:
        return tools

    logger.debug(f"Filtering tools by tags: {tags}")

    # Handle special "all" tag
    if "all" in tags:
        return tools

    # Convert tags to lowercase for case-insensitive matching
    tags_set = {tag.lower() for tag in tags}

    filtered_tools = []
    for tool in tools:
        # Convert tool tags to lowercase for case-insensitive matching
        tool_tags = {tag.lower() for tag in tool.tags}
        if tags_set & tool_tags:  # Check for any matching tags
            filtered_tools.append(tool)
            logger.debug(f"Tool '{tool.name}' matched tags: {tags_set & tool_tags}")

    return filtered_tools


class ToolManager:
    """
    Manages tools

    This class provides functionality for registering, managing, and executing tools.
    It supports multiple tool formats and provides filtering capabilities based on names and tags.
    Tools are organized by their source application for better management.
    """

    def __init__(self, warn_on_duplicate_tools: bool = True, default_format: ToolFormat = ToolFormat.MCP):
        """Initialize the ToolManager.

        Args:
            warn_on_duplicate_tools: Whether to warn when duplicate tool names are detected.
        """
        self._all_tools: dict[str, Tool] = {}
        self.warn_on_duplicate_tools = warn_on_duplicate_tools
        self.default_format = default_format

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name.

        Args:
            name: The name of the tool to retrieve.

        Returns:
            The Tool instance if found, None otherwise.
        """
        return self._all_tools.get(name)

    def list_tools(
        self,
        format: ToolFormat | None = None,
        tags: list[str] | None = None,
        tool_names: list[str] | None = None,
    ) -> list:
        """List all registered tools in the specified format.

        Args:
            format: The format to convert tools to.
            tags: Optional list of tags to filter tools by.
            app_name: Optional app name to filter tools by.
            tool_names: Optional list of tool names to filter by.

        Returns:
            List of tools in the specified format.

        Raises:
            ValueError: If an invalid format is provided.
        """
        if format is None:
            format = self.default_format

        # Start with app-specific tools or all tools
        tools = list(self._all_tools.values())
        # Apply filters
        tools = _filter_by_tags(tools, tags)
        tools = _filter_by_name(tools, tool_names)

        # Convert to requested format
        if format == ToolFormat.NATIVE:
            return [tool.fn for tool in tools]
        if format == ToolFormat.MCP:
            return [convert_tool_to_mcp_tool(tool) for tool in tools]
        elif format == ToolFormat.LANGCHAIN:
            return [convert_tool_to_langchain_tool(tool) for tool in tools]
        elif format == ToolFormat.OPENAI:
            return [convert_tool_to_openai_tool(tool) for tool in tools]
        else:
            raise ValueError(f"Invalid format: {format}")

    def add_tool(self, fn: Callable[..., Any] | Tool, name: str | None = None) -> Tool:
        """Add a tool to the manager.

        Args:
            fn: The tool function or Tool instance to add.
            name: Optional name override for the tool.

        Returns:
            The registered Tool instance.

        Raises:
            ValueError: If the tool name is invalid.
        """
        tool = fn if isinstance(fn, Tool) else Tool.from_function(fn, name=name)

        existing = self._all_tools.get(tool.name)
        if existing:
            if self.warn_on_duplicate_tools:
                if existing.fn is not tool.fn:
                    logger.warning(
                        f"Tool name '{tool.name}' conflicts with an existing tool. Skipping addition of new function."
                    )
                else:
                    logger.debug(f"Tool '{tool.name}' with the same function already exists.")
            return existing

        logger.debug(f"Adding tool: {tool.name}")
        self._all_tools[tool.name] = tool
        return tool

    def register_tools(self, tools: list[Tool]) -> None:
        """Register a list of tools.

        Args:
            tools: List of tools to register.
            app_name: Application name to group the tools under.
        """
        for tool in tools:
            app_name, tool_name = _get_app_and_tool_name(tool.name)

            # Add prefix to tool name, if not already present
            tool.name = f"{app_name}{TOOL_NAME_SEPARATOR}{tool_name}"
            tool.tags.append(app_name)
            self.add_tool(tool)

    def remove_tool(self, name: str) -> bool:
        """Remove a tool by name.

        Args:
            name: The name of the tool to remove.

        Returns:
            True if the tool was removed, False if it didn't exist.
        """
        if name in self._all_tools:
            del self._all_tools[name]
            return True
        return False

    def clear_tools(self) -> None:
        """Remove all registered tools."""
        self._all_tools.clear()

    def register_tools_from_app(
        self,
        app: BaseApplication,
        tool_names: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Register tools from an application.

        Args:
            app: The application to register tools from.
            tool_names: Optional list of specific tool names to register.
            tags: Optional list of tags to filter tools by.
        """
        try:
            functions = app.list_tools()
        except TypeError as e:
            logger.error(f"Error calling list_tools for app '{app.name}'. Error: {e}")
            return
        except Exception as e:
            logger.error(f"Failed to get tool list from app '{app.name}': {e}")
            return

        if not isinstance(functions, list):
            logger.error(f"App '{app.name}' list_tools() did not return a list. Skipping registration.")
            return

        tools = []
        for function in functions:
            if not callable(function):
                logger.warning(f"Non-callable tool from {app.name}: {function}")
                continue

            try:
                tool_instance = Tool.from_function(function)
                tool_instance.name = f"{app.name}{TOOL_NAME_SEPARATOR}{tool_instance.name}"
                if app.name not in tool_instance.tags:
                    tool_instance.tags.append(app.name)
                tools.append(tool_instance)
            except Exception as e:
                tool_name = getattr(function, "__name__", "unknown")
                logger.error(f"Failed to create Tool from '{tool_name}' in {app.name}: {e}")

        if tags:
            tools = _filter_by_tags(tools, tags)

        if tool_names:
            tools = _filter_by_name(tools, tool_names)

        if not tool_names and not tags:
            tools = _filter_by_tags(tools, [DEFAULT_IMPORTANT_TAG])

        self.register_tools(tools)

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Call a tool by name with arguments.

        Args:
            name: The name of the tool to call.
            arguments: The arguments to pass to the tool.
            context: Optional context information for the tool execution.

        Returns:
            The result of the tool execution.

        Raises:
            ToolError: If the tool is not found or execution fails.
        """
        logger.debug(f"Calling tool: {name} with arguments: {arguments}")
        app_name, _ = _get_app_and_tool_name(name)
        tool = self.get_tool(name)
        if not tool:
            logger.error(f"Unknown tool: {name}")
            raise ToolNotFoundError(f"Unknown tool: {name}")
        try:
            result = await tool.run(arguments, context)
            analytics.track_tool_called(name, app_name, "success")
            return result
        except Exception as e:
            analytics.track_tool_called(name, app_name, "error", str(e))
            raise e
