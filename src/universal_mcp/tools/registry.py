from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.tools.manager import ToolManager, _get_app_and_tool_name
from universal_mcp.types import ToolConfig, ToolFormat


class ToolRegistry(ABC):
    """
    Abstract base class for tool registries, defining a common interface and providing
    shared tool loading functionality.
    """

    def __init__(self):
        """Initializes the registry and its internal tool manager."""
        self._app_instances = {}
        self.tool_manager = ToolManager()
        logger.debug(f"{self.__class__.__name__} initialized.")

    # --- Abstract methods for the public interface ---

    @abstractmethod
    async def list_all_apps(self) -> list[dict[str, Any]]:
        """Get a list of all available apps from the platform."""
        pass

    @abstractmethod
    async def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app."""
        pass

    @abstractmethod
    async def search_apps(self, query: str, limit: int = 2, distance_threshold: float = 0.6) -> list[dict[str, Any]]:
        """Search for apps by a query."""
        pass

    @abstractmethod
    async def list_tools(self, app_id: str) -> list[dict[str, Any]]:
        """List all tools available for a specific app."""
        pass

    @abstractmethod
    async def search_tools(
        self, query: str, limit: int = 2, app_id: str | None = None, distance_threshold: float = 0.6
    ) -> list[dict[str, Any]]:
        """Search for tools by a query, optionally filtered by an app."""
        pass

    @abstractmethod
    async def export_tools(self, tools: list[str] | ToolConfig, format: ToolFormat) -> list[Any]:
        """Export a selection of tools to a specified format."""
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Call a tool with the given name and arguments."""
        pass

    @abstractmethod
    async def list_connected_apps(self) -> list[dict[str, Any]]:
        """List all apps that the user has connected."""
        pass

    # --- Abstract method for subclass implementation ---

    def _create_app_instance(self, app_name: str) -> BaseApplication:
        """Create an application instance for a given app name."""
        raise NotImplementedError("Subclasses must implement this method")

    # --- Concrete methods for shared tool loading ---

    def _load_tools(self, app_name: str, tool_names: list[str] | None) -> None:
        """Helper method to load and register tools for an app."""
        logger.info(f"Loading tools for app '{app_name}' (tools: {tool_names or 'default'})")
        try:
            if app_name not in self._app_instances:
                self._app_instances[app_name] = self._create_app_instance(app_name)
            app_instance = self._app_instances[app_name]
            self.tool_manager.register_tools_from_app(app_instance, tool_names=tool_names)
            logger.info(f"Successfully registered tools for app: {app_name}")
        except Exception as e:
            logger.error(f"Failed to load tools for app {app_name}: {e}", exc_info=True)

    def _load_tools_from_list(self, tools: list[str]) -> None:
        """Load tools from a list of full tool names (e.g., 'app__tool')."""
        logger.debug(f"Loading tools from list: {tools}")
        tools_by_app: dict[str, list[str]] = {}
        for tool_name in tools:
            app_name, _ = _get_app_and_tool_name(tool_name)
            tools_by_app.setdefault(app_name, []).append(tool_name)

        for app_name, tool_names in tools_by_app.items():
            self._load_tools(app_name, tool_names)

    def _load_tools_from_tool_config(self, tool_config: ToolConfig) -> None:
        """Load tools from a ToolConfig dictionary."""
        logger.debug(f"Loading tools from tool_config: {tool_config}")
        for app_name, tool_names in tool_config.items():
            self._load_tools(app_name, tool_names or None)
