# Request Flow

This page shows the detailed sequence of events when an AI agent calls a tool through universal-mcp.

## Overview

When an AI agent wants to call a tool (e.g., "create a GitHub issue"), the request flows through multiple layers:
1. MCP Client → MCP Server
2. Server → Tool Manager
3. Tool Manager → Tool
4. Tool → Application
5. Application → Integration → Store (for credentials)
6. Application → External API
7. Response flows back up the chain

## Complete Request Flow

```mermaid
sequenceDiagram
    participant Agent as AI Agent
    participant Client as MCP Client
    participant Server as BaseServer
    participant ToolMgr as ToolManager
    participant Tool as Tool
    participant App as Application
    participant Int as Integration
    participant Store as Store
    participant API as External API

    Agent->>Client: "Create GitHub issue"
    Client->>Server: call_tool("create_issue", args)

    Note over Server: Server validates request

    Server->>ToolMgr: call_tool("create_issue", args)
    ToolMgr->>ToolMgr: Find tool by name

    ToolMgr->>Tool: execute(**args)
    Note over Tool: Validate args against schema

    Tool->>App: create_issue(title, body, ...)

    Note over App: Need credentials for API
    App->>Int: get_credentials()
    Int->>Store: get("github_token")
    Store-->>Int: {"access_token": "ghp_..."}
    Int-->>App: {"access_token": "ghp_..."}

    Note over App: Build authenticated request
    App->>App: _get_headers()
    App->>API: POST /repos/.../issues<br/>{auth headers, body}

    API-->>App: 201 Created<br/>{issue data}

    Note over App: Parse response
    App-->>Tool: {issue_number, url, ...}
    Tool-->>ToolMgr: {issue_number, url, ...}
    ToolMgr-->>Server: {issue_number, url, ...}
    Server-->>Client: MCP Response<br/>{content: [...]}
    Client-->>Agent: "Created issue #123"
```

## Step-by-Step Breakdown

### 1. Tool Discovery (Initialization)

Before any tool can be called, it must be registered. This happens during server startup:

```mermaid
sequenceDiagram
    participant Server as BaseServer
    participant App as Application
    participant ToolMgr as ToolManager
    participant Tool as Tool

    Server->>App: list_tools()
    App-->>Server: [fn1, fn2, fn3]

    loop For each function
        Server->>Tool: from_function(fn)
        Note over Tool: Parse docstring<br/>Extract schema<br/>Create Tool instance
        Tool-->>Server: Tool instance
        Server->>ToolMgr: add_tool(tool)
    end

    Note over ToolMgr: All tools registered<br/>Ready to serve requests
```

### 2. Tool Invocation

When the agent wants to call a tool:

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as BaseServer
    participant ToolMgr as ToolManager

    Client->>Server: call_tool(name="create_issue", arguments={...})
    Server->>ToolMgr: call_tool("create_issue", {...})

    alt Tool exists
        ToolMgr-->>Server: result
        Server-->>Client: success response
    else Tool not found
        ToolMgr-->>Server: ToolNotFoundError
        Server-->>Client: error response
    end
```

### 3. Argument Validation

The Tool validates arguments against its JSON schema:

```mermaid
sequenceDiagram
    participant ToolMgr as ToolManager
    participant Tool as Tool
    participant Fn as Function

    ToolMgr->>Tool: execute(**arguments)

    Note over Tool: Validate args against<br/>inputSchema

    alt Valid arguments
        Tool->>Fn: fn(**arguments)
        Fn-->>Tool: result
        Tool-->>ToolMgr: result
    else Invalid arguments
        Tool-->>ToolMgr: ValidationError
    end
```

### 4. Authentication

The application retrieves credentials:

```mermaid
sequenceDiagram
    participant App as Application
    participant Int as Integration
    participant Store as Store

    App->>Int: get_credentials()

    alt Credentials exist
        Int->>Store: get(key)
        Store-->>Int: credential_data
        Int-->>App: credentials
    else Not authorized
        Int-->>App: NotAuthorizedError
    end

    App->>App: _get_headers()
    Note over App: Inject credentials into<br/>request headers
```

### 5. API Request

The application makes the external API call:

```mermaid
sequenceDiagram
    participant App as APIApplication
    participant HTTP as httpx.Client
    participant API as External API

    App->>HTTP: request(method, url, headers, json)
    HTTP->>API: HTTP Request

    alt Success (2xx)
        API-->>HTTP: 200/201 Response
        HTTP-->>App: response.json()
    else Client Error (4xx)
        API-->>HTTP: 400/401/404 Response
        HTTP-->>App: HTTPError
    else Server Error (5xx)
        API-->>HTTP: 500 Response
        HTTP-->>App: HTTPError
    end
```

### 6. Response Processing

The response flows back up the stack:

```mermaid
sequenceDiagram
    participant App as Application
    participant Tool as Tool
    participant ToolMgr as ToolManager
    participant Server as BaseServer
    participant Client as MCP Client

    App-->>Tool: result data
    Note over Tool: May format/validate<br/>response

    Tool-->>ToolMgr: result
    ToolMgr-->>Server: result

    Note over Server: Wrap in MCP format
    Server-->>Client: {<br/>  content: [{<br/>    type: "text",<br/>    text: result<br/>  }]<br/>}
```

## Error Handling

Errors at any layer are propagated back to the client:

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as BaseServer
    participant ToolMgr as ToolManager
    participant Tool as Tool
    participant App as Application
    participant API as External API

    Client->>Server: call_tool(...)
    Server->>ToolMgr: call_tool(...)
    ToolMgr->>Tool: execute(...)
    Tool->>App: tool_function(...)
    App->>API: HTTP Request

    alt API Error
        API-->>App: 401 Unauthorized
        App-->>Tool: NotAuthorizedError
        Tool-->>ToolMgr: NotAuthorizedError
        ToolMgr-->>Server: NotAuthorizedError
        Server-->>Client: Error Response:<br/>"Not authorized. Please run<br/>authorize() first."
    end
```

## Performance Considerations

### Caching

- **Tool schemas**: Cached after first generation
- **HTTP connections**: Reused via httpx.Client
- **Credentials**: Cached in memory after first retrieval

### Async Support

Universal-mcp supports async/await for:
- `get_credentials_async()`
- `authorize_async()`
- Async application methods

This allows non-blocking I/O for better performance.

### Connection Pooling

APIApplication uses httpx.Client which:
- Maintains connection pool
- Reuses TCP connections
- Supports HTTP/2

## Related Documentation

- [Authentication Flow](auth-flow.md) - Details on credential retrieval
- [Tool Registration](tool-registration.md) - How tools are discovered
- [Server Initialization](server-init.md) - Server startup sequence
