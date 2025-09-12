import os
import shutil

import pytest
from langchain_core.tools import StructuredTool
from mcp.server.fastmcp.server import MCPTool

from universal_mcp.exceptions import ToolNotFoundError
from universal_mcp.tools.local_registry import LocalRegistry
from universal_mcp.types import ToolFormat


@pytest.fixture
def registry():
    """Provides a LocalRegistry instance and cleans up the output directory."""
    output_dir = "test_output"
    reg = LocalRegistry(output_dir=output_dir)
    yield reg
    # Cleanup the test output directory after tests are done
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


@pytest.mark.asyncio
async def test_export_tools_formats(registry: LocalRegistry):
    """Verify that tools are exported to all supported formats correctly."""
    tool_names = ["sample__get_current_date", "sample__calculate"]

    # Test MCP Format
    mcp_tools = await registry.export_tools(tool_names, format=ToolFormat.MCP)
    assert len(mcp_tools) == 2
    assert all(isinstance(t, MCPTool) for t in mcp_tools)

    # Test LangChain Format
    langchain_tools = await registry.export_tools(tool_names, format=ToolFormat.LANGCHAIN)
    assert len(langchain_tools) == 2
    assert all(isinstance(t, StructuredTool) for t in langchain_tools)

    # Test OpenAI Format
    openai_tools = await registry.export_tools(tool_names, format=ToolFormat.OPENAI)
    assert len(openai_tools) == 2
    assert all(isinstance(t, dict) and t.get("type") == "function" for t in openai_tools)

    # Test Native Format
    native_tools = await registry.export_tools(tool_names, format=ToolFormat.NATIVE)
    assert len(native_tools) == 2
    assert all(callable(t) for t in native_tools)


@pytest.mark.asyncio
async def test_call_tool_success(registry: LocalRegistry):
    """Test a successful tool call through the registry."""
    await registry.export_tools(["sample__calculate"], format=ToolFormat.NATIVE)  # Load the tool
    result = await registry.call_tool("sample__calculate", {"expression": "10 - 4"})
    assert result == "Result: 6"


@pytest.mark.asyncio
async def test_call_tool_not_found(registry: LocalRegistry):
    """Test that calling a non-existent tool raises the correct exception."""
    with pytest.raises(ToolNotFoundError):
        await registry.call_tool("nonexistent__tool", {})


@pytest.mark.asyncio
async def test_file_output_handling(registry: LocalRegistry):
    """Test that file outputs are correctly handled by writing to a file."""
    tool_name = "sample__generate_image"
    await registry.export_tools([tool_name], format=ToolFormat.NATIVE)  # Load the tool

    result = await registry.call_tool(tool_name, {"prompt": "testing file output"})
    assert isinstance(result, str)
    assert "File saved to:" in result

    # Verify the file was actually created
    file_path = result.split("File saved to: ")[1]
    assert os.path.exists(file_path)


@pytest.mark.asyncio
async def test_unimplemented_methods(registry: LocalRegistry):
    """Test that abstract methods raise NotImplementedError."""
    with pytest.raises(NotImplementedError):
        await registry.list_all_apps()
    with pytest.raises(NotImplementedError):
        await registry.get_app_details("some_app")
    with pytest.raises(NotImplementedError):
        await registry.search_apps("query")
    with pytest.raises(NotImplementedError):
        await registry.list_tools("some_app")
    with pytest.raises(NotImplementedError):
        await registry.search_tools("query")
    with pytest.raises(NotImplementedError):
        await registry.list_connected_apps()
