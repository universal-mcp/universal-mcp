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
@pytest.mark.asyncio
class TestMemoryStore:
    @pytest.fixture
    def store(self):
        return MemoryStore()

    async def test_set_and_get(self, store):
        await store.set("test_key", "test_value")
        assert await store.get("test_key") == "test_value"

    async def test_delete(self, store):
        await store.set("test_key", "test_value")
        await store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            await store.get("test_key")

    async def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            await store.get("nonexistent_key")

    async def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            await store.delete("nonexistent_key")


# Test EnvironmentStore
@pytest.mark.asyncio
class TestEnvironmentStore:
    @pytest.fixture
    def store(self):
        store = EnvironmentStore()
        # Clean up any test variables after each test
        yield store
        if "TEST_ENV_KEY" in os.environ:
            del os.environ["TEST_ENV_KEY"]

    async def test_set_and_get(self, store):
        await store.set("TEST_ENV_KEY", "test_value")
        assert await store.get("TEST_ENV_KEY") == "test_value"
        assert os.getenv("TEST_ENV_KEY") == "test_value"

    async def test_delete(self, store):
        await store.set("TEST_ENV_KEY", "test_value")
        await store.delete("TEST_ENV_KEY")
        with pytest.raises(KeyNotFoundError):
            await store.get("TEST_ENV_KEY")

    async def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            await store.get("NONEXISTENT_ENV_KEY")

    async def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            await store.delete("NONEXISTENT_ENV_KEY")


# Test KeyringStore
@pytest.mark.skip(reason="Skipping KeyringStore tests")
@pytest.mark.asyncio
class TestKeyringStore:
    @pytest.fixture
    def store(self):
        store = KeyringStore("test_app")
        yield store
        # Clean up after tests
        with contextlib.suppress(KeyNotFoundError):
            store.delete("test_key")

    async def test_set_and_get(self, store):
        await store.set("test_key", "test_value")
        assert await store.get("test_key") == "test_value"

    async def test_delete(self, store):
        await store.set("test_key", "test_value")
        await store.delete("test_key")
        with pytest.raises(KeyNotFoundError):
            await store.get("test_key")

    async def test_get_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            await store.get("nonexistent_key")

    async def test_delete_nonexistent_key(self, store):
        with pytest.raises(KeyNotFoundError):
            await store.delete("nonexistent_key")


# Test DiskStore
@pytest.mark.asyncio
class TestDiskStore:
    @pytest.fixture
    def store(self, tmp_path):
        """Create a DiskStore instance with a temporary directory."""
        return DiskStore(path=tmp_path)

    async def test_disk_store_basic_operations(self, tmp_path):
        """Test get/set/delete/has operations."""
        store = DiskStore(path=tmp_path)

        # Test set and get
        await store.set("test_key", "test_value")
        assert await store.get("test_key") == "test_value"

        # Test has (synchronous method)
        assert store.has("test_key")
        assert not store.has("nonexistent_key")

        # Test delete
        await store.delete("test_key")
        assert not store.has("test_key")

    async def test_disk_store_persistence(self, tmp_path):
        """Test that data persists across instances."""
        # Create first instance and store data
        store1 = DiskStore(path=tmp_path)
        await store1.set("persistent_key", "persistent_value")
        await store1.set("another_key", {"nested": "data"})

        # Create new instance with same path
        store2 = DiskStore(path=tmp_path)

        # Verify data persists
        assert await store2.get("persistent_key") == "persistent_value"
        assert await store2.get("another_key") == {"nested": "data"}
        assert store2.has("persistent_key")
        assert store2.has("another_key")

    async def test_disk_store_clear(self, tmp_path):
        """Test clear() removes all data."""
        store = DiskStore(path=tmp_path)

        # Add multiple items
        await store.set("key1", "value1")
        await store.set("key2", "value2")
        await store.set("key3", "value3")

        # Verify they exist
        assert store.has("key1")
        assert store.has("key2")
        assert store.has("key3")

        # Clear all
        await store.clear()

        # Verify all removed
        assert not store.has("key1")
        assert not store.has("key2")
        assert not store.has("key3")
        assert await store.list_keys() == []

    async def test_disk_store_list_keys(self, tmp_path):
        """Test list_keys() functionality."""
        store = DiskStore(path=tmp_path)

        # Empty store
        assert await store.list_keys() == []

        # Add keys
        await store.set("key1", "value1")
        await store.set("key2", "value2")
        await store.set("key3", "value3")

        # List all keys
        keys = await store.list_keys()
        assert len(keys) == 3
        assert set(keys) == {"key1", "key2", "key3"}

        # Delete one key
        await store.delete("key2")
        keys = await store.list_keys()
        assert len(keys) == 2
        assert set(keys) == {"key1", "key3"}

    async def test_disk_store_key_not_found(self, tmp_path):
        """Test KeyNotFoundError is raised appropriately."""
        store = DiskStore(path=tmp_path)

        # Get nonexistent key
        with pytest.raises(KeyNotFoundError):
            await store.get("nonexistent_key")

        # Delete nonexistent key
        with pytest.raises(KeyNotFoundError):
            await store.delete("nonexistent_key")

    async def test_disk_store_complex_values(self, tmp_path):
        """Test storing complex JSON-serializable values."""
        store = DiskStore(path=tmp_path)

        # Store various types
        await store.set("string", "test")
        await store.set("number", 42)
        await store.set("float", 3.14)
        await store.set("boolean", True)
        await store.set("null", None)
        await store.set("list", [1, 2, 3])
        await store.set("dict", {"nested": {"deep": "value"}})

        # Verify retrieval
        assert await store.get("string") == "test"
        assert await store.get("number") == 42
        assert await store.get("float") == 3.14
        assert await store.get("boolean") is True
        assert await store.get("null") is None
        assert await store.get("list") == [1, 2, 3]
        assert await store.get("dict") == {"nested": {"deep": "value"}}

    async def test_disk_store_update_existing_key(self, tmp_path):
        """Test updating an existing key's value."""
        store = DiskStore(path=tmp_path)

        # Set initial value
        await store.set("update_key", "initial_value")
        assert await store.get("update_key") == "initial_value"

        # Update value
        await store.set("update_key", "updated_value")
        assert await store.get("update_key") == "updated_value"

    async def test_disk_store_special_characters_in_keys(self, tmp_path):
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
            await store.set(key, f"value_for_{key}")
            assert await store.get(key) == f"value_for_{key}"
            assert store.has(key)

        # Verify list_keys returns all
        keys = await store.list_keys()
        assert len(keys) == len(special_keys)
        assert set(keys) == set(special_keys)
