from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from universal_mcp.connections.connection import (
    ApiKeyConnection,
    Connection,
    OAuthConnection,
)


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

    Integrations are pure data/logic objects with no store reference.
    The SDK (UniversalMCP) owns persistence.

    Attributes:
        name (str): The unique name identifying this integration
        type (str): Integration type (api_key, oauth2, etc.)
    """

    def __init__(self, name: str):
        """Initializes the Integration.

        Args:
            name: The unique name/identifier for this integration
        """
        self.name = self._sanitize_key_name(name)
        self.type: str = "base"

        # Create default connection for backward compatibility
        self._default_connection: Connection | None = None

    @abstractmethod
    def create_connection(self, user_id: str | None = None) -> Connection:
        """Create a new Connection instance for a user.

        Args:
            user_id: User identifier (defaults to "default")

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
            self._default_connection = self.create_connection(user_id="default")
        return self._default_connection

    def get_connection(self, user_id: str | None = None) -> Connection:
        """Get a connection for the given user.

        For the default user (None or "default"), returns the cached default
        connection. For other users, creates a new connection each time.

        Args:
            user_id: User identifier. None or "default" returns the default connection.

        Returns:
            Connection instance for the user
        """
        if user_id is None or user_id == "default":
            return self.get_default_connection()
        return self.create_connection(user_id=user_id)

    # FACADE METHODS - For backward compatibility

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
    stored in Connection instances (in memory).

    Attributes:
        name (str): The sanitized name (e.g., "GITHUB_API_KEY")
        type (str): Set to "api_key"
    """

    def __init__(self, name: str, **kwargs):
        """Initializes ApiKeyIntegration.

        The provided `name` is sanitized (e.g., 'github' becomes 'GITHUB_API_KEY')
        to form the actual key used for storage.

        Args:
            name: The base name for the API key (e.g., "TAVILY")
            **kwargs: Additional arguments (for future extensibility)
        """
        super().__init__(name)
        self.type = "api_key"
        logger.info(f"Initializing API Key Integration: {name}")

    def create_connection(self, user_id: str | None = None) -> Connection:
        """Create API key connection.

        Args:
            user_id: User identifier (defaults to "default")

        Returns:
            New ApiKeyConnection instance
        """
        return ApiKeyConnection(
            integration_name=self.name,
            user_id=user_id or "default",
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
    ):
        """Initialize OAuth integration.

        Args:
            name: Integration name
            client_id: OAuth client ID (shared config)
            client_secret: OAuth client secret (shared config)
            auth_url: Authorization endpoint
            token_url: Token endpoint
            scopes: OAuth scopes (defaults to empty list)
        """
        # Don't sanitize name for OAuth - use raw name
        # Override parent's __init__ to skip _sanitize_key_name
        self.name = name.upper().replace("-", "_").replace(" ", "_")
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
        self._ngrok_tunnel = None  # Active ngrok tunnel (set by from_server_url with use_ngrok)
        self._callback_port = 0  # Local port for OAuth callback (set by from_server_url)

    def create_connection(self, user_id: str | None = None) -> Connection:
        """Create OAuth connection.

        Args:
            user_id: User identifier (defaults to "default")

        Returns:
            New OAuthConnection instance
        """
        return OAuthConnection(
            integration_name=self.name,
            user_id=user_id or "default",
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

        Stores the resulting credentials in-memory on the default connection.
        The SDK is responsible for persisting to a store if needed.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token credentials dictionary with access_token, refresh_token, etc.
        """
        import httpx

        logger.debug(f"exchange_code_for_token: token_url={self.token_url}, redirect_uri={redirect_uri}, has_pkce={self._pkce is not None}")

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
            logger.debug(f"POSTing to token endpoint: {self.token_url}")
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            logger.debug(f"Token endpoint response: status={response.status_code}")
            if response.status_code != 200:
                logger.error(f"Token exchange failed: status={response.status_code}, body={response.text[:500]}")
            response.raise_for_status()
            token_data = response.json()

        # Store tokens in-memory via connection
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
        logger.info(f"Token exchange successful: access_token={credentials['access_token'][:8]}..., has_refresh={credentials['refresh_token'] is not None}")

        self._pkce = None  # Clear PKCE after use
        return credentials

    async def run_oauth_flow(self, callback_port: int = 0, timeout: int = 300) -> str:
        """Run the full interactive OAuth authorization flow.

        Opens the browser for authorization, starts a local callback server,
        waits for the callback, and exchanges the code for tokens.

        If a redirect_uri was registered during from_server_url(), the callback
        server binds to the same port for consistency. If an ngrok tunnel was
        created during from_server_url(), the callback server reuses the same
        port so the tunnel continues to forward traffic correctly.

        Args:
            callback_port: Port for callback server (0 = find free port)
            timeout: Seconds to wait for the OAuth callback (default 300s / 5min)

        Returns:
            Access token string
        """
        import asyncio
        import webbrowser
        from urllib.parse import urlparse

        from universal_mcp.integrations.oauth_helpers import run_oauth_callback_server, stop_ngrok_tunnel

        has_ngrok = self._ngrok_tunnel is not None
        logger.debug(
            f"run_oauth_flow: callback_port={callback_port}, has_ngrok={has_ngrok}, "
            f"_registered_redirect_uri={self._registered_redirect_uri}, _callback_port={self._callback_port}"
        )

        # Use the stored callback port for consistency.
        # When ngrok is active, _registered_redirect_uri is the ngrok URL (port 443),
        # so we use _callback_port which holds the actual local port.
        if callback_port == 0:
            if has_ngrok and self._callback_port:
                callback_port = self._callback_port
                logger.debug(f"Using ngrok local port: {callback_port}")
            elif self._registered_redirect_uri:
                parsed = urlparse(self._registered_redirect_uri)
                if parsed.port:
                    callback_port = parsed.port
                    logger.debug(f"Using redirect URI port: {callback_port}")

        # Start callback server. Don't start a new ngrok tunnel - reuse the
        # one from from_server_url() which is still forwarding to this port.
        logger.debug(f"Starting OAuth callback server on port {callback_port}...")
        (
            _callback_url,
            actual_port,
            result_future,
            runner,
            _,
        ) = await run_oauth_callback_server(callback_port, use_ngrok=False)

        # Use the registered redirect URI (which may be an ngrok URL) as the callback URL
        callback_url = self._registered_redirect_uri or _callback_url
        logger.debug(f"Callback server started: actual_port={actual_port}, callback_url={callback_url}")

        try:
            logger.info(f"OAuth callback server started on port {actual_port}")
            if has_ngrok:
                logger.info(f"ngrok tunnel active, callback URL: {callback_url}")

            # Generate authorization URL
            import secrets

            state = secrets.token_urlsafe(32)
            auth_url = self.get_authorization_url(redirect_uri=callback_url, state=state)

            # Open browser (or print URL for remote machines)
            logger.info(f"Opening browser for OAuth authorization: {auth_url}")
            if has_ngrok:
                # On remote machines, the browser may not be available
                print(f"\nOpen this URL in your browser to authorize:\n{auth_url}\n")
                import contextlib

                with contextlib.suppress(Exception):
                    webbrowser.open(auth_url)
            else:
                webbrowser.open(auth_url)

            # Wait for callback with timeout
            logger.debug(f"Waiting for OAuth callback (timeout={timeout}s)...")
            try:
                code, returned_state = await asyncio.wait_for(result_future, timeout=timeout)
            except TimeoutError:
                logger.error(f"OAuth callback timed out after {timeout}s. The authorization server may not have redirected to {callback_url}")
                raise TimeoutError(
                    f"OAuth callback not received within {timeout}s. "
                    f"Expected redirect to: {callback_url}"
                ) from None
            logger.debug(f"OAuth callback received: code={code[:8]}..., state_match={returned_state == state}")

            # Verify state
            if returned_state != state:
                logger.error(f"OAuth state mismatch: expected={state[:8]}..., got={returned_state[:8] if returned_state else 'None'}...")
                raise ValueError("OAuth state mismatch - possible CSRF attack")

            # Exchange code for token
            credentials = await self.exchange_code_for_token(code, callback_url)

            logger.info("OAuth authorization completed successfully")
            return credentials["access_token"]
        finally:
            logger.debug("Cleaning up OAuth callback server...")
            await runner.cleanup()
            # Clean up ngrok tunnel after flow completes
            if has_ngrok and self._ngrok_tunnel:
                logger.debug("Stopping ngrok tunnel...")
                stop_ngrok_tunnel(self._ngrok_tunnel)
                self._ngrok_tunnel = None

    @classmethod
    async def from_server_url(
        cls,
        server_url: str,
        client_info: Any | None = None,
        client_name: str = "Universal MCP",
        redirect_url: str | None = None,
        callback_port: int = 0,
        _pre_discovered: tuple | None = None,
        use_ngrok: bool = False,
    ) -> tuple["OAuthIntegration", Any | None]:
        """Create an OAuthIntegration by discovering OAuth metadata from a server URL.

        Performs OAuth discovery and dynamic client registration (RFC 7591).
        The caller (SDK) is responsible for loading/saving client_info from/to a store.

        Args:
            server_url: The MCP server URL to discover OAuth for
            client_info: Pre-loaded OAuthClientInformationFull (from SDK's store).
                If None, a new client will be registered.
            client_name: Client name for registration
            redirect_url: Explicit redirect URL override
            callback_port: Port for OAuth callback (0 = find free port)
            _pre_discovered: Optional pre-discovered (auth_metadata, prm, www_auth_scope)
                to avoid redundant network requests.
            use_ngrok: If True, use ngrok to create a public tunnel for OAuth callbacks.

        Returns:
            Tuple of (OAuthIntegration, new_client_info_or_None).
            The second element is non-None only when a NEW client was registered,
            signaling the SDK to persist it.
        """
        from mcp.client.auth.utils import get_client_metadata_scopes

        from universal_mcp.integrations.oauth_helpers import (
            register_oauth_client,
            run_oauth_callback_server,
        )

        logger.debug(
            f"from_server_url: server_url={server_url}, has_client_info={client_info is not None}, "
            f"use_ngrok={use_ngrok}, has_pre_discovered={_pre_discovered is not None}"
        )

        # Use pre-discovered metadata or discover fresh
        if _pre_discovered:
            auth_metadata, prm, www_auth_scope = _pre_discovered
            logger.debug("Using pre-discovered OAuth metadata")
        else:
            from universal_mcp.integrations.oauth_helpers import discover_oauth_metadata

            logger.debug("Discovering OAuth metadata fresh...")
            auth_metadata, prm, www_auth_scope = await discover_oauth_metadata(server_url)

        if not auth_metadata:
            raise ValueError(f"No OAuth metadata found for {server_url}")

        logger.debug(
            f"OAuth metadata: auth_endpoint={auth_metadata.authorization_endpoint}, "
            f"token_endpoint={auth_metadata.token_endpoint}, "
            f"registration_endpoint={getattr(auth_metadata, 'registration_endpoint', 'N/A')}"
        )

        # Determine scopes (WWW-Authenticate scope has highest priority per MCP spec)
        scopes = get_client_metadata_scopes(www_auth_scope, prm, auth_metadata)
        logger.debug(f"Determined scopes: {scopes!r}")

        redirect_uri = redirect_url
        ngrok_tunnel = None
        ngrok_local_port = 0
        new_client_info = None  # Track if we registered a new client

        # When using ngrok, always start a tunnel for the redirect_uri
        # (even when reusing client_info, since ngrok URLs are ephemeral)
        if use_ngrok and not redirect_uri:
            logger.debug("use_ngrok=True, starting ngrok tunnel for redirect_uri...")
            callback_url, actual_port, _, runner, tunnel = await run_oauth_callback_server(
                callback_port, use_ngrok=True
            )
            redirect_uri = callback_url
            ngrok_local_port = actual_port
            if tunnel:
                ngrok_tunnel = tunnel
            await runner.cleanup()  # Stop the HTTP server; ngrok tunnel stays alive
            logger.debug(f"ngrok tunnel started: redirect_uri={redirect_uri}, local_port={ngrok_local_port}")
        elif not client_info and not redirect_uri:
            # No existing registration and no ngrok - probe for a local port
            logger.debug("No client_info and no ngrok, probing for local port...")
            callback_url, actual_port, _, runner, _ = await run_oauth_callback_server(callback_port)
            await runner.cleanup()
            redirect_uri = f"http://localhost:{actual_port}/callback"
            logger.debug(f"Local redirect_uri: {redirect_uri}")
        elif client_info and not redirect_uri:
            # Reuse redirect_uri from stored client_info
            if client_info.redirect_uris:
                redirect_uri = str(client_info.redirect_uris[0])
                logger.debug(f"Reusing stored redirect_uri: {redirect_uri}")

        if not client_info:
            logger.debug(f"Registering new OAuth client: redirect_uris=[{redirect_uri}], scopes={scopes}")
            client_info = await register_oauth_client(
                auth_metadata=auth_metadata,
                server_url=server_url,
                client_name=client_name,
                redirect_uris=[redirect_uri],
                scopes=scopes,
            )
            new_client_info = client_info  # Signal SDK to persist
            logger.info(f"Registered new OAuth client: client_id={client_info.client_id}")

        # Derive name from server URL
        from urllib.parse import urlparse

        parsed = urlparse(server_url)
        hostname = parsed.hostname or "remote"
        # Usually its mcp.linear.com/mcp or mcp.notion.com/mcp anyways.com will most probably be true hence -2
        name = hostname.split(".")[-2].lower() if hostname else "remote"

        # Create integration
        integration = cls(
            name=name,
            client_id=client_info.client_id or "",
            client_secret=client_info.client_secret or "",
            auth_url=str(auth_metadata.authorization_endpoint),
            token_url=str(auth_metadata.token_endpoint),
            scopes=scopes.split() if isinstance(scopes, str) else (scopes or []),
        )
        integration._server_url = server_url
        integration._registered_redirect_uri = redirect_uri
        integration._ngrok_tunnel = ngrok_tunnel  # None unless use_ngrok=True
        integration._callback_port = ngrok_local_port  # Local port for ngrok tunnel

        logger.debug(
            f"from_server_url complete: name={name}, client_id={client_info.client_id}, "
            f"redirect_uri={redirect_uri}, ngrok={'active' if ngrok_tunnel else 'inactive'}, "
            f"new_registration={new_client_info is not None}"
        )
        return integration, new_client_info


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
        # Silently ignore store kwarg for backward compatibility
        kwargs.pop("store", None)

        if integration_type == "api_key":
            return ApiKeyIntegration(app_name, **kwargs)
        elif integration_type == "oauth2":
            # OAuth requires additional parameters
            return OAuthIntegration(app_name, **kwargs)
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")
