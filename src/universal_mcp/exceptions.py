class UniversalMCPError(Exception):
    """Base exception for all Universal MCP errors."""

    pass


class NotAuthorizedError(UniversalMCPError):
    """Raised when an action is attempted without necessary permissions.

    This typically occurs if a user or process tries to access a protected
    resource or perform an operation for which they lack the required
    authorization credentials or roles.
    """

    pass


class ToolError(UniversalMCPError):
    """Indicates an issue related to tool discovery, validation, or execution.

    This could be due to a tool not being found, failing during its
    operation, or having invalid configuration or arguments.
    """

    pass


class ToolNotFoundError(ToolError):
    """Raised when a tool is not found"""


class InvalidSignature(UniversalMCPError):
    """Raised when a cryptographic signature verification fails.

    This can occur during webhook validation or any other process that
    relies on verifying the authenticity and integrity of a message
    using a digital signature.
    """

    pass


class StoreError(UniversalMCPError):
    """Base exception for errors related to data or credential stores.

    This serves as a generic error for issues arising from operations
    on any storage backend (e.g., KeyringStore, EnvironmentStore).
    Specific store errors should ideally subclass this.
    """

    pass


class KeyNotFoundError(StoreError):
    """Raised when a specified key cannot be found in a data or credential store.

    This is a common error when attempting to retrieve a piece of data
    (e.g., an API key, token, or client information) that does not exist
    under the given identifier.
    """

    pass


class ConfigurationError(UniversalMCPError):
    """Indicates an error was detected in application or server configuration.

    This can be due to missing required settings, invalid values for
    configuration parameters, or inconsistencies in the provided setup.
    """

    pass
