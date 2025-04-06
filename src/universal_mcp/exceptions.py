class NotAuthorizedError(Exception):
    """Raised when a user is not authorized to access a resource or perform an action."""

    def __init__(self, message="Not authorized to perform this action"):
        self.message = message
        super().__init__(self.message)
