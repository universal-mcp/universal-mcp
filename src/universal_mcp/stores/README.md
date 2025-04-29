# Universal MCP Stores

The stores module provides a flexible and secure way to manage credentials and sensitive data across different storage backends. It implements a common interface for storing, retrieving, and deleting sensitive information.

## Features

- Abstract base class defining a consistent interface for credential stores
- Multiple storage backend implementations:
  - In-memory store (temporary storage)
  - Environment variable store
  - System keyring store (secure credential storage)
- Exception handling for common error cases
- Type hints and comprehensive documentation

## Available Store Implementations

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
Leverages the system's secure credential storage facility. Provides the most secure option for storing sensitive data.

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

1. Use `KeyringStore` for production environments where security is a priority
2. Use `EnvironmentStore` for containerized or cloud environments
3. Use `MemoryStore` for testing or temporary storage only
4. Always handle `StoreError` and `KeyNotFoundError` exceptions appropriately

## Dependencies

- `keyring`: Required for the KeyringStore implementation
- `loguru`: Used for logging operations in the KeyringStore

## Contributing

New store implementations should inherit from `BaseStore` and implement all required abstract methods:
- `get(key: str) -> Any`
- `set(key: str, value: str) -> None`
- `delete(key: str) -> None`
