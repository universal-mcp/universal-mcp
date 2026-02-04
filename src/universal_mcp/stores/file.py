import json
from pathlib import Path
from typing import Any

from universal_mcp.exceptions import KeyNotFoundError, StoreError
from universal_mcp.stores.base import BaseStore


class FileStore(BaseStore):
    """File-based credential and data store using JSON format.

    This store implementation persists data to a JSON file on disk.
    All data is stored in a single JSON file, making it suitable for
    applications that need persistent storage without a database.
    The file is read and written atomically to prevent corruption.

    Attributes:
        file_path (Path): Path to the JSON file where data is stored.
    """

    def __init__(self, file_path: str | Path = "~/.universal_mcp/store.json"):
        """Initializes the FileStore.

        Args:
            file_path (str | Path, optional): Path to the JSON file for storage.
                Defaults to "~/.universal_mcp/store.json".
                The path is expanded and parent directories are created if needed.
        """
        self.file_path = Path(file_path).expanduser().resolve()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize empty file if it doesn't exist
        if not self.file_path.exists():
            self._write_data({})

    def _read_data(self) -> dict[str, Any]:
        """Reads and returns all data from the JSON file.

        Returns:
            dict[str, Any]: Dictionary containing all stored key-value pairs.

        Raises:
            StoreError: If the file cannot be read or parsed.
        """
        try:
            with open(self.file_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise StoreError(f"Failed to parse JSON from {self.file_path}: {str(e)}") from e
        except Exception as e:
            raise StoreError(f"Failed to read from {self.file_path}: {str(e)}") from e

    def _write_data(self, data: dict[str, Any]) -> None:
        """Writes data to the JSON file atomically.

        Args:
            data (dict[str, Any]): Dictionary to write to the file.

        Raises:
            StoreError: If the file cannot be written.
        """
        try:
            # Write to temporary file first, then rename for atomicity
            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.file_path)
        except Exception as e:
            raise StoreError(f"Failed to write to {self.file_path}: {str(e)}") from e

    def get(self, key: str) -> Any:
        """Retrieves the value associated with the given key from the file store.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If the file cannot be read.
        """
        data = self._read_data()
        if key not in data:
            raise KeyNotFoundError(f"Key '{key}' not found in file store")
        return data[key]

    def set(self, key: str, value: Any) -> None:
        """Sets or updates the value for a given key in the file store.

        Args:
            key (str): The key to set or update.
            value (Any): The value to associate with the key.
                        Must be JSON-serializable.

        Raises:
            StoreError: If the file cannot be read or written.
        """
        data = self._read_data()
        data[key] = value
        self._write_data(data)

    def delete(self, key: str) -> None:
        """Deletes a key-value pair from the file store.

        Args:
            key (str): The key to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If the file cannot be read or written.
        """
        data = self._read_data()
        if key not in data:
            raise KeyNotFoundError(f"Key '{key}' not found in file store")
        del data[key]
        self._write_data(data)

    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the store instance."""
        return f"{self.__class__.__name__}(file_path='{self.file_path}')"
