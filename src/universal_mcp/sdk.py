"""Universal MCP SDK - Agent-facing API for finding, installing, authorizing, and using MCP applications."""

import json
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from loguru import logger

from universal_mcp.applications.utils import app_from_slug
from universal_mcp.integrations.integration import Integration, IntegrationFactory
from universal_mcp.servers.server import create_server
from universal_mcp.stores import create_store
from universal_mcp.tools.local_registry import LocalRegistry

_DEFAULT_MANIFEST_PATH = Path.home() / ".universal-mcp" / "manifest.json"


class UniversalMCP:
    """Agent-facing SDK for finding, installing, authorizing, and using MCP applications.

    The SDK is the sole owner of the credential store. Integrations and Connections
    are pure in-memory objects; the SDK hydrates them from the store and persists
    changes back.

    Example usage:
        mcp = UniversalMCP()
        mcp.add("github")
        await mcp.authorize("github", api_key="ghp_xxx")
        tools = mcp.list_tools()
        result = await mcp.call_tool("github__create_issue", {"title": "Bug"})
    """

    def __init__(
        self,
        store_type: Literal["disk", "memory", "environment", "keyring", "file"] = "file",
        store_path: Path | None = None,
        store_name: str = "universal_mcp",
        manifest_path: Path | None = None,
    ) -> None:
        self.store = create_store(store_type=store_type, directory=store_path, service_name=store_name)
        self.registry = LocalRegistry()
        self._integrations: dict[str, Integration] = {}
        self._mcp_apps: dict[str, Any] = {}  # MCPApplication instances for lifecycle management
        self._crontab_registry: Any = None  # Lazy-loaded CrontabRegistry
        self._manifest_path = manifest_path or _DEFAULT_MANIFEST_PATH

        # Load existing manifest and re-hydrate apps
        self._load_manifest()

    # -- Store hydration -------------------------------------------------------

    async def _hydrate_credentials(self, slug: str) -> bool:
        """Load credentials from store into the integration's default connection.

        Args:
            slug: Application slug.

        Returns:
            True if credentials were successfully loaded from the store.
        """
        integration = self._integrations.get(slug)
        if not integration:
            return False

        conn = integration.get_default_connection()
        try:
            value = await self.store.get(conn.store_key)
        except KeyError:
            return False

        if not value:
            return False

        # Normalize: if value is a plain string (legacy), wrap it
        if isinstance(value, str):
            value = {"api_key": value}

        try:
            await conn.set_credentials(value)
            return True
        except (ValueError, TypeError):
            return False

    async def hydrate_all(self) -> None:
        """Hydrate credentials for all registered integrations from the store."""
        for slug in list(self._integrations):
            try:
                await self._hydrate_credentials(slug)
            except Exception as e:
                logger.debug(f"Could not hydrate credentials for '{slug}': {e}")

    # -- App lifecycle ---------------------------------------------------------

    def add(
        self,
        slug: str,
        integration_type: str = "api_key",
        tags: list[str] | None = None,
        **integration_kwargs,
    ) -> None:
        """Add an MCP application and register its tools.

        Args:
            slug: Application slug (e.g., "github", "slack").
            integration_type: Auth type ("api_key" or "oauth2").
            tags: Tool tags to register (defaults to ["all"]).
            **integration_kwargs: Extra args for integration (e.g., client_id for OAuth).
        """
        if slug in self._integrations:
            logger.info(f"App '{slug}' already added, skipping")
            return

        # Create integration (no store reference)
        integration = IntegrationFactory.create(slug, integration_type, **integration_kwargs)
        self._integrations[slug] = integration

        # Load and register app
        app_class = app_from_slug(slug)
        app = app_class(name=slug, integration=integration)
        self.registry.register_app(app, tags=tags or ["all"])

        # Persist to manifest
        self._save_manifest_entry(slug, integration_type, tags, integration_kwargs)
        logger.info(f"Added app '{slug}' with {integration_type} auth")

    async def add_from_url(
        self,
        url: str,
        name: str | None = None,
        headers: dict[str, str] | None = None,
        tags: list[str] | None = None,
        use_ngrok: bool = False,
    ) -> None:
        """Add an MCP application from a remote URL.

        Connects to the remote MCP server, discovers its tools, and registers
        them as proxy tools that forward calls to the remote server.

        Flow for OAuth apps:
        1. If stored integration (client_info) exists -> reuse it
        2. If connecting with it fails -> delete stored integration, create fresh
        3. If no stored integration -> create new one
        4. If stored connection (tokens) exists -> reuse it (handled by mcp_app.connect)

        Args:
            url: MCP server URL (e.g., "mcp.notion.so", "https://mcp.example.com/sse").
            name: Override app name (default: derived from URL domain).
            headers: HTTP headers for authentication (e.g., {"Authorization": "Bearer xxx"}).
            tags: Tool tags to filter (not used for remote tools currently).
            use_ngrok: If True, use ngrok for OAuth callbacks (for remote machines).
        """
        from universal_mcp.applications.mcp_app import MCPApplication, _derive_app_name, normalize_mcp_url

        normalized_url = normalize_mcp_url(url)
        app_name = name or _derive_app_name(normalized_url)
        logger.debug(f"add_from_url: url={url!r} normalized={normalized_url!r} app_name={app_name!r} use_ngrok={use_ngrok}")

        if app_name in self.registry._apps:
            logger.info(f"App '{app_name}' already added, skipping")
            return

        # Discover OAuth metadata (shared across attempts)
        auth_metadata, prm, www_auth_scope = None, None, None
        integration = None

        if not headers:
            logger.debug("No headers provided, attempting OAuth discovery...")
            try:
                from universal_mcp.integrations.oauth_helpers import discover_oauth_metadata

                auth_metadata, prm, www_auth_scope = await discover_oauth_metadata(normalized_url)
                logger.debug(
                    f"OAuth discovery result: auth_metadata={'found' if auth_metadata else 'None'}, "
                    f"prm={'found' if prm else 'None'}, www_auth_scope={www_auth_scope!r}"
                )
            except Exception as e:
                logger.warning(f"OAuth discovery failed for {normalized_url}: {e}", exc_info=True)
        else:
            logger.debug(f"Headers provided ({list(headers.keys())}), skipping OAuth discovery")

        if auth_metadata:
            logger.info(f"OAuth authentication detected for {normalized_url}, creating integration...")
            integration = await self._create_oauth_integration(
                normalized_url, auth_metadata, prm, www_auth_scope, use_ngrok
            )
            logger.debug(
                f"OAuth integration created: name={integration.name}, "
                f"server_url={integration._server_url}, "
                f"redirect_uri={integration._registered_redirect_uri}, "
                f"has_ngrok={integration._ngrok_tunnel is not None}"
            )
        else:
            logger.debug("No OAuth metadata found, proceeding without integration")

        # Try to connect. If it fails with an auth-related error (401) and we
        # have an OAuth integration, delete stale client_info and retry with
        # a fresh registration. Transport errors (404/Session terminated) are
        # NOT retried here — those are handled by mcp_app.connect()'s own
        # SSE fallback logic.
        logger.debug(f"Creating MCPApplication: name={app_name}, url={normalized_url}, has_integration={integration is not None}")
        mcp_app = MCPApplication(app_name, normalized_url, headers=headers, integration=integration)
        try:
            logger.debug("Attempting mcp_app.connect()...")
            await mcp_app.connect()
            logger.info(f"Successfully connected to {normalized_url}")
        except Exception as first_error:
            logger.warning(f"mcp_app.connect() failed: {type(first_error).__name__}: {first_error}", exc_info=True)
            if not integration or not auth_metadata:
                raise  # Not an OAuth app, nothing to retry

            # Only retry with fresh client registration on auth-related errors.
            # Check for HTTP 401 (httpx.HTTPStatusError) which indicates stale
            # or invalid client credentials.
            is_auth_error = False
            try:
                import httpx

                if isinstance(first_error, httpx.HTTPStatusError) and first_error.response.status_code == 401:
                    is_auth_error = True
            except ImportError:
                pass

            if not is_auth_error:
                logger.debug(f"Error is not auth-related ({type(first_error).__name__}), not retrying with fresh registration")
                raise

            # Delete stale integration and retry with fresh registration
            logger.warning("Auth error (401) detected, deleting stale client_info and re-registering...")
            from universal_mcp.integrations.oauth_helpers import StoreTokenStorage

            token_storage = StoreTokenStorage(self.store, normalized_url)
            await token_storage.delete_client_info()

            integration = await self._create_oauth_integration(
                normalized_url, auth_metadata, prm, www_auth_scope, use_ngrok, force_new=True
            )
            logger.debug(f"Re-created OAuth integration: redirect_uri={integration._registered_redirect_uri}")
            mcp_app = MCPApplication(app_name, normalized_url, headers=headers, integration=integration)
            logger.debug("Retrying mcp_app.connect() with fresh integration...")
            await mcp_app.connect()
            logger.info(f"Successfully connected on retry to {normalized_url}")

        # After successful connect, persist any new OAuth credentials to the store
        if integration:
            logger.debug("Persisting OAuth credentials to store...")
            await self._persist_oauth_credentials(integration)

        proxy_tools = mcp_app.get_proxy_tools()
        self.registry.register_remote_app(mcp_app, proxy_tools)

        # Track for lifecycle management
        self._mcp_apps[app_name] = mcp_app
        if integration:
            self._integrations[app_name] = integration

        # Persist to manifest
        self._save_manifest_entry(
            app_name,
            integration_type="oauth2" if integration else "none",
            tags=tags,
            integration_kwargs=None,
            source_type="mcp_url",
            source_path=normalized_url,
            headers=headers,
        )
        logger.info(f"Added remote MCP app '{app_name}' from {normalized_url} with {len(proxy_tools)} tools")

    async def _create_oauth_integration(
        self,
        server_url: str,
        auth_metadata,
        prm,
        www_auth_scope,
        use_ngrok: bool = False,
        force_new: bool = False,
    ):
        """Create an OAuth integration, reusing stored client_info when available.

        The SDK loads client_info from the store, passes it to from_server_url,
        and persists any newly registered client_info back.

        Args:
            server_url: Normalized MCP server URL.
            auth_metadata: Discovered OAuth metadata.
            prm: Protected resource metadata.
            www_auth_scope: WWW-Authenticate scope.
            use_ngrok: Use ngrok for OAuth callbacks.
            force_new: If True, skip stored client_info and register fresh.
        """
        from universal_mcp.integrations.integration import OAuthIntegration
        from universal_mcp.integrations.oauth_helpers import StoreTokenStorage

        logger.debug(f"_create_oauth_integration: server_url={server_url}, use_ngrok={use_ngrok}, force_new={force_new}")
        token_storage = StoreTokenStorage(self.store, server_url)

        # Load or clear client_info
        client_info = None
        if force_new:
            logger.debug("force_new=True, deleting stored client_info")
            await token_storage.delete_client_info()
        elif use_ngrok:
            # ngrok URLs are ephemeral — each session gets a new public URL.
            # Stored client_info has the old ngrok URL as its registered redirect_uri,
            # so the OAuth server would redirect to the dead URL. Always re-register.
            logger.debug("use_ngrok=True, deleting stored client_info (ngrok URLs are ephemeral)")
            await token_storage.delete_client_info()
        else:
            client_info = await token_storage.get_client_info()
            if client_info:
                logger.info(f"Reusing existing OAuth client registration for {server_url} (client_id={client_info.client_id})")
                logger.debug(f"Stored client_info redirect_uris: {client_info.redirect_uris}")
            else:
                logger.debug("No stored client_info found, will register new client")

        logger.debug(f"Calling OAuthIntegration.from_server_url(client_info={'existing' if client_info else 'None'}, use_ngrok={use_ngrok})")
        integration, new_client_info = await OAuthIntegration.from_server_url(
            server_url,
            client_info=client_info,
            _pre_discovered=(auth_metadata, prm, www_auth_scope),
            use_ngrok=use_ngrok,
        )
        logger.debug(f"from_server_url returned: integration.name={integration.name}, new_client_info={'yes' if new_client_info else 'no'}")

        # Persist newly registered client_info
        if new_client_info:
            logger.debug(f"Saving new client_info: client_id={new_client_info.client_id}, redirect_uris={new_client_info.redirect_uris}")
            await token_storage.set_client_info(new_client_info)

        # Load existing tokens into the integration's connection
        existing_tokens = await token_storage.get_tokens()
        if existing_tokens and existing_tokens.access_token:
            logger.debug(f"Pre-loading existing tokens: access_token={existing_tokens.access_token[:8]}..., has_refresh={existing_tokens.refresh_token is not None}")
            creds: dict[str, Any] = {"access_token": existing_tokens.access_token}
            if existing_tokens.refresh_token:
                creds["refresh_token"] = existing_tokens.refresh_token
            if existing_tokens.token_type:
                creds["token_type"] = existing_tokens.token_type
            try:
                await integration.set_credentials(creds)
                logger.debug("Existing tokens pre-loaded into integration")
            except Exception as e:
                logger.warning(f"Could not pre-load tokens for {server_url}: {e}", exc_info=True)
        else:
            logger.debug("No existing tokens found in store")

        return integration

    async def _persist_oauth_credentials(self, integration) -> None:
        """Persist OAuth credentials from an integration's connection to the store.

        Args:
            integration: OAuthIntegration with in-memory credentials.
        """
        if not getattr(integration, "_server_url", None):
            logger.debug("_persist_oauth_credentials: no _server_url, skipping")
            return

        try:
            creds = await integration.get_credentials()
        except Exception:
            logger.debug("_persist_oauth_credentials: no in-memory credentials to persist")
            return  # No credentials to persist

        access_token = creds.get("access_token")
        if not access_token:
            logger.debug("_persist_oauth_credentials: no access_token in credentials, skipping")
            return

        from mcp.shared.auth import OAuthToken

        from universal_mcp.integrations.oauth_helpers import StoreTokenStorage

        token_storage = StoreTokenStorage(self.store, integration._server_url)
        oauth_token = OAuthToken(
            access_token=access_token,
            token_type=creds.get("token_type", "bearer"),
            refresh_token=creds.get("refresh_token"),
            scope=creds.get("scope"),
        )
        await token_storage.set_tokens(oauth_token)
        logger.debug(f"Persisted OAuth tokens for {integration._server_url} (access_token={access_token[:8]}...)")

    async def remove(self, slug: str) -> bool:
        """Remove an application and its tools.

        Args:
            slug: Application slug.

        Returns:
            True if removed, False if not found.
        """
        is_integration = slug in self._integrations
        is_mcp_app = slug in self._mcp_apps

        if not is_integration and not is_mcp_app:
            return False

        self.registry.remove_app(slug)
        if is_integration:
            del self._integrations[slug]
        if is_mcp_app:
            await self._mcp_apps[slug].disconnect()
            del self._mcp_apps[slug]
        self._remove_manifest_entry(slug)
        logger.info(f"Removed app '{slug}'")
        return True

    def list_apps(self) -> list[str]:
        """List all registered application slugs."""
        return self.registry.list_apps()

    # -- Authorization ---------------------------------------------------------

    async def authorize(
        self,
        slug: str,
        api_key: str | None = None,
        credentials: dict[str, Any] | None = None,
    ) -> str:
        """Authorize an application with credentials.

        Sets credentials in-memory on the integration AND persists to the store.

        Args:
            slug: Application slug.
            api_key: API key (for api_key integrations).
            credentials: Full credentials dict (for OAuth or custom auth).

        Returns:
            Confirmation message or authorization instructions.
        """
        integration = self._integrations.get(slug)
        if not integration:
            raise KeyError(f"App '{slug}' not found. Call add('{slug}') first.")

        if api_key:
            creds = {"api_key": api_key}
            await integration.set_credentials(creds)
            # Persist to store
            conn = integration.get_default_connection()
            await self.store.put(conn.store_key, creds)
            return f"Authorized '{slug}' with API key"
        elif credentials:
            await integration.set_credentials(credentials)
            # Persist to store
            conn = integration.get_default_connection()
            await self.store.put(conn.store_key, credentials)
            return f"Authorized '{slug}' with provided credentials"
        else:
            return integration.authorize()

    async def is_authorized(self, slug: str) -> bool:
        """Check if an app has valid credentials.

        Tries in-memory first, then attempts to hydrate from the store.

        Args:
            slug: Application slug.

        Returns:
            True if credentials are available.
        """
        integration = self._integrations.get(slug)
        if not integration:
            return False

        # Try in-memory first
        try:
            await integration.get_credentials()
            return True
        except Exception:
            pass

        # Try hydrating from store
        try:
            return await self._hydrate_credentials(slug)
        except Exception:
            return False

    # -- Tools -----------------------------------------------------------------

    def list_tools(self, app: str | None = None) -> list[dict[str, Any]]:
        """List available tools, optionally filtered by app.

        Args:
            app: Filter by app slug.

        Returns:
            List of tool info dicts with name, description, parameters.
        """
        tools = self.registry.list_tools(app_name=app) if app else self.registry.list_tools()

        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.parameters,
            }
            for tool in tools
        ]

    def search_tools(self, query: str) -> list[dict[str, Any]]:
        """Search tools by name, description, or tags.

        Args:
            query: Search query string.

        Returns:
            Matching tools as dicts.
        """
        tools = self.registry.search_tools(query)
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.parameters,
            }
            for tool in tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Execute a registered tool.

        Args:
            tool_name: Full tool name (e.g., "github__create_issue").
            arguments: Tool arguments.

        Returns:
            Tool execution result.
        """
        return await self.registry.call_tool(tool_name, arguments or {})

    # -- Server ----------------------------------------------------------------

    def get_server(self, name: str = "Universal MCP", **kwargs) -> FastMCP:
        """Create a FastMCP server with all registered tools.

        Args:
            name: Server name.
            **kwargs: Extra args passed to FastMCP.

        Returns:
            Configured FastMCP server.
        """
        return create_server(name, self.registry, **kwargs)

    async def run(
        self,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
        port: int = 8005,
    ) -> None:
        """Start the MCP server.

        Args:
            transport: Communication protocol.
            port: Port for HTTP transports.
        """
        server = self.get_server(port=port)
        await server.run(transport=transport)  # type: ignore[misc]

    # -- Lifecycle -------------------------------------------------------------

    async def close(self) -> None:
        """Close all connections and clean up resources."""
        for name, mcp_app in list(self._mcp_apps.items()):
            try:
                await mcp_app.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting MCP app '{name}': {e}")
        self._mcp_apps.clear()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False

    # -- Crontabs --------------------------------------------------------------

    @property
    def crontab_registry(self) -> Any:
        """Lazy-loaded CrontabRegistry instance."""
        if self._crontab_registry is None:
            from universal_mcp.crontabs.registry import CrontabRegistry

            self._crontab_registry = CrontabRegistry()
        return self._crontab_registry

    def schedule(
        self,
        name: str,
        schedule: str,
        prompt: str,
        model: str | None = None,
        description: str = "",
        timezone: str = "UTC",
    ) -> dict[str, Any]:
        """Schedule a recurring AI task.

        Args:
            name: Unique job name.
            schedule: Cron expression (e.g., "0 9 * * *" for daily at 9am).
            prompt: The AI prompt to execute on schedule.
            model: Optional model override.
            description: Human-readable description.
            timezone: Timezone for the schedule.

        Returns:
            Job info dict.
        """
        from universal_mcp.crontabs.models import CrontabJob

        registry = self.crontab_registry
        job = CrontabJob(
            name=name,
            schedule=schedule,
            prompt=prompt,
            model=model,
            description=description,
            timezone=timezone,
        )
        registry.add_job(job)
        return job.model_dump()

    def unschedule(self, name: str) -> bool:
        """Remove a scheduled task.

        Args:
            name: Job name to remove.

        Returns:
            True if removed, False if not found.
        """
        registry = self.crontab_registry
        return registry.remove_job(name)

    def list_schedules(self, enabled_only: bool = False) -> list[dict[str, Any]]:
        """List scheduled tasks.

        Args:
            enabled_only: Only return enabled jobs.

        Returns:
            List of job info dicts.
        """
        registry = self.crontab_registry
        jobs = registry.list_jobs(enabled_only=enabled_only)
        return [job.model_dump() for job in jobs]

    # -- Manifest persistence --------------------------------------------------

    def _load_manifest(self) -> None:
        """Load manifest and re-hydrate apps from disk.

        Note: mcp_url entries are skipped during sync loading.
        They require async connection and must be loaded via load_manifest_async().

        Credentials are NOT loaded here (requires async). Call hydrate_all()
        or load_manifest_async() to load credentials from the store.
        """
        if not self._manifest_path.exists():
            return

        try:
            data = json.loads(self._manifest_path.read_text())
            for slug, info in data.get("apps", {}).items():
                try:
                    source_type = info.get("source_type", "package")

                    # Skip mcp_url entries - they need async loading
                    if source_type == "mcp_url":
                        continue

                    integration_type = info.get("integration_type", "api_key")
                    tags = info.get("tags")
                    kwargs = info.get("integration_kwargs", {})

                    integration = IntegrationFactory.create(slug, integration_type, **kwargs)
                    self._integrations[slug] = integration

                    app_class = app_from_slug(slug)
                    app = app_class(name=slug, integration=integration)
                    self.registry.register_app(app, tags=tags or ["all"])
                except Exception as e:
                    logger.warning(f"Failed to load app '{slug}' from manifest: {e}")
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")

    async def load_manifest_async(self) -> None:
        """Load mcp_url entries from the manifest and hydrate all credentials.

        This should be called after __init__ to fully hydrate credentials
        from the store for all integrations.
        """
        # Hydrate credentials for all integrations loaded during __init__
        await self.hydrate_all()

        if not self._manifest_path.exists():
            return

        try:
            data = json.loads(self._manifest_path.read_text())
            for slug, info in data.get("apps", {}).items():
                source_type = info.get("source_type", "package")
                if source_type != "mcp_url":
                    continue
                if slug in self._mcp_apps:
                    continue

                try:
                    source_path = info.get("source_path", "")
                    headers = info.get("headers")
                    await self.add_from_url(
                        url=source_path,
                        name=slug,
                        headers=headers,
                        tags=info.get("tags"),
                    )
                except Exception as e:
                    logger.warning(f"Failed to load MCP URL app '{slug}' from manifest: {e}")
        except Exception as e:
            logger.warning(f"Failed to load manifest for async apps: {e}")

    def _save_manifest_entry(
        self,
        slug: str,
        integration_type: str,
        tags: list[str] | None,
        integration_kwargs: dict | None = None,
        source_type: str = "package",
        source_path: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Add an entry to the manifest."""
        data = self._read_manifest()
        entry: dict[str, Any] = {
            "integration_type": integration_type,
            "tags": tags,
            "source_type": source_type,
        }
        if integration_kwargs:
            entry["integration_kwargs"] = integration_kwargs
        if source_path:
            entry["source_path"] = source_path
        if headers:
            entry["headers"] = headers
        data.setdefault("apps", {})[slug] = entry
        self._write_manifest(data)

    def _remove_manifest_entry(self, slug: str) -> None:
        """Remove an entry from the manifest."""
        data = self._read_manifest()
        data.get("apps", {}).pop(slug, None)
        self._write_manifest(data)

    def _read_manifest(self) -> dict:
        """Read the manifest file."""
        if self._manifest_path.exists():
            return json.loads(self._manifest_path.read_text())
        return {"apps": {}}

    def _write_manifest(self, data: dict) -> None:
        """Write the manifest file."""
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(json.dumps(data, indent=2))

    def __repr__(self) -> str:
        return f"UniversalMCP(apps={self.list_apps()}, tools={len(self.registry)})"
