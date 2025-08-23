import os
from typing import Any

import httpx
from loguru import logger

from universal_mcp.exceptions import NotAuthorizedError


class AgentrClient:
    """Helper class for AgentR API operations.

    This class provides utility methods for interacting with the AgentR API,
    including authentication, authorization, and credential management.

    Args:
        api_key (str, optional): AgentR API key. If not provided, will look for AGENTR_API_KEY env var.
        base_url (str, optional): Base URL for AgentR API. Defaults to https://api.agentr.dev.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        base_url = base_url or os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        self.base_url = f"{base_url.rstrip('/')}/v1"
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and AGENTR_API_KEY not found in environment variables")
        self.client = httpx.Client(
            base_url=self.base_url, headers={"X-API-KEY": self.api_key}, timeout=30, follow_redirects=True
        )

    def get_credentials(self, app_id: str) -> dict[str, Any]:
        """Retrieves the credentials for a specific integration.

        This method fetches the necessary credentials for an application,
        such as API keys or OAuth tokens, required to interact with the
        service's API.

        Args:
            app_id: The unique identifier for the application (e.g., 'asana', 'google-drive').

        Returns:
            A dictionary containing the credentials data from the API response.

        Raises:
            NotAuthorizedError: If credentials are not found, often indicating
                that the user has not yet authorized the application.
            httpx.HTTPError: For other API-related errors, such as network
                issues or server-side problems.
        """
        response = self.client.get(
            "/credentials/",
            params={"app_id": app_id},
        )
        if response.status_code == 404:
            logger.warning(f"No credentials found for app '{app_id}'. Requesting authorization...")
            action_url = self.get_authorization_url(app_id)
            raise NotAuthorizedError(action_url)
        response.raise_for_status()
        return response.json()

    def get_authorization_url(self, app_id: str) -> str:
        """Generates an authorization URL for connecting an application.

        This URL should be presented to the user to grant the necessary
        permissions for the application to access their data.

        Args:
            app_id: The ID of the application to authorize.

        Returns:
            A message containing the authorization URL.

        Raises:
            httpx.HTTPError: If the API request to generate the URL fails.
        """
        response = self.client.post("/connections/authorize", json={"app_id": app_id})
        response.raise_for_status()
        url = response.json().get("authorize_url")
        return f"Please ask the user to visit the following url to authorize the application: {url}. Render the url in proper markdown format with a clickable link."

    def list_apps(self) -> list[dict[str, Any]]:
        """Fetches a list of all available applications from the AgentR API.

        Each application represents an integration with a third-party service.

        Returns:
            A list of dictionaries, where each dictionary represents an
            application's data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self.client.get("/apps/")
        response.raise_for_status()
        return response.json().get("items", [])

    def get_app(self, app_id: str) -> dict[str, Any]:
        """Retrieves the configuration for a specific application.

        This includes details such as the application's name, description,
        and other metadata.

        Args:
            app_id: The unique identifier for the application to fetch.

        Returns:
            A dictionary containing the application's configuration data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self.client.get(f"/apps/{app_id}")
        response.raise_for_status()
        return response.json()

    def list_tools(self) -> list[dict[str, Any]]:
        """Lists all available tools from the AgentR API.

        Tools are global and not tied to a specific application at this endpoint.

        Returns:
            A list of dictionaries, where each dictionary represents a tool's
            configuration.
        """
        response = self.client.get("/tools/")
        response.raise_for_status()
        return response.json().get("items", [])

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        """Fetches the configuration for a specific tool.

        Args:
            tool_id: The unique identifier for the tool to fetch.

        Returns:
            A dictionary containing the tool's configuration data.

        Raises:
            httpx.HTTPError: If the API request fails.
        """
        response = self.client.get(f"/tools/{tool_id}")
        response.raise_for_status()
        return response.json()
