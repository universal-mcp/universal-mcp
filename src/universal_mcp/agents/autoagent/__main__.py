import asyncio

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import AutoAgent


async def main():
    agent = AutoAgent(
        name="autoagent",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        tool_registry=AgentrRegistry(),
    )
    result = await agent.invoke(
        user_input="Send an email to Manoj from my google mail account, manoj@agentr.dev, with the subject 'Hello from auto agent' and the body 'testing'"
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
