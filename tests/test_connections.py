"""Tests for Connection classes."""

import pytest

from universal_mcp.connections import ApiKeyConnection, OAuthConnection
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.stores import MemoryStore


class TestApiKeyConnection:
    """Tests for ApiKeyConnection."""

    @pytest.mark.asyncio
    async def test_store_key_format(self):
        """Test connection store key format."""
        conn = ApiKeyConnection("GITHUB_API_KEY", user_id="user_123", store=MemoryStore())
        assert conn.store_key == "connection::GITHUB_API_KEY::user_123"

    @pytest.mark.asyncio
    async def test_default_user_id(self):
        """Test default user_id is 'default'."""
        conn = ApiKeyConnection("TEST_API_KEY", store=MemoryStore())
        assert conn.user_id == "default"
        assert conn.store_key == "connection::TEST_API_KEY::default"

    @pytest.mark.asyncio
    async def test_set_and_get_credentials(self):
        """Test basic CRUD operations."""
        store = MemoryStore()
        conn = ApiKeyConnection("TEST_API_KEY", store=store)

        # Set credentials
        await conn.set_credentials({"api_key": "test_key_123"})

        # Verify stored as dict (py-key-value requires Mapping type)
        stored = await store.get("connection::TEST_API_KEY::default")
        assert stored == {"api_key": "test_key_123"}

        # Get credentials
        creds = await conn.get_credentials()
        assert creds == {"api_key": "test_key_123"}

    @pytest.mark.asyncio
    async def test_api_key_property(self):
        """Test api_key methods."""
        store = MemoryStore()
        conn = ApiKeyConnection("TEST_API_KEY", store=store)

        # Set via method
        await conn.set_api_key("property_key")

        # Get via method
        assert await conn.get_api_key() == "property_key"

        # Verify in store as dict
        stored = await store.get("connection::TEST_API_KEY::default")
        assert stored == {"api_key": "property_key"}

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing credentials raise NotAuthorizedError."""
        store = MemoryStore()
        conn = ApiKeyConnection("MISSING_API_KEY", store=store)

        with pytest.raises((NotAuthorizedError, KeyError)):
            await conn.get_credentials()

    @pytest.mark.asyncio
    async def test_no_store_raises_error(self):
        """Test that connection without store raises error."""
        conn = ApiKeyConnection("TEST_API_KEY", store=None)

        with pytest.raises(NotAuthorizedError, match="No store configured"):
            await conn.get_credentials()

    @pytest.mark.asyncio
    async def test_status_transitions(self):
        """Test connection status transitions."""
        store = MemoryStore()
        conn = ApiKeyConnection("TEST_API_KEY", store=store)

        assert conn.status == "pending"

        await conn.set_credentials({"api_key": "test"})
        assert conn.status == "active"

        conn.mark_expired()
        assert conn.status == "expired"

    @pytest.mark.asyncio
    async def test_async_get_credentials(self):
        """Test async credentials retrieval."""
        store = MemoryStore()
        conn = ApiKeyConnection("TEST_API_KEY", store=store)
        await conn.set_credentials({"api_key": "async_test"})

        creds = await conn.get_credentials()
        assert creds == {"api_key": "async_test"}


class TestOAuthConnection:
    """Tests for OAuthConnection."""

    @pytest.mark.asyncio
    async def test_store_key_format(self):
        """Test OAuth connection store key format."""
        conn = OAuthConnection("GITHUB_OAUTH", user_id="user_123", store=MemoryStore())
        assert conn.store_key == "connection::GITHUB_OAUTH::user_123"

    @pytest.mark.asyncio
    async def test_set_and_get_credentials(self):
        """Test OAuth token storage and retrieval."""
        store = MemoryStore()
        conn = OAuthConnection("GITHUB_OAUTH", store=store)

        # Set OAuth tokens
        tokens = {
            "access_token": "token_abc",
            "refresh_token": "refresh_xyz",
            "expires_at": 1234567890,
        }
        await conn.set_credentials(tokens)

        # Get credentials
        creds = await conn.get_credentials()
        assert creds == tokens

    @pytest.mark.asyncio
    async def test_missing_access_token_raises_error(self):
        """Test that credentials without access_token raise error."""
        store = MemoryStore()
        conn = OAuthConnection("GITHUB_OAUTH", store=store)

        # OAuth connections require access_token
        with pytest.raises(ValueError, match="access_token"):
            await conn.set_credentials({"refresh_token": "only_refresh"})

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing OAuth tokens raise NotAuthorizedError."""
        store = MemoryStore()
        conn = OAuthConnection("MISSING_OAUTH", store=store)

        # py-key-value raises KeyError for missing keys
        with pytest.raises((NotAuthorizedError, KeyError)):
            await conn.get_credentials()


class TestMultiUser:
    """Tests for multi-user connection scenarios."""

    @pytest.mark.asyncio
    async def test_multiple_connections_per_integration(self):
        """Test multiple users with different credentials."""
        store = MemoryStore()

        # User 1 connection
        conn1 = ApiKeyConnection("GITHUB_API_KEY", user_id="alice", store=store)
        await conn1.set_credentials({"api_key": "alice_key"})

        # User 2 connection
        conn2 = ApiKeyConnection("GITHUB_API_KEY", user_id="bob", store=store)
        await conn2.set_credentials({"api_key": "bob_key"})

        # Verify isolation
        assert await conn1.get_credentials() == {"api_key": "alice_key"}
        assert await conn2.get_credentials() == {"api_key": "bob_key"}

        # Verify store keys (stored as dicts)
        assert await store.get("connection::GITHUB_API_KEY::alice") == {"api_key": "alice_key"}
        assert await store.get("connection::GITHUB_API_KEY::bob") == {"api_key": "bob_key"}
