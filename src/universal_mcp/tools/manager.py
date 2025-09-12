from collections.abc import Callable
from typing import Any

from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.tools.tools import Tool
from universal_mcp.types import DEFAULT_APP_NAME, DEFAULT_IMPORTANT_TAG, TOOL_NAME_SEPARATOR, ToolFormat


def _get_app_and_tool_name(tool_name: str) -> tuple[str, str]:
    """Get the app name from a tool name."""
    if TOOL_NAME_SEPARATOR in tool_name:
        app_name = tool_name.split(TOOL_NAME_SEPARATOR, 1)[0]
        tool_name_without_app_name = tool_name.split(TOOL_NAME_SEPARATOR, 1)[1]
    else:
        app_name = DEFAULT_APP_NAME
        tool_name_without_app_name = tool_name
    return app_name, tool_name_without_app_name


def _sanitize_tool_names(tool_names: list[str]) -> list[str]:
    """Sanitize tool names by removing empty strings and converting to lowercase."""
    return [_get_app_and_tool_name(name)[1].lower() for name in tool_names if name]


def _filter_by_name(tools: list[Tool], tool_names: list[str] | None) -> list[Tool]:
    """Filter tools by name using set comparison for efficient matching.

    Args:
        tools: List of tools to filter.
        tool_names: List of tool names to match against.

    Returns:
        Filtered list of tools.
    """
    if not tool_names:
        return tools
    logger.debug(f"All tools: {[tool.name for tool in tools]}")
    logger.debug(f"Filtering tools by names: {tool_names}")
    tool_names_set = set(_sanitize_tool_names(tool_names))
    logger.debug(f"Tool names set: {tool_names_set}")
    filtered_tools = []
    for tool in tools:
        if tool.tool_name.lower() in tool_names_set:
            filtered_tools.append(tool)
            logger.debug(f"Tool '{tool.name}' matched name filter")
    logger.debug(f"Filtered tools: {[tool.name for tool in filtered_tools]}")
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

    def get_tools(
        self,
        tags: list[str] | None = None,
        tool_names: list[str] | None = None,
    ) -> list[Tool]:
        """Get a filtered list of registered tools.

        Args:
            tags: Optional list of tags to filter tools by.
            tool_names: Optional list of tool names to filter by.

        Returns:
            A list of Tool instances.
        """
        tools = list(self._all_tools.values())
        tools = _filter_by_tags(tools, tags)
        tools = _filter_by_name(tools, tool_names)
        return tools

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
                tool_instance.app_name = app.name
                if app.name not in tool_instance.tags:
                    tool_instance.tags.append(app.name)
                tools.append(tool_instance)
            except Exception as e:
                tool_name = getattr(function, "__name__", "unknown")
                logger.error(f"Failed to create Tool from '{tool_name}' in {app.name}: {e}")
        # logger.debug([tool.name for tool in tools])
        if tags:
            tools = _filter_by_tags(tools, tags)

        if tool_names:
            tools = _filter_by_name(tools, tool_names)

        if not tool_names and not tags:
            tools = _filter_by_tags(tools, [DEFAULT_IMPORTANT_TAG])

        self.register_tools(tools)
