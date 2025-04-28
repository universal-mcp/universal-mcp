from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class NeonApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='neon', integration=integration, **kwargs)
        self.base_url = "https://console.neon.tech/api/v2"

    def list_api_keys(self, ) -> list[Any]:
        """
        Retrieves a list of API keys from the server associated with the current client.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A list of API key objects parsed from the server's JSON response.
        
        Raises:
            requests.HTTPError: Raised if the HTTP response indicates an unsuccessful status code.
        
        Tags:
            list, api-keys, management
        """
        url = f"{self.base_url}/api_keys"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_api_key(self, key_name) -> dict[str, Any]:
        """
        Creates a new API key with the specified name.
        
        Args:
            key_name: The name to assign to the new API key. Cannot be None.
        
        Returns:
            A dictionary containing the created API key details and metadata.
        
        Raises:
            ValueError: Raised when 'key_name' is None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            create, api, authentication, management
        """
        if key_name is None:
            raise ValueError("Missing required parameter 'key_name'")
        request_body = {
            'key_name': key_name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api_keys"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def revoke_api_key(self, key_id) -> dict[str, Any]:
        """
        Revokes an API key by its identifier.
        
        Args:
            key_id: The unique identifier of the API key to be revoked.
        
        Returns:
            A dictionary containing the response data from the API after revocation.
        
        Raises:
            ValueError: If 'key_id' is None.
            requests.HTTPError: If the API request fails with a non-success status code.
        
        Tags:
            revoke, api-key, management
        """
        if key_id is None:
            raise ValueError("Missing required parameter 'key_id'")
        url = f"{self.base_url}/api_keys/{key_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_operation(self, project_id, operation_id) -> dict[str, Any]:
        """
        Retrieves details of a specific operation for a given project from the API.
        
        Args:
            project_id: str. The unique identifier of the project for which the operation details are requested.
            operation_id: str. The unique identifier of the operation to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing the operation information returned by the API.
        
        Raises:
            ValueError: Raised if 'project_id' or 'operation_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status code.
        
        Tags:
            get, operation, project-management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if operation_id is None:
            raise ValueError("Missing required parameter 'operation_id'")
        url = f"{self.base_url}/projects/{project_id}/operations/{operation_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_projects(self, cursor=None, limit=None, search=None, org_id=None, timeout=None) -> Any:
        """
        Retrieves a list of projects with optional pagination, filtering, and organizational scoping.
        
        Args:
            cursor: A string representing the pagination cursor to fetch the next set of results. Optional.
            limit: An integer specifying the maximum number of projects to return. Optional.
            search: A string to filter projects by a search term. Optional.
            org_id: A string representing the organization ID to filter projects belonging to a specific organization. Optional.
            timeout: An integer representing the request timeout in seconds. Optional.
        
        Returns:
            A JSON-decoded Python object containing the list of projects and associated metadata.
        
        Raises:
            requests.HTTPError: If the HTTP request to retrieve the projects fails or returns an error status code.
        
        Tags:
            list, projects, search, filter, pagination, management, important
        """
        url = f"{self.base_url}/projects"
        query_params = {k: v for k, v in [('cursor', cursor), ('limit', limit), ('search', search), ('org_id', org_id), ('timeout', timeout)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_project(self, project) -> Any:
        """
        Creates a new project by sending a POST request to the projects endpoint with the given project details.
        
        Args:
            project: The project data to be created. Must not be None.
        
        Returns:
            The JSON response from the server containing the created project's details.
        
        Raises:
            ValueError: If the 'project' parameter is None.
            requests.HTTPError: If the HTTP request to create the project fails with a non-success status code.
        
        Tags:
            create, project-management, api
        """
        if project is None:
            raise ValueError("Missing required parameter 'project'")
        request_body = {
            'project': project,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_shared_projects(self, cursor=None, limit=None, search=None) -> Any:
        """
        Retrieves a list of shared projects with optional pagination and search filtering.
        
        Args:
            cursor: Optional; a pagination token indicating where to continue retrieving results.
            limit: Optional; the maximum number of projects to return.
            search: Optional; a string to filter projects by name or other searchable fields.
        
        Returns:
            A JSON-decoded Python object containing the shared projects list and associated metadata.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the server returns an unsuccessful status code.
        
        Tags:
            list, projects, shared, search, api, important
        """
        url = f"{self.base_url}/projects/shared"
        query_params = {k: v for k, v in [('cursor', cursor), ('limit', limit), ('search', search)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project(self, project_id) -> dict[str, Any]:
        """
        Retrieves detailed information for a specific project by its project ID.
        
        Args:
            project_id: The unique identifier of the project to retrieve.
        
        Returns:
            A dictionary containing the project's details as returned by the API.
        
        Raises:
            ValueError: If 'project_id' is None.
            requests.HTTPError: If the HTTP request for the project fails with an error status.
        
        Tags:
            get, project, management, api, important
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_project(self, project_id, project) -> Any:
        """
        Updates an existing project with new information using a PATCH request.
        
        Args:
            project_id: The unique identifier of the project to update.
            project: A dictionary or object containing the updated project data.
        
        Returns:
            A dictionary containing the updated project details as received from the API response.
        
        Raises:
            ValueError: Raised if 'project_id' or 'project' is None.
            requests.HTTPError: Raised if the API request fails or returns an error status code.
        
        Tags:
            update, project-management, api, patch
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if project is None:
            raise ValueError("Missing required parameter 'project'")
        request_body = {
            'project': project,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project(self, project_id) -> dict[str, Any]:
        """
        Deletes a project identified by the given project_id.
        
        Args:
            project_id: The unique identifier of the project to be deleted.
        
        Returns:
            A dictionary containing the response data from the delete operation.
        
        Raises:
            ValueError: If the project_id parameter is None.
            requests.HTTPError: If the HTTP request to delete the project fails.
        
        Tags:
            delete, project-management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_operations(self, project_id, cursor=None, limit=None) -> Any:
        """
        Retrieves a paginated list of operations for a specified project.
        
        Args:
            project_id: The unique identifier of the project whose operations are to be listed.
            cursor: An optional pagination cursor indicating the position to start retrieving operations from. Defaults to None.
            limit: An optional maximum number of operations to return in the response. Defaults to None.
        
        Returns:
            A JSON-decoded object containing the list of operations and related pagination information.
        
        Raises:
            ValueError: If the required parameter 'project_id' is not provided.
            requests.HTTPError: If the HTTP request to retrieve operations fails.
        
        Tags:
            list, project-management, operations, api, async-job, important
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}/operations"
        query_params = {k: v for k, v in [('cursor', cursor), ('limit', limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_permissions(self, project_id) -> dict[str, Any]:
        """
        Retrieves the permissions assigned to a specific project.
        
        Args:
            project_id: The unique identifier of the project for which to list permissions.
        
        Returns:
            A dictionary containing the project's permissions as returned by the API.
        
        Raises:
            ValueError: If 'project_id' is None.
            requests.HTTPError: If the HTTP request to fetch permissions fails.
        
        Tags:
            list, permissions, project, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}/permissions"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def grant_permission_to_project(self, project_id, email) -> dict[str, Any]:
        """
        Grants a user permission to a specified project by sending a POST request with the user's email.
        
        Args:
            project_id: The unique identifier of the project to which the permission will be granted. Must not be None.
            email: The email address of the user to grant permission to. Must not be None.
        
        Returns:
            A dictionary containing the JSON response from the permission grant request.
        
        Raises:
            ValueError: Raised if 'project_id' or 'email' is None.
            requests.HTTPError: Raised if the HTTP request for granting permission fails with a non-success status code.
        
        Tags:
            grant, permission, project-management, api, post-request
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        request_body = {
            'email': email,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/permissions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def revoke_permission_from_project(self, project_id, permission_id) -> dict[str, Any]:
        """
        Revokes a specific permission from a project by sending a DELETE request to the appropriate API endpoint.
        
        Args:
            project_id: The unique identifier of the project from which the permission will be revoked.
            permission_id: The unique identifier of the permission to be revoked from the project.
        
        Returns:
            A dictionary containing the response data from the API after successfully revoking the permission.
        
        Raises:
            ValueError: Raised if either 'project_id' or 'permission_id' is None.
            HTTPError: Raised if the API request fails with an HTTP error response.
        
        Tags:
            revoke, permission, project, api, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if permission_id is None:
            raise ValueError("Missing required parameter 'permission_id'")
        url = f"{self.base_url}/projects/{project_id}/permissions/{permission_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_jwks(self, project_id) -> dict[str, Any]:
        """
        Retrieves the JSON Web Key Set (JWKS) for a specified project from the server.
        
        Args:
            project_id: The unique identifier of the project for which to fetch the JWKS.
        
        Returns:
            A dictionary representing the project's JWKS as obtained from the server response.
        
        Raises:
            ValueError: If 'project_id' is None.
            requests.HTTPError: If the HTTP request to fetch the JWKS fails with a non-success status code.
        
        Tags:
            get, jwks, project, http, fetch
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}/jwks"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_project_jwks(self, project_id, jwks_url, provider_name, branch_id=None, jwt_audience=None, role_names=None) -> dict[str, Any]:
        """
        Adds a JWKS (JSON Web Key Set) provider to the specified project for authentication integration.
        
        Args:
            project_id: str. Unique identifier of the project to which the JWKS provider will be added.
            jwks_url: str. The URL where the JWKS is hosted.
            provider_name: str. Name of the authentication provider.
            branch_id: Optional[str]. Identifier for the project branch, if applicable.
            jwt_audience: Optional[str]. Expected audience (aud) claim for JWT validation.
            role_names: Optional[list[str]]. List of role names to associate with this provider.
        
        Returns:
            dict[str, Any]: Response data from the server as a dictionary representation of the added JWKS provider.
        
        Raises:
            ValueError: Raised if any of the required parameters ('project_id', 'jwks_url', or 'provider_name') are missing.
            requests.HTTPError: Raised if the HTTP request to add the JWKS provider fails with a non-2xx status code.
        
        Tags:
            add, jwks, authentication, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if jwks_url is None:
            raise ValueError("Missing required parameter 'jwks_url'")
        if provider_name is None:
            raise ValueError("Missing required parameter 'provider_name'")
        request_body = {
            'jwks_url': jwks_url,
            'provider_name': provider_name,
            'branch_id': branch_id,
            'jwt_audience': jwt_audience,
            'role_names': role_names,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/jwks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_jwks(self, project_id, jwks_id) -> dict[str, Any]:
        """
        Deletes a JSON Web Key Set (JWKS) associated with a specific project.
        
        Args:
            project_id: The unique identifier of the project containing the JWKS to be deleted.
            jwks_id: The unique identifier of the JWKS to delete.
        
        Returns:
            A dictionary containing the server's response to the delete operation.
        
        Raises:
            ValueError: Raised if 'project_id' or 'jwks_id' is not provided.
            requests.HTTPError: Raised if the HTTP request for deletion fails with an unsuccessful status code.
        
        Tags:
            delete, jwks, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if jwks_id is None:
            raise ValueError("Missing required parameter 'jwks_id'")
        url = f"{self.base_url}/projects/{project_id}/jwks/{jwks_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_connection_uri(self, project_id, database_name, role_name, branch_id=None, endpoint_id=None, pooled=None) -> dict[str, Any]:
        """
        Retrieves the connection URI details for a specified database and role within a project.
        
        Args:
            project_id: str. The unique identifier of the project. Required.
            database_name: str. The name of the database for which to retrieve the connection URI. Required.
            role_name: str. The name of the role to use for the connection. Required.
            branch_id: str or None. Optional branch identifier to narrow down the connection URI.
            endpoint_id: str or None. Optional endpoint identifier for targeted connection URI retrieval.
            pooled: bool or None. Whether to request a pooled database connection. Optional.
        
        Returns:
            dict. A JSON response containing the connection URI and related connection details.
        
        Raises:
            ValueError: If any of 'project_id', 'database_name', or 'role_name' is None.
            HTTPError: If the HTTP request to retrieve the connection URI fails (propagated from the requests library).
        
        Tags:
            get, connection-uri, database, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if database_name is None:
            raise ValueError("Missing required parameter 'database_name'")
        if role_name is None:
            raise ValueError("Missing required parameter 'role_name'")
        url = f"{self.base_url}/projects/{project_id}/connection_uri"
        query_params = {k: v for k, v in [('branch_id', branch_id), ('endpoint_id', endpoint_id), ('database_name', database_name), ('role_name', role_name), ('pooled', pooled)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_branch(self, project_id, branch_id) -> Any:
        """
        Retrieves details of a specific branch within a project by project and branch ID.
        
        Args:
            project_id: The unique identifier of the project containing the branch.
            branch_id: The unique identifier of the branch to retrieve.
        
        Returns:
            A JSON-decoded object containing information about the specified branch.
        
        Raises:
            ValueError: Raised if 'project_id' or 'branch_id' is None.
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            get, branch, project, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_branch(self, project_id, branch_id) -> dict[str, Any]:
        """
        Deletes a specific branch from the given project using the API.
        
        Args:
            project_id: The unique identifier of the project containing the branch to delete.
            branch_id: The unique identifier of the branch to be deleted.
        
        Returns:
            A dictionary containing the API response data after deleting the branch.
        
        Raises:
            ValueError: Raised if 'project_id' or 'branch_id' is None.
            requests.HTTPError: Raised if the API request fails with an unsuccessful HTTP status code.
        
        Tags:
            delete, branch-management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_project_branch(self, project_id, branch_id, branch) -> dict[str, Any]:
        """
        Updates a branch in the specified project.
        
        Args:
            project_id: The unique identifier of the project containing the branch to update.
            branch_id: The unique identifier of the branch to update.
            branch: The updated branch data to apply.
        
        Returns:
            A dictionary containing the updated branch information.
        
        Raises:
            ValueError: If any of the required parameters (project_id, branch_id, branch) are None.
            HTTPError: If the API request fails.
        
        Tags:
            update, branch, project, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if branch is None:
            raise ValueError("Missing required parameter 'branch'")
        request_body = {
            'branch': branch,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def restore_project_branch(self, project_id, branch_id, source_branch_id, source_lsn=None, source_timestamp=None, preserve_under_name=None) -> dict[str, Any]:
        """
        Restores a project branch from a given source branch, allowing optional point-in-time recovery and name preservation.
        
        Args:
            project_id: str. The unique identifier of the project containing the branch to be restored.
            branch_id: str. The unique identifier of the target branch to restore.
            source_branch_id: str. The identifier of the source branch from which to restore.
            source_lsn: Optional[int|str]. The log sequence number to restore from. If None, restores from the latest available state.
            source_timestamp: Optional[str]. The timestamp to restore from (in ISO 8601 format). If None, restores from the latest available state.
            preserve_under_name: Optional[str]. If specified, preserves the previous branch contents under this name before restoring.
        
        Returns:
            dict[str, Any]: The JSON response from the server containing details about the restored branch operation.
        
        Raises:
            ValueError: If any of 'project_id', 'branch_id', or 'source_branch_id' is None.
            requests.HTTPError: If the server responds with an HTTP error status code.
        
        Tags:
            restore, branch-management, project
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if source_branch_id is None:
            raise ValueError("Missing required parameter 'source_branch_id'")
        request_body = {
            'source_branch_id': source_branch_id,
            'source_lsn': source_lsn,
            'source_timestamp': source_timestamp,
            'preserve_under_name': preserve_under_name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/restore"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_branch_schema(self, project_id, branch_id, db_name, lsn=None, timestamp=None) -> dict[str, Any]:
        """
        Retrieves the schema information for a specific project branch database, optionally at a given LSN or timestamp.
        
        Args:
            project_id: str. The unique identifier of the project whose branch schema is to be retrieved.
            branch_id: str. The unique identifier of the branch within the project.
            db_name: str. The name of the database within the specified branch.
            lsn: Optional[str]. The log sequence number for which to retrieve the schema snapshot. If not provided, the current schema is returned.
            timestamp: Optional[str]. The timestamp at which to retrieve the schema. If not provided, the current schema is returned.
        
        Returns:
            dict[str, Any]: A dictionary containing the branch schema information retrieved from the API.
        
        Raises:
            ValueError: If any of the required parameters (project_id, branch_id, db_name) are None.
            requests.HTTPError: If the underlying HTTP request fails or returns an unsuccessful status code.
        
        Tags:
            get, schema, project, branch, database, api, fetch
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if db_name is None:
            raise ValueError("Missing required parameter 'db_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/schema"
        query_params = {k: v for k, v in [('db_name', db_name), ('lsn', lsn), ('timestamp', timestamp)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def set_default_project_branch(self, project_id, branch_id) -> dict[str, Any]:
        """
        Sets the specified branch as the default branch for a given project.
        
        Args:
            project_id: The unique identifier of the project whose default branch is to be set.
            branch_id: The unique identifier of the branch to be set as default for the project.
        
        Returns:
            A dictionary containing the API response data confirming the operation.
        
        Raises:
            ValueError: Raised if 'project_id' or 'branch_id' is None.
            requests.HTTPError: Raised if the HTTP request to set the default branch fails.
        
        Tags:
            set, project-management, branch, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/set_as_default"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_branch_endpoints(self, project_id, branch_id) -> dict[str, Any]:
        """
        Retrieves a list of endpoint configurations for a specific branch within a project.
        
        Args:
            project_id: str. The unique identifier of the project whose branch endpoints are to be listed.
            branch_id: str. The unique identifier of the branch for which endpoints will be retrieved.
        
        Returns:
            dict. A dictionary containing the endpoint configurations for the specified branch.
        
        Raises:
            ValueError: Raised if either 'project_id' or 'branch_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve endpoints fails.
        
        Tags:
            list, branch, projects, endpoint, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/endpoints"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_branch_databases(self, project_id, branch_id) -> dict[str, Any]:
        """
        Retrieves a list of databases for a specific branch within a project.
        
        Args:
            project_id: The unique identifier of the project containing the branch.
            branch_id: The unique identifier of the branch whose databases are to be listed.
        
        Returns:
            A dictionary containing the retrieved list of databases and associated metadata for the specified project branch.
        
        Raises:
            ValueError: Raised if 'project_id' or 'branch_id' is None.
            HTTPError: Raised if the HTTP request to retrieve the databases fails.
        
        Tags:
            list, databases, project-management, branch-management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/databases"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_project_branch_database(self, project_id, branch_id, database) -> dict[str, Any]:
        """
        Creates a new database in the specified branch of a project and returns the resulting database object.
        
        Args:
            project_id: The unique identifier of the project in which to create the database.
            branch_id: The unique identifier of the branch within the project where the database will be created.
            database: A dictionary containing the database configuration and properties to be created.
        
        Returns:
            A dictionary representation of the created database object as returned by the API.
        
        Raises:
            ValueError: If project_id, branch_id, or database is None.
            requests.HTTPError: If the HTTP request to create the database fails.
        
        Tags:
            create, database, project-management, branch, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if database is None:
            raise ValueError("Missing required parameter 'database'")
        request_body = {
            'database': database,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/databases"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_branch_database(self, project_id, branch_id, database_name) -> dict[str, Any]:
        """
        Retrieves details of a specific database from a given project branch.
        
        Args:
            project_id: The unique identifier of the project containing the branch.
            branch_id: The unique identifier of the branch within the project.
            database_name: The name of the database to retrieve information for.
        
        Returns:
            A dictionary containing the JSON response with the requested database details.
        
        Raises:
            ValueError: Raised if any of the 'project_id', 'branch_id', or 'database_name' parameters are None.
            requests.HTTPError: Raised if the HTTP request to retrieve the database details fails.
        
        Tags:
            get, database, project-management, branch, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if database_name is None:
            raise ValueError("Missing required parameter 'database_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/databases/{database_name}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_project_branch_database(self, project_id, branch_id, database_name, database) -> dict[str, Any]:
        """
        Updates the specified database configuration for a given branch in a project.
        
        Args:
            project_id: str. Unique identifier of the project.
            branch_id: str. Identifier of the branch within the project.
            database_name: str. The name of the database to update.
            database: Any. The new configuration or content for the database.
        
        Returns:
            dict[str, Any]: A dictionary containing the server's JSON response after updating the database.
        
        Raises:
            ValueError: Raised if any of the parameters 'project_id', 'branch_id', 'database_name', or 'database' are missing or None.
            requests.HTTPError: Raised if the HTTP PATCH request fails or returns an unsuccessful status code.
        
        Tags:
            update, database, project, branch, api, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if database_name is None:
            raise ValueError("Missing required parameter 'database_name'")
        if database is None:
            raise ValueError("Missing required parameter 'database'")
        request_body = {
            'database': database,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/databases/{database_name}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_branch_database(self, project_id, branch_id, database_name) -> dict[str, Any]:
        """
        Deletes a specific database from a project's branch and returns the response details.
        
        Args:
            project_id: The unique identifier of the project containing the database to delete.
            branch_id: The unique identifier of the branch from which the database will be deleted.
            database_name: The name of the database to be deleted.
        
        Returns:
            A dictionary containing the server's response to the delete operation.
        
        Raises:
            ValueError: Raised if 'project_id', 'branch_id', or 'database_name' is None.
            requests.HTTPError: Raised if the HTTP request to delete the database fails.
        
        Tags:
            delete, database, branch, project, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if database_name is None:
            raise ValueError("Missing required parameter 'database_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/databases/{database_name}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_branch_roles(self, project_id, branch_id) -> dict[str, Any]:
        """
        Retrieve the list of roles associated with a specific branch in a given project.
        
        Args:
            project_id: str. The unique identifier of the project whose branch roles are to be listed.
            branch_id: str. The unique identifier of the branch within the project.
        
        Returns:
            dict[str, Any]: A dictionary containing role information for the specified branch.
        
        Raises:
            ValueError: Raised if 'project_id' or 'branch_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve branch roles fails.
        
        Tags:
            list, branch, roles, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/roles"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_project_branch_role(self, project_id, branch_id, role) -> dict[str, Any]:
        """
        Creates a new role for a specific branch within a project and returns the created role information.
        
        Args:
            project_id: The unique identifier of the project.
            branch_id: The unique identifier of the branch within the project.
            role: The role object or specification to be assigned to the branch.
        
        Returns:
            A dictionary containing the details of the created branch role.
        
        Raises:
            ValueError: If any of the required parameters ('project_id', 'branch_id', or 'role') are missing.
            requests.HTTPError: If the HTTP request to create the branch role fails (non-2xx status code).
        
        Tags:
            create, role-management, project, branch
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if role is None:
            raise ValueError("Missing required parameter 'role'")
        request_body = {
            'role': role,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/roles"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_branch_role(self, project_id, branch_id, role_name) -> dict[str, Any]:
        """
        Retrieves a specific role from a project branch.
        
        Args:
            project_id: The unique identifier of the project.
            branch_id: The unique identifier of the branch within the project.
            role_name: The name of the role to retrieve.
        
        Returns:
            A dictionary containing the role details and attributes.
        
        Raises:
            ValueError: Raised when any of the required parameters (project_id, branch_id, or role_name) is None.
            HTTPError: Raised when the HTTP request fails.
        
        Tags:
            get, retrieve, role, management, project, branch
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if role_name is None:
            raise ValueError("Missing required parameter 'role_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/roles/{role_name}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_branch_role(self, project_id, branch_id, role_name) -> dict[str, Any]:
        """
        Deletes a specific role from a branch within a project.
        
        Args:
            project_id: The unique identifier of the project containing the branch.
            branch_id: The identifier of the branch from which the role will be deleted.
            role_name: The name of the role to be deleted from the specified branch.
        
        Returns:
            A dictionary containing the response data from the server after successfully deleting the role.
        
        Raises:
            ValueError: Raised if any of the required parameters ('project_id', 'branch_id', or 'role_name') is None.
            requests.HTTPError: Raised if the HTTP request to delete the role fails.
        
        Tags:
            delete, role-management, project, branch, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if role_name is None:
            raise ValueError("Missing required parameter 'role_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/roles/{role_name}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_branch_role_password(self, project_id, branch_id, role_name) -> dict[str, Any]:
        """
        Retrieves the revealed password for a specified role within a project branch.
        
        Args:
            project_id: The unique identifier of the project whose branch role password is to be retrieved.
            branch_id: The unique identifier of the branch within the project.
            role_name: The name of the role for which the password should be revealed.
        
        Returns:
            A dictionary containing the revealed password and related information for the specified role.
        
        Raises:
            ValueError: Raised if any of the required parameters ('project_id', 'branch_id', or 'role_name') are None.
            requests.HTTPError: Raised if the HTTP request fails with a non-success status code.
        
        Tags:
            get, retrieve, role-management, password, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if role_name is None:
            raise ValueError("Missing required parameter 'role_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/roles/{role_name}/reveal_password"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reset_project_branch_role_password(self, project_id, branch_id, role_name) -> dict[str, Any]:
        """
        Resets the password for a specific role in a project branch.
        
        Args:
            project_id: The unique identifier of the project whose branch role password is to be reset.
            branch_id: The unique identifier of the branch within the project.
            role_name: The name of the role whose password will be reset.
        
        Returns:
            A dictionary containing the response data from the password reset operation.
        
        Raises:
            ValueError: Raised if 'project_id', 'branch_id', or 'role_name' is None.
            HTTPError: Raised if the HTTP request to reset the password fails.
        
        Tags:
            reset, role-management, project, branch, password, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        if role_name is None:
            raise ValueError("Missing required parameter 'role_name'")
        url = f"{self.base_url}/projects/{project_id}/branches/{branch_id}/roles/{role_name}/reset_password"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_vpcendpoints(self, project_id) -> dict[str, Any]:
        """
        Retrieves a list of VPC endpoints associated with a specific project.
        
        Args:
            project_id: The unique identifier of the project for which to retrieve VPC endpoints.
        
        Returns:
            A dictionary containing the VPC endpoints data for the specified project.
        
        Raises:
            ValueError: If 'project_id' is None.
            requests.HTTPError: If the HTTP request to retrieve VPC endpoints fails.
        
        Tags:
            list, vpc-endpoints, project, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}/vpc-endpoints"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def assign_project_vpcendpoint(self, project_id, vpc_endpoint_id, label) -> Any:
        """
        Assigns a VPC endpoint to a project with a specified label and returns the server response.
        
        Args:
            project_id: str. The unique identifier of the project to which the VPC endpoint will be assigned.
            vpc_endpoint_id: str. The unique identifier of the VPC endpoint to be assigned to the project.
            label: str. The label to associate with the assigned VPC endpoint.
        
        Returns:
            dict. The JSON response from the server after assigning the VPC endpoint to the project.
        
        Raises:
            ValueError: Raised if any of 'project_id', 'vpc_endpoint_id', or 'label' is None.
            requests.HTTPError: Raised if the HTTP request to assign the VPC endpoint fails (non-2xx response).
        
        Tags:
            assign, vpc-endpoint, project, management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if vpc_endpoint_id is None:
            raise ValueError("Missing required parameter 'vpc_endpoint_id'")
        if label is None:
            raise ValueError("Missing required parameter 'label'")
        request_body = {
            'label': label,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/vpc-endpoints/{vpc_endpoint_id}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_vpcendpoint(self, project_id, vpc_endpoint_id) -> Any:
        """
        Deletes a VPC endpoint associated with a given project.
        
        Args:
            project_id: The unique identifier of the project containing the VPC endpoint to delete.
            vpc_endpoint_id: The unique identifier of the VPC endpoint to be deleted.
        
        Returns:
            A dictionary containing the response from the delete operation.
        
        Raises:
            ValueError: If 'project_id' or 'vpc_endpoint_id' is None.
            requests.HTTPError: If the HTTP request to delete the VPC endpoint fails.
        
        Tags:
            delete, vpc-endpoint, management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if vpc_endpoint_id is None:
            raise ValueError("Missing required parameter 'vpc_endpoint_id'")
        url = f"{self.base_url}/projects/{project_id}/vpc-endpoints/{vpc_endpoint_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_project_endpoint(self, project_id, endpoint) -> dict[str, Any]:
        """
        Creates a new endpoint for the specified project by sending a POST request to the project endpoint API.
        
        Args:
            project_id: The unique identifier of the project for which the endpoint will be created.
            endpoint: The configuration or name of the endpoint to be created for the project.
        
        Returns:
            A dictionary containing the JSON response from the API after creating the endpoint.
        
        Raises:
            ValueError: Raised if 'project_id' or 'endpoint' is None.
            HTTPError: Raised if the HTTP request to create the endpoint returns an unsuccessful status code.
        
        Tags:
            create, endpoint, api, project-management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint is None:
            raise ValueError("Missing required parameter 'endpoint'")
        request_body = {
            'endpoint': endpoint,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/endpoints"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_project_endpoints(self, project_id) -> dict[str, Any]:
        """
        Retrieves a list of API endpoints associated with a specified project.
        
        Args:
            project_id: str. Unique identifier of the project whose endpoints are to be listed.
        
        Returns:
            dict. A dictionary representing the JSON response containing the project's endpoints.
        
        Raises:
            ValueError: If 'project_id' is None.
            HTTPError: If the HTTP request to fetch endpoints fails.
        
        Tags:
            list, endpoints, project, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/projects/{project_id}/endpoints"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_endpoint(self, project_id, endpoint_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific endpoint within a project.
        
        Args:
            project_id: str. The unique identifier of the project containing the endpoint.
            endpoint_id: str. The unique identifier of the endpoint to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing the endpoint details as returned by the API.
        
        Raises:
            ValueError: Raised if 'project_id' or 'endpoint_id' is None.
            requests.HTTPError: Raised if the HTTP request fails or an HTTP error status is returned.
        
        Tags:
            get, endpoint, project, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        url = f"{self.base_url}/projects/{project_id}/endpoints/{endpoint_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_endpoint(self, project_id, endpoint_id) -> dict[str, Any]:
        """
        Deletes a specific endpoint from a given project.
        
        Args:
            project_id: The unique identifier of the project containing the endpoint to delete.
            endpoint_id: The unique identifier of the endpoint to be deleted.
        
        Returns:
            A dictionary containing the server's JSON response to the deletion request.
        
        Raises:
            ValueError: Raised if either 'project_id' or 'endpoint_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the endpoint fails.
        
        Tags:
            delete, endpoint-management, project-management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        url = f"{self.base_url}/projects/{project_id}/endpoints/{endpoint_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_project_endpoint(self, project_id, endpoint_id, endpoint) -> dict[str, Any]:
        """
        Updates the configuration of a specific endpoint within a project.
        
        Args:
            project_id: The unique identifier of the project containing the endpoint to update.
            endpoint_id: The unique identifier of the endpoint to update.
            endpoint: A dictionary containing the new endpoint configuration data.
        
        Returns:
            A dictionary representing the updated endpoint details as returned by the API.
        
        Raises:
            ValueError: Raised if any of the required parameters ('project_id', 'endpoint_id', or 'endpoint') are missing or None.
            requests.HTTPError: Raised if the HTTP PATCH request fails due to a client or server error.
        
        Tags:
            update, endpoint-management, project, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        if endpoint is None:
            raise ValueError("Missing required parameter 'endpoint'")
        request_body = {
            'endpoint': endpoint,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{project_id}/endpoints/{endpoint_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def start_project_endpoint(self, project_id, endpoint_id) -> dict[str, Any]:
        """
        Starts the specified endpoint for a given project by making a POST request to the API.
        
        Args:
            project_id: str. The identifier of the project containing the endpoint to start.
            endpoint_id: str. The identifier of the endpoint to start within the project.
        
        Returns:
            dict[str, Any]: The JSON response from the API after starting the endpoint.
        
        Raises:
            ValueError: If 'project_id' or 'endpoint_id' is None.
            requests.HTTPError: If the HTTP request to start the endpoint fails.
        
        Tags:
            start, endpoint, project-management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        url = f"{self.base_url}/projects/{project_id}/endpoints/{endpoint_id}/start"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def suspend_project_endpoint(self, project_id, endpoint_id) -> dict[str, Any]:
        """
        Suspends a specific endpoint within a project by issuing a POST request to the suspend endpoint API.
        
        Args:
            project_id: str. Unique identifier of the project containing the endpoint to be suspended.
            endpoint_id: str. Unique identifier of the endpoint to suspend.
        
        Returns:
            dict[str, Any]: The parsed JSON response from the API after suspending the endpoint.
        
        Raises:
            ValueError: Raised if 'project_id' or 'endpoint_id' is None.
            requests.HTTPError: Raised if the POST request to the API fails (non-2xx status code).
        
        Tags:
            suspend, endpoint, management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        url = f"{self.base_url}/projects/{project_id}/endpoints/{endpoint_id}/suspend"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def restart_project_endpoint(self, project_id, endpoint_id) -> dict[str, Any]:
        """
        Restarts a specific project endpoint by sending a POST request to the server.
        
        Args:
            project_id: str. The unique identifier of the project containing the endpoint to be restarted.
            endpoint_id: str. The unique identifier of the endpoint to restart.
        
        Returns:
            dict. The server's JSON response containing details of the restarted endpoint operation.
        
        Raises:
            ValueError: If 'project_id' or 'endpoint_id' is None.
            HTTPError: If the HTTP request to restart the endpoint fails (raised by response.raise_for_status()).
        
        Tags:
            restart, endpoint-management, project-management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        url = f"{self.base_url}/projects/{project_id}/endpoints/{endpoint_id}/restart"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization(self, org_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific organization using its unique organization ID.
        
        Args:
            org_id: str. The unique identifier of the organization to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing the organization's details as returned by the API.
        
        Raises:
            ValueError: Raised if the 'org_id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to fetch the organization fails (e.g., not found, server error).
        
        Tags:
            get, organization, api, management
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        url = f"{self.base_url}/organizations/{org_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def revoke_org_api_key(self, org_id, key_id) -> dict[str, Any]:
        """
        Revokes an API key for a specific organization by sending a DELETE request.
        
        Args:
            org_id: The unique identifier of the organization whose API key is to be revoked.
            key_id: The unique identifier of the API key to revoke.
        
        Returns:
            A dictionary containing the response from the API after revoking the key.
        
        Raises:
            ValueError: Raised if 'org_id' or 'key_id' is None.
            requests.HTTPError: Raised if the HTTP request fails with a non-success status code.
        
        Tags:
            revoke, api-key, management, delete
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if key_id is None:
            raise ValueError("Missing required parameter 'key_id'")
        url = f"{self.base_url}/organizations/{org_id}/api_keys/{key_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization_members(self, org_id) -> dict[str, Any]:
        """
        Retrieves the list of members belonging to a specified organization by organization ID.
        
        Args:
            org_id: The unique identifier of the organization whose members are to be fetched.
        
        Returns:
            A dictionary containing the organization members' details as returned by the API.
        
        Raises:
            ValueError: If 'org_id' is None.
            HTTPError: If the HTTP request to the API endpoint fails.
        
        Tags:
            get, list, organization, members, api
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        url = f"{self.base_url}/organizations/{org_id}/members"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization_member(self, org_id, member_id) -> dict[str, Any]:
        """
        Retrieves information about a specific member within an organization by their identifiers.
        
        Args:
            org_id: The unique identifier of the organization. Must not be None.
            member_id: The unique identifier of the member within the organization. Must not be None.
        
        Returns:
            A dictionary containing the member details as returned by the API.
        
        Raises:
            ValueError: Raised if either 'org_id' or 'member_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the member fails.
        
        Tags:
            get, organization, member, management, api
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if member_id is None:
            raise ValueError("Missing required parameter 'member_id'")
        url = f"{self.base_url}/organizations/{org_id}/members/{member_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_organization_member(self, org_id, member_id, role) -> dict[str, Any]:
        """
        Updates the role of a specific member within an organization.
        
        Args:
            org_id: The unique identifier of the organization.
            member_id: The unique identifier of the member whose role is to be updated.
            role: The new role to assign to the organization member.
        
        Returns:
            A dictionary containing the updated member information as returned by the API.
        
        Raises:
            ValueError: Raised if 'org_id', 'member_id', or 'role' is None.
            requests.HTTPError: Raised if the HTTP PATCH request fails.
        
        Tags:
            update, organization, member-management, role, api
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if member_id is None:
            raise ValueError("Missing required parameter 'member_id'")
        if role is None:
            raise ValueError("Missing required parameter 'role'")
        request_body = {
            'role': role,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/organizations/{org_id}/members/{member_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def remove_organization_member(self, org_id, member_id) -> dict[str, Any]:
        """
        Removes a specified member from an organization.
        
        Args:
            org_id: str. The unique identifier of the organization from which the member will be removed.
            member_id: str. The unique identifier of the member to remove from the organization.
        
        Returns:
            dict[str, Any]: The response data from the API after attempting to remove the member.
        
        Raises:
            ValueError: Raised if 'org_id' or 'member_id' is None.
            requests.HTTPError: Raised if the API response contains an HTTP error status.
        
        Tags:
            remove, member-management, organization
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if member_id is None:
            raise ValueError("Missing required parameter 'member_id'")
        url = f"{self.base_url}/organizations/{org_id}/members/{member_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization_invitations(self, org_id) -> dict[str, Any]:
        """
        Retrieves the list of invitations for a specified organization.
        
        Args:
            org_id: The unique identifier of the organization for which to fetch invitations.
        
        Returns:
            A dictionary containing the organization's invitations as returned by the API.
        
        Raises:
            ValueError: If 'org_id' is None.
            requests.HTTPError: If the HTTP request to the remote API fails with a non-success status code.
        
        Tags:
            get, organization, invitations, api
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        url = f"{self.base_url}/organizations/{org_id}/invitations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_organization_invitations(self, org_id, invitations) -> dict[str, Any]:
        """
        Creates new invitations for users to join an organization by sending a POST request to the organization's invitations endpoint.
        
        Args:
            org_id: The identifier of the organization to which invitations will be sent.
            invitations: A list of invitation details to be sent to users (must be serializable to JSON).
        
        Returns:
            A dictionary containing the API response data for the created invitations.
        
        Raises:
            ValueError: If 'org_id' or 'invitations' is None.
            requests.HTTPError: If the HTTP request to the API fails.
        
        Tags:
            create, invitations, api, organization-management
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if invitations is None:
            raise ValueError("Missing required parameter 'invitations'")
        request_body = {
            'invitations': invitations,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/organizations/{org_id}/invitations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_organization_vpcendpoints(self, org_id, region_id) -> dict[str, Any]:
        """
        Retrieves a list of VPC endpoints for a specified organization and region.
        
        Args:
            org_id: The unique identifier of the organization for which to list VPC endpoints.
            region_id: The identifier of the region within the organization to filter VPC endpoints.
        
        Returns:
            A dictionary containing the VPC endpoints data for the specified organization and region.
        
        Raises:
            ValueError: Raised if 'org_id' or 'region_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve VPC endpoints results in an error status code.
        
        Tags:
            list, vpc, networking, management
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if region_id is None:
            raise ValueError("Missing required parameter 'region_id'")
        url = f"{self.base_url}/organizations/{org_id}/vpc/region/{region_id}/vpc-endpoints"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization_vpcendpoint_details(self, org_id, region_id, vpc_endpoint_id) -> dict[str, Any]:
        """
        Retrieves details about a specific VPC endpoint for an organization in a given region.
        
        Args:
            org_id: str. The unique identifier of the organization.
            region_id: str. The identifier of the region containing the VPC endpoint.
            vpc_endpoint_id: str. The unique identifier of the VPC endpoint to retrieve details for.
        
        Returns:
            dict[str, Any]: A dictionary containing the details of the specified VPC endpoint.
        
        Raises:
            ValueError: If any of 'org_id', 'region_id', or 'vpc_endpoint_id' is None.
            requests.HTTPError: If the HTTP request to retrieve details fails with an error status code.
        
        Tags:
            get, vpc-endpoint, organization, networking, details
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if region_id is None:
            raise ValueError("Missing required parameter 'region_id'")
        if vpc_endpoint_id is None:
            raise ValueError("Missing required parameter 'vpc_endpoint_id'")
        url = f"{self.base_url}/organizations/{org_id}/vpc/region/{region_id}/vpc-endpoints/{vpc_endpoint_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def assign_organization_vpcendpoint(self, org_id, region_id, vpc_endpoint_id, label) -> Any:
        """
        Assigns a label to a specified organization VPC endpoint in a given region.
        
        Args:
            org_id: str. Unique identifier of the organization.
            region_id: str. Identifier for the region where the VPC endpoint resides.
            vpc_endpoint_id: str. Unique identifier of the VPC endpoint to assign the label to.
            label: str. The label to assign to the VPC endpoint.
        
        Returns:
            dict. JSON response from the API containing details of the labeled VPC endpoint.
        
        Raises:
            ValueError: Raised if any of the required parameters ('org_id', 'region_id', 'vpc_endpoint_id', or 'label') are None.
            requests.HTTPError: Raised if the HTTP request to the API fails with an error status code.
        
        Tags:
            assign, vpc-endpoint, label, management, network, api
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if region_id is None:
            raise ValueError("Missing required parameter 'region_id'")
        if vpc_endpoint_id is None:
            raise ValueError("Missing required parameter 'vpc_endpoint_id'")
        if label is None:
            raise ValueError("Missing required parameter 'label'")
        request_body = {
            'label': label,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/organizations/{org_id}/vpc/region/{region_id}/vpc-endpoints/{vpc_endpoint_id}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_organization_vpcendpoint(self, org_id, region_id, vpc_endpoint_id) -> Any:
        """
        Deletes a specific VPC endpoint associated with an organization and region.
        
        Args:
            org_id: The unique identifier of the organization.
            region_id: The unique identifier of the region where the VPC endpoint is located.
            vpc_endpoint_id: The identifier of the VPC endpoint to delete.
        
        Returns:
            The JSON response from the API containing the result of the delete operation.
        
        Raises:
            ValueError: Raised if any of 'org_id', 'region_id', or 'vpc_endpoint_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the VPC endpoint fails.
        
        Tags:
            delete, vpc-endpoint, organization, management
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if region_id is None:
            raise ValueError("Missing required parameter 'region_id'")
        if vpc_endpoint_id is None:
            raise ValueError("Missing required parameter 'vpc_endpoint_id'")
        url = f"{self.base_url}/organizations/{org_id}/vpc/region/{region_id}/vpc-endpoints/{vpc_endpoint_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_active_regions(self, ) -> dict[str, Any]:
        """
        Retrieves a list of active regions available in the system.
        
        Returns:
            A dictionary containing information about active regions, with region identifiers as keys and their properties as values.
        
        Raises:
            HTTPError: If the HTTP request fails or returns an unsuccessful status code.
        
        Tags:
            retrieve, regions, http, get, api, geography
        """
        url = f"{self.base_url}/regions"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_current_user_info(self, ) -> dict[str, Any]:
        """
        Retrieves information about the currently authenticated user from the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing details about the current user as returned by the API.
        
        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.
        
        Tags:
            get, user-info, api
        """
        url = f"{self.base_url}/users/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_current_user_organizations(self, ) -> dict[str, Any]:
        """
        Retrieves a list of organizations associated with the current authenticated user.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing details of organizations the current user belongs to.
        
        Raises:
            requests.HTTPError: If the HTTP request to fetch organizations fails or returns an error status code.
        
        Tags:
            get, organizations, user, api
        """
        url = f"{self.base_url}/users/me/organizations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def transfer_projects_from_user_to_org(self, org_id, project_ids) -> dict[str, Any]:
        """
        Transfers ownership of specified projects from the authenticated user to a target organization.
        
        Args:
            org_id: str. The unique identifier of the target organization to which projects will be transferred.
            project_ids: list. A list of project IDs to transfer to the organization.
        
        Returns:
            dict. The server's JSON response containing the result of the project transfer operation.
        
        Raises:
            ValueError: Raised if 'org_id' or 'project_ids' is None.
            requests.HTTPError: Raised if the HTTP request to transfer projects fails.
        
        Tags:
            transfer, projects, organization, management
        """
        if org_id is None:
            raise ValueError("Missing required parameter 'org_id'")
        if project_ids is None:
            raise ValueError("Missing required parameter 'project_ids'")
        request_body = {
            'org_id': org_id,
            'project_ids': project_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/me/projects/transfer"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.list_api_keys,
            self.create_api_key,
            self.revoke_api_key,
            self.get_project_operation,
            self.list_projects,
            self.create_project,
            self.list_shared_projects,
            self.get_project,
            self.update_project,
            self.delete_project,
            self.list_project_operations,
            self.list_project_permissions,
            self.grant_permission_to_project,
            self.revoke_permission_from_project,
            self.get_project_jwks,
            self.add_project_jwks,
            self.delete_project_jwks,
            self.get_connection_uri,
            self.get_project_branch,
            self.delete_project_branch,
            self.update_project_branch,
            self.restore_project_branch,
            self.get_project_branch_schema,
            self.set_default_project_branch,
            self.list_project_branch_endpoints,
            self.list_project_branch_databases,
            self.create_project_branch_database,
            self.get_project_branch_database,
            self.update_project_branch_database,
            self.delete_project_branch_database,
            self.list_project_branch_roles,
            self.create_project_branch_role,
            self.get_project_branch_role,
            self.delete_project_branch_role,
            self.get_project_branch_role_password,
            self.reset_project_branch_role_password,
            self.list_project_vpcendpoints,
            self.assign_project_vpcendpoint,
            self.delete_project_vpcendpoint,
            self.create_project_endpoint,
            self.list_project_endpoints,
            self.get_project_endpoint,
            self.delete_project_endpoint,
            self.update_project_endpoint,
            self.start_project_endpoint,
            self.suspend_project_endpoint,
            self.restart_project_endpoint,
            self.get_organization,
            self.revoke_org_api_key,
            self.get_organization_members,
            self.get_organization_member,
            self.update_organization_member,
            self.remove_organization_member,
            self.get_organization_invitations,
            self.create_organization_invitations,
            self.list_organization_vpcendpoints,
            self.get_organization_vpcendpoint_details,
            self.assign_organization_vpcendpoint,
            self.delete_organization_vpcendpoint,
            self.get_active_regions,
            self.get_current_user_info,
            self.get_current_user_organizations,
            self.transfer_projects_from_user_to_org
        ]
