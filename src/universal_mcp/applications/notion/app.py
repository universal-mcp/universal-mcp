from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from typing import Any, Dict, List

class NotionApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes a new instance of the class with given integration and additional options.
        
        Args:
            integration: An optional Integration instance to configure the connection. Defaults to None.
            **kwargs: Additional keyword arguments for configuration.
        
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

    def notion_retrieve_auser(self, id, request_body=None) -> Dict[str, Any]:
        """
        Retrieves user information from the Notion API by user ID.
        
        Args:
            id: The unique identifier of the user whose information is to be retrieved.
            request_body: A dictionary representing the request body, optional, default is None.
        
        Returns:
            A dictionary containing the user's information from the Notion API.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/users/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_list_all_users(self, ) -> Dict[str, Any]:
        """
        Fetches and returns a list of all users from the Notion API.
        
        Args:
            None: This method does not take any parameters.
        
        Returns:
            A dictionary containing the JSON response from the Notion API, representing all users data.
        """
        url = f"{self.base_url}/v1/users"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_your_token_sbot_user(self, ) -> Dict[str, Any]:
        """
        Retrieves the current user's token data from the Notion API.
        
        Args:
            self: Instance of the class containing the necessary configuration and authentication details for accessing the Notion API.
        
        Returns:
            A dictionary containing the current user's token information as retrieved from the Notion API.
        """
        url = f"{self.base_url}/v1/users/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_adatabase(self, id) -> Dict[str, Any]:
        """
        Retrieves a Notion database by its unique identifier.
        
        Args:
            id: A string representing the unique identifier of the Notion database to be retrieved.
        
        Returns:
            A dictionary containing the details of the retrieved Notion database.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_update_adatabase(self, id, request_body=None) -> Dict[str, Any]:
        """
        Updates a Notion database with the given ID and request body data.
        
        Args:
            self: An instance of the class containing configuration and methods for HTTP requests.
            id: A string representing the unique identifier of the Notion database to be updated.
            request_body: An optional dictionary containing the fields and values to update in the database.
        
        Returns:
            A dictionary representing the JSON response from the Notion API after updating the database.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_query_adatabase(self, id, request_body=None) -> Dict[str, Any]:
        """
        Executes a query on a Notion database using the Notion API.
        
        Args:
            self: Instance of the class which should contain 'base_url' and '_post' method.
            id: A string representing the unique identifier of the Notion database to query.
            request_body: Optional. A dictionary representing the request body for the query. Defaults to None.
        
        Returns:
            A dictionary containing the JSON response from the Notion API after querying the specified database.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/databases/{id}/query"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_create_adatabase(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new database in Notion using the provided request body.
        
        Args:
            self: Reference to the current instance of the class.
            request_body: Optional dictionary containing the specifications for creating the Notion database. If None, a default empty request body is used.
        
        Returns:
            A dictionary representing the JSON response from the Notion API, containing data about the newly created database.
        """
        url = f"{self.base_url}/v1/databases/"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_create_apage(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new page in Notion by sending a POST request with the specified request body.
        
        Args:
            request_body: Optional; A dictionary containing the data to create a new page in Notion. Defaults to None.
        
        Returns:
            A dictionary containing the JSON response from the Notion API with the details of the newly created page.
        """
        url = f"{self.base_url}/v1/pages/"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_apage(self, id) -> Dict[str, Any]:
        """
        Retrieves a page from the Notion API using a given page ID.
        
        Args:
            id: The unique identifier of the Notion page to be retrieved.
        
        Returns:
            A dictionary containing the JSON response from the Notion API, representing the page data.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/pages/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_update_page_properties(self, id, request_body=None) -> Dict[str, Any]:
        """
        Updates the properties of a Notion page identified by a given ID.
        
        Args:
            self: Instance of the class containing the Notion API credentials and methods.
            id: The unique identifier of the Notion page to update. Must not be None.
            request_body: An optional dictionary representing the request body to be sent with the update request. Defaults to None, indicating no additional properties to update.
        
        Returns:
            A dictionary containing the JSON response from the Notion API after the page update request.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/pages/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_apage_property_item(self, page_id, property_id) -> Dict[str, Any]:
        """
        Retrieves a specific property item from a page in Notion using the page and property IDs.
        
        Args:
            page_id: The unique identifier for the Notion page from which the property item should be retrieved.
            property_id: The unique identifier for the property item within the specified page that should be retrieved.
        
        Returns:
            A dictionary containing the JSON response from the Notion API representing the requested property item.
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

    def notion_retrieve_block_children(self, id, page_size=None) -> Dict[str, Any]:
        """
        Retrieves the child blocks of a specified Notion block.
        
        Args:
            self: The instance of the class this method belongs to.
            id: The unique identifier of the parent block whose children are to be retrieved.
            page_size: Optional; the number of child blocks to retrieve per request.
        
        Returns:
            A dictionary containing the JSON response with details about the child blocks.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {k: v for k, v in [('page_size', page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_append_block_children(self, id, request_body=None) -> Dict[str, Any]:
        """
        Appends child blocks to a block in Notion using its API.
        
        Args:
            self: Instance of the class containing Notion API credentials and configuration.
            id: The unique identifier of the parent block to which child blocks are to be appended.
            request_body: An optional dictionary containing the block data to append. Defaults to None.
        
        Returns:
            A dictionary representing the response from the Notion API, containing the result of the append operation.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}/children"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_ablock(self, id) -> Dict[str, Any]:
        """
        Retrieves a block from the Notion API using the specified block ID.
        
        Args:
            id: The unique identifier of the block to retrieve from the Notion API. Must be a non-null string.
        
        Returns:
            A dictionary containing the block data in JSON format as retrieved from the Notion API.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_delete_ablock(self, id) -> Dict[str, Any]:
        """
        Deletes a block from the Notion database using the specified block ID.
        
        Args:
            id: The unique identifier of the block to be deleted. Must not be None.
        
        Returns:
            A dictionary containing the JSON response from the Notion API after attempting to delete the block.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_update_ablock(self, id, request_body=None) -> Dict[str, Any]:
        """
        Updates a block in Notion with the given ID and request body.
        
        Args:
            id: The unique identifier of the Notion block to update.
            request_body: The request body containing the updates to be made to the block. Defaults to None if not provided.
        
        Returns:
            A dictionary containing the JSON response from the Notion API after the block has been updated.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/blocks/{id}"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_search(self, request_body=None) -> Dict[str, Any]:
        """
        Executes a search request to the Notion API and returns the response in JSON format.
        
        Args:
            request_body: An optional dictionary containing the search parameters for the API request. Defaults to None if not provided.
        
        Returns:
            A dictionary containing the response from the Notion API in JSON format.
        """
        url = f"{self.base_url}/v1/search"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_comments(self, block_id=None, page_size=None, request_body=None) -> Dict[str, Any]:
        """
        Retrieves comments from a Notion block using the Notion API.
        
        Args:
            block_id: Optional; The ID of the block for which to retrieve comments. If None, it retrieves comments for all blocks available to the user.
            page_size: Optional; The maximum number of comments to retrieve in one request. If None, the default page size will be used.
            request_body: Optional; A dictionary to include additional parameters in the request body. If None, no extra parameters are added.
        
        Returns:
            A dictionary containing the JSON response from the Notion API with the comments retrieved.
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {k: v for k, v in [('block_id', block_id), ('page_size', page_size)] if v is not None}
        json_body = request_body if request_body is not None else None
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_add_comment_to_page(self, request_body=None) -> Dict[str, Any]:
        """
        Adds a comment to a specified Notion page using the provided request body.
        
        Args:
            request_body: An optional dictionary containing the details of the comment to be added to the Notion page. If None, no data is sent in the request's body.
        
        Returns:
            A dictionary containing the response data from the Notion API, parsed from JSON format.
        """
        url = f"{self.base_url}/v1/comments"
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of functions that interact with Notion's API for various operations.
        
        Args:
            None: This method does not take any parameters.
        
        Returns:
            A list of functions that perform specific operations with Notion's API, such as retrieving or updating users, databases, pages, blocks, and comments.
        """
        return [
            self.notion_retrieve_auser,
            self.notion_list_all_users,
            self.notion_retrieve_your_token_sbot_user,
            self.notion_retrieve_adatabase,
            self.notion_update_adatabase,
            self.notion_query_adatabase,
            self.notion_create_adatabase,
            self.notion_create_apage,
            self.notion_retrieve_apage,
            self.notion_update_page_properties,
            self.notion_retrieve_apage_property_item,
            self.notion_retrieve_block_children,
            self.notion_append_block_children,
            self.notion_retrieve_ablock,
            self.notion_delete_ablock,
            self.notion_update_ablock,
            self.notion_search,
            self.notion_retrieve_comments,
            self.notion_add_comment_to_page
        ]
