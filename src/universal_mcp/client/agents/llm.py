from typing import Any

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionToolParam


class LLMClient:
    """Simplified LLM client for OpenAI with tool calling support."""

    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()
        logger.info(f"LLMClient initialized with model: {self.model}")

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        tools: list[ChatCompletionToolParam] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ChatCompletionMessage:
        """Generate response using OpenAI with optional tool calling."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message
