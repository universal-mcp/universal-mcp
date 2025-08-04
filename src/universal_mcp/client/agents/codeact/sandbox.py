import builtins
import contextlib
import io
from typing import Any


def eval_unsafe(code: str, _locals: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    # Store original keys before execution
    original_keys = set(_locals.keys())
    result = f"Executing code...\n{code}\n\nOutput:\n"
    result += "=" * 50 + "\n"
    try:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            # Execute the code in the provided locals context
            # Using exec to allow dynamic code execution
            # This is a simplified version; in production, consider security implications
            exec(code, builtins.__dict__, _locals)
        result += f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
    except Exception as e:
        result += f"Error during execution: {repr(e)}"

    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    return result, new_vars
