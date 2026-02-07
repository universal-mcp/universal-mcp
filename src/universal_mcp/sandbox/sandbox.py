from typing import TypedDict


class SandboxResult(TypedDict):
    """
    Standardized result from sandbox code execution.

    Fields:
        exit_code: 0 for success, 1 for error, 2 for timeout
        stdout: Standard output from code execution
        stderr: Standard error from code execution
        error_type: Type of error if exit_code != 0 (e.g., "SyntaxError", "TimeoutError")
        error_message: Detailed error message with hints for recovery
    """

    exit_code: int
    stdout: str
    stderr: str
    error_type: str | None
    error_message: str | None


# Global error hints map for consistent error messages across all sandbox implementations
ERROR_RECOVERY_HINTS = {
    "SyntaxError": """Recovery checklist:
- Verify all parentheses (), brackets [], and braces {} are properly matched
- Check indentation consistency (use 4 spaces per level)
- Ensure colons ':' are present after function/class definitions and control statements
- Confirm 'async def' is used for ALL function definitions (not 'def')
- Check for missing commas in lists, dictionaries, or function arguments
- Verify string quotes are properly closed""",
    "IndentationError": """Recovery checklist:
- Check indentation consistency (use 4 spaces per level)
- Ensure all blocks are properly indented
- Verify no mixing of tabs and spaces""",
    "ImportError": """Recovery suggestions:
- Verify the module name is spelled correctly
- Only standard library modules and pandas are pre-installed
- If this is a tool function, search for it using search_functions first
- Then load the tool using load_functions before using it in code
- For pandas Excel support, use engines 'calamine' (Excel) or 'pyarrow' (CSV)
- Consider using preloaded functions or search for external tools instead""",
    "ModuleNotFoundError": """Recovery suggestions:
- Verify the module name is spelled correctly
- Only standard library modules and pandas are pre-installed
- If this is a tool function, search for it using search_functions first
- Then load the tool using load_functions before using it in code""",
    "NameError": """Recovery suggestions:
- Check if the variable/function is defined before using it
- Verify there are no typos in the variable/function name
- Ensure the variable is in scope (defined in the same or outer scope)
- If from a previous execution, verify it was actually assigned (not just printed)
- Check that any required imports are present""",
    "ZeroDivisionError": """Recovery suggestions:
- Add a check to ensure the divisor is not zero before division
- Use a conditional: 'if denominator != 0: result = numerator / denominator'
- Consider using try-except for this specific operation if zero is expected
- Review the logic that produces the divisor to understand why it's zero""",
    "TypeError": """Recovery suggestions:
- Verify function arguments match expected types and count
- Check if you're calling a non-callable object
- Ensure async functions are called with 'await'
- Confirm operators are used with compatible types (e.g., can't add string + int)""",
    "ValueError": """Recovery suggestions:
- Check if input values are in the expected range or format
- Verify string-to-number conversions have valid input
- Ensure unpacking matches the number of values (e.g., 'a, b = [1, 2]')""",
    "KeyError": """Recovery suggestions:
- Verify the dictionary key exists before accessing (use 'key in dict' or 'dict.get(key)')
- Check for typos in key names
- Use smart_print() to examine the dictionary structure first
- Consider using 'dict.get(key, default_value)' for safer access""",
    "IndexError": """Recovery suggestions:
- Verify list/array indices are within bounds (0 to len-1)
- Check if the list is empty before accessing
- Use 'if len(list) > index:' before accessing
- Consider using slicing with safety: 'list[:10]' instead of 'list[10]'""",
    "AttributeError": """Recovery suggestions:
- Check if the object has the attribute you're accessing
- Use smart_print() to examine the object structure first
- Verify the object is of the expected type
- Check if the object is None when it shouldn't be""",
}

DEFAULT_ERROR_HINT = """Recovery suggestions:
- Review the error message carefully for clues
- Break down the code into smaller steps to isolate the issue
- Use smart_print() to examine intermediate values"""


class Sandbox:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def run(self, code) -> SandboxResult:
        raise NotImplementedError

    def get_context(self):
        raise NotImplementedError

    def update_context(self, context):
        raise NotImplementedError
