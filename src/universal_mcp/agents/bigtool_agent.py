from universal_mcp.agents.bigtool import BigToolAgent
from universal_mcp.agentr.registry import AgentrRegistry

agent = BigToolAgent(
    name="BigTool Agent",
    instructions="You are a helpful assistant that can use various tools to complete tasks.",
    model="gemini/gemini-2.0-flash-001",
    registry=AgentrRegistry()
)