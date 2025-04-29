import inspect
import os
from pathlib import Path
from loguru import logger
import shutil
import importlib.util
from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape

from universal_mcp.utils.openapi import generate_api_client, load_schema


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

def get_class_info(module: any) -> tuple[str | None, any]:
    """Find the main class in the generated module."""
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__ == "temp_module":
            return name, obj
    return None, None

def generate_readme(
    app_dir: Path, folder_name: str, tools: list
) -> Path:
    """Generate README.md with API documentation.
    
    Args:
        app_dir: Directory where the README will be generated
        folder_name: Name of the application folder
        tools: List of Function objects from the OpenAPI schema
        
    Returns:
        Path to the generated README file
        
    Raises:
        FileNotFoundError: If the template directory doesn't exist
        TemplateError: If there's an error rendering the template
        IOError: If there's an error writing the README file
    """
    app = folder_name.replace("_", " ").title()
    logger.info(f"Generating README for {app} in {app_dir}")

    # Format tools into (name, description) tuples
    formatted_tools = []
    for tool in tools:
        name = tool.__name__
        description = tool.__doc__.strip().split("\n")[0]
        formatted_tools.append((name, description))

    # Set up Jinja2 environment
    template_dir = Path(__file__).parent.parent / "templates"
    if not template_dir.exists():
        logger.error(f"Template directory not found: {template_dir}")
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    try:
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape()
        )
        template = env.get_template("README.md.j2")
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        raise TemplateError(f"Error loading template: {e}")

    # Render the template
    try:
        readme_content = template.render(
            name=app,
            tools=formatted_tools
        )
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise TemplateError(f"Error rendering template: {e}")

    # Write the README file
    readme_file = app_dir / "README.md"
    try:
        with open(readme_file, "w") as f:
            f.write(readme_content)
        logger.info(f"Documentation generated at: {readme_file}")
    except Exception as e:
        logger.error(f"Error writing README file: {e}")
        raise IOError(f"Error writing README file: {e}")

    return readme_file

def test_correct_output(gen_file: Path):
    # Check file is non-empty
    if gen_file.stat().st_size == 0:
        msg = f"Generated file {gen_file} is empty."
        logger.error(msg)
        return False

    # Basic import test on generated code
    try:
        spec = importlib.util.spec_from_file_location("temp_module", gen_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        logger.info("Intermediate code import test passed.")
        return True
    except Exception as e:
        logger.error(f"Import test failed for generated code: {e}")
        return False
    return True


def generate_api_from_schema(
    schema_path: Path,
    output_path: Path | None = None,
    add_docstrings: bool = True,
) -> tuple[Path, Path]:
    """
    Generate API client from OpenAPI schema and write to app.py with a README.

    Steps:
    1. Parse and validate the OpenAPI schema.
    2. Generate client code.
    3. Ensure output directory exists.
    4. Write code to an intermediate app_generated.py and perform basic import checks.
    5. Copy/overwrite intermediate file to app.py.
    6. Collect tools and generate README.md.
    """
    # Local imports for logging and file operations


    logger.info("Starting API generation for schema: %s", schema_path)

    # 1. Parse and validate schema
    try:
        schema = validate_and_load_schema(schema_path)
        logger.info("Schema loaded and validated successfully.")
    except Exception as e:
        logger.error("Failed to load or validate schema: %s", e)
        raise

    # 2. Generate client code
    try:
        code = generate_api_client(schema)
        logger.info("API client code generated.")
    except Exception as e:
        logger.error("Code generation failed: %s", e)
        raise

    # If no output_path provided, return raw code
    if not output_path:
        logger.debug("No output_path provided, returning code as string.")
        return {"code": code}

    # 3. Ensure output directory exists
    target_dir = output_path
    if not target_dir.exists():
        logger.info("Creating output directory: %s", target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

    # 4. Write to intermediate file and perform basic checks
    gen_file = target_dir / "app_generated.py"
    logger.info("Writing generated code to intermediate file: %s", gen_file)
    with open(gen_file, "w") as f:
        f.write(code)

    if not test_correct_output(gen_file):
        logger.error("Generated code validation failed for '%s'. Aborting generation.", gen_file)
        logger.info("Next steps:")
        logger.info(" 1) Review your OpenAPI schema for potential mismatches.")
        logger.info(" 2) Inspect '%s' for syntax or logic errors in the generated code.", gen_file)
        logger.info(" 3) Correct the issues and re-run the command.")
        return {"error": "Validation failed. See logs above for detailed instructions."}

    # 5. Copy to final app.py (overwrite if exists)
    app_file = target_dir / "app.py"
    if app_file.exists():
        logger.warning("Overwriting existing file: %s", app_file)
    else:
        logger.info("Creating new file: %s", app_file)
    shutil.copy(gen_file, app_file)
    logger.info("App file written to: %s", app_file)

    # 6. Collect tools and generate README
    import importlib.util
    import sys

    # Load the generated module as "temp_module"
    spec = importlib.util.spec_from_file_location("temp_module", str(app_file))
    module = importlib.util.module_from_spec(spec)
    sys.modules["temp_module"] = module
    spec.loader.exec_module(module)

    # Retrieve the generated API class
    class_name, cls = get_class_info(module)

    # Instantiate client and collect its tools
    tools = []
    if cls:
        try:
            client = cls()
            tools = client.list_tools()
        except Exception as e:
            logger.warning("Failed to instantiate '%s' or list tools: %s", class_name, e)
    else:
        logger.warning("No generated class found in module 'temp_module'")
    readme_file = generate_readme(target_dir, output_path.stem, tools)
    logger.info("README generated at: %s", readme_file)


    # Cleanup intermediate file
    try:
        os.remove(gen_file)
        logger.debug("Cleaned up intermediate file: %s", gen_file)
    except Exception as e:
        logger.warning("Could not remove intermediate file %s: %s", gen_file, e)

    return app_file, readme_file
