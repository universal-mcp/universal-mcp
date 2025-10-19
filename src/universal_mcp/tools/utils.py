from universal_mcp.types import DEFAULT_APP_NAME, TOOL_NAME_SEPARATOR, ToolConfig


def get_app_and_tool_name(tool_name: str) -> tuple[str, str]:
    """Get the app and tool name from a tool name."""
    if TOOL_NAME_SEPARATOR in tool_name:
        app_name = tool_name.split(TOOL_NAME_SEPARATOR, 1)[0]
        tool_name_without_app_name = tool_name.split(TOOL_NAME_SEPARATOR, 1)[1]
    else:
        app_name = DEFAULT_APP_NAME
        tool_name_without_app_name = tool_name
    return app_name, tool_name_without_app_name


def tool_config_to_list(tools: ToolConfig) -> list[str]:
    """Convert a ToolConfig dictionary to a list of tool names."""
    return [
        f"{app_name}{TOOL_NAME_SEPARATOR}{tool_name}"
        for app_name, tool_names in tools.items()
        for tool_name in tool_names
    ]


def list_to_tool_config(tools: list[str]) -> ToolConfig:
    """Convert a list of tool names to a ToolConfig dictionary."""
    tool_config = {}
    for tool_name in tools:
        app_name, tool_name_without_app_name = get_app_and_tool_name(tool_name)
        tool_config.setdefault(app_name, []).append(tool_name_without_app_name)
    return tool_config
