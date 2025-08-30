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
    await agent.run_interactive()
    # print(result)


if __name__ == "__main__":
    asyncio.run(main())
