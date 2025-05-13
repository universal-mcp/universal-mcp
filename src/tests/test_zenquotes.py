import pytest

from universal_mcp.config import AppConfig, ServerConfig
from universal_mcp.servers import LocalServer


@pytest.mark.asyncio
async def test_zenquotes():
    apps_list = [
        AppConfig(
            name="zenquotes",
            integration=None,
        )
    ]

    server_config = ServerConfig(name="Test Server", description="Test Server", apps=apps_list)
    server = LocalServer(server_config)

    # List available tools
    tools = await server.list_tools()
    assert len(tools) > 0
    # Get a random quote
    result = await server.call_tool("zenquotes_get_quote", {})
    assert len(result) > 0
    quote = result[0].text
    assert quote is not None
    assert len(quote) > 0
