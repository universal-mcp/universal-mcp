from universal_mcp.integrations.integration import Integration

from .client import AgentrClient


class AgentrIntegration(Integration):
    """Manages authentication and authorization via the AgentR platform.

    This integration uses an `AgentrClient` to interact with the AgentR API
    for operations like retrieving authorization URLs and fetching stored
    credentials. It simplifies integration with services supported by AgentR.

    Attributes:
        name (str): Name of the integration (e.g., "github", "google").
        store (BaseStore): Store, typically not used directly by this class
                       as AgentR manages the primary credential storage.
        client (AgentrClient): Client for communicating with the AgentR API.
        _credentials (dict | None): Cached credentials.
    """

    def __init__(
        self,
        name: str,
        client: AgentrClient | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        """Initializes the AgentRIntegration.

        Args:
            name (str): The name of the service integration as configured on
                        the AgentR platform (e.g., "github").
            client (AgentrClient | None, optional): The AgentR client. If not provided,
                                                   a new `AgentrClient` will be created.
            api_key (str | None, optional): API key for AgentR. If not provided,
                                           will be loaded from environment variables.
            base_url (str | None, optional): Base URL for AgentR API. If not provided,
                                            will be loaded from environment variables.
            **kwargs: Additional arguments passed to the parent `Integration`.
        """
        super().__init__(name, **kwargs)
        self.type = "agentr"
        self.client = client or AgentrClient(api_key=api_key, base_url=base_url)
        self._credentials = None

    def set_credentials(self, credentials: dict[str, str] | None = None) -> str:
        """Not used for direct credential setting; initiates authorization instead.

        For AgentR integrations, credentials are set via the AgentR platform's
        OAuth flow. This method effectively redirects to the `authorize` flow.

        Args:
            credentials (dict | None, optional): Not used by this implementation.

        Returns:
            str: The authorization URL or message from the `authorize()` method.
        """
        raise NotImplementedError("AgentR integrations do not support direct credential setting")

    @property
    def credentials(self):
        """Retrieves credentials from the AgentR API, with caching.

        If credentials are not cached locally (in `_credentials`), this property
        fetches them from the AgentR platform using `self.client.get_credentials`.

        Returns:
            dict: The credentials dictionary obtained from AgentR.

        Raises:
            NotAuthorizedError: If credentials are not found (e.g., 404 from AgentR).
            httpx.HTTPStatusError: For other API errors from AgentR.
        """
        if self._credentials is not None:
            return self._credentials
        self._credentials = self.client.get_credentials(self.name)
        return self._credentials

    def get_credentials(self):
        """Retrieves credentials from the AgentR API. Alias for `credentials` property.

        Returns:
            dict: The credentials dictionary obtained from AgentR.

        Raises:
            NotAuthorizedError: If credentials are not found.
            httpx.HTTPStatusError: For other API errors.
        """
        return self.credentials

    def authorize(self) -> str:
        """Retrieves the authorization URL from the AgentR platform.

        This URL should be presented to the user to initiate the OAuth flow
        managed by AgentR for the service associated with `self.name`.

        Returns:
            str: The authorization URL.

        Raises:
            httpx.HTTPStatusError: If the API request to AgentR fails.
        """
        return self.client.get_authorization_url(self.name)
