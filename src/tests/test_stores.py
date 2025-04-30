import contextlib
import os

import pytest

from universal_mcp.stores.store import (
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
