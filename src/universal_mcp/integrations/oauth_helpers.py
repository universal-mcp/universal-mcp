"""OAuth helper utilities for MCP URL applications."""

import asyncio
from typing import Any
from urllib.parse import parse_qs, urlparse

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

# py-key-value stores are used directly - they raise KeyError for missing keys


class OAuthCallbackError(Exception):
    """Error during OAuth callback handling."""

    pass


class StoreTokenStorage:
    """Adapts py-key-value store to MCP SDK's TokenStorage protocol."""

    def __init__(self, store, server_url: str):
        """Initialize token storage.

        Args:
            store: py-key-value store instance (DiskStore, MemoryStore, KeyringStore)
            server_url: MCP server URL for key namespacing
        """
        self.store = store
        self.server_url = server_url

    @staticmethod
    def _sanitize_key(key: str) -> str:
        """Sanitize key for filesystem safety.

        Replaces characters that are problematic in file paths.
        """
        return key.replace("://", "_").replace("/", "_").replace(":", "_")

    def _tokens_key(self) -> str:
        """Generate key for OAuth tokens."""
        sanitized_url = self._sanitize_key(self.server_url)
        return f"oauth::{sanitized_url}::tokens"

    def _client_info_key(self) -> str:
        """Generate key for OAuth client info."""
        sanitized_url = self._sanitize_key(self.server_url)
        return f"oauth::{sanitized_url}::client_info"

    async def get_tokens(self) -> OAuthToken | None:
        """Get stored OAuth tokens."""
        try:
            data = await self.store.get(self._tokens_key())
            return OAuthToken(**data) if isinstance(data, dict) else None
        except KeyError:
            return None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        """Store OAuth tokens."""
        # OAuthToken is a Pydantic model, use model_dump(mode='json') for proper serialization
        await self.store.put(self._tokens_key(), tokens.model_dump(mode="json", exclude_none=True))

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        """Get stored OAuth client information."""
        try:
            data = await self.store.get(self._client_info_key())
            return OAuthClientInformationFull(**data) if isinstance(data, dict) else None
        except KeyError:
            return None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        """Store OAuth client information."""
        # Use mode='json' to properly serialize URLs and other Pydantic types
        await self.store.put(self._client_info_key(), client_info.model_dump(mode="json", exclude_none=True))

    async def delete_client_info(self) -> None:
        """Delete stored OAuth client information."""
        import contextlib

        with contextlib.suppress(KeyError):
            await self.store.delete(self._client_info_key())


def parse_callback_url(url: str):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get("code")
    error = query_params.get("error")
    state = query_params.get("state")

    return code, error, state


def start_ngrok_tunnel(port: int) -> tuple[str, Any]:
    """Start an ngrok tunnel to the given local port.

    Requires pyngrok: ``pip install universal-mcp[ngrok]``

    Args:
        port: Local port to tunnel to.

    Returns:
        Tuple of (public_url, tunnel) where public_url is the HTTPS ngrok URL
        and tunnel is the pyngrok tunnel object (needed for cleanup).

    Raises:
        ImportError: If pyngrok is not installed.
    """
    try:
        from pyngrok import ngrok
    except ImportError:
        raise ImportError(
            "pyngrok is required for ngrok support. Install it with: pip install universal-mcp[ngrok]"
        ) from None

    tunnel = ngrok.connect(port, "http")
    public_url = tunnel.public_url
    # Ensure HTTPS
    if public_url.startswith("http://"):
        public_url = public_url.replace("http://", "https://", 1)
    logger.info(f"ngrok tunnel started: {public_url} -> localhost:{port}")
    return public_url, tunnel


def stop_ngrok_tunnel(tunnel: Any) -> None:
    """Stop an ngrok tunnel.

    Args:
        tunnel: The pyngrok tunnel object returned by start_ngrok_tunnel().
    """
    try:
        from pyngrok import ngrok

        ngrok.disconnect(tunnel.public_url)
        logger.info("ngrok tunnel stopped")
    except Exception as e:
        logger.debug(f"Error stopping ngrok tunnel: {e}")


async def run_oauth_callback_server(
    port: int = 0,
    use_ngrok: bool = False,
) -> tuple[str, int, asyncio.Future[tuple[str, str | None]], web.AppRunner, Any]:
    """Start a minimal aiohttp web server to receive OAuth callback.

    Args:
        port: Port to bind to (0 = find free port)
        use_ngrok: If True, start an ngrok tunnel and return the public URL
            as the callback URL. Requires pyngrok to be installed.

    Returns:
        Tuple of (callback_url, actual_port, result_future, runner, ngrok_tunnel) where
        result_future resolves to (code, state) when the callback is received.
        ngrok_tunnel is the pyngrok tunnel object (None when use_ngrok=False).
        The caller MUST call `await runner.cleanup()` when done.
    """
    loop = asyncio.get_running_loop()
    result: asyncio.Future[tuple[str, str | None]] = loop.create_future()

    async def handle_callback_wrapped(request: web.Request) -> web.Response:
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

    async def handle_root(request: web.Request) -> web.Response:
        """Catch-all handler for debugging - logs unexpected requests."""
        path = request.path
        query = dict(request.query)
        logger.debug(f"OAuth callback server received request: {request.method} {path} query={query}")

        # Some OAuth providers redirect to the root or a different path
        code = request.query.get("code")
        if code:
            logger.warning(f"Received OAuth code on unexpected path '{path}', processing anyway...")
            return await handle_callback_wrapped(request)

        return web.Response(
            text=f"<html><body><h1>OAuth Callback Server</h1><p>Waiting for callback on /callback</p><p>Got: {path}</p></body></html>",
            content_type="text/html",
        )

    app = web.Application()
    app.router.add_get("/callback", handle_callback_wrapped)
    app.router.add_get("/{path:.*}", handle_root)  # Catch-all for debugging

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)  # Bind to all interfaces (needed for ngrok)
    await site.start()

    # Get actual port
    actual_port = site._server.sockets[0].getsockname()[1]

    ngrok_tunnel = None
    if use_ngrok:
        public_url, ngrok_tunnel = start_ngrok_tunnel(actual_port)
        callback_url = f"{public_url}/callback"
    else:
        callback_url = f"http://localhost:{actual_port}/callback"

    return callback_url, actual_port, result, runner, ngrok_tunnel


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
    logger.debug(f"Discovering OAuth metadata for {server_url}")
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: GET server_url, look for 401 + WWW-Authenticate header
            try:
                logger.debug(f"Step 1: GET {server_url}")
                response = await client.get(server_url)
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"WWW-Authenticate header: {response.headers.get('www-authenticate')}")
            except httpx.ConnectError as e:
                logger.warning(f"Could not connect to {server_url}: {e}")
                return None, None, None

            prm: ProtectedResourceMetadata | None = None
            www_auth_url: str | None = None
            www_auth_scope: str | None = None

            # Step 2: If 401, extract resource_metadata and scope from WWW-Authenticate
            if response.status_code == 401:
                logger.debug("Step 2: Extracting metadata from WWW-Authenticate header")
                www_auth_url = extract_resource_metadata_from_www_auth(response)
                www_auth_scope = extract_scope_from_www_auth(response)
                logger.debug(f"Extracted: www_auth_url={www_auth_url}, scope={www_auth_scope}")

            # Step 3: Try to discover protected resource metadata
            logger.debug("Step 3: Discovering protected resource metadata")
            prm_urls = build_protected_resource_metadata_discovery_urls(www_auth_url, server_url)
            logger.debug(f"Trying PRM URLs: {prm_urls}")
            for prm_url in prm_urls:
                try:
                    logger.debug(f"Trying PRM URL: {prm_url}")
                    prm_response = await client.get(prm_url)
                    logger.debug(f"PRM response status: {prm_response.status_code}")
                    prm = await handle_protected_resource_response(prm_response)
                    if prm:
                        logger.debug(f"Found PRM: {prm}")
                        break
                except httpx.ConnectError as e:
                    logger.debug(f"PRM URL {prm_url} failed: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"PRM URL {prm_url} error: {e}")
                    continue

            # Step 4: Get authorization server URL
            auth_server_url = str(prm.authorization_servers[0]) if prm and prm.authorization_servers else server_url
            logger.debug(f"Step 4: Auth server URL: {auth_server_url}")

            # Step 5: Discover authorization server metadata
            logger.debug("Step 5: Discovering authorization server metadata")
            auth_urls = build_oauth_authorization_server_metadata_discovery_urls(auth_server_url, server_url)

            # Add fallback: try base domain without path segments
            # E.g., https://mcp.linear.app/.well-known/oauth-authorization-server
            from urllib.parse import urlparse

            parsed = urlparse(server_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            fallback_url = f"{base_url}/.well-known/oauth-authorization-server"
            if fallback_url not in auth_urls:
                auth_urls.append(fallback_url)
                logger.debug(f"Added fallback URL: {fallback_url}")

            logger.debug(f"Trying auth URLs: {auth_urls}")

            asm: OAuthMetadata | None = None
            for auth_url in auth_urls:
                try:
                    logger.debug(f"Trying auth URL: {auth_url}")
                    auth_response = await client.get(auth_url)
                    logger.debug(f"Auth response status: {auth_response.status_code}")
                    should_continue, asm = await handle_auth_metadata_response(auth_response)
                    if asm:
                        logger.info(f"Found OAuth metadata at {auth_url}")
                        break
                    if not should_continue:
                        logger.debug(f"Stopping auth discovery at {auth_url}")
                        break
                except httpx.ConnectError as e:
                    logger.debug(f"Auth URL {auth_url} failed: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"Auth URL {auth_url} error: {e}")
                    continue

            if asm:
                logger.info(f"OAuth discovery successful for {server_url}")
            else:
                logger.warning(f"OAuth metadata not found for {server_url}")

            return asm, prm, www_auth_scope

    except Exception as e:
        logger.error(f"Error discovering OAuth metadata for {server_url}: {e}", exc_info=True)
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

    logger.debug(
        f"register_oauth_client: server_url={server_url}, client_name={client_name}, "
        f"redirect_uris={redirect_uris}, scopes={scopes}"
    )

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
    request = create_client_registration_request(auth_metadata, client_metadata, server_url)
    logger.debug(f"Registration endpoint: {request.url}, method={request.method}")

    # Send registration request
    async with httpx.AsyncClient() as client:
        response = await client.send(request)

    logger.debug(f"Registration response: status={response.status_code}")
    if response.status_code != 200 and response.status_code != 201:
        logger.error(f"Client registration failed: status={response.status_code}, body={response.text[:500]}")

    # Parse and return response
    client_info = await handle_registration_response(response)
    logger.info(f"OAuth client registered: client_id={client_info.client_id}")
    return client_info
