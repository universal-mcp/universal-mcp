# Universal MCP Stores

The stores module provides a flexible and secure way to manage credentials and sensitive data across different storage backends. It implements a common interface for storing, retrieving, and deleting sensitive information.

## Features

- Abstract base class defining a consistent interface for credential stores
- Multiple storage backend implementations:
  - Disk store (persistent file-based storage) - **recommended default**
  - In-memory store (temporary storage)
  - Environment variable store
  - System keyring store (secure credential storage)
- Exception handling for common error cases
- Type hints and comprehensive documentation

## Available Store Implementations

### DiskStore (Recommended Default)
A file-based persistent store using JSON serialization. Each key is stored in a separate file with a hashed filename for filesystem safety. This is the recommended default for single-user deployments.

```python
from universal_mcp.stores import DiskStore

# Uses default path: ~/.universal-mcp/store
store = DiskStore()
store.set("api_key", "secret123")
value = store.get("api_key")  # Returns "secret123"

# Custom path
store = DiskStore(path="/custom/path", app_name="my_app")

# Additional methods
store.has("api_key")  # Returns True
store.list_keys()     # Returns ["api_key"]
store.clear()         # Removes all keys
```

### MemoryStore
A simple in-memory store that persists data only for the duration of program execution. Useful for testing or temporary storage.

```python
from universal_mcp.stores import MemoryStore

store = MemoryStore()
store.set("api_key", "secret123")
value = store.get("api_key")  # Returns "secret123"
```

### EnvironmentStore
Uses environment variables to store and retrieve credentials. Useful for containerized environments or CI/CD pipelines.

```python
from universal_mcp.stores import EnvironmentStore

store = EnvironmentStore()
store.set("API_KEY", "secret123")
value = store.get("API_KEY")  # Returns "secret123"
```

### KeyringStore
Leverages the system's secure credential storage facility (macOS Keychain, Windows Credential Manager, Linux Secret Service). Provides the most secure option for storing sensitive data.

```python
from universal_mcp.stores import KeyringStore

store = KeyringStore(app_name="my_app")
store.set("api_key", "secret123")
value = store.get("api_key")  # Returns "secret123"
```

## Error Handling

The module provides specific exception types for handling errors:

- `StoreError`: Base exception for all store-related errors
- `KeyNotFoundError`: Raised when a requested key is not found in the store

## Best Practices

1. Use `DiskStore` as the default for single-user local deployments (persistent, simple)
2. Use `KeyringStore` for production environments where security is a priority
3. Use `EnvironmentStore` for containerized or cloud environments
4. Use `MemoryStore` for testing or temporary storage only
5. Always handle `StoreError` and `KeyNotFoundError` exceptions appropriately

## Dependencies

- `keyring`: Required for the KeyringStore implementation
- `loguru`: Used for logging operations in the KeyringStore

## Contributing

New store implementations should inherit from `BaseStore` and implement all required abstract methods:
- `get(key: str) -> Any`
- `set(key: str, value: str) -> None`
- `delete(key: str) -> None`
