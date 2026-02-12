"""Server module - creates FastMCP servers backed by a LocalRegistry.

Uses FastMCP's native tool management. LocalRegistry is the catalog of
available apps/tools; FastMCP handles the MCP protocol.
"""

from typing import Any

from fastmcp import FastMCP
from loguru import logger

from universal_mcp.applications.application import BaseApplication
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.config import ServerConfig
from universal_mcp.exceptions import ConfigurationError
from universal_mcp.integrations.integration import ApiKeyIntegration
from universal_mcp.stores import create_store
from universal_mcp.tools.local_registry import LocalRegistry


def create_server(
    name: str,
    registry: LocalRegistry,
    description: str = "",
    **kwargs: Any,
) -> FastMCP:
    """Create a FastMCP server from a LocalRegistry.

    Registers all tools from the registry into FastMCP's native system.
    FastMCP then handles list_tools/call_tool via the MCP protocol.

    Args:
        name: Server name.
        registry: LocalRegistry containing apps and tools.
        description: Server description.
        **kwargs: Extra args passed to FastMCP (e.g. port).

    Returns:
        A configured FastMCP server instance.
    """
    server = FastMCP(name, description, **kwargs)
    _register_tools(server, registry)
    return server


def create_server_from_config(config: ServerConfig) -> tuple[FastMCP, LocalRegistry]:
    """Create a FastMCP server from a ServerConfig.

    Loads apps and store from config, populates a LocalRegistry,
    and creates a FastMCP server with all tools registered.

    Note: mcp_url apps are not loaded here (they require async).
    Use create_server_from_config_async() for full support.

    Args:
        config: Server configuration.

    Returns:
        Tuple of (FastMCP server, LocalRegistry).
    """
    registry = LocalRegistry()
    _load_config_into_registry(config, registry)

    server = FastMCP(config.name, config.description, port=config.port)
    _register_tools(server, registry)

    return server, registry


async def create_server_from_config_async(config: ServerConfig) -> tuple[FastMCP, LocalRegistry]:
    """Create a FastMCP server from a ServerConfig, including mcp_url apps.

    Like create_server_from_config but also connects to remote MCP servers.

    Args:
        config: Server configuration.

    Returns:
        Tuple of (FastMCP server, LocalRegistry).
    """
    registry = LocalRegistry()
    _load_config_into_registry(config, registry)
    await _load_mcp_url_apps(config, registry)

    server = FastMCP(config.name, config.description, port=config.port)
    _register_tools(server, registry)

    return server, registry


def create_server_from_app(
    app: BaseApplication,
    name: str | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> tuple[FastMCP, LocalRegistry]:
    """Create a FastMCP server for a single application.

    Args:
        app: Application instance.
        name: Server name (defaults to app name).
        description: Server description.
        **kwargs: Extra args passed to FastMCP.

    Returns:
        Tuple of (FastMCP server, LocalRegistry).
    """
    registry = LocalRegistry()
    registry.register_app(app, tags=["all"])

    server_name = name or f"{app.name.title()} MCP Server"
    server_desc = description or f"MCP server for {app.name}"

    server = FastMCP(server_name, server_desc, **kwargs)
    _register_tools(server, registry)

    return server, registry


# ── Internal helpers ──────────────────────────────────────────


def _register_tools(server: FastMCP, registry: LocalRegistry) -> None:
    """Register all tools from a LocalRegistry into a FastMCP server."""
    tools = registry.list_tools()
    for tool in tools:
        server.add_tool(tool)
    logger.info(f"Registered {len(tools)} tools with FastMCP server")


def _load_config_into_registry(config: ServerConfig, registry: LocalRegistry) -> None:
    """Load apps and store tools from config into a registry."""
    store = None
    if config.store:
        try:
            store = create_store(
                store_type=config.store.type,
                directory=config.store.path,
                service_name=config.store.name
            )
            # Register store operations as tools (using py-key-value API)
            registry.register_tool(store.put, app_name="store")
            registry.register_tool(store.delete, app_name="store")
            logger.info(f"Store loaded: {config.store.type}")
        except Exception as e:
            logger.error(f"Failed to setup store: {e}", exc_info=True)
            raise ConfigurationError(f"Store setup failed: {str(e)}") from e

    if not config.apps:
        logger.warning("No applications configured")
        return

    for app_config in config.apps:
        # Skip mcp_url apps - they need async loading via _load_mcp_url_apps
        if app_config.source_type == "mcp_url":
            continue

        try:
            integration = None
            if app_config.integration:
                if app_config.integration.type == "api_key":
                    integration = ApiKeyIntegration(
                        app_config.name,
                        store=store,
                        **(app_config.integration.credentials or {}),
                    )
                else:
                    raise ValueError(f"Unsupported integration type: {app_config.integration.type}")

            app_class = app_from_slug(app_config.name)
            app = app_class(name=app_config.name, integration=integration)
            registry.register_app(app, tool_names=app_config.actions)
            logger.info(f"Loaded app: {app_config.name}")
        except Exception as e:
            logger.error(f"Failed to load app {app_config.name}: {e}", exc_info=True)


async def _load_mcp_url_apps(config: ServerConfig, registry: LocalRegistry) -> None:
    """Load mcp_url apps from config into the registry (async)."""
    if not config.apps:
        return

    from universal_mcp.applications.mcp_app import MCPApplication

    for app_config in config.apps:
        if app_config.source_type != "mcp_url":
            continue

        try:
            url = app_config.source_path
            if not url:
                logger.error(f"mcp_url app '{app_config.name}' missing source_path")
                continue

            # Extract headers from integration credentials if available
            headers = None
            if app_config.integration and app_config.integration.credentials:
                headers = app_config.integration.credentials.get("headers")

            mcp_app = MCPApplication(app_config.name, url, headers=headers)
            await mcp_app.connect()

            proxy_tools = mcp_app.get_proxy_tools()
            registry.register_remote_app(mcp_app, proxy_tools)
            logger.info(f"Loaded MCP URL app: {app_config.name} from {url}")
        except Exception as e:
            logger.error(f"Failed to load MCP URL app {app_config.name}: {e}", exc_info=True)
