"""
GitHub Agent Example
-------------------
This script demonstrates how to create an agent that can interact with GitHub using the Universal MCP framework.
It shows how to:
1. Set up GitHub tools
2. Configure the OpenAI client with OpenRouter
3. Use tools to perform GitHub actions
4. Handle tool responses

The example specifically shows how to star a GitHub repository.
"""

import asyncio
import json
import os

from openai import OpenAI

from universal_mcp.applications import app_from_slug
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools.manager import ToolManager

# Configuration Section
# -------------------
MODEL = os.environ.get("OPEN_AI_MODEL", "gpt-4o")  # The AI model to use
REPOSITORY = os.environ.get(
    "REPOSITORY", "manojbajaj95/config"
)  # The GitHub repository to interact with

# Initialize OpenAI client with OpenRouter configuration
# ---------------------------------------------------
# This sets up the client to use OpenRouter as the API provider
client = OpenAI()


async def setup_github_tools() -> ToolManager:
    """
    Initialize and configure GitHub tools.

    This function:
    1. Creates a GitHub application instance
    2. Sets up the integration
    3. Registers specific GitHub tools for use

    Returns:
        ToolManager: A configured tool manager with GitHub tools registered
    """
    # Create GitHub application instance
    app = app_from_slug("github")

    # Set up the integration
    integration = AgentRIntegration(name="github")
    app_instance = app(integration=integration)

    # Initialize and configure tool manager
    tool_manager = ToolManager()

    # Register GitHub tools
    # Note: Currently only registering tools with 'issues' tag
    # You can uncomment the tools parameter to specify specific tools
    tool_manager.register_tools_from_app(
        app_instance,
        tool_names=["github_star_repository"],  # Use specific tools
        tags=["repository"],  # Look up tools by tags
    )
    return tool_manager


async def main():
    """
    Main execution function that:
    1. Sets up the GitHub tools
    2. Prepares the AI conversation
    3. Gets AI response
    4. Handles tool execution
    """
    # Step 1: Setup tools
    tool_manager = await setup_github_tools()
    tools = tool_manager.list_tools(format="openai")

    # Step 2: Prepare conversation messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can use tools.",
        },
        {"role": "user", "content": f"Star the repository {REPOSITORY}"},
    ]

    # Step 3: Get AI response with tool usage
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Let the AI decide which tools to use
    )
    response_message = response.choices[0].message
    for tool_call in response_message.tool_calls:
        # Step 4: Handle tool execution
        function_name = tool_call.function.name
        function_arguments = json.loads(tool_call.function.arguments)
        result = await tool_manager.call_tool(function_name, function_arguments)
        print(result)


if __name__ == "__main__":
    # Run the main function using asyncio
    asyncio.run(main())
