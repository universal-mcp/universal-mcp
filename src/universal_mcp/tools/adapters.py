from universal_mcp.tools.tools import Tool


def convert_tool_to_mcp_tool(
    tool: Tool,
):
    from mcp.server.fastmcp.server import MCPTool

    return MCPTool(
        name=tool.name,
        description=tool.description or "",
        inputSchema=tool.parameters,
    )


def convert_tool_to_langchain_tool(
    tool: Tool,
):
    from langchain_core.tools import StructuredTool

    """Convert an tool to a LangChain tool.

    NOTE: this tool can be executed only in a context of an active MCP client session.

    Args:
        tool: Tool to convert

    Returns:
        a LangChain tool
    """

    async def call_tool(
        **arguments: dict[str, any],
    ):
        call_tool_result = await tool.run(arguments)
        return call_tool_result

    return StructuredTool(
        name=tool.name,
        description=tool.description or "",
        coroutine=call_tool,
        response_format="content",
    )
