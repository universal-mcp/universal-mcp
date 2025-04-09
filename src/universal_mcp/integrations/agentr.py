import os

import httpx
from loguru import logger

from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations.integration import Integration


class AgentRIntegration(Integration):
    """Integration class for AgentR API authentication and authorization.

    This class handles API key authentication and OAuth authorization flow for AgentR services.

    Args:
        name (str): Name of the integration
        api_key (str, optional): AgentR API key. If not provided, will look for AGENTR_API_KEY env var
        **kwargs: Additional keyword arguments passed to parent Integration class

    Raises:
        ValueError: If no API key is provided or found in environment variables
    """

    def __init__(self, name: str, api_key: str = None, **kwargs):
        super().__init__(name, **kwargs)
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        if not self.api_key:
            logger.error(
                "API key for AgentR is missing. Please visit https://agentr.dev to create an API key, then set it as AGENTR_API_KEY environment variable."
            )
            raise ValueError("AgentR API key required - get one at https://agentr.dev")
        self.base_url = os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")

    def set_credentials(self, credentials: dict | None = None):
        """Set credentials for the integration.

        This method is not implemented for AgentR integration. Instead it redirects to the authorize flow.

        Args:
            credentials (dict | None, optional): Credentials dict (not used). Defaults to None.

        Returns:
            str: Authorization URL from authorize() method
        """
        return self.authorize()
        # raise NotImplementedError("AgentR Integration does not support setting credentials. Visit the authorize url to set credentials.")

    def get_credentials(self):
        """Get credentials for the integration from the AgentR API.

        Makes API request to retrieve stored credentials for this integration.

        Returns:
            dict: Credentials data from API response

        Raises:
            NotAuthorizedError: If credentials are not found (404 response)
            HTTPError: For other API errors
        """
        response = httpx.get(
            f"{self.base_url}/api/{self.name}/credentials/",
            headers={"accept": "application/json", "X-API-KEY": self.api_key},
        )
        if response.status_code == 404:
            action = self.authorize()
            raise NotAuthorizedError(action)
        response.raise_for_status()
        data = response.json()
        return data

    def authorize(self):
        """Get authorization URL for the integration.

        Makes API request to get OAuth authorization URL.

        Returns:
            str: Message containing authorization URL

        Raises:
            HTTPError: If API request fails
        """
        response = httpx.get(
            f"{self.base_url}/api/{self.name}/authorize/",
            headers={"X-API-KEY": self.api_key},
        )
        response.raise_for_status()
        url = response.json()

        return f"Please ask the user to visit the following url to authorize the application: {url}. Render the url in proper markdown format with a clickable link."
