"""Tests for LocalRegistry - a catalog of available apps and tools."""

import pytest

from universal_mcp.exceptions import ToolNotFoundError
from universal_mcp.tools.local_registry import LocalRegistry
from fastmcp.tools import Tool


class MockApp:
    """Mock application for testing."""

    def __init__(self):
        self.name = "mock_app"

    def list_tools(self):
        return [self.search, self.create_user]

    @staticmethod
    def search(query: str) -> str:
        """Search for something.

        Args:
            query: The search query

        Returns:
            Search results

        Tags: search, important
        """
        return f"Results for: {query}"

    @staticmethod
    def create_user(name: str, age: int) -> str:
        """Create a user.

        Args:
            name: User name
            age: User age

        Returns:
            Created user info

        Tags: user
        """
        return f"Created user: {name}, age {age}"


class TestLocalRegistryBasics:
    """Basic registry operations."""

    def test_init(self):
        registry = LocalRegistry(output_dir="test_output")
        assert len(registry) == 0
        assert registry.list_apps() == []
        assert repr(registry) == "LocalRegistry(apps=0, tools=0)"

    def test_register_tool_function(self):
        registry = LocalRegistry()

        async def greet(name: str) -> str:
            """Say hello.

            Args:
                name: Who to greet

            Returns:
                Greeting
            """
            return f"Hello, {name}!"

        tool = registry.register_tool(greet)
        assert tool.name == "greet"
        assert len(registry) == 1

    def test_register_tool_with_app_name(self):
        registry = LocalRegistry()

        async def fetch(url: str) -> str:
            """Fetch a URL.

            Args:
                url: The URL

            Returns:
                Content
            """
            return url

        tool = registry.register_tool(fetch, app_name="http")
        assert tool.name == "http__fetch"
        assert "http" in tool.tags

    def test_register_tool_instance(self):
        registry = LocalRegistry()

        def double(x: int) -> int:
            """Double a number.

            Args:
                x: Input

            Returns:
                Doubled
            """
            return x * 2

        tool = Tool.from_function(double)
        registered = registry.register_tool(tool, app_name="math")
        assert registered.name == "double"
        assert len(registry) == 1


class TestLocalRegistryApps:
    """App registration and management."""

    def test_register_app(self):
        registry = LocalRegistry()
        app = MockApp()

        registry.register_app(app)

        assert "mock_app" in registry.list_apps()
        assert registry.get_app("mock_app") is app
        assert len(registry) > 0

    def test_register_app_with_specific_tools(self):
        registry = LocalRegistry()
        app = MockApp()

        registry.register_app(app, tool_names=["search"])

        tools = registry.list_tools()
        tool_names = [t.name.split("__")[-1] for t in tools]
        assert "search" in tool_names
        assert "create_user" not in tool_names

    def test_remove_app(self):
        registry = LocalRegistry()
        app = MockApp()
        registry.register_app(app)

        assert registry.remove_app("mock_app") is True
        assert "mock_app" not in registry.list_apps()
        assert len(registry) == 0

    def test_remove_nonexistent_app(self):
        registry = LocalRegistry()
        assert registry.remove_app("nope") is False

    def test_get_nonexistent_app(self):
        registry = LocalRegistry()
        assert registry.get_app("nope") is None


class TestLocalRegistryQuery:
    """Querying and filtering tools."""

    def test_list_tools_by_tags(self):
        registry = LocalRegistry()

        async def search_fn(q: str) -> str:
            """Search.

            Args:
                q: Query

            Returns:
                Results

            Tags: search
            """
            return q

        async def admin_fn(cmd: str) -> str:
            """Admin.

            Args:
                cmd: Command

            Returns:
                Result

            Tags: admin
            """
            return cmd

        registry.register_tool(search_fn)
        registry.register_tool(admin_fn)

        assert len(registry.list_tools(tags=["search"])) == 1
        assert len(registry.list_tools(tags=["admin"])) == 1
        assert len(registry.list_tools()) == 2

    def test_remove_tool(self):
        registry = LocalRegistry()

        async def temp(x: int) -> int:
            """Temp.

            Args:
                x: Input

            Returns:
                Output
            """
            return x

        tool = registry.register_tool(temp, app_name="tmp")
        assert len(registry) == 1

        assert registry.remove_tool(tool.name) is True
        assert len(registry) == 0
        assert registry.remove_tool(tool.name) is False

    def test_clear(self):
        registry = LocalRegistry()
        app = MockApp()
        registry.register_app(app)

        async def extra(x: int) -> int:
            """Extra.

            Args:
                x: Input

            Returns:
                Output
            """
            return x

        registry.register_tool(extra)
        assert len(registry) > 0

        registry.clear()
        assert len(registry) == 0
        assert registry.list_apps() == []


class TestLocalRegistrySearch:
    """Search capabilities."""

    def _build_registry(self):
        """Helper: registry with a few tools and apps."""
        registry = LocalRegistry()

        class GithubApp:
            name = "github"
            def list_tools(self):
                return [self.create_issue, self.list_repos]
            @staticmethod
            def create_issue(title: str) -> str:
                """Create a GitHub issue.

                Args:
                    title: Issue title

                Returns:
                    Created issue URL

                Tags: issues, important
                """
                return title
            @staticmethod
            def list_repos(org: str) -> list:
                """List repositories for an org.

                Args:
                    org: Organization name

                Returns:
                    List of repos

                Tags: repos, important
                """
                return []

        class SlackApp:
            name = "slack"
            def list_tools(self):
                return [self.send_message]
            @staticmethod
            def send_message(channel: str, text: str) -> str:
                """Send a Slack message.

                Args:
                    channel: Channel name
                    text: Message text

                Returns:
                    Message ID

                Tags: messaging, important
                """
                return "ok"

        registry.register_app(GithubApp())
        registry.register_app(SlackApp())
        return registry

    # ── search_apps ───────────────────────────────────────

    def test_search_apps_exact(self):
        registry = self._build_registry()
        assert registry.search_apps("github") == ["github"]

    def test_search_apps_substring(self):
        registry = self._build_registry()
        assert registry.search_apps("git") == ["github"]

    def test_search_apps_case_insensitive(self):
        registry = self._build_registry()
        assert registry.search_apps("SLACK") == ["slack"]

    def test_search_apps_no_match(self):
        registry = self._build_registry()
        assert registry.search_apps("jira") == []

    def test_search_apps_multiple_matches(self):
        registry = self._build_registry()
        # both "github" and "slack" contain "a"
        results = registry.search_apps("a")
        assert "slack" in results

    # ── search_tools ──────────────────────────────────────

    def test_search_tools_by_name(self):
        registry = self._build_registry()
        results = registry.search_tools("create_issue")
        assert len(results) == 1
        assert results[0].name.endswith("create_issue")

    def test_search_tools_by_partial_name(self):
        registry = self._build_registry()
        results = registry.search_tools("issue")
        assert len(results) == 1

    def test_search_tools_by_description(self):
        registry = self._build_registry()
        results = registry.search_tools("Slack message")
        assert len(results) == 1
        assert results[0].name.endswith("send_message")

    def test_search_tools_by_tag(self):
        registry = self._build_registry()
        results = registry.search_tools("messaging")
        assert len(results) == 1
        assert results[0].name.endswith("send_message")

    def test_search_tools_by_app_name(self):
        registry = self._build_registry()
        results = registry.search_tools("github")
        # should match tools whose app_name is "github"
        assert all(t.name.startswith("github__") for t in results)
        assert len(results) == 2

    def test_search_tools_case_insensitive(self):
        registry = self._build_registry()
        results = registry.search_tools("REPOS")
        assert len(results) == 1

    def test_search_tools_no_match(self):
        registry = self._build_registry()
        assert registry.search_tools("zzz_nonexistent") == []

    def test_search_tools_broad_query(self):
        registry = self._build_registry()
        # "important" tag is on all three tools
        results = registry.search_tools("important")
        assert len(results) == 3


@pytest.mark.asyncio
class TestLocalRegistryExecution:
    """Tool execution."""

    async def test_call_tool(self):
        registry = LocalRegistry()

        async def multiply(a: int, b: int) -> int:
            """Multiply two numbers.

            Args:
                a: First
                b: Second

            Returns:
                Product
            """
            return a * b

        tool = registry.register_tool(multiply)
        result = await registry.call_tool(tool.name, {"a": 5, "b": 3})
        assert result == "15"

    async def test_call_nonexistent_tool(self):
        registry = LocalRegistry()
        with pytest.raises(ToolNotFoundError):
            await registry.call_tool("nope", {})

    async def test_call_app_tool(self):
        registry = LocalRegistry()
        app = MockApp()
        registry.register_app(app)

        tools = registry.list_tools()
        search_tool = next(t for t in tools if t.name.endswith("search"))

        result = await registry.call_tool(search_tool.name, {"query": "python"})
        assert result == "Results for: python"
