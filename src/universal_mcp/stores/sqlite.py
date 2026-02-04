import json
import sqlite3
from pathlib import Path
from typing import Any

from universal_mcp.exceptions import KeyNotFoundError, StoreError
from universal_mcp.stores.base import BaseStore


class SQLiteStore(BaseStore):
    """SQLite database-based credential and data store.

    This store implementation uses a SQLite database to persist key-value
    pairs. Values are serialized as JSON strings, allowing storage of
    complex data types. The database file is created automatically if it
    doesn't exist. This store is suitable for applications needing
    persistent, transactional storage with better performance than
    file-based stores for frequent operations.

    Attributes:
        db_path (Path): Path to the SQLite database file.
        table_name (str): Name of the table used for storing key-value pairs.
    """

    def __init__(
        self, db_path: str | Path = "~/.universal_mcp/store.db", table_name: str = "credentials"
    ):
        """Initializes the SQLiteStore.

        Args:
            db_path (str | Path, optional): Path to the SQLite database file.
                Defaults to "~/.universal_mcp/store.db".
            table_name (str, optional): Name of the table for storing data.
                Defaults to "credentials".
        """
        self.db_path = Path(db_path).expanduser().resolve()
        self.table_name = table_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database and table
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the database and creates the table if it doesn't exist.

        Raises:
            StoreError: If database initialization fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as e:
            raise StoreError(f"Failed to initialize database at {self.db_path}: {str(e)}") from e

    def get(self, key: str) -> Any:
        """Retrieves the value associated with the given key from the SQLite store.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            Any: The value associated with the key (deserialized from JSON).

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If database operation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"SELECT value FROM {self.table_name} WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row is None:
                    raise KeyNotFoundError(f"Key '{key}' not found in SQLite store")
                return json.loads(row[0])
        except KeyNotFoundError:
            raise
        except Exception as e:
            raise StoreError(f"Failed to retrieve key '{key}' from SQLite store: {str(e)}") from e

    def set(self, key: str, value: Any) -> None:
        """Sets or updates the value for a given key in the SQLite store.

        Args:
            key (str): The key to set or update.
            value (Any): The value to associate with the key.
                        Must be JSON-serializable.

        Raises:
            StoreError: If database operation fails.
        """
        try:
            json_value = json.dumps(value)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"INSERT OR REPLACE INTO {self.table_name} (key, value) VALUES (?, ?)",
                    (key, json_value),
                )
                conn.commit()
        except Exception as e:
            raise StoreError(f"Failed to store key '{key}' in SQLite store: {str(e)}") from e

    def delete(self, key: str) -> None:
        """Deletes a key-value pair from the SQLite store.

        Args:
            key (str): The key to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If database operation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"DELETE FROM {self.table_name} WHERE key = ?", (key,))
                conn.commit()
                if cursor.rowcount == 0:
                    raise KeyNotFoundError(f"Key '{key}' not found in SQLite store")
        except KeyNotFoundError:
            raise
        except Exception as e:
            raise StoreError(f"Failed to delete key '{key}' from SQLite store: {str(e)}") from e

    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the store instance."""
        return f"{self.__class__.__name__}(db_path='{self.db_path}', table_name='{self.table_name}')"
