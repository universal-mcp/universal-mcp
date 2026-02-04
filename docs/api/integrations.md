# Integrations API

Integrations handle authentication and credential management for applications.

## Integration (Base)

::: universal_mcp.integrations.integration.Integration
    options:
      show_source: false
      members:
        - __init__
        - authorize
        - authorize_async
        - get_credentials
        - get_credentials_async

## ApiKeyIntegration

::: universal_mcp.integrations.integration.ApiKeyIntegration
    options:
      show_source: false

## OAuthIntegration

::: universal_mcp.integrations.integration.OAuthIntegration
    options:
      show_source: false

## IntegrationFactory

::: universal_mcp.integrations.integration.IntegrationFactory
    options:
      show_source: false

## Usage Examples

### API Key Integration

```python
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import KeyringStore

# Create store
store = KeyringStore(service_name="my-app")

# Create integration
integration = ApiKeyIntegration(
    name="api_key",
    store=store,
    api_key_name="MY_API_KEY"
)

# First time: authorize (prompts user to set key)
print(integration.authorize())
# Output: "Please set MY_API_KEY environment variable or in keyring"

# After setting key in keyring:
# store.set("MY_API_KEY", "sk_live_...")

# Get credentials
creds = integration.get_credentials()
print(creds)
# Output: {"api_key": "sk_live_..."}
```

### Custom Header Format

```python
integration = ApiKeyIntegration(
    name="api_key",
    store=store,
    api_key_name="BEARER_TOKEN",
    headers={"Authorization": "Bearer {api_key}"}
)

# When used in application:
headers = integration.get_credentials()
# Returns: {"Authorization": "Bearer sk_live_..."}
```

### OAuth 2.0 Integration

```python
from universal_mcp.integrations import OAuthIntegration
from universal_mcp.stores import KeyringStore

store = KeyringStore(service_name="my-app")

integration = OAuthIntegration(
    name="github_oauth",
    store=store,
    client_id="Iv1.abc123...",
    client_secret="secret_xyz...",
    auth_url="https://github.com/login/oauth/authorize",
    token_url="https://github.com/login/oauth/access_token",
    scopes=["repo", "user"],
    callback_port=8080
)

# First time: authorize
auth_url = integration.authorize()
print(f"Please visit: {auth_url}")
# Opens browser, user authorizes, callback receives code
# Tokens automatically stored in keyring

# Subsequent calls: get credentials
creds = integration.get_credentials()
print(creds)
# Output: {
#   "access_token": "gho_...",
#   "refresh_token": "ghr_...",
#   "expires_at": 1234567890
# }

# Token automatically refreshed when expired
```

### OAuth Token Refresh

```python
# Manual refresh (usually automatic)
integration.refresh_token()

# Check if token is expired
import time
creds = integration.get_credentials()
if creds.get("expires_at", 0) < time.time():
    integration.refresh_token()
    creds = integration.get_credentials()
```

### Integration Factory

```python
from universal_mcp.integrations import IntegrationFactory
from universal_mcp.stores import KeyringStore

store = KeyringStore()

# Create API key integration
factory = IntegrationFactory()
integration = factory.create_integration(
    integration_type="api_key",
    name="my_api",
    store=store,
    api_key_name="API_KEY"
)

# Create OAuth integration
integration = factory.create_integration(
    integration_type="oauth",
    name="oauth_app",
    store=store,
    client_id="...",
    client_secret="...",
    auth_url="https://...",
    token_url="https://...",
    scopes=["read"]
)
```

## Integration Factories

### Creating from Configuration

```python
from universal_mcp.integrations import create_integration
from universal_mcp.stores import KeyringStore

store = KeyringStore()

# API Key
integration = create_integration(
    config={
        "type": "api_key",
        "name": "my_api",
        "api_key_name": "API_KEY"
    },
    store=store
)

# OAuth
integration = create_integration(
    config={
        "type": "oauth",
        "name": "oauth_app",
        "client_id": "...",
        "client_secret": "...",
        "auth_url": "https://...",
        "token_url": "https://...",
        "scopes": ["read", "write"]
    },
    store=store
)
```

## Async Support

All integrations support async operations:

```python
# Async authorize
auth_result = await integration.authorize_async()

# Async get credentials
creds = await integration.get_credentials_async()
```

## Error Handling

```python
from universal_mcp.exceptions import NotAuthorizedError, KeyNotFoundError

try:
    creds = integration.get_credentials()
except NotAuthorizedError:
    # No credentials found
    print("Please authorize first:")
    print(integration.authorize())
except KeyNotFoundError as e:
    # Specific key missing
    print(f"Missing key: {e.key}")
```

## Best Practices

### 1. Use KeyringStore for Production

```python
# Good - secure storage
store = KeyringStore(service_name="my-app")

# Avoid - credentials lost on restart
store = MemoryStore()
```

### 2. Handle Authorization Errors

```python
def ensure_authorized(integration):
    try:
        return integration.get_credentials()
    except NotAuthorizedError:
        print("Not authorized. Starting auth flow...")
        print(integration.authorize())
        return integration.get_credentials()
```

### 3. Use Environment Variables for Client Secrets

```python
import os

integration = OAuthIntegration(
    name="oauth",
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],  # Never hardcode!
    # ...
)
```

### 4. Scope Minimization

```python
# Good - minimal scopes
scopes=["repo:status", "user:email"]

# Bad - excessive permissions
scopes=["repo", "admin:org", "delete:packages"]
```

## Related Documentation

- [Architecture: Authentication Flow](../architecture/auth-flow.md) - Detailed auth flows
- [Applications API](applications.md) - Using integrations in apps
- [Stores API](stores.md) - Storage backend options
