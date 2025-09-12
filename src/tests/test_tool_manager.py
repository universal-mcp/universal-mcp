import pytest

from universal_mcp.applications.application import BaseApplication
from universal_mcp.tools.manager import Tool, ToolManager
from universal_mcp.types import TOOL_NAME_SEPARATOR


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


def test_add_tool(tool_manager: ToolManager):
    tool = tool_manager.add_tool(dummy_add)
    assert tool.name == "dummy_add"
    assert tool.name in [t.name for t in tool_manager.get_tools()]


def test_add_duplicate_tool(tool_manager: ToolManager):
    tool1 = tool_manager.add_tool(dummy_add)
    tool2 = tool_manager.add_tool(dummy_add)
    assert tool1 is tool2  # Should return existing tool
    assert len(tool_manager.get_tools()) == 1


def test_remove_tool(tool_manager: ToolManager):
    tool = tool_manager.add_tool(dummy_add)
    assert tool_manager.remove_tool(tool.name) is True
    assert tool_manager.get_tool(tool.name) is None
    assert tool_manager.remove_tool("nonexistent") is False


def test_clear_tools(tool_manager: ToolManager, dummy_tools):
    for tool in dummy_tools:
        tool_manager.add_tool(tool)
    assert len(tool_manager.get_tools()) == 3
    tool_manager.clear_tools()
    assert len(tool_manager.get_tools()) == 0


def test_get_tools_no_filters(tool_manager: ToolManager, dummy_tools):
    for tool in dummy_tools:
        tool_manager.add_tool(tool)

    tools = tool_manager.get_tools()
    assert len(tools) == 3


def test_filter_tools_by_tags(tool_manager: ToolManager, dummy_tools):
    for tool in dummy_tools:
        tool_manager.add_tool(tool)

    # Test filtering by important tag
    important_tools = tool_manager.get_tools(tags=["important"])
    assert len(important_tools) == 1
    assert important_tools[0].name == "dummy_add"

    # Test filtering by math tag
    math_tools = tool_manager.get_tools(tags=["math"])
    assert len(math_tools) == 2


@pytest.mark.asyncio
async def test_call_tool_from_app_with_tags(tool_manager: ToolManager):
    app = ExampleApp()
    # Only important are added by default
    tool_manager.register_tools_from_app(app, tags=["math"])
    tools = tool_manager.get_tools()
    assert len(tools) == 2
    assert "example_app__dummy_add" in [t.name for t in tools]
    assert "example_app__dummy_multiply" in [t.name for t in tools]


@pytest.mark.asyncio
async def test_load_tool_from_name(tool_manager: ToolManager):
    app = ExampleApp()
    # Only important are added by default
    tool_manager.register_tools_from_app(app, tool_names=["dummy_multiply", "dummy_add"])
    tools = tool_manager.get_tools()
    assert len(tools) == 2
    assert f"example_app{TOOL_NAME_SEPARATOR}dummy_multiply" in [t.name for t in tools]
    assert f"example_app{TOOL_NAME_SEPARATOR}dummy_add" in [t.name for t in tools]
