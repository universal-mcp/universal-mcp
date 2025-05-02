from universal_mcp.applications import BaseApplication
from universal_mcp.servers import SingleMCPServer


class Calculator(BaseApplication):
    def __init__(self):
        super().__init__(name="calculator", description="A simple calculator")

    def evaluate(self, expression: str) -> int:
        """Evaluate a mathematical expression and return the result as an integer.

        Args:
            expression (str): A string containing a valid mathematical expression.
                            Supports basic arithmetic operations (+, -, *, /, **).

        Returns:
            int: The result of evaluating the expression.
        """
        return eval(expression)

    def list_tools(self) -> list[str]:
        return [self.evaluate]


app = Calculator()
mcp = SingleMCPServer(app)


def test_evaluate():
    assert app.evaluate("2 + 2") == 4
    assert app.evaluate("2 - 2") == 0
    assert app.evaluate("2 * 2") == 4
    assert app.evaluate("2 / 2") == 1
    assert app.evaluate("2 ** 2") == 4


if __name__ == "__main__":
    test_evaluate()
    mcp.run()
