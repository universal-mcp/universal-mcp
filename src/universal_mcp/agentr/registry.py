import inspect
import base64
from typing import Any

from loguru import logger

from universal_mcp.agentr.client import AgentrClient
from universal_mcp.applications.application import BaseApplication
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.exceptions import ToolError, ToolNotFoundError
from universal_mcp.tools.adapters import convert_tools
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
        super().__init__()
        self.client = client or AgentrClient(**kwargs)

    def _create_app_instance(self, app_name: str) -> BaseApplication:
        """Create an app instance with an AgentrIntegration."""
        app = app_from_slug(app_name)
        integration = AgentrIntegration(name=app_name, client=self.client)
        return app(integration=integration)

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
            app_info = self.client.get_app_details(app_id=app_id)
            return app_info
        except Exception as e:
            logger.error(f"Error getting details for app {app_id}: {e}")
            return {}

    async def search_apps(
        self,
        query: str,
        limit: int = 10,
        distance_threshold: float = 0.6,
    ) -> list[dict[str, Any]]:
        """Search for apps by a query.

        Args:
            query: The query to search for
            limit: The number of apps to return

        Returns:
            List of app dictionaries matching the query
        """
        try:
            apps = self.client.search_all_apps(query=query, limit=limit, distance_threshold=distance_threshold)
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
        distance_threshold: float = 0.6,
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
            tools = self.client.search_all_tools(
                query=query, limit=limit, app_id=app_id, distance_threshold=distance_threshold
            )
            return tools
        except Exception as e:
            logger.error(f"Error searching tools from AgentR: {e}")
            return []

    async def export_tools(
        self,
        tools: list[str] | ToolConfig,
        format: ToolFormat,
    ) -> list[Any]:
        """Export given tools to required format.

        Args:
            tools: List of tool identifiers to export
            format: The format to export tools to (native, mcp, langchain, openai)

        Returns:
            List of tools in the specified format
        """
        from langchain_core.tools import StructuredTool

        try:
            logger.info(f"Exporting tools to {format.value} format")
            if isinstance(tools, dict):
                self._load_tools_from_tool_config(tools)
            else:
                self._load_tools_from_list(tools)

            loaded_tools = self.tool_manager.get_tools()

            if format != ToolFormat.LANGCHAIN:
                return convert_tools(loaded_tools, format)

            logger.info(f"Exporting {len(loaded_tools)} tools to LangChain format with special handling")

            langchain_tools = []
            for tool in loaded_tools:
                full_docstring = inspect.getdoc(tool.fn)

                def create_coroutine(t):
                    async def call_tool_wrapper(**arguments: dict[str, Any]):
                        logger.debug(
                            f"Executing registry-wrapped LangChain tool '{t.name}' with arguments: {arguments}"
                        )
                        return await self.call_tool(t.name, arguments)

                    return call_tool_wrapper

                langchain_tool = StructuredTool(
                    name=tool.name,
                    description=full_docstring or tool.description or "",
                    coroutine=create_coroutine(tool),
                    response_format="content",
                    args_schema=tool.parameters,
                )
                langchain_tools.append(langchain_tool)

            return langchain_tools

        except Exception as e:
            logger.error(f"Error exporting tools: {e}")
            return []

    def _handle_special_output(self, data: Any) -> Any:
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

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        logger.debug(f"Calling tool: {tool_name} with arguments: {tool_args}")
        tool = self.tool_manager.get_tool(tool_name)
        if not tool:
            logger.error(f"Unknown tool: {tool_name}")
            raise ToolNotFoundError(f"Unknown tool: {tool_name}")
        try:
            data = await tool.run(tool_args)
            logger.debug(f"Tool {tool_name} called with args {tool_args} and returned {data}")
            return self._handle_special_output(data)
        except Exception as e:
            raise e

    async def list_connected_apps(self) -> list[dict[str, Any]]:
        """List all apps that the user has connected."""
        return self.client.list_my_connections()

    async def authorise_app(self, app_id: str) -> str:
        """Authorise an app to connect to the user's account.

        Args:
            app_id: The ID of the app to authorise

        Returns:
            String containing authorisation url
        """
        url = self.client.get_authorization_url(app_id=app_id)
        return url
