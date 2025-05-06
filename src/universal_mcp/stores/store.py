import os
from abc import ABC, abstractmethod
from typing import Any

import keyring
from loguru import logger

from universal_mcp.exceptions import KeyNotFoundError, StoreError


class BaseStore(ABC):
    """
    Abstract base class defining the interface for credential stores.
    All credential stores must implement get, set and delete methods.
    """

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        Retrieve a value from the store by key.

        Args:
            key (str): The key to look up

        Returns:
            Any: The stored value

        Raises:
            KeyNotFoundError: If the key is not found in the store
            StoreError: If there is an error accessing the store
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        """
        Store a value in the store with the given key.

        Args:
            key (str): The key to store the value under
            value (str): The value to store

        Raises:
            StoreError: If there is an error storing the value
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a value from the store by key.

        Args:
            key (str): The key to delete

        Raises:
            KeyNotFoundError: If the key is not found in the store
            StoreError: If there is an error deleting the value
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return self.__repr__()


class MemoryStore(BaseStore):
    """
    In-memory credential store implementation.
    Stores credentials in a dictionary that persists only for the duration of the program execution.
    """

    def __init__(self):
        """Initialize an empty dictionary to store the data."""
        self.data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        """
        Retrieve a value from the in-memory store by key.

        Args:
            key (str): The key to look up

        Returns:
            Any: The stored value

        Raises:
            KeyNotFoundError: If the key is not found in the store
        """
        if key not in self.data:
            raise KeyNotFoundError(f"Key '{key}' not found in memory store")
        return self.data[key]

    def set(self, key: str, value: str) -> None:
        """
        Store a value in the in-memory store with the given key.

        Args:
            key (str): The key to store the value under
            value (str): The value to store
        """
        self.data[key] = value

    def delete(self, key: str) -> None:
        """
        Delete a value from the in-memory store by key.

        Args:
            key (str): The key to delete

        Raises:
            KeyNotFoundError: If the key is not found in the store
        """
        if key not in self.data:
            raise KeyNotFoundError(f"Key '{key}' not found in memory store")
        del self.data[key]


class EnvironmentStore(BaseStore):
    """
    Environment variable-based credential store implementation.
    Uses OS environment variables to store and retrieve credentials.
    """

    def get(self, key: str) -> Any:
        """
        Retrieve a value from environment variables by key.

        Args:
            key (str): The environment variable name to look up

        Returns:
            Any: The stored value

        Raises:
            KeyNotFoundError: If the environment variable is not found
        """
        value = os.getenv(key)
        if value is None:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        return value

    def set(self, key: str, value: str) -> None:
        """
        Set an environment variable.

        Args:
            key (str): The environment variable name
            value (str): The value to set
        """
        os.environ[key] = value

    def delete(self, key: str) -> None:
        """
        Delete an environment variable.

        Args:
            key (str): The environment variable name to delete

        Raises:
            KeyNotFoundError: If the environment variable is not found
        """
        if key not in os.environ:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        del os.environ[key]


class KeyringStore(BaseStore):
    """
    System keyring-based credential store implementation.
    Uses the system's secure credential storage facility via the keyring library.
    """

    def __init__(self, app_name: str = "universal_mcp"):
        """
        Initialize the keyring store.

        Args:
            app_name (str): The application name to use in keyring, defaults to "universal_mcp"
        """
        self.app_name = app_name

    def get(self, key: str) -> Any:
        """
        Retrieve a password from the system keyring.

        Args:
            key (str): The key to look up

        Returns:
            Any: The stored value

        Raises:
            KeyNotFoundError: If the key is not found in the keyring
            StoreError: If there is an error accessing the keyring
        """
        try:
            logger.info(f"Getting password for {key} from keyring")
            value = keyring.get_password(self.app_name, key)
            if value is None:
                raise KeyNotFoundError(f"Key '{key}' not found in keyring")
            return value
        except Exception as e:
            raise KeyNotFoundError(f"Key '{key}' not found in keyring") from e

    def set(self, key: str, value: str) -> None:
        """
        Store a password in the system keyring.

        Args:
            key (str): The key to store the password under
            value (str): The password to store

        Raises:
            StoreError: If there is an error storing in the keyring
        """
        try:
            logger.info(f"Setting password for {key} in keyring")
            keyring.set_password(self.app_name, key, value)
        except Exception as e:
            raise StoreError(f"Error storing in keyring: {str(e)}") from e

    def delete(self, key: str) -> None:
        """
        Delete a password from the system keyring.

        Args:
            key (str): The key to delete

        Raises:
            KeyNotFoundError: If the key is not found in the keyring
            StoreError: If there is an error deleting from the keyring
        """
        try:
            logger.info(f"Deleting password for {key} from keyring")
            keyring.delete_password(self.app_name, key)
        except Exception as e:
            raise KeyNotFoundError(f"Key '{key}' not found in keyring") from e
