import importlib
import subprocess
import sys
from pathlib import Path

from loguru import logger

from universal_mcp.applications.application import (
    APIApplication,
    BaseApplication,
    GraphQLApplication,
)
from universal_mcp.utils.common import (
    get_default_class_name,
    get_default_module_path,
    get_default_package_name,
    get_default_repository_path,
)

UNIVERSAL_MCP_HOME = Path.home() / ".universal-mcp" / "packages"

if not UNIVERSAL_MCP_HOME.exists():
    UNIVERSAL_MCP_HOME.mkdir(parents=True, exist_ok=True)

# set python path to include the universal-mcp home directory
sys.path.append(str(UNIVERSAL_MCP_HOME))


# Name are in the format of "app-name", eg, google-calendar
# Class name is NameApp, eg, GoogleCalendarApp


def _install_or_upgrade_package(package_name: str, repository_path: str):
    """
    Helper to install a package via pip from the universal-mcp GitHub repository.
    """
    cmd = [
        "uv",
        "pip",
        "install",
        "--upgrade",
        repository_path,
        "--target",
        str(UNIVERSAL_MCP_HOME),
    ]
    logger.debug(f"Installing package '{package_name}' with command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"Command stdout: {result.stdout}")
        if result.stderr:
            logger.info(f"Command stderr: {result.stderr}")
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed for '{package_name}': {e}")
        if e.stdout:
            logger.error(f"Command stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Command stderr: {e.stderr}")
        raise ModuleNotFoundError(f"Installation failed for package '{package_name}'") from e
    else:
        logger.debug(f"Package {package_name} installed successfully")


def app_from_slug(slug: str):
    """
    Dynamically resolve and return the application class for the given slug.
    Attempts installation from GitHub if the package is not found locally.
    """
    class_name = get_default_class_name(slug)
    module_path = get_default_module_path(slug)
    package_name = get_default_package_name(slug)
    repository_path = get_default_repository_path(slug)
    logger.debug(f"Resolving app for slug '{slug}' → module '{module_path}', class '{class_name}'")
    try:
        _install_or_upgrade_package(package_name, repository_path)
        module = importlib.import_module(module_path)
        class_ = getattr(module, class_name)
        logger.debug(f"Loaded class '{class_}' from module '{module_path}'")
        return class_
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Package '{module_path}' not found locally. Please install it first.") from e
    except AttributeError as e:
        raise AttributeError(f"Class '{class_name}' not found in module '{module_path}'") from e
    except Exception as e:
        raise Exception(f"Error importing module '{module_path}': {e}") from e


__all__ = [
    "app_from_slug",
    "BaseApplication",
    "APIApplication",
    "GraphQLApplication",
]
