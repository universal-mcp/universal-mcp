# Tools API

The tools system converts Python functions into AI-callable tools with JSON schemas.

## Tool

::: universal_mcp.tools.tools.Tool
    options:
      show_source: false

## ToolManager

::: universal_mcp.tools.manager.ToolManager
    options:
      show_source: false

## FuncMetadata

::: universal_mcp.tools.func_metadata.FuncMetadata
    options:
      show_source: false

## Usage Examples

### Creating Tools from Functions

```python
from universal_mcp.tools import Tool

def greet(name: str, greeting: str = "Hello") -> str:
    """Greet someone by name.

    Args:
        name: Person's name
        greeting: Greeting word (default: Hello)

    Returns:
        Greeting message
    """
    return f"{greeting}, {name}!"

# Create tool from function
tool = Tool.from_function(greet)

print(tool.name)  # "greet"
print(tool.description)  # "Greet someone by name"
print(tool.inputSchema)
# {
#   "type": "object",
#   "properties": {
#     "name": {"type": "string", "description": "Person's name"},
#     "greeting": {
#       "type": "string",
#       "description": "Greeting word (default: Hello)",
#       "default": "Hello"
#     }
#   },
#   "required": ["name"]
# }

# Execute tool
result = tool.execute(name="Alice", greeting="Hi")
print(result)  # "Hi, Alice!"
```

### Using ToolManager

```python
from universal_mcp.tools import ToolManager, Tool

manager = ToolManager()

# Add tools
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

manager.add_tool(Tool.from_function(add))
manager.add_tool(Tool.from_function(multiply))

# List tools
tools = manager.list_tools()
print([t.name for t in tools])  # ["add", "multiply"]

# Get specific tool
tool = manager.get_tool("add")

# Call tool by name
result = manager.call_tool("add", {"a": 5, "b": 3})
print(result)  # 8
```

### Complex Type Examples

#### Lists and Dicts

```python
def process_items(
    items: list[str],
    config: dict[str, any] | None = None
) -> dict:
    """Process a list of items.

    Args:
        items: List of item names
        config: Optional configuration dict

    Returns:
        Processing results
    """
    # ...
```

Generated schema:
```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {"type": "string"}
    },
    "config": {
      "type": "object"
    }
  },
  "required": ["items"]
}
```

#### Literal Types (Enums)

```python
from typing import Literal

def set_log_level(
    level: Literal["debug", "info", "warning", "error"]
) -> None:
    """Set logging level.

    Args:
        level: Log level to set
    """
    # ...
```

Generated schema:
```json
{
  "type": "object",
  "properties": {
    "level": {
      "type": "string",
      "enum": ["debug", "info", "warning", "error"]
    }
  },
  "required": ["level"]
}
```

#### Union Types

```python
def search(query: str | int) -> list[dict]:
    """Search by query (text or ID).

    Args:
        query: Search query (string) or ID (integer)

    Returns:
        Search results
    """
    # ...
```

Generated schema:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "anyOf": [
        {"type": "string"},
        {"type": "integer"}
      ]
    }
  },
  "required": ["query"]
}
```

### FuncMetadata Examples

```python
from universal_mcp.tools import FuncMetadata

def example_func(arg1: str, arg2: int = 10) -> dict:
    """Example function.

    Args:
        arg1: First argument
        arg2: Second argument

    Returns:
        Result dictionary
    """
    pass

# Extract metadata
metadata = FuncMetadata.extract_from_function(example_func)

print(metadata.name)  # "example_func"
print(metadata.description)  # "Example function"
print(metadata.parameters)
# {
#   "arg1": {
#     "type": "string",
#     "description": "First argument",
#     "required": True
#   },
#   "arg2": {
#     "type": "integer",
#     "description": "Second argument",
#     "default": 10,
#     "required": False
#   }
# }
```

## Docstring Formats

### Google Style (Recommended)

```python
def function(arg1: str, arg2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong
    """
```

### NumPy Style

```python
def function(arg1: str, arg2: int) -> bool:
    """Short description.

    Longer description if needed.

    Parameters
    ----------
    arg1 : str
        Description of arg1
    arg2 : int
        Description of arg2

    Returns
    -------
    bool
        Description of return value
    """
```

### reStructuredText Style

```python
def function(arg1: str, arg2: int) -> bool:
    """Short description.

    Longer description if needed.

    :param arg1: Description of arg1
    :param arg2: Description of arg2
    :return: Description of return value
    :rtype: bool
    """
```

## Tool Validation

Tools validate arguments against their schema:

```python
tool = Tool.from_function(greet)

# Valid call
result = tool.execute(name="Alice")  # OK

# Invalid: missing required argument
try:
    tool.execute(greeting="Hi")  # Missing 'name'
except Exception as e:
    print(e)  # Validation error

# Invalid: wrong type
try:
    tool.execute(name=123)  # name should be string
except Exception as e:
    print(e)  # Type error
```

## Advanced: Custom Tool Creation

```python
from universal_mcp.tools import Tool

# Create tool manually (without function)
tool = Tool(
    name="custom_tool",
    description="A custom tool",
    inputSchema={
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        },
        "required": ["input"]
    },
    fn=lambda input: f"Processed: {input}"
)

result = tool.execute(input="test")
print(result)  # "Processed: test"
```

## Best Practices

### 1. Write Clear Docstrings

```python
# Good
def create_user(name: str, email: str) -> dict:
    """Create a new user account.

    Args:
        name: Full name (2-50 characters)
        email: Valid email address

    Returns:
        Created user object with id and created_at timestamp
    """

# Bad
def create_user(name: str, email: str) -> dict:
    """Creates user."""  # Too brief, no details
```

### 2. Use Type Hints

```python
# Good
def search(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> list[dict]:

# Bad
def search(query, limit=10, offset=0):
    # No schema can be generated
```

### 3. Use Literal for Enums

```python
# Good - generates proper enum
from typing import Literal

def sort(
    order: Literal["asc", "desc"]
) -> list:

# Bad - accepts any string
def sort(order: str) -> list:
```

### 4. Document Exceptions

```python
def divide(a: float, b: float) -> float:
    """Divide two numbers.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Result of division

    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

## Related Documentation

- [Architecture: Tool Registration](../architecture/tool-registration.md) - Registration flow
- [Applications API](applications.md) - Creating tool providers
- [Adapters API](adapters.md) - Converting tool formats
