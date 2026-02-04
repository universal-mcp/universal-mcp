# OAuth Client API

OAuth 2.0 flow implementation with callback server and token storage.

## CallbackServer

::: universal_mcp.client.oauth.CallbackServer
    options:
      show_source: false

## TokenStore

::: universal_mcp.client.token_store.TokenStore
    options:
      show_source: false

## Usage Examples

### OAuth Flow with Callback Server

```python
from universal_mcp.client.oauth import CallbackServer
from universal_mcp.client.token_store import TokenStore

# Start callback server
callback = CallbackServer(port=8080)
callback.start()

# Build authorization URL
auth_url = (
    f"https://provider.com/oauth/authorize"
    f"?client_id={client_id}"
    f"&redirect_uri=http://localhost:8080/callback"
    f"&scope=read+write"
)

print(f"Visit: {auth_url}")

# Wait for callback (blocks until user authorizes)
code = callback.wait_for_code(timeout=300)

callback.stop()

# Exchange code for token
# ... token exchange logic ...
```

### Token Storage

```python
from universal_mcp.client.token_store import TokenStore

store = TokenStore()

# Store tokens
store.save_token("github", {
    "access_token": "gho_...",
    "refresh_token": "ghr_...",
    "expires_at": 1234567890
})

# Retrieve tokens
tokens = store.load_token("github")

# Check if token is expired
import time
if tokens["expires_at"] < time.time():
    # Token expired, refresh needed
    pass
```

## Related Documentation

- [Integrations API](integrations.md) - OAuth integration using these components
- [Architecture: Authentication Flow](../architecture/auth-flow.md) - Complete OAuth flow
