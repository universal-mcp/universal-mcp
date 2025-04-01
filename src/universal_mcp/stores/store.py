import os
from abc import ABC, abstractmethod


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

class RedisStore(Store):
    """
    Store that uses a redis database to store credentials.
    """
    def __init__(self, host: str, port: int, db: int):
        import redis
        self.host = host
        self.port = port
        self.db = db
        self.redis = redis.Redis(host=self.host, port=self.port, db=self.db)

    def get(self, key: str):
        return self.redis.get(key)

    def set(self, key: str, value: str):
        self.redis.set(key, value)

    def delete(self, key: str):
        self.redis.delete(key)