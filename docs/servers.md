# Servers

This package provides server implementations for hosting and managing MCP (Model Control Protocol) applications.

## Overview

The server implementations provide different ways to host and expose MCP applications and their tools. The base `BaseServer` class provides common functionality that all server implementations inherit.

## Supported Server Types

### Local Server
The `LocalServer` class provides a local development server implementation that:
- Loads applications from local configuration
- Manages a local store for data persistence
- Supports integration with external services
- Exposes application tools through the MCP protocol

### AgentR Server
The `AgentRServer` class provides a server implementation that:
- Connects to the AgentR API
- Dynamically fetches and loads available applications
- Manages AgentR-specific integrations
- Requires an API key for authentication

### Single MCP Server
The `SingleMCPServer` class provides a minimal server implementation that:
- Hosts a single application instance
- Ideal for development and testing
- Does not manage integrations or stores internally
- Exposes only the tools from the provided application

## Core Features

All server implementations provide:

- Tool management and registration
- Application loading and configuration
- Error handling and logging
- MCP protocol compliance
- Integration support

## Usage

Each server implementation can be initialized with a `ServerConfig` object that specifies:
- Server name and description
- Port configuration
- Application configurations
- Store configuration (where applicable)

Example:
```python
from universal_mcp.servers import LocalServer
from universal_mcp.config import ServerConfig

config = ServerConfig(
    name="My Local Server",
    description="Development server for testing applications",
    port=8000,
    # ... additional configuration
)

server = LocalServer(config)
```

## Tool Management

Servers provide methods for:
- Adding individual tools
- Listing available tools
- Calling tools with proper error handling
- Formatting tool results

## Error Handling

All servers implement comprehensive error handling for:
- Tool execution failures
- Application loading errors
- Integration setup issues
- API communication problems
