"""Per-user credential instances for Integrations.

Separates user-specific credentials (tokens, keys) from shared integration
configuration (OAuth client settings, endpoints).

All operations are async for non-blocking I/O.
"""

from abc import ABC, abstractmethod
from typing import Any

from universal_mcp.exceptions import NotAuthorizedError


class Connection(ABC):
    """Per-user credential instance for an Integration (async-only).

    Represents a single user's connection to an integration. While an Integration
    defines HOW to connect (client configuration, endpoints), a Connection holds
    WHAT credentials to use (access tokens, API keys).

    This separation enables:
    - Multi-user support: Multiple connections per integration
    - OAuth support: Client config separate from user tokens
    - Proper state management: Mutable credentials separate from immutable config

    All credential operations are async for non-blocking I/O.
    """

    def __init__(
        self,
        integration_name: str,
        user_id: str | None = None,
        store: Any | None = None,
    ):
        """Initialize a Connection.

        Args:
            integration_name: Name of the integration this connection uses
            user_id: User identifier (defaults to "default" for single-user scenarios)
            store: Storage backend (py-key-value store instance)
        """
        self.integration_name = integration_name
        self.user_id = user_id or "default"
        self.store = store
        self._status = "pending"  # pending, active, expired, revoked

    @abstractmethod
    async def get_credentials(self) -> dict[str, Any]:
        """Retrieve user-specific credentials asynchronously.

        Returns:
            Dictionary containing credentials (structure depends on auth type)

        Raises:
            NotAuthorizedError: If credentials are not found or invalid
        """
        pass

    @abstractmethod
    async def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Store user-specific credentials asynchronously.

        Args:
            credentials: Dictionary containing credentials to store
        """
        pass

    @property
    def store_key(self) -> str:
        """Generate unique key for this connection's credentials.

        Format: connection::{integration_name}::{user_id}
        Example: "connection::GITHUB_API_KEY::user_123"

        Returns:
            Unique store key for this connection
        """
        return f"connection::{self.integration_name}::{self.user_id}"

    @property
    def status(self) -> str:
        """Get connection status.

        Returns:
            Status string (pending, active, expired, revoked)
        """
        return self._status

    def mark_active(self) -> None:
        """Mark connection as active."""
        self._status = "active"

    def mark_expired(self) -> None:
        """Mark connection as expired."""
        self._status = "expired"


class ApiKeyConnection(Connection):
    """Connection for API key authentication (async-only).

    Manages a single user's API key for an integration.
    All operations are async for non-blocking I/O.
    """

    def __init__(self, *args, **kwargs):
        """Initialize API key connection."""
        super().__init__(*args, **kwargs)
        self._api_key_cache: str | None = None

    async def get_credentials(self) -> dict[str, Any]:
        """Get API key from store asynchronously.

        Returns:
            Dictionary containing api_key or full credentials dict

        Raises:
            NotAuthorizedError: If no store configured or key not found
        """
        if not self.store:
            raise NotAuthorizedError("No store configured")

        try:
            value = await self.store.get(self.store_key)
        except KeyError:
            raise NotAuthorizedError(f"No API key found for {self.integration_name}")

        if not value:
            raise NotAuthorizedError(f"No API key found for {self.integration_name}")

        self.mark_active()

        # If value is already a dict (full credentials), return as-is
        if isinstance(value, dict):
            return value

        # Otherwise, wrap string API key in standard format
        return {"api_key": value}

    async def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Store API key asynchronously.

        Args:
            credentials: Dictionary containing api_key or full credentials dict

        Raises:
            ValueError: If credentials is invalid or api_key not found
        """
        if not isinstance(credentials, dict):
            raise ValueError("Credentials must be a dictionary")

        # Always store as a dict (py-key-value requires Mapping type)
        if not self.store:
            raise ValueError("No store configured")

        await self.store.put(self.store_key, credentials)

        # Cache API key if present
        if "api_key" in credentials:
            self._api_key_cache = credentials["api_key"]

        self.mark_active()

    async def get_api_key(self) -> str:
        """Get API key string asynchronously.

        Convenience method that extracts just the key value.

        Returns:
            The API key string

        Raises:
            NotAuthorizedError: If API key not found
        """
        if not self._api_key_cache:
            creds = await self.get_credentials()
            self._api_key_cache = creds.get("api_key")
        return self._api_key_cache  # type: ignore

    async def set_api_key(self, value: str) -> None:
        """Set API key asynchronously (convenience method).

        Args:
            value: API key string
        """
        await self.set_credentials({"api_key": value})


class OAuthConnection(Connection):
    """Connection for OAuth 2.0 authentication (async-only).

    Manages OAuth tokens (access, refresh) for a single user.
    The OAuth client configuration (client_id, client_secret, endpoints)
    lives in the Integration, not here.

    All operations are async for non-blocking I/O.
    """

    def __init__(self, *args, **kwargs):
        """Initialize OAuth connection."""
        super().__init__(*args, **kwargs)
        self._token_cache: dict[str, Any] | None = None

    async def get_credentials(self) -> dict[str, Any]:
        """Get OAuth tokens from store asynchronously.

        Returns:
            Dictionary containing access_token, refresh_token, expires_at, etc.

        Raises:
            NotAuthorizedError: If no store configured or tokens not found
        """
        if not self.store:
            raise NotAuthorizedError("No store configured")

        # py-key-value may return None or raise KeyError for missing keys
        try:
            value = await self.store.get(self.store_key)
        except KeyError as e:
            raise NotAuthorizedError(f"No OAuth token found for {self.integration_name}") from e

        if not value or not isinstance(value, dict):
            raise NotAuthorizedError(f"No OAuth token found for {self.integration_name}")

        # TODO: Check token expiration, refresh if needed
        self.mark_active()
        return value  # {"access_token": "...", "refresh_token": "...", "expires_at": ...}

    async def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Store OAuth tokens asynchronously.

        Args:
            credentials: Dictionary containing at minimum access_token

        Raises:
            ValueError: If required fields missing
        """
        required_fields = ["access_token"]
        if not all(k in credentials for k in required_fields):
            raise ValueError("OAuth credentials require access_token")

        if self.store:
            await self.store.put(self.store_key, credentials)
        self._token_cache = credentials
        self.mark_active()
