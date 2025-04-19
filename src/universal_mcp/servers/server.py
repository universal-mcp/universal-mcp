import os
from abc import ABC, abstractmethod
from typing import Any

import httpx
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from universal_mcp.applications import Application, app_from_slug
from universal_mcp.config import AppConfig, IntegrationConfig, ServerConfig, StoreConfig
from universal_mcp.exceptions import NotAuthorizedError, ToolError
from universal_mcp.integrations import AgentRIntegration, ApiKeyIntegration, Integration
from universal_mcp.stores import BaseStore, store_from_config
from universal_mcp.tools.tools import ToolManager


class IntegrationFactory:
    """Factory class for creating integrations"""
    
    @staticmethod
    def create(config: IntegrationConfig | None, store: BaseStore | None = None, api_key: str | None = None) -> Integration | None:
        if not config:
            return None
            
        if config.type == "api_key":
            integration = ApiKeyIntegration(config.name, store=store)
            if config.credentials:
                integration.set_credentials(config.credentials)
            return integration
        elif config.type == "agentr":
            return AgentRIntegration(config.name, api_key=api_key)
            
        raise ValueError(f"Unsupported integration type: {config.type}")


class BaseServer(FastMCP, ABC):
    """Base server class with common functionality"""

    def __init__(self, config: ServerConfig, **kwargs):
        super().__init__(config.name, config.description, **kwargs)
        logger.info(f"Initializing server: {config.name} with store: {config.store}")
        
        self.store = self._setup_store(config.store)
        self._tool_manager = ToolManager(warn_on_duplicate_tools=True)
        self._load_apps()

    def _setup_store(self, store_config: StoreConfig | None) -> BaseStore | None:
        """Setup and configure the store"""
        if not store_config:
            return None
        
        store = store_from_config(store_config)
        self._tool_manager.add_tool(store.set, name="set")
        self._tool_manager.add_tool(store.delete, name="store_delete") 
        return store

    @abstractmethod
    def _load_apps(self) -> None:
        """Load and register applications"""
        pass
                    
    async def call_tool(self, name: str, arguments: dict[str, Any]):
        """Call a tool with error handling"""
        logger.info(f"Calling tool: {name} with arguments: {arguments}")
        try:
            result = await self._tool_manager.call_tool(name, arguments)
            logger.info(f"Tool '{name}' completed successfully via ToolManager")
            if isinstance(result, str):
                 return [TextContent(type="text", text=result)]
            elif isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
                 return result
            else:
                 logger.warning(f"Tool '{name}' returned unexpected type: {type(result)}. Wrapping in TextContent.")
                 return [TextContent(type="text", text=str(result))]

        except ToolError as e:
            if isinstance(e.__cause__, NotAuthorizedError):
                message = f"Not authorized to call tool {name}: {e.__cause__.message}"
                logger.warning(message)
                return [TextContent(type="text", text=message)]
            logger.error(f"Error calling tool {name}: {str(e)}")
            raise


class LocalServer(BaseServer):
    """Local development server"""

    def __init__(self, config: ServerConfig, **kwargs):
        self.config = config
        super().__init__(config, **kwargs)

    def _load_app(self, app_config: AppConfig) -> Application | None:
        """Load a single application with its integration"""
        try:
            integration = IntegrationFactory.create(
                app_config.integration,
                store=self.store
            )
            return app_from_slug(app_config.name)(integration=integration)
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}")
            return None

    def _load_apps(self) -> None:
        """Load all configured applications"""
        logger.info(f"Loading apps: {self.config.apps}")
        for app_config in self.config.apps:
            app = self._load_app(app_config)
            if app:
                self._tool_manager.register_tools_from_app(app, app_config.actions)


class AgentRServer(BaseServer):
    """AgentR API-connected server"""

    def __init__(self, config: ServerConfig, api_key: str | None = None, **kwargs):
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        self.base_url = os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        
        if not self.api_key:
            raise ValueError("API key required - get one at https://agentr.dev")
            
        super().__init__(config, **kwargs)

    def _fetch_apps(self) -> list[AppConfig]:
        """Fetch available apps from AgentR API"""
        response = httpx.get(
            f"{self.base_url}/api/apps/",
            headers={"X-API-KEY": self.api_key},
            timeout=10,
        )
        response.raise_for_status()
        return [AppConfig.model_validate(app) for app in response.json()]

    def _load_app(self, app_config: AppConfig) -> Application | None:
        """Load a single application with AgentR integration"""
        try:
            integration = IntegrationFactory.create(
                app_config.integration,
                api_key=self.api_key
            )
            return app_from_slug(app_config.name)(integration=integration)
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}")
            return None

    def _load_apps(self) -> None:
        """Load all apps available from AgentR"""
        for app_config in self._fetch_apps():
            app = self._load_app(app_config)
            if app:
                self._tool_manager.register_tools_from_app(app, app_config.actions)
