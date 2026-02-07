import json
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StoreConfig(BaseModel):
    """Specifies the configuration for a credential or token store.

    Defines where and how sensitive information like API keys or OAuth tokens
    should be stored and retrieved.
    """

    name: str = Field(
        default="universal_mcp",
        description="Name of the store service or context (e.g., 'my_app_tokens', 'global_api_keys').",
    )
    type: Literal["disk", "memory", "environment", "keyring"] = Field(
        default="disk",
        description="Storage backend: 'disk' (default, persistent file-based), 'memory' (transient), 'environment' (env vars), 'keyring' (system secure storage).",
    )
    path: Path | None = Field(
        default=None,
        description="Path for disk-based store. Defaults to ~/.universal-mcp/store",
    )


class ConnectionConfig(BaseModel):
    """Configuration for a user-specific connection.

    Represents a single user's credentials for an integration.
    Separate from IntegrationConfig which holds shared configuration.
    """

    integration_name: str = Field(
        description="Name of the integration this connection uses"
    )
    user_id: str = Field(
        default="default",
        description="User identifier for multi-user scenarios"
    )
    credentials: dict[str, Any] | None = Field(
        default=None,
        description="User-specific credentials (tokens, keys)"
    )
    status: str = Field(
        default="pending",
        description="Connection status: pending, active, expired, revoked"
    )


class IntegrationConfig(BaseModel):
    """Configuration for an integration template (shared config).

    Defines HOW to connect (client configuration, endpoints) as opposed to
    WHAT credentials to use (which are in ConnectionConfig).

    For OAuth integrations, this holds the client_id/client_secret (shared
    across all users). For API key integrations, this just defines the
    integration type and store configuration.
    """

    name: str = Field(
        ..., description="A unique name for this integration instance (e.g., 'my_github_oauth', 'tavily_api_key')."
    )
    type: Literal["api_key", "oauth2", "basic_auth"] = Field(
        default="api_key",
        description="Authentication mechanism: 'api_key' (Bearer token), 'oauth2' (OAuth 2.0), or 'basic_auth' (user/pass).",
    )

    # For OAuth integrations (shared config)
    client_id: str | None = Field(
        default=None,
        description="OAuth client ID (shared across users)"
    )
    client_secret: str | None = Field(
        default=None,
        description="OAuth client secret (shared across users)"
    )
    auth_url: str | None = Field(
        default=None,
        description="OAuth authorization endpoint"
    )
    token_url: str | None = Field(
        default=None,
        description="OAuth token endpoint"
    )
    scopes: list[str] | None = Field(
        default=None,
        description="OAuth scopes"
    )

    # Backward compatibility - direct credentials
    credentials: dict[str, Any] | None = Field(
        default=None,
        description="Directly provided credentials (legacy, prefer Connection model). Structure depends on the integration type (e.g., {'api_key': 'value'}). Use with caution for sensitive data; prefer using a 'store'.",
    )
    store: StoreConfig | None = Field(
        default=None,
        description="Configuration for the credential store to be used for this integration, overriding any default server-level store.",
    )


class AppConfig(BaseModel):
    """Configuration for a single application to be loaded by the MCP server.

    Defines an application's name (slug), its integration settings for
    authentication, and optionally, a list of specific actions (tools)
    it provides.
    """

    name: str = Field(
        ...,
        description="The unique name or slug of the application (e.g., 'github', 'google-calendar'). This is often used to dynamically load the application module.",
    )
    integration: IntegrationConfig | None = Field(
        default=None,
        description="Authentication and credential configuration for this application. If None, the application is assumed not to require authentication or uses a global/default mechanism.",
    )
    actions: list[str] | None = Field(
        default=None,
        description="A list of specific actions or tools provided by this application that should be exposed. If None or empty, all tools from the application might be exposed by default, depending on the application's implementation.",
    )

    source_type: Literal["package", "local_folder", "remote_zip", "remote_file", "local_file", "mcp_url"] = Field(
        default="package",
        description="The source of the application. 'package' (default) installs from a repository, 'local_folder' loads from a local path, 'remote_zip' downloads and extracts a project zip, 'remote_file' downloads a single Python file from a URL, 'local_file' loads a single Python file from the local filesystem, 'mcp_url' connects to a remote MCP server by URL.",
    )
    source_path: str | None = Field(
        default=None,
        description="The path or URL for 'local_folder', 'remote_zip', 'remote_file', or 'local_file' source types.",
    )

    @model_validator(mode="after")
    def check_path_for_non_package_sources(self) -> Self:
        if self.source_type in ["local_folder", "remote_zip", "remote_file", "local_file", "mcp_url"] and not self.source_path:
            raise ValueError(f"'source_path' is required for source_type '{self.source_type}'")
        return self


class ServerConfig(BaseSettings):
    """Core configuration settings for the Universal MCP server.

    Manages server behavior, including its name, description, transport protocol,
    network settings (port/host), applications to load, default credential store,
    and logging verbosity. Settings can be loaded from environment variables or
    a .env file.
    """

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )
    name: str = Field(default="Universal MCP", description="Name of the MCP server")
    description: str = Field(
        default="Universal MCP", description="A brief description of this MCP server's purpose or deployment."
    )
    type: Literal["local"] = Field(
        default="local",
        description="Server type. 'local' loads apps from the 'apps' list in config.",
    )
    transport: Literal["stdio", "sse", "streamable-http"] = Field(
        default="stdio",
        description="The communication protocol the server will use to interact with clients (e.g., an AI agent).",
    )
    port: int = Field(
        default=8005,
        description="Network port for 'sse' or 'streamable-http' transports. Must be between 1 and 65535.",
        ge=1,
        le=65535,
    )
    log_level: str = Field(
        default="INFO", description="Logging level for the server (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
    # Local specific settings
    apps: list[AppConfig] | None = Field(
        default=None,
        description="A list of application configurations to load on the local server.",
    )
    store: StoreConfig | None = Field(
        default=None,
        description="Default credential store configuration for applications that do not define their own specific store.",
    )

    @field_validator("log_level", mode="before")
    def validate_log_level(cls, v: str) -> str:
        """Validates and normalizes the log_level field."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("port", mode="before")
    def validate_port(cls, v: int) -> int:
        """Validates the port number is within the valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @classmethod
    def load_json_config(cls, path: str = "server_config.json") -> Self:
        """Loads server configuration from a JSON file.

        Args:
            path (str, optional): The path to the JSON configuration file.
                Defaults to "local_config.json".

        Returns:
            ServerConfig: An instance of ServerConfig populated with data
                          from the JSON file.
        """
        with open(path) as f:
            data = json.load(f)
        return cls.model_validate(data)


class ClientTransportConfig(BaseModel):
    """Configuration for how an MCP client connects to an MCP server.

    Specifies the transport protocol and its associated parameters, such as
    the command for stdio, URL for HTTP-based transports (SSE, streamable_http),
    and any necessary headers or environment variables.
    """

    transport: str | None = Field(
        default=None,
        description="The transport protocol (e.g., 'stdio', 'sse', 'streamable_http'). Auto-detected in model_validate if not set.",
    )
    command: str | None = Field(
        default=None, description="The command to execute for 'stdio' transport (e.g., 'python -m mcp_server.run')."
    )
    args: list[str] = Field(default=[], description="List of arguments for the 'stdio' command.")
    env: dict[str, str] = Field(default={}, description="Environment variables to set for the 'stdio' command.")
    url: str | None = Field(default=None, description="The URL for 'sse' or 'streamable_http' transport.")
    headers: dict[str, str] = Field(
        default={}, description="HTTP headers to include for 'sse' or 'streamable_http' transport (e.g., {'Authorization': 'Bearer <token>'})."
    )

    @model_validator(mode="after")
    def determine_transport_if_not_set(self) -> Self:
        """Determines and sets the transport type if not explicitly provided.

        - If `command` is present, transport is set to 'stdio'.
        - If `url` is present, transport is 'streamable_http' if URL ends with '/mcp',
          otherwise 'sse' if URL ends with '/sse'.
        - Raises ValueError if transport cannot be determined or if neither
          `command` nor `url` is provided.
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


class ClientConfig(BaseSettings):
    """Configuration for a client application that interacts with MCP servers and an LLM.

    Defines connections to one or more MCP servers (via `mcpServers`) and
    optionally, settings for an LLM to be used by the client (e.g., by an agent).
    """

    mcpServers: dict[str, ClientTransportConfig] = Field(
        ...,
        description="A dictionary where keys are descriptive names for MCP server connections and values are `ClientTransportConfig` objects defining how to connect to each server.",
    )

    @classmethod
    def load_json_config(cls, path: str = "servers.json") -> Self:
        """Loads client configuration from a JSON file.

        Args:
            path (str, optional): The path to the JSON configuration file.
                Defaults to "servers.json".

        Returns:
            ClientConfig: An instance of ClientConfig populated with data
                          from the JSON file.
        """
        with open(path) as f:
            data = json.load(f)
        return cls.model_validate(data)

    def save_json_config(self, path: str) -> None:
        """Saves the client configuration to a JSON file.

        Args:
            path (str): The path to save the JSON configuration file.
        """
        with open(path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)
