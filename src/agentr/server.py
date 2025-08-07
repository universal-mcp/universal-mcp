from loguru import logger

from universal_mcp.applications import app_from_config
from universal_mcp.config import AppConfig, ServerConfig
from universal_mcp.servers.server import BaseServer
from universal_mcp.tools import ToolManager

from .client import AgentrClient
from .integration import AgentRIntegration


def load_from_agentr_server(client: AgentrClient, tool_manager: ToolManager) -> None:
    """Load apps from AgentR server and register their tools."""
    try:
        apps = client.fetch_apps()
        for app in apps:
            try:
                app_config = AppConfig.model_validate(app)
                integration = (
                    AgentRIntegration(name=app_config.integration.name, client=client)  # type: ignore
                    if app_config.integration
                    else None
                )
                app_instance = app_from_config(app_config)(integration=integration)
                tool_manager.register_tools_from_app(app_instance, app_config.actions)
                logger.info(f"Loaded app from AgentR: {app_config.name}")
            except Exception as e:
                logger.error(f"Failed to load app from AgentR: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to fetch apps from AgentR: {e}", exc_info=True)
        raise


class AgentRServer(BaseServer):
    """Server that loads apps from AgentR server."""

    def __init__(self, config: ServerConfig, **kwargs):
        super().__init__(config, **kwargs)
        self._tools_loaded = False
        self.api_key = config.api_key.get_secret_value() if config.api_key else None
        self.base_url = config.base_url
        self.client = AgentrClient(api_key=self.api_key, base_url=self.base_url)

    @property
    def tool_manager(self) -> ToolManager:
        if self._tool_manager is None:
            self._tool_manager = ToolManager(warn_on_duplicate_tools=True)
        if not self._tools_loaded:
            load_from_agentr_server(self.client, self._tool_manager)
            self._tools_loaded = True
        return self._tool_manager
