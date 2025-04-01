from pydantic import BaseModel
from typing import Literal

class StoreConfig(BaseModel):
    type: Literal["memory", "environment"]

class IntegrationConfig(BaseModel):
    name: str
    type: Literal["api_key", "agentr"]
    credentials: dict | None = None
    store: StoreConfig | None = None

class AppConfig(BaseModel):
    name: str
    integration: IntegrationConfig | None = None
