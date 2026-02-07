"""Connection management for user-specific credentials."""

from universal_mcp.connections.connection import (
    ApiKeyConnection,
    Connection,
    OAuthConnection,
)

__all__ = [
    "Connection",
    "ApiKeyConnection",
    "OAuthConnection",
]
