import json
from collections.abc import Callable
from typing import Any

from loguru import logger

from universal_mcp.analytics import analytics
from universal_mcp.applications.application import BaseApplication
from universal_mcp.exceptions import ToolError
from universal_mcp.tools.adapters import (
    ToolFormat,
    convert_tool_to_langchain_tool,
    convert_tool_to_mcp_tool,
    convert_tool_to_openai_tool,
)
from universal_mcp.tools.tools import Tool

# Constants
DEFAULT_IMPORTANT_TAG = "important"
TOOL_NAME_SEPARATOR = "_"


def _filter_by_name(tools: list[Tool], tool_names: list[str]) -> list[Tool]:
    if not tool_names:
        return tools
    return [tool for tool in tools if tool.name in tool_names]


def _filter_by_tags(tools: list[Tool], tags: list[str] | None) -> list[Tool]:
    tags = tags or [DEFAULT_IMPORTANT_TAG]
    return [tool for tool in tools if any(tag in tool.tags for tag in tags)]


class ToolManager:
    """Manages FastMCP tools.

    This class provides functionality for registering, managing, and executing tools.
    It supports multiple tool formats and provides filtering capabilities based on names and tags.
    """

    def __init__(self, warn_on_duplicate_tools: bool = True):
        """Initialize the ToolManager.

        Args:
            warn_on_duplicate_tools: Whether to warn when duplicate tool names are detected.
        """
        self._tools: dict[str, Tool] = {}
        self.warn_on_duplicate_tools = warn_on_duplicate_tools

    def get_tool(self, name: str) -> Tool | None:
        """Get tool by name.

        Args:
            name: The name of the tool to retrieve.

        Returns:
            The Tool instance if found, None otherwise.
        """
        return self._tools.get(name)

    def list_tools(
        self,
        format: ToolFormat = ToolFormat.MCP,
        tags: list[str] | None = None,
    ) -> list[Tool]:
        """List all registered tools in the specified format.

        Args:
            format: The format to convert tools to.

        Returns:
            List of tools in the specified format.

        Raises:
            ValueError: If an invalid format is provided.
        """

        tools = []
        if tags:
            tools = [
                tool
                for tool in self._tools.values()
                if any(tag in tool.tags for tag in tags)
            ]
        else:
            tools = list(self._tools.values())

        if format == ToolFormat.MCP:
            tools = [convert_tool_to_mcp_tool(tool) for tool in tools]
        elif format == ToolFormat.LANGCHAIN:
            tools = [
                convert_tool_to_langchain_tool(tool) for tool in self._tools.values()
            ]
        elif format == ToolFormat.OPENAI:
            tools = [convert_tool_to_openai_tool(tool) for tool in self._tools.values()]
        else:
            raise ValueError(f"Invalid format: {format}")

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

        if not tool.name or not isinstance(tool.name, str):
            raise ValueError("Tool name must be a non-empty string")

        existing = self._tools.get(tool.name)
        if existing:
            if self.warn_on_duplicate_tools:
                if existing.fn is not tool.fn:
                    logger.warning(
                        f"Tool name '{tool.name}' conflicts with an existing tool. Skipping addition of new function."
                    )
                else:
                    logger.debug(
                        f"Tool '{tool.name}' with the same function already exists."
                    )
            return existing

        logger.debug(f"Adding tool: {tool.name}")
        self._tools[tool.name] = tool
        return tool

    def register_tools(self, tools: list[Tool]) -> None:
        """Register a list of tools."""
        for tool in tools:
            self.add_tool(tool)

    def remove_tool(self, name: str) -> bool:
        """Remove a tool by name.

        Args:
            name: The name of the tool to remove.

        Returns:
            True if the tool was removed, False if it didn't exist.
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def clear_tools(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()

    def register_tools_from_app(
        self,
        app: BaseApplication,
        tool_names: list[str] = None,
        tags: list[str] = None,
    ) -> None:
        """Register tools from an application.

        Args:
            app: The application to register tools from.
            tools: Optional list of specific tool names to register.
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
            logger.error(
                f"App '{app.name}' list_tools() did not return a list. Skipping registration."
            )
            return

        tools = []
        for function in functions:
            if not callable(function):
                logger.warning(f"Non-callable tool from {app.name}: {function}")
                continue

            try:
                tool_instance = Tool.from_function(function)
                tool_instance.name = (
                    f"{app.name}{TOOL_NAME_SEPARATOR}{tool_instance.name}"
                )
                tool_instance.tags.append(
                    app.name
                ) if app.name not in tool_instance.tags else None
                tools.append(tool_instance)
            except Exception as e:
                tool_name = getattr(function, "__name__", "unknown")
                logger.error(
                    f"Failed to create Tool from '{tool_name}' in {app.name}: {e}"
                )

        tools = _filter_by_name(tools, tool_names)
        tools = _filter_by_tags(tools, tags)
        self.register_tools(tools)
        return

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
        tool = self.get_tool(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")

        try:
            result = await tool.run(arguments, context)
            app_name = tool.name.split(TOOL_NAME_SEPARATOR)[0]
            analytics.track_tool_called(name, app_name, "success")
            return result
        except Exception as e:
            app_name = tool.name.split(TOOL_NAME_SEPARATOR)[0]
            analytics.track_tool_called(name, app_name, "error", str(e))
            raise ToolError(f"Tool execution failed: {str(e)}") from e

    async def handle_tool_calls(
        self, response: Any, format: ToolFormat = ToolFormat.OPENAI
    ) -> Any:
        """Handle tool calls from a openai response.

        Args:
            response: The response containing tool calls to handle.
            format: The format of the response (default: OPENAI)

        Returns:
            Tuple containing:
            - List of tool execution results
            - List of tool call messages for conversation history

        Raises:
            ToolError: If tool execution fails.
            ValueError: If the response format is invalid.
        """
        if format == ToolFormat.OPENAI:
            results = []
            tool_messages = []

            if not hasattr(response, "choices") or not response.choices:
                raise ValueError("Invalid response format: missing choices")

            response_message = response.choices[0].message
            if not hasattr(response_message, "tool_calls"):
                raise ValueError("Invalid response format: missing tool_calls")

            for tool_call in response_message.tool_calls:
                try:
                    name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    result = await self.call_tool(name, arguments)

                    # Add successful tool call message
                    tool_messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": name,
                            "content": str(result),
                        }
                    )
                    results.append(result)

                except json.JSONDecodeError as e:
                    error_msg = f"Invalid tool arguments JSON: {e}"
                    tool_messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": name,
                            "content": error_msg,
                        }
                    )
                    raise ToolError(error_msg) from e
                except Exception as e:
                    error_msg = f"Tool call failed: {e}"
                    tool_messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": name,
                            "content": error_msg,
                        }
                    )
                    raise ToolError(error_msg) from e

            return results, tool_messages
