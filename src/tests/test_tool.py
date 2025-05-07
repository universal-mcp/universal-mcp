from typing import Annotated

from pydantic import Field

from universal_mcp.tools.func_metadata import FuncMetadata
from universal_mcp.tools.tools import Tool
from universal_mcp.utils.docstring_parser import parse_docstring


def test_func_metadata_annotated():
    def func(a: Annotated[int, Field(title="First integer")], b: int):
        """Test function with annotated and typed args"""
        return a + b

    meta = FuncMetadata.func_metadata(func)
    assert meta.arg_model.model_json_schema() == {
        "type": "object",
        "title": "funcArguments",
        "properties": {
            "a": {"type": "integer", "title": "First integer"},
            "b": {"type": "integer", "title": "B"},
        },
        "required": ["a", "b"],
    }


def test_func_metadata_no_annotated():
    def func(a: int, b: int):
        """Test function with no annotated args

        Args:
            a: The first integer
            b: The second integer
        """
        return a + b

    tool = Tool.from_function(func)
    meta = tool.fn_metadata
    assert meta.arg_model.model_json_schema() == {
        "type": "object",
        "title": "funcArguments",
        "properties": {
            "a": {"type": "integer", "title": "The first integer"},
            "b": {"type": "integer", "title": "The second integer"},
        },
        "required": ["a", "b"],
    }


def test_func_metadata_no_args():
    def func():
        """Test function with no args"""
        return 42

    meta = FuncMetadata.func_metadata(func)
    assert meta.arg_model.model_json_schema() == {
        "type": "object",
        "title": "funcArguments",
        "properties": {},
        # "required": [],
    }


def test_func_metadata_untyped():
    def func(a, b=10):
        """Test function with untyped args"""
        return a + b

    meta = FuncMetadata.func_metadata(func)
    assert meta.arg_model.model_json_schema() == {
        "type": "object",
        "title": "funcArguments",
        "properties": {
            "a": {"type": "string", "title": "a"},
            "b": {"type": "string", "title": "b", "default": 10},
        },
        "required": ["a"],
    }


def test_func_metadata_required():
    def func(a: int, b: str, c: float = 1.0):
        """Test function with required and optional args"""
        return f"{a} {b} {c}"

    meta = FuncMetadata.func_metadata(func)
    assert meta.arg_model.model_json_schema() == {
        "type": "object",
        "title": "funcArguments",
        "properties": {
            "a": {"type": "integer", "title": "A"},
            "b": {"type": "string", "title": "B"},
            "c": {"type": "number", "title": "C", "default": 1.0},
        },
        "required": ["a", "b"],
    }


def test_func_metadata_none_type():
    def func(a: None = None):
        """Test function with None type"""
        return a

    meta = FuncMetadata.func_metadata(func)
    assert meta.arg_model.model_json_schema() == {
        "type": "object",
        "title": "funcArguments",
        "properties": {
            "a": {"type": "null", "title": "A", "default": None},
        },
    }


def test_parse_docstring_empty_none():
    """Test with None input."""
    docstring = None
    expected = {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}
    assert parse_docstring(docstring) == expected


def test_parse_docstring_empty_string():
    """Test with an empty string input."""
    docstring = ""
    expected = {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}
    assert parse_docstring(docstring) == expected


def test_parse_docstring_whitespace_string():
    """Test with a whitespace-only string input."""
    docstring = "   \n  "
    expected = {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_only():
    """Test with only a summary and no sections."""
    docstring = """
    This is a short summary.
    It spans multiple lines.
    """
    expected = {
        "summary": "This is a short summary. It spans multiple lines.",
        "args": {},
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_args():
    """Test with summary and an Args section."""
    docstring = """
    Function to add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    expected = {
        "summary": "Function to add two numbers.",
        "args": {"a": "The first number.", "b": "The second number."},
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_returns():
    """Test with summary and a simple Returns section."""
    docstring = """
    Calculates the sum.

    Returns:
        The sum of a and b.
    """
    expected = {
        "summary": "Calculates the sum.",
        "args": {},
        "returns": "The sum of a and b.",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_raises():
    """Test with summary and a simple Raises section."""
    docstring = """
    Divides two numbers.

    Raises:
        ZeroDivisionError: If the denominator is zero.
    """
    expected = {
        "summary": "Divides two numbers.",
        "args": {},
        "returns": "",
        "raises": {"ZeroDivisionError": "If the denominator is zero."},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_tags():
    """Test with summary and a simple Tags section."""
    docstring = """
    Processes data.

    Tags:
        data, processing, important
    """
    expected = {
        "summary": "Processes data.",
        "args": {},
        "returns": "",
        "raises": {},
        "tags": ["data", "processing", "important"],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_multiple_sections_single_line():
    """Test with summary and multiple sections with single-line content."""
    docstring = """
    Performs a basic operation.

    Args:
        input: Input value.
    Returns:
        Output value.
    Raises:
        Exception: If something goes wrong.
    Tags:
        basic, test
    """
    expected = {
        "summary": "Performs a basic operation.",
        "args": {"input": "Input value."},
        "returns": "Output value.",
        "raises": {"Exception": "If something goes wrong."},
        "tags": ["basic", "test"],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_args_multi_line():
    """Test with Args section containing a multi-line description."""
    docstring = """
    Processes complex input.

    Args:
        config: Configuration object.
                It contains settings for the processing job,
                including connection details and parameters.
    """
    expected = {
        "summary": "Processes complex input.",
        "args": {
            "config": "Configuration object. It contains settings for the processing job, including connection details and parameters."
        },
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_returns_multi_line():
    """Test with Returns section spanning multiple lines."""
    docstring = """
    Fetches detailed information.

    Returns:
        A dictionary containing comprehensive details about the fetched data,
        including timestamps, source, and processing status. This is a detailed response.
    """
    expected = {
        "summary": "Fetches detailed information.",
        "args": {},
        "returns": "A dictionary containing comprehensive details about the fetched data, including timestamps, source, and processing status. This is a detailed response.",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_raises_multi_line():
    """Test with Raises section containing a multi-line description for an exception."""
    docstring = """
    Performs a critical action.

    Raises:
        CriticalError: This error indicates a major failure
                       during the critical action execution.
                       Further details are logged separately.
    """
    expected = {
        "summary": "Performs a critical action.",
        "args": {},
        "returns": "",
        "raises": {
            "CriticalError": "This error indicates a major failure during the critical action execution. Further details are logged separately."
        },
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_no_summary():
    """Test a docstring that starts immediately with a section."""
    docstring = """
    Args:
        data: The data to process.
    Returns:
        Processed data.
    """
    expected = {
        "summary": "",
        "args": {"data": "The data to process."},
        "returns": "Processed data.",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected
