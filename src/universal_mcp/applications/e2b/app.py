from e2b_code_interpreter import Sandbox
from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class E2BApp(APIApplication):
    """
    Application for interacting with the E2B secure cloud sandboxes
    to execute Python code.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="e2b", integration=integration)
        self.api_key: str | None = None

    def _set_api_key(self):
        if self.api_key:
            return

        if not self.integration:
            raise ValueError("Integration is None. Cannot retrieve E2B API Key.")

        credentials = self.integration.get_credentials()
        if not credentials:
            raise ValueError(
                f"Failed to retrieve E2B API Key using integration '{self.integration.name}'. "
                f"Check store configuration (e.g., ensure the correct environment variable is set)."
            )

        self.api_key = credentials
        logger.info("E2B API Key successfully retrieved via integration.")

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

    def execute_python_code(self, code: str) -> str:
        """
        Executes Python code within a secure E2B cloud sandbox.

        Args:
            code: The string containing the Python code to execute.

        Returns:
            A string containing the formatted standard output (stdout) and standard error (stderr)
            from the execution. If an error occurs during setup or execution, an
            error message string is returned.
        """
        self._set_api_key()
        with Sandbox(api_key=self.api_key) as sandbox:
            execution = sandbox.run_code(code=code)
            result = self._format_execution_output(execution.logs)
            return result

    def list_tools(self):
        return [
            self.execute_python_code,
        ]
