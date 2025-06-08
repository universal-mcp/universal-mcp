import asyncio
from contextlib import asynccontextmanager

from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


@asynccontextmanager
async def load_tools():
    url = "http://0.0.0.0:8005/sse"
    client = MultiServerMCPClient(
        {
            "agentr": {
                "url": url,
                "transport": "sse",
            },
        }
    )
    async with client.session("agentr") as session:
        tools = await load_mcp_tools(session)
        yield tools


@asynccontextmanager
async def create_agent():
    # llm = AzureChatOpenAI(
    #     model="gpt-4o",
    #     api_version="2024-12-01-preview",
    # )
    llm = ChatOpenAI(model="google/gemini-2.5-flash-preview-05-20")
    async with load_tools() as tools:
        yield create_react_agent(
            model=llm,
            tools=tools,
            debug=False,
        )


async def main():
    async with create_agent() as agent:
        print("Welcome to the agent!")
        messages = []
        while True:
            human_input = input("Enter your message: ")
            if human_input.lower() in ["exit", "quit", "q"]:
                break
            messages.append(HumanMessage(content=human_input))
            results = await agent.ainvoke({"messages": messages})
            ai_message = results["messages"][-1]
            messages.append(ai_message)
            print(ai_message.content)


if __name__ == "__main__":
    asyncio.run(main())
