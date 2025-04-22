from typing import Any
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration

class FigmaApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='figmaapp', integration=integration, **kwargs)
        self.base_url = "https://api.figma.com/v1"

    def get_design(self, file_key) -> Any:
        """
        Retrieves the design data for a specified file key from the external API.
        
        Args:
            file_key: str. The unique identifier for the design file to retrieve.
        
        Returns:
            dict. The JSON response containing the design data for the specified file key.
        
        Raises:
            ValueError: Raised if 'file_key' is None.
            HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            get, design, api, network, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/files/{file_key}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_design_node(self, file_key, ids=None) -> Any:
        """
        Retrieves specific design node data from a file using the provided file key and optional node IDs.
        
        Args:
            file_key: A string representing the unique identifier of the file to retrieve nodes from.
            ids: An optional list or comma-separated string of node IDs to filter the results. If omitted, fetches all nodes.
        
        Returns:
            The JSON-decoded response containing the requested node data from the API.
        
        Raises:
            ValueError: If 'file_key' is None.
            requests.HTTPError: If the HTTP request to the API fails (non-2xx response).
        
        Tags:
            get, design-node, file, api, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/files/{file_key}/nodes"
        query_params = {k: v for k, v in [('ids', ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_images(self, file_key) -> Any:
        """
        Retrieves the list of images associated with the specified file key from the remote service.
        
        Args:
            file_key: The unique identifier for the file whose images are to be retrieved. Must not be None.
        
        Returns:
            A JSON-serializable object containing the retrieved images' information as returned by the remote service.
        
        Raises:
            ValueError: Raised if 'file_key' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve images fails (i.e., response status is not successful).
        
        Tags:
            get, images, api, fetch, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/files/{file_key}/images"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_image_node(self, file_key, ids=None) -> Any:
        """
        Retrieves image node data for a specified file key, optionally filtering by image IDs.
        
        Args:
            file_key: The unique key or identifier for the file whose image node data is to be fetched. Must not be None.
            ids: Optional. A value or list of values specifying specific image IDs to filter the results.
        
        Returns:
            A parsed JSON object containing the image node data returned by the API.
        
        Raises:
            ValueError: If 'file_key' is None.
            requests.HTTPError: If the HTTP request to retrieve the image node data fails.
        
        Tags:
            get, image-node, api, async-job, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/images/{file_key}"
        query_params = {k: v for k, v in [('ids', ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_comments(self, file_key) -> Any:
        """
        Retrieves the list of comments associated with a specified file.
        
        Args:
            file_key: The unique identifier of the file for which to fetch comments.
        
        Returns:
            A JSON object containing the comments data for the specified file.
        
        Raises:
            ValueError: If 'file_key' is None.
            requests.exceptions.HTTPError: If the HTTP request to fetch comments fails.
        
        Tags:
            get, file-comments, fetch, api, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/files/{file_key}/comments"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_anew_comment(self, file_key, comment_id=None, message=None) -> Any:
        """
        Posts a new comment to a file, or replies to an existing comment if a comment ID is provided.
        
        Args:
            file_key: str. The unique identifier of the file to which the comment will be posted. Required.
            comment_id: Optional[str]. The ID of an existing comment to reply to. If None, creates a new top-level comment. Default is None.
            message: Optional[str]. The content of the comment. Default is None.
        
        Returns:
            dict. The JSON response from the server containing details of the newly created comment or reply.
        
        Raises:
            ValueError: If 'file_key' is None.
            requests.HTTPError: If the server returns an unsuccessful status code.
        
        Tags:
            post, comment, files, api, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        request_body = {
            'comment_id': comment_id,
            'message': message,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_key}/comments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_team_projects(self, team_id) -> Any:
        """
        Retrieves the list of projects associated with a specified team.
        
        Args:
            team_id: The unique identifier of the team whose projects are to be fetched.
        
        Returns:
            The parsed JSON response containing the team's projects.
        
        Raises:
            ValueError: If the required parameter 'team_id' is None.
            requests.HTTPError: If the HTTP request to fetch the projects fails (non-2xx response).
        
        Tags:
            get, list, projects, team, api, important
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/teams/{team_id}/projects"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_files(self, project_id) -> Any:
        """
        Retrieves the list of files associated with the specified project.
        
        Args:
            project_id: The unique identifier of the project whose files are to be fetched.
        
        Returns:
            A JSON-decoded Python object containing the list of project files and related metadata as returned by the server.
        
        Raises:
            ValueError: Raised if 'project_id' is None.
            requests.HTTPError: Raised if the HTTP request to fetch project files fails with an unsuccessful status code.
        
        Tags:
            get, list, project-management, files, important
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}/files"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_variable_collection(self, file_key, variableCollections=None) -> Any:
        """
        Creates a new collection of variables for a specified file by sending a POST request to the server.
        
        Args:
            file_key: str. The identifier of the file to which the variable collection will be added.
            variableCollections: Optional. The variable collection data to add. If None, no additional variables are included.
        
        Returns:
            dict. The response from the server parsed as a JSON object containing details about the created variable collection.
        
        Raises:
            ValueError: Raised if 'file_key' is None.
            requests.HTTPError: Raised if the HTTP request to the server fails (non-2xx response).
        
        Tags:
            create, variable-collection, api-call, post, management, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        request_body = {
            'variableCollections': variableCollections,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/files/{file_key}/variables"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_dev_resources(self, file_key) -> Any:
        """
        Retrieves development resources associated with a specific file key from the server.
        
        Args:
            file_key: The unique identifier of the file for which to fetch development resources.
        
        Returns:
            The parsed JSON response containing the development resources for the specified file.
        
        Raises:
            ValueError: Raised if 'file_key' is None.
            requests.HTTPError: Raised if the HTTP request fails with an error status code.
        
        Tags:
            get, dev-resources, file-management, api, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/files/{file_key}/dev_resources"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_dev_resource(self, dev_resources=None) -> Any:
        """
        Posts developer resource data to the remote API endpoint and returns the parsed JSON response.
        
        Args:
            dev_resources: Optional. The developer resource data to post in the request body. Can be any serializable object or None.
        
        Returns:
            The parsed JSON response from the API as a Python object.
        
        Raises:
            requests.HTTPError: Raised if the HTTP response status code indicates an error (response.raise_for_status()).
        
        Tags:
            post, dev-resources, api, request, important
        """
        request_body = {
            'dev_resources': dev_resources,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/dev_resources"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_library_analytics(self, library_file_key) -> Any:
        """
        Retrieves analytics usage data for a specific library file by its key.
        
        Args:
            library_file_key: The unique identifier (key) of the library file for which analytics are retrieved. Must not be None.
        
        Returns:
            A parsed JSON object containing usage analytics data for the specified library file.
        
        Raises:
            ValueError: If 'library_file_key' is None.
            requests.exceptions.HTTPError: If the HTTP request for analytics data fails with an unsuccessful status code.
        
        Tags:
            get, analytics, library, usage, api, important
        """
        if library_file_key is None:
            raise ValueError("Missing required parameter 'library_file_key'")
        url = f"{self.base_url}/analytics/libraries/{library_file_key}/usages"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_actions_analytics(self, library_file_key) -> Any:
        """
        Retrieves analytics data about actions associated with a specified library file key.
        
        Args:
            library_file_key: The unique identifier of the library file for which to fetch action analytics.
        
        Returns:
            A JSON-serializable object containing analytics information about actions for the given library file key.
        
        Raises:
            ValueError: If 'library_file_key' is None.
            requests.HTTPError: If the HTTP request to the analytics endpoint fails or returns an error status code.
        
        Tags:
            get, analytics, actions, library-file, http, important
        """
        if library_file_key is None:
            raise ValueError("Missing required parameter 'library_file_key'")
        url = f"{self.base_url}/analytics/libraries/{library_file_key}/actions"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_all_webhooks_for_team(self, ) -> Any:
        """
        Retrieves all webhooks configured for the team by sending a GET request to the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            The JSON-decoded response containing a list of webhooks for the team.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.
        
        Tags:
            get, list, webhooks, management, important
        """
        url = f"{self.base_url}/"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_webhook(self, ) -> Any:
        """
        Sends a POST request to register a new webhook and returns the response data.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            dict: JSON-decoded response from the webhook registration endpoint.
        
        Raises:
            requests.exceptions.HTTPError: If the server returns an unsuccessful HTTP status code.
        
        Tags:
            add, webhook, http, post, api, important
        """
        url = f"{self.base_url}/"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_webhook(self, webhook_id) -> Any:
        """
        Deletes a webhook with the specified webhook ID from the service.
        
        Args:
            webhook_id: The unique identifier of the webhook to be deleted. Must not be None.
        
        Returns:
            The JSON-decoded response from the delete request as a Python object.
        
        Raises:
            ValueError: If 'webhook_id' is None.
            requests.HTTPError: If the delete request returns an unsuccessful HTTP status code.
        
        Tags:
            delete, webhook, api, management, important
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/{webhook_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_design,
            self.get_design_node,
            self.get_images,
            self.get_image_node,
            self.get_file_comments,
            self.post_anew_comment,
            self.get_team_projects,
            self.get_project_files,
            self.create_variable_collection,
            self.get_dev_resources,
            self.post_dev_resource,
            self.get_library_analytics,
            self.get_actions_analytics,
            self.get_all_webhooks_for_team,
            self.add_webhook,
            self.delete_webhook
        ]
