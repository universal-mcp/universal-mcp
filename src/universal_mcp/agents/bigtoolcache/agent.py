from universal_mcp.agents.bigtoolcache import BigToolAgentCache
from universal_mcp.agentr.registry import AgentrRegistry

async def agent():
    agent_object = await BigToolAgentCache(
        name="BigTool Agent 2",
        instructions="You are a helpful assistant that can use various tools to complete tasks.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
    )._build_graph()
    return agent_object