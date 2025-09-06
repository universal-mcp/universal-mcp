from dataclasses import dataclass, field

from .prompts import SYSTEM_PROMPT


@dataclass(kw_only=True)
class Context:
    """The context for the agent."""

    system_prompt: str = field(
        default=SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    model: str = field(
        default="anthropic/claude-4-sonnet-20250514",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    recursion_limit: int = field(
        default=10,
        metadata={
            "description": "The maximum number of times the agent can call itself recursively. "
            "This is to prevent infinite recursion."
        },
    )
