"""Tests for UniversalMCP SDK."""

import pytest
from pathlib import Path
from universal_mcp.sdk import UniversalMCP


@pytest.fixture
def sdk(tmp_path):
    """Create an SDK instance with memory store and temp manifest."""
    return UniversalMCP(
        store_type="memory",
        manifest_path=tmp_path / "manifest.json",
    )


class TestSDKAppLifecycle:
    """App add/remove/list."""

    def test_init_empty(self, sdk):
        assert sdk.list_apps() == []
        assert sdk.list_tools() == []

    def test_add_app(self, sdk):
        sdk.add("sample")
        assert "sample" in sdk.list_apps()
        assert len(sdk.list_tools()) > 0

    def test_add_app_idempotent(self, sdk):
        sdk.add("sample")
        sdk.add("sample")  # Should not raise
        assert sdk.list_apps().count("sample") == 1

    @pytest.mark.asyncio
    async def test_remove_app(self, sdk):
        sdk.add("sample")
        assert await sdk.remove("sample") is True
        assert "sample" not in sdk.list_apps()
        assert sdk.list_tools() == []

    @pytest.mark.asyncio
    async def test_remove_nonexistent(self, sdk):
        assert await sdk.remove("nope") is False

    def test_add_nonexistent_app(self, sdk):
        with pytest.raises(Exception):
            sdk.add("nonexistent_app_xyz")


class TestSDKTools:
    """Tool listing and search."""

    def test_list_tools(self, sdk):
        sdk.add("sample")
        tools = sdk.list_tools()
        assert len(tools) > 0
        # Each tool should be a dict with name, description, parameters
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool

    def test_list_tools_by_app(self, sdk):
        sdk.add("sample")
        tools = sdk.list_tools(app="sample")
        assert len(tools) > 0
        # All tools should be from the sample app
        for tool in tools:
            assert tool["name"].startswith("sample__")

    def test_search_tools(self, sdk):
        sdk.add("sample")
        results = sdk.search_tools("calculate")
        assert len(results) > 0
        assert any("calculate" in t["name"] for t in results)

    def test_search_no_results(self, sdk):
        sdk.add("sample")
        results = sdk.search_tools("zzz_nonexistent")
        assert results == []


@pytest.mark.asyncio
class TestSDKExecution:
    """Tool execution."""

    async def test_call_tool(self, sdk):
        sdk.add("sample")
        tools = sdk.list_tools()
        # Find a simple tool to test
        calc_tool = next(t for t in tools if "calculate" in t["name"])
        result = await sdk.call_tool(calc_tool["name"], {"expression": "2 + 3"})
        assert "5" in str(result)

    async def test_call_nonexistent_tool(self, sdk):
        from universal_mcp.exceptions import ToolNotFoundError
        with pytest.raises(ToolNotFoundError):
            await sdk.call_tool("nonexistent__tool", {})


@pytest.mark.asyncio
class TestSDKAuthorization:
    """Authorization."""

    async def test_authorize_returns_instructions_when_no_key(self, sdk):
        sdk.add("sample")
        result = await sdk.authorize("sample")
        # Should return instructions since no key provided
        assert isinstance(result, str)

    async def test_authorize_not_added(self, sdk):
        with pytest.raises(KeyError):
            await sdk.authorize("not_added")

    async def test_is_authorized_false(self, sdk):
        sdk.add("sample")
        # Sample app has api_key integration with no key set
        result = await sdk.is_authorized("sample")
        assert isinstance(result, bool)

    async def test_is_authorized_not_added(self, sdk):
        result = await sdk.is_authorized("nope")
        assert result is False


class TestSDKManifest:
    """Manifest persistence."""

    def test_manifest_created_on_add(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        sdk = UniversalMCP(store_type="memory", manifest_path=manifest)
        sdk.add("sample")
        assert manifest.exists()

    def test_manifest_survives_restart(self, tmp_path):
        manifest = tmp_path / "manifest.json"

        # First instance: add app
        sdk1 = UniversalMCP(store_type="memory", manifest_path=manifest)
        sdk1.add("sample")
        tool_count = len(sdk1.list_tools())
        assert tool_count > 0

        # Second instance: should re-hydrate from manifest
        sdk2 = UniversalMCP(store_type="memory", manifest_path=manifest)
        assert "sample" in sdk2.list_apps()
        assert len(sdk2.list_tools()) == tool_count

    @pytest.mark.asyncio
    async def test_manifest_remove_persists(self, tmp_path):
        manifest = tmp_path / "manifest.json"

        sdk1 = UniversalMCP(store_type="memory", manifest_path=manifest)
        sdk1.add("sample")
        await sdk1.remove("sample")

        sdk2 = UniversalMCP(store_type="memory", manifest_path=manifest)
        assert sdk2.list_apps() == []


class TestSDKServer:
    """Server creation."""

    def test_get_server(self, sdk):
        sdk.add("sample")
        server = sdk.get_server("Test Server")
        assert server is not None

    def test_repr(self, sdk):
        assert "UniversalMCP" in repr(sdk)
