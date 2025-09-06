import asyncio

from dotenv import load_dotenv
from langsmith import Client, aevaluate

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.bigtool2 import BigToolAgent2
from universal_mcp.agents.bigtoolcache import BigToolAgentCache
from universal_mcp.agents.planner import PlannerAgent

load_dotenv()


async def target_function1(inputs: dict):
    agent = await BigToolAgent2(
        name="bigtool2",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
    )._build_graph()
    result = await agent.ainvoke(
        inputs, config={"recursion_limit": 15}, context={"model": "anthropic/claude-4-sonnet-20250514"}
    )
    return result


async def target_function2(inputs: dict):
    agent = await BigToolAgentCache(
        name="bigtoolcache",
        instructions="You are a helpful assistant that can use tools to help the user.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
    )._build_graph()
    result = await agent.ainvoke(
        inputs, config={"recursion_limit": 15}, context={"model": "anthropic/claude-4-sonnet-20250514"}
    )
    return result


async def target_function3(inputs: dict):
    agent = await PlannerAgent(
        name="planner-agent",
        instructions="You are a helpful assistant.",
        model="anthropic/claude-4-sonnet-20250514",
        registry=AgentrRegistry(),
    )._build_graph()
    result = await agent.ainvoke(
        inputs, config={"recursion_limit": 35}, context={"model": "anthropic/claude-4-sonnet-20250514"}
    )
    return result


if __name__ == "__main__":
    client = Client()
    dataset_name = "bigtool-tests"
    #     asyncio.run(aevaluate(
    #     target_function1,
    #     data=client.list_examples(
    #         dataset_name=dataset_name,example_ids=["5425de13-58b0-44b3-802f-9e5e6b2e3a0c", "56bcf12f-2608-4ad7-8538-507ff0e22df1", "79ecefe9-3a13-428e-bdda-f3cc1eb03578", "c0a2e3cf-9bea-4cf3-90be-7ab8945094b3", "a73827d5-2c77-4d8b-a486-93b0e8ce6713"]
    #     ),
    #     evaluators=[],
    #     experiment_prefix ="test-1-errors"
    # ))

    asyncio.run(
        aevaluate(
            target_function3,
            data=client.list_examples(dataset_name=dataset_name),
            evaluators=[],
            experiment_prefix="planner35",
        )
    )
