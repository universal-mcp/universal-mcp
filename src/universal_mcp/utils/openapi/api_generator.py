import importlib.util
import inspect
import os
import shutil
from pathlib import Path

from loguru import logger

from universal_mcp.utils.openapi.openapi import generate_api_client, load_schema


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
    class_name: str | None = None,
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
        code = generate_api_client(schema, class_name)
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
        logger.info(
            " 2) Inspect '%s' for syntax or logic errors in the generated code.",
            gen_file,
        )
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

    # Cleanup intermediate file
    try:
        os.remove(gen_file)
        logger.debug("Cleaned up intermediate file: %s", gen_file)
    except Exception as e:
        logger.warning("Could not remove intermediate file %s: %s", gen_file, e)

    return app_file
