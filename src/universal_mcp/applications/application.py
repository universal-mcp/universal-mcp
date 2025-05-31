from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import httpx
from gql import Client as GraphQLClient
from gql import gql
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode
from loguru import logger

from universal_mcp.analytics import analytics
from universal_mcp.integrations import Integration


class BaseApplication(ABC):
    """
    Base class for all applications in the Universal MCP system.

    This abstract base class defines the common interface and functionality
    that all applications must implement. It provides basic initialization
    and credential management capabilities.

    Attributes:
        name (str): The name of the application
        _credentials (Optional[Dict[str, Any]]): Cached credentials for the application
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """
        Initialize the base application.

        Args:
            name: The name of the application
            **kwargs: Additional keyword arguments passed to the application
        """
        self.name = name
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")
        analytics.track_app_loaded(name)  # Track app loading

    @abstractmethod
    def list_tools(self) -> list[Callable]:
        """
        List all available tools for the application.

        Returns:
            List[Any]: A list of tools available in the application
        """
        pass


class APIApplication(BaseApplication):
    """
    Application that uses HTTP APIs to interact with external services.

    This class provides a base implementation for applications that communicate
    with external services via HTTP APIs. It handles authentication, request
    management, and response processing.

    Attributes:
        name (str): The name of the application
        integration (Optional[Integration]): The integration configuration
        default_timeout (int): Default timeout for HTTP requests in seconds
        base_url (str): Base URL for API requests
    """

    def __init__(
        self,
        name: str,
        integration: Integration | None = None,
        client: httpx.Client | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the API application.

        Args:
            name: The name of the application
            integration: Optional integration configuration
            **kwargs: Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self.default_timeout: int = 180
        self.integration = integration
        logger.debug(f"Initializing APIApplication '{name}' with integration: {integration}")
        self._client: httpx.Client | None = client
        self.base_url: str = ""

    def _get_headers(self) -> dict[str, str]:
        """
        Get the headers for API requests.

        This method constructs the appropriate headers based on the available
        credentials. It supports various authentication methods including
        direct headers, API keys, and access tokens.

        Returns:
            Dict[str, str]: Headers to be used in API requests
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
        """
        Get the HTTP client instance.

        This property ensures that the HTTP client is properly initialized
        with the correct base URL and headers.

        Returns:
            httpx.Client: The initialized HTTP client
        """
        if not self._client:
            headers = self._get_headers()
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=headers,
                timeout=self.default_timeout,
            )
        return self._client

    def _handle_api_error(self, response: httpx.Response) -> None:
        """
        Handle API errors with full error context including status code and response body.
        
        This provides complete error information to LLMs including the actual API error
        response body, not just the HTTP status code.
        
        Args:
            response: The HTTP response to check for errors
            
        Raises:
            httpx.HTTPStatusError: If the response indicates an error status, with full error details
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                error_body = response.text if response.text else "<empty response>"
            except Exception:
                error_body = "<unable to read response>"
            
            # Create detailed error message with status code and full response
            error_message = f"HTTP {response.status_code}: {error_body}"
            
            logger.error(f"API Error: {error_message}")
            raise httpx.HTTPStatusError(
                error_message,
                request=exc.request,
                response=exc.response,
            ) from exc

    def _handle_response(self, response: httpx.Response) -> dict[str, Any] | str:
        """
        Handle successful API responses by automatically parsing JSON or returning success message.
        
        This method automatically handles JSON parsing for responses that contain JSON data,
        and returns appropriate success messages for operations that don't return JSON (like DELETE).
        
        Args:
            response: The HTTP response to process
            
        Returns:
            dict[str, Any] | str: Parsed JSON data if response contains JSON, 
                                 otherwise a success message with status code
        """
        # Use enhanced error handling that includes response body context
        self._handle_api_error(response)
        
        # Try to parse as JSON first
        try:
            if response.text.strip():  
                return response.json()
        except Exception:
            # If JSON parsing fails or response is empty, return success message
            pass
        
        # For non-JSON responses (like DELETE operations), return success message
        return f"Success: HTTP {response.status_code}"

    def _get(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """
        Make a GET request to the specified URL.

        Args:
            url: The URL to send the request to
            params: Optional query parameters

        Returns:
            httpx.Response: The raw HTTP response object

        Raises:
            httpx.HTTPStatusError: If the request fails (when raise_for_status() is called)
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
        """
        Make a POST request to the specified URL.

        Args:
            url: The URL to send the request to
            data: The data to send. For 'application/json', this is JSON-serializable.
                  For 'application/x-www-form-urlencoded' or 'multipart/form-data', this is a dict of form fields.
                  For other content types, this is raw bytes or string.
            params: Optional query parameters
            content_type: The Content-Type of the request body.
                         Examples: 'application/json', 'application/x-www-form-urlencoded',
                                   'multipart/form-data', 'application/octet-stream', 'text/plain'.
            files: Optional dictionary of files to upload for 'multipart/form-data'.
                   Example: {'file_field_name': ('filename.txt', open('file.txt', 'rb'), 'text/plain')}

        Returns:
            httpx.Response: The raw HTTP response object

        Raises:
            httpx.HTTPStatusError: If the request fails (when raise_for_status() is called)
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
        """
        Make a PUT request to the specified URL.

        Args:
            url: The URL to send the request to
            data: The data to send. For 'application/json', this is JSON-serializable.
                  For 'application/x-www-form-urlencoded' or 'multipart/form-data', this is a dict of form fields.
                  For other content types, this is raw bytes or string.
            params: Optional query parameters
            content_type: The Content-Type of the request body.
                         Examples: 'application/json', 'application/x-www-form-urlencoded',
                                   'multipart/form-data', 'application/octet-stream', 'text/plain'.
            files: Optional dictionary of files to upload for 'multipart/form-data'.
                   Example: {'file_field_name': ('filename.txt', open('file.txt', 'rb'), 'text/plain')}

        Returns:
            httpx.Response: The raw HTTP response object

        Raises:
            httpx.HTTPStatusError: If the request fails (when raise_for_status() is called)
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
        """
        Make a DELETE request to the specified URL.

        Args:
            url: The URL to send the request to
            params: Optional query parameters

        Returns:
            httpx.Response: The raw HTTP response object

        Raises:
            httpx.HTTPStatusError: If the request fails (when raise_for_status() is called)
        """
        logger.debug(f"Making DELETE request to {url} with params: {params}")
        response = self.client.delete(url, params=params, timeout=self.default_timeout)
        logger.debug(f"DELETE request successful with status code: {response.status_code}")
        return response

    def _patch(self, url: str, data: dict[str, Any], params: dict[str, Any] | None = None) -> httpx.Response:
        """
        Make a PATCH request to the specified URL.

        Args:
            url: The URL to send the request to
            data: The data to send in the request body
            params: Optional query parameters

        Returns:
            httpx.Response: The raw HTTP response object

        Raises:
            httpx.HTTPStatusError: If the request fails (when raise_for_status() is called)
        """
        logger.debug(f"Making PATCH request to {url} with params: {params} and data: {data}")
        response = self.client.patch(
            url,
            json=data,
            params=params,
        )
        logger.debug(f"PATCH request successful with status code: {response.status_code}")
        return response

    # New convenience methods that handle responses automatically with enhanced error handling
    def _get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | str:
        """
        Make a GET request and automatically handle the response with enhanced error handling.

        Args:
            url: The URL to send the request to
            params: Optional query parameters

        Returns:
            dict[str, Any] | str: Parsed JSON response if available, otherwise success message

        Raises:
            httpx.HTTPStatusError: If the request fails with detailed error information including response body
        """
        response = self._get(url, params)
        return self._handle_response(response)

    def _post_json(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """
        Make a POST request and automatically handle the response with enhanced error handling.

        Args:
            url: The URL to send the request to
            data: The data to send
            params: Optional query parameters
            content_type: The Content-Type of the request body
            files: Optional dictionary of files to upload

        Returns:
            dict[str, Any] | str: Parsed JSON response if available, otherwise success message

        Raises:
            httpx.HTTPStatusError: If the request fails with detailed error information including response body
        """
        response = self._post(url, data, params, content_type, files)
        return self._handle_response(response)

    def _put_json(
        self,
        url: str,
        data: Any,
        params: dict[str, Any] | None = None,
        content_type: str = "application/json",
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """
        Make a PUT request and automatically handle the response with enhanced error handling.

        Args:
            url: The URL to send the request to
            data: The data to send
            params: Optional query parameters
            content_type: The Content-Type of the request body
            files: Optional dictionary of files to upload

        Returns:
            dict[str, Any] | str: Parsed JSON response if available, otherwise success message

        Raises:
            httpx.HTTPStatusError: If the request fails with detailed error information including response body
        """
        response = self._put(url, data, params, content_type, files)
        return self._handle_response(response)

    def _delete_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | str:
        """
        Make a DELETE request and automatically handle the response with enhanced error handling.

        Args:
            url: The URL to send the request to
            params: Optional query parameters

        Returns:
            dict[str, Any] | str: Parsed JSON response if available, otherwise success message

        Raises:
            httpx.HTTPStatusError: If the request fails with detailed error information including response body
        """
        response = self._delete(url, params)
        return self._handle_response(response)

    def _patch_json(self, url: str, data: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any] | str:
        """
        Make a PATCH request and automatically handle the response with enhanced error handling.

        Args:
            url: The URL to send the request to
            data: The data to send in the request body
            params: Optional query parameters

        Returns:
            dict[str, Any] | str: Parsed JSON response if available, otherwise success message

        Raises:
            httpx.HTTPStatusError: If the request fails with detailed error information including response body
        """
        response = self._patch(url, data, params)
        return self._handle_response(response)


class GraphQLApplication(BaseApplication):
    """
    Application that uses GraphQL to interact with external services.

    This class provides a base implementation for applications that communicate
    with external services via GraphQL. It handles authentication, query execution,
    and response processing.

    Attributes:
        name (str): The name of the application
        base_url (str): Base URL for GraphQL endpoint
        integration (Optional[Integration]): The integration configuration
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        integration: Integration | None = None,
        client: GraphQLClient | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the GraphQL application.

        Args:
            name: The name of the application
            base_url: The base URL for the GraphQL endpoint
            integration: Optional integration configuration
            **kwargs: Additional keyword arguments
        """
        super().__init__(name, **kwargs)
        self.base_url = base_url
        self.integration = integration
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")
        self._client: GraphQLClient | None = client

    def _get_headers(self) -> dict[str, str]:
        """
        Get the headers for GraphQL requests.

        This method constructs the appropriate headers based on the available
        credentials. It supports various authentication methods including
        direct headers, API keys, and access tokens.

        Returns:
            Dict[str, str]: Headers to be used in GraphQL requests
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
        """
        Get the GraphQL client instance.

        This property ensures that the GraphQL client is properly initialized
        with the correct transport and headers.

        Returns:
            Client: The initialized GraphQL client
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
        """
        Execute a GraphQL mutation.

        Args:
            mutation: The GraphQL mutation string or DocumentNode
            variables: Optional variables for the mutation

        Returns:
            Dict[str, Any]: The result of the mutation

        Raises:
            Exception: If the mutation execution fails
        """
        if isinstance(mutation, str):
            mutation = gql(mutation)
        return self.client.execute(mutation, variable_values=variables)

    def query(
        self,
        query: str | DocumentNode,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: The GraphQL query string or DocumentNode
            variables: Optional variables for the query

        Returns:
            Dict[str, Any]: The result of the query

        Raises:
            Exception: If the query execution fails
        """
        if isinstance(query, str):
            query = gql(query)
        return self.client.execute(query, variable_values=variables)
