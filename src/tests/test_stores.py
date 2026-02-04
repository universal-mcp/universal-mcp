import contextlib
import os

import pytest

from universal_mcp.stores.store import (
    DiskStore,
    EnvironmentStore,
    KeyNotFoundError,
    KeyringStore,
    MemoryStore,
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


# Test DiskStore
class TestDiskStore:
    @pytest.fixture
    def store(self, tmp_path):
        """Create a DiskStore instance with a temporary directory."""
        return DiskStore(path=tmp_path)

    def test_disk_store_basic_operations(self, tmp_path):
        """Test get/set/delete/has operations."""
        store = DiskStore(path=tmp_path)

        # Test set and get
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"

        # Test has
        assert store.has("test_key")
        assert not store.has("nonexistent_key")

        # Test delete
        store.delete("test_key")
        assert not store.has("test_key")

    def test_disk_store_persistence(self, tmp_path):
        """Test that data persists across instances."""
        # Create first instance and store data
        store1 = DiskStore(path=tmp_path)
        store1.set("persistent_key", "persistent_value")
        store1.set("another_key", {"nested": "data"})

        # Create new instance with same path
        store2 = DiskStore(path=tmp_path)

        # Verify data persists
        assert store2.get("persistent_key") == "persistent_value"
        assert store2.get("another_key") == {"nested": "data"}
        assert store2.has("persistent_key")
        assert store2.has("another_key")

    def test_disk_store_clear(self, tmp_path):
        """Test clear() removes all data."""
        store = DiskStore(path=tmp_path)

        # Add multiple items
        store.set("key1", "value1")
        store.set("key2", "value2")
        store.set("key3", "value3")

        # Verify they exist
        assert store.has("key1")
        assert store.has("key2")
        assert store.has("key3")

        # Clear all
        store.clear()

        # Verify all removed
        assert not store.has("key1")
        assert not store.has("key2")
        assert not store.has("key3")
        assert store.list_keys() == []

    def test_disk_store_list_keys(self, tmp_path):
        """Test list_keys() functionality."""
        store = DiskStore(path=tmp_path)

        # Empty store
        assert store.list_keys() == []

        # Add keys
        store.set("key1", "value1")
        store.set("key2", "value2")
        store.set("key3", "value3")

        # List all keys
        keys = store.list_keys()
        assert len(keys) == 3
        assert set(keys) == {"key1", "key2", "key3"}

        # Delete one key
        store.delete("key2")
        keys = store.list_keys()
        assert len(keys) == 2
        assert set(keys) == {"key1", "key3"}

    def test_disk_store_key_not_found(self, tmp_path):
        """Test KeyNotFoundError is raised appropriately."""
        store = DiskStore(path=tmp_path)

        # Get nonexistent key
        with pytest.raises(KeyNotFoundError):
            store.get("nonexistent_key")

        # Delete nonexistent key
        with pytest.raises(KeyNotFoundError):
            store.delete("nonexistent_key")

    def test_disk_store_complex_values(self, tmp_path):
        """Test storing complex JSON-serializable values."""
        store = DiskStore(path=tmp_path)

        # Store various types
        store.set("string", "test")
        store.set("number", 42)
        store.set("float", 3.14)
        store.set("boolean", True)
        store.set("null", None)
        store.set("list", [1, 2, 3])
        store.set("dict", {"nested": {"deep": "value"}})

        # Verify retrieval
        assert store.get("string") == "test"
        assert store.get("number") == 42
        assert store.get("float") == 3.14
        assert store.get("boolean") is True
        assert store.get("null") is None
        assert store.get("list") == [1, 2, 3]
        assert store.get("dict") == {"nested": {"deep": "value"}}

    def test_disk_store_update_existing_key(self, tmp_path):
        """Test updating an existing key's value."""
        store = DiskStore(path=tmp_path)

        # Set initial value
        store.set("update_key", "initial_value")
        assert store.get("update_key") == "initial_value"

        # Update value
        store.set("update_key", "updated_value")
        assert store.get("update_key") == "updated_value"

    def test_disk_store_special_characters_in_keys(self, tmp_path):
        """Test that keys with special characters are handled correctly."""
        store = DiskStore(path=tmp_path)

        # Keys with special characters
        special_keys = [
            "key/with/slashes",
            "key:with:colons",
            "key with spaces",
            "key@with#symbols",
            "unicode_🔑_key"
        ]

        for key in special_keys:
            store.set(key, f"value_for_{key}")
            assert store.get(key) == f"value_for_{key}"
            assert store.has(key)

        # Verify list_keys returns all
        keys = store.list_keys()
        assert len(keys) == len(special_keys)
        assert set(keys) == set(special_keys)
