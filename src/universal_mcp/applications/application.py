from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx
from gql import Client as GraphQLClient
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode
from loguru import logger

from universal_mcp.integrations.integration import Integration

DEFAULT_API_TIMEOUT = 30  # seconds


async def _build_auth_headers(integration: "Integration | None") -> dict[str, str]:
    """Build authentication headers from an integration's credentials.

    Supports direct headers, API keys, and access tokens.
    """
    if not integration:
        return {}
    credentials = await integration.get_credentials()

    headers = credentials.get("headers")
    if headers:
        return headers

    api_key = credentials.get("api_key") or credentials.get("API_KEY") or credentials.get("apiKey")
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}

    access_token = credentials.get("access_token")
    if access_token:
        return {"Authorization": f"Bearer {access_token}"}

    return {}


class BaseApplication(ABC):
    """Defines the foundational structure for applications in Universal MCP.

    This abstract base class (ABC) outlines the common interface and core
    functionality that all concrete application classes must implement.
    It handles basic initialization, such as setting the application name,
    and mandates the implementation of a method to list available tools.
    Analytics for application loading are also tracked here.

    Attributes:
        name (str): The unique name identifying the application.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initializes the BaseApplication.

        Args:
            name (str): The unique name for this application instance.
            **kwargs (Any): Additional keyword arguments that might be specific
                             to the concrete application implementation. These are
                             logged but not directly used by BaseApplication.
        """
        self.name = name
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")

    @abstractmethod
    def list_tools(self) -> list[Callable]:
        """Lists all tools provided by this application.

        This method must be implemented by concrete subclasses to return
        a list of callable tool objects that the application exposes.

        Returns:
            list[Callable]: A list of callable objects, where each callable
                            represents a tool offered by the application.
        """
        pass


class APIApplication(BaseApplication):
    """Base class for applications interacting with RESTful HTTP APIs.

    Extends `BaseApplication` to provide functionalities specific to
    API-based integrations. This includes managing an `httpx.Client`
    for making HTTP requests, handling authentication headers, processing
    responses, and offering convenient methods for common HTTP verbs
    (GET, POST, PUT, DELETE, PATCH).

    Attributes:
        name (str): The name of the application.
        integration (Integration | None): An optional Integration object
            responsible for managing authentication and credentials.
        default_timeout (int): The default timeout in seconds for HTTP requests.
        base_url (str): The base URL for the API endpoint. This should be
                        set by the subclass.
        _client (httpx.Client | None): The internal httpx client instance.
    """

    def __init__(
        self,
        name: str,
        integration: Integration | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the APIApplication.

        Args:
            name (str): The unique name for this application instance.
            integration (Integration | None, optional): An Integration object
                to handle authentication. Defaults to None.
            **kwargs (Any): Additional keyword arguments passed to the
                             BaseApplication.
        """
        super().__init__(name, **kwargs)
        self.default_timeout: int = DEFAULT_API_TIMEOUT
        self.integration = integration
        logger.debug(f"Initializing APIApplication '{name}' with integration: {integration}")
        self.base_url: str = ""

    async def _get_headers(self) -> dict[str, str]:
        """Constructs HTTP headers for API requests based on the integration asynchronously.

        Returns:
            Dictionary of HTTP headers. Returns empty dict if no integration configured
            or no suitable credentials found.
        """
        return await _build_auth_headers(self.integration)

    @asynccontextmanager
    async def get_async_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Provides an initialized `httpx.AsyncClient` instance for use as a context manager.

        The client is configured with the `base_url` and headers derived
        from the `_get_headers` method.

        Returns:
            httpx.AsyncClient: A new `httpx.AsyncClient` instance.
        """
        headers = await self._get_headers()
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.default_timeout,
        ) as client:
            yield client

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Processes an HTTP response, checking for errors and parsing JSON.

        This method first calls `response.raise_for_status()` to raise an
        `httpx.HTTPStatusError` if the HTTP request failed. If successful,
        it attempts to parse the response body as JSON. If JSON parsing
        fails, it returns a dictionary containing the success status,
        status code, and raw text of the response.

        Args:
            response (httpx.Response): The HTTP response object from `httpx`.

        Returns:
            dict[str, Any]: The parsed JSON response as a dictionary, or
                            a status dictionary if JSON parsing is not possible
                            for a successful response.

        Raises:
            httpx.HTTPStatusError: If the HTTP response status code indicates
                                 an error (4xx or 5xx).
        """
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return {"status": "success", "status_code": response.status_code, "text": response.text}

    async def _request(
        self,
        method: str,
        url: str,
        data: Any = None,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an async HTTP request with content-type dispatching."""
        async with self.get_async_client() as client:
            kwargs: dict[str, Any] = {"params": params}

            if content_type == "multipart/form-data":
                kwargs["data"] = data
                kwargs["files"] = files
            elif content_type == "application/x-www-form-urlencoded":
                kwargs["headers"] = {"Content-Type": content_type}
                kwargs["data"] = data
            elif content_type == "application/json":
                kwargs["json"] = data
            else:
                kwargs["headers"] = {"Content-Type": content_type}
                kwargs["content"] = data

            response = await getattr(client, method)(url, **kwargs)
        return response

    async def _get(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes an asynchronous GET request to the specified URL.

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            params (dict[str, Any] | None, optional): Optional URL query parameters.

        Returns:
            httpx.Response: The raw HTTP response object.
        """
        async with self.get_async_client() as client:
            response = await client.get(url, params=params)
        return response

    async def _post(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Makes an asynchronous POST request to the specified URL.

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            data (Any): The data to send in the request body.
            params (dict[str, Any] | None, optional): Optional URL query parameters.
            content_type (str, optional): The Content-Type of the request body.
            files (dict[str, Any] | None, optional): A dictionary for file uploads.

        Returns:
            httpx.Response: The raw HTTP response object.
        """
        return await self._request("post", url, data, params, content_type, files)

    async def _put(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Makes an asynchronous PUT request to the specified URL.

        Args:
            url (str): The URL endpoint for the request.
            data (Any): The data to send in the request body.
            params (dict[str, Any] | None, optional): URL query parameters.
            content_type (str, optional): The Content-Type of the request body.
            files (dict[str, Any] | None, optional): A dictionary for file uploads.

        Returns:
            httpx.Response: The raw HTTP response object.
        """
        return await self._request("put", url, data, params, content_type, files)

    async def _delete(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes an asynchronous DELETE request to the specified URL.

        Args:
            url (str): The URL endpoint for the request.
            params (dict[str, Any] | None, optional): URL query parameters.

        Returns:
            httpx.Response: The raw HTTP response object.
        """
        async with self.get_async_client() as client:
            response = await client.delete(url, params=params)
        return response

    async def _patch(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Makes an asynchronous PATCH request to the specified URL.

        Args:
            url (str): The URL endpoint for the request.
            data (Any): The data to send in the request body.
            params (dict[str, Any] | None, optional): URL query parameters.
            content_type (str, optional): The Content-Type of the request body.
            files (dict[str, Any] | None, optional): A dictionary for file uploads.

        Returns:
            httpx.Response: The raw HTTP response object.
        """
        return await self._request("patch", url, data, params, content_type, files)


class GraphQLApplication(BaseApplication):
    """Base class for applications interacting with GraphQL APIs.

    Extends `BaseApplication` to facilitate interactions with services
    that provide a GraphQL endpoint. It manages a `gql.Client` for
    executing queries and mutations, handles authentication headers
    similarly to `APIApplication`, and provides dedicated methods for
    GraphQL operations.

    Attributes:
        name (str): The name of the application.
        base_url (str): The complete URL of the GraphQL endpoint.
        integration (Integration | None): An optional Integration object
            for managing authentication.
        _client (GraphQLClient | None): The internal `gql.Client` instance.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        integration: Integration | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the GraphQLApplication.

        Args:
            name (str): The unique name for this application instance.
            base_url (str): The full URL of the GraphQL endpoint.
            integration (Integration | None, optional): An Integration object
                to handle authentication. Defaults to None.
            client (GraphQLClient | None, optional): An existing `gql.Client`
                instance. If None, a new client will be created on demand.
                Defaults to None.
            async_client (GraphQLClient | None, optional): An existing async `gql.Client`
                instance. If None, a new client will be created on demand.
                Defaults to None.
            **kwargs (Any): Additional keyword arguments passed to the
                             BaseApplication.
        """
        super().__init__(name, **kwargs)
        self.base_url = base_url
        self.integration = integration
        self.default_timeout: float = DEFAULT_API_TIMEOUT
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")

    async def _get_headers(self) -> dict[str, str]:
        """Constructs HTTP headers for GraphQL requests based on the integration asynchronously.

        Returns:
            dict[str, str]: A dictionary of HTTP headers.
        """
        return await _build_auth_headers(self.integration)

    @asynccontextmanager
    async def get_async_client(self) -> AsyncGenerator[GraphQLClient, None]:
        """Provides an initialized async `gql.Client` instance.

        If a client was not provided during initialization or has not been
        created yet, this property instantiates a new `gql.Client`.
        The client is configured with an `AIOHTTPTransport` using the
        `base_url` and headers from `_get_headers`. It's also set to
        fetch the schema from the transport.

        Returns:
            GraphQLClient: The active async `gql.Client` instance.
        """
        headers = await self._get_headers()
        transport = AIOHTTPTransport(url=self.base_url, headers=headers)
        async with GraphQLClient(transport=transport, fetch_schema_from_transport=True) as client:
            yield client

    async def mutate(
        self,
        mutation: str | DocumentNode,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executes a GraphQL mutation asynchronously.

        Args:
            mutation (str | DocumentNode): The GraphQL mutation string or a
                pre-parsed `gql.DocumentNode` object. If a string is provided,
                it will be parsed using `gql()`.
            variables (dict[str, Any] | None, optional): A dictionary of variables
                to pass with the mutation. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response from the GraphQL server as a dictionary.

        Raises:
            Exception: If the GraphQL client encounters an error during execution
                       (e.g., network issue, GraphQL server error).
        """
        request = gql(mutation) if isinstance(mutation, str) else mutation
        async with self.get_async_client() as client:
            return await client.execute(request, variable_values=variables)  # type: ignore[arg-type]

    async def query(
        self,
        query: str | DocumentNode,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executes a GraphQL query asynchronously.

        Args:
            query (str | DocumentNode): The GraphQL query string or a
                pre-parsed `gql.DocumentNode` object. If a string is provided,
                it will be parsed using `gql()`.
            variables (dict[str, Any] | None, optional): A dictionary of variables
                to pass with the query. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response from the GraphQL server as a dictionary.

        Raises:
            Exception: If the GraphQL client encounters an error during execution
                               (e.g., network issue, GraphQL server error).
        """
        request = gql(query) if isinstance(query, str) else query
        async with self.get_async_client() as client:
            return await client.execute(request, variable_values=variables)  # type: ignore[arg-type]
