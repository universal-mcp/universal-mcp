from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.tools.adapters import convert_tools
from universal_mcp.tools.manager import ToolManager
from universal_mcp.tools.utils import list_to_tool_config, tool_config_to_list
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

    def _load_tools_from_app(self, app_name: str, tool_names: list[str] | None) -> None:
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
        tool_config = list_to_tool_config(tools)
        for app_name, tool_names in tool_config.items():
            self._load_tools_from_app(app_name, tool_names or None)

    def _load_tools_from_tool_config(self, tool_config: ToolConfig) -> None:
        """Load tools from a ToolConfig dictionary."""
        logger.debug(f"Loading tools from tool_config: {tool_config}")
        for app_name, tool_names in tool_config.items():
            self._load_tools_from_app(app_name, tool_names or None)

    # --- Abstract method for subclass implementation ---

    def _create_app_instance(self, app_name: str) -> BaseApplication:
        """Create an application instance for a given app name."""
        raise NotImplementedError("Subclasses must implement this method")

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

    async def load_tools(self, tools: list[str] | ToolConfig | None = None):
        """Load the tools to be used"""
        if isinstance(tools, list):
            self._load_tools_from_list(tools)
        elif isinstance(tools, dict):
            self._load_tools_from_tool_config(tools)
        else:
            raise ValueError(f"Invalid tools type: {type(tools)}. Expected list or ToolConfig.")
        return self.tool_manager.get_tools()

    async def export_tools(
        self, tools: list[str] | ToolConfig | None = None, format: ToolFormat = ToolFormat.NATIVE
    ) -> list[Any]:
        """Export the loaded tools as in required format"""
        if tools is not None:
            # Load the tools if they are not already loaded
            await self.load_tools(tools)
        tools_list = tool_config_to_list(tools) if isinstance(tools, dict) else tools
        loaded_tools = self.tool_manager.get_tools(tool_names=tools_list)
        exported_tools = convert_tools(loaded_tools, format)
        logger.info(f"Exported {len(exported_tools)} tools to {format.value} format")
        return exported_tools if isinstance(exported_tools, list) else [exported_tools]

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Call a tool with the given name and arguments."""
        result = await self.tool_manager.get_tool(tool_name)
        return await result.run(tool_args)

    @abstractmethod
    async def list_connected_apps(self) -> list[dict[str, Any]]:
        """List all apps that the user has connected."""
        pass
