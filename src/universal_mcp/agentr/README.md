# AgentR Python SDK

The official Python SDK for the AgentR platform, a component of the Universal MCP framework.

*Currently in beta, breaking changes are expected.*

The AgentR Python SDK provides convenient access to the AgentR REST API from any Python 3.10+ application, allowing for dynamic loading and management of tools and integrations.

## Installation

```bash
pip install universal-mcp
```

## Usage

The AgentR platform is designed to seamlessly integrate a wide array of tools into your agentic applications. The primary entry point for this is the `Agentr` class, which provides a high-level interface for loading and listing tools.

### High-Level Client (`Agentr`)

This is the recommended way to get started. It abstracts away the details of the registry and tool management.

```python
import os
from universal_mcp.agentr import Agentr
from universal_mcp.tools import ToolFormat

# Initialize the main client
# It reads from environment variables by default (AGENTR_API_KEY, AGENTR_BASE_URL)
agentr = Agentr(
    api_key=os.environ.get("AGENTR_API_KEY")
)

# Load specific tools from the AgentR server into the tool manager
agentr.load_tools(["reddit__search_subreddits", "google-drive__list_files"])

# List the tools that are now loaded and ready to be used
# You can specify a format compatible with your LLM (e.g., OPENAI)
tools = agentr.list_tools(format=ToolFormat.OPENAI)
print(tools)
```

### Low-Level API

For more granular control over the AgentR platform, you can use the lower-level components directly.

#### AgentrClient

The `AgentrClient` provides direct, one-to-one access to the AgentR REST API endpoints. The following examples have been updated to reflect the latest API structure.

```python
import os
from universal_mcp.agentr import AgentrClient
from universal_mcp.exceptions import NotAuthorizedError

# Initialize the low-level client
client = AgentrClient(
    api_key=os.environ.get("AGENTR_API_KEY")
)

# Fetch a list of available applications from the AgentR server
apps = client.list_apps()
print("Available Apps:", apps)

# Get credentials for a specific app by its ID (e.g., 'reddit')
# This will raise a NotAuthorizedError if the user needs to authenticate.
try:
    credentials = client.get_credentials(app_id="reddit")
    print("Reddit credentials found.")
except NotAuthorizedError as e:
    print(e)  # "Please ask the user to visit the following url to authorize..."

# List all available tools globally
all_tools = client.list_tools()
print("All Available Tools:", all_tools)

# Example of fetching a single app and a single tool
if apps:
    # Note: We access dictionary keys, not attributes
    app_id = apps[0]['id']

    # Fetch a single app's details
    app_details = client.get_app(app_id)
    print(f"Fetched details for app '{app_id}':", app_details)

if all_tools:
    tool_id = all_tools[0]['id']

    # Fetch a single tool's details
    tool_details = client.get_tool(tool_id)
    print(f"Fetched details for tool '{tool_id}':", tool_details)
```

#### AgentrIntegration

This class handles the authentication and authorization flow for a single integration (e.g., "reddit"). It's used under the hood by applications to acquire credentials.

```python
from universal_mcp.agentr import AgentrIntegration, AgentrClient
from universal_mcp.exceptions import NotAuthorizedError

client = AgentrClient()

# Create an integration for a specific service
reddit_integration = AgentrIntegration(name="reddit", client=client)

# If credentials are not present, this will raise NotAuthorizedError
try:
    creds = reddit_integration.credentials
    print("Successfully retrieved credentials.")
except NotAuthorizedError:
    # Get the URL to send the user to for authentication
    auth_url = reddit_integration.authorize()
    print(f"Please authorize here: {auth_url}")

# You can also use the get_credentials() method
try:
    creds = reddit_integration.get_credentials()
    print("Successfully retrieved credentials again.")
except NotAuthorizedError:
    print("Still not authorized.")
```

#### AgentrRegistry

The registry is responsible for discovering which tools are available on the AgentR platform.

```python
import asyncio
from universal_mcp.agentr import AgentrRegistry, AgentrClient

client = AgentrClient()
registry = AgentrRegistry(client=client)

async def main():
    # List all apps available on the AgentR platform
    available_apps = await registry.list_apps()
    print(available_apps)

    if available_apps:
        app_id = available_apps[0]['id']
        # Get details for a specific app
        app_details = await registry.get_app_details(app_id)
        print(f"Details for {app_id}:", app_details)

    # The load_tools method is used internally by the high-level Agentr client
    # but can be called directly if needed.
    # from universal_mcp.tools import ToolManager
    # tool_manager = ToolManager()
    # registry.load_tools(["reddit_search_subreddits"], tool_manager)
    # print(tool_manager.list_tools())


if __name__ == "__main__":
    asyncio.run(main())
```

#### AgentrServer

For server-side deployments, `AgentrServer` can be used to load all configured applications and their tools from an AgentR instance on startup.

```python
from universal_mcp.config import ServerConfig
from universal_mcp.agentr.server import AgentrServer

# Configuration for the server
config = ServerConfig(
    type="agentr",
    api_key="your-agentr-api-key"
)

# The server will automatically fetch and register all tools on initialization
server = AgentrServer(config=config)

# The tool manager is now populated with tools from the AgentR instance
tool_manager = server.tool_manager
print(tool_manager.list_tools())
```

## Executing Tools

Once tools are loaded, you can execute them using the `call_tool` method on the `ToolManager` instance, which is available via `agentr.manager`.

```python
import os
import asyncio
from universal_mcp.agentr import Agentr

async def main():
    # 1. Initialize Agentr
    agentr = Agentr(api_key=os.environ.get("AGENTR_API_KEY"))

    # 2. Load the tool(s) you want to use
    tool_name = "reddit__search_subreddits"
    agentr.load_tools([tool_name])

    # 3. Execute the tool using the tool manager
    try:
        # Note the 'await' since call_tool is an async method
        result = await agentr.manager.call_tool(
            name=tool_name,
            arguments={"query": "elon musk", "limit": 5, "sort": "relevance"}
        )
        print("Execution result:", result)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```
