"""Store module - exposes py-key-value stores directly."""

from pathlib import Path

from key_value.aio.stores.disk import DiskStore
from key_value.aio.stores.keyring import KeyringStore
from key_value.aio.stores.memory import MemoryStore
from key_value.aio.stores.base import BaseStore
from key_value.aio.stores.filetree import FileTreeStore


def create_store(
    store_type: str = "disk",
    directory: Path | str | None = None,
    service_name: str = "universal_mcp",
):
    """Create a store instance with sensible defaults.

    Args:
        store_type: Type of store ("disk", "memory", "keyring")
        directory: Directory for disk store (defaults to ~/.universal_mcp/store)
        service_name: Service name for keyring store

    Returns:
        Configured py-key-value store instance

    Raises:
        ValueError: If store_type is not supported

    Examples:
        >>> store = create_store()  # Default: DiskStore
        >>> store = create_store("memory")  # Fast in-memory
        >>> store = create_store("keyring")  # Secure OS keychain
    """
    store_type = store_type.lower()

    if store_type == "disk" or store_type == "file":
        if directory is None:
            directory = Path.home() / ".universal_mcp" / "store"
        Path(directory).mkdir(parents=True, exist_ok=True)
        if store_type == "file":
            return FileTreeStore(data_directory=directory)
        return DiskStore(directory=str(directory))
    elif store_type == "memory":
        return MemoryStore()

    elif store_type == "keyring":
        return KeyringStore(service_name=service_name)

    else:
        raise ValueError(f"Unsupported store type: {store_type}. Choose from: disk, memory, keyring")


__all__ = [
    "BaseStore",
    "DiskStore",
    "MemoryStore",
    "KeyringStore",
    "create_store",
]
