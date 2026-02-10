from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from universal_mcp.connections.connection import (
    ApiKeyConnection,
    Connection,
    OAuthConnection,
)
from universal_mcp.exceptions import KeyNotFoundError, NotAuthorizedError
from universal_mcp.stores import BaseStore, MemoryStore


def sanitize_api_key_name(name: str) -> str:
    suffix = "_API_KEY"
    if name.endswith(suffix) or name.endswith(suffix.lower()):
        return name.upper()
    else:
        return f"{name.upper()}{suffix}"


class Integration(ABC):
    """Authentication integration template.

    Defines HOW to connect (client config, endpoints, scopes).
    Delegates user credentials to Connection instances.

    An Integration is a reusable template that can have multiple Connections
    (one per user). This separation enables multi-user support and proper
    OAuth implementation where client credentials are separate from user tokens.

    Attributes:
        name (str): The unique name identifying this integration
        store (BaseStore): The storage backend for connections
        type (str): Integration type (api_key, oauth2, etc.)
    """

    def __init__(self, name: str, store: BaseStore | None = None):
        """Initializes the Integration.

        Args:
            name: The unique name/identifier for this integration
            store: A store instance for persisting credentials. Defaults to MemoryStore()
        """
        self.name = self._sanitize_key_name(name)
        self.store = store or MemoryStore()
        self.type: str = "base"

        # Create default connection for backward compatibility
        self._default_connection: Connection | None = None

    @abstractmethod
    def create_connection(
        self, user_id: str | None = None, store: BaseStore | None = None
    ) -> Connection:
        """Create a new Connection instance for a user.

        Args:
            user_id: User identifier (defaults to "default")
            store: Storage backend (defaults to self.store)

        Returns:
            A new Connection instance
        """
        pass

    def get_default_connection(self) -> Connection:
        """Get or create the default connection (for single-user scenarios).

        Returns:
            The default connection instance
        """
        if not self._default_connection:
            self._default_connection = self.create_connection(user_id="default", store=self.store)
        return self._default_connection

    # FACADE METHODS - Async-only, delegate to default connection

    async def get_credentials(self) -> dict[str, Any]:
        """Get credentials from default connection asynchronously.

        Returns:
            Dictionary containing credentials

        Raises:
            NotAuthorizedError: If credentials not found
        """
        return await self.get_default_connection().get_credentials()

    async def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Set credentials on default connection asynchronously.

        Args:
            credentials: Dictionary containing credentials to store
        """
        await self.get_default_connection().set_credentials(credentials)

    @abstractmethod
    def authorize(self) -> str:
        """Return authorization setup instructions.

        Returns:
            Human-readable instruction message
        """
        pass

    @staticmethod
    def _sanitize_key_name(name: str) -> str:
        """Sanitize integration name (uppercase, add _API_KEY suffix if needed).

        Args:
            name: Raw integration name

        Returns:
            Sanitized name
        """
        name = name.upper().replace("-", "_").replace(" ", "_")
        if not name.endswith("_API_KEY") and not name.endswith("_TOKEN"):
            name = f"{name}_API_KEY"
        return name

    def __str__(self) -> str:
        return f"Integration(name={self.name}, type={self.type})"

    def __repr__(self) -> str:
        return self.__str__()


class ApiKeyIntegration(Integration):
    """API Key authentication integration.

    Manages API key authentication using the Connection abstraction.
    The integration holds no user-specific state - all credentials are
    stored in Connection instances.

    Attributes:
        name (str): The sanitized name (e.g., "GITHUB_API_KEY")
        store (BaseStore): Store for persisting credentials
        type (str): Set to "api_key"
    """

    def __init__(self, name: str, store: BaseStore | None = None, **kwargs):
        """Initializes ApiKeyIntegration.

        The provided `name` is sanitized (e.g., 'github' becomes 'GITHUB_API_KEY')
        to form the actual key used for storage.

        Args:
            name: The base name for the API key (e.g., "TAVILY")
            store: Store for credentials. Defaults to MemoryStore()
            **kwargs: Additional arguments (for future extensibility)
        """
        super().__init__(name, store)
        self.type = "api_key"
        logger.info(f"Initializing API Key Integration: {name} with store: {store}")

    def create_connection(
        self, user_id: str | None = None, store: BaseStore | None = None
    ) -> Connection:
        """Create API key connection.

        Args:
            user_id: User identifier (defaults to "default")
            store: Storage backend (defaults to self.store)

        Returns:
            New ApiKeyConnection instance
        """
        return ApiKeyConnection(
            integration_name=self.name,
            user_id=user_id or "default",
            store=store or self.store,
        )

    def authorize(self) -> str:
        """Return API key setup instructions.

        Returns:
            Instruction message for setting up API key
        """
        return (
            f"To authorize {self.name}, set your API key:\n\n"
            f"  integration.set_credentials({{'api_key': 'your-key-here'}})\n\n"
            f"Or use environment variable: {self.name}"
        )

    # Convenience methods (async-only)
    async def get_api_key(self) -> str:
        """Get API key from default connection asynchronously.

        Returns:
            The API key string

        Raises:
            NotAuthorizedError: If API key not found
        """
        conn = self.get_default_connection()
        assert isinstance(conn, ApiKeyConnection)
        return await conn.get_api_key()

    async def set_api_key(self, value: str) -> None:
        """Set API key on default connection asynchronously.

        Args:
            value: API key string
        """
        conn = self.get_default_connection()
        assert isinstance(conn, ApiKeyConnection)
        await conn.set_api_key(value)


class OAuthIntegration(Integration):
    """OAuth 2.0 authentication integration.

    Holds shared OAuth client configuration (client_id, client_secret, endpoints)
    while delegating user-specific tokens to OAuthConnection instances.

    This separation enables proper OAuth implementation where:
    - Integration = OAuth app registration (shared across users)
    - Connection = User's access/refresh tokens (per-user)

    Attributes:
        name (str): Integration name
        store (BaseStore): Store for persisting user tokens
        type (str): Set to "oauth2"
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret
        auth_url (str): Authorization endpoint URL
        token_url (str): Token endpoint URL
        scopes (list[str]): OAuth scopes
    """

    def __init__(
        self,
        name: str,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        scopes: list[str] | None = None,
        store: BaseStore | None = None,
    ):
        """Initialize OAuth integration.

        Args:
            name: Integration name
            client_id: OAuth client ID (shared config)
            client_secret: OAuth client secret (shared config)
            auth_url: Authorization endpoint
            token_url: Token endpoint
            scopes: OAuth scopes (defaults to empty list)
            store: Storage backend for user tokens
        """
        super().__init__(name, store)
        self.type = "oauth2"

        # Integration config (shared across users)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.scopes = scopes or []

    def create_connection(
        self, user_id: str | None = None, store: BaseStore | None = None
    ) -> Connection:
        """Create OAuth connection.

        Args:
            user_id: User identifier (defaults to "default")
            store: Storage backend (defaults to self.store)

        Returns:
            New OAuthConnection instance
        """
        return OAuthConnection(
            integration_name=self.name,
            user_id=user_id or "default",
            store=store or self.store,
        )

    def authorize(self) -> str:
        """Return OAuth setup instructions.

        Returns:
            Instruction message for OAuth flow
        """
        return (
            f"To authorize {self.name}, complete the OAuth flow:\n\n"
            f"1. Visit: {self.auth_url}\n"
            f"2. Grant permissions for scopes: {', '.join(self.scopes)}\n"
            f"3. Exchange authorization code for tokens\n\n"
            "OAuth flow will be handled automatically."
        )

    def get_authorization_url(self, redirect_uri: str, state: str | None = None) -> str:
        """Generate OAuth authorization URL.

        Args:
            redirect_uri: Redirect URI for OAuth callback
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL

        Raises:
            NotImplementedError: OAuth flow not yet implemented
        """
        # TODO: Implement OAuth flow
        raise NotImplementedError("OAuth flow not yet implemented")

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response dictionary

        Raises:
            NotImplementedError: OAuth token exchange not yet implemented
        """
        # TODO: Implement token exchange
        raise NotImplementedError("OAuth token exchange not yet implemented")


class IntegrationFactory:
    """A factory for creating integration instances."""

    @staticmethod
    def create(app_name: str, integration_type: str = "api_key", **kwargs) -> Integration:
        """Create an integration instance.

        Args:
            app_name: Name of the application
            integration_type: Type of integration ("api_key" or "oauth2")
            **kwargs: Additional arguments for specific integration types

        Returns:
            Integration instance

        Raises:
            ValueError: If integration type is not supported
        """
        if integration_type == "api_key":
            return ApiKeyIntegration(app_name, **kwargs)
        elif integration_type == "oauth2":
            # OAuth requires additional parameters
            return OAuthIntegration(app_name, **kwargs)
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")
