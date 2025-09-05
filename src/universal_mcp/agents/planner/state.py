from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from universal_mcp.types import AgentrToolConfig


class State(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    apps_with_tools: AgentrToolConfig
