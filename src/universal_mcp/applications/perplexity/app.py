from typing import Any, Literal

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class PerplexityApp(APIApplication):
    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="perplexity", integration=integration)
        self.base_url = "https://api.perplexity.ai"

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
        Initiates a chat completion request to generate AI responses using various models with customizable parameters.

        Args:
            query: The input text/prompt to send to the chat model
            model: The model to use for chat completion. Options include 'r1-1776', 'sonar', 'sonar-pro', 'sonar-reasoning', 'sonar-reasoning-pro', 'sonar-deep-research'. Defaults to 'sonar'
            temperature: Controls randomness in the model's output. Higher values make output more random, lower values more deterministic. Defaults to 1
            system_prompt: Initial system message to guide the model's behavior. Defaults to 'Be precise and concise.'

        Returns:
            A dictionary containing the generated content and citations, with keys 'content' (str) and 'citations' (list), or a string in some cases

        Raises:
            AuthenticationError: Raised when API authentication fails due to missing or invalid credentials
            HTTPError: Raised when the API request fails or returns an error status

        Tags:
            chat, generate, ai, completion, important
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
