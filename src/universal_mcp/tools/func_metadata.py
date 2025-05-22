import inspect
import json
from collections.abc import Awaitable, Callable, Sequence
from typing import (
    Annotated,
    Any,
    ForwardRef,
    Type,
)

from mcp.server.fastmcp.exceptions import InvalidSignature
from pydantic import BaseModel, ConfigDict, Field, WithJsonSchema, create_model
from pydantic._internal._typing_extra import eval_type_backport
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined


def _map_docstring_type_to_python_type(type_str: str | None) -> Any:
    """Maps common docstring type strings to Python types."""
    if not type_str:
        return Any
    type_str_lower = type_str.lower()
    mapping = {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "number": float,  # Or consider decimal.Decimal if precision is key
        "bool": bool,
        "boolean": bool,
        "list": list,
        "array": list, # Common in OpenAPI/JS docstrings
        "dict": dict,
        "object": dict, # Common in OpenAPI/JS docstrings
        "any": Any,
        # Add more mappings as needed
    }
    return mapping.get(type_str_lower, Any) # Default to Any if unrecognized

def _map_docstring_type_to_schema_type(type_str: str | None) -> str:
    """Maps common docstring type strings to JSON schema type strings."""
    if not type_str:
        return "string" # Default schema type if not specified or recognized
    type_str_lower = type_str.lower()
    mapping = {
        "str": "string",
        "string": "string",
        "int": "integer",
        "integer": "integer",
        "float": "number",
        "number": "number",
        "bool": "boolean",
        "boolean": "boolean",
        "list": "array",
        "array": "array",
        "dict": "object",
        "object": "object",
        "any": "object", # Or "string" / "any" if your schema validator supports it
                         # "object" is a safe bet for generic "any"
        # Add more mappings as needed
    }
    return mapping.get(type_str_lower, "string") # Default to "string" if unrecognized


def _get_typed_annotation(annotation: Any, globalns: dict[str, Any]) -> Any:
    def try_eval_type(value: Any, globalns: dict[str, Any], localns: dict[str, Any]) -> tuple[Any, bool]:
        try:
            return eval_type_backport(value, globalns, localns), True
        except NameError:
            return value, False

    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation, status = try_eval_type(annotation, globalns, globalns)

        if status is False:
            raise InvalidSignature(f"Unable to evaluate type annotation {annotation}")

    return annotation


def _get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    """Get function signature while evaluating forward references"""
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=_get_typed_annotation(param.annotation, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


class ArgModelBase(BaseModel):
    """A model representing the arguments to a function."""

    def model_dump_one_level(self) -> dict[str, Any]:
        """Return a dict of the model's fields, one level deep.

        That is, sub-models etc are not dumped - they are kept as pydantic models.
        """
        kwargs: dict[str, Any] = {}
        for field_name in self.__class__.model_fields:
            kwargs[field_name] = getattr(self, field_name)
        return kwargs

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class FuncMetadata(BaseModel):
    arg_model: Annotated[type[ArgModelBase], WithJsonSchema(None)]

    async def call_fn_with_arg_validation(
        self,
        fn: Callable[..., Any] | Awaitable[Any],
        fn_is_async: bool,
        arguments_to_validate: dict[str, Any],
        arguments_to_pass_directly: dict[str, Any] | None,
        context: dict[str, Any] | None = None,
    ) -> Any:
        arguments_pre_parsed = self.pre_parse_json(arguments_to_validate)
        arguments_parsed_model = self.arg_model.model_validate(arguments_pre_parsed)
        arguments_parsed_dict = arguments_parsed_model.model_dump_one_level()

        arguments_parsed_dict |= arguments_to_pass_directly or {}

        if fn_is_async:
            if isinstance(fn, Awaitable):
                return await fn
            return await fn(**arguments_parsed_dict)
        if isinstance(fn, Callable):
            return fn(**arguments_parsed_dict)
        raise TypeError("fn must be either Callable or Awaitable")

    def pre_parse_json(self, data: dict[str, Any]) -> dict[str, Any]:
        new_data = data.copy()
        for field_name, _field_info in self.arg_model.model_fields.items():
            if field_name not in data:
                continue
            if isinstance(data[field_name], str):
                try:
                    pre_parsed = json.loads(data[field_name])
                except json.JSONDecodeError:
                    continue
                if isinstance(pre_parsed, str | int | float):
                    continue
                new_data[field_name] = pre_parsed
        assert new_data.keys() == data.keys()
        return new_data

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @classmethod
    def func_metadata(
        cls,
        func: Callable[..., Any],
        skip_names: Sequence[str] = (),
        arg_description: dict[str, dict[str, str | None]] | None = None, # Updated signature
    ) -> "FuncMetadata":
        sig = _get_typed_signature(func)
        params = sig.parameters
        dynamic_pydantic_model_params: dict[str, Any] = {}
        globalns = getattr(func, "__globals__", {})

        arg_description_map = arg_description or {}

        for param in params.values():
            if param.name.startswith("_"):
                raise InvalidSignature(f"Parameter {param.name} of {func.__name__} cannot start with '_'")
            if param.name in skip_names:
                continue

            annotation = param.annotation
            param_doc_info = arg_description_map.get(param.name)
            docstring_description = param_doc_info.get("description") if param_doc_info else None
            docstring_type_str = param_doc_info.get("type_str") if param_doc_info else None

            # `x: None` / `x: None = None`
            if annotation is None:
                annotation = Annotated[
                    Type[None], # Use Type[None] for clarity, though None works
                    Field(default=param.default if param.default is not inspect.Parameter.empty else PydanticUndefined),
                ]

            elif annotation is inspect.Parameter.empty:
                if docstring_type_str:
                    # Type hint from docstring
                    resolved_python_type = _map_docstring_type_to_python_type(docstring_type_str)
                    resolved_schema_type = _map_docstring_type_to_schema_type(docstring_type_str)
                    annotation = Annotated[
                        resolved_python_type,
                        Field(default=param.default if param.default is not inspect.Parameter.empty else PydanticUndefined),
                        WithJsonSchema({"title": param.name, "type": resolved_schema_type, "description": docstring_description or ""})
                    ]
                else:
                    annotation = Annotated[
                        Any,
                        Field(default=param.default if param.default is not inspect.Parameter.empty else PydanticUndefined),
                        WithJsonSchema({"title": param.name, "type": "string", "description": docstring_description or ""}),
                    ]
            
            else:
                _existing_field_info = FieldInfo.from_annotated_attribute(
                    _get_typed_annotation(annotation, globalns),
                     param.default if param.default is not inspect.Parameter.empty else PydanticUndefined
                )
                current_schema_dict = _existing_field_info.json_schema_extra or {}
                if isinstance(current_schema_dict, dict): # Ensure it's a dict
                    if not current_schema_dict.get("description") and docstring_description:
                        current_schema_dict["description"] = docstring_description
                    if not current_schema_dict.get("title"): # Prefer title from FieldInfo if set
                         current_schema_dict["title"] = _existing_field_info.title or param.name

                if current_schema_dict: # Only add WithJsonSchema if there's something to add/override
                     annotation = Annotated[
                        _existing_field_info.annotation, # Use the resolved annotation from FieldInfo
                        _existing_field_info, # Pass the existing FieldInfo itself
                        WithJsonSchema(current_schema_dict)
                    ]
                else: # If no description to add, keep original annotation logic
                    annotation = _existing_field_info.annotation # The core type
            field_info = FieldInfo.from_annotated_attribute(
                _get_typed_annotation(annotation, globalns), # Ensure ForwardRefs are resolved
                param.default if param.default is not inspect.Parameter.empty else PydanticUndefined,
            )
            if not field_info.description and docstring_description:
                field_info.description = docstring_description
            
            if not field_info.title:
                field_info.title = param.name

            dynamic_pydantic_model_params[param.name] = (
                field_info.annotation, # This should be the core Python type
                field_info,             # This carries all metadata (default, description, schema_extra)
            )

        arguments_model = create_model(
            f"{func.__name__}Arguments",
            **dynamic_pydantic_model_params,
            __base__=ArgModelBase,
        )
        resp = FuncMetadata(arg_model=arguments_model)
        return resp
    