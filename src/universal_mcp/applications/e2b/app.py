
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
                # This typically means the environment variable was not set or accessible.
                logger.error(
                    f"Failed to retrieve E2B API Key using integration '{self.integration.name}'. "
                    f"Check store configuration (e.g., ensure the correct environment variable is set)."
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


    def execute_python_code(self, code: str) -> str | dict: # Return type can now be dict
        """
        Executes Python code within a secure E2B cloud sandbox.

        Args:
            code: The string containing the Python code to execute.

        Returns:
            A string containing the formatted stdout/stderr, or a dictionary
            indicating that the API key is required.
        """
        # --- ADD THIS CHECK AT THE BEGINNING ---
        current_api_key = None
        integration_name = "E2B" # Default name if no integration
        if self.integration:
            integration_name = self.integration.name
            try:
                credentials = self.integration.get_credentials()
                if credentials and credentials.get("api_key"):
                    current_api_key = credentials["api_key"]
                else:
                    # Key is missing from the store (keyring)
                    logger.warning(f"API Key '{integration_name}' not found via integration.")
                    return {
                        "status": "tool_error",
                        "error_type": "api_key_required",
                        "key_name": integration_name,
                        "message": f"API Key required for {self.name}. Please provide the '{integration_name}' key.",
                    }
            except Exception as e:
                 # Handle potential errors during credential retrieval (e.g., keyring issues)
                 logger.error(f"Error getting credentials for {integration_name}: {e}")
                 return {
                        "status": "tool_error",
                        "error_type": "credential_error",
                        "key_name": integration_name,
                        "message": f"Error retrieving credentials for {integration_name}: {e}",
                    }
        else:
             # Integration itself wasn't configured for the app
             logger.error("E2B integration is not configured for this application.")
             return {
                 "status": "tool_error",
                 "error_type": "configuration_error",
                 "key_name": None,
                 "message": "E2B integration is not configured. Cannot execute code.",
             }

        # If we reached here, the key was found
        self.api_key = current_api_key

        # Original logic proceeds now, using self.api_key which is guaranteed to be set
        try:
            with Sandbox(api_key=self.api_key) as sandbox:
                execution = sandbox.run_code(code=code)
                result = self._format_execution_output(execution.logs)
                return result
        except Exception as e:
            logger.error(f"Error during E2B sandbox execution: {e}")
            return f"Error during code execution: {e}" # Return execution error string

    def list_tools(self):
        return [
                self.execute_python_code,
            ]
        