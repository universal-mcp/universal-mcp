from universal_mcp.config import IntegrationConfig
from universal_mcp.integrations.integration import (
    AgentRIntegration,
    ApiKeyIntegration,
    Integration,
    OAuthIntegration,
)
from universal_mcp.stores.store import BaseStore


def integration_from_config(config: IntegrationConfig, store: BaseStore | None = None, **kwargs) -> Integration:
    if config.type == "api_key":
        return ApiKeyIntegration(config.name, store=store, **kwargs)
    elif config.type == "agentr":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("api_key is required for AgentR integration")
        return AgentRIntegration(config.name, api_key=api_key)
    else:
        raise ValueError(f"Unsupported integration type: {config.type}")


__all__ = [
    "AgentRIntegration",
    "ApiKeyIntegration",
    "Integration",
    "OAuthIntegration",
    "integration_from_config",
]
