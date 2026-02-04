"""Universal MCP Client - Simplified wrapper around FastMCP client."""

from fastmcp import Client
from fastmcp.client.auth import OAuth

# Re-export FastMCP's client
__all__ = [
    "Client",
    "OAuth",
]
