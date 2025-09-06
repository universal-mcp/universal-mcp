import importlib

from loguru import logger

from universal_mcp.applications.application import BaseApplication

# --- Default Name Generators ---


def get_default_package_name(slug: str) -> str:
    """
    Convert a repository slug to a package name.
    """
    slug = slug.strip().lower().replace("-", "_")
    package_name = f"universal_mcp.applications.{slug}"
    return package_name


def get_default_module_path(slug: str) -> str:
    """
    Convert a repository slug to a module path.
    """
    package_name = get_default_package_name(slug)
    module_path = f"{package_name}.app"
    return module_path


def get_default_class_name(slug: str) -> str:
    """
    Convert a repository slug to a class name.
    """
    slug = slug.strip().lower()
    parts = slug.replace("-", "_").split("_")
    class_name = "".join(part.capitalize() for part in parts) + "App"
    return class_name


# --- Application Loaders ---


def app_from_slug(slug: str) -> type[BaseApplication]:
    """Loads an application from a slug."""
    return load_app_from_package(slug)


def load_app_from_package(slug: str) -> type[BaseApplication]:
    """Loads an application from a pip-installable package."""
    logger.debug(f"Loading '{slug}' as a package.")
    module_path_str = get_default_module_path(slug)
    class_name_str = get_default_class_name(slug)
    module = importlib.import_module(module_path_str)
    return getattr(module, class_name_str)
