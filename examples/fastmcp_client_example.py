"""
Ultra-simple MCP client using FastMCP's built-in OAuth support.

FastMCP's client is simpler and has built-in OAuth 2.1 with PKCE.
It automatically handles token storage using py-key-value.

Run with:
    uv run python examples/fastmcp_client_example.py
"""

import asyncio

from fastmcp import Client


async def main():
    """Connect to an MCP server using FastMCP's built-in OAuth."""

    # Simple OAuth connection - FastMCP handles everything
    async with Client("https://mcp.notion.com/mcp", auth="oauth") as client:

        print("✅ Connected to Notion MCP server!\n")

        # List available tools
        tools = await client.list_tools()
        print(f"📋 Found {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool.name}")
        print()

        # List available resources
        try:
            resources = await client.list_resources()
            print(f"📦 Found {len(resources)} resources:")
            for resource in resources:
                print(f"  • {resource.uri}")
            print()
        except Exception as e:
            print(f"  (No resources or error: {e})\n")

        # Example: Call a tool (uncomment to use)
        # if tools:
        #     result = await client.call_tool(tools[0].name, {})
        #     print(f"\n🔧 Tool result: {result}")


async def main_with_custom_storage():
    """
    Example with custom token storage using py-key-value.

    FastMCP uses py-key-value for token storage, just like our implementation!
    """
    from fastmcp.client.auth import OAuth
    from key_value.aio.stores.disk import DiskStore
    from pathlib import Path

    # Create custom token storage location
    token_path = Path.home() / ".universal_mcp" / "fastmcp_tokens"
    token_path.mkdir(parents=True, exist_ok=True)

    token_storage = DiskStore(path=str(token_path))

    # Configure OAuth with custom storage
    oauth = OAuth(
        mcp_url="https://mcp.notion.com/mcp",
        token_storage=token_storage,
        client_name="Universal MCP FastMCP Client",
        scopes="user",
    )

    async with Client("https://mcp.notion.com/mcp", auth=oauth) as client:
        await client.ping()
        print("✅ Connected with custom token storage!")

        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")


if __name__ == "__main__":
    # Run the simple example
    asyncio.run(main())

    # Or use custom storage:
    # asyncio.run(main_with_custom_storage())
