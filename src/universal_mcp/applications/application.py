from abc import ABC, abstractmethod
from typing import Union
import httpx
from loguru import logger

from universal_mcp.analytics import analytics
from universal_mcp.integrations import Integration
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class BaseApplication(ABC):
    """
    BaseApplication is the base class for all applications.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")
        analytics.track_app_loaded(name)  # Track app loading

    @abstractmethod
    def list_tools(self):
        pass


class APIApplication(BaseApplication):
    """
    APIApplication is an application that uses an API to interact with the world.
    """

    def __init__(self, name: str, integration: Integration = None, **kwargs):
        super().__init__(name, **kwargs)
        self.default_timeout = 180
        self.integration = integration
        logger.debug(
            f"Initializing APIApplication '{name}' with integration: {integration}"
        )
        self._client = None

    def _get_headers(self):
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
        api_key = (
            credentials.get("api_key")
            or credentials.get("API_KEY")
            or credentials.get("apiKey")
        )
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
    def client(self):
        if not self._client:
            headers = self._get_headers()
            self._client = httpx.Client(headers=headers, timeout=self.default_timeout)
        return self._client

    def _get(self, url, params=None):
        logger.debug(f"Making GET request to {url} with params: {params}")
        response = self.client.get(
            url, params=params
        )
        response.raise_for_status()
        logger.debug(
            f"GET request successful with status code: {response.status_code}"
        )
        return response

    def _post(self, url, data, params=None):
        logger.debug(
            f"Making POST request to {url} with params: {params} and data: {data}"
        )
        response = self.client.post(
            url,
            json=data,
            params=params,
        )
        response.raise_for_status()
        logger.debug(
            f"POST request successful with status code: {response.status_code}"
        )
        return response
    

    def _put(self, url, data, params=None):
        logger.debug(
            f"Making PUT request to {url} with params: {params} and data: {data}"
        )
        response = self.client.put(
            url,
            json=data,
            params=params,
        )
        response.raise_for_status()
        logger.debug(
            f"PUT request successful with status code: {response.status_code}"
        )
        return response
    

    def _delete(self, url, params=None):
        logger.debug(f"Making DELETE request to {url} with params: {params}")
        response = self.client.delete(
            url, params=params, timeout=self.default_timeout
        )
        response.raise_for_status()
        logger.debug(
            f"DELETE request successful with status code: {response.status_code}"
        )
        return response


    def _patch(self, url, data, params=None):
        logger.debug(
            f"Making PATCH request to {url} with params: {params} and data: {data}"
        )
        response = self.client.patch(
            url,
            json=data,
            params=params,
        )
        response.raise_for_status()
        logger.debug(
            f"PATCH request successful with status code: {response.status_code}"
        )
        return response

    def validate(self):
        pass




class GraphQLApplication(BaseApplication):
    """
    GraphQLApplication is a collection of tools that can be used by an agent.
    """

    def __init__(self, name: str, base_url: str, integration: Integration = None, **kwargs):
        super().__init__(name,**kwargs)
        self.base_url = base_url
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")
        analytics.track_app_loaded(name)  # Track app loading
        self._client = None

    def _get_headers(self):
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
        api_key = (
            credentials.get("api_key")
            or credentials.get("API_KEY")
            or credentials.get("apiKey")
        )
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
    def client(self):
        if not self._client:
            headers = self._get_headers()
            transport = RequestsHTTPTransport(
                url=self.base_url,
                headers=headers
            )
            self._client = Client(transport=transport, fetch_schema_from_transport=True)
        return self._client
    
    def mutate(self, mutation: Union[str, gql], variables: dict = None):
        if isinstance(mutation, str):
            mutation = gql(mutation)
        return self.client.execute(mutation, variable_values=variables)
    
    def query(self, query: Union[str, gql], variables: dict = None):
        if isinstance(query, str):
            query = gql(query)
        return self.client.execute(query, variable_values=variables)

    @abstractmethod
    def list_tools(self):
        pass
