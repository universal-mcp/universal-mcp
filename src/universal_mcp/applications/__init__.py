import importlib
import os
import subprocess
import sys

from loguru import logger

from universal_mcp.applications.application import (
    APIApplication,
    BaseApplication,
    GraphQLApplication,
)

UNIVERSAL_MCP_HOME = os.path.join(os.path.expanduser("~"), ".universal-mcp", "packages")

if not os.path.exists(UNIVERSAL_MCP_HOME):
    os.makedirs(UNIVERSAL_MCP_HOME)

# set python path to include the universal-mcp home directory
sys.path.append(UNIVERSAL_MCP_HOME)


# Name are in the format of "app-name", eg, google-calendar
# Class name is NameApp, eg, GoogleCalendarApp


def _install_or_upgrade_package(package_prefix: str, slug_clean: str):
    """
    Helper to install a package via pip from the universal-mcp GitHub repository.
    """
    # Check current version with uv pip show
    repo_url = f"git+https://github.com/universal-mcp/{slug_clean}"
    cmd = [
        "uv",
        "pip",
        "install",
        "--upgrade",
        repo_url,
        "--target",
        UNIVERSAL_MCP_HOME,
    ]
    logger.debug(f"Installing package '{slug_clean}' with command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed for '{slug_clean}': {e}")
        raise ModuleNotFoundError(
            f"Installation failed for package '{slug_clean}'"
        ) from e
    else:
        logger.debug(f"Package '{slug_clean}' installed successfully")


def app_from_slug(slug: str):
    """
    Dynamically resolve and return the application class for the given slug.
    Attempts installation from GitHub if the package is not found locally.
    """
    slug_clean = slug.strip().lower()
    class_name = "".join(part.capitalize() for part in slug_clean.split("-")) + "App"
    package_prefix = f"universal_mcp_{slug_clean.replace('-', '_')}"
    module_path = f"{package_prefix}.app"

    logger.debug(
        f"Resolving app for slug '{slug}' → module '{module_path}', class '{class_name}'"
    )
    try:
        _install_or_upgrade_package(package_prefix, slug_clean)
        module = importlib.import_module(module_path)
        class_ = getattr(module, class_name)
        logger.debug(f"Loaded class '{class_}' from module '{module_path}'")
        return class_
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            f"Package '{module_path}' not found locally. Please install it first."
        ) from e
    except AttributeError as e:
        raise AttributeError(
            f"Class '{class_name}' not found in module '{module_path}'"
        ) from e
    except Exception as e:
        raise Exception(f"Error importing module '{module_path}': {e}") from e


__all__ = [
    "app_from_slug",
    "BaseApplication",
    "APIApplication",
    "GraphQLApplication",
]
