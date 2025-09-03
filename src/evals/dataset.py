import csv
import json
from typing import Any


def load_dataset(file_path: str) -> list[dict[str, Any]]:
    """
    Loads a dataset from a CSV or JSONL file.

    Args:
        file_path: The path to the dataset file.

    Returns:
        A list of dictionaries, where each dictionary represents an example.
    """
    if file_path.endswith(".csv"):
        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    elif file_path.endswith(".jsonl"):
        with open(file_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    else:
        raise ValueError("Unsupported file format. Please use CSV or JSONL.")
