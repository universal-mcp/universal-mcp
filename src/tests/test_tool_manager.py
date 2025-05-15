import pytest

from universal_mcp.applications.application import BaseApplication
from universal_mcp.exceptions import ToolError
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.manager import Tool, ToolManager


# Dummy tools for testing
async def dummy_add(a: int, b: int) -> int:
    """
    Adds two integers asynchronously.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The sum of a and b.

    Tags:
        math, important
    """
    return a + b


async def dummy_multiply(a: int, b: int) -> int:
    """
    Multiplies two integers asynchronously.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The product of a and b.

    Tags:
        math
    """
    return a * b


async def dummy_error() -> None:
    """
    Raises a ValueError for testing error handling.

    Raises:
        ValueError: Always raised with the message "Test error".

    Tags:
        test
    """
    raise ValueError("Test error")


@pytest.fixture
def tool_manager():
    return ToolManager()


@pytest.fixture
def dummy_tools():
    return [Tool.from_function(dummy_add), Tool.from_function(dummy_multiply), Tool.from_function(dummy_error)]


class ExampleApp(BaseApplication):
    def __init__(self):
        super().__init__(name="example_app")

    def list_tools(self):
        return [dummy_add, dummy_multiply, dummy_error]


def test_add_tool(tool_manager):
    tool = tool_manager.add_tool(dummy_add)
    assert tool.name == "dummy_add"
    assert tool.name in [t.name for t in tool_manager.list_tools()]


def test_add_duplicate_tool(tool_manager):
    tool1 = tool_manager.add_tool(dummy_add)
    tool2 = tool_manager.add_tool(dummy_add)
    assert tool1 is tool2  # Should return existing tool
    assert len(tool_manager.list_tools()) == 1


def test_remove_tool(tool_manager):
    tool = tool_manager.add_tool(dummy_add)
    assert tool_manager.remove_tool(tool.name) is True
    assert tool_manager.get_tool(tool.name) is None
    assert tool_manager.remove_tool("nonexistent") is False


def test_clear_tools(tool_manager, dummy_tools):
    for tool in dummy_tools:
        tool_manager.add_tool(tool)
    assert len(tool_manager.list_tools()) == 3
    tool_manager.clear_tools()
    assert len(tool_manager.list_tools()) == 0


def test_list_tools_format(tool_manager, dummy_tools):
    for tool in dummy_tools:
        tool_manager.add_tool(tool)

    # Test MCP format
    mcp_tools = tool_manager.list_tools(format=ToolFormat.MCP)
    assert len(mcp_tools) == 3

    # Test LangChain format
    langchain_tools = tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
    assert len(langchain_tools) == 3

    # Test OpenAI format
    openai_tools = tool_manager.list_tools(format=ToolFormat.OPENAI)
    assert len(openai_tools) == 3


def test_filter_tools_by_tags(tool_manager, dummy_tools):
    for tool in dummy_tools:
        tool_manager.add_tool(tool)

    # Test filtering by important tag
    important_tools = tool_manager.list_tools(tags=["important"])
    assert len(important_tools) == 1
    assert important_tools[0].name == "dummy_add"

    # Test filtering by math tag
    math_tools = tool_manager.list_tools(tags=["math"])
    assert len(math_tools) == 2


@pytest.mark.asyncio
async def test_call_tool_success(tool_manager):
    tool_manager.add_tool(dummy_add)
    result = await tool_manager.call_tool("dummy_add", {"a": 2, "b": 3})
    assert result == 5


@pytest.mark.asyncio
async def test_call_tool_error(tool_manager):
    tool_manager.add_tool(dummy_error)
    with pytest.raises(ToolError):
        await tool_manager.call_tool("dummy_error", {})


@pytest.mark.asyncio
async def test_call_nonexistent_tool(tool_manager):
    with pytest.raises(ToolError):
        await tool_manager.call_tool("nonexistent", {})


@pytest.mark.asyncio
async def test_call_tool_from_app(tool_manager):
    app = ExampleApp()
    # Only important are added by default
    tool_manager.register_tools_from_app(app)
    tools = tool_manager.list_tools()
    assert len(tools) == 1
    assert "example_app_dummy_add" in [t.name for t in tools]
    result = await tool_manager.call_tool("example_app_dummy_add", {"a": 2, "b": 3})
    assert result == 5


@pytest.mark.asyncio
async def test_call_tool_from_app_with_tags(tool_manager):
    app = ExampleApp()
    # Only important are added by default
    tool_manager.register_tools_from_app(app, tags=["math"])
    tools = tool_manager.list_tools()
    assert len(tools) == 2
    assert "example_app_dummy_add" in [t.name for t in tools]
    assert "example_app_dummy_multiply" in [t.name for t in tools]


@pytest.mark.asyncio
async def test_load_tool_from_name(tool_manager):
    app = ExampleApp()
    # Only important are added by default
    tool_manager.register_tools_from_app(app, tool_names=["dummy_multiply", "dummy_add"])
    tools = tool_manager.list_tools()
    assert len(tools) == 2
    assert "example_app_dummy_multiply" in [t.name for t in tools]
    assert "example_app_dummy_add" in [t.name for t in tools]
