from universal_mcp.servers import LocalServer
import pytest

@pytest.mark.asyncio
async def test_zenquotes():
    apps_list = [
        {
            "name": "zenquotes",
            "integration": None
        }
    ]
    
    server = LocalServer(name="Test Server", description="Test Server", apps_list=apps_list)
    
    # List available tools
    tools = await server.list_tools()
    assert len(tools) > 0
    # Get a random quote
    result = await server.call_tool("zenquote_get_quote", {})
    assert len(result) > 0
    quote = result[0].text
    assert quote is not None
    assert len(quote) > 0


