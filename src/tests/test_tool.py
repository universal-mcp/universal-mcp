from typing import Annotated

from pydantic import Field

from universal_mcp.tools.func_metadata import FuncMetadata


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