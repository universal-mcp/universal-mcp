import contextlib
import os
from pathlib import Path

import pytest

from universal_mcp.exceptions import KeyNotFoundError, StoreError
from universal_mcp.stores import (
    EnvironmentStore,
    FileStore,
    KeyringStore,
    MemoryStore,
    PostgresStore,
    SQLiteStore,
)


# Test MemoryStore
class TestMemoryStore:
    @pytest.fixture
    def store(self):
        return MemoryStore()

    def test_set_and_get(self, store):
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

    def test_delete(self, store):
        store.set("test_key", "test_value")
        store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            store.get("test_key")

    def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.get("nonexistent_key")

    def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.delete("nonexistent_key")


# Test EnvironmentStore
class TestEnvironmentStore:
    @pytest.fixture
    def store(self):
        store = EnvironmentStore()
        # Clean up any test variables after each test
        yield store
        if "TEST_ENV_KEY" in os.environ:
            del os.environ["TEST_ENV_KEY"]

    def test_set_and_get(self, store):
        store.set("TEST_ENV_KEY", "test_value")
        assert store.get("TEST_ENV_KEY") == "test_value"
        assert os.getenv("TEST_ENV_KEY") == "test_value"

    def test_delete(self, store):
        store.set("TEST_ENV_KEY", "test_value")
        store.delete("TEST_ENV_KEY")
        with pytest.raises(KeyNotFoundError):
            store.get("TEST_ENV_KEY")

    def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.get("NONEXISTENT_ENV_KEY")

    def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.delete("NONEXISTENT_ENV_KEY")


# Test KeyringStore
@pytest.mark.skip(reason="Skipping KeyringStore tests")
class TestKeyringStore:
    @pytest.fixture
    def store(self):
        store = KeyringStore("test_app")
        yield store
        # Clean up after tests
        with contextlib.suppress(KeyNotFoundError):
            store.delete("test_key")

    def test_set_and_get(self, store):
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

    def test_delete(self, store):
        store.set("test_key", "test_value")
        store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            store.get("test_key")

    def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.get("nonexistent_key")

    def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.delete("nonexistent_key")


# Test FileStore
class TestFileStore:
    @pytest.fixture
    def store(self, tmp_path):
        """Create a FileStore with a temporary file."""
        file_path = tmp_path / "test_store.json"
        return FileStore(file_path)

    def test_set_and_get(self, store):
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

    def test_set_and_get_complex_types(self, store):
        """Test storing complex JSON-serializable types."""
        test_data = {"nested": {"key": "value"}, "list": [1, 2, 3], "number": 42}
        store.set("complex_key", test_data)
        assert store.get("complex_key") == test_data

    def test_delete(self, store):
        store.set("test_key", "test_value")
        store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            store.get("test_key")

    def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.get("nonexistent_key")

    def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.delete("nonexistent_key")

    def test_persistence(self, tmp_path):
        """Test that data persists across store instances."""
        file_path = tmp_path / "persistence_test.json"

        # Create first store and set a value
        store1 = FileStore(file_path)
        store1.set("persist_key", "persist_value")

        # Create second store with same file and verify value persists
        store2 = FileStore(file_path)
        assert store2.get("persist_key") == "persist_value"

    def test_update_existing_key(self, store):
        """Test that updating an existing key works correctly."""
        store.set("update_key", "old_value")
        store.set("update_key", "new_value")
        assert store.get("update_key") == "new_value"

    def test_file_creation(self, tmp_path):
        """Test that the store creates the file and parent directories."""
        nested_path = tmp_path / "nested" / "dir" / "store.json"
        store = FileStore(nested_path)
        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_repr(self, store):
        """Test string representation."""
        repr_str = repr(store)
        assert "FileStore" in repr_str
        assert "file_path" in repr_str


# Test SQLiteStore
class TestSQLiteStore:
    @pytest.fixture
    def store(self, tmp_path):
        """Create a SQLiteStore with a temporary database."""
        db_path = tmp_path / "test_store.db"
        return SQLiteStore(db_path)

    def test_set_and_get(self, store):
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

    def test_set_and_get_complex_types(self, store):
        """Test storing complex JSON-serializable types."""
        test_data = {"nested": {"key": "value"}, "list": [1, 2, 3], "number": 42, "bool": True}
        store.set("complex_key", test_data)
        assert store.get("complex_key") == test_data

    def test_delete(self, store):
        store.set("test_key", "test_value")
        store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            store.get("test_key")

    def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.get("nonexistent_key")

    def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.delete("nonexistent_key")

    def test_persistence(self, tmp_path):
        """Test that data persists across store instances."""
        db_path = tmp_path / "persistence_test.db"

        # Create first store and set a value
        store1 = SQLiteStore(db_path)
        store1.set("persist_key", "persist_value")

        # Create second store with same database and verify value persists
        store2 = SQLiteStore(db_path)
        assert store2.get("persist_key") == "persist_value"

    def test_update_existing_key(self, store):
        """Test that updating an existing key works correctly."""
        store.set("update_key", "old_value")
        store.set("update_key", "new_value")
        assert store.get("update_key") == "new_value"

    def test_multiple_keys(self, store):
        """Test storing multiple keys."""
        store.set("key1", "value1")
        store.set("key2", "value2")
        store.set("key3", "value3")

        assert store.get("key1") == "value1"
        assert store.get("key2") == "value2"
        assert store.get("key3") == "value3"

    def test_custom_table_name(self, tmp_path):
        """Test using a custom table name."""
        db_path = tmp_path / "custom_table.db"
        store = SQLiteStore(db_path, table_name="custom_creds")
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

    def test_repr(self, store):
        """Test string representation."""
        repr_str = repr(store)
        assert "SQLiteStore" in repr_str
        assert "db_path" in repr_str
        assert "table_name" in repr_str


# Test PostgresStore
@pytest.mark.skip(reason="Skipping PostgresStore tests - requires running PostgreSQL server")
class TestPostgresStore:
    @pytest.fixture
    def store(self):
        """Create a PostgresStore with test database connection.

        Note: This requires a running PostgreSQL server with test database.
        Set POSTGRES_TEST_CONNECTION_STRING environment variable or use default parameters.
        """
        connection_string = os.getenv(
            "POSTGRES_TEST_CONNECTION_STRING",
            "postgresql://postgres:postgres@localhost:5432/test_db",
        )
        store = PostgresStore(connection_string=connection_string, table_name="test_credentials")

        # Clean up before tests
        try:
            # Clear any existing test data
            with store._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {store.table_name}")
                conn.commit()
        except Exception:
            pass  # Table might not exist yet

        yield store

        # Clean up after tests
        try:
            with store._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DROP TABLE IF EXISTS {store.table_name}")
                conn.commit()
        except Exception:
            pass

    def test_set_and_get(self, store):
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

    def test_set_and_get_complex_types(self, store):
        """Test storing complex JSON-serializable types."""
        test_data = {"nested": {"key": "value"}, "list": [1, 2, 3], "number": 42, "bool": True}
        store.set("complex_key", test_data)
        assert store.get("complex_key") == test_data

    def test_delete(self, store):
        store.set("test_key", "test_value")
        store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            store.get("test_key")

    def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.get("nonexistent_key")

    def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            store.delete("nonexistent_key")

    def test_update_existing_key(self, store):
        """Test that updating an existing key works correctly."""
        store.set("update_key", "old_value")
        store.set("update_key", "new_value")
        assert store.get("update_key") == "new_value"

    def test_multiple_keys(self, store):
        """Test storing multiple keys."""
        store.set("key1", "value1")
        store.set("key2", "value2")
        store.set("key3", "value3")

        assert store.get("key1") == "value1"
        assert store.get("key2") == "value2"
        assert store.get("key3") == "value3"

    def test_repr(self, store):
        """Test string representation (should hide sensitive info)."""
        repr_str = repr(store)
        assert "PostgresStore" in repr_str
        assert "***" in repr_str  # Password should be hidden


# Test that psycopg2 import error is handled gracefully
class TestPostgresStoreImport:
    def test_missing_psycopg2_raises_import_error(self, monkeypatch):
        """Test that PostgresStore raises ImportError when psycopg2 is not available."""
        # Mock the import to raise ImportError
        import builtins
        import sys

        # Save original psycopg2 module if it exists
        original_psycopg2 = sys.modules.get("psycopg2")
        original_extras = sys.modules.get("psycopg2.extras")

        # Remove from sys.modules to force re-import
        if "psycopg2" in sys.modules:
            del sys.modules["psycopg2"]
        if "psycopg2.extras" in sys.modules:
            del sys.modules["psycopg2.extras"]

        # Mock the import to fail
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "psycopg2":
                raise ImportError("No module named 'psycopg2'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        try:
            with pytest.raises(ImportError, match="psycopg2 is required"):
                PostgresStore()
        finally:
            # Restore original modules
            if original_psycopg2 is not None:
                sys.modules["psycopg2"] = original_psycopg2
            if original_extras is not None:
                sys.modules["psycopg2.extras"] = original_extras
            monkeypatch.undo()
