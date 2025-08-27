from abc import ABC, abstractmethod
from typing import Any

from universal_mcp.types import ToolConfig, ToolFormat


class ToolRegistry(ABC):
    """Abstract base class for platform-specific functionality.

    This class abstracts away platform-specific operations like fetching apps,
    loading actions, and managing integrations. This allows the agents to
    work with different platforms without being tightly coupled to any specific one.

    The following methods are abstract and must be implemented by the subclass:
    - list_all_apps: Get list of available apps from the platform.
    - get_app_details: Get details of a specific app.
    - search_apps: Search for apps by a query.
    - list_tools: List all tools available on the platform, filter by app_id.
    - search_tools: Search for tools by a query.
    - export_tools: Export tools to required format.
    """

    @abstractmethod
    async def list_all_apps(self) -> list[dict[str, Any]]:
        """Get list of available apps from the platform.

        Returns:
            Return a list of apps with their details
        """
        pass

    @abstractmethod
    async def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app.

        Args:
            app_id: The ID of the app to get details for

        Returns:
            Dictionary containing app details
        """
        pass

    @abstractmethod
    async def search_apps(
        self,
        query: str,
        limit: int = 2,
    ) -> list[dict[str, Any]]:
        """Search for apps by a query."""
        pass

    @abstractmethod
    async def list_tools(
        self,
        app_id: str,
    ) -> list[dict[str, Any]]:
        """List all tools available on the platform, filter by app_id."""
        pass

    @abstractmethod
    async def search_tools(
        self,
        query: str,
        limit: int = 2,
    ) -> list[dict[str, Any]]:
        """Search for tools by a query."""
        pass

    @abstractmethod
    async def export_tools(
        self,
        tools: list[str] | ToolConfig,
        format: ToolFormat,
    ) -> str:
        """Export giventools to required format."""
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        pass
