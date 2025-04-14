from typing import Any, Literal

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration
from loguru import logger


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
        if not credentials or "apiKey" not in credentials:
            raise ValueError(
                f"Failed to retrieve Perplexity API Key using integration '{self.integration.name}'. "
            )
        api_key = (
            credentials.get("api_key")
            or credentials.get("API_KEY")
            or credentials.get("apiKey")
        )
        if not api_key:
            raise ValueError(
                f"Invalid credential format received for Perplexity API Key via integration '{self.integration.name}'. "
            )
        self.api_key = api_key

    def _get_headers(self) -> dict[str, str]:
        self._set_api_key()
        logger.info(f"Perplexity API Key: {self.api_key}")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def chat(
        self,
        query: str,
        model: Literal[
            "r1-1776",
            "sonar",
            "sonar-pro",
            "sonar-reasoning",
            "sonar-reasoning-pro",
            "sonar-deep-research",
        ] = "sonar",
        temperature: float = 1,
        system_prompt: str = "Be precise and concise.",
    ) -> dict[str, Any] | str:
        """
        Sends a query to a Perplexity Sonar online model and returns the response.

        This uses the chat completions endpoint, suitable for conversational queries
        and leveraging Perplexity's online capabilities.

        Args:
            query: The user's query or message.
            model: The specific Perplexity model to use (e.g., "r1-1776","sonar","sonar-pro","sonar-reasoning","sonar-reasoning-pro", "sonar-deep-research").Defaults to 'sonar'.
            temperature: Sampling temperature for the response generation (e.g., 0.7).
            system_prompt: An optional system message to guide the model's behavior.

        Returns:
            A dictionary containing 'content' (str) and 'citations' (list) on success, or a string containing an error message on failure.
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
            # "max_tokens": 512,
        }

        data = self._post(endpoint, data=payload)
        response = data.json()
        content = response["choices"][0]["message"]["content"]
        citations = response.get("citations", [])
        return {"content": content, "citations": citations}

    def list_tools(self):
        return [
            self.chat,
        ]
