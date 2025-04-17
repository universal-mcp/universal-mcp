from typing import Annotated

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
                f"Invalid credential format received for E2B API Key via integration '{self.integration.name}'. "
            )
        api_key = (
            credentials.get("api_key")
            or credentials.get("API_KEY")
            or credentials.get("apiKey")
        )
        if not api_key:
            raise ValueError(
                f"Invalid credential format received for E2B API Key via integration '{self.integration.name}'. "
            )
        self.api_key = api_key
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

    def execute_python_code(
        self, code: Annotated[str, "The Python code to execute."]
    ) -> str:
        """
        Executes Python code within a secure E2B cloud sandbox.

        Args:
            code: The string containing the Python code to execute.

        Returns:
            A string containing the formatted standard output (stdout) and standard error (stderr)
            from the execution. If an error occurs during setup or execution, an
            error message string is returned.

        Raises:
            NotAuthorizedError: If the API key is not set.
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
