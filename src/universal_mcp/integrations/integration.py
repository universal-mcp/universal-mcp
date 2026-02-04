from typing import Any

from loguru import logger

from universal_mcp.exceptions import KeyNotFoundError, NotAuthorizedError
from universal_mcp.stores import BaseStore, MemoryStore


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
    API key handling.

    Each integration is associated with a name and can use a `BaseStore`
    instance for persisting credentials or other relevant data.

    Attributes:
        name (str): The unique name identifying this integration instance
                    (e.g., "my_app_api_key").
        store (BaseStore): The storage backend (e.g., `MemoryStore`,
                       `KeyringStore`) used for persisting credentials.
                       Defaults to `MemoryStore` if not provided.
    """

    def __init__(self, name: str, store: BaseStore | None = None):
        """Initializes the Integration.

        Args:
            name (str): The unique name/identifier for this integration instance.
            store (BaseStore | None, optional): A store instance for
                persisting credentials. Defaults to `MemoryStore()`.
        """
        self.name = name
        self.store = store or MemoryStore()
        self.type = ""

    def authorize(self) -> str:
        """Provides instructions for the authorization process.

        Returns a human-readable instruction string for the user on how to
        authorize this integration.

        Returns:
            str: Instruction message for the user.
        """
        return f"Please authorize {self.name} before using this integration."

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
            if credentials is None:  # Explicitly check for None if store can return it
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

    def __str__(self) -> str:
        return f"Integration(name={self.name}, type={self.type})"

    def __repr__(self) -> str:
        return self.__str__()


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
    def api_key(self) -> str:  # Changed to str, as it raises if None effectively
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
                credentials = self.store.get(self.name)  # type: ignore
                self._api_key = credentials
            except KeyNotFoundError as e:
                action = self.authorize()
                raise NotAuthorizedError(action) from e
        return self._api_key  # type: ignore

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


class IntegrationFactory:
    """A factory for creating integration instances."""

    @staticmethod
    def create(app_name: str, integration_type: str = "api_key", **kwargs) -> "Integration":
        """Create an integration instance."""
        if integration_type == "api_key":
            return ApiKeyIntegration(app_name, **kwargs)
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")
