import pytest

from universal_mcp.applications.sample.app import SampleApp


@pytest.mark.asyncio
async def test_sample_app_initialization():
    """Test that the SampleApp initializes correctly."""
    app = SampleApp()

    # Check app initialized
    assert app is not None
    assert app.name == "sample"


@pytest.mark.asyncio
async def test_sample_app_tools():
    """Test that the SampleApp provides the expected tools."""
    app = SampleApp()

    # Get list of tools
    tools = app.list_tools()

    # Check that tools are available
    assert len(tools) > 0

    # Check specific tools exist
    tool_names = [tool.__name__ for tool in tools]
    expected_tools = [
        "get_current_time",
        "get_current_date",
        "calculate",
        "read_file",
        "write_file",
        "get_simple_weather",
        "generate_image",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names


@pytest.mark.asyncio
async def test_sample_app_basic_functionality():
    """Test basic functionality of SampleApp tools."""
    app = SampleApp()

    # Test get_current_time
    current_time = app.get_current_time()
    assert isinstance(current_time, str)
    assert len(current_time) > 0

    # Test get_current_date
    current_date = app.get_current_date()
    assert isinstance(current_date, str)
    assert len(current_date) > 0

    # Test calculate
    result = app.calculate("2 + 2")
    assert "Result: 4" in result

    # Test calculate with error
    error_result = app.calculate("invalid expression")
    assert "Error in calculation" in error_result
