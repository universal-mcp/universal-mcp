import base64
import os
from typing import Any

from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.exceptions import ToolError, ToolNotFoundError
from universal_mcp.integrations.integration import IntegrationFactory
from universal_mcp.tools.adapters import convert_tools
from universal_mcp.tools.manager import ToolManager
from universal_mcp.tools.utils import list_to_tool_config
from universal_mcp.types import ToolConfig, ToolFormat


class LocalRegistry:
    """A local implementation of the tool registry."""

    def __init__(self, output_dir: str = "output"):
        """Initialize the LocalRegistry."""
        self._app_instances = {}
        self.tool_manager = ToolManager()
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        logger.debug(f"LocalRegistry initialized. Output directory: {self.output_dir}")

    def _create_app_instance(self, app_name: str) -> BaseApplication:
        """Create a local app instance with a default integration."""
        app = app_from_slug(app_name)
        integration = IntegrationFactory.create(app_name)
        return app(integration=integration)

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
