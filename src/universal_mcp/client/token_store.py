from mcp.client.auth import TokenStorage as MCPTokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

from universal_mcp.exceptions import KeyNotFoundError
from universal_mcp.stores.store import KeyringStore


class TokenStore(MCPTokenStorage):
    """Persistent storage for OAuth tokens and client information using KeyringStore.

    This class implements the `mcp.client.auth.TokenStorage` interface,
    providing a mechanism to securely store and retrieve OAuth 2.0 tokens
    (as `OAuthToken` objects) and OAuth client registration details
    (as `OAuthClientInformationFull` objects).

    It utilizes an underlying `KeyringStore` instance, which typically
    delegates to the operating system's secure credential management
    system (e.g., macOS Keychain, Windows Credential Manager, Linux KWallet).
    This ensures that sensitive token data is stored securely and persistently.

    Attributes:
        store (KeyringStore): The `KeyringStore` instance used for actually
            storing and retrieving the serialized token and client info data.
    """

    def __init__(self, store: KeyringStore):
        """Initializes the TokenStore.

        Args:
            store (KeyringStore): An instance of `KeyringStore` that will be
                used for the actual persistence of tokens and client information.
        """
        self.store = store
        # These are not meant to be persistent caches in this implementation
        # self._tokens: OAuthToken | None = None
        # self._client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        """Retrieves OAuth tokens from the persistent KeyringStore.

        Fetches the JSON string representation of tokens from the store using
        the key "tokens" and deserializes it into an `OAuthToken` object.

        Returns:
            OAuthToken | None: The deserialized `OAuthToken` object if found
                               and successfully parsed, otherwise None.
        """
        try:
            return OAuthToken.model_validate_json(self.store.get("tokens"))
        except KeyNotFoundError:
            return None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        """Serializes OAuth tokens to JSON and saves them to the KeyringStore.

        The provided `OAuthToken` object is converted to its JSON string
        representation and stored in the `KeyringStore` under the key "tokens".

        Args:
            tokens (OAuthToken): The `OAuthToken` object to store.
        """
        self.store.set("tokens", tokens.model_dump_json())

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        """Retrieves OAuth client information from the persistent KeyringStore.

        Fetches the JSON string representation of client information from the
        store using the key "client_info" and deserializes it into an
        `OAuthClientInformationFull` object.

        Returns:
            OAuthClientInformationFull | None: The deserialized object if found
                                              and successfully parsed, otherwise None.
        """
        try:
            return OAuthClientInformationFull.model_validate_json(self.store.get("client_info"))
        except KeyNotFoundError:
            return None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        """Serializes OAuth client information to JSON and saves it to KeyringStore.

        The provided `OAuthClientInformationFull` object is converted to its
        JSON string representation and stored in the `KeyringStore` under the
        key "client_info".

        Args:
            client_info (OAuthClientInformationFull): The client information object
                to store.
        """
        self.store.set("client_info", client_info.model_dump_json())
