"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated


@dataclass(kw_only=True)
class InputState(TypedDict):
    """Input state for the agent workflow."""
    target_script_path: str = field(default="")


@dataclass(kw_only=True)
class OutputState(TypedDict):
    """Output state for the agent workflow."""
    updated_script: str = field(default="")
    functions_processed: int = field(default=0)


@dataclass(kw_only=True)
class State(InputState, OutputState):
    """Complete state for the agent workflow."""
    # Core message history
    extracted_functions: List[Tuple[str, str]] = field(default_factory=list)
    original_script: str = field(default="")
    current_function_index: int = field(default=0)
    docstrings: Dict[str, str] = field(default_factory=dict)


class DocstringOutput(BaseModel):
    """Structure for the generated docstring output."""
    summary: str = Field(description="A clear, concise summary of what the function does")
    args: Dict[str, str] = Field(description="Dictionary mapping parameter names to their descriptions")
    returns: str = Field(description="Description of what the function returns")