"""Tests for Integration with Connection separation."""

import pytest

from universal_mcp.connections import ApiKeyConnection
from universal_mcp.integrations import ApiKeyIntegration, OAuthIntegration
from universal_mcp.stores import MemoryStore


class TestApiKeyIntegration:
    """Tests for ApiKeyIntegration with Connection."""

    @pytest.mark.asyncio
    async def test_backward_compatibility_api_key_property(self):
        """Test that old api_key property still works."""
        store = MemoryStore()
        integration = ApiKeyIntegration("TEST", store=store)

        # Old way: set via property
        await integration.set_api_key("test_key_123")

        # Old way: get via property
        assert await integration.get_api_key() == "test_key_123"

    @pytest.mark.asyncio
    async def test_backward_compatibility_get_credentials(self):
        """Test that get_credentials() still works."""
        store = MemoryStore()
        integration = ApiKeyIntegration("TEST", store=store)

        await integration.set_credentials({"api_key": "test_key"})
        creds = await integration.get_credentials()

        assert creds == {"api_key": "test_key"}

    @pytest.mark.asyncio
    async def test_async_get_credentials(self):
        """Test async get_credentials method."""
        store = MemoryStore()
        integration = ApiKeyIntegration("TEST", store=store)
        await integration.set_api_key("async_key")

        creds = await integration.get_credentials()
        assert creds == {"api_key": "async_key"}

    @pytest.mark.asyncio
    async def test_create_connection_multi_user(self):
        """Test creating multiple connections for different users."""
        store = MemoryStore()
        integration = ApiKeyIntegration("GITHUB", store=store)

        # Create connections for different users
        conn1 = integration.create_connection(user_id="alice")
        await conn1.set_credentials({"api_key": "alice_key"})

        conn2 = integration.create_connection(user_id="bob")
        await conn2.set_credentials({"api_key": "bob_key"})

        # Verify isolation
        assert await conn1.get_credentials() == {"api_key": "alice_key"}
        assert await conn2.get_credentials() == {"api_key": "bob_key"}

    @pytest.mark.asyncio
    async def test_default_connection_isolation(self):
        """Test that default connection is separate from user connections."""
        store = MemoryStore()
        integration = ApiKeyIntegration("TEST", store=store)

        # Set via default (old way)
        await integration.set_api_key("default_key")

        # Create user connection
        user_conn = integration.create_connection(user_id="user1")
        await user_conn.set_credentials({"api_key": "user1_key"})

        # Verify isolation
        assert await integration.get_credentials() == {"api_key": "default_key"}
        assert await user_conn.get_credentials() == {"api_key": "user1_key"}

    @pytest.mark.asyncio
    async def test_connection_type(self):
        """Test that ApiKeyIntegration creates ApiKeyConnection."""
        integration = ApiKeyIntegration("TEST", store=MemoryStore())
        conn = integration.create_connection()

        assert isinstance(conn, ApiKeyConnection)

    @pytest.mark.asyncio
    async def test_authorize_message(self):
        """Test authorization instruction message."""
        integration = ApiKeyIntegration("TEST", store=MemoryStore())
        msg = integration.authorize()

        assert "TEST_API_KEY" in msg
        assert "api_key" in msg.lower()

    @pytest.mark.asyncio
    async def test_store_key_format(self):
        """Test API key storage format."""
        store = MemoryStore()

        # Create integration
        integration = ApiKeyIntegration("GITHUB", store=store)

        # Set credentials
        await integration.set_credentials({"api_key": "test_key"})

        # Verify stored with correct key format (always dict)
        stored = await store.get("connection::GITHUB_API_KEY::default")
        assert stored == {"api_key": "test_key"}

        # Get credentials
        creds = await integration.get_credentials()
        assert creds == {"api_key": "test_key"}


class TestOAuthIntegration:
    """Tests for OAuthIntegration."""

    @pytest.mark.asyncio
    async def test_oauth_initialization(self):
        """Test OAuthIntegration initialization with client config."""
        integration = OAuthIntegration(
            name="GITHUB",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            scopes=["repo", "user"],
            store=MemoryStore(),
        )

        # OAuth integrations don't add _API_KEY suffix
        assert integration.name == "GITHUB"
        assert integration.type == "oauth2"
        assert integration.client_id == "client_123"
        assert integration.client_secret == "secret_456"
        assert integration.scopes == ["repo", "user"]

    @pytest.mark.asyncio
    async def test_oauth_create_connection(self):
        """Test creating OAuth connections."""
        integration = OAuthIntegration(
            name="GITHUB",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            store=MemoryStore(),
        )

        conn = integration.create_connection(user_id="alice")
        assert conn.user_id == "alice"
        # OAuth integrations use clean names
        assert conn.integration_name == "GITHUB"

    @pytest.mark.asyncio
    async def test_oauth_authorize_message(self):
        """Test OAuth authorization message includes flow info."""
        integration = OAuthIntegration(
            name="GITHUB",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            scopes=["repo"],
            store=MemoryStore(),
        )

        msg = integration.authorize()
        assert "OAuth" in msg
        assert "https://github.com/login/oauth/authorize" in msg
        assert "repo" in msg

    def test_oauth_methods_implemented(self):
        """Test that OAuth flow methods are implemented and work."""
        integration = OAuthIntegration(
            name="GITHUB",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            store=MemoryStore(),
        )

        # get_authorization_url should return a valid URL with PKCE
        url = integration.get_authorization_url("http://localhost/callback", state="test")
        assert "https://github.com/login/oauth/authorize?" in url
        assert "code_challenge=" in url
        assert "client_id=client_123" in url

    @pytest.mark.asyncio
    async def test_oauth_multi_user(self):
        """Test OAuth with multiple user tokens."""
        store = MemoryStore()
        integration = OAuthIntegration(
            name="GITHUB",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            store=store,
        )

        # Alice's tokens
        alice_conn = integration.create_connection(user_id="alice")
        await alice_conn.set_credentials({"access_token": "alice_token", "refresh_token": "alice_refresh"})

        # Bob's tokens
        bob_conn = integration.create_connection(user_id="bob")
        await bob_conn.set_credentials({"access_token": "bob_token", "refresh_token": "bob_refresh"})

        # Verify isolation
        creds_alice = await alice_conn.get_credentials()
        assert creds_alice["access_token"] == "alice_token"
        creds_bob = await bob_conn.get_credentials()
        assert creds_bob["access_token"] == "bob_token"


class TestIntegrationFactory:
    """Tests for IntegrationFactory."""

    @pytest.mark.asyncio
    async def test_create_api_key_integration(self):
        """Test factory creates ApiKeyIntegration."""
        from universal_mcp.integrations import IntegrationFactory

        integration = IntegrationFactory.create("TEST", integration_type="api_key")
        assert isinstance(integration, ApiKeyIntegration)
        assert integration.type == "api_key"

    @pytest.mark.asyncio
    async def test_create_oauth_integration(self):
        """Test factory creates OAuthIntegration."""
        from universal_mcp.integrations import IntegrationFactory

        integration = IntegrationFactory.create(
            "GITHUB",
            integration_type="oauth2",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://example.com/auth",
            token_url="https://example.com/token",
        )
        assert isinstance(integration, OAuthIntegration)
        assert integration.type == "oauth2"

    @pytest.mark.asyncio
    async def test_unsupported_type_raises_error(self):
        """Test factory raises error for unsupported type."""
        from universal_mcp.integrations import IntegrationFactory

        with pytest.raises(ValueError, match="Unsupported integration type"):
            IntegrationFactory.create("TEST", integration_type="unsupported")
