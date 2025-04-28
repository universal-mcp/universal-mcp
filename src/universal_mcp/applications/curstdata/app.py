from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class CrustdataApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='crustdata', integration=integration, **kwargs)
        self.base_url = "https://api.crustdata.com"

    def _get_headers(self) -> dict[str, Any]:
        api_key = self.integration.get_credentials().get("api_key")
        return {
            "Authorization":  f"Token {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def screen_companies(self, metrics, filters, offset, count, sorts) -> dict[str, Any]:
        """
        Screens companies based on specified metrics, filters, sorting, and pagination parameters, and returns the result as a JSON-compatible dictionary.
        
        Args:
            metrics: List or structure specifying the financial or business metrics to screen companies by.
            filters: List or structure defining the filter criteria to apply to the company screening.
            offset: Integer specifying the starting index for paginated results.
            count: Integer specifying the maximum number of results to return.
            sorts: List or structure describing the sorting criteria for the returned companies.
        
        Returns:
            A dictionary representing the JSON response from the company screener API, typically containing the screened companies and associated data.
        
        Raises:
            ValueError: If any of the required parameters (metrics, filters, offset, count, sorts) is None.
            requests.HTTPError: If the HTTP request to the screener API fails or returns a bad status code.
        
        Tags:
            screen, companies, api, filter, pagination
        """
        if metrics is None:
            raise ValueError("Missing required parameter 'metrics'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        request_body = {
            'metrics': metrics,
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/screener/screen/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_headcount_timeseries(self, filters, offset, count, sorts) -> dict[str, Any]:
        """
        Retrieve headcount timeseries data from the data lab endpoint using the provided filters, pagination, and sorting options.
        
        Args:
            filters: dict. Dictionary specifying filter criteria to apply to the headcount timeseries query.
            offset: int. The starting index for pagination of the timeseries results.
            count: int. The number of records to retrieve in the result set.
            sorts: list or dict. Sorting options to order the returned timeseries data.
        
        Returns:
            dict. Parsed JSON response containing the headcount timeseries data and associated metadata.
        
        Raises:
            ValueError: Raised if any of the required parameters ('filters', 'offset', 'count', 'sorts') are not provided (i.e., are None).
            requests.HTTPError: Raised if the HTTP request to the endpoint fails or returns a non-success status code.
        
        Tags:
            get, fetch, headcount, timeseries, data, api, management
        """
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        request_body = {
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_lab/headcount_timeseries/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_headcount_by_facet_timeseries(self, filters, offset, count, sorts) -> dict[str, Any]:
        """
        Retrieves headcount timeseries data aggregated by specified facets using provided filters and sorting options.
        
        Args:
            filters: dict. A dictionary specifying the filter criteria for the data retrieval.
            offset: int. The number of records to skip before starting to return results, used for pagination.
            count: int. The maximum number of records to return.
            sorts: list or dict. Sorting instructions determining the order of the returned timeseries data.
        
        Returns:
            dict. A dictionary containing the requested headcount timeseries data aggregated by facets.
        
        Raises:
            ValueError: Raised if any of the required parameters ('filters', 'offset', 'count', 'sorts') is None.
            requests.HTTPError: Raised if the HTTP request to the data source fails (non-2xx response).
        
        Tags:
            get, timeseries, headcount, data-retrieval, facets, management
        """
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        request_body = {
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_lab/headcount_by_facet_timeseries/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_funding_milestone_timeseries(self, filters, offset, count, sorts) -> dict[str, Any]:
        """
        Retrieves a time series of funding milestone data based on specified filters, pagination, and sorting options.
        
        Args:
            filters: dict. Criteria to filter the funding milestones to include in the time series.
            offset: int. The starting index for pagination of the results.
            count: int. The maximum number of records to return.
            sorts: list. Sorting rules to apply to the results.
        
        Returns:
            dict. A JSON-compatible dictionary containing the retrieved funding milestone time series data.
        
        Raises:
            ValueError: If any of the required parameters ('filters', 'offset', 'count', or 'sorts') are None.
            requests.HTTPError: If the underlying HTTP request fails or returns an error status code.
        
        Tags:
            get, fetch, timeseries, funding, milestones, data-lab, api
        """
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        request_body = {
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_lab/funding_milestone_timeseries/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_decision_makers(self, filters, offset, count, sorts, decision_maker_titles) -> dict[str, Any]:
        """
        Retrieves decision makers based on specified filters and parameters.
        
        Args:
            filters: Dictionary containing filter criteria for decision makers.
            offset: Integer indicating the starting position for retrieving results.
            count: Integer specifying the number of results to retrieve.
            sorts: List or dictionary defining the sorting order of the results.
            decision_maker_titles: List of titles to filter decision makers by.
        
        Returns:
            Dictionary containing decision maker data with structure dependent on the API response.
        
        Raises:
            ValueError: Raised when any of the required parameters (filters, offset, count, sorts, decision_maker_titles) is None.
            HTTPError: Raised when the API request fails with an error status code.
        
        Tags:
            retrieve, search, data, decision-makers, api, filtering
        """
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        if decision_maker_titles is None:
            raise ValueError("Missing required parameter 'decision_maker_titles'")
        request_body = {
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
            'decision_maker_titles': decision_maker_titles,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_lab/decision_makers/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_web_traffic(self, filters, offset, count, sorts) -> dict[str, Any]:
        """
        Retrieves web traffic data based on provided filters, pagination, and sorting criteria.
        
        Args:
            filters: dict. Filtering options to apply to the web traffic query.
            offset: int. The starting index from which to retrieve results (pagination offset).
            count: int. The number of records to retrieve (pagination count).
            sorts: list. Sorting criteria to order the web traffic results.
        
        Returns:
            dict. Parsed JSON response containing the web traffic data matching the specified criteria.
        
        Raises:
            ValueError: If any of the required parameters ('filters', 'offset', 'count', or 'sorts') are None.
            requests.HTTPError: If the HTTP request to the web traffic endpoint fails or returns an error status code.
        
        Tags:
            get, web-traffic, data, fetch, api
        """
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        request_body = {
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_lab/webtraffic/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_investor_portfolio(self, investor_name) -> dict[str, Any]:
        """
        Retrieves the investment portfolio information for a specified investor.
        
        Args:
            investor_name: str. The name of the investor whose portfolio data is to be fetched.
        
        Returns:
            dict[str, Any]: A dictionary containing portfolio data for the given investor as returned by the API.
        
        Raises:
            ValueError: If 'investor_name' is None.
            HTTPError: If the HTTP request to the portfolio endpoint fails.
        
        Tags:
            get, portfolio, investor, api
        """
        if investor_name is None:
            raise ValueError("Missing required parameter 'investor_name'")
        url = f"{self.base_url}/data_lab/investor_portfolio"
        query_params = {k: v for k, v in [('investor_name', investor_name)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_job_listings(self, tickers, dataset, filters, offset, count, sorts) -> dict[str, Any]:
        """
        Retrieves job listings data based on specified parameters.
        
        Args:
            tickers: List of ticker symbols to filter job listings.
            dataset: Specific dataset to query for job listings.
            filters: Criteria to filter the job listings results.
            offset: Starting position for pagination of results.
            count: Number of results to return per page.
            sorts: Sorting criteria for the returned job listings.
        
        Returns:
            A dictionary containing job listings data and associated metadata.
        
        Raises:
            ValueError: Raised when any of the required parameters is None.
            HTTPError: Raised when the HTTP request fails.
        
        Tags:
            get, retrieve, job-listings, data, pagination, filtering, important
        """
        if tickers is None:
            raise ValueError("Missing required parameter 'tickers'")
        if dataset is None:
            raise ValueError("Missing required parameter 'dataset'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if offset is None:
            raise ValueError("Missing required parameter 'offset'")
        if count is None:
            raise ValueError("Missing required parameter 'count'")
        if sorts is None:
            raise ValueError("Missing required parameter 'sorts'")
        request_body = {
            'tickers': tickers,
            'dataset': dataset,
            'filters': filters,
            'offset': offset,
            'count': count,
            'sorts': sorts,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_lab/job_listings/Table/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_persons(self, job_id) -> dict[str, Any]:
        """
        Submits a search request for persons associated with a given asynchronous job and returns the search results as a dictionary.
        
        Args:
            job_id: The identifier of the asynchronous job used to retrieve associated persons.
        
        Returns:
            A dictionary containing the search results for persons related to the specified job.
        
        Raises:
            ValueError: Raised if job_id is None.
            HTTPError: Raised if the HTTP request to the person search endpoint fails (from response.raise_for_status()).
        
        Tags:
            search, person, async-job, status, api, important
        """
        if job_id is None:
            raise ValueError("Missing required parameter 'job_id'")
        request_body = {
            'job_id': job_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/screener/person/search"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_companies(self, filters, page) -> dict[str, Any]:
        """
        Searches for companies using specified filters and pagination parameters.
        
        Args:
            filters: Dictionary containing filter criteria for company search.
            page: Dictionary or object containing pagination parameters (e.g., page number, size).
        
        Returns:
            Dictionary containing search results with company data and pagination information.
        
        Raises:
            ValueError: Raised when either 'filters' or 'page' parameters are None.
            HTTPError: Raised when the API request fails with an error status code.
        
        Tags:
            search, company, filtering, pagination, api
        """
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if page is None:
            raise ValueError("Missing required parameter 'page'")
        request_body = {
            'filters': filters,
            'page': page,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/screener/company/search"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def enrich_person(self, linkedin_profile_url, enrich_realtime, fields) -> dict[str, Any]:
        """
        Retrieves enriched person data from LinkedIn profile using the provided profile URL, enrichment mode, and requested fields.
        
        Args:
            linkedin_profile_url: str. The LinkedIn profile URL of the person to enrich.
            enrich_realtime: bool. Whether to perform enrichment in real-time (True) or allow cached data (False).
            fields: str. Comma-separated list of fields to include in the enrichment.
        
        Returns:
            dict[str, Any]: A dictionary containing the enriched person data as returned by the enrichment API.
        
        Raises:
            ValueError: If any of 'linkedin_profile_url', 'enrich_realtime', or 'fields' is None.
            requests.HTTPError: If the API response status is not successful.
        
        Tags:
            enrich, person, lookup, api
        """
        if linkedin_profile_url is None:
            raise ValueError("Missing required parameter 'linkedin_profile_url'")
        if enrich_realtime is None:
            raise ValueError("Missing required parameter 'enrich_realtime'")
        if fields is None:
            raise ValueError("Missing required parameter 'fields'")
        url = f"{self.base_url}/screener/person/enrich"
        query_params = {k: v for k, v in [('linkedin_profile_url', linkedin_profile_url), ('enrich_realtime', enrich_realtime), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def enrich_company(self, company_domain, enrich_realtime) -> dict[str, Any]:
        """
        Retrieves enriched company data using the provided company domain and enrichment mode.
        
        Args:
            company_domain: str. The company's domain name to enrich. Must not be None.
            enrich_realtime: bool. Flag indicating whether to perform real-time enrichment. Must not be None.
        
        Returns:
            dict[str, Any]: The JSON response containing enriched company information.
        
        Raises:
            ValueError: Raised if 'company_domain' or 'enrich_realtime' is None.
            HTTPError: Raised if the HTTP request returned an unsuccessful status code.
        
        Tags:
            enrich, company, ai
        """
        if company_domain is None:
            raise ValueError("Missing required parameter 'company_domain'")
        if enrich_realtime is None:
            raise ValueError("Missing required parameter 'enrich_realtime'")
        url = f"{self.base_url}/screener/company"
        query_params = {k: v for k, v in [('company_domain', company_domain), ('enrich_realtime', enrich_realtime)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_linked_in_posts(self, company_linkedin_url) -> dict[str, Any]:
        """
        Fetches LinkedIn posts for a specified company using its LinkedIn URL.
        
        Args:
            company_linkedin_url: str. The public LinkedIn URL of the target company whose posts you want to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing LinkedIn posts and associated metadata for the specified company.
        
        Raises:
            ValueError: Raised if 'company_linkedin_url' is None.
            HTTPError: Raised if the HTTP request to the LinkedIn posts service fails.
        
        Tags:
            fetch, linkedin, posts, company, api
        """
        if company_linkedin_url is None:
            raise ValueError("Missing required parameter 'company_linkedin_url'")
        url = f"{self.base_url}/screener/linkedin_posts"
        query_params = {k: v for k, v in [('company_linkedin_url', company_linkedin_url)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_linked_in_posts(self, keyword, page, sort_by, date_posted) -> dict[str, Any]:
        """
        Searches LinkedIn posts using the provided keyword and filters, returning the search results as a dictionary.
        
        Args:
            keyword: str. The keyword or phrase to search for in LinkedIn posts.
            page: int. The results page number to retrieve.
            sort_by: str. The sorting method to apply to the search results (e.g., 'relevance', 'date').
            date_posted: str. A filter indicating the date range of posts to include (e.g., 'past_24_hours', 'past_week').
        
        Returns:
            dict[str, Any]: A dictionary containing the LinkedIn post search results.
        
        Raises:
            ValueError: Raised if any of the required parameters ('keyword', 'page', 'sort_by', 'date_posted') are missing.
            requests.HTTPError: Raised if the HTTP request to the LinkedIn search endpoint returns an unsuccessful status code.
        
        Tags:
            search, linkedin, posts, api
        """
        if keyword is None:
            raise ValueError("Missing required parameter 'keyword'")
        if page is None:
            raise ValueError("Missing required parameter 'page'")
        if sort_by is None:
            raise ValueError("Missing required parameter 'sort_by'")
        if date_posted is None:
            raise ValueError("Missing required parameter 'date_posted'")
        request_body = {
            'keyword': keyword,
            'page': page,
            'sort_by': sort_by,
            'date_posted': date_posted,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/screener/linkedin_posts/keyword_search/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.screen_companies,
            self.get_headcount_timeseries,
            self.get_headcount_by_facet_timeseries,
            self.get_funding_milestone_timeseries,
            self.get_decision_makers,
            self.get_web_traffic,
            self.get_investor_portfolio,
            self.get_job_listings,
            self.search_persons,
            self.search_companies,
            self.enrich_person,
            self.enrich_company,
            self.get_linked_in_posts,
            self.search_linked_in_posts
        ]
