from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from universal_mcp.connections.connection import (
    ApiKeyConnection,
    Connection,
    OAuthConnection,
)
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
    def create_connection(self, user_id: str | None = None, store: BaseStore | None = None) -> Connection:
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

    def create_connection(self, user_id: str | None = None, store: BaseStore | None = None) -> Connection:
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
        # Don't sanitize name for OAuth - use raw name
        # Override parent's __init__ to skip _sanitize_key_name
        self.name = name.upper().replace("-", "_").replace(" ", "_")
        self.store = store or MemoryStore()
        self.type = "oauth2"
        self._default_connection: Connection | None = None

        # Integration config (shared across users)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.scopes = scopes or []

        # OAuth flow state (per-instance)
        self._pkce = None  # Will hold PKCEParameters during auth flow
        self._server_url = None  # Original server URL (set by from_server_url)
        self._registered_redirect_uri = None  # Redirect URI registered with auth server

    def create_connection(self, user_id: str | None = None, store: BaseStore | None = None) -> Connection:
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
        """Generate OAuth authorization URL with PKCE.

        Args:
            redirect_uri: Redirect URI for OAuth callback
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL string
        """
        import secrets
        from urllib.parse import urlencode

        from mcp.client.auth.oauth2 import PKCEParameters

        # Generate PKCE
        self._pkce = PKCEParameters.generate()

        # Generate state if not provided
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": self._pkce.code_challenge,
            "code_challenge_method": "S256",
        }
        if self.scopes:
            params["scope"] = " ".join(self.scopes)

        return f"{self.auth_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token credentials dictionary with access_token, refresh_token, etc.
        """
        import httpx

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
        }
        if self._pkce:
            data["code_verifier"] = self._pkce.code_verifier
        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

        # Store tokens via connection
        import time

        expires_in = token_data.get("expires_in")
        credentials = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": (time.time() + expires_in) if expires_in else None,
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope"),
        }
        await self.set_credentials(credentials)

        # Also store in token storage if we have server_url
        if self._server_url and self.store:
            from mcp.shared.auth import OAuthToken

            from universal_mcp.integrations.oauth_helpers import StoreTokenStorage

            oauth_token = OAuthToken(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "bearer"),
                expires_in=token_data.get("expires_in"),
                refresh_token=token_data.get("refresh_token"),
                scope=token_data.get("scope"),
            )
            token_storage = StoreTokenStorage(self.store, self._server_url)
            await token_storage.set_tokens(oauth_token)

        self._pkce = None  # Clear PKCE after use
        return credentials

    async def run_oauth_flow(self, callback_port: int = 0) -> str:
        """Run the full interactive OAuth authorization flow.

        Opens the browser for authorization, starts a local callback server,
        waits for the callback, and exchanges the code for tokens.

        If a redirect_uri was registered during from_server_url(), the callback
        server binds to the same port for consistency.

        Args:
            callback_port: Port for callback server (0 = find free port)

        Returns:
            Access token string
        """
        import webbrowser
        from urllib.parse import urlparse

        from universal_mcp.integrations.oauth_helpers import run_oauth_callback_server

        # Use the registered redirect URI port if available, for consistency
        if self._registered_redirect_uri and callback_port == 0:
            parsed = urlparse(self._registered_redirect_uri)
            if parsed.port:
                callback_port = parsed.port

        # Start callback server
        callback_url, actual_port, result_future, runner = await run_oauth_callback_server(callback_port)

        try:
            logger.info(f"OAuth callback server started on port {actual_port}")

            # Generate authorization URL
            import secrets

            state = secrets.token_urlsafe(32)
            auth_url = self.get_authorization_url(redirect_uri=callback_url, state=state)

            # Open browser
            logger.info(f"Opening browser for OAuth authorization: {auth_url}")
            webbrowser.open(auth_url)

            # Wait for callback
            code, returned_state = await result_future

            # Verify state
            if returned_state != state:
                raise ValueError("OAuth state mismatch - possible CSRF attack")

            # Exchange code for token
            credentials = await self.exchange_code_for_token(code, callback_url)

            logger.info("OAuth authorization completed successfully")
            return credentials["access_token"]
        finally:
            await runner.cleanup()

    @classmethod
    async def from_server_url(
        cls,
        server_url: str,
        store: BaseStore | None = None,
        client_name: str = "Universal MCP",
        callback_port: int = 0,
        _pre_discovered: tuple | None = None,
    ) -> "OAuthIntegration":
        """Create an OAuthIntegration by discovering OAuth metadata from a server URL.

        Performs OAuth discovery and dynamic client registration (RFC 7591).

        Args:
            server_url: The MCP server URL to discover OAuth for
            store: Storage backend for tokens
            client_name: Client name for registration
            callback_port: Port for OAuth callback (0 = find free port)
            _pre_discovered: Optional pre-discovered (auth_metadata, prm, www_auth_scope)
                to avoid redundant network requests.

        Returns:
            Configured OAuthIntegration instance
        """
        from mcp.client.auth.utils import get_client_metadata_scopes

        from universal_mcp.integrations.oauth_helpers import (
            StoreTokenStorage,
            discover_oauth_metadata,
            register_oauth_client,
            run_oauth_callback_server,
        )

        # Use pre-discovered metadata or discover fresh
        if _pre_discovered:
            auth_metadata, prm, www_auth_scope = _pre_discovered
        else:
            auth_metadata, prm, www_auth_scope = await discover_oauth_metadata(server_url)

        if not auth_metadata:
            raise ValueError(f"No OAuth metadata found for {server_url}")

        # Determine scopes (WWW-Authenticate scope has highest priority per MCP spec)
        scopes = get_client_metadata_scopes(www_auth_scope, prm, auth_metadata)

        # Start callback server to determine actual port BEFORE registration
        # This ensures the registered redirect_uri matches the actual callback port
        callback_url, actual_port, _, runner = await run_oauth_callback_server(callback_port)
        await runner.cleanup()  # Stop the server; we just needed the port

        redirect_uri = f"http://localhost:{actual_port}/callback"
        client_info = await register_oauth_client(
            auth_metadata=auth_metadata,
            server_url=server_url,
            client_name=client_name,
            redirect_uris=[redirect_uri],
            scopes=scopes,
        )

        # Derive name from server URL
        from urllib.parse import urlparse

        parsed = urlparse(server_url)
        hostname = parsed.hostname or "remote"
        name = hostname.split(".")[0] if hostname else "remote"

        # Create integration
        integration = cls(
            name=name,
            client_id=client_info.client_id or "",
            client_secret=client_info.client_secret or "",
            auth_url=str(auth_metadata.authorization_endpoint),
            token_url=str(auth_metadata.token_endpoint),
            scopes=scopes.split() if isinstance(scopes, str) else (scopes or []),
            store=store,
        )
        integration._server_url = server_url
        integration._registered_redirect_uri = redirect_uri

        # Store client info for future use
        if store:
            token_storage = StoreTokenStorage(store, server_url)
            await token_storage.set_client_info(client_info)

        return integration


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
