# Architecture Documentation

Welcome to the universal-mcp architecture documentation. This section provides detailed technical diagrams and explanations of the internal architecture for contributors.

## Overview

Universal-mcp is an MCP (Model Context Protocol) middleware framework that sits between AI agents and external applications/APIs. It provides credential management, tool registration, authentication flows, and flexible storage backends.

## Architecture Diagrams

Navigate to the following sections to understand different aspects of the system:

### Core Architecture

- **[System Architecture](overview.md)** - High-level overview of how components interact
- **[Class Hierarchy](class-hierarchy.md)** - UML class diagrams showing inheritance relationships

### Runtime Flows

- **[Request Flow](request-flow.md)** - Sequence diagram of how tool requests are processed
- **[Authentication Flow](auth-flow.md)** - OAuth, API Key, and AgentR authentication patterns
- **[Tool Registration](tool-registration.md)** - How tools are discovered and registered
- **[Server Initialization](server-init.md)** - Server startup sequences for LocalServer and SingleMCPServer

## Key Concepts

### Applications

Applications are adapters that wrap external APIs or services. They expose tools that AI agents can call. Universal-mcp supports:

- **APIApplication** - RESTful HTTP API integrations
- **GraphQLApplication** - GraphQL API integrations

### Integrations

Integrations handle authentication and credential management:

- **ApiKeyIntegration** - Simple API key auth
- **OAuthIntegration** - OAuth 2.0 flows
- **AgentRIntegration** - Platform-managed credentials

### Stores

Stores persist credentials and configuration:

- **MemoryStore** - In-memory (non-persistent)
- **EnvironmentStore** - OS environment variables
- **KeyringStore** - System keyring (secure)

### Servers

Servers expose the MCP protocol to AI agents:

- **LocalServer** - Multi-application server with config file
- **SingleMCPServer** - Single application wrapper

## For Contributors

If you're contributing to universal-mcp:

1. Start with the [System Architecture](overview.md) to understand the big picture
2. Review the [Class Hierarchy](class-hierarchy.md) to see how components relate
3. Study relevant runtime flows to understand behavior
4. Refer to the [API Reference](../api/index.md) for detailed class documentation

## Diagrams Format

All diagrams are created using [Mermaid](https://mermaid.js.org/), a markdown-based diagramming tool. You can edit the diagram source directly in the markdown files.
