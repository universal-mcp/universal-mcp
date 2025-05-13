import ast
import importlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from loguru import logger


def _import_class(module_path: str, class_name: str):
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
        raise ModuleNotFoundError(f"Class '{class_name}' not found in module '{module_path}'") from e


def _get_single_class_name(file_path: Path) -> str:
    with open(file_path) as file:
        tree = ast.parse(file.read(), filename=str(file_path))
    class_defs = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    if len(class_defs) == 1:
        logger.info(f"Auto-detected class: {class_defs[0]}")
        return class_defs[0]
    elif len(class_defs) == 0:
        raise ValueError(f"No class found in {file_path}")
    else:
        raise ValueError(f"Multiple classes found in {file_path}; please specify one.")


def generate_readme(app: Path) -> Path:
    """Generate README.md with API documentation from a file containing one class."""
    class_name = _get_single_class_name(app)
    app_instance = _import_class(app, class_name)(integration=None)
    tools = app_instance.list_tools()

    formatted_tools = []
    for tool in tools:
        name = tool.__name__
        description = tool.__doc__.strip().split("\n")[0]
        formatted_tools.append((name, description))

    template_dir = Path(__file__).parent.parent / "templates"
    if not template_dir.exists():
        logger.error(f"Template directory not found: {template_dir}")
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    try:
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape())
        template = env.get_template("README.md.j2")
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        raise TemplateError(f"Error loading template: {e}") from e

    try:
        readme_content = template.render(name=class_name, tools=formatted_tools)
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise TemplateError(f"Error rendering template: {e}") from e

    readme_file = app.parent / "README.md"
    try:
        with open(readme_file, "w") as f:
            f.write(readme_content)
        logger.info(f"Documentation generated at: {readme_file}")
    except Exception as e:
        logger.error(f"Error writing README file: {e}")
        raise OSError(f"Error writing README file: {e}") from e

    return readme_file
