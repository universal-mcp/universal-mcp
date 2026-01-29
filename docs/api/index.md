# API Reference

Complete API documentation for universal-mcp, generated from source code docstrings.

## Overview

This section provides detailed documentation for all public classes, methods, and functions in universal-mcp. The documentation is automatically generated from source code using [mkdocstrings](https://mkdocstrings.github.io/).

## Core Modules

### Applications
**[Applications API](applications.md)** - Base classes for creating API integrations

- `BaseApplication` - Abstract base for all applications
- `APIApplication` - REST API wrapper with HTTP client
- `GraphQLApplication` - GraphQL API wrapper with GQL client

### Integrations
**[Integrations API](integrations.md)** - Authentication and credential management

- `Integration` - Base integration class
- `ApiKeyIntegration` - Simple API key authentication
- `OAuthIntegration` - OAuth 2.0 flow implementation
- `AgentRIntegration` - Platform-managed credentials

### Tools
**[Tools API](tools.md)** - Tool definition and management

- `Tool` - Individual tool wrapper
- `ToolManager` - Central tool registry
- `FuncMetadata` - Function metadata extraction

### Servers
**[Servers API](servers.md)** - MCP server implementations

- `BaseServer` - Abstract MCP server base
- `LocalServer` - Multi-application YAML-configured server
- `SingleMCPServer` - Single application wrapper

### Stores
**[Stores API](stores.md)** - Credential storage backends

- `BaseStore` - Abstract storage interface
- `MemoryStore` - In-memory storage
- `EnvironmentStore` - Environment variable storage
- `KeyringStore` - System keyring storage

## Supporting Modules

### Configuration
**[Configuration API](config.md)** - Pydantic configuration models

- `ServerConfig` - Server configuration
- `AppConfig` - Application configuration
- `IntegrationConfig` - Integration configuration
- `StoreConfig` - Store configuration

### Registry
**[Registry API](registry.md)** - Tool registry implementations

- `ToolRegistry` - Abstract registry interface
- `LocalRegistry` - Local tool storage

### Adapters
**[Adapters API](adapters.md)** - Tool format converters

- MCP adapter - Native format
- LangChain adapter - LangChain tool format
- OpenAI adapter - OpenAI function calling format

### OAuth Client
**[OAuth Client API](client.md)** - OAuth flow implementation

- `CallbackServer` - OAuth callback handler
- `TokenStore` - Token storage utilities

### Exceptions
**[Exceptions API](exceptions.md)** - Exception hierarchy

- `UniversalMCPError` - Base exception
- `NotAuthorizedError` - Authentication errors
- `ToolNotFoundError` - Tool lookup errors
- And more...

### Types
**[Types API](types.md)** - Type definitions and enums

- Enums for integration types, store types, etc.
- Type aliases and constants

## Usage Examples

Each API page includes:

- **Class signatures** with type hints
- **Method documentation** from docstrings
- **Parameter descriptions** with types and defaults
- **Return value documentation**
- **Usage examples** where applicable

## Navigation Tips

- Use the search bar (top right) to find specific classes or methods
- Click on type hints to navigate to related classes
- Check the [Architecture](../architecture/index.md) section for conceptual diagrams
- See the main documentation for usage guides

## Contributing

When adding new features to universal-mcp:

1. Write clear docstrings following Google style
2. Include type hints on all public methods
3. Document parameters, return values, and exceptions
4. Add usage examples for complex functionality

The API documentation will be automatically generated from your docstrings.
