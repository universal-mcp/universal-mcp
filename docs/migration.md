# Migration Guide

This guide covers breaking changes and migration paths for upgrading Universal MCP.

## Migrating to v0.2.x (Single-User SDK Architecture)

Universal MCP v0.2.x introduces a significant architectural shift to a single-user SDK model. This version removes the AgentR platform integration and OAuth support in favor of simpler, local-first credential management.

### Key Changes

#### 1. AgentR Platform Removal

The AgentR platform integration has been removed. This includes:

- `AgentRServer` class removed
- `AgentRIntegration` class removed
- `type: "agentr"` server configuration no longer supported
- `type: "agentr"` integration configuration no longer supported
- `AGENTR_API_KEY` environment variable no longer used

**Migration:**

Before (v0.1.x):
```json
{
  "type": "agentr",
  "apps": []
}
```

After (v0.2.x):
```json
{
  "type": "local",
  "apps": [
    {
      "name": "github",
      "integration": {
        "name": "GITHUB_TOKEN",
        "type": "api_key",
        "store": { "type": "disk" }
      }
    }
  ]
}
```

#### 2. OAuth Integration Removal

OAuth-based authentication has been removed. Universal MCP now focuses on API key-based authentication, which is simpler and more appropriate for single-user SDK deployments.

**Migration:**

If you were using OAuth via AgentR:
1. Obtain a personal access token or API key from the service provider
2. Configure the integration as `type: "api_key"`
3. Store the token in your preferred store (disk, environment, keyring)

Example for GitHub:
```json
{
  "name": "github",
  "integration": {
    "name": "GITHUB_TOKEN",
    "type": "api_key",
    "store": { "type": "disk" }
  }
}
```

#### 3. DiskStore as Default

A new `DiskStore` has been added and is now the recommended default store type. It provides persistent file-based storage at `~/.universal-mcp/store`.

**Migration:**

Before (v0.1.x):
```json
{
  "store": {
    "type": "keyring"
  }
}
```

After (v0.2.x) - using new default:
```json
{
  "store": {
    "type": "disk"
  }
}
```

Note: `keyring`, `environment`, and `memory` stores are still supported.

#### 4. FastMCP Migration

The server implementation now uses FastMCP as its base. This provides better MCP protocol compliance and simplified server implementation.

**Impact:**
- Most users won't notice any change in behavior
- If you were extending `BaseServer`, review the new implementation

#### 5. CLI Changes

The playground command has been removed. Use the standard `run` command:

```bash
# Run server with configuration
universal_mcp run -c config.json
```

### Configuration Schema Changes

#### ServerConfig

| Field | v0.1.x | v0.2.x |
|-------|--------|--------|
| `type` | `"local"` \| `"agentr"` | `"local"` only |

#### IntegrationConfig

| Field | v0.1.x | v0.2.x |
|-------|--------|--------|
| `type` | `"api_key"` \| `"agentr"` \| `"oauth"` | `"api_key"` \| `"basic_auth"` |

#### StoreConfig

| Field | v0.1.x | v0.2.x |
|-------|--------|--------|
| `type` | `"memory"` \| `"environment"` \| `"keyring"` | `"disk"` \| `"memory"` \| `"environment"` \| `"keyring"` |

### Complete Migration Example

**Before (v0.1.x with AgentR):**
```json
{
  "name": "My MCP Server",
  "type": "agentr",
  "transport": "sse",
  "port": 8005
}
```

**After (v0.2.x):**
```json
{
  "name": "My MCP Server",
  "type": "local",
  "transport": "sse",
  "port": 8005,
  "store": {
    "type": "disk"
  },
  "apps": [
    {
      "name": "github",
      "integration": {
        "name": "GITHUB_TOKEN",
        "type": "api_key"
      }
    },
    {
      "name": "tavily",
      "integration": {
        "name": "TAVILY_API_KEY",
        "type": "api_key",
        "store": { "type": "environment" }
      }
    }
  ]
}
```

### Credential Migration

If you had credentials stored via AgentR, you'll need to:

1. Obtain API keys/tokens directly from each service provider
2. Store them using your preferred store:

**Using DiskStore (programmatic):**
```python
from universal_mcp.stores import DiskStore

store = DiskStore()
store.set("GITHUB_TOKEN_API_KEY", "your_github_token")
store.set("TAVILY_API_KEY", "your_tavily_key")
```

**Using environment variables:**
```bash
export GITHUB_TOKEN_API_KEY="your_github_token"
export TAVILY_API_KEY="your_tavily_key"
```

### Deprecation Timeline

- v0.2.x: AgentR and OAuth removed
- Future versions will continue with the single-user SDK architecture

### Getting Help

If you encounter issues during migration:
1. Check the [main documentation](index.md) for current usage patterns
2. Review the [stores documentation](stores.md) for credential storage options
3. Open an issue on GitHub for unresolved problems
