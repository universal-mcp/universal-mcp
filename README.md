# Universal MCP

Universal MCP acts as a middle ware for your API applications. It can store your credentials, authorize, enable disable apps on the fly and much more.


## 🌟 Features

- **MCP (Model Context Protocol) Integration**: Seamlessly works with MCP server architecture
- **Simplified API Integration**: Connect to services like GitHub, Google Calendar, Gmail, Reddit, Tavily, and more with minimal code
- **Managed Authentication**: Built-in support for API keys and OAuth-based authentication flows
- **Extensible Architecture**: Easily build and add new app integrations with minimal boilerplate
- **Credential Management**: Flexible storage options for API credentials with memory and environment-based implementations

## 🔧 Installation

Install AgentR using pip:

```bash
pip install universal-mcp
```

## 🚀 Quick Start

### 1. Get an API Key
Before using AgentR with services that require authorization (like GitHub, Gmail, etc.), you'll need an AgentR API key:

Visit https://agentr.dev to create an account
Generate an API key from your dashboard
Set it as an environment variable or include it directly in your code:

```bash
export AGENTR_API_KEY="your_api_key_here"
```

### 2. Create a basic server

```bash
from agentr.server import TestServer

# Define your applications list
apps_list = [
    {
        "name": "tavily",
        "integration": {
            "name": "tavily_api_key",
            "type": "api_key",
            "store": {
                "type": "environment",
            }
        },        
    },
    {
        "name": "zenquotes",
        "integration": None
    },
    {
        "name": "github",
        "integration": {
            "name": "github",
            "type": "agentr",
        }
    }
]

# Create a server with these applications
server = TestServer(name="My Agent Server", description="A server for my agent apps", apps_list=apps_list)

# Run the server
if __name__ == "__main__":
    server.run()
```

## Using Playground

Start MCP Server
```bash
universal_mcp run -t sse
```

Start FastAPI app
```bash
fastapi run src/playground
```

Start Frontend
```bash
streamlit run src/playground/streamlit.py
```


## 🧩 Available Applications
AgentR comes with several pre-built applications:

| Application | Description | Authentication Type |
|-------------|-------------|---------------------|
| GitHub | Star repositories and more | OAuth (AgentR) |
| Google Calendar | Retrieve calendar events | OAuth (AgentR) |
| Gmail | Send emails | OAuth (AgentR) |
| Reddit | Access Reddit data | OAuth (AgentR) |
| Resend | Send emails via Resend API | API Key |
| Tavily | Web search capabilities | API Key |
| ZenQuotes | Get inspirational quotes | None |

> **Note**: More applications are coming soon! Stay tuned for updates to our application catalog.

## 🔐 Integration Types
AgentR supports two primary integration types:

### 1. API Key Integration
For services that authenticate via API keys:
```python
{
    "name": "service_name",
    "integration": {
        "name": "service_api_key",
        "type": "api_key",
        "store": {
            "type": "environment",  # or "memory"
        }
    }
}
```

### 2. OAuth Integration (via AgentR)
For services requiring OAuth flow:
```python
{
    "name": "service_name",
    "integration": {
        "name": "service_name",
        "type": "agentr"
    }
}
```
When using OAuth integrations, users will be directed to authenticate with the service provider through a secure flow managed by AgentR.

## 🤖 CLI Usage
AgentR includes a command-line interface for common operations:

```bash
# Get version information
agentr version

# Generate API client from OpenAPI schema

# Use the name of the API as the output filename (e.g., twitter, petstore, github)
universal_mcp generate --schema petstore.json --output outputfilename

# The tool will create src/universal_mcp/applications/petstore/ with app.py and README.md

# Run the test server
agentr run

# Install AgentR for specific applications
agentr install claude
```

## 📋 Requirements

- Python 3.11+
- Dependencies (automatically installed):
  - loguru >= 0.7.3
  - mcp >= 1.5.0
  - pyyaml >= 6.0.2
  - typer >= 0.15.2


## 📝 License

This project is licensed under the MIT License.
