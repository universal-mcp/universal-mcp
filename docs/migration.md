# Migration Guide

This guide covers breaking changes and migration paths for upgrading Universal MCP.

## v2.0 Architecture

Universal MCP v2.0 is a single-user SDK focused on local-first credential management with clean separation between integrations (configuration templates) and connections (per-user credentials).

### Key Features

- **Integration/Connection Separation**: Clear separation between integration configuration (how to connect) and user credentials (what to authenticate with)
- **Multi-user Ready**: Support for multiple users with different credentials per integration
- **OAuth Support**: Proper OAuth 2.0 implementation with client credentials separate from user tokens
- **Local-First**: DiskStore as default for persistent credential storage

### Configuration Schema

#### ServerConfig

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"local"` | Server type (local only) |
| `transport` | `"stdio"` \| `"sse"` \| `"streamable-http"` | Communication protocol |
| `store` | `StoreConfig` | Default credential store |
| `apps` | `AppConfig[]` | Applications to load |

#### IntegrationConfig

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Integration name (e.g., "GITHUB_TOKEN") |
| `type` | `"api_key"` \| `"oauth2"` \| `"basic_auth"` | Authentication type |
| `store` | `StoreConfig` | Credential store (overrides server default) |

For OAuth integrations, additional fields:
- `client_id`: OAuth client ID
- `client_secret`: OAuth client secret
- `auth_url`: Authorization endpoint
- `token_url`: Token endpoint
- `scopes`: OAuth scopes

#### StoreConfig

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"disk"` \| `"memory"` \| `"environment"` \| `"keyring"` | Storage backend |
| `path` | `string` | Path for disk store (defaults to `~/.universal-mcp/store`) |

### Example Configuration

```json
{
  "name": "My MCP Server",
  "type": "local",
  "transport": "stdio",
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
      "name": "google",
      "integration": {
        "name": "GOOGLE_OAUTH",
        "type": "oauth2",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/calendar"]
      }
    }
  ]
}
```

### Credential Storage

**Programmatic (DiskStore):**
```python
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import DiskStore

store = DiskStore()
integration = ApiKeyIntegration("GITHUB_TOKEN", store=store)
integration.api_key = "ghp_your_github_token"
```

**Environment Variables:**
```bash
export GITHUB_TOKEN_API_KEY="ghp_your_github_token"
export TAVILY_API_KEY="tvly_your_tavily_key"
```

**Multi-User (v2.0):**
```python
# Create connections for different users
alice_conn = integration.create_connection(user_id="alice")
alice_conn.set_credentials({"api_key": "alice_key"})

bob_conn = integration.create_connection(user_id="bob")
bob_conn.set_credentials({"api_key": "bob_key"})
```

### Getting Help

If you encounter issues during migration:
1. Check the [main documentation](index.md) for current usage patterns
2. Review the [stores documentation](stores.md) for credential storage options
3. Open an issue on GitHub for unresolved problems
