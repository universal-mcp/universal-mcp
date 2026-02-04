import os
from typing import Any

from universal_mcp.exceptions import KeyNotFoundError
from universal_mcp.stores.base import BaseStore


class EnvironmentStore(BaseStore):
    """Credential and data store using operating system environment variables.

    This store implementation interacts directly with environment variables
    using `os.getenv`, `os.environ[]`, and `del os.environ[]`.
    Changes made via `set` or `delete` will affect the environment of the
    current Python process and potentially its subprocesses, but typically
    do not persist beyond the life of the parent shell or system session
    unless explicitly managed externally.
    """

    def get(self, key: str) -> Any:
        """Retrieves the value of an environment variable.

        Args:
            key (str): The name of the environment variable.

        Returns:
            Any: The value of the environment variable as a string.

        Raises:
            KeyNotFoundError: If the environment variable is not set.
        """
        value = os.getenv(key)
        if value is None:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        return value

    def set(self, key: str, value: Any) -> None:
        """Sets an environment variable in the current process.

        Args:
            key (str): The name of the environment variable.
            value (Any): The value to set for the environment variable.
                         It will be converted to a string.
        """
        os.environ[key] = str(value)

    def delete(self, key: str) -> None:
        """Deletes an environment variable from the current process.

        Args:
            key (str): The name of the environment variable to delete.

        Raises:
            KeyNotFoundError: If the environment variable is not set.
        """
        if key not in os.environ:
            raise KeyNotFoundError(f"Environment variable '{key}' not found")
        del os.environ[key]
