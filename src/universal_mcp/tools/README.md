# Universal MCP Tools

This directory contains the core tooling infrastructure for Universal MCP, providing a flexible and extensible framework for defining, managing, and converting tools across different formats.

## Components

### `tools.py`
The main module containing the core tool management functionality:

- `Tool` class: Represents a tool with metadata, validation, and execution capabilities
- `ToolManager` class: Manages tool registration, lookup, and execution
- Conversion utilities for different tool formats (OpenAI, LangChain, MCP)

### `adapters.py`
Contains adapters for converting tools between different formats:
- `convert_tool_to_mcp_tool`: Converts a tool to MCP format
- `convert_tool_to_langchain_tool`: Converts a tool to LangChain format

### `func_metadata.py`
Provides function metadata and argument validation:
- `FuncMetadata` class: Handles function signature analysis and argument validation
- `ArgModelBase` class: Base model for function arguments
- Utilities for parsing and validating function signatures

## Usage

### Creating a Tool

```python
from universal_mcp.tools import Tool

def my_tool(param1: str, param2: int) -> str:
    """A simple tool that does something.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    return f"Result: {param1} {param2}"

tool = Tool.from_function(my_tool)
```

### Managing Tools

```python
from universal_mcp.tools import ToolManager

manager = ToolManager()
manager.add_tool(my_tool)

# Get a tool by name
tool = manager.get_tool("my_tool")

# List all tools in a specific format
tools = manager.list_tools(format="openai")  # or "langchain" or "mcp"
```

### Converting Tools

```python
from universal_mcp.tools import convert_tool_to_langchain_tool

langchain_tool = convert_tool_to_langchain_tool(tool)
```

## Features

- Automatic docstring parsing for tool metadata
- Type validation using Pydantic
- Support for both sync and async tools
- JSON schema generation for tool parameters
- Error handling and analytics tracking
- Tag-based tool organization
- Multiple format support (OpenAI, LangChain, MCP)

## Best Practices

1. Always provide clear docstrings for your tools
2. Use type hints for better validation
3. Handle errors appropriately in your tool implementations
4. Use tags to organize related tools
5. Consider async implementations for I/O-bound operations
