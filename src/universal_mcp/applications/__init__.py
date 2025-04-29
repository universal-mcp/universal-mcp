import importlib

from loguru import logger

from universal_mcp.applications.application import (
    APIApplication,
    BaseApplication,
    GraphQLApplication,
)
import subprocess

# Name are in the format of "app-name", eg, google-calendar
# Folder name is "app_name", eg, google_calendar
# Class name is NameApp, eg, GoogleCalendarApp

def _import_class(module_path: str, class_name: str):
    """
    Helper to import a class by name from a module.
    Raises ModuleNotFoundError if module or class does not exist.
    """
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        logger.debug(f"Import failed for module '{module_path}': {e}")
        raise
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        logger.error(f"Class '{class_name}' not found in module '{module_path}'")
        raise ModuleNotFoundError(f"Class '{class_name}' not found in module '{module_path}'") from e

def _install_package(slug_clean: str):
    """
    Helper to install a package via pip from the universal-mcp GitHub repository.
    """
    repo_url = f"git+https://github.com/universal-mcp/{slug_clean}"
    cmd = ["uv", "pip", "install", repo_url]
    logger.info(f"Installing package '{slug_clean}' with command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed for '{slug_clean}': {e}")
        raise ModuleNotFoundError(f"Installation failed for package '{slug_clean}'") from e
    else:
        logger.info(f"Package '{slug_clean}' installed successfully")

def app_from_slug(slug: str):
    """
    Dynamically resolve and return the application class for the given slug.
    Attempts installation from GitHub if the package is not found locally.
    """
    slug_clean = slug.strip().lower()
    class_name = "".join(part.capitalize() for part in slug_clean.split("-")) + "App"
    package_prefix = f"universal_mcp_{slug_clean.replace('-', '_')}"
    module_path = f"{package_prefix}.app"

    logger.info(f"Resolving app for slug '{slug}' → module '{module_path}', class '{class_name}'")
    try:
        return _import_class(module_path, class_name)
    except ModuleNotFoundError as orig_err:
        logger.warning(f"Module '{module_path}' not found locally: {orig_err}. Installing...")
        _install_package(slug_clean)
        # Retry import after installation
        try:
            return _import_class(module_path, class_name)
        except ModuleNotFoundError as retry_err:
            logger.error(f"Still cannot import '{module_path}' after installation: {retry_err}")
            raise

__all__ = [
    "app_from_slug",
    "BaseApplication",
    "APIApplication",
    "GraphQLApplication",
]
