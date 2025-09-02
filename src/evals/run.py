import argparse
import asyncio
from typing import Any

from dotenv import load_dotenv
from langsmith import Client, aevaluate
from langsmith.evaluation import RunEvaluator

from evals.dataset import load_dataset
from evals.evaluators import correctness_evaluator, exact_match_evaluator
from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.autoagent import AutoAgent
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.react import ReactAgent
from universal_mcp.agents.simple import SimpleAgent

load_dotenv()


# 1. Agent Factory
def get_agent(agent_name: str) -> BaseAgent:
    """
    Factory function to get an agent instance by name.
    """
    common_params = {
        "instructions": "You are a helpful assistant.",
        "model": "anthropic/claude-4-sonnet-20250514",
        "tool_registry": AgentrRegistry() if agent_name != "simple" else None,
    }
    if agent_name == "simple":
        return SimpleAgent(name="simple-agent", **common_params)
    elif agent_name == "react":
        return ReactAgent(name="react-agent", **common_params)
    elif agent_name == "auto":
        return AutoAgent(name="auto-agent", **common_params)
    else:
        raise ValueError(f"Unknown agent: {agent_name}. Available agents: simple, react, auto")


# 2. Evaluator Registry
EVALUATORS: dict[str, Any] = {
    "llm_as_judge": correctness_evaluator,
    "exact_match": exact_match_evaluator,
}


def get_evaluator(evaluator_name: str) -> RunEvaluator:
    """
    Retrieves an evaluator from the registry.
    """
    evaluator = EVALUATORS.get(evaluator_name)
    if evaluator is None:
        raise ValueError(f"Unknown evaluator: {evaluator_name}. Available evaluators: {', '.join(EVALUATORS.keys())}")
    return evaluator


# Wrapper to run the agent and format the output consistently
async def agent_runner(agent: BaseAgent, inputs: dict):
    """
    Runs the agent and returns a dictionary with the final output.
    """
    result = await agent.invoke(user_input=inputs["user_input"])
    # Extract the last message content as the final response
    if isinstance(result, dict) and "messages" in result and result["messages"]:
        content = result["messages"][-1].content
        if isinstance(content, str):
            final_response = content
        elif isinstance(content, list):
            # Handle list of content blocks (e.g., from Anthropic)
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            final_response = "\n".join(text_parts)
        else:
            final_response = str(content)
    else:
        final_response = str(result)
    return {"output": final_response}


async def main(agent_name: str, dataset_path: str, evaluator_name: str):
    """
    The main function for the evaluation CLI.
    """
    print(f"Starting evaluation with agent='{agent_name}', dataset='{dataset_path}', evaluator='{evaluator_name}'")

    # 1. Get the agent and evaluator
    agent = get_agent(agent_name)
    evaluator = get_evaluator(evaluator_name)

    # Create a callable for aevaluate
    async def target_func(inputs: dict):
        return await agent_runner(agent, inputs)

    # 2. Load the dataset from file
    dataset_examples = load_dataset(dataset_path)

    # 3. Upload dataset to LangSmith for the evaluation run
    client = Client()
    dataset_name = dataset_path.split("/")[-1].split(".")[0]
    # dataset_name = f"{agent_name}-{evaluator_name}-eval-dataset"
    try:
        # If dataset with same name and examples exists, read it.
        # Otherwise, a new one is created.
        dataset = client.create_dataset(
            dataset_name, description=f"Dataset for {agent_name} evaluation with {evaluator_name}."
        )
        for example in dataset_examples:
            client.create_example(
                inputs={"user_input": example["user_input"]},
                outputs={"output": example.get("expected_output")} if "expected_output" in example else None,
                dataset_id=dataset.id,
            )
        print(f"Created and populated dataset '{dataset_name}' for this run.")
    except Exception:
        print(f"Using existing dataset '{dataset_name}'.")

    # 4. Run the evaluation
    await aevaluate(
        target_func,
        data=dataset_name,  # Pass the dataset name
        evaluators=[evaluator],
        experiment_prefix=f"{agent_name}-{evaluator_name}-eval",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluations on different agents.")
    parser.add_argument(
        "agent",
        type=str,
        choices=["simple", "react", "auto"],
        help="The name of the agent to evaluate.",
    )
    parser.add_argument(
        "dataset",
        type=str,
        help="Path to the dataset file (e.g., src/evals/example_dataset.jsonl).",
    )
    parser.add_argument(
        "evaluator",
        type=str,
        choices=list(EVALUATORS.keys()),
        help="The name of the evaluator to use.",
    )
    args = parser.parse_args()

    asyncio.run(main(agent_name=args.agent, dataset_path=args.dataset, evaluator_name=args.evaluator))
