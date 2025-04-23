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

    def _get_client(self) -> FirecrawlApiClient:
        """Initializes and returns the Firecrawl client after ensuring API key is set."""
        api_key = self.integration.get_credentials().get("api_key")
        return FirecrawlApiClient(api_key=api_key)

    def scrape_url(
        self, url: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """
        Scrapes a single URL using Firecrawl and returns the extracted data.

        Args:
            url: The URL of the web page to scrape.
            params: Optional dictionary of parameters to customize the scrape.

        Returns:
            A dictionary containing the scraped data on success,
            or a string containing an error message on failure.

        Tags:
            scrape, important
        """
        try:
            client = self._get_client()
            response_data = client.scrape_url(url=url, params=params)
            return response_data

        except Exception as e:
            return f"Error scraping URL {url}: {type(e).__name__} - {e}"

    def search(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """
        Performs a web search using Firecrawl's search capability.

        Args:
            query: The search query string.
            params: Optional dictionary of search parameters.

        Returns:
            A dictionary containing the search results on success,
            or a string containing an error message on failure.

        Tags:
            search, important
        """
        try:
            client = self._get_client()
            response = client.search(query=query, params=params)
            return response
        except Exception as e:
            return f"Error performing search for '{query}': {type(e).__name__} - {e}"

    def start_crawl(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts a crawl job for a given URL using Firecrawl. Returns the job ID immediately.

        Args:
            url: The starting URL for the crawl.
            params: Optional dictionary of parameters to customize the crawl.
            idempotency_key: Optional unique key to prevent duplicate jobs.

        Returns:
            A dictionary containing the job initiation response on success,
            or a string containing an error message on failure.

        Tags:
            crawl, async_job, start
        """
        try:
            client = self._get_client()
            response = client.async_crawl_url(
                url=url, params=params, idempotency_key=idempotency_key
            )
            return response

        except Exception as e:
            return f"Error starting crawl for URL {url}: {type(e).__name__} - {e}"

    def check_crawl_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks the status of a previously initiated Firecrawl crawl job.

        Args:
            job_id: The ID of the crawl job to check.

        Returns:
            A dictionary containing the job status details on success,
            or a string containing an error message on failure.

        Tags:
            crawl, async_job, status
        """
        try:
            client = self._get_client()
            status = client.check_crawl_status(id=job_id)
            return status

        except Exception as e:
            return f"Error checking crawl status for job ID {job_id}: {type(e).__name__} - {e}"

    def cancel_crawl(self, job_id: str) -> dict[str, Any] | str:
        """
        Cancels a currently running Firecrawl crawl job.

        Args:
            job_id: The ID of the crawl job to cancel.

        Returns:
            A dictionary confirming the cancellation status on success,
            or a string containing an error message on failure.

        Tags:
            crawl, async_job, management, cancel
        """
        try:
            client = self._get_client()
            response = client.cancel_crawl(id=job_id)

            return response

        except Exception as e:
            return f"Error cancelling crawl job ID {job_id}: {type(e).__name__} - {e}"

    def start_batch_scrape(
        self,
        urls: list[str],
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts a batch scrape job for multiple URLs using Firecrawl.

        Args:
            urls: A list of URLs to scrape.
            params: Optional dictionary of parameters applied to all scrapes.
            idempotency_key: Optional unique key to prevent duplicate jobs.

        Returns:
            A dictionary containing the job initiation response on success,
            or a string containing an error message on failure.

        Tags:
            scrape, batch, async_job, start
        """
        try:
            client = self._get_client()
            response = client.async_batch_scrape_urls(
                urls=urls, params=params, idempotency_key=idempotency_key
            )
            return response

        except Exception as e:
            return f"Error starting batch scrape: {type(e).__name__} - {e}"

    def check_batch_scrape_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks the status of a previously initiated Firecrawl batch scrape job.

        Args:
            job_id: The ID of the batch scrape job to check.

        Returns:
            A dictionary containing the job status details on success,
            or a string containing an error message on failure.

        Tags:
            scrape, batch, async_job, status
        """
        try:
            client = self._get_client()
            status = client.check_batch_scrape_status(id=job_id)
            return status

        except Exception as e:
            return f"Error checking batch scrape status for job ID {job_id}: {type(e).__name__} - {e}"

    def start_extract(
        self,
        urls: list[str],
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts an extraction job for one or more URLs using Firecrawl.

        Args:
            urls: A list of URLs to extract data from.
            params: Dictionary of parameters. MUST include 'prompt' or 'schema'.
            idempotency_key: Optional unique key to prevent duplicate jobs.

        Returns:
            A dictionary containing the job initiation response on success,
            or a string containing an error message on failure.

        Tags:
            extract, ai, async_job, start
        """

        try:
            client = self._get_client()
            response = client.async_extract(
                urls=urls, params=params, idempotency_key=idempotency_key
            )
            return response

        except Exception as e:
            return f"Error starting extraction: {type(e).__name__} - {e}"

    def check_extract_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks the status of a previously initiated Firecrawl extraction job.

        Args:
            job_id: The ID of the extraction job to check.

        Returns:
            A dictionary containing the job status details on success,
            or a string containing an error message on failure.

        Tags:
            extract, ai, async_job, status
        """
        try:
            client = self._get_client()
            status = client.get_extract_status(job_id=job_id)
            return status

        except Exception as e:
            return f"Error checking extraction status for job ID {job_id}: {type(e).__name__} - {e}"

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
