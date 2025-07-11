# Universal MCP

Universal MCP acts as a middleware layer for your API applications, enabling seamless integration with various services through the Model Control Protocol (MCP). It simplifies credential management, authorization, dynamic app enablement, and provides a robust framework for building and managing AI-powered tools.

## 🌟 Features

- **MCP (Model Control Protocol) Integration**: Seamlessly works with MCP server architecture for standardized agent-tool communication.
- **Simplified API Integration**: Connect to services like GitHub, Google Calendar, Gmail, Reddit, Tavily, and more with minimal code. See [AgentR](https://agentr.dev) for a list of available applications.
- **Managed Authentication**: Built-in support for API keys and OAuth-based authentication flows, often managed via the AgentR platform.
- **Extensible Architecture**: Easily build and add new app integrations with minimal boilerplate using provided base classes and generation tools.
- **Credential Management**: Flexible and secure storage options for API credentials (memory, environment variables, system keyring).
- **Comprehensive Tool Management**: Robust tool registration, Pydantic-based validation, automatic docstring parsing, and execution capabilities. Supports conversion between MCP, LangChain, and OpenAI tool formats.
- **Multiple Server Types**: Configurations for local development, AgentR-connected dynamic app loading, and single-application servers.
- **Playground Environment**: Includes an interactive Streamlit-based playground for testing agents and tools.

## 🔧 Installation

Install Universal MCP using pip:

```bash
pip install universal-mcp
```

## 🚀 Quick Start

**Important Prerequisite: AgentR API Key (If Using AgentR Integration)**

If you plan to use integrations with `type: "agentr"` (for services like GitHub, Gmail, Notion via the AgentR platform), or if you run the MCP server itself with `type: "agentr"`, you first need an AgentR API key:

1.  Visit [https://agentr.dev](https://agentr.dev) to create an account and generate an API key from your dashboard.
2.  Set it as an environment variable _before_ running the MCP server:
    ```bash
    export AGENTR_API_KEY="your_api_key_here"
    ```

**1. Create a Configuration File (e.g., `config.json`)**

This file defines the server settings, credential stores, and the applications to load with their respective integrations.

```json
{
  "name": "My Local MCP Server",
  "description": "A server for testing applications locally",
  "type": "local", // "local" or "agentr"
  "transport": "sse", // "sse", "stdio", or "http"
  "port": 8005, // Relevant for "sse" or "http"
  "store": {
    // Default store for integrations
    "name": "my_mcp_store",
    "type": "keyring" // "keyring", "environment", or "memory"
  },
  "apps": [
    {
      "name": "zenquotes", // App slug (e.g., from agentr.dev)
      "integration": null // No authentication needed for this app
    },
    {
      "name": "tavily",
      "integration": {
        "name": "TAVILY_API_KEY", // Unique name for this credential if type is "api_key"
        "type": "api_key",
        "store": {
          // Override default store for this specific app
          "type": "environment" // Looks for TAVILY_API_KEY env var
        }
      }
    },
    {
      "name": "github",
      "integration": {
        "name": "github", // Matches the service name in AgentR
        "type": "agentr" // Uses AgentR platform for auth/creds
      }
    }
  ]
}
```

_Notes on `config.json`:_

- `type: "local"`: Runs applications defined directly in the config's `apps` list.
- `type: "agentr"`: Connects to the AgentR platform to dynamically load user-enabled apps (ignores the `apps` list in the config) and handle credentials. Requires `AGENTR_API_KEY` environment variable.
- `store`: Defines credential storage.
  - `environment`: Looks for an environment variable named `<INTEGRATION_NAME_UPPERCASE>` (e.g., `TAVILY_API_KEY` for the example above).
  - `keyring`: Uses the system's secure credential storage.
  - `memory`: Transient storage, lost when the server stops.
- `integration`: Configures authentication for each app.
  - `type: "agentr"`: Uses the AgentR platform for OAuth/credential management.
  - `type: "api_key"`: Uses the specified `store` to retrieve the key.

**2. Run the Server via CLI**

Ensure any required environment variables (like `TAVILY_API_KEY` for the Tavily example, or `AGENTR_API_KEY` if using `"agentr"` type server/integrations) are set.

```bash
universal_mcp run -c config.json
```

The server will start, load the configured applications (or connect to AgentR if `type: "agentr"`), and listen for connections based on the `transport` type.

## 🛠️ Using the Playground

The `playground` directory provides a runnable Streamlit application for interacting with agents that can use tools from an MCP server.

**Prerequisites:**

- **`local_config.json`**: This file must exist in the **project root directory** (the same directory as this `README.md`). It configures the _local_ MCP server that the playground's agent can connect to if you choose to run one. For an example, see the `local_config.json` structure in the [Playground README](playground/README.md).
- **Dependencies**: Install playground-specific dependencies. If you have the project cloned, you might install them via:
  ```bash
  pip install -e .[playground]
  # or manually install fastapi, streamlit, uvicorn, langchain-openai, etc.
  ```

**Running the Playground:**

The easiest way is to use the automated startup script from the **project root directory**:

```bash
python playground
```

This script will:

1. Optionally start a local MCP server (based on your `local_config.json`) if you confirm.
2. Launch the Streamlit application.

For more detailed setup, manual startup instructions, and an explanation of the `local_config.json` for the playground, please refer to the [Playground README](playground/README.md).

## 🧩 Available Applications

Universal MCP can integrate with a wide variety of applications. For a list of publicly available applications and their slugs (e.g., "github", "google-calendar"), please visit [AgentR Applications](https://agentr.dev).
Applications are typically installed dynamically by Universal MCP from their respective repositories when first referenced by slug.

_Authentication Type Notes:_

- _OAuth (via AgentR)_: Usually requires configuring the app's integration with `type: "agentr"` in your `ServerConfig`. This leverages the AgentR platform for the OAuth flow and requires the `AGENTR_API_KEY` to be set.
- _API Key (via Integration)_: Requires configuring `type: "api_key"` for the app's integration in your `ServerConfig`, along with a `store` (like `environment` or `keyring`) to specify where the API key is located.

## 🔐 Integration Types

Universal MCP supports different ways to handle authentication for applications:

### 1. API Key Integration (`type: "api_key"`)

For services that authenticate via simple API keys.

```json
// In your ServerConfig apps array:
{
  "name": "tavily",
  "integration": {
    "name": "TAVILY_API_KEY", // Used by the store (e.g., as env var name)
    "type": "api_key",
    "store": {
      "type": "environment" // Or "keyring", "memory"
    }
  }
}
```

### 2. AgentR Integration (`type: "agentr"`)

Recommended for services integrated with the AgentR platform, which typically handles OAuth flows or centrally managed credentials. Requires the `AGENTR_API_KEY` environment variable to be set for the MCP server process.

```json
// In your ServerConfig apps array:
{
  "name": "github",
  "integration": {
    "name": "github", // Matches the service name configured in AgentR
    "type": "agentr"
  }
}
```

When an action requiring authorization is called, the `AgentRIntegration` will prompt the user (via the MCP client) to visit a URL to complete the OAuth flow managed by AgentR. This is also the default integration type for apps if the main server config is `type: "agentr"`.

### 3. Direct OAuth Integration (`type: "oauth"`)

While `AgentRIntegration` is generally preferred for OAuth, a direct `OAuthIntegration` class exists. However, it requires manual configuration of client IDs, secrets, and callback handling, which is more complex to set up outside the AgentR platform.

## 🤖 CLI Usage

Universal MCP includes a powerful command-line interface:

```bash
# Run the MCP server using a configuration file
universal_mcp run -c config.json

# Initialize a new MCP application project structure
universal_mcp init --app-name my-cool-app --o ./my-apps --integration-type api_key

# Generate API client code and application structure from an OpenAPI schema
universal_mcp generate -s <path_to_schema.json_or_yaml> -o <path/to/app_output_directory> --c CustomAppClassName
# Example: universal_mcp generate -s notion_api.yaml -o ./custom_apps/notion --c MyNotionApp

# Preprocess an OpenAPI schema using an LLM to fill/enhance descriptions
universal_mcp preprocess -s <path_to_input_schema.json_or_yaml> -o <path_to_processed_schema.json_or_yaml>

# Generate Google-style docstrings for functions in a Python file using an LLM
universal_mcp docgen <path/to/app_file.py>

# Generate a README.md for a generated application file
universal_mcp readme <path/to/app_file.py>

# Install MCP configuration for supported desktop apps (e.g., Claude, Cursor)
# Requires an AgentR API key for configuration.
universal_mcp install claude
universal_mcp install cursor

# Check installed version (standard typer command)
universal_mcp --version
```

## 📋 Requirements

- Python 3.10+
- Key Dependencies (installed automatically via pip, see `pyproject.toml` for full list):
  - `mcp-server`
  - `loguru`
  - `typer`
  - `httpx`
  - `pydantic`
  - `pyyaml`
  - `keyring` (for `KeyringStore`)
  - `litellm` (for `docgen` and `preprocess` commands)
  - `uv` (used internally for dynamic package installation)

## 📚 Documentation

For more detailed information about specific components:

- [Applications Framework](src/universal_mcp/applications/README.md)
- [Tool Management](src/universal_mcp/tools/README.md)
- [Server Implementations](src/universal_mcp/servers/README.md)
- [Credential Stores](src/universal_mcp/stores/README.md)
- [Integration & Authentication](src/universal_mcp/integrations/README.md)
- [Playground Usage](playground/README.md)

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
