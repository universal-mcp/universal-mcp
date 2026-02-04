from universal_mcp.config import StoreConfig
from universal_mcp.stores.base import BaseStore
from universal_mcp.stores.environment import EnvironmentStore
from universal_mcp.stores.file import FileStore
from universal_mcp.stores.keyring import KeyringStore
from universal_mcp.stores.memory import MemoryStore
from universal_mcp.stores.postgres import PostgresStore
from universal_mcp.stores.sqlite import SQLiteStore


def store_from_config(store_config: StoreConfig):
    """Create a store instance from a configuration object.

    Args:
        store_config (StoreConfig): Configuration object specifying the store type and parameters.

    Returns:
        BaseStore: An instance of the specified store type.

    Raises:
        ValueError: If the store type is invalid or unsupported.
    """
    if store_config.type == "memory":
        return MemoryStore()
    elif store_config.type == "environment":
        return EnvironmentStore()
    elif store_config.type == "keyring":
        return KeyringStore(app_name=store_config.name)
    elif store_config.type == "file":
        # Use default path or custom path if provided in config
        return FileStore()
    elif store_config.type == "sqlite":
        # Use default path or custom path if provided in config
        return SQLiteStore()
    elif store_config.type == "postgres":
        # Requires connection_string or connection_params in config
        raise ValueError("PostgresStore requires connection parameters. Use PostgresStore directly.")
    else:
        raise ValueError(f"Invalid store type: {store_config.type}")


__all__ = [
    "BaseStore",
    "MemoryStore",
    "EnvironmentStore",
    "KeyringStore",
    "FileStore",
    "SQLiteStore",
    "PostgresStore",
    "store_from_config",
]
