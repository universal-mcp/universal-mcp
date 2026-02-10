"""Tool format adapters - convert FastMCP Tools to various formats."""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastmcp.tools import Tool
from loguru import logger

from universal_mcp.types import ToolFormat


def convert_tools(tools: list[Tool], format: ToolFormat) -> list[Any]:
    """Convert a list of FastMCP Tool objects to a specified format."""
    if format == ToolFormat.NATIVE:
        return [convert_to_native_tool(tool) for tool in tools]
    if format == ToolFormat.MCP:
        return [tool.to_mcp_tool() for tool in tools]
    if format == ToolFormat.LANGCHAIN:
        return [convert_tool_to_langchain_tool(tool) for tool in tools]
    if format == ToolFormat.OPENAI:
        return [convert_tool_to_openai_tool(tool) for tool in tools]
    raise ValueError(f"Invalid format: {format}")


def convert_to_native_tool(tool: Tool) -> Callable[..., Any]:
    """Convert a FastMCP Tool to a plain callable."""
    fn = getattr(tool, "fn", None)
    if fn is None:
        raise ValueError(f"Tool '{tool.name}' has no underlying function")
    wrapper: Callable[..., Any]
    if inspect.iscoroutinefunction(fn):
        @wraps(fn)
        async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await fn(*args, **kwargs)
        wrapper = _async_wrapper
    else:
        @wraps(fn)
        def _sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)
        wrapper = _sync_wrapper

    wrapper.__name__ = tool.name
    wrapper.__doc__ = getattr(fn, "__doc__", None)
    return wrapper


def convert_tool_to_openai_tool(tool: Tool) -> dict[str, Any]:
    """Convert a FastMCP Tool to an OpenAI function tool definition."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.parameters,
        },
    }


def convert_tool_to_langchain_tool(tool: Tool):
    """Convert a FastMCP Tool to a LangChain StructuredTool."""
    from langchain_core.tools import StructuredTool

    full_docstring = inspect.getdoc(getattr(tool, "fn", None))

    async def call_tool(**arguments: dict[str, Any]):
        result = await tool.run(arguments)
        return result

    return StructuredTool(
        name=tool.name,
        description=full_docstring or tool.description or "",
        coroutine=call_tool,
        response_format="content",
        args_schema=tool.parameters,
    )


def transform_mcp_tool_to_openai_tool(mcp_tool):
    """Convert an MCP Tool to an OpenAI ChatCompletionToolParam."""
    from openai.types.chat import ChatCompletionToolParam

    return ChatCompletionToolParam(
        type="function",
        function={
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.inputSchema,
            "strict": False,
        },
    )
