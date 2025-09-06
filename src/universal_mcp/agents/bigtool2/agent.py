from universal_mcp.agents.bigtool2 import BigToolAgent2
from universal_mcp.agentr.registry import AgentrRegistry

async def agent():
    agent_object = await BigToolAgent2(
        name="BigTool Agent 2",
        instructions="You are a helpful assistant that can use various tools to complete tasks.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
    )._build_graph()
    return agent_object