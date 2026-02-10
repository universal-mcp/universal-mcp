"""
E2B Sandbox implementation
To be used for production

Note: E2B is a cloud-based sandbox. Context is managed remotely in the E2B environment.
The namespace attribute is not used since execution happens in a remote Python kernel.
"""

import asyncio
import base64
from typing import Any

import cloudpickle as pickle
from e2b_code_interpreter import Sandbox as e2b_sandbox
from loguru import logger

from universal_mcp.agents.Sandbox.sandbox import Sandbox, SandboxResult


def get_user_defined_locals():
    return {k: v for k, v in globals().items() if not k.startswith("_")}


class E2BSandbox(Sandbox):
    """E2B cloud-based sandbox with context persistence.

    Note: Uses a lock to serialize execution - only one code execution at a time.
    This prevents race conditions when multiple parallel calls occur.
    Context is managed remotely in the E2B Python kernel.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = asyncio.Lock()
        self.sbx = e2b_sandbox.create(timeout=self.timeout)
        self.sbx.commands.run("pip install cloudpickle")
        logger.info(f"E2B Sandbox created with timeout: id {self.sbx.sandbox_id}, timeout {self.timeout}")

    def __del__(self):
        if hasattr(self, "sandbox"):
            self.sbx.kill()
            del self.sbx

    async def get_context(self):
        """
        Extract the current namespace variables from the sandbox.
        Returns a base64-encoded pickled dict of all picklable user variables.
        """
        code = """
from cloudpickle import pickle
import base64

# Known IPython/E2B built-ins to exclude
EXCLUDE_VARS = {
    'In', 'Out', 'get_ipython', 'exit', 'quit', 'open', 'pandas', 'Figure',
    'IPython', 'BaseFormatter', 'JSONFormatter', 'Unicode', 'ObjectName',
    'chart_figure_to_dict', 'orjson', 'E2BDataFormatter', 'E2BChartFormatter',
    'E2BJSONFormatter', 'ip', 'Any', 'display', 'Image', 'UnixViewer',
    'show_file', 'original_save', 'save', 'os'
}

# Get all variables from globals, excluding built-ins and IPython internals
_vars = {}
for k, v in globals().items():
    if k.startswith('_'):
        continue
    if k in EXCLUDE_VARS:
        continue
    # Try to pickle each variable individually
    try:
        pickle.dumps(v)
        _vars[k] = v
    except:
        pass  # Skip unpicklable objects

_serialized = base64.b64encode(pickle.dumps(_vars)).decode('utf-8')
print(_serialized)
"""
        stdout, stderr = await self.run(code)
        if stderr:
            raise RuntimeError(f"Error getting context: {stderr}")
        return stdout.strip()

    async def update_context(self, context: str | dict[str, Any]):
        """
        Send variables to the kernel namespace using pickle.

        Args:
            context: Either a serialized context string (from get_context())
                    or a dict of variables to add to the namespace
        """
        if not context:
            return

        # If context is a string, it's already serialized from get_context()
        if isinstance(context, str):
            pickled_vars = context
        else:
            # If context is a dict, serialize it
            pickled_vars = base64.b64encode(pickle.dumps(context)).decode()
        logger.info(f"Updating context: {pickled_vars}")
        code = f"""
print("Updating context")
from cloudpickle import pickle
import base64
print("Imported pickle, base64")
pickled = base64.b64decode('{pickled_vars}')
print("Decoded pickled")
vars_dict = pickle.loads(pickled)
print("Vars dict: ", vars_dict)
globals().update(vars_dict)
"""
        await self.run(code)

    async def run(self, code: str) -> SandboxResult:
        """
        Execute Python code in E2B cloud sandbox with lock.

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
                # Not sure if e2b supports async
                exec_result = self.sbx.run_code(code)

                # Extract stdout and stderr
                result["stdout"] = "\n".join(exec_result.logs.stdout)
                stderr_output = "\n".join(exec_result.logs.stderr)

                # Check if there was an error
                if exec_result.error:
                    result["exit_code"] = 1
                    result["error_type"] = (
                        exec_result.error.name if hasattr(exec_result.error, "name") else "ExecutionError"
                    )
                    result["error_message"] = (
                        f"{result['error_type']}: {exec_result.error.value if hasattr(exec_result.error, 'value') else str(exec_result.error)}"
                    )

                    # Add stderr if present
                    if stderr_output:
                        result["stderr"] = stderr_output

                elif stderr_output:
                    # If there's stderr but no error, still include it
                    result["stderr"] = stderr_output

                logger.info(f"Run result: exit_code={result['exit_code']} stdout_len={len(result['stdout'])}")

            except Exception as e:
                result["exit_code"] = 1
                result["error_type"] = type(e).__name__
                result["error_message"] = f"""E2B execution failed: {type(e).__name__}: {str(e)}

This indicates a problem with the E2B sandbox. Consider:
- Check if the E2B API key is valid
- Verify network connectivity to E2B services
- Review E2B service status
- Try breaking down the code into smaller parts"""
                logger.error(result["error_message"])

            return result
