import os
import webbrowser
from contextlib import AsyncExitStack
from typing import Any, Literal

from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.auth import OAuthClientProvider
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import Server
from mcp.shared.auth import OAuthClientMetadata
from mcp.types import (
    CallToolResult as MCPCallToolResult,
)
from mcp.types import (
    Tool as MCPTool,
)
from openai.types.chat import ChatCompletionToolParam

from universal_mcp.client.oauth import CallbackServer
from universal_mcp.client.token_store import TokenStore
from universal_mcp.config import ClientTransportConfig
from universal_mcp.stores.store import KeyringStore
from universal_mcp.tools.adapters import transform_mcp_tool_to_openai_tool


class MCPClient:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: ClientTransportConfig) -> None:
        self.name: str = name
        self.config: ClientTransportConfig = config
        self.session: ClientSession | None = None
        self.server_url: str = config.url

        # Set up callback server
        self.callback_server = CallbackServer(port=3000)
        self.callback_server.start()

        # Create OAuth authentication handler using the new interface
        if self.server_url and not self.config.headers:
            self.store = KeyringStore(self.name)
            self.auth = OAuthClientProvider(
                server_url="/".join(self.server_url.split("/")[:-1]),
                client_metadata=OAuthClientMetadata.model_validate(self.client_metadata_dict),
                storage=TokenStore(self.store),
                redirect_handler=self._default_redirect_handler,
                callback_handler=self._callback_handler,
            )
        else:
            self.auth = None

    async def _callback_handler(self) -> tuple[str, str | None]:
        """Wait for OAuth callback and return auth code and state."""
        print("⏳ Waiting for authorization callback...")
        try:
            auth_code = self.callback_server.wait_for_callback(timeout=300)
            return auth_code, self.callback_server.get_state()
        finally:
            self.callback_server.stop()

    @property
    def client_metadata_dict(self) -> dict[str, Any]:
        return {
            "client_name": "Simple Auth Client",
            "redirect_uris": ["http://localhost:3000/callback"],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
        }

    async def _default_redirect_handler(self, authorization_url: str) -> None:
        """Default redirect handler that opens the URL in a browser."""
        print(f"Opening browser for authorization: {authorization_url}")
        webbrowser.open(authorization_url)

    async def initialize(self, exit_stack: AsyncExitStack):
        """Initialize the server connection."""
        transport = self.config.transport
        try:
            if transport == "stdio":
                command = self.config["command"]
                if command is None:
                    raise ValueError("The command must be a valid string and cannot be None.")

                server_params = StdioServerParameters(
                    command=command,
                    args=self.config["args"],
                    env={**os.environ, **self.config["env"]} if self.config.get("env") else None,
                )
                stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
                session = await exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.session = session
            elif transport == "streamable_http":
                url = self.config.get("url")
                headers = self.config.get("headers", {})
                if not url:
                    raise ValueError("'url' must be provided for streamable_http transport.")
                streamable_http_transport = await exit_stack.enter_async_context(
                    streamablehttp_client(url=url, headers=headers, auth=self.auth)
                )
                read, write, _ = streamable_http_transport
                session = await exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.session = session
            elif transport == "sse":
                url = self.config.url
                headers = self.config.headers
                if not url:
                    raise ValueError("'url' must be provided for sse transport.")
                sse_transport = await exit_stack.enter_async_context(
                    sse_client(url=url, headers=headers, auth=self.auth)
                )
                read, write = sse_transport
                session = await exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.session = session
            else:
                raise ValueError(f"Unknown transport: {transport}")
        except Exception as e:
            logger.error(f"Error initializing server {self.name}: {e}")
            raise

    async def list_tools(self) -> list[MCPTool]:
        """List available tools from the server."""
        if self.session:
            tools = await self.session.list_tools()
            return list(tools.tools)
        return []

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPCallToolResult:
        """Call a tool on the server."""
        if self.session:
            return await self.session.call_tool(tool_name, arguments)
        return MCPCallToolResult(
            content=[],
            isError=True,
        )


class MultiClientServer(Server):
    """
    Manages multiple MCP servers and maintains a mapping from tool name to the server that provides it.
    """

    def __init__(self, clients: dict[str, ClientTransportConfig]):
        self.clients: list[MCPClient] = [MCPClient(name, config) for name, config in clients.items()]
        self.tool_to_client: dict[str, MCPClient] = {}
        self._mcp_tools: list[MCPTool] = []
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def __aenter__(self):
        """Initialize the server connection."""
        for client in self.clients:
            await client.initialize(self._exit_stack)
        await self._populate_tool_mapping()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the server connection."""
        self.clients.clear()
        self.tool_to_client.clear()
        self._mcp_tools.clear()
        await self._exit_stack.aclose()

    async def _populate_tool_mapping(self):
        """Populate the mapping from tool name to server."""
        self.tool_to_client.clear()
        self._mcp_tools.clear()
        for client in self.clients:
            try:
                tools = await client.list_tools()
                for tool in tools:
                    self._mcp_tools.append(tool)
                    tool_name = tool.name
                    logger.info(f"Found tool: {tool_name} from client: {client.name}")
                    if tool_name:
                        self.tool_to_client[tool_name] = client
            except Exception as e:
                logger.warning(f"Failed to list tools for client {client.name}: {e}")

    async def list_tools(self, format: Literal["mcp", "openai"] = "mcp") -> list[MCPTool | ChatCompletionToolParam]:
        """List available tools from all servers."""
        if format == "mcp":
            return self._mcp_tools
        elif format == "openai":
            return [transform_mcp_tool_to_openai_tool(tool) for tool in self._mcp_tools]
        else:
            raise ValueError(f"Invalid format: {format}")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPCallToolResult:
        """Call a tool on the server."""
        client = self.tool_to_client[tool_name]
        return await client.call_tool(tool_name, arguments)
