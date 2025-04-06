import os
from abc import ABC, abstractmethod

import keyring


class Store(ABC):
    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass


class MemoryStore:
    """
    Acts as credential store for the applications.
    Responsible for storing and retrieving credentials.
    Ideally should be a key value store
    """

    def __init__(self):
        self.data = {}

    def get(self, key: str):
        return self.data.get(key)

    def set(self, key: str, value: str):
        self.data[key] = value

    def delete(self, key: str):
        del self.data[key]


class EnvironmentStore(Store):
    """
    Store that uses environment variables to store credentials.
    """

    def __init__(self):
        pass

    def get(self, key: str):
        return {"api_key": os.getenv(key)}

    def set(self, key: str, value: str):
        os.environ[key] = value

    def delete(self, key: str):
        del os.environ[key]


class KeyringStore(Store):
    """
    Store that uses keyring to store credentials.
    """

    def __init__(self, app_name: str = "universal_mcp"):
        self.app_name = app_name

    def get(self, key: str):
        return keyring.get_password(self.app_name, key)

    def set(self, key: str, value: str):
        keyring.set_password(self.app_name, key, value)

    def delete(self, key: str):
        keyring.delete_password(self.app_name, key)
