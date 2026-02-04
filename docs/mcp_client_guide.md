# MCP Client Guide

The Universal MCP Client uses [FastMCP](https://gofastmcp.com/) for connecting to MCP servers with OAuth 2.1 authentication. FastMCP provides built-in OAuth support with automatic token management using [py-key-value](https://strawgate.com/py-key-value/).

## Features

- 🔐 **OAuth 2.1 with PKCE** - Secure authentication with Proof Key for Code Exchange
- 💾 **Automatic Token Management** - Tokens stored and refreshed automatically via py-key-value
- 🔄 **Connection Management** - Efficient connection lifecycle handling
- 🌐 **Multiple Transports** - HTTP, STDIO, and in-memory connections
- ⚡ **Async/Await** - Modern async Python API with context managers

## Quick Start

### Basic Usage

```python
import asyncio
from fastmcp import Client

async def main():
    # Connect with OAuth (FastMCP handles everything automatically)
    async with Client("https://your-server.com/mcp", auth="oauth") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")

        # Call a tool
        result = await client.call_tool("tool_name", {"arg": "value"})
        print(f"Result: {result}")

        # List resources
        resources = await client.list_resources()
        print(f"Resources: {[r.uri for r in resources]}")

asyncio.run(main())
```

Run the example:
```bash
uv run python examples/simple_client.py
```

## OAuth Configuration

### Simple OAuth (Recommended)

The simplest approach uses the string "oauth":

```python
from fastmcp import Client

async with Client("https://your-server.com/mcp", auth="oauth") as client:
    await client.ping()
```

FastMCP automatically:
- Discovers OAuth endpoints
- Registers the client dynamically
- Opens browser for authorization
- Stores tokens securely
- Refreshes expired tokens

### Advanced OAuth Configuration

For more control, use the `OAuth` helper:

```python
from fastmcp import Client
from fastmcp.client.auth import OAuth

oauth = OAuth(
    mcp_url="https://your-server.com/mcp",
    client_name="My Custom Client",
    scopes="user admin",  # Space-separated or list
    callback_port=3000,   # Fixed callback port
)

async with Client("https://your-server.com/mcp", auth=oauth) as client:
    await client.ping()
```

### Custom Token Storage

By default, tokens are stored in memory and lost on restart. For persistence, provide a py-key-value store:

```python
from fastmcp import Client
from fastmcp.client.auth import OAuth
from key_value.aio.stores.disk import DiskStore
from pathlib import Path

# Create custom storage location
token_path = Path.home() / ".universal_mcp" / "tokens"
token_path.mkdir(parents=True, exist_ok=True)

token_storage = DiskStore(path=str(token_path))

oauth = OAuth(
    mcp_url="https://your-server.com/mcp",
    token_storage=token_storage,
    client_name="My Client",
)

async with Client("https://your-server.com/mcp", auth=oauth) as client:
    tools = await client.list_tools()
```

### Encrypted Token Storage

For production, use encrypted storage:

```python
from fastmcp.client.auth import OAuth
from key_value.aio.stores.disk import DiskStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
from cryptography.fernet import Fernet
import os

# Create encryption key (store securely!)
# key = Fernet.generate_key()
# os.environ["OAUTH_STORAGE_ENCRYPTION_KEY"] = key.decode()

encrypted_storage = FernetEncryptionWrapper(
    key_value=DiskStore(path="~/.universal_mcp/tokens"),
    fernet=Fernet(os.environ["OAUTH_STORAGE_ENCRYPTION_KEY"])
)

oauth = OAuth(
    mcp_url="https://your-server.com/mcp",
    token_storage=encrypted_storage,
)
```

## Storage Backends (py-key-value)

FastMCP uses py-key-value for token storage, supporting multiple backends:

### DiskStore (Default for persistence)
```python
from key_value.aio.stores.disk import DiskStore

token_storage = DiskStore(path="~/.universal_mcp/tokens")
```

### MemoryStore (for testing)
```python
from key_value.aio.stores.memory import MemoryStore

token_storage = MemoryStore()  # Lost on restart
```

### KeyringStore (OS-level secure storage)
```python
from key_value.aio.stores.keyring import KeyringStore

token_storage = KeyringStore(service="universal-mcp")
```

### Redis (for distributed systems)
```python
from key_value.aio.stores.redis import RedisStore

token_storage = RedisStore(url="redis://localhost:6379/0")
```

### DynamoDB (for cloud deployments)
```python
from key_value.aio.stores.dynamodb import DynamoDBStore

token_storage = DynamoDBStore(table_name="mcp-tokens")
```

## Connection Transports

### HTTP Transport (Remote Servers)

```python
from fastmcp import Client

# Simple URL
async with Client("https://your-server.com/mcp", auth="oauth") as client:
    await client.ping()
```

### STDIO Transport (Local Servers)

```python
from fastmcp import Client

# Run server as subprocess
async with Client("my_server.py") as client:
    await client.ping()

# With environment variables
async with Client("my_server.py", env={"API_KEY": "secret"}) as client:
    await client.ping()
```

### In-Memory Transport (Testing)

```python
from fastmcp import Client, FastMCP

# Create server
server = FastMCP("TestServer")

@server.tool()
def add(a: int, b: int) -> int:
    return a + b

# Connect directly
client = Client(server)
async with client:
    result = await client.call_tool("add", {"a": 5, "b": 3})
    print(result)
```

## API Reference

### Client Class

#### Constructor
```python
Client(
    source,                  # Server URL, file path, or FastMCP instance
    auth=None,              # "oauth" or OAuth instance
    auto_initialize=True,   # Auto handshake
    timeout=None,           # Operation timeout
    env=None,               # Environment variables (STDIO)
    log_handler=None,       # Server log callback
    progress_handler=None,  # Progress callback
)
```

#### Methods

##### Connection Management
- `async with client:` - Context manager for lifecycle
- `is_connected()` - Check connection status
- `initialize(timeout=None)` - Manual initialization
- `close()` - Close connection

##### Server Operations
- `list_tools()` - Get available tools
- `call_tool(name, arguments)` - Execute tool
- `list_resources()` - Get available resources
- `read_resource(uri)` - Read resource content
- `list_prompts()` - Get available prompts
- `get_prompt(name, arguments)` - Get rendered prompt
- `ping()` - Test server connection

## OAuth Flow

### First Connection

1. Client checks for stored tokens
2. If none found, initiates OAuth flow:
   - Discovers OAuth endpoints via `.well-known/oauth-authorization-server`
   - Performs dynamic client registration (RFC 7591)
   - Starts local callback server
   - Opens browser to authorization URL
   - User authorizes application
   - Exchanges authorization code for tokens (PKCE)
3. Tokens stored in configured backend
4. Connection established

### Subsequent Connections

1. Client loads stored tokens
2. If valid, connection established immediately
3. If expired, automatically refreshes using refresh token
4. If refresh fails, repeats OAuth flow

## Multi-Server Configuration

Connect to multiple servers using a configuration dictionary:

```python
from fastmcp import Client

config = {
    "mcpServers": {
        "weather": {
            "url": "https://weather-api.example.com/mcp"
        },
        "assistant": {
            "command": "python",
            "args": ["./assistant_server.py"]
        }
    }
}

client = Client(config)

async with client:
    # Tools prefixed with server names
    weather = await client.call_tool("weather_get_forecast", {"city": "London"})
    response = await client.call_tool("assistant_answer_question", {"question": "Hello"})
```

## Error Handling

```python
from fastmcp import Client
from fastmcp.exceptions import MCPError, AuthenticationError

try:
    async with Client("https://your-server.com/mcp", auth="oauth") as client:
        tools = await client.list_tools()
        result = await client.call_tool("my_tool", {"arg": "value"})
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except MCPError as e:
    print(f"MCP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

### Test a Local Server

```python
import asyncio
from fastmcp import Client

async def test_server():
    client = Client("my_server.py")
    async with client:
        # Test tool listing
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")

        # Test tool execution
        result = await client.call_tool("example_tool", {})
        print(f"Result: {result}")

asyncio.run(test_server())
```

### Test with In-Memory Server

```python
from fastmcp import Client, FastMCP

server = FastMCP("TestServer")

@server.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

async def test():
    client = Client(server)
    async with client:
        result = await client.call_tool("greet", {"name": "World"})
        assert result.data == "Hello, World!"

import asyncio
asyncio.run(test())
```

## Troubleshooting

### OAuth Browser Not Opening
- Check server URL is correct
- Ensure callback port (default random) is available
- Try setting fixed callback port: `OAuth(callback_port=3000)`

### Connection Refused
- Verify server is running
- Check URL/path is correct
- Ensure no firewall blocking

### Tokens Not Persisting
- Check you're using a persistent store (DiskStore, KeyringStore, etc.)
- Verify path is writable
- Check file permissions

### Token Refresh Failing
- Delete stored tokens and re-authenticate
- Check server supports refresh tokens
- Verify OAuth endpoint configuration

## Examples

### Connect to Notion
```python
from fastmcp import Client

async with Client("https://mcp.notion.com/mcp", auth="oauth") as client:
    tools = await client.list_tools()
    print(f"Notion tools: {[t.name for t in tools]}")
```

### Connect to GitHub
```python
from fastmcp import Client

async with Client("https://api.github.com/mcp", auth="oauth") as client:
    repos = await client.list_resources()
    print(f"Repositories: {[r.uri for r in repos]}")
```

### Custom Storage Example
```python
from fastmcp import Client
from fastmcp.client.auth import OAuth
from key_value.aio.stores.disk import DiskStore

oauth = OAuth(
    mcp_url="https://your-server.com/mcp",
    token_storage=DiskStore(path="~/.my_app/tokens"),
    client_name="My Application",
    scopes="read write",
)

async with Client("https://your-server.com/mcp", auth=oauth) as client:
    await client.ping()
```

## See Also

- **[FastMCP Documentation](https://gofastmcp.com/)** - Complete FastMCP docs
- **[FastMCP OAuth Guide](https://gofastmcp.com/clients/auth/oauth)** - Detailed OAuth documentation
- **[FastMCP Client API](https://gofastmcp.com/clients/client)** - Client API reference
- **[py-key-value Documentation](https://strawgate.com/py-key-value/)** - Storage backend library
- **[py-key-value GitHub](https://github.com/strawgate/py-key-value)** - Source and examples
- **[MCP Protocol](https://modelcontextprotocol.io)** - MCP specification
- **[OAuth 2.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-07)** - OAuth 2.1 spec
