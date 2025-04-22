from abc import ABC, abstractmethod

import httpx
from loguru import logger

from universal_mcp.analytics import analytics
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import Integration


class Application(ABC):
    """
    Application is collection of tools that can be used by an agent.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        logger.debug(f"Initializing Application '{name}' with kwargs: {kwargs}")
        analytics.track_app_loaded(name)  # Track app loading

    @abstractmethod
    def list_tools(self):
        pass


class APIApplication(Application):
    """
    APIApplication is an application that uses an API to interact with the world.
    """

    def __init__(self, name: str, integration: Integration = None, **kwargs):
        super().__init__(name, **kwargs)
        self.default_timeout = 30
        self.integration = integration
        logger.debug(f"Initializing APIApplication '{name}' with integration: {integration}")

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

    def _get(self, url, params=None):
        try:
            headers = self._get_headers()
            logger.debug(f"Making GET request to {url} with params: {params}")
            response = httpx.get(
                url, headers=headers, params=params, timeout=self.default_timeout
            )
            response.raise_for_status()
            logger.debug(f"GET request successful with status code: {response.status_code}")
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error getting {url}: {e}")
            raise e

    def _post(self, url, data, params=None):
        try:
            headers = self._get_headers()
            logger.debug(f"Making POST request to {url} with params: {params} and data: {data}")
            response = httpx.post(
                url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.default_timeout,
            )
            response.raise_for_status()
            logger.debug(f"POST request successful with status code: {response.status_code}")
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded for {url}")
                return e.response.text or "Rate limit exceeded. Please try again later."
            else:
                raise e
        except Exception as e:
            logger.error(f"Error posting {url}: {e}")
            raise e

    def _put(self, url, data, params=None):
        try:
            headers = self._get_headers()
            logger.debug(f"Making PUT request to {url} with params: {params} and data: {data}")
            response = httpx.put(
                url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.default_timeout,
            )
            response.raise_for_status()
            logger.debug(f"PUT request successful with status code: {response.status_code}")
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error posting {url}: {e}")
            raise e

    def _delete(self, url, params=None):
        try:
            headers = self._get_headers()
            logger.debug(f"Making DELETE request to {url} with params: {params}")
            response = httpx.delete(
                url, headers=headers, params=params, timeout=self.default_timeout
            )
            response.raise_for_status()
            logger.debug(f"DELETE request successful with status code: {response.status_code}")
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error posting {url}: {e}")
            raise e

    def _patch(self, url, data, params=None):
        try:
            headers = self._get_headers()
            logger.debug(f"Making PATCH request to {url} with params: {params} and data: {data}")
            response = httpx.patch(
                url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.default_timeout,
            )
            response.raise_for_status()
            logger.debug(f"PATCH request successful with status code: {response.status_code}")
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error patching {url}: {e}")
            raise e

    def validate(self):
        pass
