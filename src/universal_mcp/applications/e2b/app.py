from typing import Annotated

from e2b_code_interpreter import Sandbox

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class E2BApp(APIApplication):
    """
    Application for interacting with the E2B secure cloud sandboxes
    to execute Python code.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="e2b", integration=integration)

    def _format_execution_output(self, logs) -> str:
        """Helper function to format the E2B execution logs nicely."""
        output_parts = []

        if logs.stdout:
            stdout_content = "".join(logs.stdout).strip()
            if stdout_content:
                output_parts.append(f"\n{stdout_content}")

        if logs.stderr:
            stderr_content = "".join(logs.stderr).strip()
            if stderr_content:
                output_parts.append(f"--- ERROR ---\n{stderr_content}")

        if not output_parts:
            return "Execution finished with no output (stdout/stderr)."
        return "\n\n".join(output_parts)

    def execute_python_code(
        self, code: Annotated[str, "The Python code to execute."]
    ) -> str:
        """
        Executes Python code in a sandbox environment and returns the formatted output

        Args:
            code: String containing the Python code to be executed in the sandbox

        Returns:
            A string containing the formatted execution output/logs from running the code

        Raises:
            SandboxError: When there are issues with sandbox initialization or code execution
            AuthenticationError: When API key authentication fails during sandbox setup
            ValueError: When provided code string is empty or invalid

        Tags:
            execute, sandbox, code-execution, security, important
        """
        api_key = self.integration.get_credentials().get("api_key")
        with Sandbox(api_key=api_key) as sandbox:
            execution = sandbox.run_code(code=code)
            result = self._format_execution_output(execution.logs)
            return result

    def list_tools(self):
        return [
            self.execute_python_code,
        ]
