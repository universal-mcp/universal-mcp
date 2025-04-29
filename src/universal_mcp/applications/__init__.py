import importlib
import subprocess
from loguru import logger

from universal_mcp.applications.application import (
    APIApplication,
    BaseApplication,
    GraphQLApplication,
)

# Name are in the format of "app-name", eg, google-calendar
# Folder name is "app_name", eg, google_calendar
# Class name is NameApp, eg, GoogleCalendarApp


def app_from_slug(slug: str):
    name = slug.lower().strip()
    app_name = "".join(word.title() for word in name.split("-")) + "App"
    slug_underscored = name.replace("-", "_")
    package_name = f"universal_mcp_{slug_underscored}"
    logger.info(f"Attempting to import {package_name} from installed packages")
    try:
        module = importlib.import_module(f"{package_name}.app")
        app_class = getattr(module, app_name)
        return app_class
    except ModuleNotFoundError:
        logger.warning(f"Module '{package_name}' not found. Attempting to install from AgentR.")
        install_command = ["uv", "pip", "install", f"git+https://github.com/universal-mcp/{name}"]
        try:
            subprocess.check_call(install_command)
            logger.info(f"Successfully installed 'universal-mcp-{name}'.Attempting import again.")
            module = importlib.import_module(f"{package_name}.app")
            logger.info(f"Successfully imported {package_name} from installed packages")
            app_class = getattr(module, app_name)
            return app_class
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing 'universal-mcp-{name}': {e}")
            raise ModuleNotFoundError(f"Could not find or install module 'universal-mcp-{name}'") from e
        except ModuleNotFoundError:
            logger.error(f"Module '{slug_underscored}.app' not found even after installation.")
            raise

__all__ = [
    "app_from_slug",
    "BaseApplication",
    "APIApplication",
    "GraphQLApplication",
]
