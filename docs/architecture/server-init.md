# Server Initialization

This page documents the startup sequences for LocalServer and SingleMCPServer, showing how configuration is loaded and applications are initialized.

## Overview

Universal-mcp provides two server types:

1. **LocalServer** - Multi-application server configured via YAML
2. **SingleMCPServer** - Programmatic wrapper for a single application

Each has different initialization flows optimized for their use case.

## LocalServer Initialization

LocalServer loads multiple applications from a YAML configuration file.

### Complete Startup Flow

```mermaid
sequenceDiagram
    participant CLI as CLI/User
    participant Server as LocalServer
    participant Config as ServerConfig
    participant Store as Store Factory
    participant Int as Integration Factory
    participant App as Application Loader
    participant ToolMgr as ToolManager

    CLI->>Server: from_config("config.yaml")

    Server->>Config: Load YAML file
    Config->>Config: Parse and validate
    Config-->>Server: ServerConfig object

    Note over Server: Create server instance

    Server->>Store: Create store from config
    alt KeyringStore
        Store->>Store: Connect to system keyring
    else EnvironmentStore
        Store->>Store: Access os.environ
    else MemoryStore
        Store->>Store: Create in-memory dict
    end
    Store-->>Server: Store instance

    loop For each application in config
        Server->>Int: Create integration
        Int->>Store: Link to store
        Int-->>Server: Integration instance

        Server->>App: Load application module
        App->>App: Import Python module
        App->>App: Instantiate app class
        App-->>Server: Application instance

        Server->>App: list_tools()
        App-->>Server: [tool1, tool2, ...]

        loop For each tool
            Server->>ToolMgr: Register tool
        end
    end

    Note over Server: Server ready

    Server->>Server: run()
    Note over Server: Start FastMCP server<br/>Listen for MCP requests
```

### Configuration Loading

```mermaid
flowchart TD
    A[config.yaml] --> B[Read file]
    B --> C[Parse YAML]
    C --> D{Valid?}

    D -->|No| E[ConfigurationError]
    D -->|Yes| F[Create Pydantic models]

    F --> G[ServerConfig]
    G --> H[StoreConfig]
    G --> I[AppConfig list]

    I --> J[For each app]
    J --> K[Resolve environment variables]
    J --> L[Validate required fields]
    J --> M[Create IntegrationConfig]
```

### Example Configuration

```yaml
# config.yaml
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
    module: my_apps.slack_app
    class_name: SlackApp
    integration:
      type: api_key
      api_key_name: SLACK_BOT_TOKEN
      headers:
        Authorization: "Bearer {api_key}"
```

### Store Creation

```mermaid
flowchart TD
    A[StoreConfig] --> B{Store type?}

    B -->|keyring| C[Create KeyringStore]
    C --> D[service_name from config]
    D --> E[KeyringStore instance]

    B -->|environment| F[Create EnvironmentStore]
    F --> E

    B -->|memory| G[Create MemoryStore]
    G --> E

    B -->|custom| H[Import custom class]
    H --> I[Instantiate custom store]
    I --> E
```

### Application Loading

```mermaid
sequenceDiagram
    participant Server as LocalServer
    participant Loader as ApplicationLoader
    participant Module as Python Module System
    participant AppClass as Application Class

    Server->>Loader: Load application from config
    Loader->>Module: importlib.import_module(app.module)
    Module-->>Loader: Module object

    Loader->>Module: getattr(module, app.class_name)
    Module-->>Loader: Application class

    Loader->>AppClass: __init__(name, integration, **kwargs)
    AppClass-->>Loader: Application instance

    Loader-->>Server: Application ready
```

### Error Handling During Startup

```mermaid
flowchart TD
    A[Start initialization] --> B{Config file exists?}
    B -->|No| C[ConfigurationError]
    B -->|Yes| D{Valid YAML?}

    D -->|No| E[YAMLError]
    D -->|Yes| F{Schema valid?}

    F -->|No| G[ValidationError]
    F -->|Yes| H{Module importable?}

    H -->|No| I[ImportError]
    H -->|Yes| J{Class exists?}

    J -->|No| K[AttributeError]
    J -->|Yes| L{App init successful?}

    L -->|No| M[InitializationError]
    L -->|Yes| N[Application loaded]

    C --> O[Exit with error]
    E --> O
    G --> O
    I --> O
    K --> O
    M --> O

    N --> P[Continue with next app]
```

## SingleMCPServer Initialization

SingleMCPServer wraps a single application instance with minimal configuration.

### Startup Flow

```mermaid
sequenceDiagram
    participant User as Developer
    participant App as Application Instance
    participant Server as SingleMCPServer
    participant ToolMgr as ToolManager

    Note over User: Create application programmatically

    User->>App: Create application instance<br/>my_app = MyApp(...)

    User->>Server: SingleMCPServer(my_app)

    Server->>Server: Initialize FastMCP
    Server->>Server: Set up tool registry

    Note over Server: Lazy loading -<br/>tools not loaded yet

    User->>Server: run()

    Note over Server: First request triggers<br/>tool discovery

    Server->>App: list_tools()
    App-->>Server: [tool1, tool2, ...]

    loop For each tool
        Server->>ToolMgr: Register tool
    end

    Note over Server: Server ready,<br/>handle requests
```

### Lazy Tool Loading

SingleMCPServer uses lazy loading for better performance:

```mermaid
flowchart TD
    A[SingleMCPServer created] --> B[Server running]
    B --> C{First request received?}

    C -->|No| D[Wait for request]
    D --> C

    C -->|Yes| E{Tools loaded?}
    E -->|No| F[Load tools from app]
    F --> G[Cache tools]
    G --> H[Handle request]

    E -->|Yes| H
    H --> I[Subsequent requests]
    I --> H
```

### Example Usage

```python
from universal_mcp.applications import APIApplication
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import KeyringStore

# Create store
store = KeyringStore(service_name="my-app")

# Create integration
integration = ApiKeyIntegration(
    name="my_api_key",
    store=store,
    api_key_name="MY_API_KEY"
)

# Create application
class MyApp(APIApplication):
    def __init__(self):
        super().__init__(
            name="my_app",
            integration=integration
        )
        self.base_url = "https://api.example.com"

    def list_tools(self):
        return [self.get_data]

    def get_data(self, query: str) -> dict:
        """Get data from API."""
        return self.get(f"/data?q={query}")

# Create and run server
app = MyApp()
server = SingleMCPServer(app)
server.run()  # Blocks and serves MCP requests
```

## Comparison: LocalServer vs SingleMCPServer

| Feature | LocalServer | SingleMCPServer |
|---------|-------------|-----------------|
| **Configuration** | YAML file | Programmatic |
| **Applications** | Multiple | Single |
| **Tool Loading** | Eager (at startup) | Lazy (on first request) |
| **Best For** | Production, multiple integrations | Development, testing |
| **Store Setup** | Configured in YAML | Passed to application |
| **Reload** | Requires restart | Requires restart |
| **Complexity** | Higher | Lower |

## Server Lifecycle

### LocalServer Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: from_config()
    Created --> Configuring: Load YAML
    Configuring --> CreatingStore: Parse config
    CreatingStore --> LoadingApps: Initialize store
    LoadingApps --> RegisteringTools: For each app
    RegisteringTools --> Ready: All tools registered
    Ready --> Running: run()
    Running --> Serving: Handle MCP requests
    Serving --> Serving: Process tool calls
    Serving --> Shutdown: SIGTERM/SIGINT
    Shutdown --> [*]
```

### SingleMCPServer Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: __init__(app)
    Created --> Ready: Minimal setup
    Ready --> Running: run()
    Running --> LazyLoad: First request
    LazyLoad --> Serving: Tools loaded
    Serving --> Serving: Process tool calls
    Serving --> Shutdown: SIGTERM/SIGINT
    Shutdown --> [*]
```

## Configuration Validation

LocalServer validates configuration at startup:

```mermaid
flowchart TD
    A[ServerConfig] --> B{All required fields present?}
    B -->|No| C[Missing field error]

    B -->|Yes| D{Store type valid?}
    D -->|No| E[Invalid store type]

    D -->|Yes| F[Validate each AppConfig]
    F --> G{Module path valid?}
    G -->|No| H[Invalid module path]

    G -->|Yes| I{Integration config valid?}
    I -->|No| J[Invalid integration]

    I -->|Yes| K{Required env vars set?}
    K -->|No| L[Missing environment variable]

    K -->|Yes| M[Configuration valid]

    C --> N[Startup failed]
    E --> N
    H --> N
    J --> N
    L --> N

    M --> O[Proceed with initialization]
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ConfigurationError` | Invalid YAML syntax | Fix YAML formatting |
| `ModuleNotFoundError` | Application module not found | Check module path, install package |
| `AttributeError` | Class name not found in module | Check class_name in config |
| `ValidationError` | Missing required field | Add required fields to config |
| `EnvironmentError` | Environment variable not set | Set required environment variables |

## Hot Reload (Future Feature)

Currently, both servers require restart for configuration changes. Future versions may support hot reload:

```mermaid
sequenceDiagram
    participant FS as File System
    participant Watcher as Config Watcher
    participant Server as Server

    FS->>Watcher: config.yaml modified
    Watcher->>Server: Configuration changed event

    Server->>Server: Pause request handling
    Server->>Server: Reload configuration
    Server->>Server: Reinitialize applications
    Server->>Server: Update tool registry
    Server->>Server: Resume request handling

    Note over Server: Zero-downtime reload
```

## Debugging Startup Issues

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run server
server = LocalServer.from_config("config.yaml")
```

### Check Configuration

```python
from universal_mcp.config import ServerConfig

# Load and validate without starting server
config = ServerConfig.from_yaml("config.yaml")
print(config.model_dump_json(indent=2))
```

### Test Application Loading

```python
from universal_mcp.applications.utils import load_application

# Test loading a single app
app = load_application({
    "name": "test",
    "module": "my_module",
    "class_name": "MyApp"
})
print(f"Loaded: {app}")
print(f"Tools: {app.list_tools()}")
```

## Related Documentation

- [System Architecture](overview.md) - High-level architecture
- [Tool Registration](tool-registration.md) - What happens after initialization
- [Configuration API](../api/config.md) - Configuration schema reference
- [Servers API](../api/servers.md) - Server class reference
