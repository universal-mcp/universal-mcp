from abc import ABC, abstractmethod
from typing import Any


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
