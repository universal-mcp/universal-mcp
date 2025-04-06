"""Utility & helper functions."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage


import ast
from typing import List, Optional, Tuple

def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)

class FunctionExtractor(ast.NodeVisitor):
    """
    An AST node visitor that collects the source code of all function
    and method definitions within a Python script.
    """
    def __init__(self, source_code: str):
        self.source_lines = source_code.splitlines(keepends=True)
        self.functions: List[Tuple[str, str]] = [] # Store tuples of (function_name, function_source)

    def _get_source_segment(self, node: ast.AST) -> Optional[str]:
        """Safely extracts the source segment for a node using ast.get_source_segment."""
        try:
            source_segment = ast.get_source_segment(
                "".join(self.source_lines), node
                )
            return source_segment
        except Exception as e:
            # Handle cases where source cannot be retrieved (rare with valid ASTs)
            print(f"Warning: Could not retrieve source for node {getattr(node, 'name', 'unknown')} at line {getattr(node, 'lineno', 'unknown')}: {e}")
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
        # Visit nodes inside this async function if needed
        self.generic_visit(node)

def extract_functions_from_script(file_path: str) -> List[Tuple[str, str]]:
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
    print(f"Attempting to read script: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        raise
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise

    print("Parsing the script into an Abstract Syntax Tree (AST)...")
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        print(f"Error: Invalid Python syntax in {file_path} at line {e.lineno}, offset {e.offset}: {e.msg}")
        raise
    except Exception as e:
        print(f"Error parsing {file_path} into AST: {e}")
        raise

    print("Extracting functions using AST visitor...")
    extractor = FunctionExtractor(source_code)
    extractor.visit(tree)

    print(f"Found {len(extractor.functions)} functions/methods.")
    return extractor.functions