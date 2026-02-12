"""Tests for the sandbox module - InProcessSandbox, SubprocessSandbox, and CodeSandbox."""

import pytest

from universal_mcp.sandbox.code_tool import CodeSandbox
from universal_mcp.sandbox.in_process_sandbox import InProcessSandbox
from universal_mcp.sandbox.sandbox import Sandbox, SandboxResult
from universal_mcp.sandbox.subprocess_sandbox import SubprocessSandbox

# -- Base types --------------------------------------------------------


class TestSandboxResult:
    """Tests for SandboxResult TypedDict."""

    def test_valid_result(self):
        result: SandboxResult = {
            "exit_code": 0,
            "stdout": "hello",
            "stderr": "",
            "error_type": None,
            "error_message": None,
        }
        assert result["exit_code"] == 0
        assert result["stdout"] == "hello"

    def test_error_result(self):
        result: SandboxResult = {
            "exit_code": 1,
            "stdout": "",
            "stderr": "",
            "error_type": "SyntaxError",
            "error_message": "invalid syntax",
        }
        assert result["exit_code"] == 1
        assert result["error_type"] == "SyntaxError"


class TestBaseSandbox:
    """Tests for base Sandbox class."""

    def test_default_timeout(self):
        sb = Sandbox()
        assert sb.timeout == 10

    def test_custom_timeout(self):
        sb = Sandbox(timeout=60)
        assert sb.timeout == 60

    @pytest.mark.asyncio
    async def test_run_not_implemented(self):
        sb = Sandbox()
        with pytest.raises(NotImplementedError):
            await sb.run("x = 1")


# -- InProcessSandbox -------------------------------------------------


class TestInProcessSandbox:
    """Tests for InProcessSandbox."""

    @pytest.fixture
    def sandbox(self):
        return InProcessSandbox(timeout=5)

    @pytest.mark.asyncio
    async def test_basic_print(self, sandbox):
        result = await sandbox.run('print("hello world")')
        assert result["exit_code"] == 0
        assert "hello world" in result["stdout"]

    @pytest.mark.asyncio
    async def test_variable_persistence(self, sandbox):
        await sandbox.run("x = 42")
        result = await sandbox.run("print(x)")
        assert result["exit_code"] == 0
        assert "42" in result["stdout"]

    @pytest.mark.asyncio
    async def test_import_persistence(self, sandbox):
        await sandbox.run("import math")
        result = await sandbox.run("print(math.pi)")
        assert result["exit_code"] == 0
        assert "3.14" in result["stdout"]

    @pytest.mark.asyncio
    async def test_function_persistence(self, sandbox):
        await sandbox.run("def double(n): return n * 2")
        result = await sandbox.run("print(double(5))")
        assert result["exit_code"] == 0
        assert "10" in result["stdout"]

    @pytest.mark.asyncio
    async def test_syntax_error(self, sandbox):
        result = await sandbox.run("def foo(")
        assert result["exit_code"] == 1
        assert result["error_type"] == "SyntaxError"

    @pytest.mark.asyncio
    async def test_name_error(self, sandbox):
        result = await sandbox.run("print(undefined_var)")
        assert result["exit_code"] == 1
        assert result["error_type"] == "NameError"

    @pytest.mark.asyncio
    async def test_zero_division_error(self, sandbox):
        result = await sandbox.run("1 / 0")
        assert result["exit_code"] == 1
        assert result["error_type"] == "ZeroDivisionError"

    @pytest.mark.asyncio
    async def test_type_error(self, sandbox):
        result = await sandbox.run('"hello" + 5')
        assert result["exit_code"] == 1
        assert result["error_type"] == "TypeError"

    @pytest.mark.asyncio
    async def test_no_output(self, sandbox):
        result = await sandbox.run("x = 1 + 1")
        assert result["exit_code"] == 0
        assert result["stdout"] == ""

    @pytest.mark.asyncio
    async def test_multiline_code(self, sandbox):
        code = """
results = []
for i in range(5):
    results.append(i * i)
print(results)
"""
        result = await sandbox.run(code)
        assert result["exit_code"] == 0
        assert "[0, 1, 4, 9, 16]" in result["stdout"]

    @pytest.mark.asyncio
    async def test_namespace_isolation(self):
        """Two sandbox instances should have separate namespaces."""
        sb1 = InProcessSandbox(timeout=5)
        sb2 = InProcessSandbox(timeout=5)

        await sb1.run("shared_var = 'from_sb1'")
        result = await sb2.run("print(shared_var)")
        assert result["exit_code"] == 1  # NameError - not defined in sb2

    @pytest.mark.asyncio
    async def test_import_error(self, sandbox):
        result = await sandbox.run("import nonexistent_module")
        assert result["exit_code"] != 0
        assert result["error_type"] in ["ImportError", "ModuleNotFoundError"]
        assert "Recovery" in result["error_message"]

    @pytest.mark.asyncio
    async def test_update_context_with_variable(self, sandbox):
        await sandbox.update_context({"a": 5})
        result = await sandbox.run("print(a)")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "5"

    @pytest.mark.asyncio
    async def test_update_context_with_function(self, sandbox):
        def hello():
            print("Hello World")  # noqa: T201

        await sandbox.update_context({"hello": hello})
        result = await sandbox.run("hello()")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "Hello World"

    @pytest.mark.asyncio
    async def test_update_context_with_class(self, sandbox):
        class Hello:
            def world(self):
                return "World"

        await sandbox.update_context({"Hello": Hello})
        result = await sandbox.run("print(Hello().world())")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "World"

    @pytest.mark.asyncio
    async def test_cross_persistence(self):
        """Context serialization and restoration across instances."""
        sb1 = InProcessSandbox(timeout=5)
        await sb1.run("a = 5")
        context = await sb1.get_context()

        sb2 = InProcessSandbox(timeout=5)
        await sb2.update_context(context)
        result = await sb2.run("print(a)")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "5"

    @pytest.mark.asyncio
    async def test_complex_context_preservation(self, sandbox):
        await sandbox.run("data = {'key': 'value', 'numbers': [1, 2, 3]}")
        result = await sandbox.run("print(data['key'])")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "value"

        result = await sandbox.run("print(sum(data['numbers']))")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "6"

    @pytest.mark.asyncio
    async def test_multiple_prints(self, sandbox):
        code = "print('Line 1')\nprint('Line 2')\nprint('Line 3')"
        result = await sandbox.run(code)
        assert result["exit_code"] == 0
        lines = result["stdout"].strip().split("\n")
        assert len(lines) == 3
        assert lines == ["Line 1", "Line 2", "Line 3"]

    @pytest.mark.asyncio
    async def test_async_code_execution(self, sandbox):
        code = """
async def async_func():
    return "async result"

result = await async_func()
print(result)
"""
        result = await sandbox.run(code)
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "async result"

    @pytest.mark.asyncio
    async def test_class_persistence(self, sandbox):
        code1 = """
class Calculator:
    def __init__(self, value):
        self.value = value
    def add(self, x):
        return self.value + x

calc = Calculator(10)
print(calc.add(5))
"""
        result = await sandbox.run(code1)
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "15"

        result = await sandbox.run("calc2 = Calculator(20)\nprint(calc2.add(15))")
        assert result["exit_code"] == 0
        assert result["stdout"].strip() == "35"


# -- SubprocessSandbox (parametrized from test_sandboxes.py) -----------


@pytest.fixture(
    params=[
        pytest.param("in_process", id="InProcess"),
        pytest.param("subprocess", id="Subprocess"),
    ]
)
def any_sandbox(request):
    """Create a sandbox instance - parametrized across implementations."""
    if request.param == "in_process":
        return InProcessSandbox(timeout=10)
    return SubprocessSandbox(timeout=10)


@pytest.mark.asyncio
async def test_parametrized_simple_exec(any_sandbox):
    result = await any_sandbox.run("print('Hello World')")
    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "Hello World"


@pytest.mark.asyncio
async def test_parametrized_multi_turn(any_sandbox):
    await any_sandbox.run("a = 5")
    await any_sandbox.run("b = 6")
    result = await any_sandbox.run("print(a + b)")
    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "11"


@pytest.mark.asyncio
async def test_parametrized_syntax_error(any_sandbox):
    result = await any_sandbox.run("print('Hello World'")
    assert result["exit_code"] != 0
    assert result["error_type"] in ["SyntaxError", "IndentationError"]


@pytest.mark.asyncio
async def test_parametrized_name_error(any_sandbox):
    result = await any_sandbox.run("print(undefined_variable)")
    assert result["exit_code"] != 0
    assert result["error_type"] == "NameError"


@pytest.mark.asyncio
async def test_parametrized_function_persistence(any_sandbox):
    await any_sandbox.run("def calculate_square(x): return x * x")
    result = await any_sandbox.run("print(calculate_square(7))")
    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "49"


# -- CodeSandbox -------------------------------------------------------


class TestCodeSandbox:
    """Tests for CodeSandbox (sandbox tool wrapper)."""

    @pytest.fixture
    def code_sandbox(self):
        return CodeSandbox(timeout=5)

    @pytest.mark.asyncio
    async def test_execute_code_output(self, code_sandbox):
        result = await code_sandbox.execute_code('print("hello")')
        assert "hello" in result

    @pytest.mark.asyncio
    async def test_execute_code_no_output(self, code_sandbox):
        result = await code_sandbox.execute_code("x = 42")
        assert "no output" in result.lower() or "successfully" in result.lower()

    @pytest.mark.asyncio
    async def test_execute_code_error(self, code_sandbox):
        result = await code_sandbox.execute_code("1 / 0")
        assert "Error" in result
        assert "ZeroDivisionError" in result

    @pytest.mark.asyncio
    async def test_variable_persistence(self, code_sandbox):
        await code_sandbox.execute_code("name = 'universal-mcp'")
        result = await code_sandbox.execute_code("print(name)")
        assert "universal-mcp" in result

    @pytest.mark.asyncio
    async def test_get_context_empty(self, code_sandbox):
        result = await code_sandbox.get_sandbox_context()
        assert "empty" in result.lower()

    @pytest.mark.asyncio
    async def test_get_context_with_vars(self, code_sandbox):
        await code_sandbox.execute_code("x = 42\ny = 'hello'")
        result = await code_sandbox.get_sandbox_context()
        assert "x" in result
        assert "int" in result
        assert "y" in result
        assert "str" in result

    @pytest.mark.asyncio
    async def test_reset_sandbox(self, code_sandbox):
        await code_sandbox.execute_code("x = 42")
        result = await code_sandbox.reset_sandbox()
        assert "reset" in result.lower() or "cleared" in result.lower()
        # Verify variable is gone
        result = await code_sandbox.execute_code("print(x)")
        assert "Error" in result

    def test_list_tools(self, code_sandbox):
        tools = code_sandbox.list_tools()
        assert len(tools) == 3
        names = [t.__name__ for t in tools]
        assert "execute_code" in names
        assert "get_sandbox_context" in names
        assert "reset_sandbox" in names

    def test_name(self, code_sandbox):
        assert code_sandbox.name == "sandbox"


class TestCodeSandboxFactory:
    """Tests for CodeSandbox instantiation."""

    def test_default_timeout(self):
        sb = CodeSandbox()
        assert sb._sandbox.timeout == 30

    def test_custom_timeout(self):
        sb = CodeSandbox(timeout=60)
        assert sb._sandbox.timeout == 60
