# Adapters API

Tool format converters for different AI frameworks.

## Overview

Adapters convert universal-mcp tools to different formats:
- **MCP Adapter**: Native MCP format (default)
- **LangChain Adapter**: LangChain tool format
- **OpenAI Adapter**: OpenAI function calling format

## Adapters Module

::: universal_mcp.tools.adapters
    options:
      show_source: false

## Usage Examples

### MCP Format (Native)

```python
from universal_mcp.tools import Tool

def get_weather(city: str) -> dict:
    """Get weather for a city."""
    return {"temp": 72, "condition": "sunny"}

tool = Tool.from_function(get_weather)

# MCP format (default)
mcp_format = tool.to_mcp()
print(mcp_format)
# {
#   "name": "get_weather",
#   "description": "Get weather for a city",
#   "inputSchema": {
#     "type": "object",
#     "properties": {
#       "city": {"type": "string"}
#     },
#     "required": ["city"]
#   }
# }
```

### LangChain Format

```python
from universal_mcp.tools.adapters import to_langchain

# Convert tool to LangChain format
langchain_tool = to_langchain(tool)

# Use with LangChain
from langchain.agents import initialize_agent

agent = initialize_agent(
    tools=[langchain_tool],
    llm=llm,
    agent="zero-shot-react-description"
)
```

### OpenAI Function Format

```python
from universal_mcp.tools.adapters import to_openai

# Convert tool to OpenAI function format
openai_function = to_openai(tool)

# Use with OpenAI API
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[...],
    functions=[openai_function]
)
```

### Batch Conversion

```python
from universal_mcp.tools.adapters import convert_tools

tools = [tool1, tool2, tool3]

# Convert all to LangChain
langchain_tools = convert_tools(tools, format="langchain")

# Convert all to OpenAI
openai_functions = convert_tools(tools, format="openai")
```

## Related Documentation

- [Tools API](tools.md) - Tool creation
- [Applications API](applications.md) - Creating tools
