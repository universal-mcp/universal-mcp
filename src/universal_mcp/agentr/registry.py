from typing import Any

from loguru import logger

from universal_mcp.agentr.client import AgentrClient
from universal_mcp.applications import app_from_slug
from universal_mcp.tools.manager import ToolManager, _get_app_and_tool_name
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from .integration import AgentrIntegration


class AgentrRegistry(ToolRegistry):
    """Platform manager implementation for AgentR platform."""

    def __init__(self, client: AgentrClient | None = None, **kwargs):
        """Initialize the AgentR platform manager."""

        self.client = client or AgentrClient(**kwargs)
        self.tool_manager = ToolManager()
        logger.debug("AgentrRegistry initialized successfully")

    async def list_all_apps(self) -> list[dict[str, Any]]:
        """Get list of available apps from AgentR.

        Returns:
            List of app dictionaries with id, name, description, and available fields
        """
        if self.client is None:
            raise ValueError("Client is not initialized")
        try:
            all_apps = self.client.list_all_apps()
            return all_apps
        except Exception as e:
            logger.error(f"Error fetching apps from AgentR: {e}")
            return []

    async def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app from AgentR.

        Args:
            app_id: The ID of the app to get details for

        Returns:
            Dictionary containing app details
        """
        try:
            app_info = self.client.get_app_details(app_id)
            return app_info
        except Exception as e:
            logger.error(f"Error getting details for app {app_id}: {e}")
            return {}

    async def search_apps(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for apps by a query.

        Args:
            query: The query to search for
            limit: The number of apps to return

        Returns:
            List of app dictionaries matching the query
        """
        try:
            apps = self.client.search_all_apps(query, limit)
            return apps
        except Exception as e:
            logger.error(f"Error searching apps from AgentR: {e}")
            return []

    async def list_tools(
        self,
        app_id: str,
    ) -> list[dict[str, Any]]:
        """List all tools available on the platform, filter by app_id.

        Args:
            app_id: The ID of the app to list tools for

        Returns:
            List of tool dictionaries for the specified app
        """
        try:
            all_tools = self.client.list_all_tools(app_id=app_id)
            return all_tools
        except Exception as e:
            logger.error(f"Error listing tools for app {app_id}: {e}")
            return []

    async def search_tools(
        self,
        query: str,
        limit: int = 2,
        app_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for tools by a query.

        Args:
            query: The query to search for
            limit: The number of tools to return
            app_id: The ID of the app to list tools for
        Returns:
            List of tool dictionaries matching the query
        """
        try:
            tools = self.client.search_all_tools(query, limit, app_id)
            return tools
        except Exception as e:
            logger.error(f"Error searching tools from AgentR: {e}")
            return []

    async def export_tools(
        self,
        tools: list[str] | ToolConfig,
        format: ToolFormat,
    ) -> str:
        """Export given tools to required format.

        Args:
            tools: List of tool identifiers to export
            format: The format to export tools to (native, mcp, langchain, openai)

        Returns:
            String representation of tools in the specified format
        """
        try:
            # Clear tools from tool manager before loading new tools
            self.tool_manager.clear_tools()
            if isinstance(tools, ToolConfig):
                print("Loading tools from tool config")
                self._load_tools_from_tool_config(tools, self.tool_manager)
            else:
                print("Loading tools from list")
                self._load_agentr_tools_from_list(tools, self.tool_manager)
            loaded_tools = self.tool_manager.list_tools(format=format)
            logger.info(f"Exporting {len(loaded_tools)} tools to {format} format")
            return loaded_tools
        except Exception as e:
            logger.error(f"Error exporting tools: {e}")
            return ""

    def _load_tools(self, app_name: str, tool_names: list[str], tool_manager: ToolManager) -> None:
        """Helper method to load and register tools for an app."""
        app = app_from_slug(app_name)
        integration = AgentrIntegration(name=app_name, client=self.client)
        app_instance = app(integration=integration)
        tool_manager.register_tools_from_app(app_instance, tool_names=tool_names)

    def _load_agentr_tools_from_list(self, tools: list[str], tool_manager: ToolManager) -> None:
        """Load tools from AgentR and register them as tools.

        Args:
            tools: The list of tools to load (prefixed with app name)
            tool_manager: The tool manager to register tools with
        """
        logger.info(f"Loading all tools: {tools}")
        tools_by_app = {}
        for tool_name in tools:
            app_name, _ = _get_app_and_tool_name(tool_name)
            tools_by_app.setdefault(app_name, []).append(tool_name)

        for app_name, tool_names in tools_by_app.items():
            self._load_tools(app_name, tool_names, tool_manager)

    def _load_tools_from_tool_config(self, tool_config: ToolConfig, tool_manager: ToolManager) -> None:
        """Load tools from ToolConfig and register them as tools.

        Args:
            tool_config: The tool configuration containing app names and tools
            tool_manager: The tool manager to register tools with
        """
        for app_name, tool_data in tool_config.agentrServers.items():
            self._load_tools(app_name, tool_data.tools, tool_manager)

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        return await self.tool_manager.call_tool(tool_name, tool_args)
