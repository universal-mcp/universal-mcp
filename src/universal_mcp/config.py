import json
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
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
    type: Literal["api_key", "oauth", "agentr", "oauth2", "basic_auth"] = Field(
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
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    name: str = Field(default="Universal MCP", description="Name of the MCP server")
    description: str = Field(default="Universal MCP", description="Description of the MCP server")
    base_url: str = Field(
        default="https://api.agentr.dev", description="Base URL for AgentR API", alias="AGENTR_BASE_URL"
    )
    api_key: SecretStr | None = Field(default=None, description="API key for authentication", alias="AGENTR_API_KEY")
    type: Literal["local", "agentr"] = Field(default="agentr", description="Type of server deployment")
    transport: Literal["stdio", "sse", "streamable-http"] = Field(
        default="stdio", description="Transport protocol to use"
    )
    port: int = Field(default=8005, description="Port to run the server on (if applicable)", ge=1024, le=65535)
    host: str = Field(default="localhost", description="Host to bind the server to (if applicable)")
    apps: list[AppConfig] | None = Field(default=None, description="List of configured applications")
    store: StoreConfig | None = Field(default=None, description="Default store configuration")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None, description="OpenTelemetry OTLP exporter endpoint", alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )

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

    @classmethod
    def load_json_config(cls, path: str = "local_config.json") -> Self:
        with open(path) as f:
            data = json.load(f)
        return cls.model_validate(data)


class ClientTransportConfig(BaseModel):
    transport: str | None = None
    command: str | None = None
    args: list[str] = []
    env: dict[str, str] = {}
    url: str | None = None
    headers: dict[str, str] = {}

    @model_validator(mode="after")
    def model_validate(self) -> Self:
        """
        Set the transport type based on the presence of command or url.
        - If command is present, transport is 'stdio'.
        - Else if url ends with 'mcp', transport is 'streamable_http'.
        - Else, transport is 'sse'.
        """
        if self.command:
            self.transport = "stdio"
        elif self.url:
            # Remove search params from url
            url = self.url.split("?")[0]
            if url.rstrip("/").endswith("mcp"):
                self.transport = "streamable_http"
            elif url.rstrip("/").endswith("sse"):
                self.transport = "sse"
            else:
                raise ValueError(f"Unknown transport: {self.url}")
        else:
            raise ValueError("Either command or url must be provided")
        return self


class LLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str


class ClientConfig(BaseSettings):
    mcpServers: dict[str, ClientTransportConfig]
    llm: LLMConfig | None = None

    @classmethod
    def load_json_config(cls, path: str = "servers.json") -> Self:
        with open(path) as f:
            data = json.load(f)
        return cls.model_validate(data)
