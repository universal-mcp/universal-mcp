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
from universal_mcp.tools.adapters import ToolFormat, format_to_mcp_result
from universal_mcp.utils.agentr import AgentrClient


class BaseServer(FastMCP):
    """Provides foundational functionality for Universal MCP server implementations.

    This class extends `mcp.server.fastmcp.FastMCP` and serves as the
    base for more specialized server types like `LocalServer` and `AgentRServer`.
    It handles common tasks such as initializing with a `ServerConfig`,
    managing a `ToolManager` for adding, listing, and calling tools,
    and basic error handling for server and tool operations.

    Attributes:
        config (ServerConfig): The server's configuration object.
        _tool_manager (ToolManager): Manages the registration and execution
                                   of tools available on this server.
    """

    def __init__(self, config: ServerConfig, tool_manager: ToolManager | None = None, **kwargs):
        """Initializes the BaseServer.

        Args:
            config (ServerConfig): The configuration object for the server.
            tool_manager (ToolManager | None, optional): An instance of
                `ToolManager`. If None, a new one is created.
                Defaults to None.
            **kwargs: Additional keyword arguments passed to the `FastMCP`
                      parent class (e.g., port, host).

        Raises:
            ConfigurationError: If server initialization fails due to invalid
                                configuration or other issues.
        """
        try:
            super().__init__(config.name, config.description, port=config.port, **kwargs) # type: ignore
            logger.info(f"Initializing server: {config.name} ({config.type}) with store: {config.store}")
            self.config = config
            self._tool_manager = tool_manager or ToolManager(warn_on_duplicate_tools=True)
            # Validate config after setting attributes to ensure proper initialization
            ServerConfig.model_validate(config)
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise ConfigurationError(f"Server initialization failed: {str(e)}") from e

    def add_tool(self, tool: Callable) -> None:
        """Adds a new tool to the server's tool manager.

        Args:
            tool (Callable): The callable object representing the tool to be added.
                             This tool should conform to the expected signature
                             and metadata conventions for MCP tools.

        Raises:
            ValueError: If the provided tool is invalid or cannot be registered.
        """
        self._tool_manager.add_tool(tool)

    async def list_tools(self) -> list: # type: ignore
        """Lists all tools registered with the server in MCP format.

        Returns:
            list: A list of tool definitions, formatted according to the
                  MCP specification.
        """
        return self._tool_manager.list_tools(format=ToolFormat.MCP)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Calls a registered tool by name with the provided arguments.

        Handles tool execution and wraps the outcome (success or error)
        in a list of MCP `TextContent` objects.

        Args:
            name (str): The name of the tool to call.
            arguments (dict[str, Any]): A dictionary of arguments for the tool.

        Returns:
            list[TextContent]: A list of `TextContent` objects representing the
                               output of the tool. If an error occurs, this list
                               may contain error information.

        Raises:
            ToolError: If tool execution fails for reasons other than invalid
                       name or arguments (which raise ValueError).
            ValueError: If the tool name is empty or arguments are not a dictionary.
        """
        if not name:
            raise ValueError("Tool name is required")
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")

        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        try:
            result = await self._tool_manager.call_tool(name, arguments)
            logger.info(f"Tool '{name}' completed successfully")
            return format_to_mcp_result(result)
        except Exception as e:
            logger.error(f"Tool '{name}' failed: {e}", exc_info=True)
            raise ToolError(f"Tool execution failed: {str(e)}") from e


class LocalServer(BaseServer):
    """MCP server for local development, loading apps from local configuration.

    This server type reads its application and integration settings from the
    provided `ServerConfig`. It is typically used for running and testing
    MCP applications in a local environment. It handles setting up a
    credential store (e.g., memory, keyring, environment) and dynamically
    loading application modules by their slugs.

    Attributes:
        store (BaseStore | None): The configured credential store instance.
                                None if no store is configured.
    """

    def __init__(self, config: ServerConfig, **kwargs):
        """Initializes the LocalServer.

        Args:
            config (ServerConfig): The server configuration object, which includes
                                 settings for applications and the default store.
            **kwargs: Additional keyword arguments passed to the `BaseServer`.
        """
        super().__init__(config, **kwargs)
        self.store = self._setup_store(config.store)
        self._load_apps()

    def _setup_store(self, store_config: StoreConfig | None) -> BaseStore | None:
        """Initializes the credential store based on the server configuration.

        If a `store_config` is provided, this method creates and configures
        the specified store type (e.g., memory, keyring). It also registers
        the store's `set` and `delete` methods as tools with the server.

        Args:
            store_config (StoreConfig | None): The configuration for the store.

        Returns:
            BaseStore | None: The initialized store instance, or None if no
                              `store_config` was provided.

        Raises:
            ConfigurationError: If the store setup fails due to invalid
                                configuration or other issues.
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
        """Loads and configures a single application based on `AppConfig`.

        This method instantiates an application module identified by `app_config.name`
        (slug). It also sets up the application's integration (for authentication)
        based on `app_config.integration`, using the server's configured store
        if the integration requires one.

        Args:
            app_config (AppConfig): The configuration for the application to load.

        Returns:
            BaseApplication | None: The initialized application instance if loading
                                    and configuration are successful, otherwise None.
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
        """Loads all applications defined in the server's configuration.

        Iterates through the `AppConfig` entries in `self.config.apps`.
        For each entry, it attempts to load the application and its integration
        using `_load_app`. If successful, the application's tools (actions)
        are registered with the server's `ToolManager`.

        This method handles errors gracefully for individual app loading,
        allowing the server to start even if some applications fail to load.
        """
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
    """MCP server that connects to the AgentR platform to manage applications.

    This server type dynamically fetches its list of available applications
    and their configurations from the AgentR API. It primarily uses
    `AgentRIntegration` for handling authentication and authorization,
    delegating these tasks to the AgentR platform. An AgentR API key is
    required for its operation.

    Attributes:
        api_key (str | None): The AgentR API key used for authentication.
        client (AgentrClient): The client instance for interacting with the
                             AgentR API.
    """

    def __init__(self, config: ServerConfig, **kwargs):
        """Initializes the AgentRServer.

        Args:
            config (ServerConfig): The server configuration object. The `api_key`
                                 and `base_url` from this config are used to
                                 initialize the `AgentrClient`.
            **kwargs: Additional keyword arguments passed to the `BaseServer`.

        Raises:
            ValueError: If the `api_key` is not provided in the configuration.
        """
        super().__init__(config, **kwargs)
        self.api_key = config.api_key.get_secret_value() if config.api_key else None
        if not self.api_key:
            raise ValueError("API key is required for AgentR server")
        logger.info(f"Initializing AgentR server with API key: {self.api_key} and base URL: {config.base_url}") # type: ignore
        self.client = AgentrClient(api_key=self.api_key, base_url=config.base_url) # type: ignore
        self._load_apps()

    def _fetch_apps(self) -> list[AppConfig]:
        """Fetches available application configurations from the AgentR API.

        This method uses the `AgentrClient` to retrieve the list of applications
        associated with the configured API key. It includes retry logic for
        transient network issues.

        Returns:
            list[AppConfig]: A list of `AppConfig` objects parsed from the
                             AgentR API response.

        Raises:
            httpx.HTTPStatusError: If the API request to AgentR fails definitively
                                 (e.g., 4xx or 5xx errors after retries).
            ValidationError: If the application configuration data received from
                             AgentR fails Pydantic validation.
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
        """Loads a single application using AgentRIntegration.

        For each `AppConfig` fetched from AgentR, this method instantiates the
        application module (identified by `app_config.name`) and configures it
        with an `AgentRIntegration`. This integration will use the server's
        AgentR API key and base URL for its operations.

        Args:
            app_config (AppConfig): The configuration for the application to load.

        Returns:
            BaseApplication | None: The initialized application instance if loading
                                    is successful, otherwise None.
        """
        try:
            integration = (
                AgentRIntegration(name=app_config.integration.name, api_key=self.api_key, base_url=self.config.base_url) # type: ignore
                if app_config.integration
                else None
            )
            app = app_from_slug(app_config.name)(integration=integration) # type: ignore
            logger.info(f"Successfully loaded app: {app_config.name}")
            return app
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)
            return None

    def _load_apps(self) -> None:
        """Fetches all application configurations from AgentR and registers their tools.

        This method first calls `_fetch_apps` to get the list of applications
        from the AgentR platform. Then, for each application, it uses `_load_app`
        to instantiate it with `AgentRIntegration`. If successful, the application's
        tools are registered with the server's `ToolManager`.

        Handles errors gracefully, allowing the server to start even if some
        applications fail to load or if fetching apps from AgentR fails.
        """
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

        except Exception as e:
            logger.error("Failed to load apps", exc_info=True)
            # Don't raise the exception to allow server to start with partial functionality
            logger.warning(f"Server will start with limited functionality due to app loading failures: {e}")


class SingleMCPServer(BaseServer):
    """Minimal MCP server for hosting a single, pre-configured application.

    This server is designed for scenarios where you need to quickly expose
    the tools of a single, already instantiated and configured
    `BaseApplication` object. It does not handle complex app loading or
    integration setups itself; these are expected to be done on the
    `app_instance` before it's passed to this server.

    It's useful for testing, simple demos, or embedding a specific set of
    tools without the overhead of more complex server configurations.
    If no `ServerConfig` is provided, a default one is generated based
    on the application's name.
    """

    def __init__(
        self,
        app_instance: BaseApplication,
        config: ServerConfig | None = None,
        **kwargs,
    ):
        """Initializes the SingleMCPServer.

        Args:
            app_instance (BaseApplication): The fully configured application
                instance whose tools will be exposed by this server.
            config (ServerConfig | None, optional): A server configuration.
                If None, a default configuration is generated using the
                name of the `app_instance`. Defaults to None.
            **kwargs: Additional keyword arguments passed to `BaseServer`.

        Raises:
            ValueError: If `app_instance` is None.
        """
        if not app_instance:
            raise ValueError("app_instance is required for SingleMCPServer")

        config = config or ServerConfig(
            type="local", # type: ignore
            name=f"{app_instance.name.title()} MCP Server for Local Development", # type: ignore
            description=f"Minimal MCP server for the local {app_instance.name} application.", # type: ignore
        )
        super().__init__(config, **kwargs)
        self._tool_manager.register_tools_from_app(app_instance, tags="all")
