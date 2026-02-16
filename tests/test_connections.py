"""Tests for Connection classes (store-free, in-memory only)."""

import pytest

from universal_mcp.connections import ApiKeyConnection, OAuthConnection
from universal_mcp.exceptions import NotAuthorizedError


class TestApiKeyConnection:
    """Tests for ApiKeyConnection."""

    @pytest.mark.asyncio
    async def test_store_key_format(self):
        """Test connection store key format."""
        conn = ApiKeyConnection("GITHUB_API_KEY", user_id="user_123")
        assert conn.store_key == "connection::GITHUB_API_KEY::user_123"

    @pytest.mark.asyncio
    async def test_default_user_id(self):
        """Test default user_id is 'default'."""
        conn = ApiKeyConnection("TEST_API_KEY")
        assert conn.user_id == "default"
        assert conn.store_key == "connection::TEST_API_KEY::default"

    @pytest.mark.asyncio
    async def test_set_and_get_credentials(self):
        """Test basic in-memory CRUD operations."""
        conn = ApiKeyConnection("TEST_API_KEY")

        # Set credentials
        await conn.set_credentials({"api_key": "test_key_123"})

        # Get credentials (in-memory round-trip)
        creds = await conn.get_credentials()
        assert creds == {"api_key": "test_key_123"}

    @pytest.mark.asyncio
    async def test_api_key_property(self):
        """Test api_key methods."""
        conn = ApiKeyConnection("TEST_API_KEY")

        # Set via method
        await conn.set_api_key("property_key")

        # Get via method
        assert await conn.get_api_key() == "property_key"

        # Get via get_credentials
        creds = await conn.get_credentials()
        assert creds == {"api_key": "property_key"}

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing credentials raise NotAuthorizedError."""
        conn = ApiKeyConnection("MISSING_API_KEY")

        with pytest.raises(NotAuthorizedError):
            await conn.get_credentials()

    @pytest.mark.asyncio
    async def test_no_credentials_raises_error(self):
        """Test that connection without credentials raises error."""
        conn = ApiKeyConnection("TEST_API_KEY")

        with pytest.raises(NotAuthorizedError):
            await conn.get_credentials()

    @pytest.mark.asyncio
    async def test_status_transitions(self):
        """Test connection status transitions."""
        conn = ApiKeyConnection("TEST_API_KEY")

        assert conn.status == "pending"

        await conn.set_credentials({"api_key": "test"})
        assert conn.status == "active"

        conn.mark_expired()
        assert conn.status == "expired"

    @pytest.mark.asyncio
    async def test_async_get_credentials(self):
        """Test async credentials retrieval."""
        conn = ApiKeyConnection("TEST_API_KEY")
        await conn.set_credentials({"api_key": "async_test"})

        creds = await conn.get_credentials()
        assert creds == {"api_key": "async_test"}


class TestOAuthConnection:
    """Tests for OAuthConnection."""

    @pytest.mark.asyncio
    async def test_store_key_format(self):
        """Test OAuth connection store key format."""
        conn = OAuthConnection("GITHUB_OAUTH", user_id="user_123")
        assert conn.store_key == "connection::GITHUB_OAUTH::user_123"

    @pytest.mark.asyncio
    async def test_set_and_get_credentials(self):
        """Test OAuth token storage and retrieval (in-memory)."""
        conn = OAuthConnection("GITHUB_OAUTH")

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
        conn = OAuthConnection("GITHUB_OAUTH")

        # OAuth connections require access_token
        with pytest.raises(ValueError, match="access_token"):
            await conn.set_credentials({"refresh_token": "only_refresh"})

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing OAuth tokens raise NotAuthorizedError."""
        conn = OAuthConnection("MISSING_OAUTH")

        with pytest.raises(NotAuthorizedError):
            await conn.get_credentials()


class TestMultiUser:
    """Tests for multi-user connection scenarios."""

    @pytest.mark.asyncio
    async def test_multiple_connections_per_integration(self):
        """Test multiple users with different credentials."""
        # User 1 connection
        conn1 = ApiKeyConnection("GITHUB_API_KEY", user_id="alice")
        await conn1.set_credentials({"api_key": "alice_key"})

        # User 2 connection
        conn2 = ApiKeyConnection("GITHUB_API_KEY", user_id="bob")
        await conn2.set_credentials({"api_key": "bob_key"})

        # Verify isolation
        assert await conn1.get_credentials() == {"api_key": "alice_key"}
        assert await conn2.get_credentials() == {"api_key": "bob_key"}

        # Verify store keys are different
        assert conn1.store_key == "connection::GITHUB_API_KEY::alice"
        assert conn2.store_key == "connection::GITHUB_API_KEY::bob"
