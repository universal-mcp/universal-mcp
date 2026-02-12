"""Universal MCP SDK - Agent-facing API for finding, installing, authorizing, and using MCP applications."""

import json
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from loguru import logger

from universal_mcp.applications.utils import app_from_slug
from universal_mcp.config import StoreConfig
from universal_mcp.integrations.integration import Integration, IntegrationFactory
from universal_mcp.servers.server import create_server
from universal_mcp.stores import store_from_config
from universal_mcp.tools.local_registry import LocalRegistry

_DEFAULT_MANIFEST_PATH = Path.home() / ".universal-mcp" / "manifest.json"


class UniversalMCP:
    """Agent-facing SDK for finding, installing, authorizing, and using MCP applications.

    Example usage:
        mcp = UniversalMCP()
        mcp.add("github")
        await mcp.authorize("github", api_key="ghp_xxx")
        tools = mcp.list_tools()
        result = await mcp.call_tool("github__create_issue", {"title": "Bug"})
    """

    def __init__(
        self,
        store_type: Literal["disk", "memory", "environment", "keyring"] = "disk",
        store_path: Path | None = None,
        store_name: str = "universal_mcp",
        manifest_path: Path | None = None,
    ) -> None:
        store_config = StoreConfig(type=store_type, name=store_name, path=store_path)
        self.store = store_from_config(store_config)
        self.registry = LocalRegistry()
        self._integrations: dict[str, Integration] = {}
        self._mcp_apps: dict[str, Any] = {}  # MCPApplication instances for lifecycle management
        self._crontab_registry: Any = None  # Lazy-loaded CrontabRegistry
        self._manifest_path = manifest_path or _DEFAULT_MANIFEST_PATH

        # Load existing manifest and re-hydrate apps
        self._load_manifest()

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

        # Create integration
        integration = IntegrationFactory.create(
            slug, integration_type, store=self.store, **integration_kwargs
        )
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
    ) -> None:
        """Add an MCP application from a remote URL.

        Connects to the remote MCP server, discovers its tools, and registers
        them as proxy tools that forward calls to the remote server.

        If no headers are provided, attempts OAuth discovery and dynamic client
        registration for servers that require authentication.

        Args:
            url: MCP server URL (e.g., "mcp.notion.so", "https://mcp.example.com/sse").
            name: Override app name (default: derived from URL domain).
            headers: HTTP headers for authentication (e.g., {"Authorization": "Bearer xxx"}).
            tags: Tool tags to filter (not used for remote tools currently).
        """
        from universal_mcp.applications.mcp_app import MCPApplication, _derive_app_name, normalize_mcp_url

        normalized_url = normalize_mcp_url(url)
        app_name = name or _derive_app_name(normalized_url)

        if app_name in self.registry._apps:
            logger.info(f"App '{app_name}' already added, skipping")
            return

        integration = None
        if not headers:
            # Probe for OAuth authentication
            try:
                from universal_mcp.integrations.integration import OAuthIntegration
                from universal_mcp.integrations.oauth_helpers import discover_oauth_metadata

                auth_metadata, prm, www_auth_scope = await discover_oauth_metadata(normalized_url)
                if auth_metadata:
                    logger.info(f"OAuth authentication detected for {normalized_url}, registering client...")
                    integration = await OAuthIntegration.from_server_url(
                        normalized_url,
                        store=self.store,
                        _pre_discovered=(auth_metadata, prm, www_auth_scope),
                    )
            except Exception as e:
                logger.debug(f"OAuth discovery skipped for {normalized_url}: {e}")

        mcp_app = MCPApplication(app_name, normalized_url, headers=headers, integration=integration)
        await mcp_app.connect()

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
            await integration.set_credentials({"api_key": api_key})
            return f"Authorized '{slug}' with API key"
        elif credentials:
            await integration.set_credentials(credentials)
            return f"Authorized '{slug}' with provided credentials"
        else:
            return integration.authorize()

    async def is_authorized(self, slug: str) -> bool:
        """Check if an app has valid credentials.

        Args:
            slug: Application slug.

        Returns:
            True if credentials are available.
        """
        integration = self._integrations.get(slug)
        if not integration:
            return False
        try:
            await integration.get_credentials()
            return True
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

                    integration = IntegrationFactory.create(
                        slug, integration_type, store=self.store, **kwargs
                    )
                    self._integrations[slug] = integration

                    app_class = app_from_slug(slug)
                    app = app_class(name=slug, integration=integration)
                    self.registry.register_app(app, tags=tags or ["all"])
                except Exception as e:
                    logger.warning(f"Failed to load app '{slug}' from manifest: {e}")
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")

    async def load_manifest_async(self) -> None:
        """Load mcp_url entries from the manifest that require async connection."""
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
