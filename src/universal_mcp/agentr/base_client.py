from abc import ABC, abstractmethod
from typing import Any

class BaseAgentrClient(ABC):
    """
    Abstract Base Class defining the contract for an Agentr client.
    
    This allows for different implementations (e.g., HTTP-based, direct DB)
    to be used interchangeably by the AgentrRegistry.
    """

    @abstractmethod
    def me(self):
        """Get the current user's profile."""
        pass

    @abstractmethod
    def get_credentials(self, app_id: str) -> dict[str, Any]:
        """Get credentials for an integration from the AgentR API.

        Args:
            app_id (str): The ID of the app (e.g., 'asana', 'google-drive').

        Returns:
            dict: Credentials data from API response.

        Raises:
            NotAuthorizedError: If credentials are not found (404 response).
            HTTPError: For other API errors.
        """
        pass
    
    @abstractmethod
    def get_authorization_url(self, app_id: str) -> str:
        """Get the authorization URL to connect an app.

        Args:
            app_id (str): The ID of the app to authorize.

        Returns:
            str: A message containing the authorization URL.

        Raises:
            HTTPError: If the API request fails.
        """
        pass

    @abstractmethod
    def list_all_apps(self):
        """Fetch available apps from AgentR API.

        Returns:
            List[Dict[str, Any]]: A list of application data dictionaries.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        pass

    @abstractmethod
    def list_my_apps(self):
        """Fetch user apps from AgentR API.

        Returns:
            List[Dict[str, Any]]: A list of user app data dictionaries.
        """
        pass

    @abstractmethod
    def list_my_connections(self):
        """Fetch user connections from AgentR API.

        Returns:
            List[Dict[str, Any]]: A list of user connection data dictionaries.
        """
        pass
        
    @abstractmethod
    def get_app_details(self, app_id: str):
        """Fetch a specific app from AgentR API.

        Args:
            app_id (str): ID of the app to fetch.

        Returns:
            dict: App configuration data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        pass

    @abstractmethod
    def list_all_tools(self, app_id: str | None = None):
        """List all available tools from the AgentR API.

        Note: In the backend, tools are globally listed and not tied to a
              specific app at this endpoint.

        Returns:
            List[Dict[str, Any]]: A list of tool configurations.
        """
        pass
    
    @abstractmethod
    def get_tool_details(self, tool_id: str):
        """Fetch a specific tool configuration from the AgentR API.

        Args:
            tool_id (str): ID of the tool to fetch.

        Returns:
            dict: Tool configuration data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        pass
    
    @abstractmethod
    def search_all_apps(self, query: str, limit: int = 2):
        """Search for apps from the AgentR API.

        Args:
            query (str): The query to search for.
            limit (int, optional): The number of apps to return. Defaults to 2.

        Returns:
            List[Dict[str, Any]]: A list of app data dictionaries.
        """
        pass
    
    @abstractmethod
    def search_all_tools(self, query: str, limit: int = 2, app_id: str | None = None):
        """Search for tools from the AgentR API.

        Args:
            query (str): The query to search for.
            limit (int, optional): The number of tools to return. Defaults to 2.
            app_id (str, optional): The ID of the app to search tools for.
        """
        pass