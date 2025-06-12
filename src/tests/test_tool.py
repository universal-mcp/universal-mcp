import inspect
from typing import Annotated

from pydantic import Field

from universal_mcp.tools.docstring_parser import parse_docstring  # Assuming this is the updated one
from universal_mcp.tools.func_metadata import FuncMetadata
from universal_mcp.tools.tools import Tool


def test_func_metadata_annotated():
    def func(a: Annotated[int, Field(title="First integer")], b: int):
        """Test function with annotated and typed args"""
        return a + b

    meta = FuncMetadata.func_metadata(func)
    schema = meta.arg_model.model_json_schema()
    assert schema["properties"]["a"]["type"] == "integer"
    assert schema["properties"]["a"]["title"] == "First integer"  # From Annotated
    assert schema["properties"]["b"]["type"] == "integer"
    assert schema["properties"]["b"]["title"] == "b"  # Pydantic's default title is field name
    assert "a" in schema["required"]
    assert "b" in schema["required"]


def test_func_metadata_no_annotated():
    def func(a: int, b: int):
        """Test function with no annotated args

        Args:
            a: The first integer
            b: The second integer
        """
        return a + b

    raw_doc = inspect.getdoc(func)
    parsed_doc = parse_docstring(raw_doc)
    arg_descriptions_for_func_metadata = parsed_doc.get("args", {})

    meta = FuncMetadata.func_metadata(func, arg_description=arg_descriptions_for_func_metadata)
    schema = meta.arg_model.model_json_schema()

    assert schema["properties"]["a"]["type"] == "integer"
    # Title might be "a" by default, description "The first integer"
    assert schema["properties"]["a"].get("description") == "The first integer"
    assert schema["properties"]["a"].get("title") == "a"
    assert schema["properties"]["b"]["type"] == "integer"
    assert schema["properties"]["b"].get("description") == "The second integer"
    assert schema["properties"]["b"].get("title") == "b"
    assert "a" in schema["required"]
    assert "b" in schema["required"]


def test_func_metadata_no_args():
    def func():
        """Test function with no args"""
        return 42

    meta = FuncMetadata.func_metadata(func)
    schema = meta.arg_model.model_json_schema()
    assert schema["properties"] == {}
    assert schema.get("required") is None or len(schema.get("required", [])) == 0


def test_func_metadata_untyped_no_docstring_type():
    def func(a, b=10):
        """Test function with untyped args
        Args:
            a: Untyped a
            b: Untyped b with default
        """  # No type_str in docstring
        return a + b

    raw_doc = inspect.getdoc(func)
    parsed_doc = parse_docstring(raw_doc)
    arg_descriptions_for_func_metadata = parsed_doc.get("args", {})

    meta = FuncMetadata.func_metadata(func, arg_description=arg_descriptions_for_func_metadata)
    schema = meta.arg_model.model_json_schema()

    assert schema["properties"]["a"]["type"] == "string"  # Default schema type for Any
    assert schema["properties"]["a"].get("description") == "Untyped a"
    assert schema["properties"]["b"]["type"] == "string"
    assert schema["properties"]["b"].get("description") == "Untyped b with default"
    assert schema["properties"]["b"]["default"] == 10
    assert "a" in schema["required"]
    assert "b" not in schema.get("required", [])


def test_func_metadata_required():
    def func(a: int, b: str, c: float = 1.0):
        """Test function with required and optional args
        Args:
            a: An int
            b: A string
            c: A float
        """
        return f"{a} {b} {c}"

    raw_doc = inspect.getdoc(func)
    parsed_doc = parse_docstring(raw_doc)
    arg_descriptions_for_func_metadata = parsed_doc.get("args", {})

    meta = FuncMetadata.func_metadata(func, arg_description=arg_descriptions_for_func_metadata)
    schema = meta.arg_model.model_json_schema()

    assert schema["properties"]["a"]["type"] == "integer"
    assert schema["properties"]["a"].get("description") == "An int"
    assert schema["properties"]["b"]["type"] == "string"
    assert schema["properties"]["b"].get("description") == "A string"
    assert schema["properties"]["c"]["type"] == "number"
    assert schema["properties"]["c"].get("description") == "A float"
    assert schema["properties"]["c"]["default"] == 1.0
    assert "a" in schema["required"]
    assert "b" in schema["required"]
    assert "c" not in schema.get("required", [])


def test_func_metadata_none_type():
    def func(a: None = None):
        """Test function with None type
        Args:
            a: A None value
        """
        return a

    raw_doc = inspect.getdoc(func)
    parsed_doc = parse_docstring(raw_doc)
    arg_descriptions_for_func_metadata = parsed_doc.get("args", {})

    meta = FuncMetadata.func_metadata(func, arg_description=arg_descriptions_for_func_metadata)
    schema = meta.arg_model.model_json_schema()
    assert schema["properties"]["a"]["type"] == "null"
    assert schema["properties"]["a"].get("description") == "A None value"
    assert schema["properties"]["a"]["default"] is None


def test_parse_docstring_empty_none():
    docstring = None
    expected = {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}
    assert parse_docstring(docstring) == expected


def test_parse_docstring_empty_string():
    docstring = ""
    expected = {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}
    assert parse_docstring(docstring) == expected


def test_parse_docstring_whitespace_string():
    docstring = "   \n  "
    expected = {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_only():
    docstring = "This is a short summary.\nIt spans multiple lines."
    expected = {
        "summary": "This is a short summary. It spans multiple lines.",
        "args": {},
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_args_no_type_str():
    docstring = "Function to add two numbers.\n\nArgs:\n    a: The first number.\n    b: The second number."
    expected = {
        "summary": "Function to add two numbers.",
        "args": {
            "a": {"description": "The first number.", "type_str": None},
            "b": {"description": "The second number.", "type_str": None},
        },
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_returns():
    docstring = "Calculates the sum.\n\nReturns:\n    The sum of a and b."
    expected = {
        "summary": "Calculates the sum.",
        "args": {},
        "returns": "The sum of a and b.",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_raises():
    docstring = "Divides two numbers.\n\nRaises:\n    ZeroDivisionError: If the denominator is zero."
    expected = {
        "summary": "Divides two numbers.",
        "args": {},
        "returns": "",
        "raises": {"ZeroDivisionError": "If the denominator is zero."},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_summary_and_tags():
    docstring = "Processes data.\n\nTags:\n    data, processing, important"
    expected = {
        "summary": "Processes data.",
        "args": {},
        "returns": "",
        "raises": {},
        "tags": ["data", "processing", "important"],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_multiple_sections_single_line():
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
        "args": {"input": {"description": "Input value.", "type_str": None}},
        "returns": "Output value.",
        "raises": {"Exception": "If something goes wrong."},
        "tags": ["basic", "test"],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_args_multi_line():
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
            "config": {
                "description": "Configuration object. It contains settings for the processing job, including connection details and parameters.",
                "type_str": None,
            }
        },
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_returns_multi_line():
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
    docstring = "Args:\n    data: The data to process.\nReturns:\n    Processed data."
    expected = {
        "summary": "",
        "args": {"data": {"description": "The data to process.", "type_str": None}},
        "returns": "Processed data.",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_with_type_str():
    docstring = """
    Processes an item.

    Args:
        item_id (int): The ID of the item.
        name (str): The name of the item.
        details (object): Optional details.
    """
    expected = {
        "summary": "Processes an item.",
        "args": {
            "item_id": {"description": "The ID of the item.", "type_str": "int"},
            "name": {"description": "The name of the item.", "type_str": "str"},
            "details": {"description": "Optional details.", "type_str": "object"},
        },
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_with_mixed_type_str_and_none():
    docstring = """
    Handles configuration.

    Args:
        path (string): Path to config file.
        strict_mode: Enable strict mode. (No type in docstring)
        retries (integer): Number of retries.
    """
    expected = {
        "summary": "Handles configuration.",
        "args": {
            "path": {"description": "Path to config file.", "type_str": "string"},
            "strict_mode": {
                "description": "Enable strict mode. (No type in docstring)",
                "type_str": None,
            },  # Corrected description
            "retries": {"description": "Number of retries.", "type_str": "integer"},
        },
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_parse_docstring_type_str_with_spaces_in_type():
    docstring = """
    Args:
        complex_type (list of strings): A list containing strings.
    """
    expected = {
        "summary": "",
        "args": {
            "complex_type": {"description": "A list containing strings.", "type_str": "list of strings"},
        },
        "returns": "",
        "raises": {},
        "tags": [],
    }
    assert parse_docstring(docstring) == expected


def test_func_metadata_untyped_with_docstring_type():
    def func(name, age, data=None):
        """Test function with untyped args but types in docstring
        Args:
            name (str): The name.
            age (int): The age.
            data (list): Optional data.
        """
        return f"{name} is {age}"

    raw_doc = inspect.getdoc(func)
    parsed_doc = parse_docstring(raw_doc)
    arg_descriptions_for_func_metadata = parsed_doc.get("args", {})

    meta = FuncMetadata.func_metadata(func, arg_description=arg_descriptions_for_func_metadata)
    schema = meta.arg_model.model_json_schema()

    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["name"].get("description") == "The name."
    assert schema["properties"]["age"]["type"] == "integer"
    assert schema["properties"]["age"].get("description") == "The age."
    assert schema["properties"]["data"]["type"] == "array"
    assert schema["properties"]["data"].get("description") == "Optional data."
    assert schema["properties"]["data"]["default"] is None

    assert "name" in schema["required"]
    assert "age" in schema["required"]
    assert "data" not in schema.get("required", [])


def test_func_metadata_mixed_hints_and_docstring_types():
    def func(item_id: int, quantity, details: str = "default details"):
        """
        Processes an order.

        Args:
            item_id: The ID of the item (already typed).
            quantity (integer): The number of items.
            details (string): Order details.
        """
        return item_id * quantity

    raw_doc = inspect.getdoc(func)
    parsed_doc = parse_docstring(raw_doc)
    arg_descriptions_for_func_metadata = parsed_doc.get("args", {})

    meta = FuncMetadata.func_metadata(func, arg_description=arg_descriptions_for_func_metadata)
    schema = meta.arg_model.model_json_schema()

    assert schema["properties"]["item_id"]["type"] == "integer"
    assert schema["properties"]["item_id"].get("description") == "The ID of the item (already typed)."

    assert schema["properties"]["quantity"]["type"] == "integer"
    assert schema["properties"]["quantity"].get("description") == "The number of items."

    assert schema["properties"]["details"]["type"] == "string"
    assert schema["properties"]["details"].get("description") == "Order details."
    assert schema["properties"]["details"]["default"] == "default details"

    assert "item_id" in schema["required"]
    assert "quantity" in schema["required"]
    assert "details" not in schema.get("required", [])


def test_tool_from_function_with_docstring_types():
    """Test the full Tool.from_function flow with docstring types"""

    def my_tool(name, age=30):
        """
        A simple tool.

        Args:
            name (string): The name to use.
            age (int): The age value.
        Returns:
            A greeting string.
        """
        return f"Hello {name}, you are {age}."

    tool_instance = Tool.from_function(my_tool)

    assert tool_instance.name == "my_tool"
    assert tool_instance.description == "A simple tool."
    assert tool_instance.args_description == {"name": "The name to use.", "age": "The age value."}
    assert tool_instance.returns_description == "A greeting string."

    meta_schema = tool_instance.fn_metadata.arg_model.model_json_schema()
    assert meta_schema["properties"]["name"]["type"] == "string"
    assert meta_schema["properties"]["name"].get("description") == "The name to use."
    assert meta_schema["properties"]["age"]["type"] == "integer"
    assert meta_schema["properties"]["age"].get("description") == "The age value."
    assert meta_schema["properties"]["age"]["default"] == 30
    assert "name" in meta_schema["required"]
    assert "age" not in meta_schema.get("required", [])
