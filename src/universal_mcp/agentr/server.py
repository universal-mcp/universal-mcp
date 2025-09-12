from loguru import logger

from universal_mcp.config import ServerConfig
from universal_mcp.servers.server import BaseServer
from universal_mcp.tools import ToolManager

from .client import AgentrClient
from .registry import AgentrRegistry


class AgentrServer(BaseServer):
    """Server that loads apps and tools from an AgentR instance."""

    def __init__(self, config: ServerConfig, registry: AgentrRegistry | None = None, **kwargs):
        super().__init__(config, **kwargs)

        if registry:
            self.registry = registry
        else:
            api_key = config.api_key.get_secret_value() if config.api_key else None
            client = AgentrClient(api_key=api_key, base_url=config.base_url)
            self.registry = AgentrRegistry(client=client)

        self._tools_loaded = False
        self._load_all_tools_from_remote()

    def _load_all_tools_from_remote(self):
        """Load all available tools from the remote AgentR server."""
        if self._tools_loaded:
            return

        logger.info("Loading all available tools from AgentR server...")
        try:
            all_apps = self.registry.client.list_all_apps()
            if not all_apps:
                logger.warning("No apps found on AgentR server.")
                self._tools_loaded = True
                return

            # Create a tool config to load all default (important) tools for each app
            tool_config = {app["name"]: [] for app in all_apps}

            self.registry._load_tools_from_tool_config(tool_config)
            self._tools_loaded = True
            logger.info(f"Finished loading tools for {len(all_apps)} app(s) from AgentR server.")
        except Exception as e:
            logger.error(f"Failed to load tools from AgentR: {e}", exc_info=True)
            raise

    @property
    def tool_manager(self) -> ToolManager:
        return self.registry.tool_manager
