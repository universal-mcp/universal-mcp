from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class NotionApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="notion", integration=integration, **kwargs)
        self.base_url = "https://api.notion.com"

    def _get_headers(self):
        if not self.integration:
            raise ValueError("Integration not configured for NotionApp")
        credentials = self.integration.get_credentials()
        if "headers" in credentials:
            return credentials["headers"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def retrieve_a_user(self, id, request_body=None) -> dict[str, Any]:
        """
        Retrieves a user's details from the server using their unique identifier.

        Args:
            id: The unique identifier of the user to retrieve
            request_body: Optional request body data for the request. Defaults to None

        Returns:
            A dictionary containing user details retrieved from the server response

        Raises:
            ValueError: Raised when the 'id' parameter is None
            requests.exceptions.HTTPError: Raised when the server returns an unsuccessful status code

        Tags:
            retrieve, get, user, api, single-record, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/users/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_all_users(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a complete list of users from the API endpoint.

        Args:
            None: This method does not take any parameters.

        Returns:
            dict[str, Any]: A dictionary containing user data where keys are strings and values can be of any type, representing user information retrieved from the API.

        Raises:
            HTTPError: Raised when the API request fails or returns a non-200 status code
            RequestException: Raised when there are network connectivity issues or other request-related problems

        Tags:
            list, users, api, fetch, management, important
        """
        url = f"{self.base_url}/v1/users"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_your_token_sbot_user(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the current user's authentication token information from the SBOT service.

        Returns:
            A dictionary containing the authentication token and related user information from the JSON response.

        Raises:
            requests.exceptions.HTTPError: When the API request fails or returns a non-200 status code
            requests.exceptions.RequestException: When there are network connectivity issues or other request-related problems

        Tags:
            retrieve, authentication, token, user, api, important
        """
        url = f"{self.base_url}/v1/users/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_database(self, id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific database using its unique identifier.

        Args:
            id: Unique identifier for the database to retrieve. Must be a non-null value.

        Returns:
            A dictionary containing detailed information about the requested database.

        Raises:
            ValueError: Raised when the 'id' parameter is None
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            retrieve, get, database, api, data-access, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_a_database(self, id, request_body=None) -> dict[str, Any]:
        """
        Updates a database entry with the specified ID using a PATCH request.

        Args:
            id: The unique identifier of the database entry to update.
            request_body: Optional dictionary containing the fields and values to update. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the server's JSON response after the update operation.

        Raises:
            ValueError: When the 'id' parameter is None.
            requests.exceptions.HTTPError: When the server returns an unsuccessful status code.

        Tags:
            update, database, patch, important, api, management
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def query_a_database(self, id, request_body=None) -> dict[str, Any]:
        """
        Executes a database query operation using a specified database ID and optional request parameters

        Args:
            id: The unique identifier of the database to query
            request_body: Optional JSON-compatible dictionary representing the body of the query request; if None, no additional query data is sent

        Returns:
            A dictionary containing the response data from the database query as parsed from JSON

        Raises:
            ValueError: Raised when the required 'id' parameter is None
            HTTPError: Raised when the HTTP request fails or returns an error status code

        Tags:
            query, database, api, data-retrieval, http, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}/query"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_a_database(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new database on the server by sending a POST request to the database endpoint.

        Args:
            request_body: Optional dictionary containing configuration parameters for the new database. Defaults to None.

        Returns:
            A dictionary containing the server's JSON response with details of the created database.

        Raises:
            HTTPError: Raised when the server returns a non-200 status code indicating database creation failure
            RequestException: Raised when network connectivity issues occur during the API request
            JSONDecodeError: Raised when the server response cannot be parsed as valid JSON

        Tags:
            create, database, api, management, important
        """
        url = f"{self.base_url}/v1/databases/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_a_page(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new page by sending a POST request to the API endpoint.

        Args:
            request_body: Optional dictionary containing the page data to be sent in the POST request body. Defaults to None.

        Returns:
            Dictionary containing the JSON response from the server with details of the newly created page.

        Raises:
            HTTPError: When the server returns a non-200 status code, indicating a failed request
            RequestException: When network-related issues occur during the API request

        Tags:
            create, page, api, http, post, important
        """
        url = f"{self.base_url}/v1/pages/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_page(self, id) -> dict[str, Any]:
        """
        Retrieves a specific page's data from a remote server using its unique identifier.

        Args:
            id: The unique identifier of the page to retrieve

        Returns:
            A dictionary containing the page data returned from the server's JSON response

        Raises:
            ValueError: When the 'id' parameter is None
            HTTPError: When the server returns an unsuccessful status code

        Tags:
            retrieve, fetch, api, http, get, page, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/pages/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_page_properties(self, id, request_body=None) -> dict[str, Any]:
        """
        Updates the properties of a page with the specified ID using the provided request body.

        Args:
            id: The unique identifier of the page to update. Must not be None.
            request_body: Optional dictionary containing the properties to be updated. Defaults to None.

        Returns:
            Dictionary containing the updated page properties as returned by the server.

        Raises:
            ValueError: When the required 'id' parameter is None
            HTTPError: When the server returns an unsuccessful status code
            RequestException: When there is an error making the HTTP request

        Tags:
            update, api, page-management, http, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/pages/{id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_page_property_item(self, page_id, property_id) -> dict[str, Any]:
        """
        Retrieves a specific property item from a Notion page using the page ID and property ID.

        Args:
            page_id: The unique identifier of the Notion page from which to retrieve the property
            property_id: The unique identifier of the specific property to retrieve

        Returns:
            A dictionary containing the property item's details from the API response

        Raises:
            ValueError: When either page_id or property_id is None
            HTTPError: When the API request fails or returns an error status code

        Tags:
            retrieve, get, property, page, api, notion, important
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        if property_id is None:
            raise ValueError("Missing required parameter 'property_id'")
        url = f"{self.base_url}/v1/pages/{page_id}/properties/{property_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_block_children(self, id, page_size=None) -> dict[str, Any]:
        """
        Retrieves all child blocks for a specified parent block using its ID via the API.

        Args:
            id: The unique identifier of the parent block whose children are to be retrieved
            page_size: Optional integer specifying the maximum number of children to return per page in the response

        Returns:
            A dictionary containing the API response data with the children blocks information

        Raises:
            ValueError: When the required 'id' parameter is None
            HTTPError: When the API request fails or returns an error status code

        Tags:
            retrieve, list, blocks, children, pagination, api-call, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {k: v for k, v in [("page_size", page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def append_block_children(self, id, request_body=None) -> dict[str, Any]:
        """
        Appends child elements to a specified block and returns the updated block data.

        Args:
            id: String identifier of the block to which children will be appended
            request_body: Optional dictionary containing the child elements to be appended (default: None)

        Returns:
            dict[str, Any]: A dictionary containing the updated block data after appending the children

        Raises:
            ValueError: When the required 'id' parameter is None
            HTTPError: When the API request fails or returns an error status code

        Tags:
            append, update, blocks, children, api, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_block(self, id) -> dict[str, Any]:
        """
        Retrieves a specific block of data from the API using its unique identifier.

        Args:
            id: The unique identifier for the block to be retrieved. Must be a non-None value.

        Returns:
            A dictionary containing the block data retrieved from the API, parsed from the JSON response.

        Raises:
            ValueError: When the 'id' parameter is None
            HTTPError: When the API request fails or returns an error status code

        Tags:
            retrieve, fetch, api, data, block, single, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_a_block(self, id) -> dict[str, Any]:
        """
        Deletes a specified block by its ID and returns the server response.

        Args:
            id: The unique identifier of the block to be deleted. Must not be None.

        Returns:
            A dictionary containing the server's response data after the deletion operation.

        Raises:
            ValueError: When the 'id' parameter is None
            HTTPError: When the server returns an unsuccessful status code

        Tags:
            delete, important, management, api, http, block-management
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_a_block(self, id, request_body=None) -> dict[str, Any]:
        """
        Updates a specific block resource via a PATCH request to the API endpoint

        Args:
            id: The unique identifier of the block to update
            request_body: Optional dictionary containing the update data for the block. Defaults to None

        Returns:
            Dictionary containing the server's JSON response with the updated block information

        Raises:
            ValueError: When the required 'id' parameter is None
            HTTPError: When the server responds with an error status code

        Tags:
            update, patch, api, block-management, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def search(self, request_body=None) -> dict[str, Any]:
        """
        Executes a search operation by sending a POST request to the search endpoint and returns the results

        Args:
            request_body: Optional dictionary containing the search parameters and filters to be sent in the request. Defaults to None.

        Returns:
            A dictionary containing the parsed JSON response from the search operation with search results and metadata

        Raises:
            HTTPError: Raised when the search request fails or returns a non-200 status code
            JSONDecodeError: Raised when the response cannot be parsed as valid JSON

        Tags:
            search, important, http, query, api-request, json
        """
        url = f"{self.base_url}/v1/search"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_comments(
        self, block_id=None, page_size=None, request_body=None
    ) -> dict[str, Any]:
        """
        Retrieves comments from a remote server with optional block filtering and pagination support.

        Args:
            block_id: Optional string or ID that specifies which block's comments to retrieve. If None, retrieves all comments.
            page_size: Optional integer specifying the number of comments to return per page. If None, uses server's default pagination.
            request_body: Optional dictionary for future extensibility. Currently unused.

        Returns:
            Dictionary containing comment data parsed from the server's JSON response.

        Raises:
            HTTPError: Raised when the server returns a non-200 status code
            RequestException: Raised for network-related errors during the HTTP request

        Tags:
            retrieve, fetch, comments, api, pagination, http, important
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {
            k: v
            for k, v in [("block_id", block_id), ("page_size", page_size)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_comment_to_page(self, request_body=None) -> dict[str, Any]:
        """
        Adds a comment to a page by making an HTTP POST request to the comments endpoint.

        Args:
            request_body: Optional dictionary containing the comment data to be posted. If None, an empty comment will be created. Defaults to None.

        Returns:
            Dictionary containing the server's JSON response with details of the created comment.

        Raises:
            HTTPError: Raised when the server returns a non-200 status code, indicating the comment creation failed.
            RequestException: Raised when there are network connectivity issues or other request-related problems.

        Tags:
            add, create, comment, post, api, content-management, important
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.retrieve_a_user,
            self.list_all_users,
            self.retrieve_your_token_sbot_user,
            self.retrieve_a_database,
            self.update_a_database,
            self.query_a_database,
            self.create_a_database,
            self.create_a_page,
            self.retrieve_a_page,
            self.update_page_properties,
            self.retrieve_a_page_property_item,
            self.retrieve_block_children,
            self.append_block_children,
            self.retrieve_a_block,
            self.delete_a_block,
            self.update_a_block,
            self.search,
            self.retrieve_comments,
            self.add_comment_to_page,
        ]
