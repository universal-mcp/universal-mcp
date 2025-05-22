
import inspect
import json
from collections.abc import Awaitable, Callable, Sequence
from typing import (
    Annotated,
    Any,
    ForwardRef,
    Type,
)

from mcp.server.fastmcp.exceptions import InvalidSignature # Assuming this path is correct
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
        "number": float,
        "bool": bool,
        "boolean": bool,
        "list": list,
        "array": list, 
        "dict": dict,
        "object": dict,
        "any": Any,
    }
    return mapping.get(type_str_lower, Any) 

def _map_docstring_type_to_schema_type(type_str: str | None) -> str:
    """Maps common docstring type strings to JSON schema type strings."""
    # This function might not be strictly needed if Pydantic correctly infers
    # schema types from Python types, but kept for explicitness if used.
    # The primary use-case now is for json_schema_extra for untyped Any.
    if not type_str:
        return "string" 
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
        "any": "string", # Defaulting "any" from docstring to schema "string" if not more specific
    }
    return mapping.get(type_str_lower, "string")


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
    def model_dump_one_level(self) -> dict[str, Any]:
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
        arg_description: dict[str, dict[str, str | None]] | None = None,
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

            sig_annotation = param.annotation
            default_val = param.default if param.default is not inspect.Parameter.empty else PydanticUndefined

            param_doc_info = arg_description_map.get(param.name, {})
            docstring_description = param_doc_info.get("description")
            docstring_type_str = param_doc_info.get("type_str")
            
            # This will be the annotation passed to FieldInfo.from_annotated_attribute
            annotation_for_field_builder: Any

            if sig_annotation is None: # Handles `x: None` or `x: None = None`
                annotation_for_field_builder = Type[None]
            elif sig_annotation is inspect.Parameter.empty: # Parameter is untyped in signature
                py_type_from_doc = _map_docstring_type_to_python_type(docstring_type_str) # Defaults to Any

                # If truly untyped (no type in signature, no type string in docstring),
                # tests expect schema type "string". We achieve this by using
                # Field(json_schema_extra={"type": "string"}).
                # _map_docstring_type_to_schema_type(None) defaults to "string".
                if py_type_from_doc is Any and not docstring_type_str:
                    schema_type_for_any = _map_docstring_type_to_schema_type(docstring_type_str)
                    annotation_for_field_builder = Annotated[Any, Field(json_schema_extra={"type": schema_type_for_any})]
                else:
                    # Type comes from docstring (e.g., "(int)", "(list)")
                    # Or docstring specified "(any)" which maps to Python Any.
                    # Pydantic infers schema type from py_type_from_doc (e.g., int -> "integer", list -> "array").
                    annotation_for_field_builder = py_type_from_doc
            else: # Parameter has a type hint in the signature
                annotation_for_field_builder = _get_typed_annotation(sig_annotation, globalns)

            # Create FieldInfo. This correctly processes annotation_for_field_builder,
            # including any nested Annotated[Type, Field(...)] or constraints.
            field_info = FieldInfo.from_annotated_attribute(annotation_for_field_builder, default_val)

            # Augment title and description on the FieldInfo object if they weren't already provided
            # by Field(title=...) or Field(description=...) in an Annotated hint.
            if field_info.description is None and docstring_description:
                field_info.description = docstring_description
            
            if field_info.title is None:
                field_info.title = param.name # Default title to parameter name

            # field_info.annotation contains the core Python type (e.g., int from Annotated[int, Field(...)])
            core_type_for_model = field_info.annotation
            
            dynamic_pydantic_model_params[param.name] = (core_type_for_model, field_info)

        arguments_model = create_model(
            f"{func.__name__}Arguments",
            **dynamic_pydantic_model_params,
            __base__=ArgModelBase,
        )
        return FuncMetadata(arg_model=arguments_model)
