import asyncio

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.planner import PlannerAgent


async def main():
    registry = AgentrRegistry()
    agent = PlannerAgent(
        name="planner-agent",
        instructions="You are a helpful assistant.",
        model="gemini/gemini-2.5-flash",
        registry=registry,
    )
    from rich.console import Console

    console = Console()
    console.print("Starting agent...", style="yellow")
    async for event in agent.stream(user_input="Send an email to manoj@agentr.dev'", thread_id="xyz"):
        console.print(event.content, style="red")


if __name__ == "__main__":
    asyncio.run(main())
