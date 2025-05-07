# Import necessary libraries
import os  # For environment variable access
from typing import Annotated  # For type annotations

from langchain_openai import ChatOpenAI  # OpenAI's chat model interface
from langgraph.prebuilt import (
    create_react_agent,
)  # Pre-built ReAct agent implementation
from loguru import logger  # For logging

from universal_mcp.tools.adapters import ToolFormat  # Tool format definitions
from universal_mcp.tools.manager import ToolManager  # Tool management system


# Define a simple calculator tool that can evaluate mathematical expressions
async def calculate(s: Annotated[str, "The expression to calculate"]) -> int:
    """
    Calculate the result of the expression.
    Args:
        s: A string containing a mathematical expression to evaluate
    Returns:
        The integer result of the calculation
    """
    logger.info(f"Calculating {s}")
    return eval(s)


async def main():
    # Initialize the OpenAI model - defaults to "gpt-4o-mini" if not specified
    model = os.environ.get("OPEN_AI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model)

    # Create a tool manager and register our calculator tool
    tool_manager = ToolManager()
    tool_manager.add_tool(calculate, name="calculate")

    # Get the list of tools in LangChain format
    tools = tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
    print(tools)

    # Create a ReAct agent with the specified tools and system prompt
    agent = create_react_agent(
        llm,
        tools=tools,
        prompt="You are a helpful assistant that can use tools to help the user.",
    )

    # Run the agent with a simple math question
    result = await agent.ainvoke(
        input={"messages": [{"role": "user", "content": "What is 2 + 2?"}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    # Run the async main function
    import asyncio

    asyncio.run(main())
