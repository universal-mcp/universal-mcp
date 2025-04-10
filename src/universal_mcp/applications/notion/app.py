from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from typing import Any, Dict, List

class NotionApiApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes the NotionAPIApp with a specified integration and optional additional keyword arguments.
        
        Args:
            integration: An Integration object to be used for authenticating or interfacing with the Notion API. Defaults to None.
            kwargs: Additional keyword arguments that are passed to the parent's class initialization.
        
        Returns:
            None
        """
        super().__init__(name='notionapiapp', integration=integration, **kwargs)
        self.base_url = "https://api.notion.com"

    def retrieve_a_user(self, id, request_body=None) -> Dict[str, Any]:
        """
        Retrieves a user's information from the API based on the user ID.
        
        Args:
            self: The instance of the class this method is a part of.
            id: The unique identifier of the user to retrieve. Must not be None.
            request_body: Optional JSON serializable dictionary for any additional parameters to be passed in the request. Defaults to None.
        
        Returns:
            A dictionary containing the user's information retrieved from the API.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/users/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_all_users(self, ) -> Dict[str, Any]:
        """
        Retrieves a list of all users from the API.
        
        Args:
            None: This method does not take any parameters.
        
        Returns:
            A dictionary containing the JSON response from the API, with details about all users.
        """
        url = f"{self.base_url}/v1/users"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_your_token_sbot_user(self, ) -> Dict[str, Any]:
        """
        Retrieves the token for the current user from the server.
        
        Args:
            None: This method does not take any parameters.
        
        Returns:
            A dictionary containing the JSON response from the server with the user's token information.
        """
        url = f"{self.base_url}/v1/users/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_database(self, id) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific database by its ID.
        
        Args:
            id: The unique identifier of the database to retrieve.
        
        Returns:
            A dictionary containing the detailed information of the specified database.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_a_database(self, id, request_body=None) -> Dict[str, Any]:
        """
        Updates a database entry with the given identifier and optional request body.
        
        Args:
            self: The instance of the class; refers to the current object.
            id: The unique identifier of the database entry to be updated. Must not be None.
            request_body: Optional. A dictionary containing the data to be updated in the database. Defaults to None.
        
        Returns:
            A dictionary containing the JSON response from the API, after updating the database entry.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def query_a_database(self, id, request_body=None) -> Dict[str, Any]:
        """
        Queries a database by sending a POST request to a specified endpoint.
        
        Args:
            id: The identifier of the database to query. This parameter is required.
            request_body: Optional dictionary representing the JSON body of the request. Defaults to None if not provided.
        
        Returns:
            A dictionary representing the JSON response from the database query.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}/query"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_a_database(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new database by sending a POST request to the specified endpoint.
        
        Args:
            request_body: The JSON data to be sent in the request body for creating the database. Defaults to None if not provided.
        
        Returns:
            A dictionary containing the JSON response from the server, which includes details about the newly created database.
        """
        url = f"{self.base_url}/v1/databases/"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_a_page(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new page using the specified request body data.
        
        Args:
            request_body: Optional dictionary containing the data to create the new page. Defaults to None if not provided.
        
        Returns:
            A dictionary representing the JSON response from the server after attempting to create the page.
        """
        url = f"{self.base_url}/v1/pages/"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_page(self, id) -> Dict[str, Any]:
        """
        Retrieves a page's details using the provided page ID.
        
        Args:
            self: Instance of the class containing this method.
            id: The unique identifier of the page to retrieve.
        
        Returns:
            A dictionary containing the details of the specified page.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/pages/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_page_properties(self, id, request_body=None) -> Dict[str, Any]:
        """
        Updates the properties of a page with the specified ID using a PATCH request.
        
        Args:
            id: The unique identifier of the page to update. This parameter is required.
            request_body: Optional dictionary specifying the properties to update on the page. Defaults to None if not provided.
        
        Returns:
            A dictionary containing the response data from the server after updating the page properties.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/pages/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_page_property_item(self, page_id, property_id) -> Dict[str, Any]:
        """
        Retrieves a specific property item from a page by page ID and property ID.
        
        Args:
            page_id: The unique identifier of the page from which to retrieve the property item.
            property_id: The unique identifier of the property item to retrieve from the specified page.
        
        Returns:
            A dictionary containing the details of the property item, as retrieved from the page.
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

    def retrieve_block_children(self, id, page_size=None) -> Dict[str, Any]:
        """
        Retrieves the children of a block by its unique identifier, with optional pagination.
        
        Args:
            id: The unique identifier of the block whose children are to be retrieved.
            page_size: Optional; the maximum number of children to return per page. If not provided, the default page size is used.
        
        Returns:
            A dictionary containing the children of the specified block along with their details.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {k: v for k, v in [('page_size', page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def append_block_children(self, id, request_body=None) -> Dict[str, Any]:
        """
        Appends children to a given block by ID and returns the response as a dictionary.
        
        Args:
            id: The unique identifier of the block to which children are to be appended.
            request_body: Optional. A dictionary representing the request body. Defaults to None.
        
        Returns:
            A dictionary containing the JSON response from the server after appending children to the block.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_a_block(self, id) -> Dict[str, Any]:
        """
        Retrieves a block by its unique identifier from the server.
        
        Args:
            id: The unique identifier of the block to be retrieved. Must be a non-null string.
        
        Returns:
            A dictionary containing the block data retrieved from the server.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_a_block(self, id) -> Dict[str, Any]:
        """
        Deletes a block with the specified identifier from the system.
        
        Args:
            id: The unique identifier of the block to be deleted.
        
        Returns:
            A dictionary containing the JSON response from the server after the block is deleted.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_a_block(self, id, request_body=None) -> Dict[str, Any]:
        """
        Updates an existing block with new data using the provided identifier and request body.
        
        Args:
            id: The unique identifier of the block to be updated.
            request_body: Optional; a dictionary representing the data of the block to update. Defaults to None if not specified.
        
        Returns:
            A dictionary containing the JSON response from the server after updating the block.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def search(self, request_body=None) -> Dict[str, Any]:
        """
        Performs a search operation by sending a POST request to the specified search endpoint.
        
        Args:
            request_body: An optional dictionary representing the request payload to be sent in the POST request. Defaults to None if not provided.
        
        Returns:
            A dictionary containing the response data of the search operation, parsed from the JSON content of the HTTP response.
        """
        url = f"{self.base_url}/v1/search"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def retrieve_comments(self, block_id=None, page_size=None, request_body=None) -> Dict[str, Any]:
        """
        Fetches comments from a specified endpoint with optional filtering and pagination.
        
        Args:
            block_id: Optional; The ID of the block for which to retrieve comments. If not specified, comments for all blocks are retrieved.
            page_size: Optional; The number of comments to retrieve per page. If not specified, a default page size is used.
            request_body: Optional; A dictionary representing the request body to send. If not specified, no body is sent.
        
        Returns:
            A dictionary containing the retrieved comments data.
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {k: v for k, v in [('block_id', block_id), ('page_size', page_size)] if v is not None}
        json_body = request_body if request_body is not None else None
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_comment_to_page(self, request_body=None) -> Dict[str, Any]:
        """
        Sends a POST request to add a new comment to a page.
        
        Args:
            request_body: Optional; A dictionary containing the comment data to send in the request body. Defaults to None.
        
        Returns:
            A dictionary containing the JSON response from the server after adding the comment.
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of methods available for various user and database operations.
        
        Args:
            self: Instance of the class, typically used to access attributes and methods.
        
        Returns:
            List of method references that can be used to perform specific operations related to users and databases.
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
