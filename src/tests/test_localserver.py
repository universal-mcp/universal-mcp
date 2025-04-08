import pytest

from universal_mcp.config import AppConfig
from universal_mcp.servers.server import LocalServer


@pytest.mark.asyncio
async def test_local_server():
    apps_list = [AppConfig(name="zenquotes")]
    server = LocalServer(
        name="Test Server",
        description="Test Server",
        apps_list=apps_list,
    )

    # Check server initialized
    assert server is not None
    assert server.name == "Test Server"

    # Check apps loaded from config
    assert len(server.apps_list) > 0

    # Check tools registered
    tools = await server.list_tools()
    assert len(tools) > 0

    # Verify tool properties
    for tool in tools:
        assert tool.name is not None
        assert tool.description is not None
