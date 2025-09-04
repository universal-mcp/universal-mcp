import inspect
from collections.abc import Callable
from typing import Any
import functools
import httpx
from pydantic import BaseModel, Field, create_model

from universal_mcp.exceptions import NotAuthorizedError, ToolError
from universal_mcp.tools.docstring_parser import parse_docstring
from universal_mcp.types import TOOL_NAME_SEPARATOR

from .func_metadata import FuncMetadata


def _get_return_type_schema(return_annotation: Any) -> dict[str, Any] | None:
    """Convert return type annotation to JSON schema using Pydantic."""
    if return_annotation == inspect.Signature.empty or return_annotation == Any:
        return None

    try:
        temp_model = create_model("ReturnTypeModel", return_value=(return_annotation, ...))

        full_schema = temp_model.model_json_schema()
        return_field_schema = full_schema.get("properties", {}).get("return_value")

        return return_field_schema
    except Exception:
        return None


class Tool(BaseModel):
    """Internal tool registration info."""

    fn: Callable[..., Any] = Field(exclude=True)
    app_name: str | None = Field(default=None, description="Name of the app that the tool belongs to")
    tool_name: str = Field(description="Name of the tool")
    description: str | None = Field(default=None, description="Summary line from the tool's docstring")
    args_description: dict[str, str] = Field(
        default_factory=dict, description="Descriptions of arguments from the docstring"
    )
    returns_description: str = Field(default="", description="Description of the return value from the docstring")
    raises_description: dict[str, str] = Field(
        default_factory=dict,
        description="Descriptions of exceptions raised from the docstring",
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorizing the tool")
    parameters: dict[str, Any] = Field(description="JSON schema for tool parameters")
    output_schema: dict[str, Any] | None = Field(default=None, description="JSON schema for tool output")
    fn_metadata: FuncMetadata | None = Field(
        default=None, description="Metadata about the function including a pydantic model for tool arguments"
    )
    is_async: bool = Field(description="Whether the tool is async")

    @property
    def name(self) -> str:
        return f"{self.app_name}{TOOL_NAME_SEPARATOR}{self.tool_name}" if self.app_name else self.tool_name

    @classmethod
    def from_function(
        cls,
        fn: Callable[..., Any],
        name: str | None = None,
    ) -> "Tool":
        """Create a Tool from a function."""

        # --- START: MODIFIED LOGIC TO HANDLE functools.partial ---
        skip_names = ()
        if isinstance(fn, functools.partial):
            func_for_inspection = fn.func
            # Determine which argument names are already bound in the partial
            sig = inspect.signature(func_for_inspection)
            param_names = list(sig.parameters.keys())
            num_bound_args = len(fn.args)
            skip_names = tuple(param_names[:num_bound_args])
        else:
            func_for_inspection = fn
        # --- END: MODIFIED LOGIC ---

        # Use the underlying function for its name and metadata
        func_name = name or func_for_inspection.__name__

        if func_name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")

        raw_doc = inspect.getdoc(func_for_inspection)
        parsed_doc = parse_docstring(raw_doc)

        is_async = inspect.iscoroutinefunction(func_for_inspection)

        # Pass the original function for inspection and tell it which names to skip
        func_arg_metadata = FuncMetadata.func_metadata(
            func_for_inspection, 
            arg_description=parsed_doc["args"],
            skip_names=skip_names # <-- Pass the names of bound arguments to be skipped
        )
        parameters = func_arg_metadata.arg_model.model_json_schema()

        sig = inspect.signature(func_for_inspection)
        output_schema = _get_return_type_schema(sig.return_annotation)

        simple_args_descriptions: dict[str, str] = {}
        if parsed_doc.get("args"):
            for arg_name, arg_details in parsed_doc["args"].items():
                if isinstance(arg_details, dict):
                    simple_args_descriptions[arg_name] = arg_details.get("description") or ""

        return cls(
            fn=fn, #<-- IMPORTANT: Store the original callable (which is the partial object) for execution
            tool_name=func_name,
            description=parsed_doc["summary"],
            args_description=simple_args_descriptions,
            returns_description=parsed_doc["returns"],
            raises_description=parsed_doc["raises"],
            tags=parsed_doc["tags"],
            parameters=parameters,
            output_schema=output_schema,
            fn_metadata=func_arg_metadata,
            is_async=is_async,
        )

    async def run(
        self,
        arguments: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Run the tool with arguments."""
        try:
            return await self.fn_metadata.call_fn_with_arg_validation(
                self.fn, self.is_async, arguments, None, context=context
            )
        except NotAuthorizedError as e:
            message = f"Not authorized to call tool {self.name}: {e.message}"
            return message
        except httpx.HTTPStatusError as e:
            error_body = e.response.text or "<empty response>"
            message = f"HTTP Error, status code: {e.response.status_code}, error body: {error_body}"
            raise ToolError(message) from e
        except ValueError as e:
            message = f"Invalid arguments for tool {self.name}: {e}"
            raise ToolError(message) from e
        except Exception as e:
            raise ToolError(f"Error executing tool {self.name}: {e}") from e
