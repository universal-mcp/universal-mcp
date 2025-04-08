from typing import Any

from firecrawl import FirecrawlApp as FirecrawlApiClient
from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import Integration


class FirecrawlApp(APIApplication):
    """
    Application for interacting with the Firecrawl service (firecrawl.dev)
    to scrape web pages, perform searches, and manage crawl/batch scrape/extract jobs.
    Requires a Firecrawl API key configured via integration
    (e.g., FIRECRAWL_API_KEY environment variable).
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="firecrawl", integration=integration)
        self.api_key: str | None = None
        self._attempt_initial_key_load()

    def _attempt_initial_key_load(self):
        """Attempts to load the API key during initialization."""
        if self.integration:
            credentials = self.integration.get_credentials()
            if credentials and credentials.get("api_key"):
                self.api_key = credentials["api_key"]
                logger.info(
                    "Firecrawl API Key successfully retrieved via integration during init."
                )
            else:
                logger.warning(
                    "Firecrawl API Key not found in credentials during init. Will try again on first use."
                )

    def _get_firecrawl_client(self) -> FirecrawlApiClient:
        """Ensures the API key is available and returns an initialized Firecrawl client."""
        if not self.api_key:
            logger.debug(
                "Firecrawl API key not loaded, attempting retrieval via integration."
            )
            if not self.integration:
                raise NotAuthorizedError("Firecrawl integration is not configured.")

            credentials = self.integration.get_credentials()
            if credentials and credentials.get("api_key"):
                self.api_key = credentials["api_key"]
                logger.info("Firecrawl API Key successfully retrieved via integration.")
            else:
                action = (
                    self.integration.authorize()
                    if hasattr(self.integration, "authorize")
                    else "Configure API Key"
                )
                raise NotAuthorizedError(
                    f"Firecrawl API Key not found in provided integration credentials. Action required: {action}"
                )

        if not self.api_key:
            raise NotAuthorizedError(
                "Firecrawl API Key is missing or could not be loaded."
            )

        return FirecrawlApiClient(api_key=self.api_key)

    def scrape_url(
        self, url: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """
        Scrapes a single URL using Firecrawl and returns the extracted data.

        Args:
            url: The URL of the web page to scrape.
            params: Optional dictionary of parameters to customize the scrape.
                    Refer to Firecrawl documentation for 'pageOptions', 'extractorOptions', 'jsonOptions'.
                    Example: {'pageOptions': {'onlyMainContent': True}}

        Returns:
            A dictionary containing the scraped data (e.g., 'content', 'markdown', 'metadata')
            on success, or a string containing an error message on failure.
        """
        logger.info(f"Attempting to scrape URL: {url} with params: {params}")
        try:
            client = self._get_firecrawl_client()
            response_data = client.scrape_url(url=url, params=params)
            logger.info(f"Successfully scraped URL: {url}")
            return response_data
        except Exception as e:
            logger.error(f"Failed to scrape URL {url}: {type(e).__name__} - {e}")
            return f"Error scraping URL {url}: {type(e).__name__} - {e}"

    def search(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """
        Performs a web search using Firecrawl's search capability.

        Args:
            query: The search query string.
            params: Optional dictionary of search parameters (e.g., limit, lang, country, scrapeOptions).
                    Refer to Firecrawl documentation for details.
                    Example: {'limit': 3, 'country': 'DE'}

        Returns:
            A dictionary containing the search results (typically {'success': bool, 'data': [...]})
            on success, or a string containing an error message on failure.
        """
        logger.info(f"Attempting search for query: '{query}' with params: {params}")
        try:
            client = self._get_firecrawl_client()
            # The library method returns the full response dictionary
            response = client.search(query=query, params=params)
            logger.info(f"Successfully performed search for query: '{query}'")
            return response
        except Exception as e:
            logger.error(
                f"Failed to perform search for '{query}': {type(e).__name__} - {e}"
            )
            return f"Error performing search for '{query}': {type(e).__name__} - {e}"

    # --- Asynchronous Job Pattern Tools ---

    def start_crawl(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts a crawl job for a given URL using Firecrawl. Returns the job ID immediately.
        Use 'check_crawl_status' to monitor progress and retrieve results.

        Args:
            url: The starting URL for the crawl.
            params: Optional dictionary of parameters to customize the crawl (e.g., crawlerOptions).
                    Example: {'crawlerOptions': {'excludes': ['blog/'], 'maxDepth': 2}}
            idempotency_key: Optional unique key to prevent duplicate jobs if the request is retried.

        Returns:
            A dictionary containing the job initiation response (e.g., {'success': bool, 'id': str})
            on success, or a string containing an error message on failure.
        """
        logger.info(
            f"Attempting to start crawl job for URL: {url} with params: {params}"
        )
        try:
            client = self._get_firecrawl_client()
            # Use the library's async method which returns the job ID response
            response = client.async_crawl_url(
                url=url, params=params, idempotency_key=idempotency_key
            )
            if response.get("success"):
                logger.info(
                    f"Successfully started crawl job for URL: {url}. Job ID: {response.get('id')}"
                )
            else:
                logger.error(
                    f"Failed to start crawl job for URL {url}. Response: {response}"
                )
            return response
        except Exception as e:
            logger.error(
                f"Failed to start crawl for URL {url}: {type(e).__name__} - {e}"
            )
            return f"Error starting crawl for URL {url}: {type(e).__name__} - {e}"

    def check_crawl_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks the status of a previously initiated Firecrawl crawl job.
        If the job is completed, this retrieves the results (potentially paginated).

        Args:
            job_id: The ID of the crawl job to check.

        Returns:
            A dictionary containing the job status details (e.g., 'status', 'progress', 'data' if completed)
            on success, or a string containing an error message on failure.
            Common status values: 'pending', 'queued', 'scraping', 'completed', 'failed'.
        """
        logger.info(f"Attempting to check status for crawl job ID: {job_id}")
        try:
            client = self._get_firecrawl_client()
            # Library method handles pagination for completed jobs
            status = client.check_crawl_status(id=job_id)
            logger.info(
                f"Successfully checked status for job ID: {job_id}. Status: {status.get('status', 'unknown')}"
            )
            return status
        except Exception as e:
            logger.error(
                f"Failed to check crawl status for job ID {job_id}: {type(e).__name__} - {e}"
            )
            return f"Error checking crawl status for job ID {job_id}: {type(e).__name__} - {e}"

    def cancel_crawl(self, job_id: str) -> dict[str, Any] | str:
        """
        Cancels a currently running Firecrawl crawl job.

        Args:
            job_id: The ID of the crawl job to cancel.

        Returns:
            A dictionary confirming the cancellation status (e.g., {'success': bool, 'status': 'cancelled'})
            on success, or a string containing an error message on failure.
        """
        logger.info(f"Attempting to cancel crawl job ID: {job_id}")
        try:
            client = self._get_firecrawl_client()
            response = client.cancel_crawl(id=job_id)
            logger.info(
                f"Successfully requested cancellation for job ID: {job_id}. Response: {response}"
            )
            return response
        except Exception as e:
            logger.error(
                f"Failed to cancel crawl job ID {job_id}: {type(e).__name__} - {e}"
            )
            return f"Error cancelling crawl job ID {job_id}: {type(e).__name__} - {e}"

    def start_batch_scrape(
        self,
        urls: list[str],
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts a batch scrape job for multiple URLs using Firecrawl. Returns the job ID immediately.
        Use 'check_batch_scrape_status' to monitor progress and retrieve results.

        Args:
            urls: A list of URLs to scrape.
            params: Optional dictionary of parameters applied to all scrapes in the batch.
                    Refer to Firecrawl documentation for scrape parameters.
            idempotency_key: Optional unique key to prevent duplicate jobs.

        Returns:
            A dictionary containing the job initiation response (e.g., {'success': bool, 'id': str})
            on success, or a string containing an error message on failure.
        """
        url_count = len(urls)
        logger.info(
            f"Attempting to start batch scrape job for {url_count} URLs with params: {params}"
        )
        if not urls:
            return "Error: No URLs provided for batch scrape."
        try:
            client = self._get_firecrawl_client()
            response = client.async_batch_scrape_urls(
                urls=urls, params=params, idempotency_key=idempotency_key
            )
            if response.get("success"):
                logger.info(
                    f"Successfully started batch scrape job for {url_count} URLs. Job ID: {response.get('id')}"
                )
            else:
                logger.error(
                    f"Failed to start batch scrape job for {url_count} URLs. Response: {response}"
                )
            return response
        except Exception as e:
            logger.error(f"Failed to start batch scrape: {type(e).__name__} - {e}")
            return f"Error starting batch scrape: {type(e).__name__} - {e}"

    def check_batch_scrape_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks the status of a previously initiated Firecrawl batch scrape job.
        If the job is completed, this retrieves the results for all URLs.

        Args:
            job_id: The ID of the batch scrape job to check.

        Returns:
            A dictionary containing the job status details (e.g., 'status', 'progress', 'data' list if completed)
            on success, or a string containing an error message on failure.
        """
        logger.info(f"Attempting to check status for batch scrape job ID: {job_id}")
        try:
            client = self._get_firecrawl_client()
            status = client.check_batch_scrape_status(id=job_id)
            logger.info(
                f"Successfully checked status for batch scrape job ID: {job_id}. Status: {status.get('status', 'unknown')}"
            )
            return status
        except Exception as e:
            logger.error(
                f"Failed to check batch scrape status for job ID {job_id}: {type(e).__name__} - {e}"
            )
            return f"Error checking batch scrape status for job ID {job_id}: {type(e).__name__} - {e}"

    def start_extract(
        self,
        urls: list[str],
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | str:
        """
        Starts an extraction job for one or more URLs using Firecrawl. Returns the job ID immediately.
        Use 'check_extract_status' to monitor progress and retrieve results. Requires 'prompt' or 'schema' in params.

        Args:
            urls: A list of URLs to extract data from.
            params: Dictionary of parameters. MUST include 'prompt' (string) or 'schema' (JSON schema dict or Pydantic model).
                    Optional: 'enableWebSearch', 'systemPrompt', etc. See Firecrawl docs.
                    Example: {'prompt': 'Extract the main headlines'}
                    Example: {'schema': {'type': 'object', 'properties': {'title': {'type': 'string'}}}}
            idempotency_key: Optional unique key to prevent duplicate jobs.

        Returns:
            A dictionary containing the job initiation response (e.g., {'success': bool, 'id': str})
            on success, or a string containing an error message on failure.
        """
        logger.info(
            f"Attempting to start extraction job for URLs: {urls} with params: {params}"
        )
        if not urls:
            return "Error: No URLs provided for extraction."
        if not params or (not params.get("prompt") and not params.get("schema")):
            return "Error: 'params' dictionary must include either a 'prompt' string or a 'schema' definition."
        try:
            client = self._get_firecrawl_client()
            # Pass params directly; the library handles schema conversion if needed
            response = client.async_extract(
                urls=urls, params=params, idempotency_key=idempotency_key
            )
            if response.get("success"):
                logger.info(
                    f"Successfully started extraction job for URLs. Job ID: {response.get('id')}"
                )
            else:
                logger.error(
                    f"Failed to start extraction job for URLs. Response: {response}"
                )
            return response
        except Exception as e:
            logger.error(f"Failed to start extraction: {type(e).__name__} - {e}")
            return f"Error starting extraction: {type(e).__name__} - {e}"

    def check_extract_status(self, job_id: str) -> dict[str, Any] | str:
        """
        Checks the status of a previously initiated Firecrawl extraction job.
        If the job is completed, this retrieves the extracted data.

        Args:
            job_id: The ID of the extraction job to check.

        Returns:
            A dictionary containing the job status details (e.g., 'status', 'data' if completed)
            on success, or a string containing an error message on failure.
            Common status values: 'pending', 'processing', 'completed', 'failed'.
        """
        logger.info(f"Attempting to check status for extraction job ID: {job_id}")
        try:
            client = self._get_firecrawl_client()
            status = client.get_extract_status(
                job_id=job_id
            )  # Correct library method name
            logger.info(
                f"Successfully checked status for extraction job ID: {job_id}. Status: {status.get('status', 'unknown')}"
            )
            return status
        except Exception as e:
            logger.error(
                f"Failed to check extraction status for job ID {job_id}: {type(e).__name__} - {e}"
            )
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
