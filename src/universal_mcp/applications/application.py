from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import httpx
from gql import Client as GraphQLClient
from gql import gql
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
        client: httpx.Client | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the APIApplication.

        Args:
            name (str): The unique name for this application instance.
            integration (Integration | None, optional): An Integration object
                to handle authentication. Defaults to None.
            client (httpx.Client | None, optional): An existing httpx.Client
                instance. If None, a new client will be created on demand.
                Defaults to None.
            **kwargs (Any): Additional keyword arguments passed to the
                             BaseApplication.
        """
        super().__init__(name, **kwargs)
        self.default_timeout: int = DEFAULT_API_TIMEOUT
        self.integration = integration
        logger.debug(f"Initializing APIApplication '{name}' with integration: {integration}")
        self._client: httpx.Client | None = client
        self.base_url: str = ""

    def _get_headers(self) -> dict[str, str]:
        """Constructs HTTP headers for API requests based on the integration.

        Retrieves credentials from the configured `integration` and attempts
        to create appropriate authentication headers. It supports direct header
        injection, API keys (as Bearer tokens), and access tokens (as Bearer
        tokens).

        Returns:
            dict[str, str]: A dictionary of HTTP headers. Returns an empty
                            dictionary if no integration is configured or if
                            no suitable credentials are found.
        """
        if not self.integration:
            logger.debug("No integration configured, returning empty headers")
            return {}
        credentials = self.integration.get_credentials()
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
                "Content-Type": "application/json",
            }

        # Check if access token is provided
        access_token = credentials.get("access_token")
        if access_token:
            logger.debug("Using access token from credentials")
            return {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        logger.debug("No authentication found in credentials, returning empty headers")
        return {}

    @property
    def client(self) -> httpx.Client:
        """Provides an initialized `httpx.Client` instance.

        If a client was not provided during initialization or has not been
        created yet, this property will instantiate a new `httpx.Client`.
        The client is configured with the `base_url` and headers derived
        from the `_get_headers` method.

        Returns:
            httpx.Client: The active `httpx.Client` instance.
        """
        if not self._client:
            headers = self._get_headers()
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=headers,
                timeout=self.default_timeout,
            )
        return self._client

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

    def _get(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes a GET request to the specified URL.

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
        logger.debug(f"Making GET request to {url} with params: {params}")
        response = self.client.get(url, params=params)
        logger.debug(f"GET request successful with status code: {response.status_code}")
        return response

    def _post(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Makes a POST request to the specified URL.

        Handles different `content_type` values for sending data,
        including 'application/json', 'application/x-www-form-urlencoded',
        and 'multipart/form-data' (for file uploads).

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            data (Any): The data to send in the request body.
                For 'application/json', this should be a JSON-serializable object.
                For 'application/x-www-form-urlencoded' or 'multipart/form-data' (if `files` is None),
                this should be a dictionary of form fields.
                For other content types (e.g., 'application/octet-stream'), this should be bytes or a string.
            params (dict[str, Any] | None, optional): Optional URL query parameters.
                Defaults to None.
            content_type (str, optional): The Content-Type of the request body.
                Defaults to "application/json".
            files (dict[str, Any] | None, optional): A dictionary for file uploads
                when `content_type` is 'multipart/form-data'.
                Example: `{'file_field': ('filename.txt', open('file.txt', 'rb'), 'text/plain')}`.
                Defaults to None.

        Returns:
            httpx.Response: The raw HTTP response object. The `_handle_response`
                            method should typically be used to process this.

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(
            f"Making POST request to {url} with params: {params}, data type: {type(data)}, content_type={content_type}, files: {'yes' if files else 'no'}"
        )
        headers = self._get_headers().copy()

        if content_type != "multipart/form-data":
            headers["Content-Type"] = content_type

        if content_type == "multipart/form-data":
            response = self.client.post(
                url,
                headers=headers,
                data=data,  # For regular form fields
                files=files,  # For file parts
                params=params,
            )
        elif content_type == "application/x-www-form-urlencoded":
            response = self.client.post(
                url,
                headers=headers,
                data=data,
                params=params,
            )
        elif content_type == "application/json":
            response = self.client.post(
                url,
                headers=headers,
                json=data,
                params=params,
            )
        else:  # Handles 'application/octet-stream', 'text/plain', 'image/jpeg', etc.
            response = self.client.post(
                url,
                headers=headers,
                content=data,  # Expect data to be bytes or str
                params=params,
            )
        logger.debug(f"POST request successful with status code: {response.status_code}")
        return response

    def _put(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Makes a PUT request to the specified URL.

        Handles different `content_type` values for sending data,
        including 'application/json', 'application/x-www-form-urlencoded',
        and 'multipart/form-data' (for file uploads).

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            data (Any): The data to send in the request body.
                For 'application/json', this should be a JSON-serializable object.
                For 'application/x-www-form-urlencoded' or 'multipart/form-data' (if `files` is None),
                this should be a dictionary of form fields.
                For other content types (e.g., 'application/octet-stream'), this should be bytes or a string.
            params (dict[str, Any] | None, optional): Optional URL query parameters.
                Defaults to None.
            content_type (str, optional): The Content-Type of the request body.
                Defaults to "application/json".
            files (dict[str, Any] | None, optional): A dictionary for file uploads
                when `content_type` is 'multipart/form-data'.
                Example: `{'file_field': ('filename.txt', open('file.txt', 'rb'), 'text/plain')}`.
                Defaults to None.

        Returns:
            httpx.Response: The raw HTTP response object. The `_handle_response`
                            method should typically be used to process this.

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(
            f"Making PUT request to {url} with params: {params}, data type: {type(data)}, content_type={content_type}, files: {'yes' if files else 'no'}"
        )
        headers = self._get_headers().copy()
        # For multipart/form-data, httpx handles the Content-Type header (with boundary)
        # For other content types, we set it explicitly.
        if content_type != "multipart/form-data":
            headers["Content-Type"] = content_type

        if content_type == "multipart/form-data":
            response = self.client.put(
                url,
                headers=headers,
                data=data,  # For regular form fields
                files=files,  # For file parts
                params=params,
            )
        elif content_type == "application/x-www-form-urlencoded":
            response = self.client.put(
                url,
                headers=headers,
                data=data,
                params=params,
            )
        elif content_type == "application/json":
            response = self.client.put(
                url,
                headers=headers,
                json=data,
                params=params,
            )
        else:  # Handles 'application/octet-stream', 'text/plain', 'image/jpeg', etc.
            response = self.client.put(
                url,
                headers=headers,
                content=data,  # Expect data to be bytes or str
                params=params,
            )
        logger.debug(f"PUT request successful with status code: {response.status_code}")
        return response

    def _delete(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes a DELETE request to the specified URL.

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
        logger.debug(f"Making DELETE request to {url} with params: {params}")
        response = self.client.delete(url, params=params, timeout=self.default_timeout)
        logger.debug(f"DELETE request successful with status code: {response.status_code}")
        return response

    def _patch(self, url: str, data: dict[str, Any], params: dict[str, Any] | None = None) -> httpx.Response:
        """Makes a PATCH request to the specified URL.

        Args:
            url (str): The URL endpoint for the request (relative to `base_url`).
            data (dict[str, Any]): The JSON-serializable data to send in the
                request body.
            params (dict[str, Any] | None, optional): Optional URL query parameters.
                Defaults to None.

        Returns:
            httpx.Response: The raw HTTP response object. The `_handle_response`
                            method should typically be used to process this.

        Raises:
            httpx.HTTPStatusError: Propagated if the underlying client request fails.
        """
        logger.debug(f"Making PATCH request to {url} with params: {params} and data: {data}")
        response = self.client.patch(
            url,
            json=data,
            params=params,
        )
        logger.debug(f"PATCH request successful with status code: {response.status_code}")
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
        client: GraphQLClient | None = None,
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
            **kwargs (Any): Additional keyword arguments passed to the
                             BaseApplication.
        """
        super().__init__(name, **kwargs)
        self.base_url = base_url
        self.integration = integration
        self.default_timeout: float = DEFAULT_API_TIMEOUT
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")
        self._client: GraphQLClient | None = client

    def _get_headers(self) -> dict[str, str]:
        """Constructs HTTP headers for GraphQL requests based on the integration.

        Retrieves credentials from the configured `integration` and attempts
        to create appropriate authentication headers. Primarily supports
        API keys or access tokens as Bearer tokens in the Authorization header.

        Returns:
            dict[str, str]: A dictionary of HTTP headers. Returns an empty
                            dictionary if no integration is configured or if
                            no suitable credentials are found.
        """
        if not self.integration:
            logger.debug("No integration configured, returning empty headers")
            return {}
        credentials = self.integration.get_credentials()
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

    @property
    def client(self) -> GraphQLClient:
        """Provides an initialized `gql.Client` instance.

        If a client was not provided during initialization or has not been
        created yet, this property instantiates a new `gql.Client`.
        The client is configured with a `RequestsHTTPTransport` using the
        `base_url` and headers from `_get_headers`. It's also set to
        fetch the schema from the transport.

        Returns:
            GraphQLClient: The active `gql.Client` instance.
        """
        if not self._client:
            headers = self._get_headers()
            transport = RequestsHTTPTransport(url=self.base_url, headers=headers)
            self._client = GraphQLClient(transport=transport, fetch_schema_from_transport=True)
        return self._client

    def mutate(
        self,
        mutation: str | DocumentNode,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executes a GraphQL mutation.

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
        if isinstance(mutation, str):
            mutation = gql(mutation)
        return self.client.execute(mutation, variable_values=variables)

    def query(
        self,
        query: str | DocumentNode,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executes a GraphQL query.

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
        if isinstance(query, str):
            query = gql(query)
        return self.client.execute(query, variable_values=variables)
