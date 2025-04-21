class NotAuthorizedError(Exception):
    """Raised when a user is not authorized to access a resource or perform an action."""

    def __init__(self, message: str):
        self.message = message


class ToolError(Exception):
    """Raised when a tool is not found or fails to execute."""


class InvalidSignature(Exception):
    """Raised when a signature is invalid."""
