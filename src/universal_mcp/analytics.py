import os
import uuid
from functools import lru_cache
from importlib.metadata import version

import posthog
from loguru import logger


class Analytics:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the Analytics singleton"""
        posthog.host = "https://us.i.posthog.com"
        posthog.api_key = "phc_6HXMDi8CjfIW0l04l34L7IDkpCDeOVz9cOz1KLAHXh8"
        self.enabled = os.getenv("TELEMETRY_DISABLED", "false").lower() != "true"
        self.user_id = str(uuid.uuid4())[:8]

    @staticmethod
    @lru_cache(maxsize=1)
    def get_version():
        """
        Get the version of the Universal MCP
        """
        try:
            return version("universal_mcp")
        except ImportError:
            return "unknown"

    def track_app_loaded(self, app_name: str):
        """Track when the app is loaded"""
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
        user_id=None,
    ):
        """Track when a tool is called

        Args:
            tool_name: Name of the tool being called
            status: Status of the tool call (success/error)
            error: Error message if status is error
            user_id: Optional user ID to track
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
