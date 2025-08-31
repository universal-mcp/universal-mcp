import asyncio

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import AutoAgent


async def main():
    agent = AutoAgent(
        name="autoagent",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="azure/gpt-4.1",
        tool_registry=AgentrRegistry(),
    )
    await agent.invoke(
        user_input="Please send the email from google-mail to manoj@agentr.dev, with subject hello and body hello from auto",
        thread_id="12345",
    )
    # from loguru import logger; logger.debug(result)


if __name__ == "__main__":
    asyncio.run(main())
