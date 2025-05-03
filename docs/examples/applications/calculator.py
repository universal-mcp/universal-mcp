"""
Example: Creating a Custom Tool with Universal MCP

This example demonstrates how to create a custom tool using the Universal MCP framework.
The calculator application shows the basic structure needed to create your own tools.

Key Concepts:
1. Inheriting from BaseApplication
2. Implementing required methods
3. Registering tools
4. Setting up the MCP server
"""

from universal_mcp.applications import BaseApplication
from universal_mcp.servers import SingleMCPServer


class Calculator(BaseApplication):
    """A simple calculator application that demonstrates how to create custom tools.

    This class shows the basic structure needed to create your own tools:
    1. Inherit from BaseApplication
    2. Implement __init__ with name and description
    3. Define your tool methods
    4. Register tools in list_tools()

    Example usage:
        >>> app = Calculator()
        >>> app.evaluate("2 + 2")
        4
    """

    def __init__(self):
        """Initialize the calculator application.

        The name and description are used by the MCP framework to identify and describe
        your application to users and other systems.
        """
        super().__init__(name="calculator", description="A simple calculator")

    def evaluate(self, expression: str) -> int:
        """Evaluate a mathematical expression and return the result as an integer.

        This method demonstrates how to create a tool that:
        1. Takes specific input parameters
        2. Performs a well-defined operation
        3. Returns a specific type of result

        Args:
            expression (str): A string containing a valid mathematical expression.
                            Supports basic arithmetic operations (+, -, *, /, **).
                            Example: "2 + 2", "3 * 4", "10 / 2"

        Returns:
            int: The result of evaluating the expression.

        """
        return eval(expression)

    def list_tools(self) -> list[str]:
        """Register the tools that this application provides.

        This method is required by the BaseApplication class. It tells the MCP framework
        which methods should be exposed as tools. Each method listed here will be
        available for use by the MCP system.

        Returns:
            list[str]: A list of method names that should be exposed as tools.
        """
        return [self.evaluate]


# Create an instance of the calculator application
app = Calculator()

# Create an MCP server with our calculator application
mcp = SingleMCPServer(app)


def test_evaluate():
    """Test the evaluate method to ensure it works correctly.

    This demonstrates how to write tests for your tools. Good practice includes:
    1. Testing various input cases
    2. Verifying expected outputs
    3. Testing edge cases
    """
    assert app.evaluate("2 + 2") == 4
    assert app.evaluate("2 - 2") == 0
    assert app.evaluate("2 * 2") == 4
    assert app.evaluate("2 / 2") == 1
    assert app.evaluate("2 ** 2") == 4


if __name__ == "__main__":
    # Run tests to verify the calculator works
    test_evaluate()

    # Start the MCP server
    mcp.run()
