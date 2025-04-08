from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from typing import Any, Dict, List

class NotionApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes a class instance with an optional Integration object and other keyword arguments, and sets the base_url attribute.
        
        Args:
            integration: An optional Integration object to be used with the class instance.
            **kwargs: Additional keyword arguments to be passed to the parent class __init__ method.
        
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
    

    def notion_retrieve_auser(self, request_body=None) -> Dict[str, Any]:
        """
        Retrieves information about a specific user from the Notion API.
        
        Args:
            self: The instance object on which this method is called.
            request_body: Optional. A dictionary containing the request body to send to the Notion API. Default is None.
        
        Returns:
            A dictionary containing the user information retrieved from the Notion API.
        """
        path_params = {}
        url = f"{self.base_url}/v1/users/{id}".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_list_all_users(self, ) -> Dict[str, Any]:
        """
        Retrieves a list of all users from the Notion API
        
        Args:
            self: An instance of the class containing the Notion API base URL and authentication credentials
        
        Returns:
            A dictionary containing the response data from the Notion API, where the keys are the user IDs and the values are the corresponding user data
        """
        path_params = {}
        url = f"{self.base_url}/v1/users".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_your_token_sbot_user(self, ) -> Dict[str, Any]:
        """
        Retrieves the user's token and details from the Notion API.
        
        Args:
            self: The instance of the class containing this method.
        
        Returns:
            A dictionary containing the user's token and other details retrieved from the Notion API.
        """
        path_params = {}
        url = f"{self.base_url}/v1/users/me".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_adatabase(self, ) -> Dict[str, Any]:
        """
        Retrieves a database from the Notion API and returns its data as a Python dictionary.
        
        Args:
            self: The instance of the class that the method belongs to.
            None: This function does not take any arguments.
        
        Returns:
            A Python dictionary containing the data of the retrieved Notion database.
        """
        path_params = {}
        url = f"{self.base_url}/v1/databases/{id}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_update_adatabase(self, request_body=None) -> Dict[str, Any]:
        """
        Updates a database in Notion by sending a PATCH request to the Notion API.
        
        Args:
            self: The instance of the class containing this method.
            request_body: Optional. The request body to send in the PATCH request. If None, no request body is sent.
        
        Returns:
            A dictionary containing the response from the Notion API after updating the database.
        """
        path_params = {}
        url = f"{self.base_url}/v1/databases/{id}".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_query_adatabase(self, request_body=None) -> Dict[str, Any]:
        """
        Sends a query to a specified Notion database and returns the response.
        
        Args:
            self: The instance of the class that the method belongs to.
            request_body: An optional dictionary representing the request body to send with the query. If None, no request body is sent.
        
        Returns:
            A dictionary containing the response from the Notion API, parsed from the JSON response.
        """
        path_params = {}
        url = f"{self.base_url}/v1/databases/{id}/query".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_create_adatabase(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new database in Notion and returns the created database object.
        
        Args:
            self: The instance of the class this method belongs to.
            request_body: Optional JSON data containing the properties for the new database to be created. If not provided, an empty database will be created.
        
        Returns:
            A dictionary containing the created database object, with its properties such as id, title, and other metadata.
        """
        path_params = {}
        url = f"{self.base_url}/v1/databases/".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_create_apage(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new page in Notion and returns its JSON representation.
        
        Args:
            self: The instance of the class containing this method.
            request_body: An optional dictionary or JSON-serializable object representing the request body to send to Notion when creating the new page. If not provided, None will be sent.
        
        Returns:
            A dictionary containing the JSON response from Notion, representing the newly created page.
        """
        path_params = {}
        url = f"{self.base_url}/v1/pages/".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_apage(self, ) -> Dict[str, Any]:
        """
        Retrieves a Notion page by its ID and returns its contents as a dictionary.
        
        Args:
            self: An instance of the class containing this method
            id: The ID of the Notion page to retrieve
        
        Returns:
            A dictionary containing the contents of the retrieved Notion page.
        """
        path_params = {}
        url = f"{self.base_url}/v1/pages/{id}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_update_page_properties(self, request_body=None) -> Dict[str, Any]:
        """
        Updates the properties of a Notion page by sending a PATCH request to the Notion API.
        
        Args:
            self: The instance of the class containing this method.
            request_body: A dictionary containing the properties to update for the Notion page. If not provided, it defaults to None.
        
        Returns:
            A dictionary containing the response from the Notion API after updating the page properties.
        """
        path_params = {}
        url = f"{self.base_url}/v1/pages/{id}".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_apage_property_item(self, ) -> Dict[str, Any]:
        """
        Retrieves a specific property of a Notion page and returns its value.
        
        Args:
            self: The instance of the class containing the method.
            page_id: The ID of the Notion page to retrieve the property from.
            property_id: The ID of the specific property to retrieve from the page.
        
        Returns:
            A dictionary containing the value of the requested property, or an error if the request fails.
        """
        path_params = {}
        url = f"{self.base_url}/v1/pages/{page_id}/properties/{property_id}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_block_children(self, page_size=None) -> Dict[str, Any]:
        """
        Retrieves the child blocks of a given block in Notion and returns them as a dictionary.
        
        Args:
            self: The instance of the class the method belongs to.
            page_size: Optional. The number of child blocks to retrieve per page.
        
        Returns:
            A dictionary containing the child blocks of the specified block.
        """
        path_params = {}
        url = f"{self.base_url}/v1/blocks/{id}/children".format_map(path_params)
        query_params = {k: v for k, v in [('page_size', page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_append_block_children(self, request_body=None) -> Dict[str, Any]:
        """
        Appends new child blocks to an existing block in a Notion workspace.
        
        Args:
            self: The instance of the class that this method belongs to.
            request_body: A JSON object representing the new child blocks to be appended. If None, no new blocks are appended.
        
        Returns:
            A dictionary containing the response from the Notion API, which includes the updated block data.
        """
        path_params = {}
        url = f"{self.base_url}/v1/blocks/{id}/children".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_ablock(self, ) -> Dict[str, Any]:
        """
        Retrieves a single block from the Notion API by its ID.
        
        Args:
            self: An instance of the class that contains this method.
            None: This function does not take any arguments.
        
        Returns:
            A dictionary containing the retrieved block's data. The keys and values of the dictionary will depend on the type of block retrieved.
        """
        path_params = {}
        url = f"{self.base_url}/v1/blocks/{id}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_delete_ablock(self, ) -> Dict[str, Any]:
        """
        Deletes a block from a Notion database using the Notion API.
        
        Args:
            self: An instance of the class containing this method
            id: The ID of the block to be deleted
        
        Returns:
            A dictionary containing the response from the Notion API after attempting to delete the block
        """
        path_params = {}
        url = f"{self.base_url}/v1/blocks/{id}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_update_ablock(self, request_body=None) -> Dict[str, Any]:
        """
        Updates an existing block in a Notion page and returns the updated block data.
        
        Args:
            self: The instance of the class containing this method.
            request_body: Optional. The request body containing the updated block data. If not provided, the block will be updated with default or empty values.
        
        Returns:
            A dictionary containing the updated block data, where the keys represent the block properties, and the values represent their corresponding values.
        """
        path_params = {}
        url = f"{self.base_url}/v1/blocks/{id}".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._patch(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_search(self, request_body=None) -> Dict[str, Any]:
        """
        Performs a search in Notion using the provided request body.
        
        Args:
            self: The instance of the containing class.
            request_body: Optional. A dictionary or JSON-serializable object containing the search request data.
        
        Returns:
            A dictionary containing the search results from the Notion API.
        """
        path_params = {}
        url = f"{self.base_url}/v1/search".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_retrieve_comments(self, block_id=None, page_size=None, request_body=None) -> Dict[str, Any]:
        """
        Retrieve comments from a Notion block.
        
        Args:
            block_id: The ID of the Notion block to retrieve comments for. Optional.
            page_size: The number of comments to retrieve per page. Optional.
            request_body: Additional request parameters in JSON format. Optional.
        
        Returns:
            A dictionary containing the comments retrieved from the Notion block.
        """
        path_params = {}
        url = f"{self.base_url}/v1/comments".format_map(path_params)
        query_params = {k: v for k, v in [('block_id', block_id), ('page_size', page_size)] if v is not None}
        json_body = request_body if request_body is not None else None
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def notion_add_comment_to_page(self, request_body=None) -> Dict[str, Any]:
        """
        Adds a new comment to a Notion page by making a POST request to the Notion API.
        
        Args:
            self: The object instance on which the method is called.
            request_body: A dictionary containing the request data for the new comment, or None if no request body is provided.
        
        Returns:
            A dictionary containing the response data from the Notion API, including the details of the newly created comment.
        """
        path_params = {}
        url = f"{self.base_url}/v1/comments".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of available methods for interacting with Notion.
        
        Args:
            self: An instance of the class containing the listed methods.
        
        Returns:
            A list of methods that can be used to retrieve, update, create, and manage Notion resources such as users, databases, pages, blocks, and comments.
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
