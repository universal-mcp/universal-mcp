"""
Subprocess worker for sandbox code execution.

This module runs in a separate process and executes Python code with isolation.
It communicates with the main process via pickle over stdin/stdout.
"""

import ast
import asyncio
import builtins
import contextlib
import inspect
import io
import queue
import re
import socket
import sys
import threading
import types
from typing import Any

try:
    import cloudpickle as pickle
except ImportError:
    import pickle  # Fallback to standard pickle

from loguru import logger

# Exclude types that cannot be pickled or are system types (must match sandbox.py)
EXCLUDE_TYPES = (
    types.ModuleType,
    type(re.match("", "")),
    type(re.compile("")),
    type(threading.Lock()),
    type(threading.RLock()),
    threading.Event,
    threading.Condition,
    threading.Semaphore,
    queue.Queue,
    socket.socket,
    io.IOBase,
)

# Built-in names that should not be preserved in context
BUILTIN_NAMES = set(dir(builtins)) | {
    "__builtins__",
    "__cached__",
    "__doc__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__spec__",
    "In",
    "Out",
    "exit",
    "quit",
    "get_ipython",
}


def filter_picklable(namespace: dict[str, Any]) -> dict[str, Any]:
    """
    Filter namespace to only include picklable user-defined variables and functions.

    Excludes:
    - Dunder variables (__xxx__)
    - Built-in functions and types
    - Running coroutines and async generator instances (not picklable)
    - Unpicklable types (modules, locks, sockets, etc.)

    Includes:
    - Async function definitions (async def) - these ARE picklable with cloudpickle

    Args:
        namespace: Dictionary of variables from execution

    Returns:
        Dictionary containing only picklable user-defined variables and functions
    """
    filtered = {}
    for key, value in namespace.items():
        # Skip private/dunder variables
        if key.startswith("__"):
            continue

        # Skip built-in names
        if key in BUILTIN_NAMES:
            continue

        # Skip running coroutines and async generator instances (not picklable)
        # Note: async def functions (iscoroutinefunction) ARE picklable with cloudpickle
        if inspect.iscoroutine(value):  # Running coroutine instance
            continue
        if inspect.isasyncgen(value):  # Running async generator instance
            continue

        # Skip excluded types
        if isinstance(value, EXCLUDE_TYPES):
            continue

        # Try to pickle everything else (cloudpickle can handle user-defined functions/classes)
        try:
            pickle.dumps(value)
            filtered[key] = value
        except Exception:
            # Skip unpicklable objects
            logger.warning(f"Unpicklable object: {key}")

    return filtered


async def execute_code(code: str, namespace: dict[str, Any], timeout: int) -> dict[str, Any]:
    """
    Execute Python code with async support and timeout.

    Args:
        code: Python code to execute
        namespace: Dictionary containing variables and functions
        timeout: Maximum execution time in seconds

    Returns:
        Dictionary with execution results:
        - status: 'success', 'error', or 'timeout'
        - output: Captured stdout
        - variables: Filtered namespace after execution
        - error_type: Type of exception if error occurred
        - error_message: Error message if error occurred
        - error_lineno: Line number of error if applicable
    """
    result = {
        "status": "success",
        "output": "",
        "variables": {},
        "error_type": None,
        "error_message": None,
        "error_lineno": None,
        "partial_output": "",
    }

    try:
        # Compile code with top-level await support
        compiled_code = compile(code, "<string>", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

        # Capture stdout
        with contextlib.redirect_stdout(io.StringIO()) as f:
            # Execute code (may return coroutine for async code)
            coroutine = eval(compiled_code, namespace, namespace)
            if coroutine:
                await asyncio.wait_for(coroutine, timeout=timeout)
            partial_output = f.getvalue()

        result["output"] = partial_output or "<code ran, no output printed to stdout>"
        result["variables"] = filter_picklable(namespace)

    except TimeoutError:
        result["status"] = "timeout"
        result["error_type"] = "TimeoutError"
        result["error_message"] = f"execution exceeded {timeout}s"
        result["partial_output"] = result.get("partial_output", "")

    except (SyntaxError, IndentationError) as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error_message"] = e.msg if hasattr(e, "msg") else str(e)
        result["error_lineno"] = e.lineno if hasattr(e, "lineno") else None
        result["partial_output"] = result.get("partial_output", "")

    except (ImportError, ModuleNotFoundError) as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        # Extract module name from error message
        module_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
        result["error_message"] = f"No module named '{module_name}'"
        result["partial_output"] = result.get("partial_output", "")

    except NameError as e:
        result["status"] = "error"
        result["error_type"] = "NameError"
        # Extract variable name from error message
        var_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
        result["error_message"] = f"name '{var_name}' is not defined"
        result["partial_output"] = result.get("partial_output", "")

    except ZeroDivisionError as e:
        result["status"] = "error"
        result["error_type"] = "ZeroDivisionError"
        result["error_message"] = str(e)
        result["partial_output"] = result.get("partial_output", "")

    except (TypeError, ValueError, KeyError, IndexError, AttributeError) as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error_message"] = str(e)
        result["partial_output"] = result.get("partial_output", "")

    except Exception as e:
        result["status"] = "error"
        result["error_type"] = type(e).__name__
        result["error_message"] = str(e)
        result["partial_output"] = result.get("partial_output", "")

    return result


def build_namespace(message: dict[str, Any]) -> dict[str, Any]:
    """
    Build execution namespace from message context.

    Args:
        message: Message containing context and add_context

    Returns:
        Dictionary containing merged namespace
    """
    namespace = {}

    # Add full context if provided (first execution)
    if message.get("full_context"):
        namespace.update(message["full_context"])

    # Apply context delta if provided (subsequent executions)
    if message.get("context_delta"):
        namespace.update(message["context_delta"])

    # Inject add_context (imports, classes, functions as strings)
    if message.get("add_context"):
        add_context = message["add_context"]

        # Set File alias
        exec("File = str", namespace)

        # Handle imports
        if "imports" in add_context:
            for import_stmt in add_context["imports"]:
                try:
                    exec(import_stmt, namespace)
                except Exception:
                    # Silently skip failed imports (placeholder handling in main process)
                    pass

        # Handle classes
        if "classes" in add_context:
            for class_def in add_context["classes"]:
                try:
                    exec(class_def, namespace)
                except Exception:
                    # Silently skip failed class definitions
                    pass

        # Handle functions
        if "functions" in add_context:
            for func_def in add_context["functions"]:
                try:
                    exec(func_def, namespace)
                except Exception:
                    # Silently skip failed function definitions
                    pass

    return namespace


def main():
    """Worker process main loop."""
    try:
        # Read pickled message from stdin
        message = pickle.load(sys.stdin.buffer)

        # Check command type
        if message.get("command") != "execute":
            error_result = {
                "status": "error",
                "error_type": "ValueError",
                "error_message": f"Unknown command: {message.get('command')}",
                "output": "",
                "variables": {},
            }
            pickle.dump(error_result, sys.stdout.buffer)
            sys.stdout.buffer.flush()
            return

        # Build namespace from context
        namespace = build_namespace(message)

        # Execute code with async support
        result = asyncio.run(
            execute_code(
                message["code"],
                namespace,
                message.get("timeout", 600),
            )
        )

        # Write result to stdout
        pickle.dump(result, sys.stdout.buffer)
        sys.stdout.buffer.flush()

    except EOFError:
        # Parent closed pipe
        pass
    except Exception as e:
        # Unexpected error in worker
        error_result = {
            "status": "error",
            "error_type": "WorkerError",
            "error_message": f"Worker process error: {str(e)}",
            "output": "",
            "variables": {},
        }
        try:
            pickle.dump(error_result, sys.stdout.buffer)
            sys.stdout.buffer.flush()
        except Exception:
            # Can't even send error back, just exit
            pass


if __name__ == "__main__":
    main()
