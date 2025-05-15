from typing import Any

import httpx
from loguru import logger

from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.stores import BaseStore
from universal_mcp.stores.store import KeyNotFoundError, MemoryStore
from universal_mcp.utils.agentr import AgentrClient


def sanitize_api_key_name(name: str) -> str:
    suffix = "_API_KEY"
    if name.endswith(suffix) or name.endswith(suffix.lower()):
        return name.upper()
    else:
        return f"{name.upper()}{suffix}"


class Integration:
    """Abstract base class for handling application integrations and authentication.

    This class defines the interface for different types of integrations that handle
    authentication and authorization with external services.

    Args:
        name: The name identifier for this integration
        store: Optional Store instance for persisting credentials and other data

    Attributes:
        name: The name identifier for this integration
        store: Store instance for persisting credentials and other data
    """

    def __init__(self, name: str, store: BaseStore | None = None):
        self.name = name
        if store is None:
            self.store = MemoryStore()
        else:
            self.store = store

    def authorize(self) -> str | dict[str, Any]:
        """Authorize the integration.

        Returns:
            Union[str, Dict[str, Any]]: Authorization URL or parameters needed for authorization.

        Raises:
            ValueError: If required configuration is missing.
        """
        pass

    def get_credentials(self) -> dict[str, Any]:
        """Get credentials for the integration.

        Returns:
            Dict[str, Any]: Credentials for the integration.

        Raises:
            NotAuthorizedError: If credentials are not found or invalid.
        """
        credentials = self.store.get(self.name)
        return credentials

    def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Set credentials for the integration.

        Args:
            credentials: Dictionary containing credentials for the integration.

        Raises:
            ValueError: If credentials are invalid or missing required fields.
        """
        self.store.set(self.name, credentials)


class ApiKeyIntegration(Integration):
    """Integration class for API key based authentication.

    This class implements the Integration interface for services that use API key
    authentication. It handles storing and retrieving API keys using the provided
    store.

    Args:
        name: The name identifier for this integration
        store: Optional Store instance for persisting credentials and other data
        **kwargs: Additional keyword arguments passed to parent class

    Attributes:
        name: The name identifier for this integration
        store: Store instance for persisting credentials and other data
    """

    def __init__(self, name: str, store: BaseStore | None = None, **kwargs):
        self.type = "api_key"
        sanitized_name = sanitize_api_key_name(name)
        super().__init__(sanitized_name, store, **kwargs)
        logger.info(f"Initializing API Key Integration: {name} with store: {store}")
        self._api_key: str | None = None

    @property
    def api_key(self) -> str | None:
        if not self._api_key:
            try:
                credentials = self.store.get(self.name)
                self._api_key = credentials
            except KeyNotFoundError as e:
                action = self.authorize()
                raise NotAuthorizedError(action) from e
        return self._api_key

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        """Set the API key.

        Args:
            value: The API key value to set.

        Raises:
            ValueError: If the API key is invalid.
        """
        if value is not None and not isinstance(value, str):
            raise ValueError("API key must be a string")
        self._api_key = value
        if value is not None:
            self.store.set(self.name, value)

    def get_credentials(self) -> dict[str, str]:
        """Get API key credentials.

        Returns:
            Dict[str, str]: Dictionary containing the API key.

        Raises:
            NotAuthorizedError: If API key is not found.
        """
        return {"api_key": self.api_key}

    def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Set API key credentials.

        Args:
            credentials: Dictionary containing the API key.

        Raises:
            ValueError: If credentials are invalid or missing API key.
        """
        if not credentials or not isinstance(credentials, dict):
            raise ValueError("Invalid credentials format")
        self.store.set(self.name, credentials)

    def authorize(self) -> str:
        """Get authorization instructions for API key.

        Returns:
            str: Instructions for setting up API key.
        """
        return f"Please ask the user for api key and set the API Key for {self.name} in the store"


class OAuthIntegration(Integration):
    """Integration class for OAuth based authentication.

    This class implements the Integration interface for services that use OAuth
    authentication. It handles the OAuth flow including authorization, token exchange,
    and token refresh.

    Args:
        name: The name identifier for this integration
        store: Optional Store instance for persisting credentials and other data
        client_id: OAuth client ID
        client_secret: OAuth client secret
        auth_url: OAuth authorization URL
        token_url: OAuth token exchange URL
        scope: OAuth scope string
        **kwargs: Additional keyword arguments passed to parent class

    Attributes:
        name: The name identifier for this integration
        store: Store instance for persisting credentials and other data
        client_id: OAuth client ID
        client_secret: OAuth client secret
        auth_url: OAuth authorization URL
        token_url: OAuth token exchange URL
        scope: OAuth scope string
    """

    def __init__(
        self,
        name: str,
        store: BaseStore | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        auth_url: str | None = None,
        token_url: str | None = None,
        scope: str | None = None,
        **kwargs,
    ):
        super().__init__(name, store, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.scope = scope

    def get_credentials(self) -> dict[str, Any] | None:
        """Get OAuth credentials.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing OAuth tokens if found, None otherwise.
        """
        credentials = self.store.get(self.name)
        if not credentials:
            return None
        return credentials

    def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Set OAuth credentials.

        Args:
            credentials: Dictionary containing OAuth tokens.

        Raises:
            ValueError: If credentials are invalid or missing required tokens.
        """
        if not credentials or not isinstance(credentials, dict):
            raise ValueError("Invalid credentials format")
        if "access_token" not in credentials:
            raise ValueError("Credentials must contain access_token")
        self.store.set(self.name, credentials)

    def authorize(self) -> dict[str, Any]:
        """Get OAuth authorization parameters.

        Returns:
            Dict[str, Any]: Dictionary containing OAuth authorization parameters.

        Raises:
            ValueError: If required OAuth configuration is missing.
        """
        if not all([self.client_id, self.client_secret, self.auth_url, self.token_url]):
            raise ValueError("Missing required OAuth configuration")

        auth_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.scope,
        }

        return {
            "url": self.auth_url,
            "params": auth_params,
            "client_secret": self.client_secret,
            "token_url": self.token_url,
        }

    def handle_callback(self, code: str) -> dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens.

        Args:
            code: Authorization code from OAuth callback.

        Returns:
            Dict[str, Any]: Dictionary containing OAuth tokens.

        Raises:
            ValueError: If required OAuth configuration is missing.
            httpx.HTTPError: If token exchange request fails.
        """
        if not all([self.client_id, self.client_secret, self.token_url]):
            raise ValueError("Missing required OAuth configuration")

        token_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        response = httpx.post(self.token_url, data=token_params)
        response.raise_for_status()
        credentials = response.json()
        self.store.set(self.name, credentials)
        return credentials

    def refresh_token(self) -> dict[str, Any]:
        """Refresh OAuth access token using refresh token.

        Returns:
            Dict[str, Any]: Dictionary containing new OAuth tokens.

        Raises:
            ValueError: If required OAuth configuration is missing.
            httpx.HTTPError: If token refresh request fails.
            KeyError: If refresh token is not found in current credentials.
        """
        if not all([self.client_id, self.client_secret, self.token_url]):
            raise ValueError("Missing required OAuth configuration")

        credentials = self.get_credentials()
        if not credentials or "refresh_token" not in credentials:
            raise KeyError("Refresh token not found in current credentials")

        token_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": credentials["refresh_token"],
        }

        response = httpx.post(self.token_url, data=token_params)
        response.raise_for_status()
        credentials = response.json()
        self.store.set(self.name, credentials)
        return credentials


class AgentRIntegration(Integration):
    """Integration class for AgentR API authentication and authorization.

    This class handles API key authentication and OAuth authorization flow for AgentR services.

    Args:
        name (str): Name of the integration
        api_key (str, optional): AgentR API key. If not provided, will look for AGENTR_API_KEY env var
        **kwargs: Additional keyword arguments passed to parent Integration class

    Raises:
        ValueError: If no API key is provided or found in environment variables
    """

    def __init__(self, name: str, api_key: str = None, **kwargs):
        super().__init__(name, **kwargs)
        self.client = AgentrClient(api_key=api_key)
        self._credentials = None

    def set_credentials(self, credentials: dict | None = None):
        """Set credentials for the integration.

        This method is not implemented for AgentR integration. Instead it redirects to the authorize flow.

        Args:
            credentials (dict | None, optional): Credentials dict (not used). Defaults to None.

        Returns:
            str: Authorization URL from authorize() method
        """
        return self.authorize()

    @property
    def credentials(self):
        """Get credentials for the integration from the AgentR API.

        Makes API request to retrieve stored credentials for this integration.

        Returns:
            dict: Credentials data from API response

        Raises:
            NotAuthorizedError: If credentials are not found (404 response)
            HTTPError: For other API errors
        """
        if self._credentials is not None:
            return self._credentials
        self._credentials = self.client.get_credentials(self.name)
        return self._credentials

    def get_credentials(self):
        """Get credentials for the integration from the AgentR API.

        Makes API request to retrieve stored credentials for this integration.

        Returns:
            dict: Credentials data from API response

        Raises:
            NotAuthorizedError: If credentials are not found (404 response)
            HTTPError: For other API errors
        """
        return self.credentials

    def authorize(self):
        """Get authorization URL for the integration.

        Makes API request to get OAuth authorization URL.

        Returns:
            str: Message containing authorization URL

        Raises:
            HTTPError: If API request fails
        """
        return self.client.get_authorization_url(self.name)
