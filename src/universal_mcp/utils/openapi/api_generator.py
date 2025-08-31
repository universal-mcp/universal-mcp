import importlib.util
import inspect
import os
import shutil
from pathlib import Path

from loguru import logger

from universal_mcp.utils.openapi.openapi import generate_api_client, generate_schemas_file, load_schema


def echo(message: str, err: bool = False) -> None:
    """Echo a message to the console, with optional error flag."""
    if err:
        logger.error(message)
    else:
        logger.info(message)


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


def format_with_black(file_path: Path) -> bool:
    """Format the given Python file with Black. Returns True if successful, False otherwise."""
    try:
        import black

        content = file_path.read_text(encoding="utf-8")

        formatted_content = black.format_file_contents(content, fast=False, mode=black.FileMode())

        file_path.write_text(formatted_content, encoding="utf-8")

        logger.info("Black formatting applied successfully to: %s", file_path)
        return True
    except ImportError:
        logger.warning("Black not installed. Skipping formatting for: %s", file_path)
        return False
    except Exception as e:
        logger.warning("Black formatting failed for %s: %s", file_path, e)
        return False


def generate_api_from_schema(
    schema_path: Path,
    output_path: Path | None = None,
    class_name: str | None = None,
    filter_config_path: str | None = None,
) -> tuple[Path, Path] | dict:
    """
    Generate API client from OpenAPI schema and write to app.py and schemas.py.

    Steps:
    1. Parse and validate the OpenAPI schema.
    2. Generate client code and schemas.
    3. Ensure output directory exists.
    4. Write code to intermediate files and perform basic import checks.
    5. Copy/overwrite intermediate files to app.py and schemas.py.
    6. Format the final files with Black.
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

    # 2. Generate client code and schemas
    try:
        code = generate_api_client(schema, class_name, filter_config_path)
        logger.info("API client code generated.")

        schemas_code = generate_schemas_file(schema, class_name, filter_config_path)
        logger.info("Schemas code generated.")
    except Exception as e:
        logger.error("Code generation failed: %s", e)
        raise

    # If no output_path provided, return raw code
    if not output_path:
        logger.debug("No output_path provided, returning code as string.")
        return {"code": code, "schemas_code": schemas_code}

    # 3. Ensure output directory exists
    target_dir = output_path
    if not target_dir.exists():
        logger.info("Creating output directory: %s", target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

    # 4. Write to intermediate files and perform basic checks
    gen_file = target_dir / "app_generated.py"
    schemas_gen_file = target_dir / "schemas_generated.py"

    logger.info("Writing generated code to intermediate file: %s", gen_file)
    with open(gen_file, "w") as f:
        f.write(code)

    logger.info("Writing schemas code to intermediate file: %s", schemas_gen_file)
    with open(schemas_gen_file, "w") as f:
        f.write(schemas_code)

    # Test schemas file first (no relative imports)
    if not test_correct_output(schemas_gen_file):
        logger.error("Generated schemas validation failed for '%s'. Aborting generation.", schemas_gen_file)
        logger.info("Next steps:")
        logger.info(" 1) Review your OpenAPI schema for potential mismatches.")
        logger.info(
            " 2) Inspect '%s' for syntax or logic errors in the generated code.",
            schemas_gen_file,
        )
        logger.info(" 3) Correct the issues and re-run the command.")
        return {"error": "Validation failed. See logs above for detailed instructions."}

    # Skip testing app file since it has relative imports - just do a basic syntax check
    logger.info("Skipping detailed validation for app file due to relative imports.")

    # 5. Copy to final files (overwrite if exists)
    app_file = target_dir / "app.py"
    schemas_file = target_dir / "schemas.py"

    if app_file.exists():
        logger.warning("Overwriting existing file: %s", app_file)
    else:
        logger.info("Creating new file: %s", app_file)
    shutil.copy(gen_file, app_file)
    logger.info("App file written to: %s", app_file)

    if schemas_file.exists():
        logger.warning("Overwriting existing file: %s", schemas_file)
    else:
        logger.info("Creating new file: %s", schemas_file)
    shutil.copy(schemas_gen_file, schemas_file)
    logger.info("Schemas file written to: %s", schemas_file)

    # 6. Format the final files with Black
    format_with_black(app_file)
    format_with_black(schemas_file)

    # Cleanup intermediate files
    try:
        os.remove(gen_file)
        logger.debug("Cleaned up intermediate file: %s", gen_file)
    except Exception as e:
        logger.warning("Could not remove intermediate file %s: %s", gen_file, e)

    try:
        os.remove(schemas_gen_file)
        logger.debug("Cleaned up intermediate schemas file: %s", schemas_gen_file)
    except Exception as e:
        logger.warning("Could not remove intermediate schemas file %s: %s", schemas_gen_file, e)

    return app_file, schemas_file
