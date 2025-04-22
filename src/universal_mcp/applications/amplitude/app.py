from typing import Any

from loguru import logger
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration

class AmplitudeApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='amplitude', integration=integration, **kwargs)
        self.base_url = "https://data-api.amplitude.com"
        self.api_key: str | None = None
        
    
    def _set_api_key(self):
        if self.api_key:
            return

        if not self.integration:
            raise ValueError("Integration is None. Cannot retrieve Amplitude API Key.")
        
        credentials = self.integration.get_credentials()
        if not credentials:
            raise ValueError(
                f"Failed to retrieve Amplitude API Key using integration '{self.integration.name}'. "
            )
        api_key = (credentials.get("api_key")
        or credentials.get("API_KEY")
        or credentials.get("apiKey")
    
        )
        if not api_key:
            raise ValueError("Amplitude API Key not found in credentials.")
        self.api_key = api_key

    def _get_headers(self) -> dict[str, str]:
        self._set_api_key()
        logger.info(f"Amplitude API Key: {self.api_key}")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def post_attribution(self, api_key=None, event=None) -> Any:
        """
        Sends an attribution event to the server using a POST request and returns the server's JSON response.
        
        Args:
            api_key: Optional; the API key to authenticate the request. If not provided, authentication may fail depending on server configuration.
            event: Optional; the event data as a string to include in the attribution request.
        
        Returns:
            The server's response as a JSON-deserialized Python object.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request fails or returns a non-success status code.
        
        Tags:
            post, attribution, api, important
        """
        url = f"{self.base_url}/attribution"
        query_params = {k: v for k, v in [('api_key', api_key), ('event', event)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_batch(self, request_body=None) -> dict[str, Any]:
        """
        Posts a batch request to the API.
        
        Args:
            request_body: Optional request body for the batch operation; defaults to None if not provided.
        
        Returns:
            A dictionary containing the response from the API.
        
        Raises:
            requests.exceptions.HTTPError: Raised when the HTTP request returns an unsuccessful status code.
            requests.exceptions.RequestException: Raised for any other request-related errors.
        
        Tags:
            batch, api-post, important
        """
        url = f"{self.base_url}/batch"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_cohorts(self, includeSyncInfo=None) -> dict[str, Any]:
        """
        Retrieves a list of cohorts from the API.
        
        Args:
            includeSyncInfo: Optional boolean that determines whether to include synchronization information in the response. If None, this parameter is omitted from the request.
        
        Returns:
            A dictionary containing cohort information. The structure includes cohort details with cohort IDs as keys and their respective properties as values.
        
        Raises:
            HTTPError: Raised when the API request fails, such as with 4xx or 5xx status codes.
            ConnectionError: Raised when there are network connectivity issues.
        
        Tags:
            get, list, cohorts, data-retrieval, api, important
        """
        url = f"{self.base_url}/api/3/cohorts"
        query_params = {k: v for k, v in [('includeSyncInfo', includeSyncInfo)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_cohorts_request_by_id(self, id, props=None, propKeys=None) -> dict[str, Any]:
        """
        Retrieve the details of a cohort request by its unique identifier.
        
        Args:
            id: str. The unique identifier of the cohort request to retrieve.
            props: Optional[dict]. Additional properties to include in the request. Defaults to None.
            propKeys: Optional[list]. List of property keys to filter the response. Defaults to None.
        
        Returns:
            dict. JSON response containing the cohort request details.
        
        Raises:
            ValueError: Raised if the required 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the API fails.
        
        Tags:
            get, cohort, api, management, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/api/5/cohorts/request/:id"
        query_params = {k: v for k, v in [('props', props), ('propKeys', propKeys), ('propKeys', propKeys)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_cohorts_request_status(self, request_id) -> dict[str, Any]:
        """
        Retrieves the status of a cohort request by request ID.
        
        Args:
            request_id: The unique identifier of the cohort request to check the status for. Must not be None.
        
        Returns:
            A dictionary containing the status information of the specified cohort request.
        
        Raises:
            ValueError: Raised if 'request_id' is None.
            requests.HTTPError: Raised if the HTTP request to the status endpoint fails.
        
        Tags:
            get, cohorts, status, important, management
        """
        if request_id is None:
            raise ValueError("Missing required parameter 'request_id'")
        url = f"{self.base_url}/api/5/cohorts/request-status/:request_id"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_cohorts_request_file(self, requestId) -> Any:
        """
        Retrieves a file for a specific cohorts request based on the provided request ID.
        
        Args:
            requestId: The ID of the cohorts request for which the file is to be retrieved.
        
        Returns:
            A JSON response containing the requested cohorts request file data.
        
        Raises:
            ValueError: Raised when the 'requestId' parameter is missing or None.
        
        Tags:
            fetch, cohorts, file, management, important
        """
        if requestId is None:
            raise ValueError("Missing required parameter 'requestId'")
        url = f"{self.base_url}/api/5/cohorts/request/:requestId/file"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_cohorts_upload(self, request_body=None) -> dict[str, Any]:
        """
        Uploads cohorts to the specified endpoint.
        
        Args:
            request_body: Optional request body to be sent with the POST request, defaults to None.
        
        Returns:
            A JSON response from the API as a dictionary.
        
        Raises:
            requests.RequestException: If there's an issue with the HTTP request, such as a network problem or if the API returns an unsuccessful status code.
        
        Tags:
            upload, cohorts, api_call, important
        """
        url = f"{self.base_url}/api/3/cohorts/upload"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_cohorts_membership(self, request_body=None) -> Any:
        """
        Create or update cohort membership information by sending a POST request to the designated API endpoint.
        
        Args:
            request_body: Optional; data to be sent in the request body as the cohort membership payload.
        
        Returns:
            The response from the API parsed as JSON, typically containing details about the cohort membership operation.
        
        Raises:
            requests.HTTPError: If the server returns a response with an HTTP status code indicating an error.
        
        Tags:
            post, cohorts, membership, api, important
        """
        url = f"{self.base_url}/api/3/cohorts/membership"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_dsar_requests(self, request_body=None) -> dict[str, Any]:
        """
        Submits a new DSAR (Data Subject Access Request) using the provided request body and returns the server's response as a dictionary.
        
        Args:
            request_body: Optional dictionary containing the payload for the DSAR request. Defaults to None.
        
        Returns:
            A dictionary representing the JSON response from the DSAR request API call.
        
        Raises:
            requests.HTTPError: Raised if the HTTP response status indicates an error.
            requests.RequestException: Raised for other request-related errors, such as network issues.
        
        Tags:
            post, dsar, api, management, important
        """
        url = f"{self.base_url}/api/2/dsar/requests"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_dsar_requests_by_id(self, request_id) -> dict[str, Any]:
        """
        Retrieves DSAR requests by a specified ID from the API.
        
        Args:
            request_id: The ID of the DSAR request to fetch.
        
        Returns:
            A dictionary containing the DSAR request data.
        
        Raises:
            ValueError: Raised if the required parameter 'request_id' is missing.
        
        Tags:
            fetch, dsar, api-call, data-retrieval, important
        """
        if request_id is None:
            raise ValueError("Missing required parameter 'request_id'")
        url = f"{self.base_url}/api/2/dsar/requests/:request_id"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_dsar_requests_output(self, request_id, output_id) -> Any:
        """
        Retrieves the output of a specific Data Subject Access Request (DSAR) by request and output ID from the remote API.
        
        Args:
            request_id: The unique identifier of the DSAR request.
            output_id: The unique identifier of the output associated with the DSAR request.
        
        Returns:
            The parsed JSON response containing the DSAR output details.
        
        Raises:
            ValueError: Raised if either 'request_id' or 'output_id' is None.
            requests.HTTPError: Raised if the HTTP request to the remote API fails.
        
        Tags:
            get, dsar, output, api, important
        """
        if request_id is None:
            raise ValueError("Missing required parameter 'request_id'")
        if output_id is None:
            raise ValueError("Missing required parameter 'output_id'")
        url = f"{self.base_url}/api/2/dsar/requests/:request_id/outputs/:output_id"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_annotations(self, app_id=None, date=None, label=None, chart_id=None, details=None) -> dict[str, Any]:
        """
        Sends a POST request to create a new annotation with the specified parameters in the target application.
        
        Args:
            app_id: Optional; The unique identifier of the application to which the annotation is associated.
            date: Optional; The date for the annotation in a supported date format.
            label: Optional; The label or title for the annotation.
            chart_id: Optional; The identifier of the chart related to this annotation.
            details: Optional; Additional details or description for the annotation.
        
        Returns:
            A dictionary containing the server's JSON response with information about the created annotation.
        
        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP POST request fails or if the server returns an error response.
        
        Tags:
            post, annotations, api, http, important
        """
        url = f"{self.base_url}/api/2/annotations"
        query_params = {k: v for k, v in [('app_id', app_id), ('date', date), ('label', label), ('chart_id', chart_id), ('details', details)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_annotations(self, ) -> dict[str, Any]:
        """
        Retrieves all annotation data from the API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing annotation data as returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to the annotations endpoint fails.
            requests.RequestException: If an error occurs while handling the request.
            AttributeError: If the required instance attributes (such as base_url or _get) are missing or misconfigured.
        
        Tags:
            get, annotations, api, data-retrieval, important
        """
        url = f"{self.base_url}/api/2/annotations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_funnels(self, e=None, start=None, end=None, mode=None, n=None, s=None, g=None, cs=None, limit=None) -> dict[str, Any]:
        """
        Retrieves funnel data from the server based on provided filter parameters.
        
        Args:
            e: Optional[str]. The event type or identifier to filter funnels.
            start: Optional[str]. The start date or timestamp for filtering funnel data.
            end: Optional[str]. The end date or timestamp for filtering funnel data.
            mode: Optional[str]. The mode or type of funnel analysis to perform.
            n: Optional[Any]. Additional filter or parameter for funnel selection.
            s: Optional[Any]. Additional filter or parameter for funnel selection.
            g: Optional[Any]. Additional filter or parameter for funnel selection.
            cs: Optional[Any]. Additional filter or parameter for funnel selection.
            limit: Optional[int]. Maximum number of funnel records to return.
        
        Returns:
            dict[str, Any]: A dictionary containing the JSON response with funnel data from the server.
        
        Raises:
            requests.HTTPError: If the HTTP request to the funnel API fails or returns a non-success status code.
        
        Tags:
            get, funnel, analytics, data-retrieval, important
        """
        url = f"{self.base_url}/api/2/funnels"
        query_params = {k: v for k, v in [('e', e), ('start', start), ('end', end), ('mode', mode), ('n', n), ('s', s), ('g', g), ('cs', cs), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_retention(self, se=None, re=None, rm=None, rb=None, start=None, end=None, i=None, s=None, g=None) -> dict[str, Any]:
        """
        Fetches user retention statistics from the API with optional query filters.
        
        Args:
            se: Optional; Filter by session event (type varies by API).
            re: Optional; Filter by retention event (type varies by API).
            rm: Optional; Filter by retention metric (type varies by API).
            rb: Optional; Filter by retention bucket (type varies by API).
            start: Optional; Start date for retention data filtering (type varies by API).
            end: Optional; End date for retention data filtering (type varies by API).
            i: Optional; Additional filter parameter 'i' (type and purpose varies by API).
            s: Optional; Additional filter parameter 's' (type and purpose varies by API).
            g: Optional; Additional filter parameter 'g' (type and purpose varies by API).
        
        Returns:
            A dictionary containing the retention statistics returned from the API.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the retention API fails or an error status is returned.
        
        Tags:
            get, retention, api, filter, important
        """
        url = f"{self.base_url}/api/2/retention"
        query_params = {k: v for k, v in [('se', se), ('re', re), ('rm', rm), ('rb', rb), ('start', start), ('end', end), ('i', i), ('s', s), ('g', g)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_activity(self, user=None, offset=None, limit=None) -> dict[str, Any]:
        """
        Retrieve a user's activity records from the server with optional filtering and pagination.
        
        Args:
            user: Optional; str or None. Username or user identifier to filter activity records. If None, retrieves activity for all users.
            offset: Optional; int or None. Number of records to skip before starting to collect the result set. Used for pagination.
            limit: Optional; int or None. Maximum number of activity records to return.
        
        Returns:
            dict[str, Any]: A dictionary containing the user's activity data and associated metadata as returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to retrieve activity data fails or returns an error response.
            requests.RequestException: For other network-related errors during the API request.
        
        Tags:
            get, user-activity, api, sync, important
        """
        url = f"{self.base_url}/api/2/useractivity"
        query_params = {k: v for k, v in [('user', user), ('offset', offset), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_composition(self, start=None, end=None, p=None) -> dict[str, Any]:
        """
        Retrieve composition data from the API within an optional time range and/or filter.
        
        Args:
            start: Optional; The start time for filtering results (format and type depend on API).
            end: Optional; The end time for filtering results (format and type depend on API).
            p: Optional; An additional filter parameter (meaning depends on API context).
        
        Returns:
            A dictionary representing the parsed JSON response from the composition API endpoint.
        
        Raises:
            requests.HTTPError: If the API request fails or returns a non-success HTTP status code.
        
        Tags:
            get, composition, api, data-retrieval
        """
        url = f"{self.base_url}/api/2/composition"
        query_params = {k: v for k, v in [('start', start), ('end', end), ('p', p)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users(self, start=None, end=None, m=None, i=None, s=None, g=None) -> dict[str, Any]:
        """
        Retrieves a list of users from the API, filtered by optional query parameters.
        
        Args:
            start: Optional; filter users created or updated after this value.
            end: Optional; filter users created or updated before this value.
            m: Optional; filter users by the specified 'm' parameter.
            i: Optional; filter users by the specified 'i' parameter.
            s: Optional; filter users by the specified 's' parameter.
            g: Optional; filter users by the specified 'g' parameter.
        
        Returns:
            A dictionary containing the user data returned by the API, typically including user details and metadata.
        
        Raises:
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.
        
        Tags:
            get, list, users, api, important
        """
        url = f"{self.base_url}/api/2/users"
        query_params = {k: v for k, v in [('start', start), ('end', end), ('m', m), ('i', i), ('s', s), ('g', g)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sessions_length(self, start=None, end=None, timeHistogramConfigBinTimeUnit=None, timeHistogramConfigBinMin=None, timeHistogramConfigBinMax=None, timeHistogramConfigBinSize=None) -> dict[str, Any]:
        """
        Retrieves session length data with optional time filtering and histogram configuration.
        
        Args:
            start: Start timestamp for filtering sessions data.
            end: End timestamp for filtering sessions data.
            timeHistogramConfigBinTimeUnit: Time unit for histogram bins (e.g., 'minute', 'hour', 'day').
            timeHistogramConfigBinMin: Minimum value for histogram bins.
            timeHistogramConfigBinMax: Maximum value for histogram bins.
            timeHistogramConfigBinSize: Size of each histogram bin.
        
        Returns:
            Dictionary containing session length data and histogram information.
        
        Raises:
            HTTPError: Raised when the API request fails or returns an error status code.
        
        Tags:
            retrieve, sessions, analytics, histogram, data, important
        """
        url = f"{self.base_url}/api/2/sessions/length"
        query_params = {k: v for k, v in [('start', start), ('end', end), ('timeHistogramConfigBinTimeUnit', timeHistogramConfigBinTimeUnit), ('timeHistogramConfigBinMin', timeHistogramConfigBinMin), ('timeHistogramConfigBinMax', timeHistogramConfigBinMax), ('timeHistogramConfigBinSize', timeHistogramConfigBinSize)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sessions_per_user(self, start=None, end=None) -> dict[str, Any]:
        """
        Retrieves the number of sessions per user within an optional time range.
        
        Args:
            start: Optional start datetime or string (default: None). Filters sessions to those occurring after this time.
            end: Optional end datetime or string (default: None). Filters sessions to those occurring before this time.
        
        Returns:
            A dictionary mapping user identifiers to their session counts and related session data.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the sessions API endpoint returns an unsuccessful status code.
        
        Tags:
            get, sessions, per-user, api, batch, management, important
        """
        url = f"{self.base_url}/api/2/sessions/peruser"
        query_params = {k: v for k, v in [('start', start), ('end', end)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sessions_average(self, start=None, end=None) -> dict[str, Any]:
        """
        Retrieve the average session metrics within an optional start and end date range.
        
        Args:
            start: Optional start date (str or date) to filter the session data. If None, no lower bound is applied.
            end: Optional end date (str or date) to filter the session data. If None, no upper bound is applied.
        
        Returns:
            Dictionary containing average session metrics data as returned by the API.
        
        Raises:
            requests.HTTPError: If the API request fails or returns a non-success HTTP status code.
        
        Tags:
            get, session-metrics, api, statistics, important
        """
        url = f"{self.base_url}/api/2/sessions/average"
        query_params = {k: v for k, v in [('start', start), ('end', end)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_search(self, user=None) -> dict[str, Any]:
        """
        Fetches user search data from the server based on an optional user identifier.
        
        Args:
            user: Optional; The identifier of the user to filter search results. If None, returns all user searches.
        
        Returns:
            A dictionary containing the user search data retrieved from the server.
        
        Raises:
            requests.HTTPError: If the HTTP request fails or the server returns an error response.
        
        Tags:
            get, user-search, api, important
        """
        url = f"{self.base_url}/api/2/usersearch"
        query_params = {k: v for k, v in [('user', user)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_segmentation(self, e=None, start=None, end=None, i=None, m=None, n=None, s=None, g=None, limit=None, formula=None, rollingWindow=None, rollingAverage=None) -> Any:
        """
        Retrieve segmentation data from the API based on provided filter parameters.
        
        Args:
            e: Optional[str]. Filter parameter for segmentation criteria.
            start: Optional[str|int]. Start value for the range filter, typically a date or timestamp.
            end: Optional[str|int]. End value for the range filter, typically a date or timestamp.
            i: Optional[str|int]. Additional filter parameter for segmentation.
            m: Optional[str|int]. Additional filter parameter for segmentation.
            n: Optional[str|int]. Additional filter parameter for segmentation.
            s: Optional[str|int]. Additional filter parameter for segmentation.
            g: Optional[str|int]. Additional filter parameter for segmentation.
            limit: Optional[int]. Maximum number of results to return.
            formula: Optional[str]. Formula to apply to the segmentation query.
            rollingWindow: Optional[int]. Size of the rolling window for aggregation, if applicable.
            rollingAverage: Optional[bool|int]. Whether to compute a rolling average, or window size for averaging.
        
        Returns:
            dict: Parsed JSON response containing the segmentation data from the API.
        
        Raises:
            requests.HTTPError: If the HTTP request fails or the API returns a non-success status code.
        
        Tags:
            get, segmentation, api, fetch, data-retrieval, important
        """
        url = f"{self.base_url}/api/2/segmentation"
        query_params = {k: v for k, v in [('e', e), ('start', start), ('end', end), ('i', i), ('m', m), ('n', n), ('s', s), ('g', g), ('limit', limit), ('formula', formula), ('rollingWindow', rollingWindow), ('rollingAverage', rollingAverage)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_events_list(self, ) -> dict[str, Any]:
        """
        Retrieves a list of events from the remote API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing the JSON response with the list of events.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the events API fails or returns an unsuccessful status code.
        
        Tags:
            get, events, list, api, important
        """
        url = f"{self.base_url}/api/2/events/list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_chart_query(self, chart_id) -> dict[str, Any]:
        """
        Retrieves the query details for a specific chart by its ID from the API.
        
        Args:
            chart_id: str. The unique identifier of the chart whose query details are to be retrieved.
        
        Returns:
            dict[str, Any]: A dictionary containing the query details of the specified chart as returned by the API.
        
        Raises:
            ValueError: Raised if the 'chart_id' parameter is None.
            requests.HTTPError: Raised if the HTTP response contains an unsuccessful status code.
        
        Tags:
            get, chart, query, api, important
        """
        if chart_id is None:
            raise ValueError("Missing required parameter 'chart_id'")
        url = f"{self.base_url}/api/3/chart/:chart_id/query"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_base(self, ) -> dict[str, Any]:
        """
        Retrieves the base resource information from the API and returns it as a dictionary.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing the parsed JSON response from the API's base endpoint.
        
        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
            requests.exceptions.RequestException: If a network-related error occurs during the request.
        
        Tags:
            get, base, sync, api, important
        """
        url = f"{self.base_url}/"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_revenue_ltv(self, start=None, end=None, m=None, i=None, s=None, g=None) -> dict[str, Any]:
        """
        Retrieves lifetime value (LTV) revenue data for a specified period and set of filtering parameters.
        
        Args:
            start: Optional; The start date for the LTV data query in a supported date format.
            end: Optional; The end date for the LTV data query in a supported date format.
            m: Optional; Filter for a specific metric or group, as required by the revenue API.
            i: Optional; Filter parameter, such as an internal identifier or dimension.
            s: Optional; Filter parameter, such as a segment or status value.
            g: Optional; Filter parameter, such as a grouping or granularity value.
        
        Returns:
            A dictionary containing the LTV revenue data matching the given filters, as returned by the API.
        
        Raises:
            requests.HTTPError: If the underlying HTTP request to the LTV API endpoint fails or returns a non-success status code.
        
        Tags:
            get, revenue, ltv, api, important
        """
        url = f"{self.base_url}/api/2/revenue/ltv"
        query_params = {k: v for k, v in [('start', start), ('end', end), ('m', m), ('i', i), ('s', s), ('g', g)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_event_streaming_delivery_metrics_summary(self, sync_id=None, time_period=None, start=None, end=None) -> Any:
        """
        Retrieves a summary of event streaming delivery metrics for the specified sync and time period.
        
        Args:
            sync_id: Optional; The identifier of the sync job to filter metrics by. If None, metrics for all syncs are included.
            time_period: Optional; A predefined time period (such as 'last_7_days' or 'this_month') to filter the metrics. Mutually exclusive with 'start' and 'end'.
            start: Optional; The start timestamp (ISO 8601 or compatible string) for filtering metrics. Should be used with 'end'. Ignored if 'time_period' is provided.
            end: Optional; The end timestamp (ISO 8601 or compatible string) for filtering metrics. Should be used with 'start'. Ignored if 'time_period' is provided.
        
        Returns:
            A JSON-compatible object containing the summary of delivery metrics for the requested event streaming sync and time range.
        
        Raises:
            requests.HTTPError: If the HTTP request to the delivery metrics summary endpoint fails (e.g., network error or non-2xx status code).
        
        Tags:
            get, metrics, event-streaming, summary, important
        """
        url = f"{self.base_url}/api/2/event-streaming/delivery-metrics-summary"
        query_params = {k: v for k, v in [('sync_id', sync_id), ('time_period', time_period), ('start', start), ('end', end)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_export(self, start=None, end=None) -> Any:
        """
        Retrieves export data from the API within an optional date range.
        
        Args:
            start: Optional start datetime or timestamp to filter the export data. If None, no lower bound is applied.
            end: Optional end datetime or timestamp to filter the export data. If None, no upper bound is applied.
        
        Returns:
            Deserialized JSON object containing the export data from the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API export endpoint fails or returns an error status code.
        
        Tags:
            get, export, api, data-retrieval, important
        """
        url = f"{self.base_url}/api/2/export"
        query_params = {k: v for k, v in [('start', start), ('end', end)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_group_identify(self, api_key=None, identification=None, request_body=None) -> Any:
        """
        Sends a POST request to the group identification API endpoint with optional authentication and identification parameters.
        
        Args:
            api_key: Optional API key string for authenticating the request. If not provided, authentication may rely on environment or configuration.
            identification: Optional identifier or group information used to specify which group is being identified.
            request_body: Optional request payload to be sent in the POST body. Can be any serializable object required by the API.
        
        Returns:
            A dictionary containing the parsed JSON response from the group identification endpoint.
        
        Raises:
            AuthenticationError: Raised if the required API key is missing or invalid.
            HTTPError: Raised if the HTTP response returns an unsuccessful status code.
            RequestException: Raised for other errors encountered during the POST request, such as network issues.
        
        Tags:
            post, group-identify, api, async-job, important
        """
        url = f"{self.base_url}/groupidentify"
        query_params = {k: v for k, v in [('api_key', api_key), ('identification', identification)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_2_http_api(self, request_body=None) -> dict[str, Any]:
        """
        Sends a POST request to the /2/httpapi endpoint and returns the parsed JSON response.
        
        Args:
            request_body: Optional request payload to include in the HTTP POST request as the body. Defaults to None.
        
        Returns:
            A dictionary representing the parsed JSON response from the API.
        
        Raises:
            requests.HTTPError: If the HTTP request fails or returns a non-successful status code.
            AuthenticationError: If authentication credentials (such as an API key) are missing or invalid.
        
        Tags:
            post, http, api, request, important
        """
        url = f"{self.base_url}/2/httpapi"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_identify(self, request_body=None) -> Any:
        """
        Sends a POST request to the '/identify' endpoint with the given request body and returns the parsed JSON response.
        
        Args:
            request_body: Optional request body data to include in the POST request. Defaults to None.
        
        Returns:
            The parsed JSON response from the '/identify' endpoint as a Python object.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the '/identify' endpoint fails.
            requests.RequestException: Raised for other types of network-related errors.
            AuthenticationError: Raised if authentication credentials, such as API keys, are missing or invalid.
        
        Tags:
            post, identify, api-call, network, important
        """
        url = f"{self.base_url}/identify"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_identify(self, api_key=None, identification=None) -> dict[str, Any]:
        """
        Retrieve identification information from the API using the provided credentials.
        
        Args:
            api_key: Optional API key for authentication. If not provided, the default API key will be used.
            identification: Optional identification token or ID to retrieve specific identification information.
        
        Returns:
            A dictionary containing the identification information returned by the API.
        
        Raises:
            HTTPError: Raised when the HTTP request fails or returns an error status code.
        
        Tags:
            identify, authentication, get, api, important
        """
        url = f"{self.base_url}/identify"
        query_params = {k: v for k, v in [('api_key', api_key), ('identification', identification)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_lookup_table(self, ) -> dict[str, Any]:
        """
        Retrieves a lookup table from the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing the lookup table data from the API response.
        
        Raises:
            HTTPError: Raised when the API request fails, such as due to authentication issues, server errors, or invalid requests.
        
        Tags:
            get, retrieve, lookup, api, data
        """
        url = f"{self.base_url}/api/2/lookup_table"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_lookup_table_name(self, name) -> dict[str, Any]:
        """
        Retrieves the details of a lookup table by its name from the remote API.
        
        Args:
            name: str. The name of the lookup table to fetch.
        
        Returns:
            dict[str, Any]: The JSON response containing the lookup table details.
        
        Raises:
            ValueError: If the 'name' parameter is None.
            requests.HTTPError: If the underlying HTTP request fails or returns an error status.
        
        Tags:
            get, lookup-table, api, fetch, important
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        url = f"{self.base_url}/api/2/lookup_table/:name"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_lookup_table_name(self, name, file=None) -> dict[str, Any]:
        """
        Posts a new lookup table with the specified name and optional file data, returning the API response as a dictionary.
        
        Args:
            name: str. The name of the lookup table to be created. Must not be None.
            file: Any, optional. The file data to associate with the lookup table. Defaults to None.
        
        Returns:
            dict[str, Any]: The JSON response from the API containing information about the created lookup table.
        
        Raises:
            ValueError: Raised if the 'name' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the API fails (non-success status code).
        
        Tags:
            post, lookup-table, api, management, important
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'file': file,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/2/lookup_table/:name"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def patch_lookup_table_name(self, name, file=None) -> dict[str, Any]:
        """
        Updates the name of a lookup table by sending a PATCH request with the specified parameters.
        
        Args:
            name: str. The identifier or name of the lookup table to update. Must not be None.
            file: Optional. The file or file-like object to include in the PATCH request. Defaults to None.
        
        Returns:
            dict. The response from the PATCH request parsed as a JSON dictionary.
        
        Raises:
            ValueError: Raised if the required 'name' parameter is None.
            HTTPError: Raised if the server responds with an error status code during the PATCH request.
        
        Tags:
            patch, update, async-job, management, important
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'file': file,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/2/lookup_table/:name"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_lookup_table_name(self, name) -> dict[str, Any]:
        """
        Deletes a lookup table resource by its name from the remote API.
        
        Args:
            name: str. The name of the lookup table to be deleted.
        
        Returns:
            dict[str, Any]: The parsed JSON response from the API after deletion.
        
        Raises:
            ValueError: Raised if the 'name' parameter is None.
            requests.HTTPError: Raised if the HTTP request to delete the lookup table fails.
        
        Tags:
            delete, lookup-table, api, important
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        url = f"{self.base_url}/api/2/lookup_table/:name"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_release(self, request_body=None) -> dict[str, Any]:
        """
        Sends a POST request to the release endpoint and returns the response data as a dictionary.
        
        Args:
            request_body: Optional; the request payload to include in the POST request. Should be a dictionary or compatible data structure. Defaults to None.
        
        Returns:
            A dictionary containing the parsed JSON response from the release endpoint.
        
        Raises:
            requests.HTTPError: If the POST request fails and a non-success status code is returned.
            requests.RequestException: For network-related errors during the POST request.
        
        Tags:
            post, release, api, network, important
        """
        url = f"{self.base_url}/api/2/release"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_scim_1_users(self, start_index=None, items_per_page=None, filter=None) -> Any:
        """
        Retrieves SCIM 1 users based on specified query parameters.
        
        Args:
            start_index: The index from which to start retrieving users.
            items_per_page: The number of users to retrieve per page.
            filter: A filter to apply to the user query.
        
        Returns:
            A JSON response containing the SCIM 1 users.
        
        Raises:
            requests.exceptions.HTTPError: Raised if an HTTP error occurs during the request, such as a non-200 status code.
        
        Tags:
            scim, users, query, important
        """
        url = f"{self.base_url}/scim/1/Users"
        query_params = {k: v for k, v in [('start_index', start_index), ('items_per_page', items_per_page), ('filter', filter)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_scim_1_users_id(self, id) -> dict[str, Any]:
        """
        Retrieves a SCIM user resource by user ID from the SCIM 1.0 API endpoint.
        
        Args:
            id: str. The unique identifier of the user to retrieve.
        
        Returns:
            dict[str, Any]: The SCIM user resource as a JSON-decoded dictionary.
        
        Raises:
            ValueError: If the 'id' parameter is None.
            requests.HTTPError: If the HTTP request to the SCIM endpoint fails with an unsuccessful status code.
        
        Tags:
            get, scim, user, api, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Users/:id"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_scim_1_users_id(self, id, request_body=None) -> dict[str, Any]:
        """
        Updates a SCIM user resource with the specified ID using the provided request body.
        
        Args:
            id: str. The unique identifier of the SCIM user to update.
            request_body: dict or None. Optional. The request payload containing updated user attributes.
        
        Returns:
            dict. The JSON response from the SCIM API after updating the user resource.
        
        Raises:
            ValueError: Raised when the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the SCIM API fails with a non-success status code.
        
        Tags:
            update, scim, user-management, put, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Users/:id"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def patch_scim_1_users_id(self, id, request_body=None) -> dict[str, Any]:
        """
        Partially updates a SCIM user resource identified by user ID using a PATCH request.
        
        Args:
            id: str. The unique identifier of the SCIM user to update.
            request_body: dict or None. The data to be sent in the PATCH request body. If None, no data is sent.
        
        Returns:
            dict. The JSON-decoded response from the SCIM server representing the updated user resource.
        
        Raises:
            ValueError: Raised if the required parameter 'id' is not provided.
            HTTPError: Raised if the HTTP response status code indicates an error.
        
        Tags:
            patch, scim, users, update, management, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Users/:id"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_scim_1_users_id(self, id) -> dict[str, Any]:
        """
        Deletes a SCIM user with the specified ID from the system.
        
        Args:
            id: str. The unique identifier of the SCIM user to be deleted.
        
        Returns:
            dict[str, Any]: The JSON response from the server indicating the result of the delete operation.
        
        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP response contains an unsuccessful status code.
        
        Tags:
            delete, scim, user-management, api, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Users/:id"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_scim_1_users(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new SCIM user by sending a POST request to the SCIM 1.0 Users endpoint.
        
        Args:
            request_body: Dictionary containing the user data to be created. This should follow the SCIM 1.0 user schema specification.
        
        Returns:
            Dictionary containing the JSON response from the server, typically including the created user's details and metadata.
        
        Raises:
            HTTPError: Raised when the HTTP request returns an unsuccessful status code.
            JSONDecodeError: Raised when the response cannot be parsed as JSON.
        
        Tags:
            create, user, scim, post, identity, management, important
        """
        url = f"{self.base_url}/scim/1/Users/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_scim_1_groups(self, ) -> dict[str, Any]:
        """
        Fetches SCIM 1 groups from the Anthropic API.
        
        Args:
            None: This function takes no arguments.
        
        Returns:
            A dictionary containing the SCIM 1 groups data.
        
        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            scim, groups, api-call, important
        """
        url = f"{self.base_url}/scim/1/Groups"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_scim_1_groups(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new SCIM group by sending a POST request to the /scim/1/Groups endpoint.
        
        Args:
            request_body: Optional request payload as a dictionary containing the group details to be created. Defaults to None.
        
        Returns:
            A dictionary representing the JSON response from the server, containing details of the created group.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the SCIM endpoint fails or returns an error status code.
        
        Tags:
            post, scim, group-management, api, important
        """
        url = f"{self.base_url}/scim/1/Groups"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_scim_1_groups_id(self, id) -> dict[str, Any]:
        """
        Retrieves details of a SCIM 1 group by its unique identifier.
        
        Args:
            id: str. The unique identifier of the SCIM 1 group to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing details of the requested SCIM 1 group as returned by the API.
        
        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the SCIM API fails or returns an error status code.
        
        Tags:
            retrieve, scim, group, get, api, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Groups/:id"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def patch_scim_1_groups_id(self, id, request_body=None) -> dict[str, Any]:
        """
        Partially updates a SCIM group resource by its ID using a PATCH request.
        
        Args:
            id: The unique identifier of the SCIM group to update.
            request_body: An optional dictionary containing the fields to update for the group. Defaults to None.
        
        Returns:
            A dictionary representing the updated SCIM group resource as returned by the server.
        
        Raises:
            ValueError: Raised if the 'id' parameter is not provided.
            requests.HTTPError: Raised if the HTTP request fails (e.g., the server returns an error status code).
        
        Tags:
            patch, scim, group-management, api, update, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Groups/:id"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_scim_1_groups_id(self, id) -> dict[str, Any]:
        """
        Deletes a SCIM group resource with the specified ID.
        
        Args:
            id: str. The unique identifier of the SCIM group to delete.
        
        Returns:
            dict[str, Any]: JSON response from the API after attempting to delete the group.
        
        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to delete the group fails.
        
        Tags:
            delete, scim, group-management, api, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/scim/1/Groups/:id"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_taxonomy_category(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new taxonomy category by sending a POST request to the taxonomy API.
        
        Args:
            request_body: Optional request payload as a dictionary containing the data for the category to be created. Defaults to None.
        
        Returns:
            A dictionary containing the response data from the API after creating the taxonomy category.
        
        Raises:
            requests.HTTPError: If the API response contains an unsuccessful HTTP status code.
        
        Tags:
            post, taxonomy, category, api, important
        """
        url = f"{self.base_url}/api/2/taxonomy/category"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_category(self, ) -> dict[str, Any]:
        """
        Retrieves the taxonomy category from the API.
        
        Args:
            None: This function takes no arguments.
        
        Returns:
            A dictionary containing the taxonomy category data.
        
        Raises:
            requests.HTTPError: Raised if an HTTP error occurs during the request.
        
        Tags:
            fetch, taxonomy, api-call, important, taxonomy-management
        """
        url = f"{self.base_url}/api/2/taxonomy/category"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_category_category_name(self, category_name) -> dict[str, Any]:
        """
        Retrieves taxonomy category details for a given category name from the API.
        
        Args:
            category_name: str. The name of the taxonomy category to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing the taxonomy category details returned by the API.
        
        Raises:
            ValueError: Raised if 'category_name' is None.
            requests.HTTPError: Raised if the API request fails (non-success HTTP status code).
        
        Tags:
            get, taxonomy, category, api, important
        """
        if category_name is None:
            raise ValueError("Missing required parameter 'category_name'")
        url = f"{self.base_url}/api/2/taxonomy/category/:category_name"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_taxonomy_category_category_id(self, category_id, request_body=None) -> dict[str, Any]:
        """
        Updates a taxonomy category specified by its category_id.
        
        Args:
            category_id: The ID of the taxonomy category to update.
            request_body: Optional body of data to be sent with the update request.
        
        Returns:
            A dictionary containing the response data from the API.
        
        Raises:
            ValueError: Raised if the category_id parameter is missing.
        
        Tags:
            update, taxonomy, api-call, important
        """
        if category_id is None:
            raise ValueError("Missing required parameter 'category_id'")
        url = f"{self.base_url}/api/2/taxonomy/category/:category_id"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_taxonomy_category_category_id(self, category_id) -> dict[str, Any]:
        """
        Deletes a taxonomy category by its unique category ID.
        
        Args:
            category_id: str. The unique identifier of the taxonomy category to delete.
        
        Returns:
            dict[str, Any]: The API response parsed as a dictionary containing the result of the delete operation.
        
        Raises:
            ValueError: If 'category_id' is None.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.
        
        Tags:
            delete, taxonomy, category, management, important
        """
        if category_id is None:
            raise ValueError("Missing required parameter 'category_id'")
        url = f"{self.base_url}/api/2/taxonomy/category/:category_id"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_taxonomy_event(self, request_body=None) -> dict[str, Any]:
        """
        Posts a taxonomy event to the server and returns the JSON response.
        
        Args:
            request_body: Optional dictionary containing the payload data to be sent in the POST request.
        
        Returns:
            A dictionary representing the parsed JSON response from the server.
        
        Raises:
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.
        
        Tags:
            post, taxonomy, event, api, important
        """
        url = f"{self.base_url}/api/2/taxonomy/event"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_event(self, ) -> dict[str, Any]:
        """
        Retrieves taxonomy event data from the API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing taxonomy event data from the API response.
        
        Raises:
            HTTPError: Raised when the HTTP request fails, such as with 4xx or 5xx status codes.
        
        Tags:
            get, retrieve, taxonomy, event, api, data
        """
        url = f"{self.base_url}/api/2/taxonomy/event"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_event_event_type(self, event_type) -> dict[str, Any]:
        """
        Retrieves taxonomy details for a specific event type from the API.
        
        Args:
            event_type: The event type identifier to query for taxonomy information.
        
        Returns:
            A dictionary containing the taxonomy details for the specified event type.
        
        Raises:
            ValueError: Raised when the 'event_type' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the API returns an unsuccessful status code.
        
        Tags:
            get, taxonomy, event-type, api-call, important
        """
        if event_type is None:
            raise ValueError("Missing required parameter 'event_type'")
        url = f"{self.base_url}/api/2/taxonomy/event/:event_type"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_taxonomy_event_event_type(self, event_type, request_body=None) -> dict[str, Any]:
        """
        Updates the event type in the taxonomy system by sending a PUT request with the provided request body.
        
        Args:
            event_type: str. The type of event to update in the taxonomy. Must not be None.
            request_body: Optional[dict]. The request body data to be sent in the PUT request. Defaults to None.
        
        Returns:
            dict. The JSON-decoded response from the API after updating the event type.
        
        Raises:
            ValueError: If the required parameter 'event_type' is None.
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.
        
        Tags:
            put, taxonomy, event, update, api, important
        """
        if event_type is None:
            raise ValueError("Missing required parameter 'event_type'")
        url = f"{self.base_url}/api/2/taxonomy/event/:event_type"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_taxonomy_event_event_type(self, event_type) -> dict[str, Any]:
        """
        Deletes a taxonomy event identified by the given event type.
        
        Args:
            event_type: The identifier for the taxonomy event type to delete.
        
        Returns:
            A dictionary containing the server's response to the delete operation.
        
        Raises:
            ValueError: Raised if 'event_type' is None.
            requests.HTTPError: Raised if the HTTP request to delete the event fails.
        
        Tags:
            delete, taxonomy, event, management, important
        """
        if event_type is None:
            raise ValueError("Missing required parameter 'event_type'")
        url = f"{self.base_url}/api/2/taxonomy/event/:event_type"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_taxonomy_event_property(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new taxonomy event property using the API.
        
        Args:
            request_body: Optional dictionary containing the event property details to be created. If None, creates an empty event property.
        
        Returns:
            Dictionary containing the created taxonomy event property data and metadata from the API response.
        
        Raises:
            HTTPError: Raised when the API request fails due to client or server errors (4xx or 5xx responses).
        
        Tags:
            create, post, taxonomy, event-property, api, important
        """
        url = f"{self.base_url}/api/2/taxonomy/event-property"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_event_property(self, event_property=None) -> dict[str, Any]:
        """
        Retrieves taxonomy event property data from the remote API endpoint.
        
        Args:
            event_property: Optional[str]. The name of the event property to filter the results by. If None, retrieves all event properties.
        
        Returns:
            dict[str, Any]: A dictionary containing the event property data returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.
        
        Tags:
            get, taxonomy, event-property, api, important
        """
        url = f"{self.base_url}/api/2/taxonomy/event-property"
        query_params = {k: v for k, v in [('event_property', event_property)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_taxonomy_user_property(self, request_body=None) -> dict[str, Any]:
        """
        Creates or updates a user property in the taxonomy via a POST request to the API.
        
        Args:
            request_body: Optional dictionary containing the user property data to be sent in the request body.
        
        Returns:
            Dictionary containing the JSON response from the API.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.
        
        Tags:
            post, taxonomy, user-property, api, important
        """
        url = f"{self.base_url}/api/2/taxonomy/user-property"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_user_property(self, ) -> dict[str, Any]:
        """
        Retrieves the user property taxonomy from the backend API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing the taxonomy user property data as returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.
        
        Tags:
            get, taxonomy, user-property, api, important
        """
        url = f"{self.base_url}/api/2/taxonomy/user-property"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_taxonomy_user_property_user_property(self, user_property) -> dict[str, Any]:
        """
        Retrieves information about a user property from the taxonomy service.
        
        Args:
            user_property: The identifier of the user property to retrieve.
        
        Returns:
            A dictionary containing the details of the requested user property.
        
        Raises:
            ValueError: Raised if 'user_property' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails.
        
        Tags:
            get, user-property, taxonomy, api, important
        """
        if user_property is None:
            raise ValueError("Missing required parameter 'user_property'")
        url = f"{self.base_url}/api/2/taxonomy/user-property/:user_property"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_taxonomy_user_property_user_property(self, user_property, request_body=None) -> dict[str, Any]:
        """
        Updates a user property in the taxonomy using the specified user property identifier and optional request body.
        
        Args:
            user_property: str. The identifier of the user property to update. Must not be None.
            request_body: dict or None. Optional data to include in the update request body. Defaults to None.
        
        Returns:
            dict. The server's JSON response containing details of the updated user property.
        
        Raises:
            ValueError: Raised if 'user_property' is None.
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            put, user-property, taxonomy, update, api, important
        """
        if user_property is None:
            raise ValueError("Missing required parameter 'user_property'")
        url = f"{self.base_url}/api/2/taxonomy/user-property/:user_property"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_taxonomy_user_property_user_property(self, user_property) -> dict[str, Any]:
        """
        Deletes a user property from the taxonomy via the API.
        
        Args:
            user_property: str. The identifier of the user property to delete.
        
        Returns:
            dict[str, Any]: The server's JSON response after deleting the user property.
        
        Raises:
            ValueError: Raised if 'user_property' is None.
            requests.HTTPError: Raised if the API response returns an unsuccessful status code.
        
        Tags:
            delete, taxonomy, user-property, api, management, important
        """
        if user_property is None:
            raise ValueError("Missing required parameter 'user_property'")
        url = f"{self.base_url}/api/2/taxonomy/user-property/:user_property"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_user_map(self, mapping=None, api_key=None) -> Any:
        """
        Posts a user map to the specified endpoint, optionally including a mapping and API key.
        
        Args:
            mapping: Optional mapping data to be included in the request.
            api_key: Optional Anthropic API key for authentication.
        
        Returns:
            The JSON response from the API call.
        
        Raises:
            requests.exceptions.HTTPError: Raised when the API call results in an HTTP error.
        
        Tags:
            post, map, api, important
        """
        url = f"{self.base_url}/usermap"
        query_params = {k: v for k, v in [('mapping', mapping), ('api_key', api_key)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_api_2_deletions_users(self, request_body=None) -> Any:
        """
        Submits a user deletion request to the API and returns the server's JSON response.
        
        Args:
            request_body: The request payload to be sent in the deletion request. Defaults to None.
        
        Returns:
            The JSON-decoded response from the server as returned by the deletion API endpoint.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the server fails or an invalid response is received.
        
        Tags:
            delete, users, api, post, important
        """
        url = f"{self.base_url}/api/2/deletions/users"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_api_2_deletions_users(self, start_day=None, end_day=None) -> Any:
        """
        Retrieves user deletion information between a specified date range via the API endpoint '/api/2/deletions/users'.
        
        Args:
            start_day: The beginning date for the user deletion query (optional).
            end_day: The ending date for the user deletion query (optional).
        
        Returns:
            A JSON object containing user deletion data for the specified date range.
        
        Raises:
            HTTPError: Raised when the HTTP request to the API endpoint fails.
        
        Tags:
            get, retrieve, deletion, users, data-retrieval, api
        """
        url = f"{self.base_url}/api/2/deletions/users"
        query_params = {k: v for k, v in [('start_day', start_day), ('end_day', end_day)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_api_2_deletions_users_amplitude_id_or_user_id_date(self, amplitude_id_or_user_id, date) -> Any:
        """
        Deletes user data from API 2 deletions endpoint using either Amplitude ID or user ID and a specific date.
        
        Args:
            amplitude_id_or_user_id: The Amplitude ID or user ID of the user whose data is to be deleted.
            date: The date associated with the deletion.
        
        Returns:
            The response from the API as JSON.
        
        Raises:
            ValueError: Raised if either 'amplitude_id_or_user_id' or 'date' is missing.
            requests.exceptions.HTTPError: Raised if the HTTP request returns a bad status code.
        
        Tags:
            delete, api-call, management, important
        """
        if amplitude_id_or_user_id is None:
            raise ValueError("Missing required parameter 'amplitude_id_or_user_id'")
        if date is None:
            raise ValueError("Missing required parameter 'date'")
        url = f"{self.base_url}/api/2/deletions/users/:amplitude_id_or_user_id/:date"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_user_profile(self, user_id=None, get_recs=None, rec_id=None) -> dict[str, Any]:
        """
        Retrieves a user profile from the v1 API endpoint, optionally including recommendations or a specific recommendation ID.
        
        Args:
            user_id: Optional[str]. The unique identifier of the user whose profile is to be fetched.
            get_recs: Optional[bool]. If True, include user recommendations in the response.
            rec_id: Optional[str]. The unique identifier of a specific recommendation to include in the response.
        
        Returns:
            dict[str, Any]: The JSON response from the API containing the user's profile data. May include recommendations if requested.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.
            requests.RequestException: For network-related errors or issues during the HTTP request.
        
        Tags:
            get, user-profile, api, important
        """
        url = f"{self.base_url}/v1/userprofile"
        query_params = {k: v for k, v in [('user_id', user_id), ('get_recs', get_recs), ('rec_id', rec_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.post_attribution,
            self.post_batch,
            self.get_cohorts,
            self.get_cohorts_request_by_id,
            self.get_cohorts_request_status,
            self.get_cohorts_request_file,
            self.post_cohorts_upload,
            self.post_cohorts_membership,
            self.post_dsar_requests,
            self.get_dsar_requests_by_id,
            self.get_dsar_requests_output,
            self.post_annotations,
            self.get_annotations,
            self.get_funnels,
            self.get_retention,
            self.get_user_activity,
            self.get_composition,
            self.get_users,
            self.get_sessions_length,
            self.get_sessions_per_user,
            self.get_sessions_average,
            self.get_user_search,
            self.get_segmentation,
            self.get_events_list,
            self.get_chart_query,
            self.get_base,
            self.get_revenue_ltv,
            self.get_event_streaming_delivery_metrics_summary,
            self.get_export,
            self.post_group_identify,
            self.post_2_http_api,
            self.post_identify,
            self.get_identify,
            self.get_lookup_table,
            self.get_lookup_table_name,
            self.post_lookup_table_name,
            self.patch_lookup_table_name,
            self.delete_lookup_table_name,
            self.post_release,
            self.get_scim_1_users,
            self.get_scim_1_users_id,
            self.put_scim_1_users_id,
            self.patch_scim_1_users_id,
            self.delete_scim_1_users_id,
            self.post_scim_1_users,
            self.get_scim_1_groups,
            self.post_scim_1_groups,
            self.get_scim_1_groups_id,
            self.patch_scim_1_groups_id,
            self.delete_scim_1_groups_id,
            self.post_taxonomy_category,
            self.get_taxonomy_category,
            self.get_taxonomy_category_category_name,
            self.put_taxonomy_category_category_id,
            self.delete_taxonomy_category_category_id,
            self.post_taxonomy_event,
            self.get_taxonomy_event,
            self.get_taxonomy_event_event_type,
            self.put_taxonomy_event_event_type,
            self.delete_taxonomy_event_event_type,
            self.post_taxonomy_event_property,
            self.get_taxonomy_event_property,
            self.post_taxonomy_user_property,
            self.get_taxonomy_user_property,
            self.get_taxonomy_user_property_user_property,
            self.put_taxonomy_user_property_user_property,
            self.delete_taxonomy_user_property_user_property,
            self.post_user_map,
            self.post_api_2_deletions_users,
            self.get_api_2_deletions_users,
            self.delete_api_2_deletions_users_amplitude_id_or_user_id_date,
            self.get_v1_user_profile
        ]

