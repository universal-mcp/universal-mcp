from abc import ABC, abstractmethod

import httpx
from loguru import logger

from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import Integration


class Application(ABC):
    """
    Application is collection of tools that can be used by an agent.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name

    @abstractmethod
    def list_tools(self):
        pass


class APIApplication(Application):
    """
    APIApplication is an application that uses an API to interact with the world.
    """

    def __init__(self, name: str, integration: Integration = None, **kwargs):
        super().__init__(name, **kwargs)
        self.integration = integration

    def _get_headers(self):
        return {}

    def _get(self, url, params=None):
        try:
            headers = self._get_headers()
            response = httpx.get(url, headers=headers, params=params)
            response.raise_for_status()
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
            response = httpx.post(url, headers=headers, json=data, params=params)
            response.raise_for_status()
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return e.response.text or "Rate limit exceeded. Please try again later."
            else:
                raise e
        except Exception as e:
            logger.error(f"Error posting {url}: {e}")
            raise e

    def _put(self, url, data, params=None):
        try:
            headers = self._get_headers()
            response = httpx.put(url, headers=headers, json=data, params=params)
            response.raise_for_status()
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
            response = httpx.delete(url, headers=headers, params=params)
            response.raise_for_status()
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
            response = httpx.patch(url, headers=headers, json=data, params=params)
            response.raise_for_status()
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error patching {url}: {e}")
            raise e

    def validate(self):
        pass
