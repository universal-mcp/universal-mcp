# src/universal_mcp/agents/base.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Union, Dict, Any

class Agent(ABC):
    """Abstract base class for all agents."""

    @abstractmethod
    async def stream_response(
        self,
        user_message: str,
        thread_id: str,
        **kwargs: Any
    ) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """
        Process a user message and stream back responses.

        Args:
            user_message: The message from the user.
            thread_id: The ID for the current conversation thread.
            **kwargs: Additional arguments that specific agents might need,
                      e.g., an MCP client instance, or specific configuration.

        Yields:
            Union[str, Dict[str, Any]]: Tokens (str) or structured messages/events (dict).
        """
        # This is an abstract method, so it should not have a concrete implementation.
        # The 'yield' here is just to make Python recognize it as an async generator.
        # A subclass will actually implement the logic.
        if False: # pragma: no cover
            yield {} # type: ignore
