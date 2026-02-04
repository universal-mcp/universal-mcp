# Class Hierarchy

This page shows the inheritance relationships between core classes in universal-mcp using UML class diagrams.

## Overview

Universal-mcp uses inheritance to provide extensibility points for:
- **Applications** - Wrapping different API types
- **Integrations** - Supporting different auth mechanisms
- **Stores** - Using different credential storage backends
- **Servers** - Deploying different server configurations

## Application Hierarchy

```mermaid
classDiagram
    class BaseApplication {
        <<abstract>>
        +str name
        +__init__(name, **kwargs)
        +list_tools()* list~Callable~
    }

    class APIApplication {
        +Integration integration
        +int default_timeout
        +str base_url
        +_get_headers() dict
        +_make_request(method, endpoint, **kwargs) dict
        +get(endpoint, **kwargs) dict
        +post(endpoint, **kwargs) dict
        +put(endpoint, **kwargs) dict
        +delete(endpoint, **kwargs) dict
        +patch(endpoint, **kwargs) dict
    }

    class GraphQLApplication {
        +Integration integration
        +str graphql_url
        +_get_client() GraphQLClient
        +execute_query(query, variables) dict
        +execute_mutation(mutation, variables) dict
    }

    BaseApplication <|-- APIApplication : extends
    BaseApplication <|-- GraphQLApplication : extends

    class CustomAPIApp {
        +list_tools() list~Callable~
        +custom_tool_1()
        +custom_tool_2()
    }

    APIApplication <|-- CustomAPIApp : extends

    note for BaseApplication "Abstract base defines\nthe interface all\napplications must implement"
    note for APIApplication "Provides HTTP client\nand request helpers"
    note for GraphQLApplication "Provides GraphQL\nclient and query helpers"
```

### Key Points

- **BaseApplication**: Abstract base class that all applications must inherit from
  - Requires `list_tools()` method that returns callable functions
  - Each callable becomes a tool exposed to AI agents

- **APIApplication**: Base for REST API integrations
  - Manages httpx.Client for HTTP requests
  - Provides convenience methods (get, post, put, delete, patch)
  - Handles authentication headers via Integration

- **GraphQLApplication**: Base for GraphQL integrations
  - Manages GQL client
  - Provides query and mutation helpers
  - Also uses Integration for auth

## Integration Hierarchy

```mermaid
classDiagram
    class Integration {
        +str name
        +BaseStore store
        +str type
        +authorize() str
        +get_credentials() dict
        +set_credentials(credentials) void
    }

    class ApiKeyIntegration {
        +str api_key_name
        +authorize() str
        +get_credentials() dict
        +api_key property
    }

    Integration <|-- ApiKeyIntegration : extends

    note for Integration "Base class for\nall auth strategies"
    note for ApiKeyIntegration "Simple API key\nin headers or params"
```

### Key Points

- **Integration**: Base class for authentication strategies
  - Stores credentials in a configurable Store
  - Provides authorize() for setup instructions

- **ApiKeyIntegration**: Primary auth method
  - Reads API key from store
  - Returns credentials dict for requests
  - Handles key name sanitization

## Store Hierarchy

```mermaid
classDiagram
    class BaseStore {
        <<abstract>>
        +get(key) Any*
        +set(key, value)*
        +delete(key)*
    }

    class DiskStore {
        +Path path
        +str app_name
        +get(key) Any
        +set(key, value)
        +delete(key)
        +list_keys() list~str~
        +has(key) bool
        +clear()
    }

    class MemoryStore {
        -dict data
        +get(key) Any
        +set(key, value)
        +delete(key)
    }

    class EnvironmentStore {
        +get(key) Any
        +set(key, value)
        +delete(key)
    }

    class KeyringStore {
        +str app_name
        +get(key) Any
        +set(key, value)
        +delete(key)
    }

    BaseStore <|-- DiskStore : extends
    BaseStore <|-- MemoryStore : extends
    BaseStore <|-- EnvironmentStore : extends
    BaseStore <|-- KeyringStore : extends

    note for BaseStore "Abstract storage\ninterface"
    note for DiskStore "File-based JSON storage\n(default, persistent)"
    note for MemoryStore "In-memory dict\n(non-persistent)"
    note for EnvironmentStore "OS environment\nvariables"
    note for KeyringStore "System keyring\n(secure, persistent)"
```

### Key Points

- **BaseStore**: Abstract base for credential storage
  - Simple key-value interface
  - All stores provide same API

- **DiskStore**: Default persistent storage
  - Stores each key as a separate JSON file
  - Location: `~/.universal-mcp/store/`
  - Good for single-user deployments

- **MemoryStore**: In-memory only
  - Good for testing
  - Lost on process exit

- **EnvironmentStore**: Uses os.environ
  - Read from environment variables
  - Can write but not persistent across sessions

- **KeyringStore**: Secure storage
  - Uses system keyring (macOS Keychain, Windows Credential Manager, etc.)
  - Secure and persistent

## Server Hierarchy

```mermaid
classDiagram
    class BaseServer {
        <<abstract>>
        +list~BaseApplication~ applications
        +ToolManager tool_manager
        +BaseStore store
        +__init__(applications, store)
        +list_tools()* list~Tool~
        +call_tool(name, arguments)* Any
        +run()*
    }

    class LocalServer {
        +ServerConfig config
        +from_config(config_path) LocalServer
        +list_tools() list~Tool~
        +call_tool(name, arguments) Any
        +run()
    }

    class SingleMCPServer {
        +BaseApplication application
        +__init__(application)
        +list_tools() list~Tool~
        +call_tool(name, arguments) Any
        +run()
    }

    BaseServer <|-- LocalServer : extends
    BaseServer <|-- SingleMCPServer : extends

    note for BaseServer "Uses FastMCP under\nthe hood for MCP protocol"
    note for LocalServer "Multi-app server\nwith YAML config"
    note for SingleMCPServer "Wraps single\napplication"
```

### Key Points

- **BaseServer**: Abstract base built on FastMCP
  - Implements MCP protocol
  - Manages tool registry
  - Routes tool calls

- **LocalServer**: Configuration-driven server
  - Loads apps from YAML config
  - Supports multiple applications
  - Production deployment

- **SingleMCPServer**: Programmatic wrapper
  - Wraps one application
  - Simpler for single-app scenarios
  - Good for testing and development

## Tool System Classes

```mermaid
classDiagram
    class Tool {
        +str name
        +str description
        +dict inputSchema
        +Callable fn
        +from_function(fn) Tool
        +execute(**kwargs) Any
    }

    class ToolManager {
        +dict~str,Tool~ _tools
        +add_tool(tool)
        +get_tool(name) Tool
        +list_tools() list~Tool~
        +call_tool(name, args) Any
    }

    class FuncMetadata {
        +str name
        +str description
        +dict parameters
        +extract_from_function(fn) FuncMetadata
    }

    ToolManager --> Tool : manages
    Tool --> FuncMetadata : uses for schema
```

### Key Points

- **Tool**: Represents a callable tool
  - Wraps a Python function
  - Includes JSON schema for parameters
  - Handles execution

- **ToolManager**: Central tool registry
  - Stores all available tools
  - Routes tool calls by name
  - Thread-safe

- **FuncMetadata**: Schema extraction
  - Parses function docstrings
  - Generates JSON schemas from type hints
  - Maps Python types to JSON Schema types

## Relationships Summary

The class hierarchies provide clear extension points:

1. **Add new API type**: Extend `APIApplication` or `GraphQLApplication`
2. **Add auth method**: Extend `Integration`
3. **Add storage backend**: Extend `BaseStore`
4. **Add server type**: Extend `BaseServer`

All extensions automatically work with the existing tool system and MCP protocol implementation.
