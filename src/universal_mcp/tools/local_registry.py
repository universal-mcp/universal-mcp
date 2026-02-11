"""Local Tool Registry - a catalog of available apps and tools.

Uses FastMCP's Tool and ToolManager internally. Does not manage
integrations or credentials - that is a separate concern.
"""

import base64
import inspect
import os
import re
from collections.abc import Callable
from typing import Any

from fastmcp.tools import Tool
from fastmcp.tools.tool_manager import ToolManager
from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.exceptions import ToolError, ToolNotFoundError
from universal_mcp.tools.adapters import convert_tools
from universal_mcp.tools.utils import list_to_tool_config
from universal_mcp.types import DEFAULT_IMPORTANT_TAG, TOOL_NAME_SEPARATOR, ToolConfig, ToolFormat


def _parse_tags(docstring: str | None) -> set[str]:
    """Extract tags from a docstring's Tags: section."""
    if not docstring:
        return set()
    match = re.search(r"Tags:\s*(.+?)(?:\n\s*\n|\Z)", docstring, re.DOTALL | re.IGNORECASE)
    if not match:
        return set()
    raw = match.group(1)
    return {t.strip().lower() for line in raw.splitlines() for t in line.split(",") if t.strip()}


def _make_tool_name(app_name: str | None, fn_name: str) -> str:
    """Build the full tool name with optional app prefix."""
    if app_name:
        return f"{app_name}{TOOL_NAME_SEPARATOR}{fn_name}"
    return fn_name


class LocalRegistry:
    """A catalog of available apps and tools.

    Uses FastMCP's ToolManager under the hood. Provides registration,
    search, filtering, and execution of tools.
    """

    def __init__(self, output_dir: str = "output"):
        self._apps: dict[str, BaseApplication] = {}
        self.tool_manager = ToolManager()
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    # ── Register ──────────────────────────────────────────────

    def register_app(
        self,
        app: BaseApplication,
        tool_names: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Register an application and its tools.

        Args:
            app: Application instance to register.
            tool_names: Specific tools to register (None = default tools with "important" tag).
            tags: Filter tools by tags (None = use "important" default).
        """
        self._apps[app.name] = app

        try:
            functions = app.list_tools()
        except Exception as e:
            logger.error(f"Failed to get tools from app '{app.name}': {e}")
            return

        if not isinstance(functions, list):
            logger.error(f"App '{app.name}' list_tools() did not return a list")
            return

        # Create Tool instances from functions
        tools = []
        for fn in functions:
            if not callable(fn):
                continue
            try:
                fn_name = getattr(fn, "__name__", None)
                if not fn_name:
                    continue
                docstring_tags = _parse_tags(inspect.getdoc(fn))
                docstring_tags.add(app.name)
                full_name = _make_tool_name(app.name, fn_name)
                tool = Tool.from_function(fn, name=full_name, tags=docstring_tags)
                tools.append((fn_name, tool, docstring_tags))
            except Exception as e:
                logger.error(f"Failed to create tool from '{getattr(fn, '__name__', '?')}': {e}")

        # Filter by tags
        if tags:
            tag_set = {t.lower() for t in tags}
            if "all" not in tag_set:
                tools = [(n, t, dt) for n, t, dt in tools if tag_set & dt]
        elif not tool_names:
            # Default: only register "important" tagged tools
            tools = [(n, t, dt) for n, t, dt in tools if DEFAULT_IMPORTANT_TAG in dt]

        # Filter by name
        if tool_names:
            name_set = {n.lower() for n in tool_names}
            tools = [(n, t, dt) for n, t, dt in tools if n.lower() in name_set]

        for _, tool, _ in tools:
            self.tool_manager.add_tool(tool)

        logger.info(f"Registered app '{app.name}' with {len(tools)} tools")

    def register_tool(
        self,
        fn: Callable[..., Any] | Tool,
        name: str | None = None,
        app_name: str | None = None,
    ) -> Tool:
        """Register a standalone tool function.

        Args:
            fn: A callable function or FastMCP Tool instance.
            name: Optional name override.
            app_name: Optional app name to namespace the tool under.

        Returns:
            The registered FastMCP Tool instance.
        """
        if isinstance(fn, Tool):
            tool = fn
        else:
            fn_name = name or getattr(fn, "__name__", "unknown")
            docstring_tags = _parse_tags(inspect.getdoc(fn))
            if app_name:
                docstring_tags.add(app_name)
            full_name = _make_tool_name(app_name, fn_name)
            tool = Tool.from_function(fn, name=full_name, tags=docstring_tags)

        return self.tool_manager.add_tool(tool)

    def register_remote_app(
        self,
        app: "BaseApplication",
        proxy_tools: list,
    ) -> None:
        """Register pre-built proxy tools from a remote MCP application.

        Unlike register_app(), this skips Tool.from_function() and adds
        fully-formed Tool instances directly to the tool manager.

        Args:
            app: The remote MCP application instance.
            proxy_tools: List of ProxyTool instances (already have correct names/schemas).
        """
        self._apps[app.name] = app

        for tool in proxy_tools:
            self.tool_manager.add_tool(tool)

        logger.info(f"Registered remote app '{app.name}' with {len(proxy_tools)} proxy tools")

    # ── Internal ToolManager access ───────────────────────────

    def _get_tool(self, name: str) -> Tool | None:
        """Get a tool by name from the internal ToolManager."""
        return self.tool_manager._tools.get(name)

    def _iter_tools(self) -> list[Tool]:
        """Get all tools from the internal ToolManager."""
        return list(self.tool_manager._tools.values())

    def _has_tool(self, name: str) -> bool:
        """Check if a tool exists in the ToolManager."""
        return name in self.tool_manager._tools

    def _tool_names(self) -> list[str]:
        """Get all tool names from the ToolManager."""
        return list(self.tool_manager._tools.keys())

    # ── Query ─────────────────────────────────────────────────

    def get_app(self, app_name: str) -> BaseApplication | None:
        """Get a registered app by name."""
        return self._apps.get(app_name)

    def list_apps(self) -> list[str]:
        """List all registered app names."""
        return list(self._apps.keys())

    def list_tools(
        self,
        app_name: str | None = None,
        tool_names: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> list[Tool]:
        """List registered tools, optionally filtered by app, name, or tags."""
        tools = self._iter_tools()

        if app_name:
            prefix = f"{app_name}{TOOL_NAME_SEPARATOR}"
            tools = [t for t in tools if t.name.startswith(prefix)]

        if tags:
            tag_set = {t.lower() for t in tags}
            if "all" not in tag_set:
                tools = [t for t in tools if tag_set & {tg.lower() for tg in t.tags}]

        if tool_names:
            name_set = {n.lower() for n in tool_names}
            tools = [t for t in tools if t.name.lower() in name_set]

        return tools

    # ── Search ────────────────────────────────────────────────

    def search_apps(self, query: str) -> list[str]:
        """Search registered apps by name (case-insensitive substring match)."""
        q = query.lower()
        return [name for name in self._apps if q in name.lower()]

    def search_tools(self, query: str) -> list[Tool]:
        """Search tools by name, description, or tags (case-insensitive)."""
        q = query.lower()
        results = []
        for tool in self._iter_tools():
            if q in tool.name.lower():
                results.append(tool)
            elif tool.description and q in tool.description.lower():
                results.append(tool)
            elif any(q in tag.lower() for tag in tool.tags):
                results.append(tool)
        return results

    # ── Load (bulk) ───────────────────────────────────────────

    def load_tools(self, tools: list[str] | ToolConfig) -> list[Tool]:
        """Bulk-load tools from a list of names or a ToolConfig dict.

        Args:
            tools: Either a list like ["github__create_issue"]
                   or a dict like {"github": ["create_issue"]}.

        Returns:
            List of loaded Tool instances.
        """
        if isinstance(tools, list):
            tool_config = list_to_tool_config(tools)
        elif isinstance(tools, dict):
            tool_config = tools
        else:
            raise ValueError(f"Invalid tools type: {type(tools)}. Expected list or dict.")

        for app_name, tool_names in tool_config.items():
            if app_name not in self._apps:
                self._create_and_register_app(app_name, tool_names or None)
            else:
                self.register_app(self._apps[app_name], tool_names=tool_names)

        return self._iter_tools()

    def _create_and_register_app(self, app_name: str, tool_names: list[str] | None) -> None:
        """Create an app from slug and register it."""
        from universal_mcp.applications.utils import app_from_slug

        try:
            app_class = app_from_slug(app_name)
            app = app_class(name=app_name)
            self.register_app(app, tool_names=tool_names)
        except Exception as e:
            logger.error(f"Failed to load app '{app_name}': {e}", exc_info=True)

    # ── Execute ───────────────────────────────────────────────

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Call a registered tool by name."""
        if not self._has_tool(tool_name):
            raise ToolNotFoundError(f"Tool '{tool_name}' not found.")

        tool = self._get_tool(tool_name)
        result = await tool.run(tool_args)

        # FastMCP returns a ToolResult; extract the actual content
        if hasattr(result, 'content') and result.content:
            first_content = result.content[0]
            if hasattr(first_content, 'text'):
                result = first_content.text

        return self._handle_file_output(result)

    # ── Export ────────────────────────────────────────────────

    def export_tools(
        self,
        tools: list[str] | ToolConfig,
        format: ToolFormat,
    ) -> list[Any]:
        """Export registered tools to a specific format (MCP, OpenAI, LangChain)."""
        loaded_tools = self.list_tools()
        return convert_tools(loaded_tools, format)

    # ── Remove / Clear ────────────────────────────────────────

    def remove_app(self, app_name: str) -> bool:
        """Remove an app and all its tools."""
        if app_name not in self._apps:
            return False

        prefix = f"{app_name}{TOOL_NAME_SEPARATOR}"
        to_remove = [name for name in self._tool_names() if name.startswith(prefix)]
        for name in to_remove:
            self.tool_manager.remove_tool(name)

        del self._apps[app_name]
        logger.info(f"Removed app '{app_name}'")
        return True

    def remove_tool(self, tool_name: str) -> bool:
        """Remove a single tool by its full name."""
        if self._has_tool(tool_name):
            self.tool_manager.remove_tool(tool_name)
            return True
        return False

    def clear(self) -> None:
        """Clear all apps and tools."""
        self._apps.clear()
        for name in self._tool_names():
            self.tool_manager.remove_tool(name)
        logger.info("Registry cleared")

    # ── Helpers ───────────────────────────────────────────────

    def _handle_file_output(self, data: Any) -> Any:
        """Save file outputs (images, audio) to disk."""
        if isinstance(data, dict) and data.get("type") in ["image", "audio"]:
            base64_data = data.get("data")
            file_name = data.get("file_name")
            if not base64_data or not file_name:
                raise ToolError("File data or name is missing")

            bytes_data = base64.b64decode(base64_data)
            file_path = os.path.join(self.output_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(bytes_data)
            return f"File saved to: {file_path}"
        return data

    def __len__(self) -> int:
        return len(self._iter_tools())

    def __repr__(self) -> str:
        return f"LocalRegistry(apps={len(self._apps)}, tools={len(self)})"
