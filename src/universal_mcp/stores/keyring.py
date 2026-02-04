import keyring
from loguru import logger

from universal_mcp.exceptions import KeyNotFoundError, StoreError
from universal_mcp.stores.base import BaseStore


class KeyringStore(BaseStore):
    """Secure credential store using the system's keyring service.

    This store leverages the `keyring` library to interact with the
    operating system's native secure credential management system
    (e.g., macOS Keychain, Windows Credential Manager, Freedesktop Secret
    Service / KWallet on Linux). It is suitable for storing sensitive
    data like API keys and passwords persistently and securely.

    Attributes:
        app_name (str): The service name under which credentials are stored
                        in the system keyring. This helps namespace credentials
                        for different applications.
    """

    def __init__(self, app_name: str = "universal_mcp"):
        """Initializes the KeyringStore.

        Args:
            app_name (str, optional): The service name to use when interacting
                with the system keyring. This helps to namespace credentials.
                Defaults to "universal_mcp".
        """
        self.app_name = app_name

    def get(self, key: str) -> str:
        """Retrieves a secret (password) from the system keyring.

        Args:
            key (str): The username or key associated with the secret.

        Returns:
            str: The stored secret string.

        Raises:
            KeyNotFoundError: If the key is not found in the keyring under
                              `self.app_name`, or if `keyring` library errors occur.
        """
        try:
            logger.info(f"Getting password for {key} from keyring for app {self.app_name}")
            value = keyring.get_password(self.app_name, key)
            if value is None:
                raise KeyNotFoundError(f"Key '{key}' not found in keyring for app '{self.app_name}'")
            return value
        except Exception as e:  # Catches keyring specific errors too
            # Log the original exception e if needed
            raise KeyNotFoundError(
                f"Failed to retrieve key '{key}' from keyring for app '{self.app_name}'. Original error: {type(e).__name__}"
            ) from e  # Keep original exception context

    def set(self, key: str, value: str) -> None:
        """Stores a secret (password) in the system keyring.

        Args:
            key (str): The username or key to associate with the secret.
            value (str): The secret to store. It will be converted to a string.

        Raises:
            StoreError: If storing the secret in the keyring fails.
        """
        try:
            logger.info(f"Setting password for {key} in keyring for app {self.app_name}")
            keyring.set_password(self.app_name, key, str(value))
        except Exception as e:
            raise StoreError(f"Error storing key '{key}' in keyring for app '{self.app_name}': {str(e)}") from e

    def delete(self, key: str) -> None:
        """Deletes a secret (password) from the system keyring.

        Args:
            key (str): The username or key of the secret to delete.

        Raises:
            KeyNotFoundError: If the key is not found in the keyring (note: some
                              keyring backends might not raise an error for
                              non-existent keys, this tries to standardize).
            StoreError: If deleting the secret from the keyring fails for other
                        reasons.
        """
        try:
            logger.info(f"Deleting password for {key} from keyring for app {self.app_name}")
            # Attempt to get first to see if it exists, as delete might not error
            # This is a workaround for keyring's inconsistent behavior
            existing_value = keyring.get_password(self.app_name, key)
            if existing_value is None:
                raise KeyNotFoundError(f"Key '{key}' not found in keyring for app '{self.app_name}', cannot delete.")
            keyring.delete_password(self.app_name, key)
        except KeyNotFoundError:  # Re-raise if found by the get_password check
            raise
        except Exception as e:  # Catch other keyring errors
            raise StoreError(f"Error deleting key '{key}' from keyring for app '{self.app_name}': {str(e)}") from e
