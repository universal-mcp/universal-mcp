import argparse

from dotenv import load_dotenv
from langsmith import Client

from evals.dataset import load_dataset

load_dotenv()


def upload_runs_to_dataset(project_name: str, dataset_name: str, dataset_description: str = ""):
    """
    Uploads runs from a LangSmith project to a dataset.

    Args:
        project_name: The name of the LangSmith project containing the runs.
        dataset_name: The name of the dataset to create or add to.
        dataset_description: A description for the new dataset.
    """
    client = Client()
    try:
        dataset = client.create_dataset(dataset_name, description=dataset_description)
        print(f"Created new dataset: '{dataset_name}'")
    except Exception:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Using existing dataset: '{dataset_name}'")

    runs = client.list_runs(project_name=project_name)

    example_count = 0
    for run in runs:
        client.create_example(
            inputs=run.inputs,
            outputs=run.outputs,
            dataset_id=dataset.id,
        )
        example_count += 1

    print(f"✅ Successfully uploaded {example_count} runs from project '{project_name}' to dataset '{dataset_name}'.")


def upload_dataset_from_file(
    file_path: str,
    dataset_name: str,
    dataset_description: str,
    input_keys: list[str],
    output_keys: list[str],
):
    """
    Uploads a dataset from a local file (CSV or JSONL) to LangSmith.

    Args:
        file_path: The path to the local dataset file.
        dataset_name: The name for the new dataset in LangSmith.
        dataset_description: A description for the new dataset.
        input_keys: A list of column names to be used as inputs.
        output_keys: A list of column names to be used as outputs.
    """
    client = Client()
    examples = load_dataset(file_path)

    try:
        dataset = client.create_dataset(dataset_name, description=dataset_description)
        print(f"Created new dataset: '{dataset_name}'")
    except Exception:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Using existing dataset: '{dataset_name}'")

    for example in examples:
        inputs = {key: example[key] for key in input_keys if key in example}
        outputs = {key: example[key] for key in output_keys if key in example}
        client.create_example(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

    print(f"✅ Successfully uploaded {len(examples)} examples from '{file_path}' to dataset '{dataset_name}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangSmith Dataset Utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for uploading runs from a project
    parser_runs = subparsers.add_parser("upload-runs", help="Upload runs from a project to a dataset.")
    parser_runs.add_argument("--project-name", required=True, help="The LangSmith project name.")
    parser_runs.add_argument("--dataset-name", required=True, help="The target dataset name.")
    parser_runs.add_argument(
        "--dataset-description", default="Dataset from project runs.", help="Description for the dataset."
    )

    # Sub-parser for uploading a dataset from a file
    parser_file = subparsers.add_parser("upload-file", help="Upload a dataset from a local file.")
    parser_file.add_argument("--file-path", required=True, help="Path to the local dataset file (CSV or JSONL).")
    parser_file.add_argument("--dataset-name", required=True, help="The name for the dataset in LangSmith.")
    parser_file.add_argument(
        "--dataset-description", default="Dataset uploaded from file.", help="Description for the dataset."
    )
    parser_file.add_argument("--input-keys", required=True, help="Comma-separated list of input column names.")
    parser_file.add_argument("--output-keys", required=True, help="Comma-separated list of output column names.")

    args = parser.parse_args()

    if args.command == "upload-runs":
        upload_runs_to_dataset(
            project_name=args.project_name,
            dataset_name=args.dataset_name,
            dataset_description=args.dataset_description,
        )
    elif args.command == "upload-file":
        upload_dataset_from_file(
            file_path=args.file_path,
            dataset_name=args.dataset_name,
            dataset_description=args.dataset_description,
            input_keys=args.input_keys.split(","),
            output_keys=args.output_keys.split(","),
        )
