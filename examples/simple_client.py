"""
Ultra-simple MCP client example using FastMCP.

Run with:
    uv run python examples/simple_client.py

FastMCP provides built-in OAuth 2.1 support with automatic token management.
Tokens are automatically stored and refreshed using py-key-value.
"""

import asyncio

from fastmcp import Client


async def main():
    """Simple example using Notion MCP server."""

    # Uses OAuth authentication (automatic browser-based login)
    # FastMCP handles all token storage and refresh automatically
    async with Client("https://mcp.notion.com/mcp", auth="oauth") as client:

        # List available tools
        tools = await client.list_tools()
        print(f"✅ Connected! Found {len(tools)} tools")

        # List tool names
        print("\nAvailable tools:")
        for tool in tools:
            print(f"  - {tool.name}")

        # Example: Call a tool (uncomment to use)
        # if tools:
        #     result = await client.call_tool(tools[0].name, {})
        #     print(f"\nTool result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
