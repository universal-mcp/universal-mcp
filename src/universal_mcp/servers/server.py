from collections.abc import Callable
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from universal_mcp.applications.application import BaseApplication
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.config import ServerConfig
from universal_mcp.exceptions import ConfigurationError, ToolError
from universal_mcp.integrations.integration import ApiKeyIntegration, OAuthIntegration
from universal_mcp.stores import store_from_config
from universal_mcp.tools import ToolManager
from universal_mcp.tools.adapters import convert_tool_to_mcp_tool, format_to_mcp_result
from universal_mcp.tools.local_registry import LocalRegistry

# --- Loader Implementations ---


def load_from_local_config(config: ServerConfig, tool_manager: ToolManager) -> None:
    """Load apps and store from local config, register their tools."""
    # Setup store if present
    if config.store:
        try:
            store = store_from_config(config.store)
            tool_manager.add_tool(store.set)
            tool_manager.add_tool(store.delete)
            logger.info(f"Store loaded: {config.store.type}")
        except Exception as e:
            logger.error(f"Failed to setup store: {e}", exc_info=True)
            raise ConfigurationError(f"Store setup failed: {str(e)}") from e

    # Load apps
    if not config.apps:
        logger.warning("No applications configured in local config")
        return

    for app_config in config.apps:
        try:
            integration = None
            if app_config.integration:
                if app_config.integration.type == "api_key":
                    integration = ApiKeyIntegration(config.name, store=store, **app_config.integration.credentials)
                elif app_config.integration.type == "oauth":
                    integration = OAuthIntegration(config.name, store=store, **app_config.integration.credentials)
                else:
                    raise ValueError(f"Unsupported integration type: {app_config.integration.type}")
            app = app_from_slug(app_config.name)(integration=integration)
            tool_manager.register_tools_from_app(app, tool_names=app_config.actions)
            logger.info(f"Loaded app: {app_config.name}")
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)


def load_from_application(app_instance: BaseApplication, tool_manager: ToolManager) -> None:
    """Register all tools from a single application instance."""
    tool_manager.register_tools_from_app(app_instance, tags=["all"])
    logger.info(f"Loaded tools from application: {app_instance.name}")


# --- Server Implementations ---


class BaseServer(FastMCP):
    """Base server for Universal MCP, manages ToolManager and tool invocation."""

    def __init__(self, config: ServerConfig, tool_manager: ToolManager | None = None, **kwargs):
        try:
            super().__init__(config.name, config.description, port=config.port, **kwargs)  # type: ignore
            self.config = config
            self._tool_manager = tool_manager
            self.registry: Any = None
            ServerConfig.model_validate(config)
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise ConfigurationError(f"Server initialization failed: {str(e)}") from e

    @property
    def tool_manager(self) -> ToolManager:
        if self._tool_manager is None:
            self._tool_manager = ToolManager(warn_on_duplicate_tools=True)
        return self._tool_manager

    def add_tool(self, fn: Callable, name: str | None = None, description: str | None = None) -> None:
        self.tool_manager.add_tool(fn, name)

    async def list_tools(self) -> list:  # type: ignore
        tools = self.tool_manager.get_tools()
        return [convert_tool_to_mcp_tool(tool) for tool in tools]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if not name:
            raise ValueError("Tool name is required")
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")
        try:
            # Delegate the call to the registry
            result = await self.registry.call_tool(name, arguments)
            return format_to_mcp_result(result)
        except Exception as e:
            logger.error(f"Tool '{name}' failed: {e}", exc_info=True)
            raise ToolError(f"Tool execution failed: {str(e)}") from e


class LocalServer(BaseServer):
    """Server that loads apps and store from local config."""

    def __init__(self, config: ServerConfig, registry: LocalRegistry | None = None, **kwargs):
        super().__init__(config, **kwargs)
        self.registry = registry or LocalRegistry()
        self._tools_loaded = False
        self._load_tools_from_config()

    def _load_tools_from_config(self):
        """Load tools from the server configuration into the registry."""
        if not self.config.apps:
            logger.warning("No applications configured in server config; no tools to load.")
            return

        logger.info(f"Loading tools from {len(self.config.apps)} app(s) specified in server config...")
        # Create a tool config dictionary from the server config
        tool_config = {app.name: app.actions for app in self.config.apps}
        self.registry._load_tools_from_tool_config(tool_config)
        self._tools_loaded = True
        logger.info("Finished loading tools from server config.")

    @property
    def tool_manager(self) -> ToolManager:
        return self.registry.tool_manager


class SingleMCPServer(BaseServer):
    """Server for a single, pre-configured application."""

    def __init__(
        self,
        app_instance: BaseApplication,
        config: ServerConfig | None = None,
        **kwargs,
    ):
        config = config or ServerConfig(
            type="local",
            name=f"{app_instance.name.title()} MCP Server for Local Development",
            description=f"Minimal MCP server for the local {app_instance.name} application.",
        )
        super().__init__(config, **kwargs)
        self.app_instance = app_instance
        self._tools_loaded = False

    @property
    def tool_manager(self) -> ToolManager:
        if self._tool_manager is None:
            self._tool_manager = ToolManager(warn_on_duplicate_tools=True)
        if not self._tools_loaded:
            load_from_application(self.app_instance, self._tool_manager)
            self._tools_loaded = True
        return self._tool_manager
