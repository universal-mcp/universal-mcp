# Types API

Type definitions, enums, and constants used throughout universal-mcp.

## Module Reference

::: universal_mcp.types
    options:
      show_source: false

## Common Enums

### IntegrationType

```python
from universal_mcp.types import IntegrationType

IntegrationType.API_KEY    # "api_key"
IntegrationType.OAUTH      # "oauth"
IntegrationType.AGENTR     # "agentr"
```

### StoreType

```python
from universal_mcp.types import StoreType

StoreType.MEMORY       # "memory"
StoreType.ENVIRONMENT  # "environment"
StoreType.KEYRING      # "keyring"
```

## Usage Examples

### Using Enums

```python
from universal_mcp.types import IntegrationType, StoreType

# Type-safe configuration
integration_type = IntegrationType.OAUTH
store_type = StoreType.KEYRING

# String comparison
if integration.type == IntegrationType.API_KEY:
    # Handle API key integration
    pass
```

### Type Aliases

```python
from universal_mcp.types import ToolDict, CredentialsDict

# Type hints
def process_tool(tool: ToolDict) -> None:
    """Process a tool dictionary."""
    pass

def store_credentials(creds: CredentialsDict) -> None:
    """Store credentials dictionary."""
    pass
```

## Constants

```python
from universal_mcp.types import (
    DEFAULT_TIMEOUT,
    DEFAULT_CALLBACK_PORT,
    MCP_VERSION
)

print(DEFAULT_TIMEOUT)        # 30 (seconds)
print(DEFAULT_CALLBACK_PORT)  # 8080
print(MCP_VERSION)            # "1.0.0"
```

## Related Documentation

- [Configuration API](config.md) - Using types in config
- [Integrations API](integrations.md) - Integration types
- [Stores API](stores.md) - Store types
