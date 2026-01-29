# Stores API

Stores provide secure credential storage backends.

## BaseStore

::: universal_mcp.stores.store.BaseStore
    options:
      show_source: false

## MemoryStore

::: universal_mcp.stores.store.MemoryStore
    options:
      show_source: false

## EnvironmentStore

::: universal_mcp.stores.store.EnvironmentStore
    options:
      show_source: false

## KeyringStore

::: universal_mcp.stores.store.KeyringStore
    options:
      show_source: false

## Usage Examples

### MemoryStore (Testing)

```python
from universal_mcp.stores import MemoryStore

store = MemoryStore()

# Set value
store.set("api_key", "sk_test_123")

# Get value
api_key = store.get("api_key")
print(api_key)  # "sk_test_123"

# List keys
keys = store.list_keys()
print(keys)  # ["api_key"]

# Delete
store.delete("api_key")

# Clear all
store.clear()
```

### EnvironmentStore

```python
from universal_mcp.stores import EnvironmentStore
import os

store = EnvironmentStore()

# Set (writes to os.environ)
store.set("API_KEY", "sk_live_456")

# Get
api_key = store.get("API_KEY")
print(api_key)  # "sk_live_456"

# Also accessible via os.environ
print(os.environ["API_KEY"])  # "sk_live_456"

# List all env vars
keys = store.list_keys()
print("HOME" in keys)  # True
```

### KeyringStore (Production)

```python
from universal_mcp.stores import KeyringStore

# Create with service name
store = KeyringStore(service_name="my-app")

# Set secure credential
store.set("github_token", "ghp_abc123...")

# Get credential
# (requires OS authentication on first access)
token = store.get("github_token")

# List keys for this service
keys = store.list_keys()
print(keys)  # ["github_token"]

# Delete
store.delete("github_token")
```

### Store Factory Pattern

```python
from universal_mcp.stores import create_store

# Create from config
store = create_store({
    "type": "keyring",
    "service_name": "my-app"
})

# Or
store = create_store({"type": "memory"})

# Or
store = create_store({"type": "environment"})
```

## Comparison Matrix

| Feature | MemoryStore | EnvironmentStore | KeyringStore |
|---------|-------------|------------------|--------------|
| **Persistence** | No (lost on exit) | No (per-session) | Yes (OS keyring) |
| **Security** | Low | Medium | High |
| **Setup** | None | None | OS keyring |
| **Performance** | Fastest | Fast | Slower (OS calls) |
| **Cross-process** | No | Yes (same session) | Yes |
| **Best For** | Testing | CI/CD, containers | Production |

## Security Considerations

### MemoryStore

```python
# In-process only
store = MemoryStore()
store.set("secret", "sensitive_data")

# Lost on process exit
# Visible in memory dumps
# Not shared across processes
```

**Use for:** Unit tests, temporary data

### EnvironmentStore

```python
# Accessible in process environment
store = EnvironmentStore()
store.set("SECRET", "sensitive_data")

# Visible to:
# - Child processes
# - Process inspection tools (ps env)
# - Core dumps

import os
print(os.environ["SECRET"])  # Accessible
```

**Use for:** Containerized apps, CI/CD pipelines

### KeyringStore

```python
# OS-level encryption
store = KeyringStore(service_name="my-app")
store.set("secret", "sensitive_data")

# Encrypted at rest
# Requires OS authentication
# Shared across user's apps
```

**Use for:** Desktop applications, production servers

## Platform-Specific Behavior

### macOS

```python
store = KeyringStore(service_name="my-app")
store.set("key", "value")

# Stored in Keychain
# Accessible via Keychain Access.app
# Backed up with user's iCloud Keychain
```

### Windows

```python
store = KeyringStore(service_name="my-app")
store.set("key", "value")

# Stored in Windows Credential Manager
# Accessible via Control Panel → Credential Manager
# Backed up with user profile
```

### Linux

```python
store = KeyringStore(service_name="my-app")
store.set("key", "value")

# Uses Secret Service API (GNOME Keyring, KWallet)
# Or falls back to encrypted file
```

## Error Handling

### Key Not Found

```python
from universal_mcp.exceptions import KeyNotFoundError

try:
    value = store.get("nonexistent_key")
except KeyNotFoundError as e:
    print(f"Key not found: {e.key}")
    # Set default or prompt user
    store.set(e.key, "default_value")
```

### Keyring Access Denied

```python
try:
    store = KeyringStore(service_name="my-app")
    value = store.get("key")
except Exception as e:
    print(f"Keyring access failed: {e}")
    # Fall back to environment store
    store = EnvironmentStore()
```

## Complex Data Types

Stores handle JSON serialization automatically:

```python
store = KeyringStore(service_name="my-app")

# Store dict
store.set("config", {
    "api_url": "https://api.example.com",
    "timeout": 30,
    "retries": 3
})

# Retrieve dict
config = store.get("config")
print(config["api_url"])  # Works!

# Store list
store.set("tags", ["python", "mcp", "api"])
tags = store.get("tags")
```

## Migration Between Stores

```python
def migrate_store(old_store, new_store):
    """Migrate all keys from old store to new store."""
    for key in old_store.list_keys():
        try:
            value = old_store.get(key)
            new_store.set(key, value)
            print(f"Migrated: {key}")
        except Exception as e:
            print(f"Failed to migrate {key}: {e}")

# Example: Memory to Keyring
memory_store = MemoryStore()
memory_store.set("key1", "value1")
memory_store.set("key2", "value2")

keyring_store = KeyringStore(service_name="my-app")
migrate_store(memory_store, keyring_store)
```

## Testing

### Mock Store for Tests

```python
from unittest.mock import MagicMock

def create_mock_store():
    store = MagicMock()
    store._data = {}

    def mock_get(key):
        return store._data.get(key)

    def mock_set(key, value):
        store._data[key] = value

    store.get.side_effect = mock_get
    store.set.side_effect = mock_set
    return store

# Use in tests
store = create_mock_store()
```

### In-Memory Store for Integration Tests

```python
import pytest
from universal_mcp.stores import MemoryStore

@pytest.fixture
def store():
    """Provide clean store for each test."""
    return MemoryStore()

def test_integration_flow(store):
    integration = ApiKeyIntegration("test", store)
    store.set("API_KEY", "test_key")
    creds = integration.get_credentials()
    assert creds["api_key"] == "test_key"
```

## Best Practices

### 1. Choose Right Store for Environment

```python
# Development
if os.getenv("ENV") == "development":
    store = MemoryStore()

# Production
elif os.getenv("ENV") == "production":
    store = KeyringStore(service_name="my-app")

# CI/CD
elif os.getenv("CI"):
    store = EnvironmentStore()
```

### 2. Namespace Keys

```python
# Good - namespaced keys
store.set("github.api_key", "...")
store.set("github.oauth_token", "...")
store.set("slack.bot_token", "...")

# Bad - collision risk
store.set("api_key", "...")  # Which API?
store.set("token", "...")  # Which service?
```

### 3. Handle Missing Keys Gracefully

```python
def get_or_prompt(store, key):
    try:
        return store.get(key)
    except KeyNotFoundError:
        value = input(f"Please enter {key}: ")
        store.set(key, value)
        return value
```

### 4. Clear Sensitive Data

```python
# After temporary use
store.set("temp_token", "...")
# ... use token ...
store.delete("temp_token")  # Clean up

# Or clear all on logout
def logout(store):
    store.clear()
```

## Related Documentation

- [Architecture: Authentication Flow](../architecture/auth-flow.md) - How stores are used
- [Integrations API](integrations.md) - Integrations using stores
- [Configuration API](config.md) - Store configuration
