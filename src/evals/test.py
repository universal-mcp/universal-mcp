import asyncio

from dotenv import load_dotenv
from langsmith import Client, aevaluate

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import AutoAgent

load_dotenv()


async def target_function1(inputs: dict):
    agent = AutoAgent(
        name="autoagent",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        tool_registry=AgentrRegistry(),
    )
    result = await agent.invoke(inputs["user_input"])
    return result


if __name__ == "__main__":
    client = Client()
    dataset_name = "autoagent-actual-runs"
    experiment = asyncio.run(
        aevaluate(
            target_function1,
            data=client.list_examples(dataset_name=dataset_name, splits=["choose-app"]),
            evaluators=[],
            experiment_prefix="test-1",
        )
    )
    asyncio.run(
        aevaluate(
            target_function1,
            data=client.list_examples(dataset_name=dataset_name),
            evaluators=[],
            experiment=experiment.experiment_name,
        )
    )
