from enum import Enum


class ToolFormat(str, Enum):
    """Supported tool formats."""

    NATIVE = "native"
    MCP = "mcp"
    LANGCHAIN = "langchain"
    OPENAI = "openai"
