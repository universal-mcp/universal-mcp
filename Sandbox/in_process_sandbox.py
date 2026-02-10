"""
In Process Sandbox implementation
To be used for development and testing

"""

import ast
import asyncio
import base64
import builtins
import contextlib
import inspect
import io
import queue
import re
import socket
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


class InProcessSandbox(Sandbox):
    """In-process sandbox for code execution with context persistence.

    Note: Uses a lock to serialize execution - only one code execution at a time.
    This prevents race conditions on shared namespace and stdout redirection.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.namespace = {}
        self._lock = asyncio.Lock()
        logger.info(f"InProcessSandbox created with timeout: {self.timeout}")

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
        Execute Python code in the sandbox with timeout.

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

            try:
                # Compile code with top-level await support
                compiled_code = compile(code, "<string>", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

                # Capture stdout
                with contextlib.redirect_stdout(io.StringIO()) as f:
                    # Execute code (may return coroutine for async code)
                    coroutine = eval(compiled_code, self.namespace, self.namespace)
                    if coroutine:
                        await asyncio.wait_for(coroutine, timeout=self.timeout)
                    result["stdout"] = f.getvalue()

            except TimeoutError:
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

            except (SyntaxError, IndentationError) as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                error_details = f"line {e.lineno}" if hasattr(e, "lineno") and e.lineno else "unknown location"
                result[
                    "error_message"
                ] = f"""{type(e).__name__} at {error_details}: {e.msg if hasattr(e, "msg") else str(e)}

Recovery checklist:
- Verify all parentheses (), brackets [], and braces {{}} are properly matched
- Check indentation consistency (use 4 spaces per level)
- Ensure colons ':' are present after function/class definitions and control statements
- Confirm 'async def' is used for ALL function definitions (not 'def')
- Check for missing commas in lists, dictionaries, or function arguments
- Verify string quotes are properly closed"""
                logger.error(result["error_message"])

            except (ImportError, ModuleNotFoundError) as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                module_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
                result["error_message"] = f"""{type(e).__name__}: No module named '{module_name}'

Recovery suggestions:
- Verify the module name is spelled correctly
- Only standard library modules and pandas are pre-installed
- If this is a tool function, search for it using search_functions first
- Then load the tool using load_functions before using it in code
- For pandas Excel support, use engines 'calamine' (Excel) or 'pyarrow' (CSV)
- Consider using preloaded functions or search for external tools instead"""
                logger.error(result["error_message"])

            except NameError as e:
                result["exit_code"] = 1
                result["error_type"] = "NameError"
                var_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
                is_tool = "__" in var_name
                tool_hint = (
                    "\n- This looks like a tool function. Use search_functions to find it, then load_functions to load it"
                    if is_tool
                    else ""
                )
                result["error_message"] = f"""NameError: name '{var_name}' is not defined

Recovery suggestions:
- Check if the variable/function is defined before using it
- Verify there are no typos in the variable/function name
- Ensure the variable is in scope (defined in the same or outer scope){tool_hint}
- If from a previous execution, verify it was actually assigned (not just printed)
- Check that any required imports are present"""
                logger.error(result["error_message"])

            except ZeroDivisionError as e:
                result["exit_code"] = 1
                result["error_type"] = "ZeroDivisionError"
                result["error_message"] = f"""ZeroDivisionError: {str(e)}

Recovery suggestions:
- Add a check to ensure the divisor is not zero before division
- Use a conditional: 'if denominator != 0: result = numerator / denominator'
- Consider using try-except for this specific operation if zero is expected
- Review the logic that produces the divisor to understand why it's zero"""
                logger.error(result["error_message"])

            except (TypeError, ValueError, KeyError, IndexError, AttributeError) as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                result["error_message"] = f"""{type(e).__name__}: {str(e)}

{ERROR_RECOVERY_HINTS.get(type(e).__name__, DEFAULT_ERROR_HINT)}"""
                logger.error(result["error_message"])

            except Exception as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                result["error_message"] = f"""Unexpected {type(e).__name__}: {str(e)}

This is an unexpected error. Consider:
- Review the error message carefully for clues
- Break down the code into smaller steps to isolate the issue
- Use smart_print() to examine intermediate values
- Check if this is a known limitation of the sandbox environment"""
                logger.error(result["error_message"])

            logger.info(f"Run result: exit_code={result['exit_code']} stdout_len={len(result['stdout'])}")

            return result

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
