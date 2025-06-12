import inspect
import json
from collections.abc import Awaitable, Callable, Sequence
from typing import (
    Annotated,
    Any,
    ForwardRef,
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
        "any": "string",
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

            annotation_for_field_builder: Any

            if sig_annotation is None:
                annotation_for_field_builder = type(None)
            elif sig_annotation is inspect.Parameter.empty:
                py_type_from_doc = _map_docstring_type_to_python_type(docstring_type_str)

                if py_type_from_doc is Any and not docstring_type_str:
                    schema_type_for_any = _map_docstring_type_to_schema_type(docstring_type_str)
                    annotation_for_field_builder = Annotated[
                        Any, Field(json_schema_extra={"type": schema_type_for_any})
                    ]
                else:
                    annotation_for_field_builder = py_type_from_doc
            else:  # Parameter has a type hint in the signature
                annotation_for_field_builder = _get_typed_annotation(sig_annotation, globalns)

            field_info = FieldInfo.from_annotated_attribute(annotation_for_field_builder, default_val)

            if field_info.description is None and docstring_description:
                field_info.description = docstring_description

            if field_info.title is None:
                field_info.title = param.name

            core_type_for_model = field_info.annotation

            dynamic_pydantic_model_params[param.name] = (core_type_for_model, field_info)

        arguments_model = create_model(
            f"{func.__name__}Arguments",
            **dynamic_pydantic_model_params,
            __base__=ArgModelBase,
        )
        return FuncMetadata(arg_model=arguments_model)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    current_file = Path(__file__).resolve()
    package_source_parent_dir = current_file.parent.parent.parent

    if str(package_source_parent_dir) not in sys.path:
        sys.path.insert(0, str(package_source_parent_dir))
        print(f"DEBUG: Added to sys.path: {package_source_parent_dir}")

    from universal_mcp.tools.docstring_parser import parse_docstring

    def post_crm_v_objects_emails_create(self, associations, properties) -> dict[str, Any]:
        """

        Creates an email object in the CRM using the POST method, allowing for the association of metadata with the email and requiring authentication via OAuth2 or private apps to access the necessary permissions.

        Args:
            associations (array): associations Example: [{Category': 'HUBSPOT_DEFINED', 'associationTypeId': 2}]}].
            properties (object): No description provided. Example: "{'ncy': 'monthly'}".

        Returns:
            dict[str, Any]: successful operation

        Raises:
            HTTPError: Raised when the API request fails (e.g., non-2XX status code).
            JSONDecodeError: Raised if the response body cannot be parsed as JSON.

        Tags:
            Basic
        """
        request_body_data = None
        request_body_data = {"associations": associations, "properties": properties}
        request_body_data = {k: v for k, v in request_body_data.items() if v is not None}
        url = f"{self.main_app_client.base_url}/crm/v3/objects/emails"
        query_params = {}
        response = self._post(url, data=request_body_data, params=query_params, content_type="application/json")
        response.raise_for_status()
        if response.status_code == 204 or not response.content or (not response.text.strip()):
            return None
        try:
            return response.json()
        except ValueError:
            return None

    print("--- Testing FuncMetadata with get_weather function ---")

    raw_doc = inspect.getdoc(post_crm_v_objects_emails_create)
    parsed_doc_info = parse_docstring(raw_doc)
    arg_descriptions_from_doc = parsed_doc_info.get("args", {})  # Extract just the args part

    print("\n1. Parsed Argument Descriptions from Docstring (for FuncMetadata input):")
    print(json.dumps(arg_descriptions_from_doc, indent=2))

    # 2. Create FuncMetadata instance
    # The arg_description parameter expects a dict mapping arg name to its details
    func_arg_metadata_instance = FuncMetadata.func_metadata(
        post_crm_v_objects_emails_create, arg_description=arg_descriptions_from_doc
    )

    print("\n2. FuncMetadata Instance (its __repr__):")
    print(func_arg_metadata_instance)

    # 3. Get and print the JSON schema for the arguments model
    parameters_schema = func_arg_metadata_instance.arg_model.model_json_schema()
    print("\n3. Generated JSON Schema for Parameters (from arg_model.model_json_schema()):")
    print(json.dumps(parameters_schema, indent=2))

    print("\n--- Test Complete ---")
