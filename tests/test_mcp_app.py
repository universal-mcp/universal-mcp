"""Tests for MCP URL application support - ProxyTool, MCPApplication, normalize_mcp_url."""

import pytest

from universal_mcp.applications.mcp_app import (
    MCPApplication,
    ProxyTool,
    _derive_app_name,
    normalize_mcp_url,
)
from universal_mcp.tools.local_registry import LocalRegistry


class TestNormalizeMcpUrl:
    """Tests for URL normalization."""

    def test_adds_https_scheme(self):
        assert normalize_mcp_url("mcp.notion.so") == "https://mcp.notion.so"

    def test_preserves_existing_https(self):
        assert normalize_mcp_url("https://mcp.example.com") == "https://mcp.example.com"

    def test_preserves_existing_http(self):
        assert normalize_mcp_url("http://localhost:8080") == "http://localhost:8080"

    def test_strips_trailing_slash(self):
        assert normalize_mcp_url("https://mcp.example.com/") == "https://mcp.example.com"

    def test_strips_multiple_trailing_slashes(self):
        assert normalize_mcp_url("https://mcp.example.com///") == "https://mcp.example.com"

    def test_preserves_path(self):
        assert normalize_mcp_url("https://mcp.example.com/sse") == "https://mcp.example.com/sse"

    def test_preserves_path_with_trailing_slash_stripped(self):
        assert normalize_mcp_url("https://mcp.example.com/v1/") == "https://mcp.example.com/v1"

    def test_strips_whitespace(self):
        assert normalize_mcp_url("  mcp.notion.so  ") == "https://mcp.notion.so"

    def test_empty_url_raises(self):
        with pytest.raises(ValueError, match="URL cannot be empty"):
            normalize_mcp_url("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="URL cannot be empty"):
            normalize_mcp_url("   ")

    def test_no_scheme_with_path(self):
        assert normalize_mcp_url("mcp.notion.so/v1") == "https://mcp.notion.so/v1"


class TestDeriveAppName:
    """Tests for app name derivation from URLs."""

    def test_notion(self):
        assert _derive_app_name("https://mcp.notion.so") == "notion"

    def test_github_api(self):
        assert _derive_app_name("https://api.github.com/mcp") == "github"

    def test_simple_domain(self):
        assert _derive_app_name("https://example.com") == "example"

    def test_complex_domain(self):
        assert _derive_app_name("https://mcp.stripe.dev/v1") == "stripe"


class TestProxyTool:
    """Tests for ProxyTool construction and execution."""

    @pytest.mark.asyncio
    async def test_proxy_tool_run(self):
        """ProxyTool.run() should call the proxy function with raw arguments."""
        call_log = []

        async def mock_proxy(arguments):
            call_log.append(arguments)
            return "mock result"

        tool = ProxyTool(
            fn=mock_proxy,
            name="test__my_tool",
            description="A test tool",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
            },
        )

        result = await tool.run({"query": "hello"})
        assert len(call_log) == 1
        assert call_log[0] == {"query": "hello"}
        # Result should be a ToolResult with text content
        assert result.content[0].text == "mock result"

    @pytest.mark.asyncio
    async def test_proxy_tool_returns_tool_result(self):
        """ProxyTool should pass through ToolResult if returned by fn."""
        from fastmcp.tools.tool import ToolResult
        from mcp.types import TextContent

        expected = ToolResult(content=[TextContent(type="text", text="direct result")])

        async def mock_proxy(arguments):
            return expected

        tool = ProxyTool(
            fn=mock_proxy,
            name="test__direct",
            description="Returns ToolResult directly",
            parameters={"type": "object", "properties": {}},
        )

        result = await tool.run({})
        assert result is expected

    def test_proxy_tool_attributes(self):
        """ProxyTool should have correct name, description, parameters, tags."""

        async def noop(args):
            pass

        tool = ProxyTool(
            fn=noop,
            name="myapp__do_thing",
            description="Does a thing",
            parameters={
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            },
            tags={"myapp"},
        )

        assert tool.name == "myapp__do_thing"
        assert tool.description == "Does a thing"
        assert tool.parameters["properties"]["x"]["type"] == "integer"
        assert "myapp" in tool.tags


class TestLocalRegistryRemoteApp:
    """Tests for register_remote_app in LocalRegistry."""

    def test_register_remote_app(self):
        """register_remote_app should add tools to the registry."""

        async def noop(args):
            return "ok"

        registry = LocalRegistry()
        tools = [
            ProxyTool(
                fn=noop,
                name="remote__tool_a",
                description="Tool A",
                parameters={"type": "object", "properties": {}},
                tags={"remote"},
            ),
            ProxyTool(
                fn=noop,
                name="remote__tool_b",
                description="Tool B",
                parameters={"type": "object", "properties": {}},
                tags={"remote"},
            ),
        ]

        registry.register_remote_app("remote", tools)

        assert "remote" in registry.list_apps()
        all_tools = registry.list_tools()
        tool_names = {t.name for t in all_tools}
        assert "remote__tool_a" in tool_names
        assert "remote__tool_b" in tool_names

    def test_remove_remote_app(self):
        """Removing a remote app should remove all its tools."""

        async def noop(args):
            return "ok"

        registry = LocalRegistry()
        tools = [
            ProxyTool(
                fn=noop,
                name="remote__tool_a",
                description="Tool A",
                parameters={"type": "object", "properties": {}},
                tags={"remote"},
            ),
        ]

        registry.register_remote_app("remote", tools)
        assert registry.remove_app("remote") is True
        assert "remote" not in registry.list_apps()
        assert len(registry.list_tools()) == 0


class TestMCPApplicationInit:
    """Tests for MCPApplication initialization (no network)."""

    def test_init_normalizes_url(self):
        app = MCPApplication("test", "mcp.example.com")
        assert app.url == "https://mcp.example.com"

    def test_init_stores_headers(self):
        headers = {"Authorization": "Bearer test123"}
        app = MCPApplication("test", "https://mcp.example.com", headers=headers)
        assert app.headers == headers

    def test_init_name(self):
        app = MCPApplication("myapp", "https://mcp.example.com")
        assert app.name == "myapp"

    def test_list_tools_returns_empty(self):
        app = MCPApplication("test", "https://mcp.example.com")
        assert app.list_tools() == []

    def test_get_proxy_tools_before_connect(self):
        app = MCPApplication("test", "https://mcp.example.com")
        assert app.get_proxy_tools() == []
