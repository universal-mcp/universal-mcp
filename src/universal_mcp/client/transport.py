import os
import webbrowser
from contextlib import AsyncExitStack
from typing import Any, Literal, Self

from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.auth import OAuthClientProvider
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
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
from universal_mcp.config import ClientConfig, ClientTransportConfig
from universal_mcp.stores.store import KeyringStore
from universal_mcp.tools.adapters import transform_mcp_tool_to_openai_tool


class ClientTransport:
    """
    Client for connecting to and interacting with a single MCP server.

    Manages the lifecycle of a connection to an MCP server, handles various
    transport mechanisms (stdio, sse, streamable_http), and facilitates
    authentication, including OAuth 2.0 client flows. Allows listing tools
    available on the server and calling them.
    """

    def __init__(self, name: str, config: ClientTransportConfig) -> None:
        self.name: str = name
        self.config: ClientTransportConfig = config
        self.session: ClientSession | None = None
        self.server_url: str = config.url

        # Create OAuth authentication handler if needed
        if self.server_url and not getattr(self.config, "headers", None):
            # Set up callback server
            self._callback_server = CallbackServer(port=3000)
            self.store: KeyringStore | None = KeyringStore(self.name)
            self.auth: OAuthClientProvider | None = OAuthClientProvider(
                server_url="/".join(self.server_url.split("/")[:-1]),
                client_metadata=OAuthClientMetadata.model_validate(self.client_metadata_dict),
                storage=TokenStore(self.store),
                redirect_handler=self._default_redirect_handler,
                callback_handler=self._callback_handler,
            )
        else:
            self._callback_server = None
            self.store = None
            self.auth = None

    @property
    def callback_server(self) -> CallbackServer:
        if self._callback_server and not self._callback_server.is_running:
            self._callback_server.start()
        return self._callback_server

    async def _callback_handler(self) -> tuple[str, str | None]:
        """Handles the OAuth callback by waiting for and returning auth details."""
        logger.info("⏳ Waiting for authorization callback...")
        try:
            auth_code = self.callback_server.wait_for_callback(timeout=300)
            return auth_code, self.callback_server.get_state()
        finally:
            self.callback_server.stop()

    @property
    def client_metadata_dict(self) -> dict[str, Any]:
        """Provides OAuth 2.0 client metadata for registration or authentication."""
        return {
            "client_name": self.name,
            "redirect_uris": [self.callback_server.redirect_uri],  # type: ignore
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
        }

    async def _default_redirect_handler(self, authorization_url: str) -> None:
        """Default handler for OAuth redirects; opens URL in a web browser."""
        logger.info(f"Opening browser for authorization: {authorization_url}")
        webbrowser.open(authorization_url)

    async def initialize(self, exit_stack: AsyncExitStack) -> None:
        """
        Establishes and initializes the connection to the MCP server.

        Raises:
            ValueError: If the transport type is unknown or if required
                        configuration for a transport is missing.
        """
        transport = getattr(self.config, "transport", None)
        session = None
        try:
            if transport == "stdio":
                command = self.config.get("command")
                if not command:
                    raise ValueError("The command must be a valid string and cannot be None.")

                server_params = StdioServerParameters(
                    command=command,
                    args=self.config.get("args", []),
                    env={**os.environ, **self.config.get("env", {})} if self.config.get("env") else None,
                )
                stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
                session = await exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
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
            elif transport == "sse":
                url = self.config.get("url")
                headers = self.config.get("headers", {})
                if not url:
                    raise ValueError("'url' must be provided for sse transport.")
                sse_transport = await exit_stack.enter_async_context(
                    sse_client(url=url, headers=headers, auth=self.auth)
                )
                read, write = sse_transport
                session = await exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
            else:
                raise ValueError(f"Unknown transport: {transport}")
            self.session = session
        except Exception as e:
            if session:
                await session.aclose()
            logger.error(f"Error initializing server {self.name}: {e}")
            raise

    async def list_tools(self) -> list[MCPTool]:
        """Lists all tools available on the connected MCP server."""
        if self.session:
            try:
                tools = await self.session.list_tools()
                return list(tools.tools)
            except Exception as e:
                logger.warning(f"Failed to list tools for client {self.name}: {e}")
        return []

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPCallToolResult:
        """Calls a specified tool on the connected MCP server with given arguments."""
        if self.session:
            try:
                return await self.session.call_tool(tool_name, arguments)
            except Exception as e:
                logger.error(f"Error calling tool '{tool_name}' on client {self.name}: {e}")
        return MCPCallToolResult(
            content=[],
            isError=True,
        )


class MultiClientTransport:
    """
    Aggregates multiple ClientTransport instances to act as a single MCP Server.

    Provides a unified Server interface for a collection of ClientTransport
    instances, each potentially connected to a different MCP server.
    Maintains a mapping of tool names to the specific ClientTransport that
    provides that tool.
    """

    def __init__(self, clients: dict[str, ClientTransportConfig]):
        self.clients: list[ClientTransport] = [ClientTransport(name, config) for name, config in clients.items()]
        self.tool_to_client: dict[str, ClientTransport] = {}
        self._mcp_tools: list[MCPTool] = []
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    @classmethod
    def from_file(cls, path: str) -> Self:
        mcp_config = ClientConfig.load_json_config(path)
        return cls(mcp_config.mcpServers)

    def save_to_file(self, path: str) -> None:
        mcp_config = ClientConfig(mcpServers={name: config.model_dump() for name, config in self.clients.items()})
        mcp_config.save_json_config(path)

    async def add_client(self, name: str, config: ClientTransportConfig) -> None:
        if name in self.tool_to_client:
            logger.warning(f"Client {name} already exists. Skipping.")
            return
        self.clients.append(ClientTransport(name, config))
        self.tool_to_client[name] = self.clients[-1]
        logger.info(f"Added client: {name}")
        await self._populate_tool_mapping()

    async def remove_client(self, name: str) -> None:
        if name not in self.tool_to_client:
            logger.warning(f"Client {name} not found. Skipping.")
            return
        self.clients.remove(self.tool_to_client[name])
        del self.tool_to_client[name]
        logger.info(f"Removed client: {name}")
        await self._populate_tool_mapping()

    async def __aenter__(self):
        for client in self.clients:
            await client.initialize(self._exit_stack)
        await self._populate_tool_mapping()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.clients.clear()
        self.tool_to_client.clear()
        self._mcp_tools.clear()
        await self._exit_stack.aclose()

    async def _populate_tool_mapping(self):
        self.tool_to_client.clear()
        self._mcp_tools.clear()
        for client in self.clients:
            try:
                tools = await client.list_tools()
                for tool in tools:
                    tool_name = getattr(tool, "name", None)
                    if tool_name:
                        if tool_name not in self.tool_to_client:
                            self._mcp_tools.append(tool)
                            self.tool_to_client[tool_name] = client
                            logger.info(f"Found tool: {tool_name} from client: {client.name}")
                        else:
                            logger.warning(
                                f"Duplicate tool name '{tool_name}' found in client '{client.name}'. Skipping."
                            )
            except Exception as e:
                logger.warning(f"Failed to list tools for client {client.name}: {e}")

    async def list_tools(self, format: Literal["mcp", "openai"] = "mcp") -> list[MCPTool | ChatCompletionToolParam]:
        """
        Lists all unique tools available from all managed clients.

        Args:
            format: The desired format for the returned tools.

        Returns:
            List of tools in the specified format.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        if format == "mcp":
            return self._mcp_tools
        elif format == "openai":
            return [transform_mcp_tool_to_openai_tool(tool) for tool in self._mcp_tools]
        else:
            raise ValueError(f"Invalid format: {format}")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPCallToolResult:
        """
        Calls a tool by routing the request to the appropriate ClientTransport.

        Raises:
            KeyError: If the tool_name is not found.
        """
        client = self.tool_to_client.get(tool_name)
        if not client:
            logger.error(f"Tool '{tool_name}' not found in any client.")
            return MCPCallToolResult(content=[], isError=True)
        return await client.call_tool(tool_name, arguments)
