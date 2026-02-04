# Integrations

This package provides integration classes for handling authentication and authorization with external services.

## Overview

An Integration defines how an application authenticates and authorizes with a service provider. The base `Integration` class provides an interface that all integrations must implement.

Universal MCP is designed as a single-user SDK, focusing on simple API key-based authentication with flexible credential storage.

## Supported Integrations

### API Key Integration
The `ApiKeyIntegration` class provides API key-based authentication. API keys can be stored in any supported store backend (disk, environment, keyring, or memory).

```python
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import DiskStore

# Create integration with disk-based storage
store = DiskStore()
integration = ApiKeyIntegration("GITHUB_TOKEN", store=store)

# Set credentials
integration.api_key = "your_api_key_here"

# Get credentials
credentials = integration.get_credentials()  # Returns {"api_key": "your_api_key_here"}
```

## Usage

Each integration implements three key methods:

- `authorize()` - Returns instructions for the authorization process
- `get_credentials()` - Retrieves stored credentials
- `set_credentials()` - Stores new credentials

### Configuration Example

In your server configuration:

```json
{
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
    }
  ]
}
```

### Store Options

Integrations can use any of the available store backends:

- `disk` - Persistent file-based storage (recommended default)
- `environment` - Environment variables
- `keyring` - System secure storage
- `memory` - Transient in-memory storage

See the [Stores documentation](stores.md) for more details on each store type.
