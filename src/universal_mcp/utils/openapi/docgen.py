"""Docstring generator using litellm with structured output.

This module provides a simple way to generate docstrings for Python functions
using LLMs with structured output
"""

import ast
import json
import os
import re
import sys
import textwrap
import traceback

import litellm
from pydantic import BaseModel, Field


class DocstringOutput(BaseModel):
    """Structure for the generated docstring output."""

    summary: str = Field(description="A clear, concise summary of what the function does")
    args: dict[str, str] = Field(description="Dictionary mapping parameter names to their descriptions")
    returns: str = Field(description="Description of what the function returns")
    raises: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping potential exception types/reasons to their descriptions",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="List of relevant tags for the function (e.g., action, job type, async status, importance)",
    )


class FunctionExtractor(ast.NodeVisitor):
    """
    An AST node visitor that collects the source code of all function
    and method definitions within a Python script.
    """

    def __init__(self, source_code: str):
        self.source_lines = source_code.splitlines(keepends=True)
        self.functions: list[tuple[str, str]] = []  # Store tuples of (function_name, function_source)

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
        """Visits a regular function definition and collects it if not excluded."""
        # Add the exclusion logic here
        if not node.name.startswith("_") and node.name != "list_tools":
            source_code = self._get_source_segment(node)
            if source_code:
                self.functions.append((node.name, source_code))
        # Continue traversing the AST for nested functions/classes
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visits an asynchronous function definition and collects it if not excluded."""
        # Add the exclusion logic here
        if not node.name.startswith("_") and node.name != "list_tools":
            source_code = self._get_source_segment(node)
            if source_code:
                self.functions.append((node.name, source_code))
        # Continue traversing the AST for nested functions/classes
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
        print(f"Error: Invalid Python syntax in {file_path} at line {e.lineno}, offset {e.offset}: {e.msg}")
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


def extract_json_from_text(text):
    """Extract valid JSON from text that might contain additional content.

    Args:
        text: Raw text response from the model

    Returns:
        Dict containing the extracted JSON data

    Raises:
        ValueError: If no valid JSON could be extracted
    """
    # Try to find JSON between triple backticks (common markdown pattern)
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find the first { and last } for a complete JSON object
    try:
        start = text.find("{")
        if start >= 0:
            brace_count = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        return json.loads(text[start : i + 1])
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError("Could not extract valid JSON from the response") from e


def generate_docstring(function_code: str, model: str = "perplexity/sonar") -> DocstringOutput:
    """
    Generate a docstring for a Python function using litellm with structured output.

    Args:
        function_code: The source code of the function to document
        model: The model to use for generating the docstring

    Returns:
        A DocstringOutput object containing the structured docstring components
    """
    system_prompt = """You are a helpful AI assistant specialized in writing high-quality Google-style Python docstrings.
    You MUST ALWAYS include an Args section, even if there are no arguments (in which case mention 'None').
    You should also generate a list of tags describing the function's purpose and characteristics."""

    user_prompt = f"""Generate a high-quality Google-style docstring for the following Python function.
    Analyze the function's name, parameters, return values, potential exceptions, and functionality to create a comprehensive docstring.

    The docstring MUST:
    1. Start with a clear, concise summary of what the function does
    2. ALWAYS include Args section with description of each parameter (or 'None' if no parameters)
    3. Include Returns section describing the return value (or 'None' if nothing is explicitly returned)
    4. **Optionally include a Raises section if the function might raise exceptions, describing the exception type/reason and when it's raised.**
    5. **Include a Tags section with a list of strings describing the function's purpose, characteristics, or keywords.** Tags should be lowercase and single words or hyphenated phrases. Include tags like:
        - The main action (e.g., 'scrape', 'search', 'start', 'check', 'cancel', 'list')
        - The type of job ('async_job', 'batch')
        - The stage of an asynchronous job ('start', 'status', 'cancel')
        - Related domain/feature ('ai', 'management')
        - **Significance: Add the tag 'important' to functions that represent core capabilities or primary interaction points of the class (e.g., initiating actions like scrape, search, or starting async jobs).**
    6. Be formatted according to Google Python Style Guide

    Here is the function:

    {function_code}

    Respond ONLY in JSON format with the following structure. **Include the 'raises' field only if the function is likely to raise exceptions.** **Include the 'tags' field as a list of strings.**
    {{
    "summary": "A clear, concise summary of what the function does",
    "args": {{"param_name": "param description", "param_name2": "param description"}},
    "returns": "Description of what the function returns",
    "raises": {{
        "ExceptionType": "Description of when/why this exception is raised"
    }},
    "tags": ["tag1", "tag2", "important"]
    }}
    """

    try:
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        response_text = response.choices[0].message.content

        try:
            parsed_data = extract_json_from_text(response_text)
        except ValueError as e:
            print(f"JSON extraction failed: {e}")
            print(f"Raw response: {response_text[:100]}...")  # Log first 100 chars for debugging
            # Return a default structure if extraction fails
            return DocstringOutput(
                summary="Failed to extract docstring information",
                args={"None": "This function takes no arguments"},
                returns="Unknown return value",
            )
        model_args = parsed_data.get("args")
        if not model_args:
            parsed_data["args"] = {"None": "This function takes no arguments"}

        return DocstringOutput(
            summary=parsed_data.get("summary", "No documentation available"),
            args=parsed_data.get("args", {"None": "This function takes no arguments"}),
            returns=parsed_data.get("returns", "None"),
            raises=parsed_data.get("raises", {}),
            tags=parsed_data.get("tags", []),  # Get tags, default to empty list
        )

    except Exception as e:
        print(f"Error generating docstring: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return DocstringOutput(
            summary=f"Error generating docstring: {e}",
            args={"None": "This function takes no arguments"},
            returns="None",
            raises={},
            tags=["generation-error"],
        )


def format_docstring(docstring: DocstringOutput) -> str:
    """
    Format a DocstringOutput object into the content string for a docstring.
    This function produces the content *between* the triple quotes, without
    the leading/trailing triple quotes or the main indentation.

    Args:
        docstring: The DocstringOutput object to format

    Returns:
        A formatted docstring content string ready to be indented and wrapped
        in triple quotes for insertion into code.
    """
    parts = []

    summary = docstring.summary.strip()
    if summary:
        parts.append(summary)

    filtered_args = {name: desc for name, desc in docstring.args.items() if name not in ("self", "cls")}
    args_lines = []
    if filtered_args:
        args_lines.append("Args:")
        for arg_name, arg_desc in filtered_args.items():
            arg_desc_cleaned = arg_desc.strip()
            args_lines.append(f"    {arg_name}: {arg_desc_cleaned}")
    elif docstring.args.get("None"):  # Include the 'None' placeholder if it was generated
        args_lines.append("Args:")
        none_desc_cleaned = docstring.args["None"].strip()
        args_lines.append(f"    None: {none_desc_cleaned}")

    if args_lines:
        parts.append("\n".join(args_lines))

    returns_desc_cleaned = docstring.returns.strip()
    if returns_desc_cleaned and returns_desc_cleaned.lower() not in ("none", ""):
        parts.append(f"Returns:\n    {returns_desc_cleaned}")

    raises_lines = []
    if docstring.raises:
        raises_lines.append("Raises:")
        for exception_type, exception_desc in docstring.raises.items():
            exception_desc_cleaned = exception_desc.strip()
            if exception_type.strip() and exception_desc_cleaned:  # Ensure type and desc are not empty
                raises_lines.append(f"    {exception_type.strip()}: {exception_desc_cleaned}")
    if raises_lines:
        parts.append("\n".join(raises_lines))

    cleaned_tags = [tag.strip() for tag in docstring.tags if tag and tag.strip()]
    if cleaned_tags:
        tags_string = ", ".join(cleaned_tags)
        parts.append(f"Tags:\n    {tags_string}")

    return "\n\n".join(parts)


def insert_docstring_into_function(function_code: str, docstring: str) -> str:
    """
    Insert a docstring into a function's code, replacing an existing one if present
    at the correct location, and attempting to remove misplaced string literals
    from the body.

    This version handles multiline function definitions and existing docstrings
    by carefully splicing lines based on AST node positions. It also tries to
    clean up old, misplaced string literals that might have been interpreted
    as docstrings previously.

    Args:
        function_code: The source code of the function snippet. This snippet is
                       expected to contain exactly one function definition.
        docstring: The formatted docstring string content (without triple quotes or
                   leading/trailing newlines within the content itself).

    Returns:
        The updated function code with the docstring inserted, or the original
        code if an error occurs during processing or parsing.
    """
    try:
        lines = function_code.splitlines(keepends=True)

        tree = ast.parse(function_code)
        if not tree.body or not isinstance(tree.body[0], ast.FunctionDef | ast.AsyncFunctionDef):
            print(
                "Warning: Could not parse function definition from code snippet. Returning original code.",
                file=sys.stderr,
            )
            return function_code  # Return original code if parsing fails or isn't a function

        func_node = tree.body[0]
        func_name = getattr(func_node, "name", "unknown_function")

        insert_idx = func_node.end_lineno

        if func_node.body:
            insert_idx = func_node.body[0].lineno - 1

        body_indent = "    "  # Default indentation (PEP 8)

        indent_source_idx = insert_idx
        actual_first_body_line_idx = -1
        for i in range(indent_source_idx, len(lines)):
            line = lines[i]
            stripped = line.lstrip()
            if stripped and not stripped.startswith("#"):
                actual_first_body_line_idx = i
                break

        # If a meaningful line was found at or after insertion point, use its indentation
        if actual_first_body_line_idx != -1:
            body_line = lines[actual_first_body_line_idx]
            body_indent = body_line[: len(body_line) - len(body_line.lstrip())]
        else:
            if func_node.lineno - 1 < len(lines):  # Ensure def line exists
                def_line = lines[func_node.lineno - 1]
                def_line_indent = def_line[: len(def_line) - len(def_line.lstrip())]
                body_indent = def_line_indent + "    "  # Standard 4 spaces relative indent

        # Format the new docstring lines with the calculated indentation
        new_docstring_lines_formatted = [f'{body_indent}"""\n']
        new_docstring_lines_formatted.extend([f"{body_indent}{line}\n" for line in docstring.splitlines()])
        new_docstring_lines_formatted.append(f'{body_indent}"""\n')

        output_lines = []
        output_lines.extend(lines[:insert_idx])

        # 2. Insert the new docstring
        output_lines.extend(new_docstring_lines_formatted)
        remaining_body_lines = lines[insert_idx:]

        remaining_body_code = "".join(remaining_body_lines)

        if remaining_body_code.strip():  # Only parse if there's non-whitespace content
            try:
                dummy_code = f"def _dummy_func():\n{textwrap.indent(remaining_body_code, body_indent)}"
                dummy_tree = ast.parse(dummy_code)
                dummy_body_statements = (
                    dummy_tree.body[0].body
                    if dummy_tree.body and isinstance(dummy_tree.body[0], ast.FunctionDef | ast.AsyncFunctionDef)
                    else []
                )
                cleaned_body_parts = []
                for _node in dummy_body_statements:
                    break  # Exit this loop, we'll process func_node.body instead
                cleaned_body_parts = []
                start_stmt_index = (
                    1
                    if func_node.body
                    and isinstance(func_node.body[0], ast.Expr)
                    and isinstance(func_node.body[0].value, ast.Constant)
                    and isinstance(func_node.body[0].value.value, str)
                    else 0
                )

                for i in range(start_stmt_index, len(func_node.body)):
                    stmt_node = func_node.body[i]

                    is_just_string_stmt = (
                        isinstance(stmt_node, ast.Expr)
                        and isinstance(stmt_node.value, ast.Constant)
                        and isinstance(stmt_node.value.value, str)
                    )

                    if not is_just_string_stmt:
                        stmt_start_idx = stmt_node.lineno - 1
                        stmt_end_idx = stmt_node.end_lineno - 1  # Inclusive end line index

                        cleaned_body_parts.extend(lines[stmt_start_idx : stmt_end_idx + 1])

                if func_node.body:
                    last_stmt_end_idx = func_node.body[-1].end_lineno - 1
                    for line in lines[last_stmt_end_idx + 1 :]:
                        if line.strip():
                            cleaned_body_parts.append(line)
                cleaned_body_lines = cleaned_body_parts

            except SyntaxError as parse_e:
                print(
                    f"WARNING: Could not parse function body for cleaning, keeping all body lines: {parse_e}",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
                cleaned_body_lines = remaining_body_lines
            except Exception as other_e:
                print(
                    f"WARNING: Unexpected error processing function body for cleaning, keeping all body lines: {other_e}",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
                cleaned_body_lines = remaining_body_lines
        else:
            cleaned_body_lines = []
            output_lines.extend(lines[func_node.end_lineno :])

        if func_node.body or not remaining_body_code.strip():
            output_lines.extend(cleaned_body_lines)

        final_code = "".join(output_lines)
        ast.parse(final_code)
        return final_code

    except SyntaxError as e:
        print(
            f"WARNING: Generated code snippet for '{func_name}' has syntax error: {e}",
            file=sys.stderr,
        )
        traceback.print_exc(file=sys.stderr)
        return function_code
    except Exception as e:
        print(f"Error processing function snippet for insertion: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

        return function_code


def process_file(file_path: str, model: str = "perplexity/sonar") -> int:
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
        updated_function = insert_docstring_into_function(function_code, formatted_docstring)

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
        print(updated_function, "formatted docstring", formatted_docstring)
        print(f"No changes made to {file_path}")

    return count
