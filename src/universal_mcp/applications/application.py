from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx
from gql import Client as GraphQLClient
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode
from loguru import logger

from universal_mcp.integrations.integration import Integration

DEFAULT_API_TIMEOUT = 30  # seconds


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

        Retrieves credentials from the configured `integration` asynchronously and
        attempts to create appropriate authentication headers. It supports direct header
        injection, API keys (as Bearer tokens), and access tokens (as Bearer tokens).

        Returns:
            Dictionary of HTTP headers. Returns empty dict if no integration configured
            or no suitable credentials found.
        """
        if not self.integration:
            logger.debug("No integration configured, returning empty headers")
            return {}
        credentials = await self.integration.get_credentials()
        logger.debug("Got credentials for integration")

        # Check if direct headers are provided
        headers = credentials.get("headers")
        if headers:
            logger.debug("Using direct headers from credentials")
            return headers

        # Check if api key is provided
        api_key = credentials.get("api_key") or credentials.get("API_KEY") or credentials.get("apiKey")
        if api_key:
            logger.debug("Using API key from credentials")
            return {
                "Authorization": f"Bearer {api_key}",
            }
        # Check if access token is provided
        access_token = credentials.get("access_token")
        if access_token:
            logger.debug("Using access token from credentials")
            return {
                "Authorization": f"Bearer {access_token}",
            }
        logger.debug("No authentication found in credentials, returning empty headers")
        return {}

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

    async def _get(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes an asynchronous GET request to the specified URL.

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            params (dict[str, Any] | None, optional): Optional URL query parameters.
                Defaults to None.

        Returns:
            httpx.Response: The raw HTTP response object. The `_handle_response`
                            method should typically be used to process this.

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(f"Making async GET request to {url} with params: {params}")
        async with self.get_async_client() as client:
            response = await client.get(url, params=params)
        logger.debug(f"Async GET request successful with status code: {response.status_code}")
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

        Handles different `content_type` values for sending data,
        including 'application/json', 'application/x-www-form-urlencoded',
        and 'multipart/form-data' (for file uploads).

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            data (Any): The data to send in the request body.
            params (dict[str, Any] | None, optional): Optional URL query parameters.
            content_type (str, optional): The Content-Type of the request body.
            files (dict[str, Any] | None, optional): A dictionary for file uploads.

        Returns:
            httpx.Response: The raw HTTP response object.

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(
            f"Making async POST request to {url} with params: {params}, data type: {type(data)}, content_type={content_type}, files: {'yes' if files else 'no'}"
        )
        async with self.get_async_client() as client:
            if content_type == "multipart/form-data":
                response = await client.post(
                    url,
                    data=data,
                    files=files,
                    params=params,
                )
            elif content_type == "application/x-www-form-urlencoded":
                headers = {"Content-Type": content_type}  # Explicitly set Content-Type for form data.
                response = await client.post(
                    url,
                    headers=headers,
                    data=data,
                    params=params,
                )
            elif content_type == "application/json":
                response = await client.post(
                    url,
                    json=data,  # httpx automatically sets Content-Type for json=data.
                    params=params,
                )
            else:
                headers = {"Content-Type": content_type}  # Explicitly set Content-Type for other content types.
                response = await client.post(
                    url,
                    headers=headers,
                    content=data,
                    params=params,
                )
        logger.debug(f"Async POST request successful with status code: {response.status_code}")
        return response

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

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(
            f"Making async PUT request to {url} with params: {params}, data type: {type(data)}, content_type={content_type}, files: {'yes' if files else 'no'}"
        )
        async with self.get_async_client() as client:
            if content_type == "multipart/form-data":
                response = await client.put(
                    url,
                    data=data,
                    files=files,
                    params=params,
                )
            elif content_type == "application/x-www-form-urlencoded":
                headers = {"Content-Type": content_type}  # Explicitly set Content-Type for form data.
                response = await client.put(
                    url,
                    headers=headers,
                    data=data,
                    params=params,
                )
            elif content_type == "application/json":
                response = await client.put(
                    url,
                    json=data,  # httpx automatically sets Content-Type for json=data.
                    params=params,
                )
            else:
                headers = {"Content-Type": content_type}  # Explicitly set Content-Type for other content types.
                response = await client.put(
                    url,
                    headers=headers,
                    content=data,
                    params=params,
                )
        logger.debug(f"Async PUT request successful with status code: {response.status_code}")
        return response

    async def _delete(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes an asynchronous DELETE request to the specified URL.

        Args:
            url (str): The URL endpoint for the request.
            params (dict[str, Any] | None, optional): URL query parameters.

        Returns:
            httpx.Response: The raw HTTP response object.

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(f"Making async DELETE request to {url} with params: {params}")
        async with self.get_async_client() as client:
            response = await client.delete(url, params=params)
        logger.debug(f"Async DELETE request successful with status code: {response.status_code}")
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
        logger.debug(
            f"Making async PATCH request to {url} with params: {params}, data type: {type(data)}, content_type={content_type}, files: {'yes' if files else 'no'}"
        )
        async with self.get_async_client() as client:
            if content_type == "multipart/form-data":
                response = await client.patch(url, data=data, files=files, params=params)
            elif content_type == "application/x-www-form-urlencoded":
                headers = {"Content-Type": content_type}
                response = await client.patch(url, headers=headers, data=data, params=params)
            elif content_type == "application/json":
                response = await client.patch(url, json=data, params=params)
            else:
                headers = {"Content-Type": content_type}
                response = await client.patch(url, headers=headers, content=data, params=params)
        logger.debug(f"Async PATCH request successful with status code: {response.status_code}")
        return response


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
        if not self.integration:
            logger.debug("No integration configured, returning empty headers")
            return {}
        credentials = await self.integration.get_credentials()
        logger.debug(f"Got credentials for integration: {credentials.keys()}")

        # Check if direct headers are provided
        headers = credentials.get("headers")
        if headers:
            logger.debug("Using direct headers from credentials")
            return headers

        # Check if api key is provided
        api_key = credentials.get("api_key") or credentials.get("API_KEY") or credentials.get("apiKey")
        if api_key:
            logger.debug("Using API key from credentials")
            return {
                "Authorization": f"Bearer {api_key}",
            }

        # Check if access token is provided
        access_token = credentials.get("access_token")
        if access_token:
            logger.debug("Using access token from credentials")
            return {
                "Authorization": f"Bearer {access_token}",
            }
        logger.debug("No authentication found in credentials, returning empty headers")
        return {}

    @contextmanager
    def get_sync_client(self) -> Generator[GraphQLClient, None, None]:
        """Provides an initialized synchronous `gql.Client` instance.

        If a client was not provided during initialization or has not been
        created yet, this property instantiates a new `gql.Client`.
        The client is configured with a `RequestsHTTPTransport` using the
        `base_url` and headers. It's also set to fetch the schema from the transport.

        Returns:
            GraphQLClient: The active `gql.Client` instance.
        """
        # For sync context manager, we can't call async _get_headers()
        # Return empty headers if no integration configured
        headers = {}
        if self.integration:
            logger.warning("Sync GraphQL client cannot use async integration credentials. Use get_async_client() instead.")
        transport = RequestsHTTPTransport(url=self.base_url, headers=headers)
        with GraphQLClient(transport=transport, fetch_schema_from_transport=True) as client:
            yield client

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
