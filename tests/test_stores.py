"""Tests for Store classes using py-key-value library."""

import tempfile
from pathlib import Path

import pytest

from universal_mcp.stores import DiskStore, KeyringStore, MemoryStore, create_store


class TestMemoryStore:
    """Tests for MemoryStore (py-key-value)."""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test basic set and get operations."""
        store = MemoryStore()
        test_data = {"key": "value", "nested": {"data": 123}}

        await store.put("test_key", test_data)
        result = await store.get("test_key")

        assert result == test_data

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self):
        """Test that getting nonexistent key returns None."""
        store = MemoryStore()
        result = await store.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete operation."""
        store = MemoryStore()
        await store.put("test_key", {"value": "test"})

        # Delete doesn't raise on nonexistent in py-key-value
        await store.delete("test_key")

        result = await store.get("test_key")
        assert result is None


class TestDiskStore:
    """Tests for DiskStore (py-key-value)."""

    @pytest.mark.asyncio
    async def test_persistence(self):
        """Test that data persists across store instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_data = {"persistent": "data", "value": 42}

            # Write with first instance
            store1 = DiskStore(directory=tmpdir)
            await store1.put("persist_key", test_data)

            # Read with second instance
            store2 = DiskStore(directory=tmpdir)
            result = await store2.get("persist_key")

            assert result == test_data

    @pytest.mark.asyncio
    async def test_directory_creation(self):
        """Test that store creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "nested" / "path"
            store = DiskStore(directory=nested_path)

            assert nested_path.exists()

    @pytest.mark.asyncio
    async def test_default_directory(self):
        """Test default directory is created and works."""
        store = create_store("disk")  # Uses factory which provides default
        test_data = {"test": "data"}

        await store.put("test_key", test_data)
        result = await store.get("test_key")

        assert result == test_data


class TestKeyringStore:
    """Tests for KeyringStore (py-key-value)."""

    @pytest.mark.asyncio
    async def test_basic_operations(self):
        """Test basic keyring store operations."""
        store = KeyringStore(service_name="test_service")

        # Just test it works (service_name is internal to py-key-value)
        test_data = {"key": "value"}
        await store.put("test_key", test_data)
        result = await store.get("test_key")

        assert result == test_data

    @pytest.mark.asyncio
    async def test_can_create_with_service_name(self):
        """Test keyring store can be created with service name."""
        # This should not raise
        store = KeyringStore(service_name="custom_service")
        assert isinstance(store, KeyringStore)


class TestStoreFactory:
    """Tests for create_store factory function."""

    @pytest.mark.asyncio
    async def test_create_memory_store(self):
        """Test factory creates MemoryStore."""
        store = create_store("memory")
        assert isinstance(store, MemoryStore)

    @pytest.mark.asyncio
    async def test_create_disk_store(self):
        """Test factory creates DiskStore with custom directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = create_store("disk", directory=tmpdir)
            assert isinstance(store, DiskStore)

            # Test it works
            await store.put("test", {"data": "value"})
            result = await store.get("test")
            assert result == {"data": "value"}

    @pytest.mark.asyncio
    async def test_create_keyring_store(self):
        """Test factory creates KeyringStore."""
        store = create_store("keyring", service_name="custom_service")
        assert isinstance(store, KeyringStore)

    @pytest.mark.asyncio
    async def test_default_store_type(self):
        """Test factory defaults to DiskStore."""
        store = create_store()
        assert isinstance(store, DiskStore)

    @pytest.mark.asyncio
    async def test_invalid_store_type(self):
        """Test factory raises error for invalid type."""
        with pytest.raises(ValueError, match="Unsupported store type"):
            create_store("invalid_type")

    @pytest.mark.asyncio
    async def test_case_insensitive(self):
        """Test factory handles case-insensitive types."""
        store1 = create_store("MEMORY")
        store2 = create_store("Memory")
        assert isinstance(store1, MemoryStore)
        assert isinstance(store2, MemoryStore)
