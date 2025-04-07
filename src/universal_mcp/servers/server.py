import os
from abc import ABC, abstractmethod
from typing import Any

import httpx
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import TextContent

from universal_mcp.applications import app_from_name
from universal_mcp.config import AppConfig, IntegrationConfig, StoreConfig
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import AgentRIntegration, ApiKeyIntegration, Integration
from universal_mcp.stores import store_from_config
from universal_mcp.stores.store import (
    EnvironmentStore,
    KeyringStore,
    MemoryStore,
)


class Server(FastMCP, ABC):
    """
    Server is responsible for managing the applications and the store
    It also acts as a router for the applications, and exposed to the client
    """

    def __init__(
        self, name: str, description: str, store: StoreConfig | None = None, **kwargs
    ):
        super().__init__(name, description, **kwargs)
        logger.info(f"Initializing server: {name} with store: {store}")
        self.store = store_from_config(store) if store else None

    @abstractmethod
    def _load_apps(self):
        pass

    async def call_tool(self, name: str, arguments: dict[str, Any]):
        """Call a tool by name with arguments."""
        try:
            result = await super().call_tool(name, arguments)
            return result
        except ToolError as e:
            raised_error = e.__cause__
            if isinstance(raised_error, NotAuthorizedError):
                return [TextContent(type="text", text=raised_error.message)]
            else:
                raise e


class LocalServer(Server):
    """
    Local server for development purposes
    """

    def __init__(
        self,
        apps_list: list[AppConfig] = None,
        **kwargs,
    ):
        if apps_list is None:
            apps_list = []
        super().__init__(**kwargs)
        self.apps_list = apps_list
        self.integrations_by_name: dict[str, Integration] = {}
        self._load_apps()

    def _get_store(self, store_config: StoreConfig | None):
        logger.info(f"Getting store: {store_config}")
        if store_config is None:
            return self.store
        if store_config.type == "memory":
            return MemoryStore()
        elif store_config.type == "environment":
            return EnvironmentStore()
        elif store_config.type == "keyring":
            return KeyringStore(app_name=self.name)
        return None

    def _get_integration(self, integration_config: IntegrationConfig | None):
        if not integration_config:
            return None
        if integration_config.type == "api_key":
            store = self._get_store(integration_config.store)
            integration = ApiKeyIntegration(integration_config.name, store=store)
            logger.info(f"Adding integration to dict: Name='{integration.name}'") # ADD LOGGING HERE
            self.integrations_by_name[integration.name] = integration
            if integration_config.credentials:
                integration.set_credentials(integration_config.credentials)
            return integration
        return None

    def _load_app(self, app_config: AppConfig):
        name = app_config.name
        integration = self._get_integration(app_config.integration)
        app = app_from_name(name)(integration=integration)
        return app

    def _load_apps(self):
        logger.info(f"Loading apps: {self.apps_list}")
        for app_config in self.apps_list:
            app = self._load_app(app_config)
            if app:
                tools = app.list_tools()
                for tool in tools:
                    name = app.name + "_" + tool.__name__
                    description = tool.__doc__
                    self.add_tool(tool, name=name, description=description)
                    
        logger.info("Registering server management tools.")
        self.add_tool(
            self.set_integration_credential,
            name="server_set_integration_credential", # The name the agent will use
            description="Stores an API key credential for a specific integration using its configured persistent store (e.g., keyring)."
        )

    async def set_integration_credential(self, integration_name: str, api_key_value: str) -> str:
        """
        Stores the API key for the specified integration name using its configured store.

        Args:
            integration_name: The name of the integration (e.g., 'E2B_API_KEY').
            api_key_value: The actual API key string to store.

        Returns:
            A confirmation or error message string.
        """
        logger.info(f"Attempting to set credential for integration: {integration_name}")

        integration = self.integrations_by_name.get(integration_name)

        if not integration:
            logger.error(f"Integration '{integration_name}' not found or not loaded by the server.")
            return f"Error: Integration '{integration_name}' is not configured on this server."

        if isinstance(integration, ApiKeyIntegration):
            try:
                integration.set_credentials({"api_key": api_key_value})
                logger.info(f"Successfully stored API key for {integration_name} via its store.")
                return f"Successfully stored API key for '{integration_name}'."
            except Exception as e:
                logger.error(f"Failed to store API key for {integration_name} using its store: {e}")
                return f"Error: Failed to store API key for '{integration_name}'. Reason: {e}"
        else:
            logger.warning(f"Integration '{integration_name}' is not of type ApiKeyIntegration. Cannot set API key.")
            return f"Error: Cannot set API key for integration '{integration_name}' (unsupported type: {type(integration).__name__})."

class AgentRServer(Server):
    """
    AgentR server. Connects to the AgentR API to get the apps and tools. Only supports agentr integrations.
    """

    def __init__(
        self, name: str, description: str, api_key: str | None = None, **kwargs
    ):
        super().__init__(name, description=description, **kwargs)
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        self.base_url = os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        if not self.api_key:
            raise ValueError("API key required - get one at https://agentr.dev")
        self._load_apps()

    def _load_app(self, app_config: AppConfig):
        name = app_config.name
        if app_config.integration:
            integration_name = app_config.integration.name
            integration = AgentRIntegration(integration_name, api_key=self.api_key)
        else:
            integration = None
        app = app_from_name(name)(integration=integration)
        return app

    def _list_apps_with_integrations(self):
        # TODO: get this from the API
        response = httpx.get(
            f"{self.base_url}/api/apps/", headers={"X-API-KEY": self.api_key}
        )
        response.raise_for_status()
        apps = response.json()

        logger.info(f"Apps: {apps}")
        return [AppConfig.model_validate(app) for app in apps]

    def _load_apps(self):
        apps = self._list_apps_with_integrations()
        for app in apps:
            app = self._load_app(app)
            if app:
                tools = app.list_tools()
                for tool in tools:
                    name = app.name + "_" + tool.__name__
                    description = tool.__doc__
                    self.add_tool(tool, name=name, description=description)
