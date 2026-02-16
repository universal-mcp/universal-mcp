"""Tests for MCP Client working with Integrations."""

import pytest

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import ApiKeyIntegration, OAuthIntegration


class MockAPIApp(APIApplication):
    """Mock API application for testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://api.example.com"

    def list_tools(self):
        """Return empty tool list for testing."""
        return []


class TestApplicationWithIntegration:
    """Test applications work with new Integration/Connection architecture."""

    @pytest.mark.asyncio
    async def test_api_application_with_api_key_integration(self):
        """Test APIApplication can get credentials from ApiKeyIntegration."""
        integration = ApiKeyIntegration("TEST_API")
        await integration.set_api_key("test_key_123")

        # Create application with integration
        app = MockAPIApp(name="test_app", integration=integration)

        # Verify application can get headers
        headers = await app._get_headers()
        assert headers == {"Authorization": "Bearer test_key_123"}

    @pytest.mark.asyncio
    async def test_api_application_async_credentials(self):
        """Test APIApplication can get credentials asynchronously."""
        integration = ApiKeyIntegration("TEST_API")
        await integration.set_api_key("async_key_456")

        app = MockAPIApp(name="test_app", integration=integration)

        # Verify async header retrieval works
        headers = await app._get_headers()
        assert headers == {"Authorization": "Bearer async_key_456"}

    @pytest.mark.asyncio
    async def test_api_application_with_oauth_integration(self):
        """Test APIApplication works with OAuth tokens."""
        integration = OAuthIntegration(
            name="GITHUB",
            client_id="client_123",
            client_secret="secret_456",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
        )

        # Set user tokens
        conn = integration.get_default_connection()
        await conn.set_credentials({
            "access_token": "gho_user_token",
            "refresh_token": "ghr_refresh",
        })

        app = MockAPIApp(name="test_app", integration=integration)

        # Verify application can get OAuth headers
        headers = await app._get_headers()
        assert headers == {"Authorization": "Bearer gho_user_token"}

    @pytest.mark.asyncio
    async def test_api_application_multi_user_connections(self):
        """Test application with multiple user connections."""
        integration = ApiKeyIntegration("GITHUB")

        # Create connections for different users
        alice_conn = integration.create_connection(user_id="alice")
        await alice_conn.set_credentials({"api_key": "alice_key"})

        bob_conn = integration.create_connection(user_id="bob")
        await bob_conn.set_credentials({"api_key": "bob_key"})

        # Application uses default connection
        app = MockAPIApp(name="test_app", integration=integration)
        await integration.set_api_key("default_key")

        headers = await app._get_headers()
        assert headers == {"Authorization": "Bearer default_key"}

    @pytest.mark.asyncio
    async def test_api_application_no_integration(self):
        """Test application works without integration."""
        app = MockAPIApp(name="test_app", integration=None)

        # Should return empty headers
        headers = await app._get_headers()
        assert headers == {}

    @pytest.mark.asyncio
    async def test_api_application_with_direct_headers(self):
        """Test application with direct headers in credentials."""
        integration = ApiKeyIntegration("TEST_API")

        # Set credentials with direct headers
        await integration.set_credentials({
            "headers": {
                "Authorization": "Custom custom_token",
                "X-API-Key": "another_key",
            }
        })

        app = MockAPIApp(name="test_app", integration=integration)
        headers = await app._get_headers()

        assert headers == {
            "Authorization": "Custom custom_token",
            "X-API-Key": "another_key",
        }


class TestBackwardCompatibility:
    """Test that existing code patterns still work."""

    @pytest.mark.asyncio
    async def test_old_api_key_pattern(self):
        """Test old-style API key usage still works."""
        # Old pattern: directly set API key
        integration = ApiKeyIntegration("GITHUB")
        await integration.set_api_key("ghp_old_pattern")

        app = MockAPIApp(name="github_app", integration=integration)

        # Verify it still works
        headers = await app._get_headers()
        assert headers == {"Authorization": "Bearer ghp_old_pattern"}

    @pytest.mark.asyncio
    async def test_old_credentials_dict_pattern(self):
        """Test old-style credentials dict still works."""
        integration = ApiKeyIntegration("TEST_API")

        # Old pattern: set_credentials with dict
        await integration.set_credentials({"api_key": "old_dict_key"})

        app = MockAPIApp(name="test_app", integration=integration)
        headers = await app._get_headers()

        assert headers == {"Authorization": "Bearer old_dict_key"}

    @pytest.mark.asyncio
    async def test_store_key_format(self):
        """Test API key storage uses correct format (in-memory round-trip)."""
        # Create integration and set credentials
        integration = ApiKeyIntegration("GITHUB")
        await integration.set_credentials({"api_key": "test_key_value"})

        # Should work with new format
        app = MockAPIApp(name="github_app", integration=integration)
        headers = await app._get_headers()

        assert headers == {"Authorization": "Bearer test_key_value"}

        # Verify in-memory round-trip (store is managed by SDK, not integration)
        creds = await integration.get_credentials()
        assert creds == {"api_key": "test_key_value"}

        # Verify store_key format via connection
        conn = integration.get_default_connection()
        assert conn.store_key == "connection::GITHUB_API_KEY::default"


class TestIntegrationErrorHandling:
    """Test error handling in integration scenarios."""

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_error(self):
        """Test that missing credentials are handled gracefully."""
        from universal_mcp.exceptions import NotAuthorizedError

        integration = ApiKeyIntegration("MISSING_API")

        app = MockAPIApp(name="test_app", integration=integration)

        # Should raise NotAuthorizedError when getting headers
        with pytest.raises(NotAuthorizedError):
            await app._get_headers()

    @pytest.mark.asyncio
    async def test_invalid_credentials_format(self):
        """Test that invalid credential format is caught."""
        integration = ApiKeyIntegration("TEST_API")

        # py-key-value requires dict values, empty dict is valid
        # Test with non-dict type
        with pytest.raises((ValueError, TypeError)):
            await integration.set_credentials(None)  # type: ignore

        with pytest.raises((ValueError, TypeError)):
            await integration.set_credentials("not_a_dict")  # type: ignore


class TestIntegrationWithRealWorld:
    """Test real-world usage patterns."""

    @pytest.mark.asyncio
    async def test_github_integration_pattern(self):
        """Test typical GitHub integration pattern."""
        # Setup GitHub integration
        github = ApiKeyIntegration("GITHUB_TOKEN")
        await github.set_api_key("ghp_real_token_example")

        # Create GitHub application
        app = MockAPIApp(name="github", integration=github)
        app.base_url = "https://api.github.com"

        # Verify headers are correct for GitHub API
        headers = await app._get_headers()
        assert headers["Authorization"] == "Bearer ghp_real_token_example"

    @pytest.mark.asyncio
    async def test_oauth_app_pattern(self):
        """Test typical OAuth application pattern."""
        # Setup OAuth integration (e.g., Google Calendar)
        oauth = OAuthIntegration(
            name="GOOGLE_CALENDAR",
            client_id="your-client-id.apps.googleusercontent.com",
            client_secret="your-client-secret",
            auth_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/calendar"],
        )

        # User completes OAuth flow, tokens stored
        user_conn = oauth.get_default_connection()
        await user_conn.set_credentials({
            "access_token": "ya29.user_access_token",
            "refresh_token": "1//user_refresh_token",
            "expires_at": 1234567890,
        })

        # Application uses OAuth integration
        app = MockAPIApp(name="google_calendar", integration=oauth)
        app.base_url = "https://www.googleapis.com/calendar/v3"

        # Verify OAuth token is used
        headers = await app._get_headers()
        assert headers["Authorization"] == "Bearer ya29.user_access_token"

    @pytest.mark.asyncio
    async def test_async_api_calls(self):
        """Test async API call pattern with integration."""
        integration = ApiKeyIntegration("API_KEY")
        await integration.set_api_key("async_test_key")

        app = MockAPIApp(name="async_app", integration=integration)

        # Test async client creation
        async with app.get_async_client() as client:
            assert client.base_url == "https://api.example.com"
            assert "Authorization" in client.headers
            assert client.headers["Authorization"] == "Bearer async_test_key"
