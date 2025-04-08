import os
from abc import ABC, abstractmethod

import keyring
from loguru import logger


class Store(ABC):
    """
    Abstract base class defining the interface for credential stores.
    All credential stores must implement get, set and delete methods.
    """

    @abstractmethod
    def get(self, key: str):
        """
        Retrieve a value from the store by key.

        Args:
            key (str): The key to look up

        Returns:
            The stored value if found, None otherwise
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        """
        Store a value in the store with the given key.

        Args:
            key (str): The key to store the value under
            value (str): The value to store
        """
        pass

    @abstractmethod
    def delete(self, key: str):
        """
        Delete a value from the store by key.

        Args:
            key (str): The key to delete
        """
        pass


class MemoryStore:
    """
    Acts as credential store for the applications.
    Responsible for storing and retrieving credentials.
    Ideally should be a key value store that keeps data in memory.
    """

    def __init__(self):
        """Initialize an empty dictionary to store the data."""
        self.data = {}

    def get(self, key: str):
        """
        Retrieve a value from the in-memory store by key.

        Args:
            key (str): The key to look up

        Returns:
            The stored value if found, None otherwise
        """
        return self.data.get(key)

    def set(self, key: str, value: str):
        """
        Store a value in the in-memory store with the given key.

        Args:
            key (str): The key to store the value under
            value (str): The value to store
        """
        self.data[key] = value

    def delete(self, key: str):
        """
        Delete a value from the in-memory store by key.

        Args:
            key (str): The key to delete
        """
        del self.data[key]


class EnvironmentStore(Store):
    """
    Store that uses environment variables to store credentials.
    Implements the Store interface using OS environment variables as the backend.
    """

    def __init__(self):
        """Initialize the environment store."""
        pass

    def get(self, key: str):
        """
        Retrieve a value from environment variables by key.

        Args:
            key (str): The environment variable name to look up

        Returns:
            dict: Dictionary containing the api_key from environment variable
        """
        return {"api_key": os.getenv(key)}

    def set(self, key: str, value: str):
        """
        Set an environment variable.

        Args:
            key (str): The environment variable name
            value (str): The value to set
        """
        os.environ[key] = value

    def delete(self, key: str):
        """
        Delete an environment variable.

        Args:
            key (str): The environment variable name to delete
        """
        del os.environ[key]


class KeyringStore(Store):
    """
    Store that uses keyring to store credentials.
    Implements the Store interface using system keyring as the backend.
    """

    def __init__(self, app_name: str = "universal_mcp"):
        """
        Initialize the keyring store.

        Args:
            app_name (str): The application name to use in keyring, defaults to "universal_mcp"
        """
        self.app_name = app_name

    def get(self, key: str):
        """
        Retrieve a password from the system keyring.

        Args:
            key (str): The key to look up

        Returns:
            The stored password if found, None otherwise
        """
        logger.info(f"Getting password for {key} from keyring")
        return keyring.get_password(self.app_name, key)

    def set(self, key: str, value: str):
        """
        Store a password in the system keyring.

        Args:
            key (str): The key to store the password under
            value (str): The password to store
        """
        logger.info(f"Setting password for {key} in keyring")
        keyring.set_password(self.app_name, key, value)

    def delete(self, key: str):
        """
        Delete a password from the system keyring.

        Args:
            key (str): The key to delete
        """
        logger.info(f"Deleting password for {key} from keyring")
        keyring.delete_password(self.app_name, key)
