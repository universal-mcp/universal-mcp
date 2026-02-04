# Universal MCP

## Quick Links

- **[Architecture Documentation](architecture/index.md)** - System design and flow diagrams for contributors
- **[API Reference](api/index.md)** - Complete API documentation
- **[Getting Started](#getting-started)** - Installation and setup guides
- **[Migration Guide](migration.md)** - Upgrading from previous versions

Universal MCP is a single-user SDK for building and managing AI-powered tools through the Model Control Protocol (MCP). It provides a robust framework for credential management, tool registration, and seamless integration with various services.

## Features

- **MCP (Model Control Protocol) Integration**: Seamlessly works with MCP server architecture for standardized agent-tool communication.
- **Simplified API Integration**: Connect to services like GitHub, Google Calendar, Gmail, Reddit, Tavily, and more with minimal code.
- **API Key Authentication**: Built-in support for API key-based authentication with flexible credential storage.
- **Extensible Architecture**: Easily build and add new app integrations with minimal boilerplate using provided base classes and generation tools.
- **Credential Management**: Flexible and secure storage options for API credentials (disk, memory, environment variables, system keyring).
- **Comprehensive Tool Management**: Robust tool registration, Pydantic-based validation, automatic docstring parsing, and execution capabilities. Supports conversion between MCP, LangChain, and OpenAI tool formats.
- **Local Server Architecture**: Simple local server for development and production single-user deployments.

## Installation

Install Universal MCP using pip:

```bash
pip install universal-mcp
```

## Quick Start

**1. Create a Configuration File (e.g., `config.json`)**

This file defines the server settings, credential stores, and the applications to load with their respective integrations.

```json
{
  "name": "My Local MCP Server",
  "description": "A server for local development",
  "type": "local",
  "transport": "stdio",
  "store": {
    "name": "my_mcp_store",
    "type": "disk"
  },
  "apps": [
    {
      "name": "zenquotes",
      "integration": null
    },
    {
      "name": "tavily",
      "integration": {
        "name": "TAVILY_API_KEY",
        "type": "api_key",
        "store": {
          "type": "environment"
        }
      }
    },
    {
      "name": "github",
      "integration": {
        "name": "GITHUB_TOKEN",
        "type": "api_key",
        "store": {
          "type": "disk"
        }
      }
    }
  ]
}
```

_Notes on `config.json`:_

- `type: "local"`: Runs applications defined directly in the config's `apps` list.
- `store`: Defines credential storage (default: `disk`).
  - `disk`: Persistent file-based storage at `~/.universal-mcp/store` (recommended default).
  - `environment`: Looks for an environment variable named `<INTEGRATION_NAME_UPPERCASE>` (e.g., `TAVILY_API_KEY`).
  - `keyring`: Uses the system's secure credential storage (macOS Keychain, Windows Credential Manager, etc.).
  - `memory`: Transient storage, lost when the server stops.
- `integration`: Configures authentication for each app.
  - `type: "api_key"`: Uses the specified `store` to retrieve the API key.

**2. Run the Server**

Use the SDK directly in your Python code:

```python
from universal_mcp.config import ServerConfig
from universal_mcp.servers.server import LocalServer

# Load configuration
config = ServerConfig.from_json("config.json")

# Create and run server
server = LocalServer(config)
server.run()
```

The server will start, load the configured applications, and listen for connections based on the `transport` type.


## Available Applications

Universal MCP can integrate with a wide variety of applications. Applications are typically loaded dynamically by Universal MCP from their respective packages when first referenced by slug.

Common applications include:
- **github** - GitHub API integration
- **google-calendar** - Google Calendar API
- **gmail** - Gmail API
- **tavily** - Tavily search API
- **zenquotes** - ZenQuotes API (no authentication required)

_Authentication Notes:_

- _API Key_: Configure `type: "api_key"` for the app's integration in your `ServerConfig`, along with a `store` (like `disk`, `environment`, or `keyring`) to specify where the API key is located.
- _No Auth_: Some applications (like `zenquotes`) don't require authentication. Set `integration: null`.

## Integration Types

Universal MCP supports API key-based authentication for applications:

### API Key Integration (`type: "api_key"`)

For services that authenticate via API keys or tokens.

```json
{
  "name": "tavily",
  "integration": {
    "name": "TAVILY_API_KEY",
    "type": "api_key",
    "store": {
      "type": "disk"
    }
  }
}
```

**Store Options:**

- `disk` (default): Persistent file-based storage at `~/.universal-mcp/store`
- `environment`: Reads from environment variable with the integration name
- `keyring`: Uses system secure storage
- `memory`: Transient in-memory storage


## Future Roadmap

Universal MCP has an ambitious roadmap for building a comprehensive, production-ready SDK for AI agent tooling. Our upcoming features include:

### Key Features in Development

- **Skills Registry**: A marketplace-like system for discovering, sharing, and executing reusable agent skills with versioning and composability
- **Billing Registry**: Comprehensive usage tracking and cost management for monitoring tokens, API calls, and resource consumption
- **Workflow System**: Powerful orchestration for chaining tools and skills into complex, multi-step processes with conditional logic and error handling
- **Crontabs for Agents**: Scheduled task execution with cron-like syntax for automating recurring workflows and maintenance tasks

These features will enable sophisticated agent behaviors, transparent cost management, and scalable automation. For detailed specifications and timelines, see our [complete roadmap](https://github.com/universal-mcp/universal-mcp/blob/main/ROADMAP.md).

## Requirements

- Python 3.10+
- Key Dependencies (installed automatically via pip, see `pyproject.toml` for full list):
  - `fastmcp`
  - `mcp`
  - `loguru`
  - `typer`
  - `httpx`
  - `pydantic`
  - `pyyaml`
  - `keyring` (for `KeyringStore`)
  - `uv` (used internally for dynamic package installation)

## Documentation

For more detailed information about specific components:

- [Applications Framework](applications.md)
- [Tool Management](tools_framework.md)
- [Server Implementations](servers.md)
- [Credential Stores](stores.md)
- [Integration & Authentication](integrations.md)
- [Migration Guide](migration.md)
- [Future Roadmap](https://github.com/universal-mcp/universal-mcp/blob/main/ROADMAP.md)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/universal-mcp/universal-mcp/blob/main/LICENSE) file for details.
