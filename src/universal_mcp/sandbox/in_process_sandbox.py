"""
In Process Sandbox implementation
To be used for development and testing

"""

import ast
import asyncio
import contextlib
import io
from typing import Any

import cloudpickle as pickle
from loguru import logger

from universal_mcp.sandbox.sandbox import (
    DEFAULT_ERROR_HINT,
    ERROR_RECOVERY_HINTS,
    Sandbox,
    SandboxResult,
    filter_picklable,
)


class InProcessSandbox(Sandbox):
    """In-process sandbox for code execution with context persistence.

    Note: Uses a lock to serialize execution - only one code execution at a time.
    This prevents race conditions on shared namespace and stdout redirection.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lock = asyncio.Lock()
        logger.info(f"InProcessSandbox created with timeout: {self.timeout}")

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
                hints = ERROR_RECOVERY_HINTS.get("TimeoutError", DEFAULT_ERROR_HINT)
                result["error_message"] = f"TimeoutError: execution exceeded {self.timeout}s\n\n{hints}"
                logger.error(result["error_message"])

            except (SyntaxError, IndentationError) as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                error_details = f"line {e.lineno}" if hasattr(e, "lineno") and e.lineno else "unknown location"
                hints = ERROR_RECOVERY_HINTS.get(type(e).__name__, DEFAULT_ERROR_HINT)
                result[
                    "error_message"
                ] = f"{type(e).__name__} at {error_details}: {e.msg if hasattr(e, 'msg') else str(e)}\n\n{hints}"
                logger.error(result["error_message"])

            except (ImportError, ModuleNotFoundError) as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                module_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
                hints = ERROR_RECOVERY_HINTS.get(type(e).__name__, DEFAULT_ERROR_HINT)
                result["error_message"] = f"{type(e).__name__}: No module named '{module_name}'\n\n{hints}"
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
                hints = ERROR_RECOVERY_HINTS.get("NameError", DEFAULT_ERROR_HINT)
                # Add tool hint to base hint if applicable
                if tool_hint:
                    hints = hints.replace(
                        "- Ensure the variable is in scope (defined in the same or outer scope)",
                        f"- Ensure the variable is in scope (defined in the same or outer scope){tool_hint}",
                    )
                result["error_message"] = f"NameError: name '{var_name}' is not defined\n\n{hints}"
                logger.error(result["error_message"])

            except ZeroDivisionError as e:
                result["exit_code"] = 1
                result["error_type"] = "ZeroDivisionError"
                hints = ERROR_RECOVERY_HINTS.get("ZeroDivisionError", DEFAULT_ERROR_HINT)
                result["error_message"] = f"ZeroDivisionError: {str(e)}\n\n{hints}"
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
