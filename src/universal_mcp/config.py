from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StoreConfig(BaseModel):
    """Configuration for credential storage."""

    name: str = Field(default="universal_mcp", description="Name of the store")
    type: Literal["memory", "environment", "keyring", "agentr"] = Field(
        default="memory", description="Type of credential storage to use"
    )
    path: Path | None = Field(default=None, description="Path to store credentials (if applicable)")


class IntegrationConfig(BaseModel):
    """Configuration for API integrations."""

    name: str = Field(..., description="Name of the integration")
    type: Literal["api_key", "oauth", "agentr", "oauth2"] = Field(
        default="api_key", description="Type of authentication to use"
    )
    credentials: dict[str, Any] | None = Field(default=None, description="Integration-specific credentials")
    store: StoreConfig | None = Field(default=None, description="Store configuration for credentials")


class AppConfig(BaseModel):
    """Configuration for individual applications."""

    name: str = Field(..., description="Name of the application")
    integration: IntegrationConfig | None = Field(default=None, description="Integration configuration")
    actions: list[str] | None = Field(default=None, description="List of available actions")


class ServerConfig(BaseSettings):
    """Main server configuration."""

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    name: str = Field(default="Universal MCP", description="Name of the MCP server")
    description: str = Field(default="Universal MCP", description="Description of the MCP server")
    api_key: SecretStr | None = Field(default=None, description="API key for authentication")
    type: Literal["local", "agentr"] = Field(default="agentr", description="Type of server deployment")
    transport: Literal["stdio", "sse", "http"] = Field(default="stdio", description="Transport protocol to use")
    port: int = Field(default=8005, description="Port to run the server on (if applicable)")
    host: str = Field(default="localhost", description="Host to bind the server to (if applicable)")
    apps: list[AppConfig] | None = Field(default=None, description="List of configured applications")
    store: StoreConfig | None = Field(default=None, description="Default store configuration")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    max_connections: int = Field(default=100, description="Maximum number of concurrent connections")
    request_timeout: int = Field(default=60, description="Default request timeout in seconds")

    @field_validator("log_level", mode="before")
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("port", mode="before")
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
