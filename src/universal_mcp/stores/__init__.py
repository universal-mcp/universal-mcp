from universal_mcp.config import StoreConfig
from universal_mcp.stores.store import (
    BaseStore,
    EnvironmentStore,
    KeyringStore,
    MemoryStore,
)


def store_from_config(store_config: StoreConfig):
    if store_config.type == "memory":
        return MemoryStore()
    elif store_config.type == "environment":
        return EnvironmentStore()
    elif store_config.type == "keyring":
        return KeyringStore(app_name=store_config.name)
    else:
        raise ValueError(f"Invalid store type: {store_config.type}")


__all__ = [BaseStore, MemoryStore, EnvironmentStore, KeyringStore]
