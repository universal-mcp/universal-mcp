"""OAuth helper utilities for MCP URL applications."""

import asyncio

import httpx
from aiohttp import web
from loguru import logger
from mcp.client.auth.utils import (
    build_oauth_authorization_server_metadata_discovery_urls,
    build_protected_resource_metadata_discovery_urls,
    create_client_registration_request,
    extract_resource_metadata_from_www_auth,
    extract_scope_from_www_auth,
    handle_auth_metadata_response,
    handle_protected_resource_response,
    handle_registration_response,
)
from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthClientMetadata,
    OAuthMetadata,
    OAuthToken,
    ProtectedResourceMetadata,
)

from universal_mcp.exceptions import KeyNotFoundError
from universal_mcp.stores.store import BaseStore


class OAuthCallbackError(Exception):
    """Error during OAuth callback handling."""
    pass


class StoreTokenStorage:
    """Adapts BaseStore to MCP SDK's TokenStorage protocol."""

    def __init__(self, store: BaseStore, server_url: str):
        self.store = store
        self.server_url = server_url

    def _tokens_key(self) -> str:
        return f"oauth::{self.server_url}::tokens"

    def _client_info_key(self) -> str:
        return f"oauth::{self.server_url}::client_info"

    async def get_tokens(self) -> OAuthToken | None:
        """Get stored OAuth tokens."""
        try:
            data = await self.store.get(self._tokens_key())
            return OAuthToken(**data) if isinstance(data, dict) else None
        except KeyNotFoundError:
            return None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        """Store OAuth tokens."""
        # OAuthToken is a Pydantic model, use model_dump()
        await self.store.set(self._tokens_key(), tokens.model_dump(exclude_none=True))

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        """Get stored OAuth client information."""
        try:
            data = await self.store.get(self._client_info_key())
            return OAuthClientInformationFull(**data) if isinstance(data, dict) else None
        except KeyNotFoundError:
            return None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        """Store OAuth client information."""
        await self.store.set(self._client_info_key(), client_info.model_dump(exclude_none=True))


async def run_oauth_callback_server(
    port: int = 0,
) -> tuple[str, int, asyncio.Future[tuple[str, str | None]], web.AppRunner]:
    """Start a minimal aiohttp web server to receive OAuth callback.

    Args:
        port: Port to bind to (0 = find free port)

    Returns:
        Tuple of (callback_url, actual_port, result_future, runner) where
        result_future resolves to (code, state) when the callback is received.
        The caller MUST call `await runner.cleanup()` when done.
    """
    loop = asyncio.get_running_loop()
    result: asyncio.Future[tuple[str, str | None]] = loop.create_future()

    async def handle_callback(request: web.Request) -> web.Response:
        """Handle OAuth callback request."""
        code = request.query.get("code")
        error = request.query.get("error")
        state = request.query.get("state")

        if error:
            if not result.done():
                result.set_exception(OAuthCallbackError(f"OAuth error: {error}"))
            return web.Response(
                text="<html><body><h1>Authorization Failed</h1><p>You can close this window.</p></body></html>",
                content_type="text/html",
            )

        if not code:
            if not result.done():
                result.set_exception(OAuthCallbackError("No authorization code received"))
            return web.Response(
                text="<html><body><h1>Error</h1><p>No code received.</p></body></html>",
                content_type="text/html",
            )

        if not result.done():
            result.set_result((code, state))
        return web.Response(
            text="<html><body><h1>Authorization Successful</h1><p>You can close this window.</p></body></html>",
            content_type="text/html",
        )

    app = web.Application()
    app.router.add_get("/callback", handle_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port)
    await site.start()

    # Get actual port
    actual_port = site._server.sockets[0].getsockname()[1]
    callback_url = f"http://localhost:{actual_port}/callback"

    return callback_url, actual_port, result, runner


async def discover_oauth_metadata(
    server_url: str,
) -> tuple[OAuthMetadata | None, ProtectedResourceMetadata | None, str | None]:
    """Discover OAuth metadata from a server URL.

    Uses httpx + MCP SDK helpers to discover OAuth metadata.

    Args:
        server_url: MCP server URL

    Returns:
        Tuple of (OAuthMetadata, ProtectedResourceMetadata, www_authenticate_scope).
        All elements may be None if discovery fails.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: GET server_url, look for 401 + WWW-Authenticate header
            try:
                response = await client.get(server_url)
            except httpx.ConnectError:
                logger.warning(f"Could not connect to {server_url}")
                return None, None, None

            prm: ProtectedResourceMetadata | None = None
            www_auth_url: str | None = None
            www_auth_scope: str | None = None

            # Step 2: If 401, extract resource_metadata and scope from WWW-Authenticate
            if response.status_code == 401:
                www_auth_url = extract_resource_metadata_from_www_auth(response)
                www_auth_scope = extract_scope_from_www_auth(response)

            # Step 3: Try to discover protected resource metadata
            prm_urls = build_protected_resource_metadata_discovery_urls(www_auth_url, server_url)
            for prm_url in prm_urls:
                try:
                    prm_response = await client.get(prm_url)
                    prm = await handle_protected_resource_response(prm_response)
                    if prm:
                        break
                except httpx.ConnectError:
                    continue

            # Step 4: Get authorization server URL
            auth_server_url = str(prm.authorization_servers[0]) if prm and prm.authorization_servers else server_url

            # Step 5: Discover authorization server metadata
            auth_urls = build_oauth_authorization_server_metadata_discovery_urls(
                auth_server_url, server_url
            )

            asm: OAuthMetadata | None = None
            for auth_url in auth_urls:
                try:
                    auth_response = await client.get(auth_url)
                    should_continue, asm = await handle_auth_metadata_response(auth_response)
                    if asm:
                        break
                    if not should_continue:
                        break
                except httpx.ConnectError:
                    continue

            return asm, prm, www_auth_scope

    except Exception as e:
        logger.error(f"Error discovering OAuth metadata: {e}")
        return None, None, None


async def register_oauth_client(
    auth_metadata: OAuthMetadata,
    server_url: str,
    client_name: str = "Universal MCP",
    redirect_uris: list[str] | None = None,
    scopes: str | None = None,
) -> OAuthClientInformationFull:
    """Register OAuth client dynamically per RFC 7591.

    Args:
        auth_metadata: OAuth authorization server metadata
        server_url: MCP server URL (used as fallback if no registration_endpoint)
        client_name: Human-readable client name
        redirect_uris: List of allowed redirect URIs
        scopes: Space-separated list of scopes to request

    Returns:
        OAuthClientInformationFull with client_id and client_secret

    Raises:
        OAuthRegistrationError: If registration fails
    """
    from pydantic import AnyUrl

    # Convert redirect_uris to AnyUrl
    redirect_uri_objects = [AnyUrl(uri) for uri in (redirect_uris or [])]

    # Build client metadata
    client_metadata = OAuthClientMetadata(
        redirect_uris=redirect_uri_objects,
        client_name=client_name,
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        scope=scopes,
    )

    # Create registration request
    request = create_client_registration_request(
        auth_metadata, client_metadata, server_url
    )

    # Send registration request
    async with httpx.AsyncClient() as client:
        response = await client.send(request)

    # Parse and return response
    client_info = await handle_registration_response(response)
    return client_info
