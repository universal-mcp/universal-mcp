from abc import ABC, abstractmethod
import httpx
from mcp.server.fastmcp import FastMCP
from universal_mcp.applications import app_from_name
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import ApiKeyIntegration, AgentRIntegration
from universal_mcp.stores.store import EnvironmentStore, MemoryStore
from universal_mcp.config import AppConfig, IntegrationConfig, StoreConfig
from loguru import logger
import os
from typing import Any
from mcp.types import TextContent
from mcp.server.fastmcp.exceptions import ToolError

class Server(FastMCP, ABC):
    """
    Server is responsible for managing the applications and the store
    It also acts as a router for the applications, and exposed to the client
    """
    def __init__(self, name: str, description: str, **kwargs):
        super().__init__(name, description, **kwargs)

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
    def __init__(self, name: str, description: str, apps_list: list[AppConfig] = [], **kwargs):
        super().__init__(name, description=description, **kwargs)
        self.apps_list = [AppConfig.model_validate(app) for app in apps_list]
        self._load_apps()
    
    def _get_store(self, store_config: StoreConfig):
        if store_config.type == "memory":
            return MemoryStore()
        elif store_config.type == "environment":
            return EnvironmentStore()
        return None

    def _get_integration(self, integration_config: IntegrationConfig):
        if not integration_config:
            return None
        if integration_config.type == "api_key":
            store = self._get_store(integration_config.store)
            integration = ApiKeyIntegration(integration_config.name, store=store)
            if integration_config.credentials:
                integration.set_credentials(integration_config.credentials)
            return integration
        elif integration_config.type == "agentr":
            integration = AgentRIntegration(integration_config.name, api_key=integration_config.credentials.get("api_key") if integration_config.credentials else None)
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

                

class AgentRServer(Server):
    """
    AgentR server. Connects to the AgentR API to get the apps and tools. Only supports agentr integrations.
    """
    def __init__(self, name: str, description: str, api_key: str | None = None, **kwargs):
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
            f"{self.base_url}/api/apps/",
            headers={
                "X-API-KEY": self.api_key
            }
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