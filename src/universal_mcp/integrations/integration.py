from typing import Any

import httpx
from loguru import logger

from universal_mcp.exceptions import KeyNotFoundError, NotAuthorizedError
from universal_mcp.stores import BaseStore, MemoryStore
from universal_mcp.utils.agentr import AgentrClient


def sanitize_api_key_name(name: str) -> str:
    suffix = "_API_KEY"
    if name.endswith(suffix) or name.endswith(suffix.lower()):
        return name.upper()
    else:
        return f"{name.upper()}{suffix}"


class Integration:
    """Abstract base class for handling application integrations and authentication.

    This class defines a common interface for various authentication and
    authorization strategies an application might use to connect with
    external services. Subclasses implement specific mechanisms like
    API key handling, OAuth 2.0 flows, or delegation to platforms like AgentR.

    Each integration is associated with a name and can use a `BaseStore`
    instance for persisting credentials or other relevant data.

    Attributes:
        name (str): The unique name identifying this integration instance
                    (e.g., "my_app_api_key", "github_oauth").
        store (BaseStore): The storage backend (e.g., `MemoryStore`,
                       `KeyringStore`) used for persisting credentials.
                       Defaults to `MemoryStore` if not provided.
    """

    def __init__(self, name: str, store: BaseStore | None = None):
        """Initializes the Integration.

        Args:
            name (str): The unique name for this integration instance.
            store (BaseStore | None, optional): A store instance for
                persisting credentials. Defaults to `MemoryStore()`.
        """
        self.name = name
        self.store = store or MemoryStore()

    def authorize(self) -> str | dict[str, Any]:
        """Initiates or provides details for the authorization process.

        The exact behavior and return type of this method depend on the
        specific integration subclass. It might return an authorization URL
        for the user to visit, parameters needed to construct such a URL,
        or instructions on how to manually provide credentials.

        Returns:
            str | dict[str, Any]: Typically, an authorization URL (str) or a
                                  dictionary containing parameters needed for
                                  the authorization flow.

        Raises:
            ValueError: If essential configuration for authorization is missing.
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the authorize method.")

    def get_credentials(self) -> dict[str, Any]:
        """Retrieves the stored credentials for this integration.

        Fetches credentials associated with `self.name` from the `self.store`.

        Returns:
            dict[str, Any]: A dictionary containing the credentials. The structure
                            of this dictionary is specific to the integration type.

        Raises:
            NotAuthorizedError: If credentials are not found in the store
                                or are otherwise invalid/inaccessible.
            KeyNotFoundError: If the key (self.name) is not found in the store.
        """
        try:
            credentials = self.store.get(self.name)
            if credentials is None: # Explicitly check for None if store can return it
                raise NotAuthorizedError(f"No credentials found for {self.name}")
            return credentials
        except KeyNotFoundError as e:
            raise NotAuthorizedError(f"Credentials not found for {self.name}: {e}") from e

    def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Stores the provided credentials for this integration.

        Saves the given credentials dictionary into `self.store` associated
        with `self.name`.

        Args:
            credentials (dict[str, Any]): A dictionary containing the credentials
                to be stored. The required structure depends on the integration.

        Raises:
            ValueError: If the provided credentials are invalid or missing
                        required fields for the specific integration type.
        """
        self.store.set(self.name, credentials)


class ApiKeyIntegration(Integration):
    """Handles integrations that use a simple API key for authentication.

    This class manages storing and retrieving an API key. The key name is
    automatically sanitized (e.g., uppercased and suffixed with `_API_KEY`)
    before being used with the store.

    Attributes:
        name (str): The sanitized name used as the key for storing the API key.
        store (BaseStore): Store for persisting the API key.
        type (str): Set to "api_key".
        _api_key (str | None): Cached API key.
    """

    def __init__(self, name: str, store: BaseStore | None = None, **kwargs):
        """Initializes ApiKeyIntegration.

        The provided `name` is sanitized (e.g., 'mykey' becomes 'MYKEY_API_KEY')
        to form the actual key used for storage.

        Args:
            name (str): The base name for the API key (e.g., "TAVILY").
            store (BaseStore | None, optional): Store for credentials.
                                               Defaults to `MemoryStore()`.
            **kwargs: Additional arguments passed to the parent `Integration`.
        """
        self.type = "api_key"
        sanitized_name = sanitize_api_key_name(name)
        super().__init__(sanitized_name, store, **kwargs)
        logger.info(f"Initializing API Key Integration: {name} with store: {store}")
        self._api_key: str | None = None

    @property
    def api_key(self) -> str: # Changed to str, as it raises if None effectively
        """Retrieves the API key, loading it from the store if necessary.

        If the API key is not already cached in `_api_key`, it attempts
        to load it from `self.store` using `self.name` as the key.

        Returns:
            str: The API key.

        Raises:
            NotAuthorizedError: If the API key is not found in the store.
                                The original `KeyNotFoundError` is chained.
        """
        if not self._api_key:
            try:
                credentials = self.store.get(self.name) # type: ignore
                self._api_key = credentials
            except KeyNotFoundError as e:
                action = self.authorize()
                raise NotAuthorizedError(action) from e
        return self._api_key # type: ignore

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        """Sets and stores the API key.

        Args:
            value (str | None): The API key value. If None, `_api_key` is set
                                to None, but nothing is stored (or cleared from store).
                                Consider if None should clear the store.

        Raises:
            ValueError: If `value` is provided and is not a string.
        """
        if value is not None and not isinstance(value, str):
            raise ValueError("API key must be a string")
        self._api_key = value
        if value is not None:
            self.store.set(self.name, value)

    def get_credentials(self) -> dict[str, str]:
        """Retrieves the API key and returns it in a standard dictionary format.

        Returns:
            dict[str, str]: A dictionary like `{"api_key": "your_api_key_value"}`.

        Raises:
            NotAuthorizedError: If the API key cannot be retrieved.
        """
        return {"api_key": self.api_key}

    def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Sets the API key from a dictionary.

        Expects `credentials` to be a dictionary, typically containing
        an 'api_key' field, but it stores the entire dictionary as is
        under `self.name`. For direct API key setting, use the `api_key` property.

        Args:
            credentials (dict[str, Any]): A dictionary containing the API key
                or related credential information.

        Raises:
            ValueError: If `credentials` is not a dictionary.
        """
        if not credentials or not isinstance(credentials, dict):
            raise ValueError("Invalid credentials format")
        self.store.set(self.name, credentials)

    def authorize(self) -> str:
        """Provides instructions for setting the API key.

        Since API key setup is typically manual, this method returns a
        message guiding the user on how to provide the key.

        Returns:
            str: A message instructing the user to provide the API key
                 for `self.name`.
        """
        return f"Please ask the user for api key and set the API Key for {self.name} in the store"


class OAuthIntegration(Integration):
    """Manages OAuth 2.0 authentication and authorization flows.

    This class implements the necessary steps for an OAuth 2.0 client,
    including generating authorization request parameters, handling the
    redirect callback from the authorization server, exchanging the
    authorization code for access/refresh tokens, and refreshing tokens.

    Attributes:
        name (str): Name of the integration.
        store (BaseStore): Store for OAuth tokens.
        client_id (str | None): The OAuth 2.0 Client ID.
        client_secret (str | None): The OAuth 2.0 Client Secret.
        auth_url (str | None): The authorization server's endpoint URL.
        token_url (str | None): The token server's endpoint URL.
        scope (str | None): The requested OAuth scopes, space-separated.
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
        """Initializes the OAuthIntegration.

        Args:
            name (str): The unique name for this integration instance.
            store (BaseStore | None, optional): Store for credentials.
                                               Defaults to `MemoryStore()`.
            client_id (str | None, optional): The OAuth 2.0 Client ID.
            client_secret (str | None, optional): The OAuth 2.0 Client Secret.
            auth_url (str | None, optional): The authorization server's endpoint URL.
            token_url (str | None, optional): The token server's endpoint URL.
            scope (str | None, optional): The requested OAuth scopes, space-separated.
            **kwargs: Additional arguments passed to the parent `Integration`.
        """
        super().__init__(name, store, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.scope = scope

    def get_credentials(self) -> dict[str, Any] | None:
        """Retrieves stored OAuth tokens for this integration.

        Returns:
            dict[str, Any] | None: A dictionary containing the OAuth tokens
                                  (e.g., `access_token`, `refresh_token`) if found,
                                  otherwise None.
        """
        credentials = self.store.get(self.name)
        if not credentials:
            return None
        return credentials # type: ignore

    def set_credentials(self, credentials: dict[str, Any]) -> None:
        """Stores OAuth tokens for this integration.

        Validates that essential fields like 'access_token' are present.

        Args:
            credentials (dict[str, Any]): A dictionary containing OAuth tokens.
                Must include at least 'access_token'.

        Raises:
            ValueError: If `credentials` is not a dictionary or if 'access_token'
                        is missing.
        """
        if not credentials or not isinstance(credentials, dict):
            raise ValueError("Invalid credentials format")
        if "access_token" not in credentials:
            raise ValueError("Credentials must contain access_token")
        self.store.set(self.name, credentials)

    def authorize(self) -> dict[str, Any]:
        """Constructs parameters required for the OAuth authorization request.

        These parameters are typically used to build the URL to which the
        user must be redirected to grant authorization.

        Returns:
            dict[str, Any]: A dictionary containing the authorization endpoint URL
                            (`url`), query parameters (`params`), client secret,
                            and token URL.

        Raises:
            ValueError: If essential OAuth configuration like `client_id`,
                        `client_secret`, `auth_url`, or `token_url` is missing.
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
        """Handles the OAuth callback by exchanging the authorization code for tokens.

        This method is called after the user authorizes the application and the
        authorization server redirects back with an authorization code.

        Args:
            code (str): The authorization code received from the OAuth server.

        Returns:
            dict[str, Any]: A dictionary containing the access token, refresh token
                            (if any), and other token response data. These are also
                            stored via `set_credentials`.

        Raises:
            ValueError: If essential OAuth configuration is missing.
            httpx.HTTPStatusError: If the token exchange request to `token_url` fails.
        """
        if not all([self.client_id, self.client_secret, self.token_url]): # type: ignore
            raise ValueError("Missing required OAuth configuration")

        token_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        response = httpx.post(self.token_url, data=token_params) # type: ignore
        response.raise_for_status()
        credentials = response.json()
        self.store.set(self.name, credentials)
        return credentials

    def refresh_token(self) -> dict[str, Any]:
        """Refreshes an expired access token using a stored refresh token.

        Returns:
            dict[str, Any]: A dictionary containing the new access token,
                            refresh token, and other token response data.
                            These are also stored.

        Raises:
            ValueError: If essential OAuth configuration is missing.
            KeyError: If a refresh token is not found in the stored credentials.
            httpx.HTTPStatusError: If the token refresh request fails.
        """
        if not all([self.client_id, self.client_secret, self.token_url]): # type: ignore
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

        response = httpx.post(self.token_url, data=token_params) # type: ignore
        response.raise_for_status()
        credentials = response.json()
        self.store.set(self.name, credentials)
        return credentials


class AgentRIntegration(Integration):
    """Manages authentication and authorization via the AgentR platform.

    This integration uses an `AgentrClient` to interact with the AgentR API
    for operations like retrieving authorization URLs and fetching stored
    credentials. It simplifies integration with services supported by AgentR.

    Attributes:
        name (str): Name of the integration (e.g., "github", "google").
        store (BaseStore): Store, typically not used directly by this class
                       as AgentR manages the primary credential storage.
        client (AgentrClient): Client for communicating with the AgentR API.
        _credentials (dict | None): Cached credentials.
    """

    def __init__(self, name: str, api_key: str | None = None, base_url: str | None = None, **kwargs):
        """Initializes the AgentRIntegration.

        Args:
            name (str): The name of the service integration as configured on
                        the AgentR platform (e.g., "github").
            api_key (str | None, optional): The AgentR API key. If not provided,
                                          the `AgentrClient` may attempt to load
                                          it from environment variables.
            base_url (str | None, optional): The base URL for the AgentR API.
                                           Defaults to AgentrClient's default.
            **kwargs: Additional arguments passed to the parent `Integration`.
        """
        super().__init__(name, **kwargs)
        self.client = AgentrClient(api_key=api_key, base_url=base_url)
        self._credentials = None

    def set_credentials(self, credentials: dict | None = None) -> str:
        """Not used for direct credential setting; initiates authorization instead.

        For AgentR integrations, credentials are set via the AgentR platform's
        OAuth flow. This method effectively redirects to the `authorize` flow.

        Args:
            credentials (dict | None, optional): Not used by this implementation.

        Returns:
            str: The authorization URL or message from the `authorize()` method.
        """
        return self.authorize()

    @property
    def credentials(self):
        """Retrieves credentials from the AgentR API, with caching.

        If credentials are not cached locally (in `_credentials`), this property
        fetches them from the AgentR platform using `self.client.get_credentials`.

        Returns:
            dict: The credentials dictionary obtained from AgentR.

        Raises:
            NotAuthorizedError: If credentials are not found (e.g., 404 from AgentR).
            httpx.HTTPStatusError: For other API errors from AgentR.
        """
        if self._credentials is not None:
            return self._credentials
        self._credentials = self.client.get_credentials(self.name)
        return self._credentials

    def get_credentials(self):
        """Retrieves credentials from the AgentR API. Alias for `credentials` property.

        Returns:
            dict: The credentials dictionary obtained from AgentR.

        Raises:
            NotAuthorizedError: If credentials are not found.
            httpx.HTTPStatusError: For other API errors.
        """
        return self.credentials

    def authorize(self) -> str:
        """Retrieves the authorization URL from the AgentR platform.

        This URL should be presented to the user to initiate the OAuth flow
        managed by AgentR for the service associated with `self.name`.

        Returns:
            str: The authorization URL.

        Raises:
            httpx.HTTPStatusError: If the API request to AgentR fails.
        """
        return self.client.get_authorization_url(self.name)
