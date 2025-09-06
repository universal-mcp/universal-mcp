from enum import Enum

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


ToolConfig = dict[str, list[str]]
