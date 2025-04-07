from e2b_code_interpreter import Sandbox
from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class E2bApp(APIApplication):
    """
    Application for interacting with the E2B secure cloud sandboxes
    to execute Python code.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="e2b", integration=integration)
        self.api_key: str | None = None

        if self.integration is not None:
            credentials = self.integration.get_credentials()

            if credentials and credentials.get("api_key"):
                self.api_key = credentials["api_key"]
                logger.info("E2B API Key successfully retrieved via integration.")
            else:
                logger.error(
                    f"Failed to retrieve E2B API Key using integration '{self.integration.name}'. "
                )
        else:
            logger.error("Integration is None. Cannot retrieve E2B API Key.")
            
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
            A string containing the formatted stdout/stderr, or a dictionary
            indicating that the API key is required.
        """
        current_api_key = None
        integration_name = "E2B" # Default name if no integration
        if self.integration:
            integration_name = self.integration.name
            credentials = self.integration.get_credentials()
            if credentials and credentials.get("api_key"):
                current_api_key = credentials["api_key"]
            else:
                logger.warning(f"API Key '{integration_name}' not found via integration.")
                return {
                    "status": "tool_error",
                    "error_type": "api_key_required",
                    "key_name": integration_name,
                    "message": f"API Key required for {self.name}. Please provide the '{integration_name}' key.",
                }
             
        self.api_key = current_api_key
        with Sandbox(api_key=self.api_key) as sandbox:
            execution = sandbox.run_code(code=code)
            result = self._format_execution_output(execution.logs)
            return result
 
    def list_tools(self):
        return [
                self.execute_python_code,
            ]        