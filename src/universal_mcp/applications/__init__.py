import importlib

from loguru import logger

from universal_mcp.applications.application import APIApplication, Application

# Name are in the format of "app-name", eg, google-calendar
# Folder name is "app_name", eg, google_calendar
# Class name is NameApp, eg, GoogleCalendarApp


def app_from_slug(slug: str):
    name = slug.lower().strip()
    app_name = "".join(word.title() for word in name.split("-")) + "App"
    folder_name = name.replace("-", "_").lower()
    logger.info(f"Importing {app_name} from {folder_name}")
    module = importlib.import_module(f"universal_mcp.applications.{folder_name}.app")
    app_class = getattr(module, app_name)
    return app_class


__all__ = [
    "app_from_slug",
    "Application",
    "APIApplication",
]
