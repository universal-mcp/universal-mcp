"""Code mode tool - exposes a Python REPL sandbox as MCP tools.

The code sandbox allows AI agents to execute arbitrary Python code in a
persistent REPL environment. Variables, functions, and imports survive
across calls, enabling iterative development and data analysis workflows.
"""

from universal_mcp.sandbox.in_process_sandbox import InProcessSandbox


class CodeSandbox:
    """Python REPL sandbox exposed as MCP tools.

    Provides execute_code, get_sandbox_context, and reset_sandbox as
    tool functions that can be registered with the LocalRegistry.
    """

    def __init__(self, timeout: int = 30) -> None:
        self.name = "sandbox"
        self._sandbox = InProcessSandbox(timeout=timeout)

    async def execute_code(self, code: str) -> str:
        """Execute Python code in a persistent sandbox environment.

        The sandbox maintains state between calls - variables, functions,
        imports, and class definitions persist across executions. Use print()
        to produce output.

        Args:
            code: Python code to execute. Supports top-level await for async code.

        Returns:
            stdout output from execution, or error details if execution failed.

        Tags: important, sandbox, code
        """
        result = await self._sandbox.run(code)

        if result["exit_code"] == 0:
            output = result["stdout"]
            return output if output else "(code executed successfully, no output)"
        else:
            error_type = result.get("error_type", "Error")
            error_message = result.get("error_message", "Unknown error")
            return f"Error ({error_type}): {error_message}"

    async def get_sandbox_context(self) -> str:
        """Get the current sandbox state showing defined variables and their types.

        Returns a summary of all variables currently in the sandbox namespace.
        Useful for understanding what state is available from previous executions.

        Returns:
            Summary of sandbox variables and their types.

        Tags: sandbox, code
        """
        namespace = self._sandbox.namespace
        if not namespace:
            return "Sandbox is empty - no variables defined."

        lines = ["Current sandbox variables:"]
        for key, value in sorted(namespace.items()):
            if key.startswith("__"):
                continue
            type_name = type(value).__name__
            # Show a preview for simple types
            preview = ""
            try:
                repr_val = repr(value)
                if len(repr_val) <= 80:
                    preview = f" = {repr_val}"
                else:
                    preview = f" = {repr_val[:77]}..."
            except Exception:
                pass
            lines.append(f"  {key}: {type_name}{preview}")

        return "\n".join(lines)

    async def reset_sandbox(self) -> str:
        """Reset the sandbox, clearing all variables and state.

        This removes all defined variables, functions, and imports from
        the sandbox namespace, giving you a clean slate.

        Returns:
            Confirmation message.

        Tags: sandbox, code
        """
        self._sandbox.namespace.clear()
        return "Sandbox reset - all variables and state cleared."

    def list_tools(self) -> list:
        """Return the list of tool functions for registration."""
        return [self.execute_code, self.get_sandbox_context, self.reset_sandbox]


def create_code_sandbox(timeout: int = 30) -> CodeSandbox:
    """Create a CodeSandbox instance.

    Args:
        timeout: Maximum execution time per code block in seconds.

    Returns:
        Configured CodeSandbox instance.
    """
    return CodeSandbox(timeout=timeout)
