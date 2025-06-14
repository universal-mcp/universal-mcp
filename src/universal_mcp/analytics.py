import os
import uuid
from functools import lru_cache
from importlib.metadata import version

import posthog
from loguru import logger


class Analytics:
    """A singleton class for tracking analytics events using PostHog.

    This class handles the initialization of the PostHog client and provides
    methods to track key events such as application loading and tool execution.
    Telemetry can be disabled by setting the TELEMETRY_DISABLED environment
    variable to "true".
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes the PostHog client and sets up analytics properties.

        This internal method configures the PostHog API key and host.
        It also determines if analytics should be enabled based on the
        TELEMETRY_DISABLED environment variable and generates a unique
        user ID.
        """
        posthog.host = "https://us.i.posthog.com"
        posthog.api_key = "phc_6HXMDi8CjfIW0l04l34L7IDkpCDeOVz9cOz1KLAHXh8"
        self.enabled = os.getenv("TELEMETRY_DISABLED", "false").lower() != "true"
        self.user_id = str(uuid.uuid4())[:8]

    @staticmethod
    @lru_cache(maxsize=1)
    def get_version():
        """Retrieves the installed version of the universal_mcp package.

        Uses importlib.metadata to get the package version.
        Caches the result for efficiency.

        Returns:
            str: The package version string, or "unknown" if not found.
        """
        try:
            return version("universal_mcp")
        except ImportError:  # Should be PackageNotFoundError, but matching existing code
            return "unknown"

    def track_app_loaded(self, app_name: str):
        """Tracks an event when an application is successfully loaded.

        This event helps understand which applications are being utilized.

        Args:
            app_name (str): The name of the application that was loaded.
        """
        if not self.enabled:
            return
        try:
            properties = {
                "version": self.get_version(),
                "app_name": app_name,
            }
            posthog.capture(self.user_id, "app_loaded", properties)
        except Exception as e:
            logger.error(f"Failed to track app_loaded event: {e}")

    def track_tool_called(
        self,
        tool_name: str,
        app_name: str,
        status: str,
        error: str = None,
        user_id=None,  # Note: user_id is captured in PostHog but not used from this param
    ):
        """Tracks an event when a tool is called within an application.

        This event provides insights into tool usage patterns, success rates,
        and potential errors.

        Args:
            tool_name (str): The name of the tool that was called.
            app_name (str): The name of the application the tool belongs to.
            status (str): The status of the tool call (e.g., "success", "error").
            error (str, optional): The error message if the tool call failed.
                                 Defaults to None.
            user_id (str, optional): An optional user identifier.
                                   Note: Currently, the class uses an internally
                                   generated user_id for PostHog events.
        """
        if not self.enabled:
            return
        try:
            properties = {
                "tool_name": tool_name,
                "app_name": app_name,
                "status": status,
                "error": error,
                "version": self.get_version(),
            }
            posthog.capture(self.user_id, "tool_called", properties)
        except Exception as e:
            logger.error(f"Failed to track tool_called event: {e}")


analytics = Analytics()
