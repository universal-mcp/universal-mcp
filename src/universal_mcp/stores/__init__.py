"""Storage adapters using py-key-value library.

This module provides a simplified interface to py-key-value stores,
supporting multiple backends (Memory, Disk, Keyring, etc).
"""

from key_value.aio.protocols.key_value import AsyncKeyValue
from key_value.aio.stores.disk import DiskStore
from key_value.aio.stores.keyring import KeyringStore
from key_value.aio.stores.memory import MemoryStore

# For backward compatibility with old code
BaseStore = AsyncKeyValue

__all__ = [
    "AsyncKeyValue",
    "BaseStore",
    "MemoryStore",
    "DiskStore",
    "KeyringStore",
]
