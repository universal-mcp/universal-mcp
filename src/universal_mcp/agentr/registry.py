import base64
from typing import Any

from loguru import logger

from universal_mcp.agentr.client import AgentrClient
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.exceptions import ToolError
from universal_mcp.tools.manager import ToolManager, _get_app_and_tool_name
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from .integration import AgentrIntegration

MARKDOWN_INSTRUCTIONS = """Always render the URL in markdown format for images and media files. Here are examples:
The url is provided in the response as "signed_url".
For images:
- Use markdown image syntax: ![alt text](url)
- Example: ![Generated sunset image](https://example.com/image.png)
- Always include descriptive alt text that explains what the image shows

For audio files:
- Use markdown link syntax with audio description: [🔊 Audio file description](url)
- Example: [🔊 Generated speech audio](https://example.com/audio.mp3)

For other media:
- Use descriptive link text: [📄 File description](url)
- Example: [📄 Generated document](https://example.com/document.pdf)

Always make the links clickable and include relevant context about what the user will see or hear when they access the URL."""


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
            all_apps = [{"id": app["id"], "name": app["name"], "description": app["description"]} for app in all_apps]
            # logger.debug(f"All apps: {all_apps}")
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
            if isinstance(tools, dict):
                logger.info("Loading tools from tool config")
                self._load_tools_from_tool_config(tools, self.tool_manager)
            else:
                logger.info("Loading tools from list")
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
        for app_name, tool_names in tool_config.items():
            self._load_tools(app_name, tool_names, tool_manager)

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        data = await self.tool_manager.call_tool(tool_name, tool_args)
        logger.debug(f"Tool {tool_name} called with args {tool_args} and returned {data}")
        if isinstance(data, dict):
            type_ = data.get("type")
            if type_ == "image" or type_ == "audio":
                # Special handling for images and audio
                base64_data = data.get("data")
                mime_type = data.get("mime_type")
                file_name = data.get("file_name")
                if not mime_type or not file_name:
                    raise ToolError("Mime type or file name is missing")
                bytes_data = base64.b64decode(base64_data)
                response = self.client._upload_file(file_name, mime_type, bytes_data)
                # Hard code instructions for llm
                response = {**response, "instructions": MARKDOWN_INSTRUCTIONS}
                return response
        return data

    async def list_connected_apps(self) -> list[str]:
        """List all apps that the user has connected."""
        return self.client.list_my_connections()
