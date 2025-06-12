import datetime

from universal_mcp.applications.application import BaseApplication


class SampleToolApp(BaseApplication):
    """A sample application providing basic utility tools."""

    def __init__(self):
        """Initializes the SampleToolApp with the name 'sample_tool_app'."""
        super().__init__("sample_tool_app")

    def get_current_time(self):
        """Get the current system time as a formatted string.

        Returns:
            str: The current time in the format 'YYYY-MM-DD HH:MM:SS'.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_current_date(self):
        """Get the current system date as a formatted string.

        Returns:
            str: The current date in the format 'YYYY-MM-DD'.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def calculate(self, expression: str):
        """Safely evaluate a mathematical expression.

        Args:
            expression (str): The mathematical expression to evaluate.

        Returns:
            str: The result of the calculation, or an error message if evaluation fails.
        """
        try:
            # Safe evaluation of mathematical expressions
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    def file_operations(self, operation: str, filename: str, content: str = ""):
        """Perform file read or write operations.

        Args:
            operation (str): The operation to perform, either 'read' or 'write'.
            filename (str): The name of the file to operate on.
            content (str, optional): The content to write to the file (used only for 'write'). Defaults to "".

        Returns:
            str: The result of the file operation, or an error message if the operation fails.
        """
        try:
            if operation == "read":
                with open(filename) as f:
                    return f"File content:\n{f.read()}"
            elif operation == "write":
                with open(filename, "w") as f:
                    f.write(content)
                return f"Successfully wrote to {filename}"
            else:
                return "Invalid operation. Use 'read' or 'write'"
        except Exception as e:
            return f"File operation error: {str(e)}"

    def list_tools(self):
        """List all available tool methods in this application.

        Returns:
            list: A list of callable tool methods.
        """
        return [
            self.get_current_time,
            self.get_current_date,
            self.calculate,
            self.file_operations,
        ]
