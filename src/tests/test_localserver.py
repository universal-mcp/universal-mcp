import pytest

from universal_mcp.config import AppConfig, ServerConfig
from universal_mcp.servers.server import LocalServer


@pytest.mark.asyncio
async def test_local_server():
    apps_list = [AppConfig(name="zenquotes")]
    server_config = ServerConfig(
        name="Test Server",
        description="Test Server",
        apps=apps_list,
    )
    server = LocalServer(server_config)

    # Check server initialized
    assert server is not None
    assert server.name == server_config.name

    # Check tools registered
    tools = await server.list_tools()
    assert len(tools) > 0

    # Verify tool properties
    for tool in tools:
        assert tool.name is not None
        assert tool.description is not None
