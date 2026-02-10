import builtins
import inspect
import io
import queue
import re
import socket
import threading
import types
from typing import Any, TypedDict

try:
    import cloudpickle as pickle
except ImportError:
    import pickle  # Fallback to standard pickle

from loguru import logger

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


class SandboxResult(TypedDict):
    """
    Standardized result from sandbox code execution.

    Fields:
        exit_code: 0 for success, 1 for error, 2 for timeout
        stdout: Standard output from code execution
        stderr: Standard error from code execution
        error_type: Type of error if exit_code != 0 (e.g., "SyntaxError", "TimeoutError")
        error_message: Detailed error message with hints for recovery
    """

    exit_code: int
    stdout: str
    stderr: str
    error_type: str | None
    error_message: str | None


# Global error hints map for consistent error messages across all sandbox implementations
ERROR_RECOVERY_HINTS = {
    "SyntaxError": """Recovery checklist:
- Verify all parentheses (), brackets [], and braces {} are properly matched
- Check indentation consistency (use 4 spaces per level)
- Ensure colons ':' are present after function/class definitions and control statements
- Confirm 'async def' is used for ALL function definitions (not 'def')
- Check for missing commas in lists, dictionaries, or function arguments
- Verify string quotes are properly closed""",
    "IndentationError": """Recovery checklist:
- Check indentation consistency (use 4 spaces per level)
- Ensure all blocks are properly indented
- Verify no mixing of tabs and spaces""",
    "ImportError": """Recovery suggestions:
- Verify the module name is spelled correctly
- Only standard library modules and pandas are pre-installed
- If this is a tool function, search for it using search_functions first
- Then load the tool using load_functions before using it in code
- For pandas Excel support, use engines 'calamine' (Excel) or 'pyarrow' (CSV)
- Consider using preloaded functions or search for external tools instead""",
    "ModuleNotFoundError": """Recovery suggestions:
- Verify the module name is spelled correctly
- Only standard library modules and pandas are pre-installed
- If this is a tool function, search for it using search_functions first
- Then load the tool using load_functions before using it in code""",
    "NameError": """Recovery suggestions:
- Check if the variable/function is defined before using it
- Verify there are no typos in the variable/function name
- Ensure the variable is in scope (defined in the same or outer scope)
- If from a previous execution, verify it was actually assigned (not just printed)
- Check that any required imports are present""",
    "ZeroDivisionError": """Recovery suggestions:
- Add a check to ensure the divisor is not zero before division
- Use a conditional: 'if denominator != 0: result = numerator / denominator'
- Consider using try-except for this specific operation if zero is expected
- Review the logic that produces the divisor to understand why it's zero""",
    "TypeError": """Recovery suggestions:
- Verify function arguments match expected types and count
- Check if you're calling a non-callable object
- Ensure async functions are called with 'await'
- Confirm operators are used with compatible types (e.g., can't add string + int)""",
    "ValueError": """Recovery suggestions:
- Check if input values are in the expected range or format
- Verify string-to-number conversions have valid input
- Ensure unpacking matches the number of values (e.g., 'a, b = [1, 2]')""",
    "KeyError": """Recovery suggestions:
- Verify the dictionary key exists before accessing (use 'key in dict' or 'dict.get(key)')
- Check for typos in key names
- Use smart_print() to examine the dictionary structure first
- Consider using 'dict.get(key, default_value)' for safer access""",
    "IndexError": """Recovery suggestions:
- Verify list/array indices are within bounds (0 to len-1)
- Check if the list is empty before accessing
- Use 'if len(list) > index:' before accessing
- Consider using slicing with safety: 'list[:10]' instead of 'list[10]'""",
    "AttributeError": """Recovery suggestions:
- Check if the object has the attribute you're accessing
- Use smart_print() to examine the object structure first
- Verify the object is of the expected type
- Check if the object is None when it shouldn't be""",
    "TimeoutError": """Recovery suggestions:
- Break the task into smaller, independent steps
- Check for infinite loops (e.g., 'while True' without break condition)
- Use async/await for I/O-bound operations to avoid blocking
- For long computations, consider optimizing the algorithm
- Review any loops to ensure they have proper termination conditions""",
}

DEFAULT_ERROR_HINT = """Recovery suggestions:
- Review the error message carefully for clues
- Break down the code into smaller steps to isolate the issue
- Use smart_print() to examine intermediate values"""


def filter_picklable(
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

    return filtered


class Sandbox:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.namespace = {}

    async def run(self, code: str) -> SandboxResult:
        raise NotImplementedError

    async def get_context(self) -> str:
        """
        Extract the current namespace variables from the sandbox.

        Returns:
            Base64-encoded pickled dict of variables
        """
        import base64

        filtered_vars = filter_picklable(self.namespace)
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
        import base64

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
