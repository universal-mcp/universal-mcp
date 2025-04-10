from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class NotionApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes a new instance of the Notion API app with a specified integration and additional parameters.
        
        Args:
            integration: Optional; an Integration object containing credentials for authenticating with the Notion API. Defaults to None.
            kwargs: Additional keyword arguments that are passed to the parent class initializer.
        
        Returns:
            None
        """
        super().__init__(name='notion', integration=integration, **kwargs)
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
        Retrieves user details from the server using the specified user ID.
        
        Args:
            self: Instance of the class containing the method.
            id: The unique identifier of the user to retrieve.
            request_body: Optional request body data, provided when needed. Default is None.
        
        Returns:
            A dictionary containing user details, as retrieved from the server response.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/users/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_all_users(self, ) -> dict[str, Any]:
        """
        Fetches a list of all users from the API endpoint and returns the data as a dictionary.
        
        Args:
            None: This method does not take any parameters.
        
        Returns:
            A dictionary containing the list of users retrieved from the API. The dictionary keys are strings, and the values can be of any type.
        """
        url = f"{self.base_url}/v1/users"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_your_token_sbot_user(self, ) -> dict[str, Any]:
        """
        Retrieves the authentication token for the current user from the SBOT service.
        
        Args:
            self: Instance of the class containing configuration such as 'base_url' and the '_get' method.
        
        Returns:
            A dictionary containing the JSON response of the current user's token information.
        """
        url = f"{self.base_url}/v1/users/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_database(self, id) -> dict[str, Any]:
        """
        Retrieves database details from a specified endpoint using the provided database ID.
        
        Args:
            id: A unique identifier for the database to be retrieved. Must be a non-null value.
        
        Returns:
            A dictionary containing the details of the requested database.
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
        Updates a database entry with the given ID using a PATCH request.
        
        Args:
            self: The instance of the class to which the method belongs.
            id: The unique identifier of the database entry to be updated.
            request_body: An optional dictionary containing the data to update the database entry with. Defaults to None.
        
        Returns:
            A dictionary representing the JSON response from the server after the update operation.
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
        Executes a query on a specified database using an identifier and an optional request body.
        
        Args:
            id: The unique identifier of the database to query.
            request_body: Optional JSON-compatible dictionary representing the body of the query request; if None, no additional query data is sent.
        
        Returns:
            A dictionary containing the response data from the database query as parsed from JSON.
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
        Creates a new database on the server using the specified request body.
        
        Args:
            request_body: A dictionary containing the data to be sent in the request body. Defaults to None if not provided.
        
        Returns:
            A dictionary containing the server's JSON response from the database creation request.
        """
        url = f"{self.base_url}/v1/databases/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_a_page(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new page by sending a POST request to the specified endpoint.
        
        Args:
            request_body: Optional; A dictionary containing the data to be sent in the body of the POST request. Defaults to None.
        
        Returns:
            A dictionary representing the JSON response from the server, containing the details of the newly created page.
        """
        url = f"{self.base_url}/v1/pages/"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_page(self, id) -> dict[str, Any]:
        """
        Retrieves a page by its unique identifier from a remote server.
        
        Args:
            id: The unique identifier of the page to retrieve.
        
        Returns:
            A dictionary containing the JSON response from the server, which represents the page data.
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
        Updates the properties of a page identified by its ID using the provided request body.
        
        Args:
            id: The unique identifier of the page whose properties are to be updated. Must not be None.
            request_body: An optional dictionary representing the request payload containing the properties to be updated. Defaults to None.
        
        Returns:
            A dictionary containing the updated page properties as returned by the server after the update.
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
        Retrieves the property item of a page using specified page and property identifiers.
        
        Args:
            page_id: The unique identifier of the page from which the property item is to be retrieved.
            property_id: The unique identifier of the property associated with the specified page.
        
        Returns:
            A dictionary representing the JSON response with details of the property item.
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
        Retrieves the children of a specified block using its unique identifier.
        
        Args:
            id: The unique identifier of the block whose children are to be retrieved.
            page_size: Optional; The maximum number of children to return per page in the response, if specified.
        
        Returns:
            A dictionary containing the data representing the children of the specified block.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {k: v for k, v in [('page_size', page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def append_block_children(self, id, request_body=None) -> dict[str, Any]:
        """
        Appends child elements to a block identified by its ID and returns the updated block data.
        
        Args:
            self: Instance of the class containing this method.
            id: The identifier of the block to which children will be appended. It must not be None.
            request_body: Optional dictionary containing the data of the child elements to be appended to the block.
        
        Returns:
            A dictionary representing the updated block data after appending the child elements.
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
        Retrieves a block of data from a given API endpoint using the specified block ID.
        
        Args:
            id: The unique identifier for the block to be retrieved. It must be a non-None value, otherwise a ValueError will be raised.
        
        Returns:
            A dictionary containing the JSON response from the API, representing the block data corresponding to the provided ID.
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
        Deletes a block by its unique identifier and returns the server's response.
        
        Args:
            id: The unique identifier of the block to be deleted. Must not be None.
        
        Returns:
            A dictionary containing the response data from the server after attempting to delete the block.
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
        Updates a block by sending a PATCH request to the specified endpoint.
        
        Args:
            id: The unique identifier for the block that is to be updated.
            request_body: Optional; A dictionary containing the data to update the block with. Defaults to None.
        
        Returns:
            A dictionary containing the JSON response from the server after updating the block.
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
        Executes a search query using the specified request body and returns the results.
        
        Args:
            request_body: An optional dictionary containing the data to be sent in the search request.
        
        Returns:
            A dictionary containing the JSON-decoded response from the search operation.
        """
        url = f"{self.base_url}/v1/search"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_comments(self, block_id=None, page_size=None, request_body=None) -> dict[str, Any]:
        """
        Fetches comments from a remote server for a specified block, with optional pagination.
        
        Args:
            block_id: Optional; Identifies the block whose comments should be retrieved. If None, retrieves comments without filtering by block.
            page_size: Optional; Specifies the number of comments to retrieve per page for pagination. If None, the server's default page size is used.
            request_body: Unused placeholder for future extensibility; this function currently does not utilize this parameter.
        
        Returns:
            A dictionary containing the response data from the server, parsed from JSON, with keys and values representing comment-related information.
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {k: v for k, v in [('block_id', block_id), ('page_size', page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_comment_to_page(self, request_body=None) -> dict[str, Any]:
        """
        Adds a comment to a page by sending a POST request with the provided request body.
        
        Args:
            request_body: Optional; A dictionary containing the data for the comment to be added. Defaults to None.
        
        Returns:
            A dictionary representing the JSON response from the server, which includes details of the newly added comment.
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of functions related to user and database operations.
        
        Args:
            self: The instance of the class to which the function belongs.
        
        Returns:
            A list of method references that pertain to various operations such as user retrieval, database operations, and page/block management.
        """
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
            self.add_comment_to_page
        ]
