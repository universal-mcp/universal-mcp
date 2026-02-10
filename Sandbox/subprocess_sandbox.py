"""
Subprocess Sandbox implementation
Uses subprocess isolation for safer code execution
"""

import asyncio
import base64
import builtins
import inspect
import io
import queue
import re
import socket
import subprocess
import sys
import threading
import types
from typing import Any

import cloudpickle as pickle
from loguru import logger

from universal_mcp.agents.Sandbox.sandbox import (
    DEFAULT_ERROR_HINT,
    ERROR_RECOVERY_HINTS,
    Sandbox,
    SandboxResult,
)

# Exclude types that cannot be pickled or are system types
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


class SubprocessSandbox(Sandbox):
    """Subprocess-based sandbox for isolated code execution with context persistence.

    Note: Uses a lock to serialize execution - only one code execution at a time.
    This prevents race conditions on shared namespace.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.namespace = {}  # Store picklable context between runs
        self._lock = asyncio.Lock()
        logger.info(f"SubprocessSandbox created with timeout: {self.timeout}")

    def _filter_picklable(
        self,
        namespace: dict[str, Any],
        exclude_names: set[str] | None = None,
        exclude_prefixes: tuple[str, ...] | None = None,
        exclude_callables: bool = False,
    ) -> dict[str, Any]:
        """
        Filter namespace to only include picklable user-defined variables and functions.

        Excludes:
        - Dunder variables (__xxx__)
        - Built-in functions and types
        - Running coroutines and async generator instances (not picklable)
        - Unpicklable types (modules, locks, sockets, etc.)
        - Optional: names in exclude_names set
        - Optional: names starting with exclude_prefixes
        - Optional: all callables (if exclude_callables=True)

        Includes:
        - Async function definitions (async def) - these ARE picklable with cloudpickle

        Args:
            namespace: Dictionary of variables from execution
            exclude_names: Additional names to exclude (e.g., tool function names)
            exclude_prefixes: Prefixes to exclude (e.g., ("llm__", "google_mail__"))
            exclude_callables: If True, exclude ALL callable objects

        Returns:
            Dictionary containing only picklable user-defined variables and functions
        """
        exclude_names = exclude_names or set()
        exclude_prefixes = exclude_prefixes or ()

        filtered = {}
        for key, value in namespace.items():
            # Skip private/dunder variables
            if key.startswith("__"):
                continue

            # Skip built-in names
            if key in BUILTIN_NAMES:
                continue

            # Skip additional excluded names
            if key in exclude_names:
                continue

            # Skip names with excluded prefixes
            if any(key.startswith(prefix) for prefix in exclude_prefixes):
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

            # Optionally skip all callables (for msgpack compatibility)
            if exclude_callables and callable(value):
                continue

            # Try to pickle everything else (cloudpickle can handle user-defined functions/classes)
            try:
                pickle.dumps(value)
                filtered[key] = value
            except Exception:
                # Skip unpicklable objects
                logger.warning(f"Unpicklable object: {key}")
                pass

        return filtered

    async def run(self, code: str) -> SandboxResult:
        """
        Execute Python code in a subprocess with timeout and lock.

        Uses a lock to serialize execution, preventing race conditions when
        multiple parallel calls attempt to execute code simultaneously.

        Args:
            code: Python code to execute

        Returns:
            SandboxResult with exit_code, stdout, stderr, error_type, and error_message
        """
        async with self._lock:
            result: SandboxResult = {
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
                "error_type": None,
                "error_message": None,
            }

            # Prepare message for worker
            message = {
                "command": "execute",
                "code": code,
                "full_context": self.namespace,  # Use namespace instead of context
                "context_delta": None,
                "timeout": self.timeout,
            }

            try:
                # Spawn subprocess worker
                process = subprocess.Popen(
                    [sys.executable, "-m", "universal_mcp.agents.Sandbox.sandbox_worker"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Serialize and send message
                message_data = pickle.dumps(message)

                # Communicate with timeout (add buffer to subprocess timeout)
                try:
                    stdout_data, stderr_data = process.communicate(input=message_data, timeout=self.timeout + 10)
                except subprocess.TimeoutExpired:
                    # Kill the process if it times out
                    process.kill()
                    process.wait()
                    result["exit_code"] = 2
                    result["error_type"] = "TimeoutError"
                    result["error_message"] = f"""TimeoutError: execution exceeded {self.timeout}s

Recovery suggestions:
- Break the task into smaller, independent steps
- Check for infinite loops (e.g., 'while True' without break condition)
- Use async/await for I/O-bound operations to avoid blocking
- For long computations, consider optimizing the algorithm
- Review any loops to ensure they have proper termination conditions"""
                    logger.error(result["error_message"])
                    return result

                # Deserialize result
                try:
                    worker_result = pickle.loads(stdout_data)
                except Exception as e:
                    result["exit_code"] = 1
                    result["error_type"] = "DeserializationError"
                    result["error_message"] = f"""Failed to deserialize subprocess result: {e}

This indicates a problem with the sandbox subprocess. Consider:
- Check if the worker module is available
- Review system logs for process errors
- Try breaking down the code into smaller parts"""
                    logger.error(result["error_message"])
                    return result

                # Handle execution result from worker
                if worker_result["status"] == "success":
                    result["stdout"] = worker_result["output"]
                    # Update namespace with new variables
                    if worker_result.get("variables"):
                        self.namespace.update(worker_result["variables"])

                elif worker_result["status"] == "timeout":
                    result["exit_code"] = 2
                    result["error_type"] = "TimeoutError"
                    result["error_message"] = f"""TimeoutError: execution exceeded {self.timeout}s

Recovery suggestions:
- Break the task into smaller, independent steps
- Check for infinite loops (e.g., 'while True' without break condition)
- Use async/await for I/O-bound operations to avoid blocking
- For long computations, consider optimizing the algorithm
- Review any loops to ensure they have proper termination conditions"""

                elif worker_result["status"] == "error":
                    result["exit_code"] = 1
                    result["error_type"] = worker_result.get("error_type", "Exception")
                    error_message = worker_result.get("error_message", "Unknown error")
                    error_lineno = worker_result.get("error_lineno")

                    # Add line number if available
                    error_prefix = (
                        f"{result['error_type']} at line {error_lineno}: {error_message}"
                        if error_lineno
                        else f"{result['error_type']}: {error_message}"
                    )

                    # Add recovery hints based on error type
                    hints = self._get_error_hints(result["error_type"])
                    result["error_message"] = f"{error_prefix}\n\n{hints}"

                else:
                    result["exit_code"] = 1
                    result["error_type"] = "UnknownStatus"
                    result["error_message"] = f"Unknown execution status: {worker_result['status']}"

            except Exception as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                result["error_message"] = f"""Subprocess execution failed: {type(e).__name__}: {str(e)}

This indicates a problem with the sandbox subprocess. Consider:
- Check if the worker module is available
- Review system logs for process errors
- Try breaking down the code into smaller parts"""
                logger.error(result["error_message"])

            logger.info(f"Run result: exit_code={result['exit_code']} stdout_len={len(result['stdout'])}")
            return result

    def _get_error_hints(self, error_type: str) -> str:
        """Get recovery hints for specific error types."""
        return ERROR_RECOVERY_HINTS.get(error_type, DEFAULT_ERROR_HINT)

    async def get_context(self) -> str:
        """
        Extract the current namespace variables from the sandbox.

        Returns:
            Base64-encoded pickled dict of variables
        """
        filtered_vars = self._filter_picklable(self.namespace)
        serialized = base64.b64encode(pickle.dumps(filtered_vars)).decode("utf-8")
        logger.info(f"Getting context: {len(filtered_vars)} picklable vars")
        return serialized

    async def update_context(self, context: str | dict[str, Any]):
        """
        Update the namespace with variables.

        Args:
            context: Can be:
                - str: serialized picklable context (base64-encoded pickle)
                - dict: variables to add to namespace directly
        """
        if not context:
            return

        # If context is a string, it's serialized picklable context
        if isinstance(context, str):
            try:
                pickled_vars = base64.b64decode(context)
                vars_dict = pickle.loads(pickled_vars)
                self.namespace.update(vars_dict)
                logger.info(f"Updated context with {len(vars_dict)} variables")
            except Exception as e:
                logger.error(f"Error deserializing context: {e}")

        # If context is a dict, use it directly
        else:
            self.namespace.update(context)
            logger.info(f"Updated context with {len(context)} variables")
