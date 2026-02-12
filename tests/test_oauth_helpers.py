"""Tests for OAuth helpers and OAuthIntegration."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthToken,
)

from universal_mcp.integrations.integration import OAuthIntegration
from universal_mcp.integrations.oauth_helpers import (
    StoreTokenStorage,
    discover_oauth_metadata,
)
from universal_mcp.stores import MemoryStore

# -- StoreTokenStorage tests --

@pytest.mark.asyncio
async def test_store_token_storage_get_tokens_empty():
    """StoreTokenStorage.get_tokens() returns None for empty store."""
    store = MemoryStore()
    ts = StoreTokenStorage(store, "https://example.com")
    result = await ts.get_tokens()
    assert result is None


@pytest.mark.asyncio
async def test_store_token_storage_set_and_get_tokens():
    """StoreTokenStorage can store and retrieve OAuthToken."""
    store = MemoryStore()
    ts = StoreTokenStorage(store, "https://example.com")

    token = OAuthToken(
        access_token="test-access-token",
        token_type="bearer",
        expires_in=3600,
        refresh_token="test-refresh-token",
        scope="read write",
    )
    await ts.set_tokens(token)

    result = await ts.get_tokens()
    assert result is not None
    assert result.access_token == "test-access-token"
    assert result.token_type.lower() == "bearer"  # Case-insensitive check
    assert result.refresh_token == "test-refresh-token"


@pytest.mark.asyncio
async def test_store_token_storage_get_client_info_empty():
    """StoreTokenStorage.get_client_info() returns None for empty store."""
    store = MemoryStore()
    ts = StoreTokenStorage(store, "https://example.com")
    result = await ts.get_client_info()
    assert result is None


@pytest.mark.asyncio
async def test_store_token_storage_set_and_get_client_info():
    """StoreTokenStorage can store and retrieve OAuthClientInformationFull."""
    store = MemoryStore()
    ts = StoreTokenStorage(store, "https://example.com")

    from pydantic import AnyUrl
    client_info = OAuthClientInformationFull(
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uris=[AnyUrl("http://localhost:8080/callback")],
    )
    await ts.set_client_info(client_info)

    result = await ts.get_client_info()
    assert result is not None
    assert result.client_id == "test-client-id"
    assert result.client_secret == "test-client-secret"


@pytest.mark.asyncio
async def test_store_token_storage_key_namespacing():
    """Different server URLs use different storage keys."""
    store = MemoryStore()
    ts1 = StoreTokenStorage(store, "https://server1.com")
    ts2 = StoreTokenStorage(store, "https://server2.com")

    token1 = OAuthToken(access_token="token1", token_type="bearer")
    token2 = OAuthToken(access_token="token2", token_type="bearer")

    await ts1.set_tokens(token1)
    await ts2.set_tokens(token2)

    result1 = await ts1.get_tokens()
    result2 = await ts2.get_tokens()
    assert result1.access_token == "token1"
    assert result2.access_token == "token2"


# -- discover_oauth_metadata tests --

@pytest.mark.asyncio
async def test_discover_oauth_metadata_no_server():
    """Returns None, None when server is unreachable."""
    with patch("universal_mcp.integrations.oauth_helpers.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client_cls.return_value = mock_client

        result = await discover_oauth_metadata("https://unreachable.com")
        assert result == (None, None, None)


@pytest.mark.asyncio
async def test_discover_oauth_metadata_no_oauth():
    """Returns None, None when server doesn't use OAuth (returns 200)."""
    with patch("universal_mcp.integrations.oauth_helpers.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        # Server returns 200 (no auth needed), and well-known endpoints return 404
        ok_response = MagicMock(spec=httpx.Response)
        ok_response.status_code = 200
        ok_response.headers = {}

        not_found_response = MagicMock(spec=httpx.Response)
        not_found_response.status_code = 404
        not_found_response.aread = AsyncMock(return_value=b"Not Found")

        mock_client.get = AsyncMock(side_effect=[ok_response, not_found_response, not_found_response, not_found_response])
        mock_client_cls.return_value = mock_client

        auth_meta, prm, www_scope = await discover_oauth_metadata("https://no-oauth.com")
        assert auth_meta is None
        assert www_scope is None


# -- OAuthIntegration tests --

def test_oauth_integration_init():
    """OAuthIntegration stores all config properly."""
    integration = OAuthIntegration(
        name="test",
        client_id="cid",
        client_secret="csec",
        auth_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
        scopes=["read", "write"],
    )
    assert integration.client_id == "cid"
    assert integration.client_secret == "csec"
    assert integration.auth_url == "https://auth.example.com/authorize"
    assert integration.token_url == "https://auth.example.com/token"
    assert integration.scopes == ["read", "write"]
    assert integration.type == "oauth2"
    assert integration._pkce is None
    assert integration._server_url is None


def test_oauth_integration_get_authorization_url():
    """get_authorization_url generates valid URL with PKCE."""
    integration = OAuthIntegration(
        name="test",
        client_id="my-client",
        client_secret="my-secret",
        auth_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
        scopes=["read", "write"],
    )

    url = integration.get_authorization_url(
        redirect_uri="http://localhost:8080/callback",
        state="test-state-123",
    )

    assert "https://auth.example.com/authorize?" in url
    assert "response_type=code" in url
    assert "client_id=my-client" in url
    assert "redirect_uri=http" in url
    assert "state=test-state-123" in url
    assert "code_challenge=" in url
    assert "code_challenge_method=S256" in url
    assert "scope=read+write" in url

    # PKCE should be stored
    assert integration._pkce is not None
    assert integration._pkce.code_verifier
    assert integration._pkce.code_challenge


def test_oauth_integration_get_authorization_url_generates_state():
    """get_authorization_url generates state if not provided."""
    integration = OAuthIntegration(
        name="test",
        client_id="my-client",
        client_secret="",
        auth_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
    )

    url = integration.get_authorization_url(
        redirect_uri="http://localhost:8080/callback",
    )

    assert "state=" in url


@pytest.mark.asyncio
async def test_oauth_integration_exchange_code_for_token():
    """exchange_code_for_token() POSTs to token endpoint and stores result."""
    store = MemoryStore()
    integration = OAuthIntegration(
        name="test",
        client_id="my-client",
        client_secret="my-secret",
        auth_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
        scopes=["read"],
        store=store,
    )

    # Generate PKCE first (simulating auth URL generation)
    integration.get_authorization_url("http://localhost:8080/callback", "test-state")
    assert integration._pkce is not None

    # Mock httpx response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "access_token": "new-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "new-refresh-token",
        "scope": "read",
    }

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        credentials = await integration.exchange_code_for_token(
            code="auth-code-123",
            redirect_uri="http://localhost:8080/callback",
        )

    assert credentials["access_token"] == "new-access-token"
    assert credentials["refresh_token"] == "new-refresh-token"
    assert credentials["token_type"] == "Bearer"

    # PKCE should be cleared after use
    assert integration._pkce is None

    # Credentials should be stored in connection
    stored_creds = await integration.get_credentials()
    assert stored_creds["access_token"] == "new-access-token"


def test_oauth_integration_authorize_returns_instructions():
    """authorize() returns human-readable instructions."""
    integration = OAuthIntegration(
        name="test",
        client_id="cid",
        client_secret="csec",
        auth_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
        scopes=["read"],
    )

    instructions = integration.authorize()
    assert "OAuth flow" in instructions
    assert "read" in instructions


@pytest.mark.asyncio
async def test_oauth_integration_create_connection():
    """create_connection() returns OAuthConnection."""
    from universal_mcp.connections.connection import OAuthConnection

    store = MemoryStore()
    integration = OAuthIntegration(
        name="test",
        client_id="cid",
        client_secret="csec",
        auth_url="https://auth.example.com/authorize",
        token_url="https://auth.example.com/token",
        store=store,
    )

    conn = integration.create_connection(user_id="user1", store=store)
    assert isinstance(conn, OAuthConnection)
