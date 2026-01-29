# Exceptions API

Exception hierarchy for universal-mcp errors.

## Authentication Exceptions

::: universal_mcp.exceptions.NotAuthorizedError
    options:
      show_source: false

## Store Exceptions

::: universal_mcp.exceptions.StoreError
    options:
      show_source: false

::: universal_mcp.exceptions.KeyNotFoundError
    options:
      show_source: false

## Tool Exceptions

::: universal_mcp.exceptions.ToolError
    options:
      show_source: false

::: universal_mcp.exceptions.ToolNotFoundError
    options:
      show_source: false

## Configuration Exceptions

::: universal_mcp.exceptions.ConfigurationError
    options:
      show_source: false

## Signature Exceptions

::: universal_mcp.exceptions.InvalidSignature
    options:
      show_source: false

## Usage Examples

### Handling Authentication Errors

```python
from universal_mcp.exceptions import NotAuthorizedError, KeyNotFoundError

try:
    creds = integration.get_credentials()
except NotAuthorizedError:
    print("Not authorized. Please run authorize():")
    print(integration.authorize())
except KeyNotFoundError as e:
    print(f"Missing key: {e.key}")
    # Prompt user to set key
```

### Handling Tool Errors

```python
from universal_mcp.exceptions import ToolNotFoundError, ToolError

try:
    result = server.call_tool("my_tool", args)
except ToolNotFoundError:
    print("Tool not found")
    # List available tools
    print("Available:", [t.name for t in server.list_tools()])
except ToolError as e:
    print(f"Tool error: {e}")
```

### Exception Hierarchy

```
Exception (Python base)
├── NotAuthorizedError
├── StoreError
│   └── KeyNotFoundError
├── ToolError
├── ToolNotFoundError
├── ConfigurationError
└── InvalidSignature
```

## Related Documentation

- [Integrations API](integrations.md) - Authentication errors
- [Tools API](tools.md) - Tool execution errors
