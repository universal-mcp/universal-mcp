import base64
import os
from typing import Any

from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.exceptions import ToolError, ToolNotFoundError
from universal_mcp.integrations.integration import IntegrationFactory
from universal_mcp.tools.adapters import convert_tools
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat


class LocalRegistry(ToolRegistry):
    """A local implementation of the tool registry."""

    def __init__(self, output_dir: str = "output"):
        """Initialize the LocalRegistry."""
        super().__init__()
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        logger.debug(f"Local output directory set to: {self.output_dir}")

    def _create_app_instance(self, app_name: str) -> BaseApplication:
        """Create a local app instance with a default integration."""
        app = app_from_slug(app_name)
        integration = IntegrationFactory.create(app_name)
        return app(integration=integration)

    async def list_all_apps(self) -> list[dict[str, Any]]:
        """Not implemented for LocalRegistry."""
        raise NotImplementedError("LocalRegistry does not support listing all apps.")

    async def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Not implemented for LocalRegistry."""
        raise NotImplementedError("LocalRegistry does not support getting app details.")

    async def search_apps(
        self,
        query: str,
        limit: int = 2,
    ) -> list[dict[str, Any]]:
        """Not implemented for LocalRegistry."""
        raise NotImplementedError("LocalRegistry does not support searching apps.")

    async def list_tools(
        self,
        app_id: str,
    ) -> list[dict[str, Any]]:
        """Not implemented for LocalRegistry."""
        raise NotImplementedError("LocalRegistry does not support listing tools.")

    async def search_tools(
        self,
        query: str,
        limit: int = 2,
        app_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Not implemented for LocalRegistry."""
        raise NotImplementedError("LocalRegistry does not support searching tools.")

    async def export_tools(
        self,
        tools: list[str] | ToolConfig,
        format: ToolFormat,
    ) -> list[Any]:
        """Export given tools to the required format."""
        self.tool_manager.clear_tools()
        logger.info(f"Exporting tools to {format.value} format")
        if isinstance(tools, dict):
            self._load_tools_from_tool_config(tools)
        else:
            self._load_tools_from_list(tools)

        loaded_tools = self.tool_manager.get_tools()
        exported = convert_tools(loaded_tools, format)
        logger.info(f"Exported {len(exported)} tools")
        return exported

    def _handle_file_output(self, data: Any) -> Any:
        """Handle special file outputs by writing them to the filesystem."""
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

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Call a tool and handle its output."""
        tool = self.tool_manager.get_tool(tool_name)
        if not tool:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found.")

        result = await tool.run(tool_args)
        return self._handle_file_output(result)

    async def list_connected_apps(self) -> list[dict[str, Any]]:
        """Not implemented for LocalRegistry."""
        raise NotImplementedError("LocalRegistry does not support listing connected apps.")
