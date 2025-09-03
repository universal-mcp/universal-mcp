import asyncio

from loguru import logger

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import AutoAgent


async def main():
    agent = AutoAgent(
        name="autoagent",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="azure/gpt-4.1",
        registry=AgentrRegistry(),
    )
    async for event in agent.stream(
        user_input="Send an email to manoj@agentr.dev",
        thread_id="test123",
    ):
        logger.info(event.content)
    # from loguru import logger; logger.debug(result)


if __name__ == "__main__":
    asyncio.run(main())
