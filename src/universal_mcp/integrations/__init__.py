from universal_mcp.config import IntegrationConfig
from universal_mcp.integrations.integration import (
    ApiKeyIntegration,
    Integration,
    OAuthIntegration,
)
from universal_mcp.stores.store import BaseStore


def integration_from_config(config: IntegrationConfig, store: BaseStore | None = None, **kwargs) -> Integration:
    if config.type == "api_key":
        return ApiKeyIntegration(config.name, store=store, **kwargs)
    else:
        raise ValueError(f"Unsupported integration type: {config.type}")


__all__ = [
    "AgentRIntegration",
    "ApiKeyIntegration",
    "Integration",
    "OAuthIntegration",
    "integration_from_config",
]
