from __future__ import annotations as _annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.utilities.func_metadata import FuncMetadata, func_metadata
from mcp.server.fastmcp.utilities.docstring_parser import parse_docstring

if TYPE_CHECKING:
    from mcp.server.fastmcp.server import Context
    from mcp.server.session import ServerSessionT
    from mcp.shared.context import LifespanContextT


class Tool(BaseModel):
    """Internal tool registration info."""

    fn: Callable[..., Any] = Field(exclude=True)
    name: str = Field(description="Name of the tool")
    
    summary: str = Field(description="Summary line from the tool's docstring")
    
    args_description: dict[str, str] = Field(
        default_factory=dict, description="Descriptions of arguments from the docstring"
    )
    returns_description: str = Field(
        default="", description="Description of the return value from the docstring"
    )
    raises_description: dict[str, str] = Field(
        default_factory=dict, description="Descriptions of exceptions raised from the docstring"
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorizing the tool")
    
    parameters: dict[str, Any] = Field(description="JSON schema for tool parameters")
    fn_metadata: FuncMetadata = Field(
        description="Metadata about the function including a pydantic model for tool"
        " arguments"
    )
    
    is_async: bool = Field(description="Whether the tool is async")
    context_kwarg: str | None = Field(
        None, description="Name of the kwarg that should receive context"
    )

    @classmethod
    def from_function(
        cls,
        fn: Callable[..., Any],
        name: str | None = None,
        context_kwarg: str | None = None,
    ) -> Tool:
        """Create a Tool from a function."""
        from mcp.server.fastmcp import Context

        func_name = name or fn.__name__

        if func_name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")

        raw_doc = inspect.getdoc(fn)
        parsed_doc = parse_docstring(raw_doc)
        
        is_async = inspect.iscoroutinefunction(fn)

        if context_kwarg is None:
            sig = inspect.signature(fn)
            for param_name, param in sig.parameters.items():
                if param.annotation is Context:
                    context_kwarg = param_name
                    break

        func_arg_metadata = func_metadata(
            fn,
            skip_names=[context_kwarg] if context_kwarg is not None else [],
        )
        parameters = func_arg_metadata.arg_model.model_json_schema()

        return cls(
            fn=fn,
            name=func_name,
            summary=parsed_doc["summary"],
            args_description=parsed_doc["args"],
            returns_description=parsed_doc["returns"],
            raises_description=parsed_doc["raises"],
            tags=parsed_doc["tags"],
            parameters=parameters,
            fn_metadata=func_arg_metadata,
            is_async=is_async,
            context_kwarg=context_kwarg,
        )

    async def run(
        self,
        arguments: dict[str, Any],
        context: Context[ServerSessionT, LifespanContextT] | None = None,
    ) -> Any:
        """Run the tool with arguments."""
        try:
            return await self.fn_metadata.call_fn_with_arg_validation(
                self.fn,
                self.is_async,
                arguments,
                {self.context_kwarg: context}
                if self.context_kwarg is not None
                else None,
            )
        except Exception as e:
            raise ToolError(f"Error executing tool {self.name}: {e}") from e
