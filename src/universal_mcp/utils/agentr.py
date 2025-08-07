import os

import httpx
from loguru import logger

from universal_mcp.applications import app_from_slug
from universal_mcp.config import AppConfig
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations.integration import Integration
from universal_mcp.tools.manager import ToolManager, _get_app_and_tool_name
from universal_mcp.tools.registry import ToolRegistry


class AgentrClient:
    """Helper class for AgentR API operations.

    This class provides utility methods for interacting with the AgentR API,
    including authentication, authorization, and credential management.

    Args:
        api_key (str, optional): AgentR API key. If not provided, will look for AGENTR_API_KEY env var
        base_url (str, optional): Base URL for AgentR API. Defaults to https://api.agentr.dev
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        base_url = base_url or os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and AGENTR_API_KEY not found in environment variables")
        self.client = httpx.Client(
            base_url=self.base_url, headers={"X-API-KEY": self.api_key}, timeout=30, follow_redirects=True
        )

    def get_credentials(self, integration_name: str) -> dict:
        """Get credentials for an integration from the AgentR API.

        Args:
            integration_name (str): Name of the integration to get credentials for

        Returns:
            dict: Credentials data from API response

        Raises:
            NotAuthorizedError: If credentials are not found (404 response)
            HTTPError: For other API errors
        """
        response = self.client.get(
            f"/api/{integration_name}/credentials/",
        )
        if response.status_code == 404:
            logger.warning(f"No credentials found for {integration_name}. Requesting authorization...")
            action = self.get_authorization_url(integration_name)
            raise NotAuthorizedError(action)
        response.raise_for_status()
        return response.json()

    def get_authorization_url(self, integration_name: str) -> str:
        """Get authorization URL for an integration.

        Args:
            integration_name (str): Name of the integration to get authorization URL for

        Returns:
            str: Message containing authorization URL

        Raises:
            HTTPError: If API request fails
        """
        response = self.client.get(f"/api/{integration_name}/authorize/")
        response.raise_for_status()
        url = response.json()
        return f"Please ask the user to visit the following url to authorize the application: {url}. Render the url in proper markdown format with a clickable link."

    def fetch_apps(self) -> list[AppConfig]:
        """Fetch available apps from AgentR API.

        Returns:
            List of application configurations

        Raises:
            httpx.HTTPError: If API request fails
        """
        response = self.client.get("/api/apps/")
        response.raise_for_status()
        data = response.json()
        return [AppConfig.model_validate(app) for app in data]

    def fetch_app(self, app_id: str) -> dict:
        """Fetch a specific app from AgentR API.

        Args:
            app_id (str): ID of the app to fetch

        Returns:
            dict: App configuration data

        Raises:
            httpx.HTTPError: If API request fails
        """
        response = self.client.get(f"/apps/{app_id}/")
        response.raise_for_status()
        return response.json()

    def list_all_apps(self) -> list:
        """List all apps from AgentR API.

        Returns:
            List of app names
        """
        response = self.client.get("/apps/")
        response.raise_for_status()
        return response.json()

    def list_actions(self, app_id: str):
        """List actions for an app.

        Args:
            app_id (str): ID of the app to list actions for

        Returns:
            List of action configurations
        """

        response = self.client.get(f"/apps/{app_id}/actions/")
        response.raise_for_status()
        return response.json()


class AgentRIntegration(Integration):
    """Manages authentication and authorization via the AgentR platform.

    This integration uses an `AgentrClient` to interact with the AgentR API
    for operations like retrieving authorization URLs and fetching stored
    credentials. It simplifies integration with services supported by AgentR.

    Attributes:
        name (str): Name of the integration (e.g., "github", "google").
        store (BaseStore): Store, typically not used directly by this class
                       as AgentR manages the primary credential storage.
        client (AgentrClient): Client for communicating with the AgentR API.
        _credentials (dict | None): Cached credentials.
    """

    def __init__(
        self,
        name: str,
        client: AgentrClient | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        """Initializes the AgentRIntegration.

        Args:
            name (str): The name of the service integration as configured on
                        the AgentR platform (e.g., "github").
            client (AgentrClient | None, optional): The AgentR client. If not provided,
                                                   a new `AgentrClient` will be created.
            api_key (str | None, optional): API key for AgentR. If not provided,
                                           will be loaded from environment variables.
            base_url (str | None, optional): Base URL for AgentR API. If not provided,
                                            will be loaded from environment variables.
            **kwargs: Additional arguments passed to the parent `Integration`.
        """
        super().__init__(name, **kwargs)
        self.client = client or AgentrClient(api_key=api_key, base_url=base_url)
        self._credentials = None

    def set_credentials(self, credentials: dict[str, any] | None = None) -> str:
        """Not used for direct credential setting; initiates authorization instead.

        For AgentR integrations, credentials are set via the AgentR platform's
        OAuth flow. This method effectively redirects to the `authorize` flow.

        Args:
            credentials (dict | None, optional): Not used by this implementation.

        Returns:
            str: The authorization URL or message from the `authorize()` method.
        """
        raise NotImplementedError("AgentR integrations do not support direct credential setting")

    @property
    def credentials(self):
        """Retrieves credentials from the AgentR API, with caching.

        If credentials are not cached locally (in `_credentials`), this property
        fetches them from the AgentR platform using `self.client.get_credentials`.

        Returns:
            dict: The credentials dictionary obtained from AgentR.

        Raises:
            NotAuthorizedError: If credentials are not found (e.g., 404 from AgentR).
            httpx.HTTPStatusError: For other API errors from AgentR.
        """
        if self._credentials is not None:
            return self._credentials
        self._credentials = self.client.get_credentials(self.name)
        return self._credentials

    def get_credentials(self):
        """Retrieves credentials from the AgentR API. Alias for `credentials` property.

        Returns:
            dict: The credentials dictionary obtained from AgentR.

        Raises:
            NotAuthorizedError: If credentials are not found.
            httpx.HTTPStatusError: For other API errors.
        """
        return self.credentials

    def authorize(self) -> str:
        """Retrieves the authorization URL from the AgentR platform.

        This URL should be presented to the user to initiate the OAuth flow
        managed by AgentR for the service associated with `self.name`.

        Returns:
            str: The authorization URL.

        Raises:
            httpx.HTTPStatusError: If the API request to AgentR fails.
        """
        return self.client.get_authorization_url(self.name)


class AgentrRegistry(ToolRegistry):
    """Platform manager implementation for AgentR platform."""

    def __init__(self, client: AgentrClient | None = None):
        """Initialize the AgentR platform manager."""

        self.client = client or AgentrClient()
        logger.debug("AgentrRegistry initialized successfully")

    async def list_apps(self) -> list[dict[str, any]]:
        """Get list of available apps from AgentR.

        Returns:
            List of app dictionaries with id, name, description, and available fields
        """
        try:
            all_apps = await self.client.list_all_apps()
            available_apps = [
                {"id": app["id"], "name": app["name"], "description": app.get("description", "")}
                for app in all_apps
                if app.get("available", False)
            ]
            logger.info(f"Found {len(available_apps)} available apps from AgentR")
            return available_apps
        except Exception as e:
            logger.error(f"Error fetching apps from AgentR: {e}")
            return []

    async def get_app_details(self, app_id: str) -> dict[str, any]:
        """Get detailed information about a specific app from AgentR.

        Args:
            app_id: The ID of the app to get details for

        Returns:
            Dictionary containing app details
        """
        try:
            app_info = await self.client.fetch_app(app_id)
            return {
                "id": app_info.get("id"),
                "name": app_info.get("name"),
                "description": app_info.get("description"),
                "category": app_info.get("category"),
                "available": app_info.get("available", True),
            }
        except Exception as e:
            logger.error(f"Error getting details for app {app_id}: {e}")
            return {
                "id": app_id,
                "name": app_id,
                "description": "Error loading details",
                "category": "Unknown",
                "available": True,
            }

    def load_tools(self, tools: list[str], tool_manager: ToolManager) -> None:
        """Load tools from AgentR and register them as tools.

        Args:
            tools: The list of tools to load ( prefixed with app name )
            tool_manager: The tool manager to register tools with
        """
        logger.info(f"Loading all actions for app: {tools}")
        # Group all tools by app_name, tools
        tools_by_app = {}
        for tool_name in tools:
            app_name, _ = _get_app_and_tool_name(tool_name)
            if app_name not in tools_by_app:
                tools_by_app[app_name] = []
            tools_by_app[app_name].append(tool_name)

        for app_name, tool_names in tools_by_app.items():
            app = app_from_slug(app_name)
            integration = AgentRIntegration(name=app_name)
            app_instance = app(integration=integration)
            tool_manager.register_tools_from_app(app_instance, tool_names=tool_names)
        return tool_manager
