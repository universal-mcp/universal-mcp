import pytest

from universal_mcp.config import AppConfig, ServerConfig
from universal_mcp.servers.server import LocalServer
from universal_mcp.tools.local_registry import LocalRegistry


@pytest.fixture
def registry():
    """Provides a fresh LocalRegistry for each test."""
    return LocalRegistry()


@pytest.mark.asyncio
async def test_local_server_initialization(registry: LocalRegistry):
    """Test that the server initializes correctly and loads default tools."""
    apps_list = [AppConfig(name="sample")]
    server_config = ServerConfig(apps=apps_list)
    server = LocalServer(server_config, registry=registry)

    assert server is not None
    assert server.registry is registry

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}

    # By default, only "important" tools should be loaded
    assert "sample__get_current_time" in tool_names
    assert "sample__calculate" in tool_names
    assert "sample__generate_image" in tool_names
    # This tool is not tagged as important
    assert "sample__get_simple_weather" not in tool_names


@pytest.mark.asyncio
async def test_local_server_loads_specific_actions(registry: LocalRegistry):
    """Test that the server loads only the actions specified in the config."""
    actions = ["get_current_date", "calculate"]
    apps_list = [AppConfig(name="sample", actions=actions)]
    server_config = ServerConfig(apps=apps_list)
    server = LocalServer(server_config, registry=registry)

    tools = await server.list_tools()
    assert len(tools) == 2
    tool_names = {tool.name for tool in tools}
    assert tool_names == {"sample__get_current_date", "sample__calculate"}


@pytest.mark.asyncio
async def test_local_server_no_apps(registry: LocalRegistry):
    """Test that the server handles a config with no apps gracefully."""
    server_config = ServerConfig(apps=[])
    server = LocalServer(server_config, registry=registry)

    tools = await server.list_tools()
    assert len(tools) == 0


@pytest.mark.asyncio
async def test_local_server_tool_call(registry: LocalRegistry):
    """Test that a tool can be successfully called through the server."""
    apps_list = [AppConfig(name="sample", actions=["get_current_date"])]
    server_config = ServerConfig(apps=apps_list)
    server = LocalServer(server_config, registry=registry)

    # Test tool call
    result = await server.call_tool("sample__get_current_date", {})
    assert result is not None
    # A basic check on the result format
    assert isinstance(result[0].text, str)
    assert "-" in result[0].text
