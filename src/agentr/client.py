import os
from typing import List, Optional

import httpx
from loguru import logger

from universal_mcp.config import AppConfig
from universal_mcp.exceptions import NotAuthorizedError


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

    def get_credentials(self, app_id: str, integration_id: Optional[str] = None) -> dict:
        """Get credentials for an integration from the AgentR API.

        Args:
            app_id (str): The ID of the app to get credentials for.
            integration_id (str, optional): The specific integration ID. If not provided, the default will be used.

        Returns:
            dict: Credentials data from API response

        Raises:
            NotAuthorizedError: If credentials are not found (404 response)
            HTTPError: For other API errors
        """
        params = {"app_id": app_id}
        if integration_id:
            params["integration_id"] = integration_id

        response = self.client.get("/v1/credentials/", params=params)

        if response.status_code == 404:
            logger.warning(f"No credentials found for app '{app_id}'. Requesting authorization...")
            auth_url_message = self.get_authorization_url(app_id, integration_id)
            raise NotAuthorizedError(auth_url_message)
        response.raise_for_status()
        return response.json()

    def get_authorization_url(self, app_id: str, integration_id: Optional[str] = None) -> str:
        """Get authorization URL for an integration.

        Args:
            app_id (str): The ID of the app to get the authorization URL for.
            integration_id (str, optional): The specific integration ID. If not provided, the default will be used.

        Returns:
            str: Message containing authorization URL

        Raises:
            HTTPError: If API request fails
        """
        payload = {"app_id": app_id}
        if integration_id:
            payload["integration_id"] = integration_id

        response = self.client.post("/v1/connections/authorize", json=payload)
        response.raise_for_status()
        url = response.json().get("authorize_url")
        return f"Please ask the user to visit the following url to authorize the application: {url}. Render the url in proper markdown format with a clickable link."

    def list_apps(self, search: Optional[str] = None) -> list[AppConfig]:
        """Fetch available apps from AgentR API.

        Args:
            search (str, optional): Perform a semantic search on app names and descriptions.

        Returns:
            List of application configurations

        Raises:
            httpx.HTTPError: If API request fails
        """
        params = {}
        if search:
            params["search"] = search
        response = self.client.get("/v1/apps/", params=params)
        response.raise_for_status()
        data = response.json()
        return [AppConfig.model_validate(app) for app in data]

    def get_app(self, app_id: str) -> dict:
        """Fetch a specific app from AgentR API.

        Args:
            app_id (str): ID of the app to fetch

        Returns:
            dict: App configuration data

        Raises:
            httpx.HTTPError: If API request fails
        """
        response = self.client.get(f"/v1/apps/{app_id}")
        response.raise_for_status()
        return response.json()

    def list_tools(self, search: Optional[str] = None) -> list:
        """List all tools from AgentR API.

        Args:
            search (str, optional): Perform a semantic search on tool names and descriptions.

        Returns:
            List of tools
        """
        params = {}
        if search:
            params["search"] = search
        response = self.client.get("/v1/tools/", params=params)
        response.raise_for_status()
        return response.json()

    def get_tool(self, tool_id: str) -> dict:
        """
        Retrieve a single tool by its unique ID.

        Args:
            tool_id (str): The ID of the tool to retrieve.

        Returns:
            dict: The tool data.
        """
        response = self.client.get(f"/v1/tools/{tool_id}")
        response.raise_for_status()
        return response.json()
