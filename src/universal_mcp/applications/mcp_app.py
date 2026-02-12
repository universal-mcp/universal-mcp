"""MCP URL Application - connect to remote MCP servers and proxy their tools."""

from typing import Any
from urllib.parse import urlparse

from fastmcp import Client
from fastmcp.tools.tool import Tool, ToolResult
from loguru import logger
from mcp.types import TextContent

from universal_mcp.applications.application import BaseApplication
from universal_mcp.types import TOOL_NAME_SEPARATOR


def normalize_mcp_url(url: str) -> str:
    """Normalize an MCP server URL.

    - Prepends https:// if no scheme is present
    - Strips trailing slashes (unless the path is just '/')

    Args:
        url: Raw URL string (e.g., "mcp.notion.so", "https://mcp.example.com/sse")

    Returns:
        Normalized URL string.
    """
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"

    return url.rstrip("/")


def _derive_app_name(url: str) -> str:
    """Derive an app name from a URL's domain.

    Examples:
        "https://mcp.notion.so/v1" -> "notion"
        "https://api.github.com/mcp" -> "github"
        "https://example.com" -> "example"
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    parts = hostname.split(".")
    # Filter out common prefixes/suffixes
    skip = {"www", "api", "mcp", "com", "org", "net", "io", "so", "co", "dev", "app"}
    candidates = [p for p in parts if p and p not in skip]
    if candidates:
        return candidates[0]
    # Fallback: use first non-empty part, or "remote"
    return next((p for p in parts if p), "remote")


class ProxyTool(Tool):
    """A tool that proxies calls to a remote MCP server.

    Subclasses FastMCP's Tool directly, overriding run() to forward
    the raw arguments dict to a proxy callable instead of validating
    against a Python function signature.
    """

    fn: Any  # The async proxy callable

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        """Execute the tool by forwarding arguments to the proxy function."""
        result = await self.fn(arguments)
        if isinstance(result, ToolResult):
            return result
        # Wrap string/other results in a ToolResult
        return ToolResult(content=[TextContent(type="text", text=str(result))])


class MCPApplication(BaseApplication):
    """Application that connects to a remote MCP server and exposes its tools.

    Uses FastMCP's Client to discover and proxy tools from a remote server.
    Tools are exposed as ProxyTool instances that forward calls to the remote.
    """

    def __init__(
        self,
        name: str,
        url: str,
        headers: dict[str, str] | None = None,
        integration: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)
        self.url = normalize_mcp_url(url)
        self.headers = headers or {}
        self.integration = integration
        self._client: Client | None = None
        self._remote_tools: list = []
        self._proxy_tools: list[ProxyTool] = []

    async def connect(self) -> None:
        """Connect to the remote MCP server and discover tools."""
        auth = None

        if self.integration:
            # Try to get existing tokens from OAuth integration
            from universal_mcp.exceptions import NotAuthorizedError
            from universal_mcp.integrations.oauth_helpers import OAuthCallbackError

            try:
                credentials = await self.integration.get_credentials()
                access_token = credentials.get("access_token")
                if access_token:
                    auth = access_token
            except (NotAuthorizedError, KeyError, Exception):
                # No existing tokens - run OAuth flow
                try:
                    auth = await self.integration.run_oauth_flow()
                except (ValueError, OAuthCallbackError, OSError) as e:
                    logger.warning(f"OAuth flow failed for {self.url}: {e}")
        elif self.headers:
            # If we have an Authorization header with Bearer token, pass as auth string
            auth_header = self.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                auth = auth_header.split("Bearer ", 1)[1]

        self._client = Client(self.url, auth=auth)
        await self._client.__aenter__()

        try:
            # Discover remote tools
            self._remote_tools = await self._client.list_tools()
            self._proxy_tools = self._build_proxy_tools()
        except Exception:
            await self._client.__aexit__(None, None, None)
            self._client = None
            raise

        logger.info(
            f"Connected to MCP server at {self.url}, "
            f"discovered {len(self._remote_tools)} tools"
        )

    def _build_proxy_tools(self) -> list[ProxyTool]:
        """Build ProxyTool instances from discovered remote tools."""
        proxy_tools = []
        for remote_tool in self._remote_tools:
            tool_name = remote_tool.name
            client = self._client

            async def _proxy_call(
                arguments: dict[str, Any],
                _name: str = tool_name,
                _client: Client = client,  # type: ignore[assignment]
            ) -> str:
                result = await _client.call_tool(_name, arguments)
                # Extract text from content blocks
                texts = []
                for block in result.content:
                    if hasattr(block, "text"):
                        texts.append(block.text)
                    else:
                        texts.append(str(block))
                return "\n".join(texts) if texts else ""

            full_name = f"{self.name}{TOOL_NAME_SEPARATOR}{tool_name}"
            proxy_tool = ProxyTool(
                fn=_proxy_call,
                name=full_name,
                description=remote_tool.description or "",
                parameters=remote_tool.inputSchema,
                tags={self.name},
            )
            proxy_tools.append(proxy_tool)

        return proxy_tools

    def get_proxy_tools(self) -> list[ProxyTool]:
        """Return the list of ProxyTool instances for registration."""
        return self._proxy_tools

    def list_tools(self) -> list:
        """Return proxy tools (available after connect())."""
        return self._proxy_tools

    async def disconnect(self) -> None:
        """Disconnect from the remote MCP server."""
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error disconnecting from {self.url}: {e}")
            finally:
                self._client = None
                self._remote_tools = []
                self._proxy_tools = []
