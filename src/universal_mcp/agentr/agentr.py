import os

from universal_mcp.tools import Tool, ToolFormat, ToolManager

from .client import AgentrClient
from .registry import AgentrRegistry


class Agentr:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        registry: AgentrRegistry | None = None,
        format: ToolFormat | None = None,
        manager: ToolManager | None = None,
    ):
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        self.base_url = base_url or os.getenv("AGENTR_BASE_URL")
        self.client = AgentrClient(api_key=self.api_key, base_url=self.base_url)
        self.registry = registry or AgentrRegistry(client=self.client)
        self.format = format or ToolFormat.NATIVE
        self.manager = manager or ToolManager()

    def load_tools(self, tool_names: list[str]) -> None:
        self.registry.load_tools(tool_names, self.manager)
        return

    def list_tools(self, format: ToolFormat | None = None) -> list[Tool]:
        return self.manager.list_tools(format=format or self.format)
