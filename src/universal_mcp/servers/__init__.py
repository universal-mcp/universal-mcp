from universal_mcp.config import ServerConfig
from universal_mcp.servers.server import AgentRServer, LocalServer


def server_from_config(config: ServerConfig):
    if config.type == "agentr":
        return AgentRServer(
            name=config.name,
            description=config.description,
            api_key=config.api_key,
            port=config.port,
        )
    elif config.type == "local":
        return LocalServer(
            name=config.name,
            description=config.description,
            store=config.store,
            apps_list=config.apps,
            port=config.port,
        )


__all__ = [AgentRServer, LocalServer]
