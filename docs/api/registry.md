# Registry API

Tool registry implementations for managing tool storage and discovery.

## ToolRegistry

::: universal_mcp.tools.registry.ToolRegistry
    options:
      show_source: false

## LocalRegistry

::: universal_mcp.tools.local_registry.LocalRegistry
    options:
      show_source: false

## Usage Examples

### Basic Registry Usage

```python
from universal_mcp.tools import LocalRegistry, Tool

registry = LocalRegistry()

# Register tool
def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

tool = Tool.from_function(greet)
registry.register(tool)

# Get tool
tool = registry.get("greet")

# List all tools
tools = registry.list()

# Check if tool exists
if registry.exists("greet"):
    print("Tool exists")

# Remove tool
registry.unregister("greet")
```

## Related Documentation

- [Tools API](tools.md) - Tool creation and management
- [Servers API](servers.md) - Server using registry
