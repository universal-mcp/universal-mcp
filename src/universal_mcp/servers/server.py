from collections.abc import Callable
from typing import Any

import httpx
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from pydantic import ValidationError

from universal_mcp.applications import BaseApplication, app_from_slug
from universal_mcp.config import AppConfig, ServerConfig, StoreConfig
from universal_mcp.exceptions import ConfigurationError, ToolError
from universal_mcp.integrations import AgentRIntegration, integration_from_config
from universal_mcp.stores import BaseStore, store_from_config
from universal_mcp.tools import ToolManager
from universal_mcp.utils.agentr import AgentrClient


class BaseServer(FastMCP):
    """Base server class with common functionality.

    This class provides core server functionality including store setup,
    tool management, and application loading.

    Args:
        config: Server configuration
        **kwargs: Additional keyword arguments passed to FastMCP
    """

    def __init__(self, config: ServerConfig, tool_manager: ToolManager | None = None, **kwargs):
        try:
            super().__init__(config.name, config.description, port=config.port, **kwargs)
            logger.info(f"Initializing server: {config.name} ({config.type}) with store: {config.store}")
            self.config = config
            self._tool_manager = tool_manager or ToolManager(warn_on_duplicate_tools=True)
            ServerConfig.model_validate(config)
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise ConfigurationError(f"Server initialization failed: {str(e)}") from e

    def add_tool(self, tool: Callable) -> None:
        """Add a tool to the server.

        Args:
            tool: Tool to add

        Raises:
            ValueError: If tool is invalid
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
            ValueError: If tool name is invalid or arguments are malformed
        """
        if not name:
            raise ValueError("Tool name is required")
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")

        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        try:
            result = await self._tool_manager.call_tool(name, arguments)
            logger.info(f"Tool '{name}' completed successfully")
            return self._format_tool_result(result)
        except Exception as e:
            logger.error(f"Tool '{name}' failed: {e}", exc_info=True)
            raise ToolError(f"Tool execution failed: {str(e)}") from e


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

        Raises:
            ConfigurationError: If store configuration is invalid
        """
        if not store_config:
            logger.info("No store configuration provided")
            return None

        try:
            store = store_from_config(store_config)
            self.add_tool(store.set)
            self.add_tool(store.delete)
            logger.info(f"Successfully configured store: {store_config.type}")
            return store
        except Exception as e:
            logger.error(f"Failed to setup store: {e}", exc_info=True)
            raise ConfigurationError(f"Store setup failed: {str(e)}") from e

    def _load_app(self, app_config: AppConfig) -> BaseApplication | None:
        """Load a single application with its integration.

        Args:
            app_config: Application configuration

        Returns:
            Configured application instance or None if loading fails
        """
        if not app_config.name:
            logger.error("App configuration missing name")
            return None

        try:
            integration = None
            if app_config.integration:
                try:
                    integration = integration_from_config(app_config.integration, store=self.store)
                    logger.debug(f"Successfully configured integration for {app_config.name}")
                except Exception as e:
                    logger.error(f"Failed to setup integration for {app_config.name}: {e}", exc_info=True)
                    # Continue without integration if it fails

            app = app_from_slug(app_config.name)(integration=integration)
            logger.info(f"Successfully loaded app: {app_config.name}")
            return app
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)
            return None

    def _load_apps(self) -> None:
        """Load all configured applications with graceful degradation."""
        if not self.config.apps:
            logger.warning("No applications configured")
            return

        logger.info(f"Loading {len(self.config.apps)} apps")
        loaded_apps = 0
        failed_apps = []

        for app_config in self.config.apps:
            app = self._load_app(app_config)
            if app:
                try:
                    self._tool_manager.register_tools_from_app(app, app_config.actions)
                    loaded_apps += 1
                    logger.info(f"Successfully registered tools for {app_config.name}")
                except Exception as e:
                    logger.error(f"Failed to register tools for {app_config.name}: {e}", exc_info=True)
                    failed_apps.append(app_config.name)
            else:
                failed_apps.append(app_config.name)

        if failed_apps:
            logger.warning(f"Failed to load {len(failed_apps)} apps: {', '.join(failed_apps)}")

        if loaded_apps == 0:
            logger.error("No apps were successfully loaded")
        else:
            logger.info(f"Successfully loaded {loaded_apps}/{len(self.config.apps)} apps")


class AgentRServer(BaseServer):
    """AgentR API-connected server implementation.

    Args:
        config: Server configuration
        api_key: Optional API key for AgentR authentication. If not provided,
                will attempt to read from AGENTR_API_KEY environment variable.
        max_retries: Maximum number of retries for API calls (default: 3)
        retry_delay: Delay between retries in seconds (default: 1)
        **kwargs: Additional keyword arguments passed to FastMCP
    """

    def __init__(self, config: ServerConfig, api_key: str | None = None, **kwargs):
        self.api_key = api_key or str(config.api_key)
        self.client = AgentrClient(api_key=self.api_key)
        super().__init__(config, **kwargs)
        self.integration = AgentRIntegration(name="agentr", api_key=self.client.api_key)
        self._load_apps()

    def _fetch_apps(self) -> list[AppConfig]:
        """Fetch available apps from AgentR API with retry logic.

        Returns:
            List of application configurations

        Raises:
            httpx.HTTPError: If API request fails after all retries
            ValidationError: If app configuration validation fails
        """
        try:
            apps = self.client.fetch_apps()
            validated_apps = []
            for app in apps:
                try:
                    validated_apps.append(AppConfig.model_validate(app))
                except ValidationError as e:
                    logger.error(f"Failed to validate app config: {e}", exc_info=True)
                    continue
            return validated_apps
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
            app = app_from_slug(app_config.name)(integration=integration)
            logger.info(f"Successfully loaded app: {app_config.name}")
            return app
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)
            return None

    def _load_apps(self) -> None:
        """Load all apps available from AgentR with graceful degradation."""
        try:
            app_configs = self._fetch_apps()
            if not app_configs:
                logger.warning("No apps found from AgentR API")
                return

            loaded_apps = 0
            for app_config in app_configs:
                app = self._load_app(app_config)
                if app:
                    self._tool_manager.register_tools_from_app(app, app_config.actions)
                    loaded_apps += 1

            if loaded_apps == 0:
                logger.error("Failed to load any apps from AgentR")
            else:
                logger.info(f"Successfully loaded {loaded_apps}/{len(app_configs)} apps from AgentR")

        except Exception:
            logger.error("Failed to load apps", exc_info=True)
            # Don't raise the exception to allow server to start with partial functionality
            logger.warning("Server will start with limited functionality due to app loading failures")


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
        if not app_instance:
            raise ValueError("app_instance is required")
        if not config:
            config = ServerConfig(
                type="local",
                name=f"{app_instance.name.title()} MCP Server for Local Development",
                description=f"Minimal MCP server for the local {app_instance.name} application.",
            )
        super().__init__(config, **kwargs)
        self._tool_manager.register_tools_from_app(app_instance)
