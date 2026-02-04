# Configuration API

Pydantic models for server and application configuration.

## ServerConfig

::: universal_mcp.config.ServerConfig
    options:
      show_source: false

## AppConfig

::: universal_mcp.config.AppConfig
    options:
      show_source: false

## IntegrationConfig

::: universal_mcp.config.IntegrationConfig
    options:
      show_source: false

## StoreConfig

::: universal_mcp.config.StoreConfig
    options:
      show_source: false

## Usage Examples

### Complete JSON Configuration

```json
{
  "name": "My MCP Server",
  "description": "Production MCP server",
  "type": "local",
  "transport": "stdio",
  "store": {
    "type": "disk",
    "name": "universal-mcp-prod"
  },
  "apps": [
    {
      "name": "github",
      "integration": {
        "name": "GITHUB_TOKEN",
        "type": "api_key",
        "store": {
          "type": "disk"
        }
      }
    },
    {
      "name": "slack",
      "integration": {
        "name": "SLACK_BOT_TOKEN",
        "type": "api_key",
        "store": {
          "type": "environment"
        }
      }
    },
    {
      "name": "zenquotes",
      "integration": null
    }
  ]
}
```

### Loading Configuration

```python
from universal_mcp.config import ServerConfig

# From JSON file
config = ServerConfig.load_json_config("config.json")

# From dict
config = ServerConfig.model_validate({
    "store": {"type": "disk"},
    "apps": [...]
})

# Access fields
print(config.name)
print(config.store.type)
for app in config.apps:
    print(f"App: {app.name}")
```

### Validation

Pydantic validates configuration:

```python
from universal_mcp.config import ServerConfig
from pydantic import ValidationError

try:
    config = ServerConfig.load_json_config("invalid.json")
except ValidationError as e:
    print("Configuration errors:")
    for error in e.errors():
        print(f"  {error['loc']}: {error['msg']}")
```

Example validation errors:
```
Configuration errors:
  store.type: value is not a valid enumeration member
  apps.0.name: field required
```

## Configuration Examples

### Minimal Configuration

```json
{
  "store": {
    "type": "disk"
  },
  "apps": [
    {
      "name": "zenquotes"
    }
  ]
}
```

### Multi-Environment Configuration

```json
// config.prod.json
{
  "store": {
    "type": "keyring",
    "name": "myapp-prod"
  },
  "apps": [
    {
      "name": "github",
      "integration": {
        "name": "GITHUB_TOKEN",
        "type": "api_key"
      }
    }
  ]
}
```

```json
// config.dev.json
{
  "store": {
    "type": "memory"
  },
  "apps": [
    {
      "name": "github",
      "integration": {
        "name": "DEV_GITHUB_TOKEN",
        "type": "api_key",
        "store": {
          "type": "environment"
        }
      }
    }
  ]
}
```

## Programmatic Configuration

### Building Config in Code

```python
from universal_mcp.config import (
    ServerConfig,
    AppConfig,
    IntegrationConfig,
    StoreConfig
)

config = ServerConfig(
    store=StoreConfig(type="disk", name="my-app"),
    apps=[
        AppConfig(
            name="github",
            integration=IntegrationConfig(
                name="GITHUB_TOKEN",
                type="api_key"
            )
        )
    ]
)

# Use config
from universal_mcp.servers import LocalServer
server = LocalServer(config)
```

## Integration Configuration Types

### API Key Integration

```json
{
  "integration": {
    "name": "MY_API_KEY",
    "type": "api_key",
    "store": {
      "type": "disk"
    }
  }
}
```

## Store Configuration Types

### Disk Store (Default)

```json
{
  "store": {
    "type": "disk",
    "name": "my-app-name"
  }
}
```

Stores credentials in `~/.universal-mcp/store/` as JSON files.

### Keyring Store

```json
{
  "store": {
    "type": "keyring",
    "name": "my-app-name"
  }
}
```

Uses system secure storage (macOS Keychain, Windows Credential Manager, etc.).

### Environment Store

```json
{
  "store": {
    "type": "environment"
  }
}
```

Reads credentials from environment variables.

### Memory Store

```json
{
  "store": {
    "type": "memory"
  }
}
```

Transient storage, lost when server stops. Useful for testing.

## Validation Rules

### Required Fields

```python
# ServerConfig requires:
# - type (default: "local")
# - apps (list of AppConfig, optional)
# - store (StoreConfig, optional, defaults to disk)

# AppConfig requires:
# - name (str)

# IntegrationConfig requires:
# - name (str) - credential key name
# - type (str) - "api_key" or "basic_auth"
```

### Type Validation

```python
# Enums
store.type in ["disk", "keyring", "environment", "memory"]
integration.type in ["api_key", "basic_auth"]

# Ports
port: must be 1-65535

# Lists
apps: must be list of AppConfig
```

## Configuration Best Practices

### 1. Use Environment Store for Secrets in CI/CD

```json
{
  "integration": {
    "name": "API_KEY",
    "type": "api_key",
    "store": {
      "type": "environment"
    }
  }
}
```

### 2. Separate Dev/Prod Configs

```bash
config/
  config.dev.json    # Development settings
  config.prod.json   # Production settings
  config.test.json   # Test settings
```

### 3. Validate Before Deployment

```python
def validate_config(config_path):
    try:
        config = ServerConfig.load_json_config(config_path)
        print("Configuration valid")
        return True
    except Exception as e:
        print(f"Configuration invalid: {e}")
        return False

# In CI/CD pipeline
if not validate_config("config.prod.json"):
    exit(1)
```

## Related Documentation

- [Servers API](servers.md) - Using configuration with servers
- [Architecture: Server Initialization](../architecture/server-init.md) - How config is loaded
