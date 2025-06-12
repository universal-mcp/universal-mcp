# agents/base.py
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel


class AgentType(Enum):
    REACT = "react"
    CODEACT = "codeact"
    SIMPLE = "simple"


class AgentResponse(BaseModel):
    thought: str | None = None
    action: str | None = None
    action_input: dict[str, Any] | None = None
    observation: str | None = None
    answer: str | None = None
    finished: bool = False


class BaseAgent(ABC):
    def __init__(self, name: str, instructions: str, model: str, debug: bool = False):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.conversation_history = []

    @abstractmethod
    def process_step(self, user_input: str, tool_manager) -> AgentResponse:
        pass

    def reset_conversation(self):
        self.conversation_history = []
