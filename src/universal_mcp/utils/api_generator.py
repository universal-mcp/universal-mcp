import ast
import importlib.util
import inspect
import os
import traceback
from pathlib import Path

from universal_mcp.utils.docgen import process_file
from universal_mcp.utils.openapi import generate_api_client, load_schema

README_TEMPLATE = """
# {name} MCP Server

An MCP Server for the {name} API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

{tools}

## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the {name} app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
"""


def echo(message: str, err: bool = False) -> None:
    """Echo a message to the console, with optional error flag."""
    print(message, file=os.sys.stderr if err else None)


def validate_and_load_schema(schema_path: Path) -> dict:
    """Validate schema file existence and load it."""
    if not schema_path.exists():
        echo(f"Error: Schema file {schema_path} does not exist", err=True)
        raise FileNotFoundError(f"Schema file {schema_path} does not exist")

    try:
        return load_schema(schema_path)
    except Exception as e:
        echo(f"Error loading schema: {e}", err=True)
        raise


def write_and_verify_code(output_path: Path, code: str) -> None:
    """Write generated code to file and verify its contents."""
    with open(output_path, "w") as f:
        f.write(code)
    echo(f"Generated API client at: {output_path}")

    try:
        with open(output_path) as f:
            file_content = f.read()
            echo(f"Successfully wrote {len(file_content)} bytes to {output_path}")
            ast.parse(file_content)
            echo("Python syntax check passed")
    except SyntaxError as e:
        echo(f"Warning: Generated file has syntax error: {e}", err=True)
    except Exception as e:
        echo(f"Error verifying output file: {e}", err=True)


async def generate_docstrings(script_path: str) -> dict[str, int]:
    """Generate docstrings for the given script file."""
    echo(f"Adding docstrings to {script_path}...")

    if not os.path.exists(script_path):
        echo(f"Warning: File {script_path} does not exist", err=True)
        return {"functions_processed": 0}

    try:
        with open(script_path) as f:
            content = f.read()
            echo(f"Successfully read {len(content)} bytes from {script_path}")
    except Exception as e:
        echo(f"Error reading file for docstring generation: {e}", err=True)
        return {"functions_processed": 0}

    try:
        processed = process_file(script_path)
        return {"functions_processed": processed}
    except Exception as e:
        echo(f"Error running docstring generation: {e}", err=True)
        traceback.print_exc()
        return {"functions_processed": 0}


def setup_app_directory(folder_name: str, source_file: Path) -> tuple[Path, Path]:
    """Set up application directory structure and copy generated code."""
    applications_dir = Path(__file__).parent.parent / "applications"
    app_dir = applications_dir / folder_name
    app_dir.mkdir(exist_ok=True)

    init_file = app_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("")

    app_file = app_dir / "app.py"
    with open(source_file) as src, open(app_file, "w") as dest:
        app_content = src.read()
        dest.write(app_content)

    echo(f"API client installed at: {app_file}")
    return app_dir, app_file


def get_class_info(module: any) -> tuple[str | None, any]:
    """Find the main class in the generated module."""
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__ == "temp_module":
            return name, obj
    return None, None


def collect_tools(class_obj: any, folder_name: str) -> list[tuple[str, str]]:
    """Collect tool information from the class."""
    tools = []

    # Try to get tools from list_tools method
    if class_obj and hasattr(class_obj, "list_tools"):
        try:
            instance = class_obj()
            tool_list = instance.list_tools()

            for tool in tool_list:
                func_name = tool.__name__
                if func_name.startswith("_") or func_name in ("__init__", "list_tools"):
                    continue

                doc = tool.__doc__ or f"Function for {func_name.replace('_', ' ')}"
                summary = doc.split("\n\n")[0].strip()
                tools.append((func_name, summary))
        except Exception as e:
            echo(f"Note: Couldn't instantiate class to get tool list: {e}")

    # Fall back to inspecting class methods directly
    if not tools and class_obj:
        for name, method in inspect.getmembers(class_obj, inspect.isfunction):
            if name.startswith("_") or name in ("__init__", "list_tools"):
                continue

            doc = method.__doc__ or f"Function for {name.replace('_', ' ')}"
            summary = doc.split("\n\n")[0].strip()
            tools.append((name, summary))

    return tools


def generate_readme(
    app_dir: Path, folder_name: str, tools: list[tuple[str, str]]
) -> Path:
    """Generate README.md with API documentation."""
    app = folder_name.replace("_", " ").title()

    tools_content = f"This is automatically generated from OpenAPI schema for the {folder_name.replace('_', ' ').title()} API.\n\n"
    tools_content += "## Supported Integrations\n\n"
    tools_content += (
        "This tool can be integrated with any service that supports HTTP requests.\n\n"
    )
    tools_content += "## Tool List\n\n"

    if tools:
        tools_content += "| Tool | Description |\n|------|-------------|\n"
        for tool_name, tool_desc in tools:
            tools_content += f"| {tool_name} | {tool_desc} |\n"
        tools_content += "\n"
    else:
        tools_content += (
            "No tools with documentation were found in this API client.\n\n"
        )

    readme_content = README_TEMPLATE.format(
        name=app,
        tools=tools_content,
        usage="",
    )
    readme_file = app_dir / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)

    echo(f"Documentation generated at: {readme_file}")
    return readme_file


async def generate_api_from_schema(
    schema_path: Path,
    output_path: Path | None = None,
    add_docstrings: bool = True,
) -> dict[str, str | None]:
    """
    Generate API client from OpenAPI schema with optional docstring generation.

    Args:
        schema_path: Path to the OpenAPI schema file
        output_path: Output file path - should match the API name (e.g., 'twitter.py' for Twitter API)
        add_docstrings: Whether to add docstrings to the generated code

    Returns:
        dict: A dictionary with information about the generated files
    """
    try:
        schema = validate_and_load_schema(schema_path)
        code = generate_api_client(schema)

        if not output_path:
            return {"code": code}

        folder_name = output_path.stem
        temp_output_path = output_path

        write_and_verify_code(temp_output_path, code)

        if add_docstrings:
            result = await generate_docstrings(str(temp_output_path))
            if result:
                if "functions_processed" in result:
                    echo(f"Processed {result['functions_processed']} functions")
            else:
                echo("Docstring generation failed", err=True)
        else:
            echo("Skipping docstring generation as requested")

        app_dir, app_file = setup_app_directory(folder_name, temp_output_path)

        try:
            echo("Generating README.md from function information...")
            spec = importlib.util.spec_from_file_location("temp_module", app_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            class_name, class_obj = get_class_info(module)
            if not class_name:
                class_name = folder_name.capitalize() + "App"

            tools = collect_tools(class_obj, folder_name)
            readme_file = generate_readme(app_dir, folder_name, tools)

        except Exception as e:
            echo(f"Error generating documentation: {e}", err=True)
            readme_file = None

        return {
            "app_file": str(app_file),
            "readme_file": str(readme_file) if readme_file else None,
        }

    finally:
        if output_path and output_path.exists():
            try:
                output_path.unlink()
                echo(f"Cleaned up temporary file: {output_path}")
            except Exception as e:
                echo(
                    f"Warning: Could not remove temporary file {output_path}: {e}",
                    err=True,
                )
