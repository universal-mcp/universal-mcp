from enum import StrEnum

# Constants
DEFAULT_IMPORTANT_TAG = "important"
TOOL_NAME_SEPARATOR = "__"
DEFAULT_APP_NAME = "common"


class ToolFormat(StrEnum):
    """Supported tool formats."""

    NATIVE = "native"
    MCP = "mcp"
    OPENAI = "openai"


ToolConfig = dict[str, list[str]]
