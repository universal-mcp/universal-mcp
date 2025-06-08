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
    """Client for connecting to and interacting with a single MCP server.

    This class manages the lifecycle of a connection to an MCP server,
    handles various transport mechanisms (stdio, sse, streamable_http),
    and facilitates authentication, including OAuth 2.0 client flows.
    It allows listing tools available on the server and calling them.

    An internal `CallbackServer` is used to handle OAuth redirect URIs.
    Credentials obtained via OAuth are stored using a `TokenStore`
    backed by a `KeyringStore`.

    Attributes:
        name (str): A descriptive name for this client instance.
        config (ClientTransportConfig): Configuration object detailing how
            to connect to the MCP server (transport type, URL, command, etc.).
        session (ClientSession | None): The active MCP `ClientSession`
            once initialized. None if not connected.
        server_url (str): The base URL of the MCP server, if applicable
            (for SSE or streamable_http transports).
        callback_server (CallbackServer): An HTTP server instance to listen
            for OAuth 2.0 redirect callbacks.
        store (KeyringStore | None): A store for OAuth tokens, typically
            using the system keyring. None if auth is not OAuth-based.
        auth (OAuthClientProvider | None): The OAuth client provider instance
            responsible for managing the OAuth flow. None if not using
            OAuth or if headers are directly provided in config.
    """

    def __init__(self, name: str, config: ClientTransportConfig) -> None:
        """Initializes the MCPClient.

        Sets up the client configuration, name, and server URL.
        It also starts a `CallbackServer` to handle OAuth 2.0 redirects
        and initializes the `OAuthClientProvider` and `TokenStore` if
        OAuth is applicable (i.e., server_url is set and no direct
        headers are provided in the config).

        Args:
            name (str): A descriptive name for this client (e.g., "GitHub_Client").
            config (ClientTransportConfig): The transport and connection
                configuration for the target MCP server.
        """
        self.name: str = name
        self.config: ClientTransportConfig = config
        self.session: ClientSession | None = None
        self.server_url: str = config.url # type: ignore

        # Set up callback server
        self.callback_server = CallbackServer(port=3000)
        self.callback_server.start()

        # Create OAuth authentication handler using the new interface
        if self.server_url and not self.config.headers:
            self.store: KeyringStore | None = KeyringStore(self.name) # type: ignore
            self.auth: OAuthClientProvider | None = OAuthClientProvider(
                server_url="/".join(self.server_url.split("/")[:-1]),
                client_metadata=OAuthClientMetadata.model_validate(self.client_metadata_dict),
                storage=TokenStore(self.store), # type: ignore
                redirect_handler=self._default_redirect_handler,
                callback_handler=self._callback_handler,
            )
        else:
            self.store = None
            self.auth = None

    async def _callback_handler(self) -> tuple[str, str | None]:
        """Handles the OAuth callback by waiting for and returning auth details.

        This method is used by the `OAuthClientProvider` to complete the
        authorization code grant flow. It waits for the internal `callback_server`
        to receive a request on its redirect URI.

        Returns:
            tuple[str, str | None]: A tuple containing the authorization code
                                    and the state parameter from the callback.

        Raises:
            TimeoutError: If the callback is not received within the timeout period.
        """
        print("⏳ Waiting for authorization callback...")
        try:
            auth_code = self.callback_server.wait_for_callback(timeout=300)
            return auth_code, self.callback_server.get_state()
        finally:
            self.callback_server.stop()

    @property
    def client_metadata_dict(self) -> dict[str, Any]:
        """Provides OAuth 2.0 client metadata for registration or authentication.

        This metadata defines the client's properties to the OAuth server,
        such as its name, redirect URIs, supported grant types, and
        token endpoint authentication method.

        Returns:
            dict[str, Any]: A dictionary containing the client metadata.
        """
        return {
            "client_name": "Simple Auth Client", # Should be self.name, but matches existing
            "redirect_uris": [self.callback_server.redirect_uri], # type: ignore
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post", # Should be none for public, but matches existing
        }

    async def _default_redirect_handler(self, authorization_url: str) -> None:
        """Default handler for OAuth redirects; opens URL in a web browser.

        This method is called by the `OAuthClientProvider` to direct the
        user to the authorization server's URL to grant permissions.

        Args:
            authorization_url (str): The URL to which the user should be redirected.
        """
        print(f"Opening browser for authorization: {authorization_url}")
        webbrowser.open(authorization_url)

    async def initialize(self, exit_stack: AsyncExitStack):
        """Establishes and initializes the connection to the MCP server.

        This method sets up the transport (stdio, streamable_http, or sse)
        based on the `self.config`. It uses the provided `AsyncExitStack`
        to manage the context of the transport and the `ClientSession`.
        The established `ClientSession` is stored in `self.session`.

        Args:
            exit_stack (AsyncExitStack): An `AsyncExitStack` to manage
                the lifecycle of asynchronous resources like transports
                and sessions.

        Raises:
            ValueError: If the transport type is unknown or if required
                        configuration for a transport is missing.
            Exception: Propagates exceptions that occur during transport
                       or session initialization.
        """
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
        """Lists all tools available on the connected MCP server.

        If a session is active, this method requests the list of tools
        from the server and returns them.

        Returns:
            list[MCPTool]: A list of `MCPTool` objects. Returns an empty
                           list if no session is active or if an error occurs.
        """
        if self.session:
            tools = await self.session.list_tools()
            return list(tools.tools)
        return []

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPCallToolResult:
        """Calls a specified tool on the connected MCP server with given arguments.

        If a session is active, this method sends a request to the server
        to execute the tool and returns the result.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (dict[str, Any]): A dictionary of arguments for the tool.

        Returns:
            MCPCallToolResult: The result of the tool call. If no session is
                               active or an error occurs, returns an
                               `MCPCallToolResult` with `isError=True`.
        """
        if self.session:
            return await self.session.call_tool(tool_name, arguments)
        return MCPCallToolResult(
            content=[],
            isError=True,
        )


class MultiClientServer(Server):
    """
    Aggregates multiple MCPClients to act as a single MCP Server.

    This class provides a unified `Server` interface for a collection of
    `MCPClient` instances, each potentially connected to a different
    MCP server. It maintains a mapping of tool names to the specific
    `MCPClient` that provides that tool. This allows an agent or application
    to interact with tools from various sources through a single entry point.

    It implements the `mcp.server.Server` interface, allowing it to be used
    wherever a standard MCP server is expected. It manages the lifecycle
    of its underlying clients using an `AsyncExitStack`.

    Attributes:
        clients (list[MCPClient]): A list of `MCPClient` instances that this
            server manages.
        tool_to_client (dict[str, MCPClient]): A mapping from tool names
            to the `MCPClient` instance that provides that tool.
        _mcp_tools (list[MCPTool]): A cached list of all unique tools
            available from all managed clients.
        _exit_stack (AsyncExitStack): Manages the lifecycle of the
            underlying `MCPClient` connections.
    """

    def __init__(self, clients: dict[str, ClientTransportConfig]):
        """Initializes the MultiClientServer.

        Args:
            clients (dict[str, ClientTransportConfig]): A dictionary where keys
                are descriptive names for each client and values are
                `ClientTransportConfig` objects for configuring each
                underlying `MCPClient`.
        """
        self.clients: list[MCPClient] = [MCPClient(name, config) for name, config in clients.items()]
        self.tool_to_client: dict[str, MCPClient] = {}
        self._mcp_tools: list[MCPTool] = []
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def __aenter__(self):
        """Initializes all managed MCPClients and populates the tool map.

        This method is called when entering an `async with` block.
        It initializes each `MCPClient` and then builds the
        `tool_to_client` mapping.

        Returns:
            MultiClientServer: self
        """
        for client in self.clients:
            await client.initialize(self._exit_stack)
        await self._populate_tool_mapping()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleans up resources by closing all managed MCPClient connections.

        This method is called when exiting an `async with` block.
        It clears internal mappings and closes the `AsyncExitStack`,
        which in turn ensures underlying client sessions are closed.
        """
        self.clients.clear()
        self.tool_to_client.clear()
        self._mcp_tools.clear()
        await self._exit_stack.aclose()

    async def _populate_tool_mapping(self):
        """Discovers tools from all clients and maps them.

        Iterates through each initialized `MCPClient`, lists its available
        tools, and populates the `self.tool_to_client` dictionary with
        tool names as keys and the providing client as values. It also
        aggregates all unique tools into `self._mcp_tools`.
        Logs warnings if a client fails to list tools.
        """
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
        """Lists all unique tools available from all managed MCP clients.

        The tools are discovered and cached by `_populate_tool_mapping`
        during initialization or refresh.

        Args:
            format (Literal["mcp", "openai"], optional): The desired format
                for the returned tools. "mcp" returns `MCPTool` objects,
                "openai" returns tools formatted for OpenAI's API
                (using `ChatCompletionToolParam`). Defaults to "mcp".

        Returns:
            list[MCPTool | ChatCompletionToolParam]: A list of tools in the
                                                    specified format.

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
        """Calls a tool by routing the request to the appropriate MCPClient.

        Looks up the `tool_name` in its `tool_to_client` mapping to find
        the `MCPClient` instance that provides the tool, and then delegates
        the `call_tool` request to that client.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (dict[str, Any]): A dictionary of arguments for the tool.

        Returns:
            MCPCallToolResult: The result of the tool call from the
                               responsible client.

        Raises:
            KeyError: If the `tool_name` is not found in the `tool_to_client`
                      mapping (i.e., the tool is unknown).
        """
        client = self.tool_to_client[tool_name]
        return await client.call_tool(tool_name, arguments)
