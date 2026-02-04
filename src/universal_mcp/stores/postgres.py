import json
from typing import Any

from universal_mcp.exceptions import KeyNotFoundError, StoreError
from universal_mcp.stores.base import BaseStore


class PostgresStore(BaseStore):
    """PostgreSQL database-based credential and data store.

    This store implementation uses a PostgreSQL database to persist
    key-value pairs. Values are serialized as JSON strings (stored in
    JSONB columns for efficient querying). This store is suitable for
    applications requiring a production-grade, scalable database with
    advanced features like replication and concurrent access.

    Note: Requires psycopg2 or psycopg3 to be installed separately.

    Attributes:
        connection_params (dict): Database connection parameters.
        table_name (str): Name of the table used for storing key-value pairs.
    """

    def __init__(
        self,
        connection_params: dict[str, Any] | None = None,
        table_name: str = "credentials",
        connection_string: str | None = None,
    ):
        """Initializes the PostgresStore.

        Args:
            connection_params (dict[str, Any] | None, optional): Dictionary of
                connection parameters (host, port, database, user, password).
                Defaults to None, which uses connection_string or environment variables.
            table_name (str, optional): Name of the table for storing data.
                Defaults to "credentials".
            connection_string (str | None, optional): PostgreSQL connection string.
                If provided, takes precedence over connection_params.

        Raises:
            ImportError: If psycopg2 is not installed.
            StoreError: If database connection or initialization fails.
        """
        try:
            import psycopg2
            import psycopg2.extras

            self._psycopg2 = psycopg2
            self._psycopg2_extras = psycopg2.extras
        except ImportError as e:
            raise ImportError(
                "psycopg2 is required for PostgresStore. Install it with: pip install psycopg2-binary"
            ) from e

        self.connection_string = connection_string
        self.connection_params = connection_params or {}
        self.table_name = table_name

        # Initialize database and table
        self._init_db()

    def _get_connection(self):
        """Creates and returns a database connection.

        Returns:
            Connection object from psycopg2.

        Raises:
            StoreError: If connection fails.
        """
        try:
            if self.connection_string:
                return self._psycopg2.connect(self.connection_string)
            else:
                return self._psycopg2.connect(**self.connection_params)
        except Exception as e:
            raise StoreError(f"Failed to connect to PostgreSQL database: {str(e)}") from e

    def _init_db(self) -> None:
        """Initializes the database table if it doesn't exist.

        Raises:
            StoreError: If database initialization fails.
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        key TEXT PRIMARY KEY,
                        value JSONB NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as e:
            raise StoreError(f"Failed to initialize PostgreSQL database: {str(e)}") from e

    def get(self, key: str) -> Any:
        """Retrieves the value associated with the given key from the Postgres store.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If database operation fails.
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(f"SELECT value FROM {self.table_name} WHERE key = %s", (key,))
                row = cursor.fetchone()
                if row is None:
                    raise KeyNotFoundError(f"Key '{key}' not found in Postgres store")
                return row[0]
        except KeyNotFoundError:
            raise
        except Exception as e:
            raise StoreError(f"Failed to retrieve key '{key}' from Postgres store: {str(e)}") from e

    def set(self, key: str, value: Any) -> None:
        """Sets or updates the value for a given key in the Postgres store.

        Args:
            key (str): The key to set or update.
            value (Any): The value to associate with the key.
                        Must be JSON-serializable.

        Raises:
            StoreError: If database operation fails.
        """
        try:
            json_value = json.dumps(value)
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {self.table_name} (key, value)
                    VALUES (%s, %s::jsonb)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (key, json_value),
                )
                conn.commit()
        except Exception as e:
            raise StoreError(f"Failed to store key '{key}' in Postgres store: {str(e)}") from e

    def delete(self, key: str) -> None:
        """Deletes a key-value pair from the Postgres store.

        Args:
            key (str): The key to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the store.
            StoreError: If database operation fails.
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE key = %s", (key,))
                conn.commit()
                if cursor.rowcount == 0:
                    raise KeyNotFoundError(f"Key '{key}' not found in Postgres store")
        except KeyNotFoundError:
            raise
        except Exception as e:
            raise StoreError(f"Failed to delete key '{key}' from Postgres store: {str(e)}") from e

    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the store instance."""
        if self.connection_string:
            # Don't expose full connection string for security
            return f"{self.__class__.__name__}(connection_string='***', table_name='{self.table_name}')"
        else:
            # Sanitize connection params (hide password)
            safe_params = {k: "***" if k == "password" else v for k, v in self.connection_params.items()}
            return f"{self.__class__.__name__}(connection_params={safe_params}, table_name='{self.table_name}')"
