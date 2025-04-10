import os
import sys
import uuid

from loguru import logger


def get_user_id():
    """
    Generate a unique user ID for the current session
    """
    return "universal_" + str(uuid.uuid4())[:8]


def posthog_sink(message, user_id=get_user_id()):
    """
    Custom sink for sending logs to PostHog
    """
    try:
        import posthog

        posthog.host = "https://us.i.posthog.com"
        posthog.api_key = "phc_6HXMDi8CjfIW0l04l34L7IDkpCDeOVz9cOz1KLAHXh8"

        record = message.record
        properties = {
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
        }
        posthog.capture(user_id, "universal_mcp", properties)
    except Exception:
        # Silently fail if PostHog capture fails - don't want logging to break the app
        pass


def setup_logger():
    logger.remove()
    logger.add(
        sink=sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    logger.add(
        sink=sys.stderr,
        format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="ERROR",
        colorize=True,
    )
    telemetry_enabled = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
    if telemetry_enabled:
        logger.add(posthog_sink, level="INFO")  # PostHog telemetry


setup_logger()
