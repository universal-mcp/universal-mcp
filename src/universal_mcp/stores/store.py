import hashlib
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import aiofiles
import keyring
from loguru import logger

from universal_mcp.exceptions import KeyNotFoundError, StoreError


class BaseStore(ABC):
    """Abstract base class defining a common async interface for credential stores.

    All store operations are async to support non-blocking I/O operations.
    This ensures consistent API for managing sensitive data across various storage
    backends like in-memory dictionaries, environment variables, or system keyrings.
    """

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Retrieve data from the store asynchronously.

        Args:
            key: The key for which to retrieve the value.

        Returns:
            The value associated with the key.

        Raises:
            KeyNotFoundError: If the specified key is not found in the store.
            StoreError: For other store-related operational errors.
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """Set or update a key-value pair in the store asynchronously.

        If the key already exists, its value should be updated. If the key
        does not exist, it should be created.

        Args:
            key: The key to set or update.
            value: The value to associate with the key.

        Raises:
            StoreError: For store-related operational errors (e.g., write failures).
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a key-value pair from the store asynchronously.

        Args:
            key: The key to delete.

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
        data: The dictionary holding the stored key-value pairs.
    """

    def __init__(self):
        """Initializes the MemoryStore with an empty dictionary."""
        self.data: dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        """Retrieves the value associated with the given key from the in-memory store.

        Args:
            key: The key whose value is to be retrieved.

        Returns:
            The value associated with the key.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
        """
        if key not in self.data:
            raise KeyNotFoundError(f"Key '{key}' not found in memory store")
        return self.data[key]

    async def set(self, key: str, value: Any) -> None:
        """Sets or updates the value for a given key in the in-memory store.

        Args:
            key: The key to set or update.
            value: The value to associate with the key.
        """
        self.data[key] = value

    async def delete(self, key: str) -> None:
        """Deletes a key-value pair from the in-memory store.

        Args:
            key: The key to delete.

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

    async def get(self, key: str) -> Any:
        """Retrieves the value of an environment variable.

        Args:
            key: The name of the environment variable.

        Returns:
            The value of the environment variable as a string.

        Raises:
            KeyNotFoundError: If the environment variable is not set.
        """
        value = os.getenv(key)
        if value is None:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        # Try to deserialize JSON values
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return value

    async def set(self, key: str, value: Any) -> None:
        """Sets an environment variable in the current process.

        Args:
            key: The name of the environment variable.
            value: The value to set for the environment variable.
                   It will be converted to a string.
        """
        if isinstance(value, (dict, list)):
            os.environ[key] = json.dumps(value)
        else:
            os.environ[key] = str(value)

    async def delete(self, key: str) -> None:
        """Deletes an environment variable from the current process.

        Args:
            key: The name of the environment variable to delete.

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

    Note: The keyring library is synchronous, so we wrap calls in async methods.

    Attributes:
        app_name: The service name under which credentials are stored
                  in the system keyring. This helps namespace credentials
                  for different applications.
    """

    def __init__(self, app_name: str = "universal_mcp"):
        """Initializes the KeyringStore.

        Args:
            app_name: The service name to use when interacting
                     with the system keyring. This helps to namespace credentials.
                     Defaults to "universal_mcp".
        """
        self.app_name = app_name

    async def get(self, key: str) -> str:
        """Retrieves a secret (password) from the system keyring.

        Args:
            key: The username or key associated with the secret.

        Returns:
            The stored secret string.

        Raises:
            KeyNotFoundError: If the key is not found in the keyring under
                             `self.app_name`, or if `keyring` library errors occur.
        """
        try:
            logger.info(f"Getting password for {key} from keyring for app {self.app_name}")
            value = keyring.get_password(self.app_name, key)
            if value is None:
                raise KeyNotFoundError(f"Key '{key}' not found in keyring for app '{self.app_name}'")
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return value
        except KeyNotFoundError:
            raise
        except Exception as e:  # Catches keyring specific errors too
            raise KeyNotFoundError(
                f"Failed to retrieve key '{key}' from keyring for app '{self.app_name}'. Original error: {type(e).__name__}"
            ) from e

    async def set(self, key: str, value: Any) -> None:
        """Stores a secret (password) in the system keyring.

        Args:
            key: The username or key to associate with the secret.
            value: The secret to store. It will be converted to a string.

        Raises:
            StoreError: If storing the secret in the keyring fails.
        """
        try:
            logger.info(f"Setting password for {key} in keyring for app {self.app_name}")
            store_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            keyring.set_password(self.app_name, key, store_value)
        except Exception as e:
            raise StoreError(f"Error storing key '{key}' in keyring for app '{self.app_name}': {str(e)}") from e

    async def delete(self, key: str) -> None:
        """Deletes a secret (password) from the system keyring.

        Args:
            key: The username or key of the secret to delete.

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


class DiskStore(BaseStore):
    """File-based persistent store using JSON serialization with async I/O.

    This store implementation persists data to disk as individual JSON files,
    with each key stored in a separate file. The filename is derived from a
    hash of the key to ensure filesystem safety. This provides persistent
    storage that survives application restarts while remaining simple and
    portable.

    All file operations are async using aiofiles for non-blocking I/O.

    Attributes:
        path: The directory where store files are persisted.
        app_name: The application name used for namespacing.
    """

    def __init__(self, path: Path | None = None, app_name: str = "universal_mcp"):
        """Initializes the DiskStore.

        Args:
            path: The directory path where files will be stored.
                 If None, defaults to ~/.universal-mcp/store. Defaults to None.
            app_name: The application name for namespacing.
                     Defaults to "universal_mcp".
        """
        self.app_name = app_name
        if path is None:
            path = Path.home() / f".{app_name}" / "store"
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> Path:
        """Generates a safe filesystem path for the given key.

        Args:
            key: The key to generate a path for.

        Returns:
            The file path where the key's value should be stored.
        """
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.path / f"{key_hash}.json"

    async def get(self, key: str) -> Any:
        """Retrieves the value associated with the given key from disk.

        Args:
            key: The key whose value is to be retrieved.

        Returns:
            The value associated with the key.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If reading or deserializing the file fails.
        """
        file_path = self._get_file_path(key)
        if not file_path.exists():
            raise KeyNotFoundError(f"Key '{key}' not found in disk store at {self.path}")

        try:
            async with aiofiles.open(file_path, mode="r") as f:
                content = await f.read()
                data = json.loads(content)
                return data["value"]
        except Exception as e:
            raise StoreError(f"Error reading key '{key}' from disk store: {str(e)}") from e

    async def set(self, key: str, value: Any) -> None:
        """Sets or updates the value for a given key on disk.

        Args:
            key: The key to set or update.
            value: The value to associate with the key. Must be JSON-serializable.

        Raises:
            StoreError: If writing or serializing the file fails.
        """
        file_path = self._get_file_path(key)
        try:
            content = json.dumps({"key": key, "value": value}, indent=2)
            async with aiofiles.open(file_path, mode="w") as f:
                await f.write(content)
        except Exception as e:
            raise StoreError(f"Error writing key '{key}' to disk store: {str(e)}") from e

    async def delete(self, key: str) -> None:
        """Deletes a key-value pair from disk.

        Args:
            key: The key to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If deleting the file fails.
        """
        file_path = self._get_file_path(key)
        if not file_path.exists():
            raise KeyNotFoundError(f"Key '{key}' not found in disk store at {self.path}")

        try:
            file_path.unlink()
        except Exception as e:
            raise StoreError(f"Error deleting key '{key}' from disk store: {str(e)}") from e

    async def list_keys(self) -> list[str]:
        """Lists all keys in the store.

        Returns:
            A list of all keys stored in the disk store.

        Raises:
            StoreError: If reading the store directory or files fails.
        """
        keys = []
        try:
            for file_path in self.path.glob("*.json"):
                try:
                    async with aiofiles.open(file_path, mode="r") as f:
                        content = await f.read()
                        data = json.loads(content)
                        keys.append(data["key"])
                except Exception:
                    # Skip corrupted files
                    continue
            return keys
        except Exception as e:
            raise StoreError(f"Error listing keys from disk store: {str(e)}") from e

    def has(self, key: str) -> bool:
        """Checks if a key exists in the store (synchronous).

        Args:
            key: The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        file_path = self._get_file_path(key)
        return file_path.exists()

    async def clear(self) -> None:
        """Removes all key-value pairs from the store.

        Raises:
            StoreError: If clearing the store fails.
        """
        try:
            for file_path in self.path.glob("*.json"):
                file_path.unlink()
        except Exception as e:
            raise StoreError(f"Error clearing disk store: {str(e)}") from e
