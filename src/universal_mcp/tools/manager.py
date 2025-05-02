from collections.abc import Callable
from typing import Any, Literal

from loguru import logger

from universal_mcp.analytics import analytics
from universal_mcp.applications.application import BaseApplication
from universal_mcp.exceptions import ToolError
from universal_mcp.tools.adapters import (
    convert_tool_to_langchain_tool,
    convert_tool_to_mcp_tool,
    convert_tool_to_openai_tool,
)
from universal_mcp.tools.tools import Tool


class ToolManager:
    """Manages FastMCP tools."""

    def __init__(self, warn_on_duplicate_tools: bool = True):
        self._tools: dict[str, Tool] = {}
        self.warn_on_duplicate_tools = warn_on_duplicate_tools

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name."""
        return self._tools.get(name)

    def list_tools(
        self, format: Literal["mcp", "langchain", "openai"] = "mcp"
    ) -> list[Tool]:
        """List all registered tools."""
        if format == "mcp":
            return [convert_tool_to_mcp_tool(tool) for tool in self._tools.values()]
        elif format == "langchain":
            return [
                convert_tool_to_langchain_tool(tool) for tool in self._tools.values()
            ]
        elif format == "openai":
            return [convert_tool_to_openai_tool(tool) for tool in self._tools.values()]
        else:
            raise ValueError(f"Invalid format: {format}")

    # Modified add_tool to accept name override explicitly
    def add_tool(
        self, fn: Callable[..., Any] | Tool, name: str | None = None
    ) -> Tool:  # Changed any to Any
        """Add a tool to the server, allowing name override."""
        # Create the Tool object using the provided name if available
        tool = fn if isinstance(fn, Tool) else Tool.from_function(fn, name=name)
        existing = self._tools.get(tool.name)
        if existing:
            if self.warn_on_duplicate_tools:
                # Check if it's the *exact* same function object being added again
                if existing.fn is not tool.fn:
                    logger.warning(
                        f"Tool name '{tool.name}' conflicts with an existing tool. Skipping addition of new function."
                    )
                else:
                    logger.debug(
                        f"Tool '{tool.name}' with the same function already exists."
                    )
            return existing  # Return the existing tool if name conflicts

        logger.debug(f"Adding tool: {tool.name}")
        self._tools[tool.name] = tool
        return tool

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        context=None,
    ) -> Any:
        """Call a tool by name with arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")
        try:
            result = await tool.run(arguments)
            analytics.track_tool_called(name, "success")
            return result
        except Exception as e:
            analytics.track_tool_called(name, "error", str(e))
            raise

    def get_tools_by_tags(self, tags: list[str]) -> list[Tool]:
        """Get tools by tags."""
        return [
            tool
            for tool in self._tools.values()
            if any(tag in tool.tags for tag in tags)
        ]

    def register_tools_from_app(
        self,
        app: BaseApplication,
        tools: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        try:
            available_tool_functions = app.list_tools()
        except TypeError as e:
            logger.error(f"Error calling list_tools for app '{app.name}'. Error: {e}")
            return
        except Exception as e:
            logger.error(f"Failed to get tool list from app '{app.name}': {e}")
            return

        if not isinstance(available_tool_functions, list):
            logger.error(
                f"App '{app.name}' list_tools() did not return a list. Skipping registration."
            )
            return

        # Determine the effective filter lists *before* the loop for efficiency
        # Use an empty list if None is passed, simplifies checks later
        tools_name_filter = tools or []

        # For tags, determine the filter list based on priority: passed 'tags' or default 'important'
        # This list is only used if tools_name_filter is empty.
        active_tags_filter = tags if tags else ["important"]  # Default filter

        logger.debug(
            f"Registering tools for '{app.name}'. Name filter: {tools_name_filter or 'None'}. Tag filter (if name filter empty): {active_tags_filter}"
        )

        for tool_func in available_tool_functions:
            if not callable(tool_func):
                logger.warning(
                    f"Item returned by {app.name}.list_tools() is not callable: {tool_func}. Skipping."
                )
                continue

            try:
                # Create the Tool metadata object from the function.
                # This parses docstring (including tags), gets signature etc.
                tool_instance = Tool.from_function(tool_func)
            except Exception as e:
                logger.error(
                    f"Failed to create Tool object from function '{getattr(tool_func, '__name__', 'unknown')}' in app '{app.name}': {e}"
                )
                continue  # Skip this tool if metadata creation fails

            # --- Modify the Tool instance before filtering/registration ---
            original_name = tool_instance.name
            prefixed_name = f"{app.name}_{original_name}"
            tool_instance.name = prefixed_name  # Update the name

            # Add the app name itself as a tag for categorization
            if app.name not in tool_instance.tags:
                tool_instance.tags.append(app.name)

            # --- Filtering Logic ---
            should_register = False  # Default to not registering

            if tools_name_filter:
                # --- Primary Filter: Check against specific tool names ---
                if tool_instance.name in tools_name_filter:
                    should_register = True
                    logger.debug(f"Tool '{tool_instance.name}' matched name filter.")
                # If not in the name filter, it's skipped (should_register remains False)

            else:
                # --- Secondary Filter: Check against tags (since tools_name_filter is empty) ---
                # Check if *any* tag in active_tags_filter exists in the tool's tags
                # tool_instance.tags includes tags parsed from the docstring + app.name
                if any(tag in tool_instance.tags for tag in active_tags_filter):
                    should_register = True
                    logger.debug(
                        f"Tool '{tool_instance.name}' matched tag filter {active_tags_filter}."
                    )
                # else:
                #     logger.debug(f"Tool '{tool_instance.name}' did NOT match tag filter {active_tags_filter}. Tool tags: {tool_instance.tags}")

            # --- Add the tool if it passed the filters ---
            if should_register:
                # Pass the fully configured Tool *instance* to add_tool
                self.add_tool(tool_instance)
            # else: If not registered, optionally log it for debugging:
            #    logger.trace(f"Tool '{tool_instance.name}' skipped due to filters.") # Use trace level
