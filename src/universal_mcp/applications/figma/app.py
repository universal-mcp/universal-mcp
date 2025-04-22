from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class FigmaApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="figma", integration=integration, **kwargs)
        self.base_url = "https://api.figma.com"

    def get_file(
        self,
        file_key,
        version=None,
        ids=None,
        depth=None,
        geometry=None,
        plugin_data=None,
        branch_data=None,
    ) -> Any:
        """
        Retrieves file metadata and content from the API using the specified file key and optional query parameters.

        Args:
            file_key: str. The unique identifier for the file to retrieve. Required.
            version: Optional[str]. The version of the file to retrieve. If not specified, the latest version is returned.
            ids: Optional[str or list]. Specific node IDs within the file to retrieve.
            depth: Optional[int]. The depth of the node tree to fetch for the file.
            geometry: Optional[str]. The geometry format to use when retrieving the file.
            plugin_data: Optional[str]. Plugin data to include in the response, if applicable.
            branch_data: Optional[str]. Branch data to include in the response, if applicable.

        Returns:
            dict. The JSON-decoded response containing file metadata and content.

        Raises:
            ValueError: Raised if 'file_key' is not provided.
            requests.HTTPError: Raised if the API request fails (non-2xx response).

        Tags:
            get, file, api, metadata, content, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}"
        query_params = {
            k: v
            for k, v in [
                ("version", version),
                ("ids", ids),
                ("depth", depth),
                ("geometry", geometry),
                ("plugin_data", plugin_data),
                ("branch_data", branch_data),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_nodes(
        self, file_key, ids, version=None, depth=None, geometry=None, plugin_data=None
    ) -> Any:
        """
        Fetches node data for specified IDs from a file, supporting optional filters such as version, depth, geometry, and plugin data.

        Args:
            file_key: str. The unique key identifying the file to query. Required.
            ids: str or list. The node ID(s) to retrieve from the file. Required.
            version: str or None. Optional file version to query. Defaults to the latest if not specified.
            depth: int or None. Optional depth for retrieving nested node data.
            geometry: str or None. Optional geometry specifier to filter node data.
            plugin_data: str or None. Optional plugin data to include in the response.

        Returns:
            dict. The JSON-decoded response containing node data for the requested IDs.

        Raises:
            ValueError: Raised if 'file_key' or 'ids' is not provided.

        Tags:
            get, fetch, node-data, file, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/v1/files/{file_key}/nodes"
        query_params = {
            k: v
            for k, v in [
                ("ids", ids),
                ("version", version),
                ("depth", depth),
                ("geometry", geometry),
                ("plugin_data", plugin_data),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_images(
        self,
        file_key,
        ids,
        version=None,
        scale=None,
        format=None,
        svg_outline_text=None,
        svg_include_id=None,
        svg_include_node_id=None,
        svg_simplify_stroke=None,
        contents_only=None,
        use_absolute_bounds=None,
    ) -> Any:
        """
        Retrieves image assets from a remote service for specified node IDs within a given file, with optional image format and export options.

        Args:
            file_key: str. Unique key identifying the target file. Required.
            ids: str. Comma-separated list of node IDs to export as images. Required.
            version: str, optional. Specific file version to export from.
            scale: float, optional. Image scaling factor; must be between 0.01 and 4.
            format: str, optional. Output image format (e.g., 'png', 'jpg', 'svg').
            svg_outline_text: bool, optional. If True, outlines text in SVG exports.
            svg_include_id: bool, optional. If True, includes node IDs in SVG elements.
            svg_include_node_id: bool, optional. If True, includes node IDs as attributes in SVG.
            svg_simplify_stroke: bool, optional. If True, simplifies SVG strokes.
            contents_only: bool, optional. If True, exports only node contents without background.
            use_absolute_bounds: bool, optional. If True, uses absolute bounding box for export.

        Returns:
            dict. Parsed JSON response containing image export links and metadata.

        Raises:
            ValueError: Raised if either 'file_key' or 'ids' is not provided.
            requests.HTTPError: Raised if the HTTP request for image assets fails.

        Tags:
            get, images, export, api-call, batch, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/v1/images/{file_key}"
        query_params = {
            k: v
            for k, v in [
                ("ids", ids),
                ("version", version),
                ("scale", scale),
                ("format", format),
                ("svg_outline_text", svg_outline_text),
                ("svg_include_id", svg_include_id),
                ("svg_include_node_id", svg_include_node_id),
                ("svg_simplify_stroke", svg_simplify_stroke),
                ("contents_only", contents_only),
                ("use_absolute_bounds", use_absolute_bounds),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_image_fills(self, file_key) -> Any:
        """
        Retrieves image fill data for a given file key from the API.

        Args:
            file_key: The unique identifier of the file whose image fills are to be retrieved.

        Returns:
            A dictionary or list containing the image fill data as returned by the API.

        Raises:
            ValueError: If 'file_key' is None.
            HTTPError: If the HTTP request to the API fails with an error status.

        Tags:
            get, images, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/images"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_team_projects(self, team_id) -> Any:
        """
        Retrieves the list of projects associated with a specified team.

        Args:
            team_id: The unique identifier of the team whose projects are to be fetched.

        Returns:
            A deserialized JSON object containing the projects for the given team.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to fetch team projects fails.

        Tags:
            get, list, team-projects, management, important
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/v1/teams/{team_id}/projects"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_files(self, project_id, branch_data=None) -> Any:
        """
        Retrieves the list of files associated with a specified project, optionally filtered by branch data.

        Args:
            project_id: The unique identifier for the project whose files are to be retrieved.
            branch_data: Optional branch identifier or data used to filter project files. Defaults to None.

        Returns:
            A JSON-decoded object containing the project's file information as returned by the API.

        Raises:
            ValueError: If the required parameter 'project_id' is not provided.
            requests.HTTPError: If the HTTP request to retrieve the project files fails.

        Tags:
            get, project, files, api, important
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/files"
        query_params = {
            k: v for k, v in [("branch_data", branch_data)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_versions(
        self, file_key, page_size=None, before=None, after=None
    ) -> Any:
        """
        Retrieves a paginated list of version history for a specified file.

        Args:
            file_key: The unique identifier of the file for which to fetch version history.
            page_size: Optional; The maximum number of versions to return per page.
            before: Optional; A version identifier. Only versions created before this version will be returned.
            after: Optional; A version identifier. Only versions created after this version will be returned.

        Returns:
            A JSON-decoded object containing the list of file versions and pagination information.

        Raises:
            ValueError: If 'file_key' is None.
            HTTPError: If the HTTP request to fetch the file versions fails.

        Tags:
            list, file-management, version-history, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/versions"
        query_params = {
            k: v
            for k, v in [("page_size", page_size), ("before", before), ("after", after)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_comments(self, file_key, as_md=None) -> Any:
        """
        Retrieves comments for a specified file, optionally formatting the output as Markdown.

        Args:
            file_key: The unique identifier of the file to fetch comments for.
            as_md: Optional; if specified, comments are returned as Markdown. Default is None.

        Returns:
            A JSON-compatible object containing the file's comments.

        Raises:
            ValueError: Raised if the required parameter 'file_key' is not provided.
            HTTPError: Raised if the HTTP request for fetching comments fails.

        Tags:
            get, comments, file, api, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/comments"
        query_params = {k: v for k, v in [("as_md", as_md)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_comment(self, file_key, message, comment_id=None, client_meta=None) -> Any:
        """
        Posts a comment to a specified file.

        Args:
            file_key: String identifier of the file to which the comment will be posted.
            message: String content of the comment to be posted.
            comment_id: Optional string identifier for the comment, used for threading or replying to existing comments.
            client_meta: Optional dictionary containing client-specific metadata to be associated with the comment.

        Returns:
            Dictionary containing the response data of the created comment from the API.

        Raises:
            ValueError: Raised when required parameters 'file_key' or 'message' are None.
            HTTPError: Raised when the API request fails, as indicated by response.raise_for_status().

        Tags:
            post, comment, file, api, communication, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if message is None:
            raise ValueError("Missing required parameter 'message'")
        request_body = {
            "message": message,
            "comment_id": comment_id,
            "client_meta": client_meta,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/files/{file_key}/comments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_comment(self, file_key, comment_id) -> Any:
        """
        Deletes a specific comment from a file identified by its key and comment ID.

        Args:
            file_key: The unique identifier of the file containing the comment to be deleted. Must not be None.
            comment_id: The unique identifier of the comment to delete. Must not be None.

        Returns:
            The server response as a JSON object containing details of the deletion or confirmation.

        Raises:
            ValueError: If 'file_key' or 'comment_id' is None.
            requests.HTTPError: If the HTTP request to delete the comment fails with a non-success status code.

        Tags:
            delete, comment, file-management, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        url = f"{self.base_url}/v1/files/{file_key}/comments/{comment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_comment_reactions(self, file_key, comment_id, cursor=None) -> Any:
        """
        Retrieves the reactions associated with a specific comment in a file.

        Args:
            file_key: str. The unique identifier of the file containing the comment.
            comment_id: str. The unique identifier of the comment whose reactions are to be retrieved.
            cursor: Optional[str]. A pagination cursor for fetching subsequent pages of reactions. Defaults to None.

        Returns:
            dict. A JSON-decoded dictionary containing the comment reactions data from the API response.

        Raises:
            ValueError: Raised if 'file_key' or 'comment_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status code.

        Tags:
            get, list, reactions, comments, file, api, important
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        url = f"{self.base_url}/v1/files/{file_key}/comments/{comment_id}/reactions"
        query_params = {k: v for k, v in [("cursor", cursor)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_comment_reaction(self, file_key, comment_id, emoji) -> Any:
        """
        Posts a reaction emoji to a specific comment on a file.

        Args:
            file_key: str. Identifier for the file containing the comment.
            comment_id: str. Identifier of the comment to react to.
            emoji: str. The emoji to be used as the reaction.

        Returns:
            dict. The JSON-decoded response from the server after posting the reaction.

        Raises:
            ValueError: Raised if any of the parameters 'file_key', 'comment_id', or 'emoji' are None.
            requests.HTTPError: Raised if the HTTP request to post the reaction fails.

        Tags:
            post, comment, reaction, emoji, async_job, ai
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        if emoji is None:
            raise ValueError("Missing required parameter 'emoji'")
        request_body = {
            "emoji": emoji,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/files/{file_key}/comments/{comment_id}/reactions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_comment_reaction(self, file_key, comment_id, emoji) -> Any:
        """
        Removes a specific emoji reaction from a comment in a file.

        Args:
            file_key: The unique identifier of the file containing the comment.
            comment_id: The unique identifier of the comment whose reaction should be deleted.
            emoji: The emoji reaction to be removed from the comment.

        Returns:
            The parsed JSON response from the API after deleting the reaction.

        Raises:
            ValueError: Raised if 'file_key', 'comment_id', or 'emoji' is None.
            requests.HTTPError: Raised if the HTTP request to delete the reaction fails.

        Tags:
            delete, comment-reaction, management, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        if emoji is None:
            raise ValueError("Missing required parameter 'emoji'")
        url = f"{self.base_url}/v1/files/{file_key}/comments/{comment_id}/reactions"
        query_params = {k: v for k, v in [("emoji", emoji)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_me(
        self,
    ) -> Any:
        """
        Retrieves information about the authenticated user from the API.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the user's information as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the API fails or returns a non-successful status code.

        Tags:
            get, user, profile, api, important
        """
        url = f"{self.base_url}/v1/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_team_components(
        self, team_id, page_size=None, after=None, before=None
    ) -> Any:
        """
        Retrieves a paginated list of components associated with a specified team.

        Args:
            team_id: str. The unique identifier of the team whose components are to be retrieved.
            page_size: Optional[int]. The maximum number of components to return per page.
            after: Optional[str]. A cursor for pagination to fetch results after this value.
            before: Optional[str]. A cursor for pagination to fetch results before this value.

        Returns:
            dict. A JSON-decoded dictionary containing the team components and pagination details.

        Raises:
            ValueError: Raised if 'team_id' is not provided.
            requests.exceptions.HTTPError: Raised if the HTTP request to fetch components fails.

        Tags:
            get, list, components, team, api, pagination
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/v1/teams/{team_id}/components"
        query_params = {
            k: v
            for k, v in [("page_size", page_size), ("after", after), ("before", before)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_components(self, file_key) -> Any:
        """
        Retrieves the component information for a specified file from the API.

        Args:
            file_key: The unique identifier of the file for which to fetch component details.

        Returns:
            A JSON-serializable object containing the components of the specified file.

        Raises:
            ValueError: If 'file_key' is None.
            requests.exceptions.HTTPError: If the HTTP request fails or returns an unsuccessful status code.

        Tags:
            get, file, components, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/components"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_component(self, key) -> Any:
        """
        Retrieves a component's details by its key from the API.

        Args:
            key: The unique identifier for the component to retrieve.

        Returns:
            A dictionary containing the component's details as returned by the API.

        Raises:
            ValueError: Raised if the 'key' parameter is None.
            requests.HTTPError: Raised if the HTTP request fails or the response status indicates an error.

        Tags:
            get, component, api, management
        """
        if key is None:
            raise ValueError("Missing required parameter 'key'")
        url = f"{self.base_url}/v1/components/{key}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_team_component_sets(
        self, team_id, page_size=None, after=None, before=None
    ) -> Any:
        """
        Retrieves a paginated list of component sets for a specified team.

        Args:
            team_id: str. The unique identifier of the team whose component sets are to be retrieved.
            page_size: Optional[int]. The maximum number of results to return per page.
            after: Optional[str]. A cursor for pagination to retrieve results after the specified object.
            before: Optional[str]. A cursor for pagination to retrieve results before the specified object.

        Returns:
            dict. The JSON response containing the list of component sets and any associated pagination metadata.

        Raises:
            ValueError: If 'team_id' is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            list, component-sets, team, api, async-job
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/v1/teams/{team_id}/component_sets"
        query_params = {
            k: v
            for k, v in [("page_size", page_size), ("after", after), ("before", before)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_component_sets(self, file_key) -> Any:
        """
        Retrieves the list of component sets associated with a specific file key.

        Args:
            file_key: The unique identifier of the file whose component sets are to be fetched.

        Returns:
            A JSON-compatible object containing the component sets data for the specified file.

        Raises:
            ValueError: Raised when the required parameter 'file_key' is None.
            requests.HTTPError: Raised if the HTTP request to the remote server fails or returns an unsuccessful status code.

        Tags:
            get, list, component-sets, file, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/component_sets"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_component_set(self, key) -> Any:
        """
        Retrieves a component set resource by its key from the server.

        Args:
            key: The unique identifier (string or compatible) of the component set to retrieve. Must not be None.

        Returns:
            A JSON-decoded object containing the component set data as returned by the server.

        Raises:
            ValueError: If the 'key' parameter is None.
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.

        Tags:
            get, component-set, retrieve, ai
        """
        if key is None:
            raise ValueError("Missing required parameter 'key'")
        url = f"{self.base_url}/v1/component_sets/{key}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_team_styles(self, team_id, page_size=None, after=None, before=None) -> Any:
        """
        Retrieves a list of styles for a specified team, with optional pagination controls.

        Args:
            team_id: str. The unique identifier of the team whose styles are to be retrieved.
            page_size: Optional[int]. The maximum number of style records to return per page.
            after: Optional[str]. A cursor for pagination to retrieve records after a specific point.
            before: Optional[str]. A cursor for pagination to retrieve records before a specific point.

        Returns:
            dict. The JSON response containing the team's styles and pagination information.

        Raises:
            ValueError: If 'team_id' is not provided.
            requests.HTTPError: If the HTTP request fails or returns an error status code.

        Tags:
            get, list, team, styles, pagination, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/v1/teams/{team_id}/styles"
        query_params = {
            k: v
            for k, v in [("page_size", page_size), ("after", after), ("before", before)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file_styles(self, file_key) -> Any:
        """
        Retrieves the style definitions for a specified file from the API.

        Args:
            file_key: The unique identifier of the file whose styles are to be fetched.

        Returns:
            A JSON-serializable object containing the style information of the requested file.

        Raises:
            ValueError: If 'file_key' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            get, file, styles, api, management
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/styles"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_style(self, key) -> Any:
        """
        Retrieves a style resource identified by the given key from the API.

        Args:
            key: The unique identifier of the style to retrieve. Must not be None.

        Returns:
            A dictionary representing the style resource as returned by the API.

        Raises:
            ValueError: If the 'key' parameter is None.
            requests.HTTPError: If the HTTP request to the API fails (non-success status code).

        Tags:
            get, style, api, management, important
        """
        if key is None:
            raise ValueError("Missing required parameter 'key'")
        url = f"{self.base_url}/v1/styles/{key}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_webhook(
        self, event_type, team_id, endpoint, passcode, status=None, description=None
    ) -> Any:
        """
        Registers a new webhook for a specified event type and team.

        Args:
            event_type: str. The type of event that will trigger the webhook. Required.
            team_id: str. The unique identifier of the team to associate with the webhook. Required.
            endpoint: str. The URL endpoint where the webhook payloads will be sent. Required.
            passcode: str. A secret passcode used to secure webhook communication. Required.
            status: Optional[str]. The status of the webhook (e.g., 'active', 'inactive'). Defaults to None.
            description: Optional[str]. A description of the webhook's purpose. Defaults to None.

        Returns:
            dict. The JSON response from the webhook creation API containing details of the registered webhook.

        Raises:
            ValueError: If any of the required parameters ('event_type', 'team_id', 'endpoint', or 'passcode') are missing.
            HTTPError: If the HTTP request to register the webhook fails (non-2xx status code).

        Tags:
            post, webhook, registration, api
        """
        if event_type is None:
            raise ValueError("Missing required parameter 'event_type'")
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if endpoint is None:
            raise ValueError("Missing required parameter 'endpoint'")
        if passcode is None:
            raise ValueError("Missing required parameter 'passcode'")
        request_body = {
            "event_type": event_type,
            "team_id": team_id,
            "endpoint": endpoint,
            "passcode": passcode,
            "status": status,
            "description": description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_webhook(self, webhook_id) -> Any:
        """
        Retrieves the details of a specific webhook by its unique identifier.

        Args:
            webhook_id: The unique identifier of the webhook to retrieve. Must not be None.

        Returns:
            A dictionary containing the webhook details as returned by the API.

        Raises:
            ValueError: If 'webhook_id' is None.
            requests.HTTPError: If the HTTP request to the API fails (non-2xx response).

        Tags:
            get, webhook, api, important
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/v2/webhooks/{webhook_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_webhook(
        self, webhook_id, event_type, endpoint, passcode, status=None, description=None
    ) -> Any:
        """
        Update an existing webhook's configuration with new settings such as event type, endpoint, passcode, status, or description.

        Args:
            webhook_id: The unique identifier of the webhook to update.
            event_type: The type of event that triggers the webhook.
            endpoint: The destination URL that will receive webhook payloads.
            passcode: The security passcode for webhook authentication.
            status: Optional; the activation status of the webhook (e.g., enabled, disabled).
            description: Optional; a human-readable description of the webhook.

        Returns:
            A dictionary containing the JSON response from the server after updating the webhook.

        Raises:
            ValueError: If any of 'webhook_id', 'event_type', 'endpoint', or 'passcode' is None.
            requests.HTTPError: If the server responds with an HTTP error status code.

        Tags:
            update, webhook, management, api
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        if event_type is None:
            raise ValueError("Missing required parameter 'event_type'")
        if endpoint is None:
            raise ValueError("Missing required parameter 'endpoint'")
        if passcode is None:
            raise ValueError("Missing required parameter 'passcode'")
        request_body = {
            "event_type": event_type,
            "endpoint": endpoint,
            "passcode": passcode,
            "status": status,
            "description": description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/webhooks/{webhook_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_webhook(self, webhook_id) -> Any:
        """
        Deletes a webhook with the specified webhook ID.

        Args:
            webhook_id: str. The unique identifier of the webhook to delete.

        Returns:
            dict. The JSON response from the server after successful deletion.

        Raises:
            ValueError: If 'webhook_id' is None.
            HTTPError: If the HTTP request to delete the webhook fails.

        Tags:
            delete, webhook, management, api
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/v2/webhooks/{webhook_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_team_webhooks(self, team_id) -> Any:
        """
        Retrieves the list of webhooks configured for a given team.

        Args:
            team_id: The unique identifier of the team whose webhooks are to be fetched.

        Returns:
            A JSON-decoded object containing the team's webhook configurations.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to fetch webhooks fails.

        Tags:
            get, webhooks, team, api, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/v2/teams/{team_id}/webhooks"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_webhook_requests(self, webhook_id) -> Any:
        """
        Retrieves the list of requests for a specified webhook.

        Args:
            webhook_id: The unique identifier of the webhook for which to retrieve requests.

        Returns:
            A JSON-decoded object containing the list of requests associated with the webhook.

        Raises:
            ValueError: If 'webhook_id' is None.
            requests.HTTPError: If the HTTP request to the webhook endpoint fails.

        Tags:
            get, webhook, requests, api
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/v2/webhooks/{webhook_id}/requests"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_activity_logs(
        self, events=None, start_time=None, end_time=None, limit=None, order=None
    ) -> Any:
        """
        Retrieves activity logs from the API with optional filters for events, time range, limit, and order.

        Args:
            events: Optional; a filter specifying which event types to include in the logs.
            start_time: Optional; the start of the time range (ISO 8601 format) for fetching logs.
            end_time: Optional; the end of the time range (ISO 8601 format) for fetching logs.
            limit: Optional; the maximum number of log records to retrieve.
            order: Optional; the order to sort the logs, such as 'asc' or 'desc'.

        Returns:
            A JSON-decoded object containing the retrieved activity logs.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            get, list, logs, activity, filter, api
        """
        url = f"{self.base_url}/v1/activity_logs"
        query_params = {
            k: v
            for k, v in [
                ("events", events),
                ("start_time", start_time),
                ("end_time", end_time),
                ("limit", limit),
                ("order", order),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_payments(
        self,
        plugin_payment_token=None,
        user_id=None,
        community_file_id=None,
        plugin_id=None,
        widget_id=None,
    ) -> Any:
        """
        Retrieves a list of payments based on the provided filter criteria.

        Args:
            plugin_payment_token: Optional; unique token identifying the plugin payment. Used to filter results to payments associated with this token.
            user_id: Optional; unique user identifier. Limits results to payments related to this user.
            community_file_id: Optional; unique community file identifier. Filters payments associated with this file.
            plugin_id: Optional; unique plugin identifier. Filters payments related to this plugin.
            widget_id: Optional; unique widget identifier. Restricts results to payments linked to this widget.

        Returns:
            A JSON-compatible object containing the list of payments matching the specified filters.

        Raises:
            HTTPError: If the HTTP request to the payments endpoint fails (e.g., server error, authentication failure, or invalid request).

        Tags:
            get, payments, list, filter, api
        """
        url = f"{self.base_url}/v1/payments"
        query_params = {
            k: v
            for k, v in [
                ("plugin_payment_token", plugin_payment_token),
                ("user_id", user_id),
                ("community_file_id", community_file_id),
                ("plugin_id", plugin_id),
                ("widget_id", widget_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_local_variables(self, file_key) -> Any:
        """
        Retrieves the local variables associated with a specific file identified by file_key.

        Args:
            file_key: The unique identifier of the file whose local variables are to be retrieved.

        Returns:
            A JSON-compatible object containing the local variables for the specified file.

        Raises:
            ValueError: Raised if the file_key parameter is None, indicating a missing required parameter.
            HTTPError: Raised if the HTTP request to fetch local variables fails due to a non-successful response status.

        Tags:
            get, variables, file, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/variables/local"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_published_variables(self, file_key) -> Any:
        """
        Retrieves the published variables associated with a specified file key from the server.

        Args:
            file_key: The unique identifier of the file whose published variables are to be fetched.

        Returns:
            A JSON-deserialized object containing the published variables for the specified file.

        Raises:
            ValueError: Raised if 'file_key' is None.
            requests.HTTPError: Raised if the HTTP request to fetch the published variables fails with a non-success status code.

        Tags:
            get, variables, file-management, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/variables/published"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_variables(
        self,
        file_key,
        variableCollections=None,
        variableModes=None,
        variables=None,
        variableModeValues=None,
    ) -> Any:
        """
        Posts or updates variable data for a specified file by sending a POST request to the variables endpoint.

        Args:
            file_key: The unique identifier of the file for which variables are being set or modified. Must not be None.
            variableCollections: Optional; a collection or list of variable groups to include in the request body.
            variableModes: Optional; a set or list describing variable modes to be associated with the file.
            variables: Optional; a dictionary or list containing individual variable definitions to include.
            variableModeValues: Optional; a mapping of variable modes to their corresponding values.

        Returns:
            The JSON-decoded response from the variables API, typically containing the status or result of the operation.

        Raises:
            ValueError: If 'file_key' is None.
            requests.HTTPError: If the HTTP request to the server fails or the response indicates an error status.

        Tags:
            post, variables, management, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        request_body = {
            "variableCollections": variableCollections,
            "variableModes": variableModes,
            "variables": variables,
            "variableModeValues": variableModeValues,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/files/{file_key}/variables"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_dev_resources(self, file_key, node_ids=None) -> Any:
        """
        Retrieves development resources for a specific file.

        Args:
            file_key: String identifier for the file to retrieve development resources from.
            node_ids: Optional list of node identifiers to filter the development resources by.

        Returns:
            JSON object containing the development resources for the specified file.

        Raises:
            ValueError: Raised when the required 'file_key' parameter is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).

        Tags:
            retrieve, get, file, resources, development, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        url = f"{self.base_url}/v1/files/{file_key}/dev_resources"
        query_params = {k: v for k, v in [("node_ids", node_ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_dev_resources(self, dev_resources) -> Any:
        """
        Submits developer resources to the API and returns the parsed JSON response.

        Args:
            dev_resources: The developer resources to be submitted to the API. Must not be None.

        Returns:
            dict: The JSON-decoded response from the API after submitting the developer resources.

        Raises:
            ValueError: Raised when the required parameter 'dev_resources' is None.
            requests.HTTPError: Raised if the API request results in an HTTP error status.

        Tags:
            post, dev-resources, api, http
        """
        if dev_resources is None:
            raise ValueError("Missing required parameter 'dev_resources'")
        request_body = {
            "dev_resources": dev_resources,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/dev_resources"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_dev_resources(self, dev_resources) -> Any:
        """
        Updates the development resources by sending a PUT request to the dev_resources endpoint.

        Args:
            dev_resources: The development resources data to be updated. This must not be None.

        Returns:
            The parsed JSON response from the server as a dictionary or relevant data structure.

        Raises:
            ValueError: If the 'dev_resources' parameter is None.
            requests.HTTPError: If the HTTP request fails or returns a non-success status code.

        Tags:
            put, dev-resources, update, api
        """
        if dev_resources is None:
            raise ValueError("Missing required parameter 'dev_resources'")
        request_body = {
            "dev_resources": dev_resources,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/dev_resources"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_dev_resource(self, file_key, dev_resource_id) -> Any:
        """
        Deletes a specific development resource associated with a file.

        Args:
            file_key: The unique identifier for the file containing the development resource.
            dev_resource_id: The unique identifier of the development resource to delete.

        Returns:
            The parsed JSON response from the API after successful deletion of the development resource.

        Raises:
            ValueError: Raised if either 'file_key' or 'dev_resource_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the development resource fails.

        Tags:
            delete, dev-resource, management, api
        """
        if file_key is None:
            raise ValueError("Missing required parameter 'file_key'")
        if dev_resource_id is None:
            raise ValueError("Missing required parameter 'dev_resource_id'")
        url = f"{self.base_url}/v1/files/{file_key}/dev_resources/{dev_resource_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_file,
            self.get_file_nodes,
            self.get_images,
            self.get_image_fills,
            self.get_team_projects,
            self.get_project_files,
            self.get_file_versions,
            self.get_comments,
            self.post_comment,
            self.delete_comment,
            self.get_comment_reactions,
            self.post_comment_reaction,
            self.delete_comment_reaction,
            self.get_me,
            self.get_team_components,
            self.get_file_components,
            self.get_component,
            self.get_team_component_sets,
            self.get_file_component_sets,
            self.get_component_set,
            self.get_team_styles,
            self.get_file_styles,
            self.get_style,
            self.post_webhook,
            self.get_webhook,
            self.put_webhook,
            self.delete_webhook,
            self.get_team_webhooks,
            self.get_webhook_requests,
            self.get_activity_logs,
            self.get_payments,
            self.get_local_variables,
            self.get_published_variables,
            self.post_variables,
            self.get_dev_resources,
            self.post_dev_resources,
            self.put_dev_resources,
            self.delete_dev_resource,
        ]
