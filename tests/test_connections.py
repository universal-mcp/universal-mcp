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
        assert conn.store_key == "GITHUB_API_KEY::user_123"

    @pytest.mark.asyncio
    async def test_default_user_id(self):
        """Test default user_id is 'default'."""
        conn = ApiKeyConnection("TEST_API_KEY", store=MemoryStore())
        assert conn.user_id == "default"
        assert conn.store_key == "TEST_API_KEY::default"

    @pytest.mark.asyncio
    async def test_set_and_get_credentials(self):
        """Test basic CRUD operations."""
        store = MemoryStore()
        conn = ApiKeyConnection("TEST_API_KEY", store=store)

        # Set credentials
        await conn.set_credentials({"api_key": "test_key_123"})

        # Verify stored
        assert await store.get("TEST_API_KEY::default") == "test_key_123"

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

        # Verify in store
        assert await store.get("TEST_API_KEY::default") == "property_key"

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing credentials raise NotAuthorizedError."""
        store = MemoryStore()
        conn = ApiKeyConnection("MISSING_API_KEY", store=store)

        with pytest.raises(NotAuthorizedError, match="No API key found"):
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
    async def test_backward_compatibility_migration(self):
        """Test migration from old key format to new format."""
        store = MemoryStore()

        # Set key in old format
        await store.set("GITHUB_API_KEY", "old_format_key")

        # Create connection (should migrate)
        conn = ApiKeyConnection("GITHUB_API_KEY", user_id="default", store=store)
        creds = await conn.get_credentials()

        # Verify migration
        assert creds == {"api_key": "old_format_key"}
        assert await store.get("GITHUB_API_KEY::default") == "old_format_key"

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
        assert conn.store_key == "GITHUB_OAUTH::user_123"

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

        with pytest.raises(ValueError, match="require access_token"):
            await conn.set_credentials({"refresh_token": "only_refresh"})

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing OAuth tokens raise NotAuthorizedError."""
        store = MemoryStore()
        conn = OAuthConnection("MISSING_OAUTH", store=store)

        with pytest.raises(NotAuthorizedError, match="No OAuth token found"):
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

        # Verify store keys
        assert await store.get("GITHUB_API_KEY::alice") == "alice_key"
        assert await store.get("GITHUB_API_KEY::bob") == "bob_key"
