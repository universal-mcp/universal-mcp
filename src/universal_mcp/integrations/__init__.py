"""Integration and connection management."""

from universal_mcp.connections.connection import (
    ApiKeyConnection,
    Connection,
    OAuthConnection,
)
from universal_mcp.integrations.integration import (
    ApiKeyIntegration,
    Integration,
    IntegrationFactory,
    OAuthIntegration,
)

__all__ = [
    "Integration",
    "ApiKeyIntegration",
    "OAuthIntegration",
    "IntegrationFactory",
    "Connection",
    "ApiKeyConnection",
    "OAuthConnection",
]
