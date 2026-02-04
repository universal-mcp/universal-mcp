# Universal MCP

Universal MCP acts as a middleware layer for your API applications, enabling seamless integration with various services through the Model Control Protocol (MCP). It simplifies credential management, authorization, dynamic app enablement, and provides a robust framework for building and managing AI-powered tools.

The universal mcp is designed with a single user in mind and running locally.

## Roadmap

- [ ] Connection/Integration magagement
- [ ] Tools Registry
- [ ] Skills Registry (add support for loading/building/searching/adding skills)
- [ ] CLI for agents (allow adding MCP, skills, etc, etc)
- [ ] Billing and Usage tracking
- [ ] Workflows ( for determininstic DAG runs created by agents)
- [ ] Crontab (for scheduling tasks)
- [ ] Memory ( cross run persistence of agents)

## Quick Start - MCP Client

Universal MCP uses [FastMCP](https://gofastmcp.com/) for connecting to MCP servers with OAuth 2.1 authentication:

```python
import asyncio
from fastmcp import Client

async def main():
    # Connect to an MCP server with OAuth (FastMCP handles everything!)
    async with Client("https://mcp.notion.com/mcp", auth="oauth") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")

        # Call a tool
        result = await client.call_tool("tool_name", {"arg": "value"})
        print(result)

asyncio.run(main())
```

**Features:**
- Built-in OAuth 2.1 with PKCE
- Automatic token management via [py-key-value](https://strawgate.com/py-key-value/)
- Browser-based authorization flow
- Persistent token storage (DiskStore, Redis, DynamoDB, etc.)
- Multiple transports (HTTP, STDIO, in-memory)

Run the example:
```bash
uv run python examples/simple_client.py
```

See **[MCP Client Guide](docs/mcp_client_guide.md)** for detailed documentation.

## Documentation

The primary documentation for Universal MCP is available in `/docs` folder in this repository.

Please refer to the following for more detailed information:

*   **[Main Documentation](docs/index.md)**: For an overview of the project, features, quick start, and installation.
*   **[MCP Client Guide](docs/mcp_client_guide.md)**: For connecting to MCP servers using FastMCP.
*   **[Applications Framework](docs/applications.md)**: For details on the applications module.
*   **[Integrations & Authentication](docs/integrations.md)**: For information on integration types.
*   **[Server Implementations](docs/servers.md)**: For details on server types.
*   **[Credential Stores](docs/stores.md)**: For information on credential stores.
*   **[Tools Framework](docs/tools_framework.md)**: For details on the tool management system.
*   **[Contributing Guidelines](CONTRIBUTING.md)**: For information on how to contribute to the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
