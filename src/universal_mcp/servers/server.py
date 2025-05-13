from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import httpx
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from universal_mcp.applications import BaseApplication, app_from_slug
from universal_mcp.config import AppConfig, ServerConfig, StoreConfig
from universal_mcp.integrations import AgentRIntegration, integration_from_config
from universal_mcp.stores import BaseStore, store_from_config
from universal_mcp.tools import ToolManager
from universal_mcp.utils.agentr import AgentrClient


class BaseServer(FastMCP, ABC):
    """Base server class with common functionality.

    This class provides core server functionality including store setup,
    tool management, and application loading.

    Args:
        config: Server configuration
        **kwargs: Additional keyword arguments passed to FastMCP
    """

    def __init__(self, config: ServerConfig, **kwargs):
        super().__init__(config.name, config.description, port=config.port, **kwargs)
        logger.info(f"Initializing server: {config.name} ({config.type}) with store: {config.store}")

        self.config = config  # Store config at base level for consistency
        self._tool_manager = ToolManager(warn_on_duplicate_tools=True)

    @abstractmethod
    def _load_apps(self) -> None:
        """Load and register applications."""
        pass

    def add_tool(self, tool: Callable) -> None:
        """Add a tool to the server.

        Args:
            tool: Tool to add
        """
        self._tool_manager.add_tool(tool)

    async def list_tools(self) -> list[dict]:
        """List all available tools in MCP format.

        Returns:
            List of tool definitions
        """
        return self._tool_manager.list_tools(format="mcp")

    def _format_tool_result(self, result: Any) -> list[TextContent]:
        """Format tool result into TextContent list.

        Args:
            result: Raw tool result

        Returns:
            List of TextContent objects
        """
        if isinstance(result, str):
            return [TextContent(type="text", text=result)]
        elif isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
            return result
        else:
            logger.warning(f"Tool returned unexpected type: {type(result)}. Wrapping in TextContent.")
            return [TextContent(type="text", text=str(result))]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Call a tool with comprehensive error handling.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            List of TextContent results

        Raises:
            ToolError: If tool execution fails
        """
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        result = await self._tool_manager.call_tool(name, arguments)
        logger.info(f"Tool '{name}' completed successfully")
        return self._format_tool_result(result)


class LocalServer(BaseServer):
    """Local development server implementation.

    Args:
        config: Server configuration
        **kwargs: Additional keyword arguments passed to FastMCP
    """

    def __init__(self, config: ServerConfig, **kwargs):
        super().__init__(config, **kwargs)
        self.store = self._setup_store(config.store)
        self._load_apps()

    def _setup_store(self, store_config: StoreConfig | None) -> BaseStore | None:
        """Setup and configure the store.

        Args:
            store_config: Store configuration

        Returns:
            Configured store instance or None if no config provided
        """
        if not store_config:
            return None

        store = store_from_config(store_config)
        self.add_tool(store.set)
        self.add_tool(store.delete)
        return store

    def _load_app(self, app_config: AppConfig) -> BaseApplication | None:
        """Load a single application with its integration.

        Args:
            app_config: Application configuration

        Returns:
            Configured application instance or None if loading fails
        """
        try:
            integration = (
                integration_from_config(app_config.integration, store=self.store) if app_config.integration else None
            )
            return app_from_slug(app_config.name)(integration=integration)
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)
            return None

    def _load_apps(self) -> None:
        """Load all configured applications."""
        logger.info(f"Loading apps: {self.config.apps}")
        for app_config in self.config.apps:
            app = self._load_app(app_config)
            if app:
                self._tool_manager.register_tools_from_app(app, app_config.actions)


class AgentRServer(BaseServer):
    """AgentR API-connected server implementation.

    Args:
        config: Server configuration
        api_key: Optional API key for AgentR authentication. If not provided,
                will attempt to read from AGENTR_API_KEY environment variable.
        **kwargs: Additional keyword arguments passed to FastMCP
    """

    def __init__(self, config: ServerConfig, api_key: str | None = None, **kwargs):
        self.client = AgentrClient(api_key=api_key)
        super().__init__(config, **kwargs)
        self.integration = AgentRIntegration(name="agentr", api_key=self.client.api_key)
        self._load_apps()

    def _fetch_apps(self) -> list[AppConfig]:
        """Fetch available apps from AgentR API.

        Returns:
            List of application configurations

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            apps = self.client.fetch_apps()
            return [AppConfig.model_validate(app) for app in apps]
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch apps from AgentR: {e}", exc_info=True)
            raise

    def _load_app(self, app_config: AppConfig) -> BaseApplication | None:
        """Load a single application with AgentR integration.

        Args:
            app_config: Application configuration

        Returns:
            Configured application instance or None if loading fails
        """
        try:
            integration = (
                AgentRIntegration(name=app_config.integration.name, api_key=self.client.api_key)
                if app_config.integration
                else None
            )
            return app_from_slug(app_config.name)(integration=integration)
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)
            return None

    def _load_apps(self) -> None:
        """Load all apps available from AgentR."""
        try:
            for app_config in self._fetch_apps():
                app = self._load_app(app_config)
                if app:
                    self._tool_manager.register_tools_from_app(app, app_config.actions)
        except Exception:
            logger.error("Failed to load apps", exc_info=True)
            raise


class SingleMCPServer(BaseServer):
    """
    Minimal server implementation hosting a single BaseApplication instance.

    This server type is intended for development and testing of a single
    application's tools. It does not manage integrations or stores internally
    beyond initializing the ToolManager and exposing the provided application's tools.
    The application instance passed to the constructor should already be
    configured with its appropriate integration (if required).

    Args:
        config: Server configuration (used for name, description, etc. but ignores 'apps')
        app_instance: The single BaseApplication instance to host and expose its tools.
                      Can be None, in which case no tools will be registered.
        **kwargs: Additional keyword arguments passed to FastMCP parent class.
    """

    def __init__(
        self,
        app_instance: BaseApplication,
        config: ServerConfig | None = None,
        **kwargs,
    ):
        if not config:
            config = ServerConfig(
                type="local",
                name=f"{app_instance.name.title()} MCP Server for Local Development"
                if app_instance
                else "Unnamed MCP Server",
                description=f"Minimal MCP server for the local {app_instance.name} application."
                if app_instance
                else "Minimal MCP server with no application loaded.",
            )
        super().__init__(config, **kwargs)

        self.app_instance = app_instance
        self._load_apps()

    def _load_apps(self) -> None:
        """Registers tools from the single provided application instance."""
        if not self.app_instance:
            logger.warning("No app_instance provided. No tools registered.")
            return

        tool_functions = self.app_instance.list_tools()
        for tool_func in tool_functions:
            self._tool_manager.add_tool(tool_func)
