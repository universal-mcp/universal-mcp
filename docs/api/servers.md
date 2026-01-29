# Servers API

Servers expose MCP protocol endpoints for AI agents to discover and call tools.

## BaseServer

::: universal_mcp.servers.server.BaseServer
    options:
      show_source: false

## LocalServer

::: universal_mcp.servers.server.LocalServer
    options:
      show_source: false

## SingleMCPServer

::: universal_mcp.servers.server.SingleMCPServer
    options:
      show_source: false

## Usage Examples

### LocalServer with YAML Config

```python
from universal_mcp.servers import LocalServer

# Create from config file
server = LocalServer.from_config("config.yaml")

# Run server (blocks)
server.run()
```

Example `config.yaml`:
```yaml
store:
  type: keyring
  service_name: universal-mcp

applications:
  - name: github
    module: universal_mcp.applications.github
    class_name: GitHubApp
    integration:
      type: oauth
      client_id: ${GITHUB_CLIENT_ID}
      client_secret: ${GITHUB_CLIENT_SECRET}
      auth_url: https://github.com/login/oauth/authorize
      token_url: https://github.com/login/oauth/access_token
      scopes:
        - repo
        - user

  - name: slack
    module: myapp.slack
    class_name: SlackApp
    integration:
      type: api_key
      api_key_name: SLACK_BOT_TOKEN
```

### SingleMCPServer (Programmatic)

```python
from universal_mcp.servers import SingleMCPServer
from universal_mcp.applications import APIApplication

# Create application
class MyApp(APIApplication):
    def __init__(self):
        super().__init__(name="myapp")
        self.base_url = "https://api.example.com"

    def list_tools(self):
        return [self.get_data]

    def get_data(self, query: str) -> dict:
        """Get data from API."""
        return self.get(f"/data?q={query}")

# Wrap in server
app = MyApp()
server = SingleMCPServer(app)

# Run
server.run()
```

### Multiple Applications with LocalServer

```python
from universal_mcp.servers import LocalServer
from universal_mcp.stores import KeyringStore
from universal_mcp.config import ServerConfig, AppConfig

# Build config programmatically
store = KeyringStore(service_name="my-server")

config = ServerConfig(
    store_config={"type": "keyring"},
    applications=[
        AppConfig(
            name="github",
            module="my_apps.github",
            class_name="GitHubApp",
            integration={
                "type": "oauth",
                "client_id": "...",
                # ...
            }
        ),
        AppConfig(
            name="slack",
            module="my_apps.slack",
            class_name="SlackApp",
            integration={
                "type": "api_key",
                "api_key_name": "SLACK_TOKEN"
            }
        )
    ]
)

# Create server
server = LocalServer(config, store)
server.run()
```

### Running Server in Background

```python
import threading

server = SingleMCPServer(app)

# Run in thread
thread = threading.Thread(target=server.run, daemon=True)
thread.start()

# Server now running in background
# Main thread can do other work
```

### MCP Client Integration

From an MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "universal-mcp": {
      "command": "universal_mcp",
      "args": ["serve", "--config", "config.yaml"],
      "env": {
        "GITHUB_CLIENT_ID": "...",
        "GITHUB_CLIENT_SECRET": "..."
      }
    }
  }
}
```

## Server Lifecycle

### Startup

```python
server = LocalServer.from_config("config.yaml")
# 1. Load config
# 2. Create store
# 3. Load applications
# 4. Register tools
# 5. Start FastMCP server

server.run()  # Blocks here, serving requests
```

### Graceful Shutdown

```python
import signal

server = LocalServer.from_config("config.yaml")

def signal_handler(sig, frame):
    print("Shutting down...")
    server.shutdown()  # Clean shutdown
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

server.run()
```

## Tool Discovery

### List Available Tools

```python
server = LocalServer.from_config("config.yaml")

# List all tools
tools = server.list_tools()

for tool in tools:
    print(f"{tool.name}: {tool.description}")
    print(f"  Schema: {tool.inputSchema}")
```

### Call Tool Directly

```python
# Call tool (bypassing MCP protocol)
result = server.call_tool(
    "create_issue",
    {
        "repo": "owner/repo",
        "title": "Bug report",
        "body": "Found a bug..."
    }
)
print(result)
```

## Configuration Options

### Store Configuration

```yaml
# Keyring (production)
store:
  type: keyring
  service_name: my-app

# Environment variables
store:
  type: environment

# Memory (testing only)
store:
  type: memory
```

### Application Configuration

```yaml
applications:
  - name: myapp
    module: path.to.module
    class_name: MyAppClass

    # Optional: pass kwargs to __init__
    init_kwargs:
      timeout: 30
      retry: true

    # Integration (optional)
    integration:
      type: api_key
      api_key_name: MY_API_KEY
```

### Server Options

```yaml
server:
  # Server name in MCP
  name: "My MCP Server"

  # Server version
  version: "1.0.0"

  # Enable debug logging
  debug: true

  # Custom transport options
  transport:
    buffer_size: 8192
```

## Testing

### Test Server with Mock Application

```python
from universal_mcp.servers import SingleMCPServer
from universal_mcp.applications import BaseApplication

class MockApp(BaseApplication):
    def list_tools(self):
        return [self.test_tool]

    def test_tool(self, input: str) -> str:
        """Test tool."""
        return f"Echo: {input}"

# Test
server = SingleMCPServer(MockApp("test"))
result = server.call_tool("test_tool", {"input": "hello"})
assert result == "Echo: hello"
```

### Integration Tests

```python
import pytest
from universal_mcp.servers import LocalServer

@pytest.fixture
def server():
    return LocalServer.from_config("test_config.yaml")

def test_list_tools(server):
    tools = server.list_tools()
    assert len(tools) > 0
    assert any(t.name == "expected_tool" for t in tools)

def test_call_tool(server):
    result = server.call_tool("test_tool", {"arg": "value"})
    assert result is not None
```

## Error Handling

### Application Load Errors

```python
try:
    server = LocalServer.from_config("config.yaml")
except ImportError as e:
    print(f"Failed to import application: {e}")
except Exception as e:
    print(f"Configuration error: {e}")
```

### Tool Call Errors

```python
from universal_mcp.exceptions import ToolNotFoundError, NotAuthorizedError

try:
    result = server.call_tool("my_tool", {"arg": "value"})
except ToolNotFoundError:
    print("Tool not found")
except NotAuthorizedError:
    print("Authentication required")
except Exception as e:
    print(f"Tool execution error: {e}")
```

## Best Practices

### 1. Use YAML Config for Production

```python
# Good - configuration as code
server = LocalServer.from_config("config.yaml")

# Avoid - hardcoded configuration
server = LocalServer(hardcoded_config)
```

### 2. Environment Variables for Secrets

```yaml
# Good
integration:
  client_id: ${GITHUB_CLIENT_ID}
  client_secret: ${GITHUB_CLIENT_SECRET}

# Bad - secrets in config file
integration:
  client_id: "abc123"
  client_secret: "secret456"
```

### 3. Structured Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

server = LocalServer.from_config("config.yaml")
server.run()
```

### 4. Health Checks

```python
def check_server_health(server):
    """Check if server can list tools."""
    try:
        tools = server.list_tools()
        return len(tools) > 0
    except Exception:
        return False

if not check_server_health(server):
    print("Server health check failed!")
```

## Related Documentation

- [Architecture: Server Initialization](../architecture/server-init.md) - Startup flow
- [Configuration API](config.md) - Config schema
- [Applications API](applications.md) - Creating applications
