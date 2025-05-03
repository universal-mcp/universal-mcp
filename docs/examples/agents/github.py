import asyncio

from openai import OpenAI

from universal_mcp.applications import app_from_slug
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools.manager import ToolManager

# Configuration
OPENROUTER_API_KEY = (
    "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"
)
MODEL = "google/gemini-2.0-flash-001"
REPOSITORY = "manojbajaj95/config"

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


async def setup_github_tools() -> ToolManager:
    """Initialize and configure GitHub tools."""
    app = app_from_slug("github")
    integration = AgentRIntegration(name="github")
    app_instance = app(integration=integration)

    tool_manager = ToolManager()
    tool_manager.register_tools_from_app(
        app_instance,
        # tools=["github_star_repository"],
        tags=["issues"],
    )
    return tool_manager


async def main():
    # Setup tools
    tool_manager = await setup_github_tools()
    tools = tool_manager.list_tools(format="openai")

    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can use tools.",
        },
        {"role": "user", "content": f"Star the repository {REPOSITORY}"},
    ]

    # Get AI response
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    data = await tool_manager.handle_tool_calls(response, format="openai")
    print(data)


if __name__ == "__main__":
    asyncio.run(main())
