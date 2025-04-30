import importlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from loguru import logger


def _import_class(module_path: str, class_name: str):
    """
    Helper to import a class by name from a module.
    Raises ModuleNotFoundError if module or class does not exist.
    """
    try:
        spec = importlib.util.spec_from_file_location("temp_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ModuleNotFoundError as e:
        logger.debug(f"Import failed for module '{module_path}': {e}")
        raise
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        logger.error(f"Class '{class_name}' not found in module '{module_path}'")
        raise ModuleNotFoundError(
            f"Class '{class_name}' not found in module '{module_path}'"
        ) from e

def generate_readme(app: Path, class_name: str) -> Path:
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

    # Import the app
    app_instance = _import_class(app, class_name)(integration=None)
    # List tools by calling list_tools()
    tools = app_instance.list_tools()
    # Format tools into (name, description) tuples
    formatted_tools = []
    for tool in tools:
        name = tool.__name__
        description = tool.__doc__.strip().split("\n")[0]
        formatted_tools.append((name, description))
    # Render the template
     # Set up Jinja2 environment
    template_dir = Path(__file__).parent.parent / "templates"
    if not template_dir.exists():
        logger.error(f"Template directory not found: {template_dir}")
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    try:
        env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=select_autoescape()
        )
        template = env.get_template("README.md.j2")
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        raise TemplateError(f"Error loading template: {e}") from e
    # Write the README file
    try:
        readme_content = template.render(name=class_name, tools=formatted_tools)
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise TemplateError(f"Error rendering template: {e}") from e

    # Write the README file
    app_dir = app.parent
    readme_file = app_dir / "README.md"

    # Write the README file
    readme_file = app_dir / "README.md"
    try:
        with open(readme_file, "w") as f:
            f.write(readme_content)
        logger.info(f"Documentation generated at: {readme_file}")
    except Exception as e:
        logger.error(f"Error writing README file: {e}")
        raise OSError(f"Error writing README file: {e}") from e

    return readme_file