from typing import Any

from universal_mcp.exceptions import KeyNotFoundError
from universal_mcp.stores.base import BaseStore


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
