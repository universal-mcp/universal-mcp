from typing import Any
from firecrawl import FirecrawlApp as FirecrawlApiClient
from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration

class FirecrawlApp(APIApplication):
    """
    Application for interacting with the Firecrawl service (firecrawl.dev)
    to scrape web pages, perform searches, and manage crawl/batch scrape/extract jobs.
    Requires a Firecrawl API key configured via integration.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="firecrawl", integration=integration)
        self.api_key: str | None = None
        if self.integration:
            credentials = self.integration.get_credentials()
            if credentials and credentials.get("api_key"):
                self.api_key = credentials["api_key"]
            
    def _get_api_key_or_error(self) -> str | dict:
        """
        Helper to consolidate the API key check logic used by tool methods.
        Returns the API key string on success, or the error dictionary on failure.
        """
        current_api_key = None
        integration_name = "FIRECRAWL_API_KEY"

        if self.integration:
            integration_name = self.integration.name # Get specific name if possible
            credentials = self.integration.get_credentials()
            if credentials and credentials.get("api_key"):
                current_api_key = credentials["api_key"]
            

        if not current_api_key:
            return {
                "status": "tool_error",
                "error_type": "api_key_required",
                "key_name": integration_name,
                "message": f"API Key required for {self.name}. Please provide the '{integration_name}' key.",
            }

        return current_api_key

    def scrape_url(
        self, url: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """
        Scrapes a single URL using Firecrawl.
        Returns scraped data or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error
        
        client = FirecrawlApiClient(api_key=key_or_error)
        response_data = client.scrape_url(url=url, params=params)
        return response_data

    def search(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """
        Performs a web search using Firecrawl.
        Returns search results or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        response = client.search(query=query, params=params)
        return response

    def start_crawl(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts a crawl job. Returns job ID response or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        response = client.async_crawl_url(
            url=url, params=params, idempotency_key=idempotency_key
        )
        return response

    def check_crawl_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks crawl job status. Returns status details or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        status = client.check_crawl_status(id=job_id)
        return status

    def cancel_crawl(self, job_id: str) -> dict[str, Any] | str:
        """
        Cancels a crawl job. Returns cancellation status or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        response = client.cancel_crawl(id=job_id)
        return response

    def start_batch_scrape(
        self,
        urls: list[str],
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts a batch scrape job. Returns job ID response or an error dictionary.
        """
        if not urls:
             # Return consistent error format
             return {
                "status": "tool_error",
                "error_type": "invalid_input",
                "message": "No URLs provided for batch scrape.",
            }

        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        response = client.async_batch_scrape_urls(
            urls=urls, params=params, idempotency_key=idempotency_key
        )
        return response

    def check_batch_scrape_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks batch scrape job status. Returns status details or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        status = client.check_batch_scrape_status(id=job_id)
        return status

    def start_extract(
        self,
        urls: list[str],
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts an extraction job. Returns job ID response or an error dictionary.
        """
        if not urls:
             return {
                "status": "tool_error",
                "error_type": "invalid_input",
                "message": "No URLs provided for extraction.",
            }
        if not params or (not params.get("prompt") and not params.get("schema")):
             return {
                "status": "tool_error",
                "error_type": "invalid_input",
                "message": "'params' dictionary must include either 'prompt' or 'schema'.",
            }

        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        response = client.async_extract(
            urls=urls, params=params, idempotency_key=idempotency_key
        )
        return response

    def check_extract_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks extraction job status. Returns status details or an error dictionary.
        """
        key_or_error = self._get_api_key_or_error()
        if isinstance(key_or_error, dict):
            return key_or_error

        client = FirecrawlApiClient(api_key=key_or_error)
        status = client.get_extract_status(job_id=job_id)
        return status

    def list_tools(self):
        """Returns a list of methods exposed as tools."""
        return [
            self.scrape_url,
            self.search,
            self.start_crawl,
            self.check_crawl_status,
            self.cancel_crawl,
            self.start_batch_scrape,
            self.check_batch_scrape_status,
            self.start_extract,
            self.check_extract_status,
        ]
