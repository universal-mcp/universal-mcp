from abc import ABC, abstractmethod
from typing import Any


class ToolRegistry(ABC):
    """Abstract base class for platform-specific functionality.

    This class abstracts away platform-specific operations like fetching apps,
    loading actions, and managing integrations. This allows the AutoAgent to
    work with different platforms without being tightly coupled to any specific one.
    """

    @abstractmethod
    async def list_apps(self) -> list[dict[str, Any]]:
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
    async def load_tools(self, tools: list[str]) -> None:
        """Load tools from the platform and register them as tools.

        Args:
            tools: The list of tools to load
        """
        pass
