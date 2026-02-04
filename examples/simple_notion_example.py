"""
Simple example to connect to Notion MCP server using FastMCP.

Run with:
    uv run python examples/simple_notion_example.py
"""

import asyncio

from fastmcp import Client
from fastmcp.client.auth import OAuth
from key_value.aio.stores.disk import DiskStore
from pathlib import Path


async def main():
    """Connect to Notion MCP server and test the connection."""

    # Simple OAuth connection - FastMCP handles everything
    async with Client("https://mcp.notion.com/mcp", auth="oauth") as client:

        print("✅ Connected to Notion MCP server!\n")

        # List available tools
        print("📋 Available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  • {tool.name}")
            if tool.description:
                print(f"    {tool.description}")
        print(f"\nTotal: {len(tools)} tools\n")

        # List available resources
        print("📦 Available resources:")
        try:
            resources = await client.list_resources()
            for resource in resources:
                print(f"  • {resource.uri}")
                if resource.name:
                    print(f"    {resource.name}")
            print(f"\nTotal: {len(resources)} resources\n")
        except Exception as e:
            print(f"  (No resources available or error: {e})\n")

        # Example: Call a tool if any are available
        if tools:
            print(f"💡 Example: To call a tool, use:")
            print(f"   result = await client.call_tool('{tools[0].name}', {{}})")
            print(f"   print(result)")


async def main_with_custom_storage():
    """Example with custom token storage location."""

    # Create custom token storage
    token_path = Path.home() / ".universal_mcp" / "tokens"
    token_path.mkdir(parents=True, exist_ok=True)

    token_storage = DiskStore(path=str(token_path))

    # Configure OAuth with custom storage
    oauth = OAuth(
        mcp_url="https://mcp.notion.com/mcp",
        token_storage=token_storage,
        client_name="Universal MCP Notion Client",
        scopes="user",
    )

    async with Client("https://mcp.notion.com/mcp", auth=oauth) as client:
        print("✅ Connected with custom token storage!")

        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")


if __name__ == "__main__":
    # Run the simple example
    asyncio.run(main())

    # Or use custom storage:
    # asyncio.run(main_with_custom_storage())
