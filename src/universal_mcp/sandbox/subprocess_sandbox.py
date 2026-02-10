"""
Subprocess Sandbox implementation
Uses subprocess isolation for safer code execution
"""

import asyncio
import subprocess
import sys

import cloudpickle as pickle
from loguru import logger

from universal_mcp.sandbox.sandbox import (
    DEFAULT_ERROR_HINT,
    ERROR_RECOVERY_HINTS,
    Sandbox,
    SandboxResult,
)


class SubprocessSandbox(Sandbox):
    """Subprocess-based sandbox for isolated code execution with context persistence.

    Note: Uses a lock to serialize execution - only one code execution at a time.
    This prevents race conditions on shared namespace.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lock = asyncio.Lock()
        logger.info(f"SubprocessSandbox created with timeout: {self.timeout}")

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
                    [sys.executable, "-m", "universal_mcp.sandbox.sandbox_worker"],
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
                    hints = ERROR_RECOVERY_HINTS.get("TimeoutError", DEFAULT_ERROR_HINT)
                    result["error_message"] = f"TimeoutError: execution exceeded {self.timeout}s\n\n{hints}"
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
                    hints = ERROR_RECOVERY_HINTS.get("TimeoutError", DEFAULT_ERROR_HINT)
                    result["error_message"] = f"TimeoutError: execution exceeded {self.timeout}s\n\n{hints}"

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
