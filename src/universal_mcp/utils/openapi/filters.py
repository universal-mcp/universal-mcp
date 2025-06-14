"""
Shared filtering utilities for OpenAPI selective processing.

This module contains common functions used by both the preprocessor
and API client generator for filtering operations based on JSON configuration.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


def load_filter_config(config_path: str) -> dict[str, str | list[str]]:
    """
    Load the JSON filter configuration file for selective processing.

    Expected format:
    {
        "/users/{user-id}/profile": "get",
        "/users/{user-id}/settings": "all",
        "/orders/{order-id}": ["get", "put", "delete"]
    }

    Args:
        config_path: Path to the JSON configuration file

    Returns:
        Dictionary mapping paths to methods

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
        ValueError: If config format is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Filter configuration file not found: {config_path}")

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in filter config file {config_path}: {e}") from e

    if not isinstance(config, dict):
        raise ValueError(f"Filter configuration must be a JSON object/dictionary, got {type(config)}")

    # Validate the configuration format
    for path, methods in config.items():
        if not isinstance(path, str):
            raise ValueError(f"Path keys must be strings, got {type(path)} for key: {path}")

        if isinstance(methods, str):
            if methods != "all" and methods.lower() not in [
                "get",
                "post",
                "put",
                "delete",
                "patch",
                "head",
                "options",
                "trace",
            ]:
                raise ValueError(f"Invalid method '{methods}' for path '{path}'. Use 'all' or valid HTTP methods.")
        elif isinstance(methods, list):
            for method in methods:
                if not isinstance(method, str) or method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                    "trace",
                ]:
                    raise ValueError(f"Invalid method '{method}' for path '{path}'. Use valid HTTP methods.")
        else:
            raise ValueError(f"Methods must be string or list of strings for path '{path}', got {type(methods)}")

    logger.info(f"Loaded filter configuration with {len(config)} path specifications")
    return config


def should_process_operation(path: str, method: str, filter_config: dict[str, str | list[str]] | None = None) -> bool:
    """
    Check if a specific path+method combination should be processed based on filter config.

    Args:
        path: The API path (e.g., "/users/{user-id}/profile")
        method: The HTTP method (e.g., "get")
        filter_config: Optional filter configuration dict

    Returns:
        True if the operation should be processed, False otherwise
    """
    if filter_config is None:
        return True  # No filter means process everything

    if path not in filter_config:
        return False  # Path not in config means skip

    allowed_methods = filter_config[path]
    method_lower = method.lower()

    if allowed_methods == "all":
        return True
    elif isinstance(allowed_methods, str):
        return method_lower == allowed_methods.lower()
    elif isinstance(allowed_methods, list):
        return method_lower in [m.lower() for m in allowed_methods]

    return False
