"""Docstring generator using litellm with structured output.

This module provides a simple way to generate docstrings for Python functions
using LLMs with structured output
"""

import ast
import os

import litellm
from pydantic import BaseModel, Field


class DocstringOutput(BaseModel):
    """Structure for the generated docstring output."""

    summary: str = Field(
        description="A clear, concise summary of what the function does"
    )
    args: dict[str, str] = Field(
        description="Dictionary mapping parameter names to their descriptions"
    )
    returns: str = Field(description="Description of what the function returns")


class FunctionExtractor(ast.NodeVisitor):
    """
    An AST node visitor that collects the source code of all function
    and method definitions within a Python script.
    """

    def __init__(self, source_code: str):
        self.source_lines = source_code.splitlines(keepends=True)
        self.functions: list[
            tuple[str, str]
        ] = []  # Store tuples of (function_name, function_source)

    def _get_source_segment(self, node: ast.AST) -> str | None:
        """Safely extracts the source segment for a node using ast.get_source_segment."""
        try:
            source_segment = ast.get_source_segment("".join(self.source_lines), node)
            return source_segment
        except Exception as e:
            print(
                f"Warning: Could not retrieve source for node {getattr(node, 'name', 'unknown')} at line {getattr(node, 'lineno', 'unknown')}: {e}"
            )
            return None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visits a regular function definition."""
        source_code = self._get_source_segment(node)
        if source_code:
            self.functions.append((node.name, source_code))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visits an asynchronous function definition."""
        source_code = self._get_source_segment(node)
        if source_code:
            self.functions.append((node.name, source_code))
        self.generic_visit(node)


def extract_functions_from_script(file_path: str) -> list[tuple[str, str]]:
    """
    Reads a Python script and extracts the source code of all functions.

    Args:
        file_path: The path to the Python (.py) script.

    Returns:
        A list of tuples, where each tuple contains the function name (str)
        and its full source code (str), including decorators.
        Returns an empty list if the file cannot be read, parsed, or contains no functions.

    Raises:
        FileNotFoundError: If the file_path does not exist.
        SyntaxError: If the file contains invalid Python syntax.
        Exception: For other potential I/O or AST processing errors.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        raise
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise

    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        print(
            f"Error: Invalid Python syntax in {file_path} at line {e.lineno}, offset {e.offset}: {e.msg}"
        )
        raise
    except Exception as e:
        print(f"Error parsing {file_path} into AST: {e}")
        raise

    try:
        extractor = FunctionExtractor(source_code)
        extractor.visit(tree)

        if not extractor.functions:
            print("Warning: No functions found in the file.")

        return extractor.functions
    except Exception as e:
        print(f"Error during function extraction: {e}")
        import traceback

        traceback.print_exc()
        return []


def generate_docstring(
    function_code: str, model: str = "google/gemini-flash"
) -> DocstringOutput:
    """
    Generate a docstring for a Python function using litellm with structured output.

    Args:
        function_code: The source code of the function to document
        model: The model to use for generating the docstring

    Returns:
        A DocstringOutput object containing the structured docstring components
    """
    system_prompt = """You are a helpful AI assistant specialized in writing high-quality Google-style Python docstrings.
    You MUST ALWAYS include an Args section, even if there are no arguments (in which case mention 'None')."""

    user_prompt = f"""Generate a high-quality Google-style docstring for the following Python function. 
    Analyze the function's name, parameters, return values, and functionality to create a comprehensive docstring.
    
    The docstring MUST:
    1. Start with a clear, concise summary of what the function does
    2. ALWAYS include Args section with description of each parameter (or 'None' if no parameters)
    3. Include Returns section describing the return value
    4. Be formatted according to Google Python Style Guide
    
    Here is the function:
    
    {function_code}
    
    Respond in JSON format with the following structure:
    {{
      "summary": "A clear, concise summary of what the function does",
      "args": {{"param_name": "param description", "param_name2": "param description"}},
      "returns": "Description of what the function returns"
    }}
    """

    try:
        # Use regular completion and parse the JSON ourselves instead of using response_model
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # Get the response content
        response_text = response.choices[0].message.content

        # Simple JSON extraction in case the model includes extra text
        import json
        import re

        # Find JSON object in the response using regex
        json_match = re.search(r"({.*})", response_text.replace("\n", " "), re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            parsed_data = json.loads(json_str)
        else:
            # Try to parse the whole response as JSON
            parsed_data = json.loads(response_text)

        # Ensure args is never empty
        if not parsed_data.get("args"):
            parsed_data["args"] = {"None": "This function takes no arguments"}

        # Create DocstringOutput from parsed data
        return DocstringOutput(
            summary=parsed_data.get("summary", ""),
            args=parsed_data.get("args", {"None": "This function takes no arguments"}),
            returns=parsed_data.get("returns", ""),
        )

    except Exception as e:
        print(f"Error generating docstring: {e}")
        # Return a docstring object with default values
        return DocstringOutput(
            summary="No documentation available",
            args={"None": "This function takes no arguments"},
            returns="None",
        )


def format_docstring(docstring: DocstringOutput) -> str:
    """
    Format a DocstringOutput object into a properly formatted docstring string.

    Args:
        docstring: The DocstringOutput object to format

    Returns:
        A formatted docstring string ready to be inserted into code
    """
    formatted_docstring = f"{docstring.summary}\n\n"

    if docstring.args:
        formatted_docstring += "Args:\n"
        for arg_name, arg_desc in docstring.args.items():
            formatted_docstring += f"    {arg_name}: {arg_desc}\n"
        formatted_docstring += "\n"

    if docstring.returns:
        formatted_docstring += f"Returns:\n    {docstring.returns}\n"

    return formatted_docstring.strip()


def insert_docstring_into_function(function_code: str, docstring: str) -> str:
    """
    Insert a docstring into a function's code.

    Args:
        function_code: The source code of the function
        docstring: The formatted docstring string to insert

    Returns:
        The updated function code with the docstring inserted
    """
    try:
        function_ast = ast.parse(function_code)
        if not function_ast.body or not hasattr(function_ast.body[0], "body"):
            return function_code

        function_lines = function_code.splitlines()

        # Find the function definition line (ends with ':')
        func_def_line = None
        for i, line in enumerate(function_lines):
            if "def " in line and line.strip().endswith(":"):
                func_def_line = i
                break

        if func_def_line is None:
            return function_code

        # Determine indentation from the first non-empty line after the function definition
        body_indent = ""
        for line in function_lines[func_def_line + 1 :]:
            if line.strip():
                body_indent = " " * (len(line) - len(line.lstrip()))
                break

        # Check if the function already has a docstring
        first_element = (
            function_ast.body[0].body[0] if function_ast.body[0].body else None
        )
        has_docstring = (
            isinstance(first_element, ast.Expr)
            and isinstance(first_element.value, ast.Constant)
            and isinstance(first_element.value.value, str)
        )

        docstring_lines = [
            f'{body_indent}"""',
            *[f"{body_indent}{line}" for line in docstring.split("\n")],
            f'{body_indent}"""',
        ]

        if has_docstring:
            # Find the existing docstring in the source and replace it
            for i in range(func_def_line + 1, len(function_lines)):
                if '"""' in function_lines[i] or "'''" in function_lines[i]:
                    docstring_start = i
                    # Find end of docstring
                    for j in range(docstring_start + 1, len(function_lines)):
                        if '"""' in function_lines[j] or "'''" in function_lines[j]:
                            docstring_end = j
                            # Replace the existing docstring
                            return "\n".join(
                                function_lines[:docstring_start]
                                + docstring_lines
                                + function_lines[docstring_end + 1 :]
                            )
        else:
            # Insert new docstring after function definition
            return "\n".join(
                function_lines[: func_def_line + 1]
                + docstring_lines
                + function_lines[func_def_line + 1 :]
            )

        # Default return if insertion logic fails
        return function_code
    except Exception as e:
        print(f"Error inserting docstring: {e}")
        return function_code


def process_file(file_path: str, model: str = "google/gemini-flash") -> int:
    """
    Process a Python file and add docstrings to all functions in it.

    Args:
        file_path: Path to the Python file to process
        model: The model to use for generating docstrings

    Returns:
        Number of functions processed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read the original file
    with open(file_path, encoding="utf-8") as f:
        original_content = f.read()

    # Extract functions
    functions = extract_functions_from_script(file_path)
    if not functions:
        print(f"No functions found in {file_path}")
        return 0

    updated_content = original_content
    count = 0

    # Process each function
    for function_name, function_code in functions:
        print(f"Processing function: {function_name}")

        # Generate docstring
        docstring_output = generate_docstring(function_code, model)
        formatted_docstring = format_docstring(docstring_output)

        # Insert docstring into function
        updated_function = insert_docstring_into_function(
            function_code, formatted_docstring
        )

        # Replace the function in the file content
        if updated_function != function_code:
            updated_content = updated_content.replace(function_code, updated_function)
            count += 1

    # Write the updated content back to the file
    if updated_content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"Updated {count} functions in {file_path}")
    else:
        print(f"No changes made to {file_path}")

    return count
