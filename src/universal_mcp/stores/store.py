import os
from abc import ABC, abstractmethod
from typing import Any

import keyring
from loguru import logger

from universal_mcp.exceptions import KeyNotFoundError, StoreError


class BaseStore(ABC):
    """Abstract base class defining a common interface for credential stores.

    This class outlines the essential methods (`get`, `set`, `delete`)
    that all concrete store implementations must provide. It ensures a
    consistent API for managing sensitive data across various storage
    backends like in-memory dictionaries, environment variables, or
    system keyrings.
    """

    @abstractmethod
    def get(self, key: str) -> Any:
        """Retrieve data from the store.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyNotFoundError: If the specified key is not found in the store.
            StoreError: For other store-related operational errors.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set or update a key-value pair in the store.

        If the key already exists, its value should be updated. If the key
        does not exist, it should be created.

        Args:
            key (str): The key to set or update.
            value (Any): The value to associate with the key.

        Raises:
            StoreError: For store-related operational errors (e.g., write failures).
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key-value pair from the store.

        Args:
            key (str): The key to delete.

        Raises:
            KeyNotFoundError: If the specified key is not found in the store.
            StoreError: For other store-related operational errors (e.g., delete failures).
        """
        pass

    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the store instance."""
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """Returns a human-readable string representation of the store instance."""
        return self.__repr__()


class MemoryStore(BaseStore):
    """In-memory credential and data store using a Python dictionary.

    This store implementation holds all data within a dictionary in memory.
    It is simple and fast but is not persistent; all stored data will be
    lost when the application process terminates. Primarily useful for
    testing, transient data, or development scenarios where persistence
    is not required.

    Attributes:
        data (dict[str, Any]): The dictionary holding the stored key-value pairs.
    """

    def __init__(self):
        """Initializes the MemoryStore with an empty dictionary."""
        self.data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        """Retrieves the value associated with the given key from the in-memory store.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
        """
        if key not in self.data:
            raise KeyNotFoundError(f"Key '{key}' not found in memory store")
        return self.data[key]

    def set(self, key: str, value: Any) -> None:
        """Sets or updates the value for a given key in the in-memory store.

        Args:
            key (str): The key to set or update.
            value (Any): The value to associate with the key.
        """
        self.data[key] = value  # type: ignore

    def delete(self, key: str) -> None:
        """Deletes a key-value pair from the in-memory store.

        Args:
            key (str): The key to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
        """
        if key not in self.data:
            raise KeyNotFoundError(f"Key '{key}' not found in memory store")
        del self.data[key]


class EnvironmentStore(BaseStore):
    """Credential and data store using operating system environment variables.

    This store implementation interacts directly with environment variables
    using `os.getenv`, `os.environ[]`, and `del os.environ[]`.
    Changes made via `set` or `delete` will affect the environment of the
    current Python process and potentially its subprocesses, but typically
    do not persist beyond the life of the parent shell or system session
    unless explicitly managed externally.
    """

    def get(self, key: str) -> Any:
        """Retrieves the value of an environment variable.

        Args:
            key (str): The name of the environment variable.

        Returns:
            Any: The value of the environment variable as a string.

        Raises:
            KeyNotFoundError: If the environment variable is not set.
        """
        value = os.getenv(key)
        if value is None:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        return value

    def set(self, key: str, value: Any) -> None:
        """Sets an environment variable in the current process.

        Args:
            key (str): The name of the environment variable.
            value (Any): The value to set for the environment variable.
                         It will be converted to a string.
        """
        os.environ[key] = str(value)

    def delete(self, key: str) -> None:
        """Deletes an environment variable from the current process.

        Args:
            key (str): The name of the environment variable to delete.

        Raises:
            KeyNotFoundError: If the environment variable is not set.
        """
        if key not in os.environ:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        del os.environ[key]


class KeyringStore(BaseStore):
    """Secure credential store using the system's keyring service.

    This store leverages the `keyring` library to interact with the
    operating system's native secure credential management system
    (e.g., macOS Keychain, Windows Credential Manager, Freedesktop Secret
    Service / KWallet on Linux). It is suitable for storing sensitive
    data like API keys and passwords persistently and securely.

    Attributes:
        app_name (str): The service name under which credentials are stored
                        in the system keyring. This helps namespace credentials
                        for different applications.
    """

    def __init__(self, app_name: str = "universal_mcp"):
        """Initializes the KeyringStore.

        Args:
            app_name (str, optional): The service name to use when interacting
                with the system keyring. This helps to namespace credentials.
                Defaults to "universal_mcp".
        """
        self.app_name = app_name

    def get(self, key: str) -> str:
        """Retrieves a secret (password) from the system keyring.

        Args:
            key (str): The username or key associated with the secret.

        Returns:
            str: The stored secret string.

        Raises:
            KeyNotFoundError: If the key is not found in the keyring under
                              `self.app_name`, or if `keyring` library errors occur.
        """
        try:
            logger.info(f"Getting password for {key} from keyring for app {self.app_name}")
            value = keyring.get_password(self.app_name, key)
            if value is None:
                raise KeyNotFoundError(f"Key '{key}' not found in keyring for app '{self.app_name}'")
            return value
        except Exception as e:  # Catches keyring specific errors too
            # Log the original exception e if needed
            raise KeyNotFoundError(
                f"Failed to retrieve key '{key}' from keyring for app '{self.app_name}'. Original error: {type(e).__name__}"
            ) from e  # Keep original exception context

    def set(self, key: str, value: Any) -> None:
        """Stores a secret (password) in the system keyring.

        Args:
            key (str): The username or key to associate with the secret.
            value (Any): The secret to store. It will be converted to a string.

        Raises:
            StoreError: If storing the secret in the keyring fails.
        """
        try:
            logger.info(f"Setting password for {key} in keyring for app {self.app_name}")
            keyring.set_password(self.app_name, key, str(value))
        except Exception as e:
            raise StoreError(f"Error storing key '{key}' in keyring for app '{self.app_name}': {str(e)}") from e

    def delete(self, key: str) -> None:
        """Deletes a secret (password) from the system keyring.

        Args:
            key (str): The username or key of the secret to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the keyring (note: some
                              keyring backends might not raise an error for
                              non-existent keys, this tries to standardize).
            StoreError: If deleting the secret from the keyring fails for other
                        reasons.
        """
        try:
            logger.info(f"Deleting password for {key} from keyring for app {self.app_name}")
            # Attempt to get first to see if it exists, as delete might not error
            # This is a workaround for keyring's inconsistent behavior
            existing_value = keyring.get_password(self.app_name, key)
            if existing_value is None:
                raise KeyNotFoundError(f"Key '{key}' not found in keyring for app '{self.app_name}', cannot delete.")
            keyring.delete_password(self.app_name, key)
        except KeyNotFoundError:  # Re-raise if found by the get_password check
            raise
        except Exception as e:  # Catch other keyring errors
            raise StoreError(f"Error deleting key '{key}' from keyring for app '{self.app_name}': {str(e)}") from e
