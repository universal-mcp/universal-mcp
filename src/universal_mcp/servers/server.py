import os
from abc import ABC, abstractmethod
from typing import Any

import httpx
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import TextContent

from universal_mcp.applications import app_from_slug
from universal_mcp.config import AppConfig, IntegrationConfig, StoreConfig
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import AgentRIntegration, ApiKeyIntegration
from universal_mcp.stores import store_from_config


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
        self._setup_store(store)
        self._load_apps()

    def _setup_store(self, store_config: StoreConfig | None):
        """
        Setup the store for the server.
        """
        if store_config is None:
            return
        self.store = store_from_config(store_config)
        self.add_tool(self.store.set)
        self.add_tool(self.store.delete)
        # self.add_tool(self.store.get)

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
        if not apps_list:
            self.apps_list = []
        else:
            self.apps_list = apps_list
        super().__init__(**kwargs)

    def _get_store(self, store_config: StoreConfig | None):
        logger.info(f"Getting store: {store_config}")
        # No store override, use the one from the server
        if store_config is None:
            return self.store
        return store_from_config(store_config)

    def _get_integration(self, integration_config: IntegrationConfig | None):
        if not integration_config:
            return None
        if integration_config.type == "api_key":
            store = self._get_store(integration_config.store)
            integration = ApiKeyIntegration(integration_config.name, store=store)
            if integration_config.credentials:
                integration.set_credentials(integration_config.credentials)
            return integration
        return None

    def _load_app(self, app_config: AppConfig):
        name = app_config.name
        integration = self._get_integration(app_config.integration)
        app = app_from_slug(name)(integration=integration)
        return app

    def _load_apps(self):
        logger.info(f"Loading apps: {self.apps_list}")
        for app_config in self.apps_list:
            app = self._load_app(app_config)
            if app:
                tools = app.list_tools()
                for tool in tools:
                    full_tool_name = app.name + "_" + tool.__name__
                    description = tool.__doc__
                    should_add_tool = False
                    if (
                        app_config.actions is None
                        or full_tool_name in app_config.actions
                    ):
                        should_add_tool = True
                    if should_add_tool:
                        self.add_tool(
                            tool, name=full_tool_name, description=description
                        )


class AgentRServer(Server):
    """
    AgentR server. Connects to the AgentR API to get the apps and tools. Only supports agentr integrations.
    """

    def __init__(
        self, name: str, description: str, api_key: str | None = None, **kwargs
    ):
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        self.base_url = os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        if not self.api_key:
            raise ValueError("API key required - get one at https://agentr.dev")
        super().__init__(name, description=description, **kwargs)

    def _load_app(self, app_config: AppConfig):
        name = app_config.name
        if app_config.integration:
            integration_name = app_config.integration.name
            integration = AgentRIntegration(integration_name, api_key=self.api_key)
        else:
            integration = None
        app = app_from_slug(name)(integration=integration)
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
