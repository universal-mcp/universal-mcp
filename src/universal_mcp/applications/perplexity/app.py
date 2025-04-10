from typing import Any

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class PerplexityApp(APIApplication):

    def __init__(self, integration: Integration | None = None) -> None:

        super().__init__(name="perplexity", integration=integration)
        self.api_key: str | None = None
        self.base_url = "https://api.perplexity.ai"

    def _set_api_key(self):
        
        if self.api_key:
            return

        if not self.integration:
            raise ValueError("Integration is None. Cannot retrieve Perplexity API Key.")

        credentials = self.integration.get_credentials()
        if not credentials:
             raise ValueError(
                f"Failed to retrieve Perplexity API Key using integration '{self.integration.name}'. "
                f"Check store configuration (e.g., ensure the correct source like environment variable is set)."
             )
        
        if not isinstance(credentials, str) or not credentials.strip():
             raise ValueError(
                f"Invalid credential format received for Perplexity API Key via integration '{self.integration.name}'. "
                f"Expected a non-empty string API key."
            )
        self.api_key = credentials

    def _get_headers(self) -> dict[str, str]:
        self._set_api_key()
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def chat(self, query: str, model: str = "sonar", temperature: float = 1, system_prompt: str = "Be precise and concise.") -> dict[str, Any] | str:
        """
        Sends a query to a Perplexity Sonar online model and returns the response.

        This uses the chat completions endpoint, suitable for conversational queries
        and leveraging Perplexity's online capabilities.

        Args:
            query: The user's query or message.
            model: The specific Perplexity model to use (e.g., 'sonar-small-online', 'sonar-medium-online').
                   Defaults to 'sonar-small-online'.
            temperature: Sampling temperature for the response generation (e.g., 0.7).
            system_prompt: An optional system message to guide the model's behavior.

        Returns:
            A dictionary containing the full API response on success,
            or a string containing an error message on failure.
        """
        endpoint = f"{self.base_url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            # Add other parameters like max_tokens if needed
            # "max_tokens": 512,
        }

        response = self._post(endpoint, data=payload)
        return response.json()

    def list_tools(self) -> list[callable]:
        """
        Returns a list of methods exposed as tools for the MCP server.
        """
        return [
            self.chat,
        ]