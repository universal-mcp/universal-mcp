from abc import ABC, abstractmethod
from typing import Any

from universal_mcp.tools.manager import ToolManager


class ToolRegistry(ABC):
    """Abstract base class for platform-specific functionality.

    This class abstracts away platform-specific operations like fetching apps,
    loading actions, and managing integrations. This allows the AutoAgent to
    work with different platforms without being tightly coupled to any specific one.
    """

    @abstractmethod
    def list_apps(self) -> list[dict[str, Any]]:
        """Get list of available apps from the platform.

        Returns:
            Return a list of apps with their details
        """
        pass

    @abstractmethod
    def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app.

        Args:
            app_id: The ID of the app to get details for

        Returns:
            Dictionary containing app details
        """
        pass

    @abstractmethod
    def load_tools(self, tools: list[str], tool_manager: ToolManager) -> None:
        """Load tools from the platform and register them as tools.

        Args:
            tools: The list of tools to load
        """
        pass

    @abstractmethod
    def search_tools(
        self,
        query: str,
    ) -> list[str]:
        """Retrieve a tool to use, given a search query."""
        pass
