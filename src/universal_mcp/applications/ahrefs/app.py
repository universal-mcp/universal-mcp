from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class AhrefsApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="ahrefs", integration=integration, **kwargs)
        self.base_url = "https://api.ahrefs.com/v3"

    def crawler_ips(self, output=None) -> dict[str, Any]:
        """
        Retrieve the list of public crawler IP addresses from the API.

        Args:
            output: Optional; the desired format of the output. If provided, it is included as a query parameter in the request.

        Returns:
            A dictionary containing the API response with crawler IP information.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.

        Tags:
            fetch, crawler-ips, api
        """
        url = f"{self.base_url}/public/crawler-ips"
        query_params = {k: v for k, v in [("output", output)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def crawler_ip_ranges(self, output=None) -> dict[str, Any]:
        """
        Fetches the current public crawler IP ranges from the API, optionally specifying output format.

        Args:
            output: Optional output format for the IP ranges list. If None, the default format is used.

        Returns:
            A dictionary containing the crawler IP ranges as provided by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            fetch, crawler-ip, network, api, important
        """
        url = f"{self.base_url}/public/crawler-ip-ranges"
        query_params = {k: v for k, v in [("output", output)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def limits_and_usage(self, output=None) -> dict[str, Any]:
        """
        Retrieves current API subscription limits and usage statistics from the service.

        Args:
            output: Optional; specifies the output format or filter for the request. If None, default output is used.

        Returns:
            A dictionary containing details about subscription limits and current usage statistics.

        Raises:
            HTTPError: If the HTTP request to the subscription-info endpoint fails or returns an error status.

        Tags:
            fetch, limits, usage, subscription, api
        """
        url = f"{self.base_url}/subscription-info/limits-and-usage"
        query_params = {k: v for k, v in [("output", output)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_analysis(
        self,
        select,
        targets,
        order_by=None,
        country=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Submits a batch analysis request with specified parameters and returns the analysis results as a dictionary.

        Args:
            select: The fields to be selected in the batch analysis request. Must not be None.
            targets: A list or structure specifying the analysis targets. Must not be None.
            order_by: Optional. Specifies sorting for the analysis output.
            country: Optional. Country code filter for the analysis.
            volume_mode: Optional. Analysis mode related to volume calculation.
            output: Optional. Specifies the desired output format or configuration.

        Returns:
            A dictionary containing the batch analysis results returned by the API.

        Raises:
            ValueError: Raised if either 'select' or 'targets' is None.
            requests.HTTPError: Raised if the HTTP request to the batch analysis endpoint fails.

        Tags:
            batch-analysis, submit, ai, management, async_job
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if targets is None:
            raise ValueError("Missing required parameter 'targets'")
        request_body = {
            "select": select,
            "order_by": order_by,
            "country": country,
            "volume_mode": volume_mode,
            "targets": targets,
            "output": output,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/batch-analysis/batch-analysis"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def serp_overview(
        self, select, country, keyword, top_positions=None, date=None, output=None
    ) -> dict[str, Any]:
        """
        Retrieves a SERP (Search Engine Results Page) overview report based on specified selection, country, and keyword criteria.

        Args:
            select: str. The type of overview or metrics to retrieve. Required.
            country: str. The country code indicating the region for the SERP data. Required.
            keyword: str. The target keyword for which to fetch the SERP overview. Required.
            top_positions: Optional[int]. The number of top-ranking positions to include in the results. Defaults to None.
            date: Optional[str]. The specific date for the SERP data in YYYY-MM-DD format. Defaults to None.
            output: Optional[str]. Output format or preferences for the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the SERP overview results as returned by the external API.

        Raises:
            ValueError: If any of the required parameters ('select', 'country', or 'keyword') are missing or None.
            requests.HTTPError: If the HTTP request to the API fails or an invalid response is received.

        Tags:
            serp, overview, fetch, search, report, important
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        if keyword is None:
            raise ValueError("Missing required parameter 'keyword'")
        url = f"{self.base_url}/serp-overview/serp-overview"
        query_params = {
            k: v
            for k, v in [
                ("select", select),
                ("top_positions", top_positions),
                ("date", date),
                ("country", country),
                ("keyword", keyword),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def overview(
        self,
        select,
        date,
        device,
        project_id,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        date_compared=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves rank tracking overview data for a specified project, date, and device.

        Args:
            select: Fields to include in the response (required).
            date: Date for which to retrieve data (required).
            device: Device type to filter data by (required).
            project_id: ID of the project to retrieve data for (required).
            timeout: Maximum time to wait for the response in seconds.
            offset: Number of items to skip in the result set.
            limit: Maximum number of items to return.
            order_by: Field to sort results by.
            where: Filter condition for the results.
            date_compared: Date to compare results against.
            volume_mode: Mode for volume calculations.
            output: Output format of the response.

        Returns:
            A dictionary containing rank tracking overview data.

        Raises:
            ValueError: Raised when any of the required parameters (select, date, device, project_id) is not provided.

        Tags:
            retrieve, overview, rank-tracker, data, api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        if device is None:
            raise ValueError("Missing required parameter 'device'")
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/rank-tracker/overview"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("date_compared", date_compared),
                ("date", date),
                ("device", device),
                ("project_id", project_id),
                ("volume_mode", volume_mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def competitors_overview(
        self,
        select,
        date,
        device,
        project_id,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        date_compared=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves an overview of competitor rankings for a specified project and criteria.

        Args:
            select: Fields to retrieve in the overview; required.
            date: Date for which the overview is requested (format: YYYY-MM-DD); required.
            device: Device type to filter ranking data (e.g., 'desktop', 'mobile'); required.
            project_id: Unique identifier for the target project; required.
            timeout: Optional request timeout in seconds.
            offset: Optional pagination offset for the result set.
            limit: Optional maximum number of records to return.
            order_by: Optional sorting order of the results.
            where: Optional filter expression for result narrowing.
            date_compared: Optional comparison date for historical ranking comparison.
            volume_mode: Optional mode for search volume calculation.
            output: Optional format for the output data.

        Returns:
            A dictionary containing the competitors overview data retrieved from the rank tracker service.

        Raises:
            ValueError: If any of the required parameters ('select', 'date', 'device', or 'project_id') are missing.
            requests.HTTPError: If the HTTP request to the underlying service fails or returns an error response.

        Tags:
            competitors-overview, fetch, api, management, batch
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        if device is None:
            raise ValueError("Missing required parameter 'device'")
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/rank-tracker/competitors-overview"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("date_compared", date_compared),
                ("date", date),
                ("device", device),
                ("project_id", project_id),
                ("volume_mode", volume_mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def projects(self, output=None) -> dict[str, Any]:
        """
        Retrieves a list of site audit projects from the configured base URL, optionally specifying an output format.

        Args:
            output: Optional; the desired output format for the project list (e.g., 'json', 'csv'). If None, defaults to the API's standard format.

        Returns:
            A dictionary containing project information returned by the site audit projects API.

        Raises:
            HTTPError: Raised if the HTTP request to retrieve the project list encounters an unsuccessful status code.

        Tags:
            list, projects, api, http-get, site-audit
        """
        url = f"{self.base_url}/site-audit/projects"
        query_params = {k: v for k, v in [("output", output)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def domain_rating(self, target, date, protocol=None, output=None) -> dict[str, Any]:
        """
        Fetches the domain rating and related metrics for a specified target and date.

        Args:
            target: str. The domain or URL to analyze. Required.
            date: str. The date for which to retrieve the domain rating data. Required.
            protocol: str or None. The protocol (e.g., 'http', 'https') to use for the request. Optional.
            output: str or None. The output format for the response, if applicable. Optional.

        Returns:
            dict[str, Any]: A dictionary containing domain rating data and associated metrics for the given target and date.

        Raises:
            ValueError: If 'target' or 'date' parameters are missing.
            requests.HTTPError: If the HTTP request fails or an error response is returned by the server.

        Tags:
            fetch, domain-rating, api, management
        """
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/domain-rating"
        query_params = {
            k: v
            for k, v in [
                ("protocol", protocol),
                ("target", target),
                ("date", date),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def backlinks_stats(
        self, target, date, protocol=None, mode=None, output=None
    ) -> dict[str, Any]:
        """
        Retrieves backlink statistics for a specified target and date, with optional filters for protocol, mode, and output format.

        Args:
            target: str. The target domain or URL for which to retrieve backlink statistics.
            date: str. The date for which the backlink statistics are requested (typically in 'YYYY-MM-DD' format).
            protocol: Optional[str]. Type of protocol filter to apply (e.g., 'http', 'https'). Defaults to None.
            mode: Optional[str]. The analysis mode or additional filter to refine results. Defaults to None.
            output: Optional[str]. The output format for the results. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the backlink statistics data retrieved from the API.

        Raises:
            ValueError: Raised if the required 'target' or 'date' parameters are missing.
            requests.HTTPError: Raised if the HTTP request to the underlying API fails or returns a non-success status code.

        Tags:
            fetch, backlinks, stats, seo, important
        """
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/backlinks-stats"
        query_params = {
            k: v
            for k, v in [
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("date", date),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def outlinks_stats(
        self, target, protocol=None, mode=None, output=None
    ) -> dict[str, Any]:
        """
        Retrieves outbound link statistics for the specified target from the site explorer API.

        Args:
            target: str. The required target (such as a domain or URL) for which to fetch outlink statistics.
            protocol: Optional[str]. The protocol filter to apply (e.g., 'http', 'https'). Defaults to None.
            mode: Optional[str]. The mode of operation or data retrieval (if supported by the API). Defaults to None.
            output: Optional[str]. The desired output format, if applicable. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the outlink statistics retrieved from the API.

        Raises:
            ValueError: If the required 'target' parameter is not provided.
            requests.HTTPError: If the API request fails or returns a non-success status code.

        Tags:
            outlinks, fetch, site-explorer, stats, api
        """
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/outlinks-stats"
        query_params = {
            k: v
            for k, v in [
                ("protocol", protocol),
                ("mode", mode),
                ("target", target),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def metrics(
        self,
        target,
        date,
        volume_mode=None,
        country=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves metrics data from the site explorer API endpoint.

        Args:
            target: The target website or URL to retrieve metrics for.
            date: The date for which to retrieve metrics data.
            volume_mode: Optional. The volume mode parameter for filtering results.
            country: Optional. The country code to filter results by.
            protocol: Optional. The protocol (e.g., 'http', 'https') to filter results by.
            mode: Optional. The mode parameter for controlling the type of metrics returned.
            output: Optional. The format of the output data.

        Returns:
            A dictionary containing the metrics data retrieved from the API.

        Raises:
            ValueError: Raised when required parameters 'target' or 'date' are missing.
            HTTPError: Raised when the API request fails (via raise_for_status()).

        Tags:
            retrieve, metrics, site-explorer, api, data
        """
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/metrics"
        query_params = {
            k: v
            for k, v in [
                ("volume_mode", volume_mode),
                ("country", country),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("date", date),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def refdomains_history(
        self,
        date_from,
        target,
        history_grouping=None,
        date_to=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves the historical data of reference domains from a specified site.

        Args:
            date_from: The start date for retrieving historical data.
            target: The target for which to retrieve reference domains data.
            history_grouping: Optional parameter to specify how the history should be grouped.
            date_to: Optional end date for retrieving historical data.
            protocol: Optional protocol to filter the data.
            mode: Optional mode to use for the query.
            output: Optional format of the output.

        Returns:
            A dictionary containing historical reference domains data.

        Raises:
            ValueError: Raised if either 'date_from' or 'target' parameter is missing.

        Tags:
            search, history  , management, ai
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/refdomains-history"
        query_params = {
            k: v
            for k, v in [
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def domain_rating_history(
        self, date_from, target, history_grouping=None, date_to=None, output=None
    ) -> dict[str, Any]:
        """
        Retrieves historical domain rating data for a specified target within a given date range.

        Args:
            date_from: str. The start date for the domain rating history range (format: YYYY-MM-DD). Required.
            target: str. The domain or target for which the rating history is requested. Required.
            history_grouping: Optional[str]. Granularity for grouping history data (e.g., by day, week, or month).
            date_to: Optional[str]. The end date for the domain rating history range (format: YYYY-MM-DD).
            output: Optional[str]. Desired output format or additional output options.

        Returns:
            dict[str, Any]: Parsed JSON response containing domain rating history data for the specified parameters.

        Raises:
            ValueError: If 'date_from' or 'target' is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            fetch, domain-rating, history, api
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/domain-rating-history"
        query_params = {
            k: v
            for k, v in [
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("target", target),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def url_rating_history(
        self, date_from, target, history_grouping=None, date_to=None, output=None
    ) -> dict[str, Any]:
        """
        Retrieves URL rating history data for a specified target within a date range.

        Args:
            date_from: Required string representing the start date for the rating history query.
            target: Required string representing the URL target for which to retrieve rating history.
            history_grouping: Optional parameter to specify how the history data should be grouped or aggregated.
            date_to: Optional string representing the end date for the rating history query. If not provided, likely defaults to current date.
            output: Optional parameter to specify the format or structure of the output data.

        Returns:
            A dictionary containing the URL rating history data for the specified target and date range.

        Raises:
            ValueError: Raised when required parameters 'date_from' or 'target' are not provided (None).
            HTTPError: Raised when the API request fails, as triggered by response.raise_for_status().

        Tags:
            retrieve, rating, history, url, query, api
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/url-rating-history"
        query_params = {
            k: v
            for k, v in [
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("target", target),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def pages_history(
        self,
        date_from,
        target,
        history_grouping=None,
        date_to=None,
        country=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves historical page data for a target using specified filters.

        Args:
            date_from: str. The start date for the historical data in YYYY-MM-DD format. Required.
            target: str. The URL or identifier of the website or resource to retrieve history for. Required.
            history_grouping: str, optional. The method for grouping historical data, such as by day, week, or month.
            date_to: str, optional. The end date for the historical data in YYYY-MM-DD format.
            country: str, optional. The country code (e.g., 'US', 'GB') to filter data by region.
            protocol: str, optional. The protocol to filter results, such as 'http' or 'https'.
            mode: str, optional. The operation mode for the request, specifying data type or level.
            output: str, optional. The desired output format or additional output controls.

        Returns:
            dict[str, Any]: A dictionary containing the JSON response with the historical page data matching the filters.

        Raises:
            ValueError: If 'date_from' or 'target' is not provided.
            requests.HTTPError: If the underlying HTTP request fails or returns an unsuccessful status code.

        Tags:
            fetch, history, site-explorer, data, management
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/pages-history"
        query_params = {
            k: v
            for k, v in [
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("country", country),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def metrics_history(
        self,
        date_from,
        target,
        select=None,
        volume_mode=None,
        history_grouping=None,
        date_to=None,
        country=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves historical metrics based on specified parameters.

        Args:
            date_from: The start date for metrics history (required).
            target: The target for which to retrieve metrics history (required).
            select: Optional parameters to select which metrics to include.
            volume_mode: Mode for handling volume data.
            history_grouping: Grouping strategy for historical data.
            date_to: The end date for metrics history.
            country: Country filter for metrics.
            protocol: Protocol filter for metrics.
            mode: Mode for the request.
            output: Format of the output.

        Returns:
            A dictionary containing historical metrics.

        Raises:
            ValueError: Raised if either 'date_from' or 'target' is missing.

        Tags:
            metrics, history, data-retrieval, api-call
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/metrics-history"
        query_params = {
            k: v
            for k, v in [
                ("select", select),
                ("volume_mode", volume_mode),
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("country", country),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def keywords_history(
        self,
        date_from,
        target,
        select=None,
        history_grouping=None,
        date_to=None,
        country=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches the historical keyword rankings and performance data for a specified target within an optional date range and set of filters.

        Args:
            date_from: str. The start date for the historical data query (required).
            target: str. The target for which keyword history is retrieved, such as a domain or URL (required).
            select: Optional[str]. Specifies which metrics or fields to return in the results.
            history_grouping: Optional[str]. Determines how the historical data is grouped, e.g., by keyword or date.
            date_to: Optional[str]. The end date for the historical data query.
            country: Optional[str]. Country code for filtering results.
            protocol: Optional[str]. Protocol (http or https) to filter the target.
            mode: Optional[str]. Mode or type of data retrieval as supported by the API.
            output: Optional[str]. Specifies output format or additional retrieval instructions.

        Returns:
            dict[str, Any]: Parsed JSON response containing historical keyword data for the specified target.

        Raises:
            ValueError: Raised if either 'date_from' or 'target' is missing.
            requests.HTTPError: Raised if the HTTP request fails or the API responds with an error status.

        Tags:
            fetch, retrieve, keywords-history, seo, analytics, api
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/keywords-history"
        query_params = {
            k: v
            for k, v in [
                ("select", select),
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("country", country),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def metrics_by_country(
        self,
        target,
        date,
        volume_mode=None,
        limit=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches site metrics grouped by country for a specified target and date.

        Args:
            target: str. The target domain or URL for which to retrieve country-based metrics. Required.
            date: str. The date for which metrics should be retrieved, in YYYY-MM-DD format. Required.
            volume_mode: Optional[str]. Controls how volume is calculated or presented. Defaults to None.
            limit: Optional[int]. The maximum number of country results to return. Defaults to None.
            protocol: Optional[str]. The protocol filter for the target (e.g., 'http', 'https'). Defaults to None.
            mode: Optional[str]. The operational mode for the metric query. Defaults to None.
            output: Optional[str]. The output format or type. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing metrics data grouped by country for the specified target and date.

        Raises:
            ValueError: If 'target' or 'date' is not provided.
            requests.HTTPError: If the HTTP request to the metrics API endpoint fails.

        Tags:
            fetch, metrics, country, site-explorer, api
        """
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/metrics-by-country"
        query_params = {
            k: v
            for k, v in [
                ("volume_mode", volume_mode),
                ("limit", limit),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("date", date),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def pages_by_traffic(
        self,
        target,
        volume_mode=None,
        country=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of top pages for a specified target domain or URL, ranked by estimated organic search traffic.

        Args:
            target: str. The domain or URL for which to retrieve top pages by estimated organic traffic. Required.
            volume_mode: str, optional. The search volume calculation model to use (e.g., monthly average, rolling average).
            country: str, optional. The country code to filter organic traffic data (e.g., 'US', 'GB').
            protocol: str, optional. The protocol to filter results by ('http', 'https').
            mode: str, optional. The mode of data retrieval or analysis, if applicable.
            output: str, optional. The desired format of the response output.

        Returns:
            dict. The JSON-decoded response containing details about top pages driving traffic to the target.

        Raises:
            ValueError: If the required 'target' parameter is not provided.
            requests.HTTPError: If the HTTP request is unsuccessful or the API returns an error response.

        Tags:
            list, traffic, pages, analytics, batch
        """
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/pages-by-traffic"
        query_params = {
            k: v
            for k, v in [
                ("volume_mode", volume_mode),
                ("country", country),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def all_backlinks(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        aggregation=None,
        history=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves all backlinks information for a specified target using various query parameters.

        Args:
            select: Required. Specifies the fields to select in the response.
            target: Required. The target URL or domain to retrieve backlinks for.
            timeout: Optional. Maximum time in seconds to wait for the response.
            offset: Optional. Number of items to skip before starting to collect the result set.
            limit: Optional. Maximum number of items to return in the result set.
            order_by: Optional. Field(s) to sort the results by.
            where: Optional. Filter condition for the results.
            protocol: Optional. Protocol filter (e.g., http, https).
            mode: Optional. Mode of operation for the backlinks search.
            aggregation: Optional. Aggregation method for the results.
            history: Optional. Whether to include historical data.
            output: Optional. Format of the output data.

        Returns:
            A dictionary containing the backlinks data with various attributes based on the selected fields.

        Raises:
            ValueError: Raised when required parameters 'select' or 'target' are missing.
            HTTPError: Raised when the API request fails.

        Tags:
            backlinks, retrieve, search, api, site-explorer, important
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/all-backlinks"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("aggregation", aggregation),
                ("history", history),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def broken_backlinks(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        aggregation=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches broken backlink data for the specified target from the site explorer API endpoint.

        Args:
            select: str. Required. Specifies the fields to include in the response.
            target: str. Required. The target domain or URL to analyze for broken backlinks.
            timeout: Optional[int]. Maximum time in seconds to wait for the response.
            offset: Optional[int]. Index of the first result to return (for pagination).
            limit: Optional[int]. Maximum number of results to return.
            order_by: Optional[str]. Field(s) to order the results by.
            where: Optional[str]. Filter expression for narrowing the result set.
            protocol: Optional[str]. Protocol filter (e.g., 'http', 'https').
            mode: Optional[str]. Exploration mode (e.g., 'domain', 'url').
            aggregation: Optional[str]. Aggregation method for results.
            output: Optional[str]. Output format specifier.

        Returns:
            dict[str, Any]: Parsed JSON data containing details about broken backlinks for the specified target.

        Raises:
            ValueError: If either 'select' or 'target' is not provided.
            requests.HTTPError: If the HTTP request to the API endpoint fails.

        Tags:
            fetch, broken-backlinks, site-explorer, api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/broken-backlinks"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("aggregation", aggregation),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def refdomains(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        history=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves referring domains data for a specified target using the Site Explorer API endpoint.

        Args:
            select: Fields to include in the response; required.
            target: Target domain, URL, or entity to analyze; required.
            timeout: Maximum request time in seconds (optional).
            offset: Number of items to skip for pagination (optional).
            limit: Maximum number of results to return (optional).
            order_by: Specifies field(s) and order to sort results by (optional).
            where: Filter conditions in a query-like format (optional).
            protocol: Protocol filter (e.g., 'http', 'https') (optional).
            mode: Analysis mode or data scope (optional).
            history: Include historical data if specified (optional).
            output: Format of the response output (optional).

        Returns:
            Dictionary representing the JSON response from the referring domains API endpoint.

        Raises:
            ValueError: Raised if 'select' or 'target' parameters are missing.
            requests.HTTPError: Raised if the HTTP response contained an unsuccessful status code.

        Tags:
            refdomains, fetch, api, site-explorer, data-retrieval
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/refdomains"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("history", history),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def anchors(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        history=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches anchor text distribution data for a specified target using given query parameters.

        Args:
            select: str or list. Columns or fields to include in the response. Required.
            target: str. The target URL, domain, or identifier from which to retrieve anchor data. Required.
            timeout: Optional[int]. Maximum time in seconds to wait for the API response.
            offset: Optional[int]. Offset for paginated results.
            limit: Optional[int]. Maximum number of records to return.
            order_by: Optional[str]. Sorting order of the results.
            where: Optional[str]. Filter conditions for the query.
            protocol: Optional[str]. Protocol filter (e.g., 'http', 'https').
            mode: Optional[str]. Query mode or method.
            history: Optional[str]. Historical range or filter.
            output: Optional[str]. Desired output format.

        Returns:
            dict[str, Any]: Parsed JSON response containing anchor text distribution data.

        Raises:
            ValueError: If the required 'select' or 'target' parameter is missing.
            requests.HTTPError: If the HTTP request to the API endpoint fails or returns an error status.

        Tags:
            anchors, fetch, api, site-explorer, management
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/anchors"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("history", history),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def linkeddomains(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves linked domains for a specified target using the site explorer API endpoint.

        Args:
            select: str. Specifies the fields to select in the response. Required.
            target: str. The entity (such as a domain or URL) for which to retrieve linked domains. Required.
            timeout: Optional[int]. Maximum time in seconds to wait for the API response.
            offset: Optional[int]. Number of records to skip before starting to return results.
            limit: Optional[int]. Maximum number of records to return.
            order_by: Optional[str]. Field by which to order the returned results.
            where: Optional[str]. Filter to apply to the results.
            protocol: Optional[str]. Protocol (e.g., 'http' or 'https') to filter the results.
            mode: Optional[str]. Operation mode for the query.
            output: Optional[str]. Specifies the format or type of output.

        Returns:
            dict[str, Any]: Parsed JSON response containing linked domains data for the given target.

        Raises:
            ValueError: If either 'select' or 'target' is not provided.
            requests.exceptions.HTTPError: If the API request returns an unsuccessful status code.

        Tags:
            fetch, site-explorer, linkeddomains, api, batch
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/linkeddomains"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def linked_anchors_external(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetch linked external anchor data for a specified target using provided selection and filtering criteria.

        Args:
            select: str. Specifies which fields to select in the result; required.
            target: str. The target entity (e.g., domain, URL) for which to fetch external anchor data; required.
            timeout: Optional[int]. Timeout for the request in seconds.
            offset: Optional[int]. Number of records to skip before starting to return results.
            limit: Optional[int]. Maximum number of records to return.
            order_by: Optional[str]. Field(s) to order results by.
            where: Optional[str]. Additional query/filter constraints in string format.
            protocol: Optional[str]. Protocol to use for fetching data, such as 'http' or 'https'.
            mode: Optional[str]. Mode of operation for the request.
            output: Optional[str]. Desired data output format.

        Returns:
            dict[str, Any]: A dictionary containing the linked external anchor data matching the specified criteria.

        Raises:
            ValueError: Raised if the required parameters 'select' or 'target' are not provided.
            requests.HTTPError: Raised if the HTTP request fails or returns an error response status.

        Tags:
            fetch, list, anchors, external, site-explorer, api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/linked-anchors-external"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def linked_anchors_internal(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches internal linked anchor data for a specified target from the site explorer API, applying optional filtering and query parameters.

        Args:
            select: List or string specifying which fields to retrieve from the results. Required.
            target: String indicating the target URL, domain, or identifier for which internal linked anchor data is requested. Required.
            timeout: Optional integer or float specifying the request timeout duration, in seconds.
            offset: Optional integer specifying the number of records to skip before starting to return results.
            limit: Optional integer specifying the maximum number of records to return.
            order_by: Optional string or list specifying the field(s) by which to sort the results.
            where: Optional string providing additional filter conditions for the query.
            protocol: Optional string to specify the protocol (e.g., 'http', 'https') to use in filtering.
            mode: Optional string indicating the exploration mode or data granularity.
            output: Optional string specifying the output format or data structure.

        Returns:
            A dictionary containing the response data for internal linked anchors matching the specified criteria.

        Raises:
            ValueError: Raised if the required 'select' or 'target' parameters are missing.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status.

        Tags:
            site-explorer, linked-anchors, fetch, api, internal-links, management
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/linked-anchors-internal"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organic_keywords(
        self,
        select,
        target,
        country,
        date,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        date_compared=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieve organic keyword data for a specified target and date from the Site Explorer API endpoint.

        Args:
            select: str. Comma-separated fields to include in the response. Required.
            target: str. The domain, URL, or path to retrieve keyword data for. Required.
            country: str. Country code specifying the regional database. Required.
            date: str. The date for which to fetch keyword data, in YYYY-MM-DD format. Required.
            timeout: int, optional. Request timeout in seconds.
            offset: int, optional. Number of items to skip before starting to collect the result set.
            limit: int, optional. Maximum number of results to return.
            order_by: str, optional. Field(s) to order results by.
            where: str, optional. Filter condition(s) for the query.
            protocol: str, optional. Protocol to filter by (e.g., 'http', 'https').
            mode: str, optional. SERP mode (e.g., 'domain', 'subdomain').
            date_compared: str, optional. A second date for comparison, in YYYY-MM-DD format.
            volume_mode: str, optional. Keyword search volume calculation mode.
            output: str, optional. Output format (e.g., 'json').

        Returns:
            dict[str, Any]: Parsed JSON response containing organic keyword data.

        Raises:
            ValueError: Raised when the required parameters 'select', 'target', 'country', or 'date' are missing.
            requests.HTTPError: Raised if the API request fails with an HTTP error status.

        Tags:
            fetch, keywords, organic, site-explorer, batch  , api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/organic-keywords"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("country", country),
                ("date_compared", date_compared),
                ("date", date),
                ("volume_mode", volume_mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organic_competitors(
        self,
        select,
        target,
        country,
        date,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        date_compared=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves organic competitors data for a specified target using the Site Explorer API.

        Args:
            select: list[str]. The fields to be returned in the response. Required.
            target: str. The target domain, URL, or resource to analyze. Required.
            country: str. The country or region code for the data. Required.
            date: str. The date for which to retrieve competitor data, in the expected format (e.g., 'YYYY-MM-DD'). Required.
            timeout: Optional[int]. The maximum time in seconds to wait for the response.
            offset: Optional[int]. The starting point within the collection of returned results.
            limit: Optional[int]. The maximum number of records to return.
            order_by: Optional[str]. The sorting order for the results.
            where: Optional[str]. Additional filtering to apply to the query.
            protocol: Optional[str]. The protocol to use (e.g., 'http', 'https').
            mode: Optional[str]. The mode for the data retrieval.
            date_compared: Optional[str]. A comparison date for historical data analysis.
            volume_mode: Optional[str]. The volume calculation mode.
            output: Optional[str]. The desired output format (e.g., 'json').

        Returns:
            dict[str, Any]: The JSON response from the API as a dictionary containing organic competitors data.

        Raises:
            ValueError: If any of the required parameters ('select', 'target', 'country', or 'date') are missing.
            requests.HTTPError: If the HTTP request to the Site Explorer API fails or an error status code is returned.

        Tags:
            fetch, organic-competitors, site-explorer, api, data-retrieva, important
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/organic-competitors"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("country", country),
                ("date_compared", date_compared),
                ("date", date),
                ("volume_mode", volume_mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def top_pages(
        self,
        select,
        target,
        date,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        country=None,
        date_compared=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves top pages data for a specified target and date from the site explorer API with customizable query parameters.

        Args:
            select: Fields to include in the output. Must be specified.
            target: The target domain, URL, or resource to analyze. Must be specified.
            date: The date for which to retrieve top page data. Must be specified.
            timeout: Optional request timeout (in seconds).
            offset: Optional index of the first result to return, for pagination.
            limit: Optional maximum number of results to return.
            order_by: Optional sorting instructions for results.
            where: Optional filter conditions to apply to the results.
            protocol: Optional protocol filter (e.g., 'http', 'https').
            mode: Optional mode or metric for the analysis.
            country: Optional country code to filter results by geography.
            date_compared: Optional comparison date for comparative metrics.
            volume_mode: Optional volume mode or granularity.
            output: Optional output format for the API response.

        Returns:
            A dictionary containing the top pages data retrieved from the API for the specified parameters.

        Raises:
            ValueError: If 'select', 'target', or 'date' is not provided.
            requests.HTTPError: If the API request returns an unsuccessful HTTP status code.

        Tags:
            fetch, top-pages, site-explorer, api, management
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/top-pages"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("country", country),
                ("date_compared", date_compared),
                ("date", date),
                ("volume_mode", volume_mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def paid_pages(
        self,
        select,
        target,
        date,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        country=None,
        date_compared=None,
        volume_mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches paid pages data from the Site Explorer API based on specified filters.

        Args:
            select: str. The fields to retrieve in the response. Required.
            target: str. The target domain, URL, or entity for which paid pages data is requested. Required.
            date: str. The reference date for the data. Required.
            timeout: Optional[int]. The request timeout in seconds.
            offset: Optional[int]. The number of items to skip before starting to collect the result set.
            limit: Optional[int]. Maximum number of records to retrieve.
            order_by: Optional[str]. Sorting order for the result set.
            where: Optional[str]. Filtering conditions for the results.
            protocol: Optional[str]. Protocol filter (e.g., 'http' or 'https').
            mode: Optional[str]. The exploration mode or analysis type.
            country: Optional[str]. Country code for regional data filtering.
            date_compared: Optional[str]. Secondary date for comparison analysis.
            volume_mode: Optional[str]. Mode used for volume calculations.
            output: Optional[str]. Desired response format (e.g., 'json').

        Returns:
            dict[str, Any]: JSON response containing paid pages data matching the provided filters.

        Raises:
            ValueError: If any of the required parameters ('select', 'target', or 'date') are missing.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            fetch, paid-pages, site-explorer, api, data-retrieval
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/site-explorer/paid-pages"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("country", country),
                ("date_compared", date_compared),
                ("date", date),
                ("volume_mode", volume_mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def best_by_external_links(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        history=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches data about the best-performing pages of a target site based on external links, with various filtering and output options.

        Args:
            select: str. Comma-separated list of fields to include in the response. Required.
            target: str. The target domain or URL to analyze. Required.
            timeout: Optional[int]. Maximum time in seconds to wait for the response.
            offset: Optional[int]. Number of items to skip before starting to collect the result set.
            limit: Optional[int]. Maximum number of results to return.
            order_by: Optional[str]. Field(s) to sort results by.
            where: Optional[str]. Filtering conditions to apply to the results.
            protocol: Optional[str]. Protocol to use (e.g., http, https) when target is a domain.
            mode: Optional[str]. Mode of analysis (if applicable).
            history: Optional[str]. Whether to include historical data.
            output: Optional[str]. Desired output format (e.g., json, csv).

        Returns:
            dict[str, Any]: JSON response containing details about the best-by-external-links pages for the target.

        Raises:
            ValueError: Raised if 'select' or 'target' parameters are missing.
            requests.HTTPError: Raised if the HTTP request to the external service fails.

        Tags:
            fetch, list, site-explorer, external-links, api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/best-by-external-links"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("history", history),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def best_by_internal_links(
        self,
        select,
        target,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves the best-performing internal links for a specified target using the site explorer API endpoint.

        Args:
            select: str. Comma-separated list of fields to include in the response. Required.
            target: str. The URL, domain, or path to analyze. Required.
            timeout: Optional[int]. Maximum time to wait for the API response, in seconds.
            offset: Optional[int]. Offset for paginated results.
            limit: Optional[int]. Maximum number of results to return.
            order_by: Optional[str]. Field by which to order the results.
            where: Optional[str]. Conditions to filter the results.
            protocol: Optional[str]. Protocol to use (e.g., 'http', 'https').
            mode: Optional[str]. Operational mode for the API request.
            output: Optional[str]. Desired response format (e.g., 'json').

        Returns:
            dict[str, Any]: The JSON response from the API containing details about the best internal links for the specified target.

        Raises:
            ValueError: If either 'select' or 'target' parameters are not provided.
            requests.HTTPError: If the API response contains an HTTP error status code.

        Tags:
            fetch, internal-links, site-explorer, api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/best-by-internal-links"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def total_search_volume_history(
        self,
        date_from,
        target,
        volume_mode=None,
        top_positions=None,
        history_grouping=None,
        date_to=None,
        country=None,
        protocol=None,
        mode=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches the total historical search volume data for a specified target within a given date range and optional filters.

        Args:
            date_from: str. Start date for the search volume history (required).
            target: str. The target entity to retrieve data for, such as a domain or URL (required).
            volume_mode: Optional[str]. Specifies the search volume calculation mode.
            top_positions: Optional[int]. Limits results to a specific range of top search positions.
            history_grouping: Optional[str]. Determines how history data is grouped (e.g., daily, weekly, monthly).
            date_to: Optional[str]. End date for the search volume history.
            country: Optional[str]. Country code for filtering the data.
            protocol: Optional[str]. Protocol to use for the target (e.g., 'http', 'https').
            mode: Optional[str]. API mode or additional operation mode parameter.
            output: Optional[str]. Desired output format (e.g., 'json').

        Returns:
            dict[str, Any]: A dictionary containing the requested search volume history data.

        Raises:
            ValueError: Raised if either 'date_from' or 'target' is not provided.
            requests.HTTPError: Raised if the HTTP request to the API fails (non-2xx response).

        Tags:
            fetch, search-volume, history, api, report
        """
        if date_from is None:
            raise ValueError("Missing required parameter 'date_from'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        url = f"{self.base_url}/site-explorer/total-search-volume-history"
        query_params = {
            k: v
            for k, v in [
                ("volume_mode", volume_mode),
                ("top_positions", top_positions),
                ("history_grouping", history_grouping),
                ("date_to", date_to),
                ("date_from", date_from),
                ("country", country),
                ("protocol", protocol),
                ("target", target),
                ("mode", mode),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def keyword_explorer_overview(
        self,
        select,
        country,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        target_mode=None,
        target=None,
        target_position=None,
        search_engine=None,
        keywords=None,
        keyword_list_id=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves an overview of keyword metrics and data from the keywords explorer API endpoint based on the specified filters and parameters.

        Args:
            select: Fields to retrieve in the response (required).
            country: Country code or name for which keyword data is requested (required).
            timeout: Maximum time in seconds to wait for the response (optional).
            offset: Number of items to skip before starting to collect the result set (optional).
            limit: Maximum number of items to return in the response (optional).
            order_by: Field(s) to order the results by (optional).
            where: Additional filtering criteria for querying keywords (optional).
            target_mode: Specifies the targeting mode for analysis (optional).
            target: Target entity for the keyword analysis, such as a domain or URL (optional).
            target_position: Position or ranking target for the keyword analysis (optional).
            search_engine: Search engine specification for the query (optional).
            keywords: List of keywords or a single keyword to analyze (optional).
            keyword_list_id: ID of a saved keyword list to use for the query (optional).
            output: Desired format or structure of the output data (optional).

        Returns:
            A dictionary containing keyword overview metrics and related data from the API response.

        Raises:
            ValueError: Raised if the required parameter 'select' or 'country' is missing.
            requests.HTTPError: Raised if the HTTP request to the keywords explorer API fails or returns an error response.

        Tags:
            keywords-explorer, overview, fetch, api
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        url = f"{self.base_url}/keywords-explorer/overview"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("target_mode", target_mode),
                ("target", target),
                ("target_position", target_position),
                ("country", country),
                ("search_engine", search_engine),
                ("keywords", keywords),
                ("keyword_list_id", keyword_list_id),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def volume_history(self, country, keyword, output=None) -> dict[str, Any]:
        """
        Fetches the historical search volume for a given keyword in a specified country.

        Args:
            country: str. The country code or name for which to retrieve keyword volume history. Must not be None.
            keyword: str. The keyword to query for historical volume data. Must not be None.
            output: Optional[str]. The desired output format or additional filter. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the volume history data for the specified keyword and country.

        Raises:
            ValueError: Raised if 'country' or 'keyword' parameters are not provided (i.e., are None).
            requests.HTTPError: Raised if the HTTP request fails or the remote server returns an error status code.

        Tags:
            fetch, volume-history, keywords, analytics
        """
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        if keyword is None:
            raise ValueError("Missing required parameter 'keyword'")
        url = f"{self.base_url}/keywords-explorer/volume-history"
        query_params = {
            k: v
            for k, v in [("country", country), ("keyword", keyword), ("output", output)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def volume_by_country(
        self, keyword, limit=None, search_engine=None, output=None
    ) -> dict[str, Any]:
        """
        Retrieves search volume by country for a given keyword.

        Args:
            keyword: Required keyword to search for.
            limit: Optional limit for the results.
            search_engine: Optional search engine to use.
            output: Optional output format specification.

        Returns:
            A dictionary containing the volume data by country.

        Raises:
            ValueError: Raised when the 'keyword' parameter is missing.

        Tags:
            search, scrape, volume, country
        """
        if keyword is None:
            raise ValueError("Missing required parameter 'keyword'")
        url = f"{self.base_url}/keywords-explorer/volume-by-country"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("search_engine", search_engine),
                ("keyword", keyword),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def matching_terms(
        self,
        select,
        country,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        search_engine=None,
        keywords=None,
        keyword_list_id=None,
        match_mode=None,
        terms=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves matching keyword terms from the keywords explorer API based on specified filters and search parameters.

        Args:
            select: Fields to include in the response; required.
            country: Country code to filter results; required.
            timeout: Request timeout in seconds.
            offset: Starting offset for paginated results.
            limit: Maximum number of results to return.
            order_by: Field(s) to sort the result by.
            where: Additional filters to apply to the query.
            search_engine: Search engine to use for keyword matching.
            keywords: Seed keywords to search for matching terms.
            keyword_list_id: ID of a predefined keyword list to use as a seed.
            match_mode: Mode of keyword matching (e.g., broad, exact).
            terms: Specific terms to match in keywords.
            output: Output format or additional output options.

        Returns:
            A dictionary containing the API response with the matching keyword terms and associated metadata.

        Raises:
            ValueError: If the 'select' or 'country' parameter is missing.
            requests.HTTPError: If the API request fails or returns a non-success status code.

        Tags:
            list, keywords, search, api, management
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        url = f"{self.base_url}/keywords-explorer/matching-terms"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("country", country),
                ("search_engine", search_engine),
                ("keywords", keywords),
                ("keyword_list_id", keyword_list_id),
                ("match_mode", match_mode),
                ("terms", terms),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def related_terms(
        self,
        select,
        country,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        keywords=None,
        keyword_list_id=None,
        view_for=None,
        terms=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Retrieves related keyword terms for a given selection and country, with optional filtering and pagination.

        Args:
            select: str. Fields to be returned for each related term. Required.
            country: str. Country code or identifier specifying the market context. Required.
            timeout: Optional[int]. Timeout value for the request in seconds.
            offset: Optional[int]. Number of records to skip for pagination.
            limit: Optional[int]. Maximum number of results to return.
            order_by: Optional[str]. Field(s) by which to order the returned results.
            where: Optional[Any]. Filtering conditions for the related terms.
            keywords: Optional[str]. Comma-separated string of keywords to find related terms for.
            keyword_list_id: Optional[str]. Identifier for a list of keywords to use as the basis for the search.
            view_for: Optional[str]. View context for the related terms (e.g., user-specific).
            terms: Optional[Any]. Specific terms for refining the related terms search.
            output: Optional[Any]. Output formatting or additional output options.

        Returns:
            dict. The JSON response containing related keyword terms and associated metadata.

        Raises:
            ValueError: If the required 'select' or 'country' parameter is missing.

        Tags:
            related-terms, search, keywords, api-call, management
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        url = f"{self.base_url}/keywords-explorer/related-terms"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("country", country),
                ("keywords", keywords),
                ("keyword_list_id", keyword_list_id),
                ("view_for", view_for),
                ("terms", terms),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_suggestions(
        self,
        select,
        country,
        timeout=None,
        offset=None,
        limit=None,
        order_by=None,
        where=None,
        search_engine=None,
        keywords=None,
        keyword_list_id=None,
        output=None,
    ) -> dict[str, Any]:
        """
        Fetches keyword search suggestions from the keywords explorer API based on the provided filtering and query parameters.

        Args:
            select: str. The fields to retrieve in the search results. Required.
            country: str. The country code for which to fetch suggestions. Required.
            timeout: Optional[int]. Maximum time in seconds to wait for the API response.
            offset: Optional[int]. Number of results to skip before starting to return results.
            limit: Optional[int]. Maximum number of results to return.
            order_by: Optional[str]. Sorting parameter for the search results.
            where: Optional[str]. Additional filtering conditions for the search.
            search_engine: Optional[str]. The search engine to use for suggestions.
            keywords: Optional[str]. Keywords to search for suggestions.
            keyword_list_id: Optional[str]. Identifier for a saved keyword list to filter suggestions.
            output: Optional[str]. Output format or additional output options.

        Returns:
            dict[str, Any]: JSON response containing the list of search suggestions and associated metadata.

        Raises:
            ValueError: If the required parameter 'select' or 'country' is missing.
            HTTPError: If the HTTP request to the keywords explorer API fails.

        Tags:
            search, keywords, api, suggestions
        """
        if select is None:
            raise ValueError("Missing required parameter 'select'")
        if country is None:
            raise ValueError("Missing required parameter 'country'")
        url = f"{self.base_url}/keywords-explorer/search-suggestions"
        query_params = {
            k: v
            for k, v in [
                ("timeout", timeout),
                ("offset", offset),
                ("limit", limit),
                ("order_by", order_by),
                ("where", where),
                ("select", select),
                ("country", country),
                ("search_engine", search_engine),
                ("keywords", keywords),
                ("keyword_list_id", keyword_list_id),
                ("output", output),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.crawler_ips,
            self.crawler_ip_ranges,
            self.limits_and_usage,
            self.batch_analysis,
            self.serp_overview,
            self.overview,
            self.competitors_overview,
            self.projects,
            self.domain_rating,
            self.backlinks_stats,
            self.outlinks_stats,
            self.metrics,
            self.refdomains_history,
            self.domain_rating_history,
            self.url_rating_history,
            self.pages_history,
            self.metrics_history,
            self.keywords_history,
            self.metrics_by_country,
            self.pages_by_traffic,
            self.all_backlinks,
            self.broken_backlinks,
            self.refdomains,
            self.anchors,
            self.linkeddomains,
            self.linked_anchors_external,
            self.linked_anchors_internal,
            self.organic_keywords,
            self.organic_competitors,
            self.top_pages,
            self.paid_pages,
            self.best_by_external_links,
            self.best_by_internal_links,
            self.total_search_volume_history,
            self.keyword_explorer_overview,
            self.volume_history,
            self.volume_by_country,
            self.matching_terms,
            self.related_terms,
            self.search_suggestions,
        ]
