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

def _ensure_latest_package(slug_clean: str):
    """
    Checks if the package is up-to-date by forcing a reinstall from the GitHub repo.
    """
    repo_url = f"git+https://github.com/universal-mcp/{slug_clean}"
    cmd = ["uv", "pip", "install", "--upgrade", "--force-reinstall", repo_url, "--target", UNIVERSAL_MCP_HOME]
    logger.info(f"Ensuring latest version of package '{slug_clean}' with command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Upgrade check failed for '{slug_clean}': {e}")
        raise ModuleNotFoundError(
            f"Upgrade attempt failed for package '{slug_clean}'"
        ) from e
    else:
        logger.info(f"Latest version of package '{slug_clean}' ensured successfully")

def _check_for_package_update(slug_clean: str) -> bool:
    """
    Checks whether a package from the GitHub repo has a new commit.
    Returns True if update is needed, False otherwise.
    """
    try:
        # Get latest commit hash from GitHub
        repo_url = f"https://github.com/universal-mcp/{slug_clean}.git"
        result = subprocess.run(
            ["git", "ls-remote", repo_url, "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        latest_commit = result.stdout.split()[0]

        # Get local installed package path
        package_path = os.path.join(UNIVERSAL_MCP_HOME, f"universal_mcp_{slug_clean.replace('-', '_')}")
        if not os.path.exists(package_path):
            logger.info(f"No local installation found for '{slug_clean}'. Update needed.")
            return True

        # Look for commit hash in package metadata (assuming stored in _version.py or similar)
        version_file = os.path.join(package_path, "_commit.txt")
        if not os.path.exists(version_file):
            logger.info(f"No version file found for '{slug_clean}'. Update needed.")
            return True

        with open(version_file, "r") as f:
            local_commit = f.read().strip()

        if local_commit != latest_commit:
            logger.info(f"Local commit {local_commit} != remote {latest_commit}. Update needed.")
            return True

        logger.info(f"'{slug_clean}' is up to date.")
        return False
    except Exception as e:
        logger.warning(f"Failed to check latest commit for '{slug_clean}': {e}")
        return True  # Assume update needed on error

def _import_class(module_path: str, class_name: str):
    """
    Helper to import a class by name from a module.
    Verifies whether the package is up-to-date based on GitHub HEAD commit.
    """
    slug_clean = module_path.split('.')[0].replace("universal_mcp_", "").replace("_", "-")

    try:
        module = importlib.import_module(module_path)

        # Only ensure latest if remote commit has changed
        if _check_for_package_update(slug_clean):
            _ensure_latest_package(slug_clean)
            module = importlib.reload(module)

    except ModuleNotFoundError as e:
        logger.debug(f"Import failed for module '{module_path}': {e}")
        _install_package(slug_clean)
        module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        logger.error(f"Class '{class_name}' not found in module '{module_path}'")
        raise ModuleNotFoundError(
            f"Class '{class_name}' not found in module '{module_path}'"
        ) from e


def _install_package(slug_clean: str):
    """
    Helper to install a package via pip from the universal-mcp GitHub repository.
    """
    repo_url = f"git+https://github.com/universal-mcp/{slug_clean}"
    cmd = ["uv", "pip", "install", repo_url, "--target", UNIVERSAL_MCP_HOME]
    logger.info(f"Installing package '{slug_clean}' with command: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        latest_commit = subprocess.check_output(
        ["git", "ls-remote", f"https://github.com/universal-mcp/{slug_clean}.git", "HEAD"]).decode().split()[0]
        package_path = os.path.join(UNIVERSAL_MCP_HOME, f"universal_mcp_{slug_clean.replace('-', '_')}")
        os.makedirs(package_path, exist_ok=True)
        with open(os.path.join(package_path, "_commit.txt"), "w") as f:
            f.write(latest_commit)
    except subprocess.CalledProcessError as e:
        logger.error(f"Installation failed for '{slug_clean}': {e}")
        raise ModuleNotFoundError(
            f"Installation failed for package '{slug_clean}'"
        ) from e
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

    logger.info(
        f"Resolving app for slug '{slug}' → module '{module_path}', class '{class_name}'"
    )
    try:
        return _import_class(module_path, class_name)
    except ModuleNotFoundError as orig_err:
        logger.warning(
            f"Module '{module_path}' not found locally: {orig_err}. Installing..."
        )
        _install_package(slug_clean)
        # Retry import after installation
        try:
            return _import_class(module_path, class_name)
        except ModuleNotFoundError as retry_err:
            logger.error(
                f"Still cannot import '{module_path}' after installation: {retry_err}"
            )
            raise


__all__ = [
    "app_from_slug",
    "BaseApplication",
    "APIApplication",
    "GraphQLApplication",
]
