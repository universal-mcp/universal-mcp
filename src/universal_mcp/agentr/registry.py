from loguru import logger

from universal_mcp.agentr.client import AgentrClient
from universal_mcp.applications import app_from_slug
from universal_mcp.tools.manager import ToolManager, _get_app_and_tool_name
from universal_mcp.tools.registry import ToolRegistry

from .integration import AgentrIntegration


class AgentrRegistry(ToolRegistry):
    """Platform manager implementation for AgentR platform."""

    def __init__(self, client: AgentrClient | None = None, **kwargs):
        """Initialize the AgentR platform manager."""

        self.client = client or AgentrClient(**kwargs)
        logger.debug("AgentrRegistry initialized successfully")

    def list_apps(self) -> list[dict[str, str]]:
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

    def get_app_details(self, app_id: str) -> dict[str, str]:
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

    def load_tools(self, tools: list[str] | None, tool_manager: ToolManager) -> None:
        """Load tools from AgentR and register them as tools.

        Args:
            tools: The list of tools to load ( prefixed with app name )
            tool_manager: The tool manager to register tools with
        """
        if not tools:
            return
        logger.info(f"Loading all actions for app: {tools}")
        # Group all tools by app_name, tools
        tools_by_app = {}
        for tool_name in tools:
            app_name, _ = _get_app_and_tool_name(tool_name)
            if app_name not in tools_by_app:
                tools_by_app[app_name] = []
            tools_by_app[app_name].append(tool_name)

        for app_name, tool_names in tools_by_app.items():
            app = app_from_slug(app_name)
            integration = AgentrIntegration(name=app_name)
            # TODO: Import with name param, some apps are written incorrectly and hence passing name fails
            app_instance = app(integration=integration)
            tool_manager.register_tools_from_app(app_instance, tool_names=tool_names)
        return

    def search_tools(self, query: str, limit: int = 10) -> list[str]:
        """Search for tools in AgentR.

        Args:
            query: The query to search for

        Returns:
            List of tool names
        """
        return self.client.search_all_tools(query, limit)
