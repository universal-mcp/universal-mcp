import os
from contextlib import AsyncExitStack
from typing import Any, Literal, Self

from fastmcp import Client as FastMCPClient
from fastmcp.client.transports import SSETransport, StdioTransport, StreamableHttpTransport
from loguru import logger
from mcp.types import (
    CallToolResult as MCPCallToolResult,
)
from mcp.types import (
    Tool as MCPTool,
)
from openai.types.chat import ChatCompletionToolParam

from universal_mcp.config import ClientConfig, ClientTransportConfig
from universal_mcp.tools.adapters import transform_mcp_tool_to_openai_tool


class ClientTransport:
    """
    Client for connecting to and interacting with a single MCP server.

    Manages the lifecycle of a connection to an MCP server using fastmcp.Client.
    Supports stdio, sse, and streamable_http transports. Authentication is handled
    via headers (e.g., {"Authorization": "Bearer <token>"}).
    """

    def __init__(self, name: str, config: ClientTransportConfig) -> None:
        self.name: str = name
        self.config: ClientTransportConfig = config
        self._client: FastMCPClient | None = None

    async def initialize(self, exit_stack: AsyncExitStack) -> None:
        """
        Establishes and initializes the connection to the MCP server.

        Raises:
            ValueError: If the transport type is unknown or if required
                        configuration for a transport is missing.
        """
        transport = self.config.transport
        try:
            if transport == "stdio":
                command = self.config.command
                if not command:
                    raise ValueError("The command must be a valid string and cannot be None.")

                stdio_transport = StdioTransport(
                    command=command,
                    args=self.config.args,
                    env={**os.environ, **self.config.env} if self.config.env else None,
                )
                self._client = FastMCPClient(transport=stdio_transport)
            elif transport == "streamable_http":
                url = self.config.url
                headers = self.config.headers
                if not url:
                    raise ValueError("'url' must be provided for streamable_http transport.")
                http_transport = StreamableHttpTransport(url=url, headers=headers or None)
                self._client = FastMCPClient(transport=http_transport)
            elif transport == "sse":
                url = self.config.url
                headers = self.config.headers
                if not url:
                    raise ValueError("'url' must be provided for sse transport.")
                sse_transport = SSETransport(url=url, headers=headers or None)
                self._client = FastMCPClient(transport=sse_transport)
            else:
                raise ValueError(f"Unknown transport: {transport}")

            await exit_stack.enter_async_context(self._client)
        except Exception as e:
            logger.error(f"Error initializing server {self.name}: {e}")
            raise

    async def list_tools(self) -> list[MCPTool]:
        """Lists all tools available on the connected MCP server."""
        if self._client:
            try:
                tools = await self._client.list_tools()
                return list(tools)
            except Exception as e:
                logger.warning(f"Failed to list tools for client {self.name}: {e}")
        return []

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPCallToolResult:
        """Calls a specified tool on the connected MCP server with given arguments."""
        if self._client:
            try:
                result = await self._client.call_tool(tool_name, arguments, raise_on_error=False)
                return result
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
        mcp_config = ClientConfig(mcpServers={client.name: client.config for client in self.clients})
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
