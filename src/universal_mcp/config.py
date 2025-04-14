from typing import Literal

from pydantic import BaseModel


class StoreConfig(BaseModel):
    name: str = "universal_mcp"
    type: Literal["memory", "environment", "keyring", "agentr"]


class IntegrationConfig(BaseModel):
    name: str
    type: Literal["api_key", "oauth", "agentr", "oauth2"]
    credentials: dict | None = None
    store: StoreConfig | None = None


class AppConfig(BaseModel):
    name: str
    integration: IntegrationConfig | None = None
    actions: list[str] | None = None


class ServerConfig(BaseModel):
    name: str = "Universal MCP"
    description: str = "Universal MCP"
    api_key: str | None = None
    type: Literal["local", "agentr"] = "agentr"
    transport: Literal["stdio", "sse", "http"] = "stdio"
    port: int = 8005
    apps: list[AppConfig] | None = None
    store: StoreConfig | None = None
