# Universal MCP Playground

The Playground provides an interactive environment to test and demonstrate the capabilities of agents built with LangGraph that utilize tools exposed via the Universal MCP (Model Control Protocol). It features a Streamlit-based chat interface allowing users to interact with an AI agent that can leverage tools from a connected MCP server.

## 📋 Prerequisites

Before running the playground, ensure you have the following:

1.  **Python Environment**: Python 3.11+ is recommended.
2.  **Dependencies**: Install the necessary dependencies. If you have the project cloned, you can often install them using:

    ```bash
    pip install -e .[playground]
    ```

    Alternatively, manually install `streamlit`, `langchain-openai`, `langgraph`, `langchain-mcp-adapters`, `loguru`, `pydantic`, etc.

3.  **LLM API Access (Azure OpenAI by default)**:
    The default agent in `playground/agents/react.py` uses `AzureChatOpenAI`. You'll need to set the following environment variables:

    - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
    - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL.
      _If you wish to use a different LLM, you'll need to modify `playground/agents/react.py`._

4.  **AgentR API Key (for Auto Agent)**:
    If you want to use the Auto Agent, you'll need to set the following environment variable:

    - `AUTO_AGENT_API_KEY`: Your AgentR API key (get it from [agentr.dev](https://agentr.dev))

5.  **`local_config.json` in Project Root**:
    This file is crucial. It configures the **local Universal MCP server** that the playground's agent will connect to for tools. This file must be placed in the **root directory of the `universal-mcp` project** (i.e., one level above the `src` directory).

    The agent in `playground/agents/react.py` expects to connect to an MCP server at `http://localhost:8005` using Server-Sent Events (SSE). Therefore, your `local_config.json` should reflect this:

    **Example `local_config.json` (place in project root):**

    ```json
    {
      "name": "Playground Local MCP Server",
      "description": "MCP server for playground agent tools",
      "type": "local",
      "transport": "sse", // Must be "sse" for the playground agent
      "port": 8005, // Must be 8005 for the playground agent
      "apps": [
        {
          "name": "zenquotes" // Example: Exposes the zenquotes app and its tools
        },
        {
          "name": "tavily", // Example: Exposes Tavily search
          "integration": {
            "name": "TAVILY_API_KEY", // Credential name
            "type": "api_key",
            "store": {
              "type": "environment" // Expects TAVILY_API_KEY env var
            }
          }
        }
        // Add other apps you want the agent to access
      ]
    }
    ```

    - Ensure the `transport` is `"sse"` and `port` is `8005`.
    - Add any applications (tools) you want the agent to be able to use in the `apps` array. Ensure any necessary API keys for these tools are set as environment variables if their integration is configured to use `type: "environment"`.

## 🤖 Agent Types

The playground supports two different agent types:

### React Agent (Default)
The traditional MCP-based agent that connects to MCP servers and uses tools via the Model Control Protocol. This agent works with the local MCP server configuration.

### Auto Agent
An intelligent agent that can:
- Decompose complex tasks into individual steps
- Automatically search for and select relevant apps for each task
- Choose appropriate actions from those apps
- Execute tasks in sequence with context passing between steps

To use the Auto Agent, you'll need to set the `AUTO_AGENT_API_KEY` environment variable.

## ▶️ Running the Playground

### Automated Startup (Recommended)

The easiest way to start all necessary services is using the provided Python startup script. Execute this command from the **root directory** of the `universal-mcp` project:

```bash
python playground
```

This script will:

1.  Prompt you if you want to run a local MCP server (using `local_config.json`). If you say yes, it starts the MCP server.
2.  Launch the Streamlit application.

Your default web browser should open to the Streamlit app.

### Manual Startup (Alternative)

If you prefer, or if the automated script doesn't suit your needs, you can start the components manually. Run each command from the **project root directory** in a separate terminal window:

1.  **Terminal 1: Start the Universal MCP Server**
    _(Ensures the agent has tools to connect to. Uses `local_config.json` from the project root.)_

    ```bash
    universal_mcp run -c local_config.json
    ```

    _Wait for the server to indicate it's running (e.g., "MCP SSE Server running on http://localhost:8005")._

2.  **Terminal 2: Start the Streamlit Application**
    ```bash
    python -m streamlit run playground/streamlit.py
    ```
    _This will typically open the Streamlit app in your default web browser._

## <span style="color:red;">X</span> Stopping the Services

- **Automated Startup**: Press `Ctrl + C` in the terminal where you ran `python playground`. This should terminate both the Streamlit app and the MCP server (if started by the script).

- **Manual Startup**: Go to each terminal window where you started a service (MCP server, Streamlit app) and press `Ctrl + C`.
