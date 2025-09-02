from enum import Enum
from typing import Literal

from pydantic import BaseModel

# Constants
DEFAULT_IMPORTANT_TAG = "important"
TOOL_NAME_SEPARATOR = "__"
DEFAULT_APP_NAME = "common"


class ToolFormat(str, Enum):
    """Supported tool formats."""

    NATIVE = "native"
    MCP = "mcp"
    LANGCHAIN = "langchain"
    OPENAI = "openai"


class AgentrConnection(BaseModel):
    tools: list[str]


class MCPConnection(BaseModel):
    transport: Literal["stdio", "sse", "streamable-http"]
    command: str | None = None
    args: list[str] | None = None
    url: str | None = None
    headers: dict[str, str] | None = None


class AgentrToolConfig(BaseModel):
    agentrServers: dict[str, AgentrConnection] | None = None


class ToolConfig(AgentrToolConfig):
    mcpServers: dict[str, MCPConnection] | None = None
