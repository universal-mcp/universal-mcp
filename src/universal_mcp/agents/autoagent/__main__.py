import asyncio

from universal_mcp.agentr import Agentr, AgentrClient
from universal_mcp.agents.autoagent.graph import create_agent
from universal_mcp.types import ToolFormat

tool_names = ["google-mail__send_email", "outlook__user_send_mail"]

client = AgentrClient()


# Use Agentr to fetch tools instead of math module
agentr = Agentr()
agentr.load_tools(tool_names)
all_tools = agentr.list_tools(format=ToolFormat.LANGCHAIN)


def retrieve_tools(
    query: str,
) -> list[str]:
    """Retrieve a tool to use, given a search query."""
    results = client.search_all_tools(query=query, limit=1)
    print(f"Retrieved tools: {results}")
    tool_ids = [result["id"] for result in results]

    print(f"Retrieved tools: {tool_ids}")
    return tool_ids


tool_registry = {tool.name: tool for tool in all_tools}

builder = create_agent(tool_registry, retrieve_tools_function=retrieve_tools)
agent = builder.compile()


async def main():
    result = await agent.ainvoke(
        input={
            "messages": [
                {
                    "role": "user",
                    "content": "Send an email to manoj@agentr.dev with the subject 'testing autoagent' and the body 'This is a test email from the autoagent'",
                }
            ]
        },
        context={"system_prompt": "You are a helpful assistant", "model": "azure/gpt-4.1"},
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
