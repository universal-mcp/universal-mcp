from mcp.client.auth import TokenStorage as MCPTokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

from universal_mcp.exceptions import KeyNotFoundError
from universal_mcp.stores.store import KeyringStore


class TokenStore(MCPTokenStorage):
    """Simple in-memory token storage implementation."""

    def __init__(self, store: KeyringStore):
        self.store = store
        self._tokens: OAuthToken | None = None
        self._client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        try:
            return OAuthToken.model_validate_json(self.store.get("tokens"))
        except KeyNotFoundError:
            return None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self.store.set("tokens", tokens.model_dump_json())

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        try:
            return OAuthClientInformationFull.model_validate_json(self.store.get("client_info"))
        except KeyNotFoundError:
            return None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self.store.set("client_info", client_info.model_dump_json())
