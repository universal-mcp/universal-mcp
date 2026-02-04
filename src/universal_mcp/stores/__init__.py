from universal_mcp.config import StoreConfig
from universal_mcp.stores.store import (
    BaseStore,
    DiskStore,
    EnvironmentStore,
    KeyringStore,
    MemoryStore,
)


def store_from_config(store_config: StoreConfig):
    if store_config.type == "disk":
        return DiskStore(path=store_config.path, app_name=store_config.name)
    elif store_config.type == "memory":
        return MemoryStore()
    elif store_config.type == "environment":
        return EnvironmentStore()
    elif store_config.type == "keyring":
        return KeyringStore(app_name=store_config.name)
    else:
        raise ValueError(f"Invalid store type: {store_config.type}")


__all__ = [BaseStore, DiskStore, MemoryStore, EnvironmentStore, KeyringStore]
