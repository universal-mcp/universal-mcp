from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class SupabaseApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="supabase", integration=integration, **kwargs)
        self.base_url = "https://api.supabase.com"

    def v1_get_a_branch_config(self, branch_id) -> dict[str, Any]:
        """
        Retrieves the configuration details for a specific branch by branch ID.

        Args:
            branch_id: str. The unique identifier of the branch whose configuration is to be retrieved.

        Returns:
            dict. A dictionary containing the configuration data for the specified branch.

        Raises:
            ValueError: If 'branch_id' is None.
            requests.HTTPError: If the HTTP request to fetch the branch configuration fails.

        Tags:
            get, branch, config, api
        """
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/v1/branches/{branch_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_a_branch_config(
        self,
        branch_id,
        branch_name=None,
        git_branch=None,
        reset_on_push=None,
        persistent=None,
        status=None,
    ) -> dict[str, Any]:
        """
        Updates the configuration of a specified branch by sending a PATCH request with provided configuration fields.

        Args:
            branch_id: str. Unique identifier of the branch to be updated. Required.
            branch_name: str or None. New name for the branch. Optional.
            git_branch: str or None. Name of the associated Git branch. Optional.
            reset_on_push: bool or None. If True, resets the branch on Git push. Optional.
            persistent: bool or None. Whether the branch configuration should persist across operations. Optional.
            status: str or None. Status to set for the branch (e.g., 'active', 'inactive'). Optional.

        Returns:
            dict. JSON response containing the updated branch configuration details from the API.

        Raises:
            ValueError: Raised if 'branch_id' is None.
            requests.HTTPError: Raised if the HTTP request fails or returns a non-2xx status code.

        Tags:
            update, branch-management, api, patch, config
        """
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        request_body = {
            "branch_name": branch_name,
            "git_branch": git_branch,
            "reset_on_push": reset_on_push,
            "persistent": persistent,
            "status": status,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/branches/{branch_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_delete_a_branch(self, branch_id) -> dict[str, Any]:
        """
        Deletes a branch with the specified branch ID using a DELETE request to the API.

        Args:
            branch_id: The unique identifier of the branch to be deleted.

        Returns:
            A dictionary containing the JSON response from the API after the branch is deleted.

        Raises:
            ValueError: If the required parameter 'branch_id' is None.
            HTTPError: If the DELETE request to the API fails with a non-success status code.

        Tags:
            delete, branch-management, api
        """
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/v1/branches/{branch_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_reset_a_branch(self, branch_id) -> dict[str, Any]:
        """
        Resets the specified branch by making a POST request to the branch reset endpoint.

        Args:
            branch_id: The unique identifier of the branch to reset.

        Returns:
            A dictionary containing the API response data from the branch reset operation.

        Raises:
            ValueError: If 'branch_id' is None.
            requests.HTTPError: If the HTTP request to reset the branch fails with a client or server error.

        Tags:
            reset, branch, api, post, management
        """
        if branch_id is None:
            raise ValueError("Missing required parameter 'branch_id'")
        url = f"{self.base_url}/v1/branches/{branch_id}/reset"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_projects(
        self,
    ) -> list[Any]:
        """
        Retrieves a list of all projects from the v1 API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            list: A list of project objects returned by the API.

        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            list, projects, api
        """
        url = f"{self.base_url}/v1/projects"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_create_a_project(
        self,
        db_pass,
        name,
        organization_id,
        region,
        plan=None,
        kps_enabled=None,
        desired_instance_size=None,
        template_url=None,
        release_channel=None,
        postgres_engine=None,
    ) -> dict[str, Any]:
        """
        Creates a new project with the specified configuration and returns the project details.

        Args:
            db_pass: str. The password for the project's database. Required.
            name: str. The name of the project to be created. Required.
            organization_id: str. The unique identifier of the organization under which the project is created. Required.
            region: str. The region where the project resources should be provisioned. Required.
            plan: Optional[str]. The subscription or resource plan to assign to the project.
            kps_enabled: Optional[bool]. Whether Key-Per-Service (KPS) is enabled for the project.
            desired_instance_size: Optional[str]. The desired instance size for the project's resources.
            template_url: Optional[str]. URL to a project template to use for initialization.
            release_channel: Optional[str]. The release channel to use for database engine updates.
            postgres_engine: Optional[str]. The PostgreSQL engine version to use for the project.

        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created project as returned by the API.

        Raises:
            ValueError: If any of the required parameters ('db_pass', 'name', 'organization_id', or 'region') is missing.
            requests.HTTPError: If the HTTP request to create the project fails or returns an unsuccessful status.

        Tags:
            create, project, api, management
        """
        if db_pass is None:
            raise ValueError("Missing required parameter 'db_pass'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if organization_id is None:
            raise ValueError("Missing required parameter 'organization_id'")
        if region is None:
            raise ValueError("Missing required parameter 'region'")
        request_body = {
            "db_pass": db_pass,
            "name": name,
            "organization_id": organization_id,
            "plan": plan,
            "region": region,
            "kps_enabled": kps_enabled,
            "desired_instance_size": desired_instance_size,
            "template_url": template_url,
            "release_channel": release_channel,
            "postgres_engine": postgres_engine,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_organizations(
        self,
    ) -> list[Any]:
        """
        Retrieves a list of all organizations from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A list containing organization data as returned by the API. Each element represents an organization's details.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the organizations API endpoint fails or returns a non-success status code.

        Tags:
            list, organizations, api, fetch, important
        """
        url = f"{self.base_url}/v1/organizations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_create_an_organization(self, name) -> dict[str, Any]:
        """
        Creates a new organization using the provided name and returns the organization details.

        Args:
            name: str. The name of the organization to be created. Must not be None.

        Returns:
            dict[str, Any]: A dictionary containing the created organization's details as returned by the API.

        Raises:
            ValueError: Raised if the 'name' parameter is None.
            requests.HTTPError: Raised if the HTTP request to create the organization fails.

        Tags:
            create, organization, api, async-job, management, important
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/organizations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_authorize_user(
        self,
        client_id,
        response_type,
        redirect_uri,
        scope=None,
        state=None,
        response_mode=None,
        code_challenge=None,
        code_challenge_method=None,
    ) -> Any:
        """
        Initiates the OAuth 2.0 authorization flow by constructing and sending an authorization request to the identity provider.

        Args:
            client_id: str. The client identifier issued to the application.
            response_type: str. The type of response desired, typically 'code' for authorization code flow.
            redirect_uri: str. The URI to which the authorization server will redirect after authorization.
            scope: Optional[str]. A space-delimited list of scopes requested by the application.
            state: Optional[str]. An opaque value used to maintain state between the request and the callback.
            response_mode: Optional[str]. Specifies how the result should be returned to the client (e.g., 'query', 'fragment').
            code_challenge: Optional[str]. Code challenge for PKCE (Proof Key for Code Exchange) to enhance security.
            code_challenge_method: Optional[str]. Method used to derive code challenge (e.g., 'S256').

        Returns:
            dict. JSON-decoded response from the authorization endpoint, containing the authorization response or error details.

        Raises:
            ValueError: Raised if any of the required parameters ('client_id', 'response_type', or 'redirect_uri') is not provided.
            requests.HTTPError: Raised if the HTTP request to the authorization endpoint fails (non-2xx response).

        Tags:
            authorize, oauth, identity, auth-flow, start
        """
        if client_id is None:
            raise ValueError("Missing required parameter 'client_id'")
        if response_type is None:
            raise ValueError("Missing required parameter 'response_type'")
        if redirect_uri is None:
            raise ValueError("Missing required parameter 'redirect_uri'")
        url = f"{self.base_url}/v1/oauth/authorize"
        query_params = {
            k: v
            for k, v in [
                ("client_id", client_id),
                ("response_type", response_type),
                ("redirect_uri", redirect_uri),
                ("scope", scope),
                ("state", state),
                ("response_mode", response_mode),
                ("code_challenge", code_challenge),
                ("code_challenge_method", code_challenge_method),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_snippets(self, project_ref=None) -> dict[str, Any]:
        """
        Retrieves all code snippets for the specified project, or for all projects if no project reference is provided.

        Args:
            project_ref: Optional; a reference identifier for the project to filter snippets by. If not provided, returns snippets from all projects.

        Returns:
            A dictionary containing the response payload with details of the code snippets.

        Raises:
            requests.HTTPError: Raised if the underlying HTTP request returns an unsuccessful status code.

        Tags:
            list, snippets, management, api, important
        """
        url = f"{self.base_url}/v1/snippets"
        query_params = {
            k: v for k, v in [("project_ref", project_ref)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_a_snippet(self, id) -> dict[str, Any]:
        """
        Retrieves a snippet resource by its unique identifier using a GET request to the v1 endpoint.

        Args:
            id: The unique identifier of the snippet to retrieve. Must not be None.

        Returns:
            A dictionary containing the snippet data retrieved from the API.

        Raises:
            ValueError: If the 'id' parameter is None.
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            get, snippet, api
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/snippets/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_project_api_keys(self, ref) -> list[Any]:
        """
        Retrieves the list of API keys associated with a specified project reference.

        Args:
            ref: The unique identifier of the project whose API keys are to be fetched. Must not be None.

        Returns:
            A list containing the API keys for the specified project.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            HTTPError: Raised if the HTTP request to fetch API keys fails.

        Tags:
            get, api-keys, project, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/api-keys"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_api_key(
        self, ref, type, description=None, secret_jwt_template=None
    ) -> dict[str, Any]:
        """
        Creates a new API key for the specified project with optional description and secret JWT template.

        Args:
            ref: str. Project reference or identifier for which the API key is created.
            type: str. Type or category of the API key being created.
            description: str, optional. Human-readable description of the API key.
            secret_jwt_template: Any, optional. Template used to generate the secret JWT for the API key.

        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created API key as returned by the API.

        Raises:
            ValueError: If 'ref' or 'type' is None.
            requests.HTTPError: If the API request fails or the server returns an unsuccessful status.

        Tags:
            create, api-key, management, async-job, start
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        request_body = {
            "type": type,
            "description": description,
            "secret_jwt_template": secret_jwt_template,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/api-keys"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_api_key(
        self, ref, id, description=None, secret_jwt_template=None
    ) -> dict[str, Any]:
        """
        Updates an existing API key identified by its project reference and key ID, allowing optional update of description and secret JWT template.

        Args:
            ref: str. Unique project reference identifier for the API key.
            id: str. Unique identifier of the API key to update.
            description: Optional[str]. New description for the API key. If not provided, the description is not updated.
            secret_jwt_template: Optional[Any]. New secret JWT template to associate with the API key. If not provided, this field remains unchanged.

        Returns:
            dict[str, Any]: The updated API key resource as a dictionary parsed from the response JSON.

        Raises:
            ValueError: Raised if either 'ref' or 'id' is None.
            requests.HTTPError: Raised if the HTTP request to update the API key fails or returns an error status code.

        Tags:
            update, api-key, management, patch
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        request_body = {
            "description": description,
            "secret_jwt_template": secret_jwt_template,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/api-keys/{id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_api_key(self, ref, id) -> dict[str, Any]:
        """
        Deletes an API key associated with a project using the provided reference and key ID.

        Args:
            ref: str. The unique project reference identifier.
            id: str. The API key identifier to delete.

        Returns:
            dict[str, Any]: The response from the API as a dictionary, typically containing status or metadata about the deleted API key.

        Raises:
            ValueError: Raised if 'ref' or 'id' is None.
            requests.HTTPError: Raised if the HTTP response from the deletion request contains an unsuccessful status code.

        Tags:
            delete, api-key, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v1/projects/{ref}/api-keys/{id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_branches(self, ref) -> list[Any]:
        """
        Retrieves a list of all branches for the specified project reference using the v1 API.

        Args:
            ref: The project reference identifier (str) for which branches are to be listed. Must not be None.

        Returns:
            A list containing the branch information returned by the API. Each element corresponds to a branch, as parsed from the response JSON.

        Raises:
            ValueError: If the required parameter 'ref' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            list, branches, api, project-management, important
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/branches"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_create_a_branch(
        self,
        ref,
        branch_name,
        desired_instance_size=None,
        release_channel=None,
        postgres_engine=None,
        git_branch=None,
        persistent=None,
        region=None,
    ) -> dict[str, Any]:
        """
        Creates a new branch for a specified project, configuring options such as instance size, release channel, and region.

        Args:
            ref: str. The reference ID or name of the parent project to which the branch will be added. Required.
            branch_name: str. The name for the new branch to be created. Required.
            desired_instance_size: str or None. Optional. The desired size of the instance for the new branch.
            release_channel: str or None. Optional. The release channel for the new branch (e.g., 'stable', 'beta').
            postgres_engine: str or None. Optional. The PostgreSQL engine version or type for the branch.
            git_branch: str or None. Optional. The upstream Git branch to link with the new branch.
            persistent: bool or None. Optional. Indicates whether the branch should be persistent.
            region: str or None. Optional. The deployment region for the new branch.

        Returns:
            dict[str, Any]: The API response as a dictionary containing details and metadata about the newly created branch.

        Raises:
            ValueError: If 'ref' or 'branch_name' is not provided.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            create, branch, management, api, start, important
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if branch_name is None:
            raise ValueError("Missing required parameter 'branch_name'")
        request_body = {
            "desired_instance_size": desired_instance_size,
            "release_channel": release_channel,
            "postgres_engine": postgres_engine,
            "branch_name": branch_name,
            "git_branch": git_branch,
            "persistent": persistent,
            "region": region,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/branches"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_disable_preview_branching(self, ref) -> Any:
        """
        Disables preview branching for a specified project reference by sending a DELETE request to the corresponding API endpoint.

        Args:
            ref: str. The project reference identifier for which preview branching will be disabled.

        Returns:
            Any. The parsed JSON response from the API after disabling preview branching.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to disable preview branching fails.

        Tags:
            disable, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/branches"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_hostname_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the configuration for a custom hostname associated with a given project reference.

        Args:
            ref: str. The unique project reference identifier to query the custom hostname configuration for.

        Returns:
            dict. A dictionary containing the configuration details of the project's custom hostname as returned by the API.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to fetch the hostname configuration fails.

        Tags:
            get, hostname-config, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/custom-hostname"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_verify_dns_config(self, ref) -> dict[str, Any]:
        """
        Triggers DNS configuration verification for a specified project reference via a POST request.

        Args:
            ref: The project reference or identifier for which to verify DNS configuration.

        Returns:
            A dictionary containing the JSON response from the verification API endpoint.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to the verification endpoint fails (non-2xx response).

        Tags:
            verify, dns, config, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/custom-hostname/reverify"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_activate_custom_hostname(self, ref) -> dict[str, Any]:
        """
        Activates a custom hostname for the specified project reference using the v1 API endpoint.

        Args:
            ref: The project reference or identifier for which to activate the custom hostname. Must not be None.

        Returns:
            A dictionary containing the JSON response from the API after activating the custom hostname.

        Raises:
            ValueError: If the required parameter 'ref' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            activate, custom-hostname, api, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/custom-hostname/activate"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_network_bans(self, ref) -> dict[str, Any]:
        """
        Retrieves all network bans associated with the specified project reference.

        Args:
            ref: str. The project reference identifier used to specify which project's network bans to retrieve.

        Returns:
            dict. A dictionary containing the details of all network bans for the specified project.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.HTTPError: Raised if the HTTP request returned an unsuccessful status code.

        Tags:
            list, network-bans, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/network-bans/retrieve"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_delete_network_bans(self, ref, ipv4_addresses) -> Any:
        """
        Deletes specified IPv4 addresses from the network ban list for a given project reference.

        Args:
            ref: str. The unique project reference identifier.
            ipv4_addresses: List[str]. List of IPv4 addresses to be removed from the network ban list.

        Returns:
            Any. The parsed JSON response from the API indicating the result of the delete operation.

        Raises:
            ValueError: Raised if the 'ref' or 'ipv4_addresses' parameter is None.
            requests.HTTPError: Raised if the HTTP request to delete network bans fails.

        Tags:
            delete, network-bans, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if ipv4_addresses is None:
            raise ValueError("Missing required parameter 'ipv4_addresses'")
        request_body = {
            "ipv4_addresses": ipv4_addresses,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/network-bans"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_network_restrictions(self, ref) -> dict[str, Any]:
        """
        Retrieves network restriction settings for a given project reference.

        Args:
            ref: str. The unique reference identifier of the project whose network restrictions are to be fetched.

        Returns:
            dict. The network restriction settings associated with the specified project, as a parsed JSON object.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.HTTPError: Raised if the HTTP request to fetch network restrictions returns an unsuccessful status code.

        Tags:
            get, network-restrictions, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/network-restrictions"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_network_restrictions(
        self, ref, dbAllowedCidrs=None, dbAllowedCidrsV6=None
    ) -> dict[str, Any]:
        """
        Updates network access restrictions for the specified project by applying the given allowed IPv4 and IPv6 CIDR ranges.

        Args:
            ref: str. The project reference identifier. Required.
            dbAllowedCidrs: Optional[list[str]]. A list of allowed IPv4 CIDR ranges for database access. Defaults to None.
            dbAllowedCidrsV6: Optional[list[str]]. A list of allowed IPv6 CIDR ranges for database access. Defaults to None.

        Returns:
            dict[str, Any]: The response from the API after updating network restrictions.

        Raises:
            ValueError: If the 'ref' parameter is not provided.
            requests.HTTPError: If the HTTP request fails or an error status is returned by the API.

        Tags:
            update, network-restrictions, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        request_body = {
            "dbAllowedCidrs": dbAllowedCidrs,
            "dbAllowedCidrsV6": dbAllowedCidrsV6,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/network-restrictions/apply"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_pgsodium_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the pgSodium configuration for a specified project reference from the v1 API endpoint.

        Args:
            ref: str. The project reference identifier for which to fetch the pgSodium configuration.

        Returns:
            dict. The pgSodium configuration as parsed from the API response JSON.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.

        Tags:
            get, pgsodium, config, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/pgsodium"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_pgsodium_config(self, ref, root_key) -> dict[str, Any]:
        """
        Updates the pgsodium configuration for a specified project reference using the provided root key.

        Args:
            ref: str. The unique project reference identifier for which the pgsodium configuration will be updated.
            root_key: str. The root encryption key to set in the pgsodium configuration.

        Returns:
            dict. The server's JSON response confirming the updated pgsodium configuration.

        Raises:
            ValueError: Raised if 'ref' or 'root_key' is None.
            requests.HTTPError: Raised if the HTTP request fails with an unsuccessful status code.

        Tags:
            update, pgsodium, config, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if root_key is None:
            raise ValueError("Missing required parameter 'root_key'")
        request_body = {
            "root_key": root_key,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/pgsodium"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_postgrest_service_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the configuration details for the PostgREST service associated with the specified project reference.

        Args:
            ref: str. The unique reference identifier for the project whose PostgREST configuration is to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the PostgREST service configuration details for the specified project.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.HTTPError: Raised if the HTTP request to fetch the PostgREST configuration fails.

        Tags:
            fetch, postgrest, service-config, project
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/postgrest"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_postgrest_service_config(
        self,
        ref,
        max_rows=None,
        db_pool=None,
        db_extra_search_path=None,
        db_schema=None,
    ) -> dict[str, Any]:
        """
        Updates the configuration settings for a PostgREST service for a specified project.

        Args:
            ref: str. The unique identifier of the project whose PostgREST service configuration will be updated.
            max_rows: Optional[int]. The maximum number of rows that the PostgREST service will return per request. If None, the setting remains unchanged.
            db_pool: Optional[int]. The number of database connections in the pool for the PostgREST service. If None, the setting remains unchanged.
            db_extra_search_path: Optional[str]. Additional search path for the database schema. If None, the setting remains unchanged.
            db_schema: Optional[str]. The database schema to be used by the PostgREST service. If None, the setting remains unchanged.

        Returns:
            dict[str, Any]: The updated configuration of the PostgREST service as returned by the backend API.

        Raises:
            ValueError: Raised if the 'ref' parameter is not provided.
            requests.HTTPError: Raised if the server responds with an error status code.

        Tags:
            update, postgrest, service-config, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        request_body = {
            "max_rows": max_rows,
            "db_pool": db_pool,
            "db_extra_search_path": db_extra_search_path,
            "db_schema": db_schema,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/postgrest"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_delete_a_project(self, ref) -> dict[str, Any]:
        """
        Deletes a project identified by its reference and returns the API response as a dictionary.

        Args:
            ref: str. The unique identifier or reference of the project to be deleted.

        Returns:
            dict[str, Any]: The response from the API as a dictionary containing information about the deleted project.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP DELETE request returns an unsuccessful status code.

        Tags:
            delete, project-management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_secrets(self, ref) -> list[Any]:
        """
        Lists all secrets for the specified project reference via the v1 API.

        Args:
            ref: The project reference identifier as a string. Must not be None.

        Returns:
            A list containing the secrets associated with the specified project.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the underlying HTTP request fails with a non-success status code.

        Tags:
            list, secrets, management, v1
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/secrets"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_bulk_create_secrets(self, ref, items) -> Any:
        """
        Creates multiple secrets for a specified project reference in a single batch request.

        Args:
            ref: The project reference identifier as a string. Must not be None.
            items: A list or array of secret objects to create in bulk. Must not be None.

        Returns:
            The JSON-decoded response from the server containing the results of the bulk secrets creation.

        Raises:
            ValueError: If either 'ref' or 'items' is None.
            requests.HTTPError: If the HTTP response from the server indicates an unsuccessful status code.

        Tags:
            bulk-create, secrets, batch, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if items is None:
            raise ValueError("Missing required parameter 'items'")
        request_body = items
        url = f"{self.base_url}/v1/projects/{ref}/secrets"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_bulk_delete_secrets(self, ref, items) -> dict[str, Any]:
        """
        Deletes multiple secrets from a given project by making a bulk delete request.

        Args:
            ref: str. The unique reference or identifier of the project containing the secrets.
            items: list. A list of secret identifiers to delete from the project.

        Returns:
            dict. The parsed JSON response from the server after the bulk delete operation.

        Raises:
            ValueError: If the 'ref' or 'items' parameter is None.
            HTTPError: If the HTTP request to delete secrets fails with a non-successful status code.

        Tags:
            delete, bulk, secrets, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if items is None:
            raise ValueError("Missing required parameter 'items'")
        url = f"{self.base_url}/v1/projects/{ref}/secrets"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_ssl_enforcement_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the SSL enforcement configuration for the specified project.

        Args:
            ref: str. The unique identifier of the project for which to fetch the SSL enforcement configuration.

        Returns:
            dict. The SSL enforcement configuration as a parsed JSON dictionary.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to fetch the configuration fails (i.e., non-2xx response code).

        Tags:
            get, ssl-enforcement, config, project, api, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/ssl-enforcement"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_ssl_enforcement_config(self, ref, requestedConfig) -> dict[str, Any]:
        """
        Updates the SSL enforcement configuration for the specified project reference.

        Args:
            ref: str. The unique project reference identifier to update the SSL enforcement configuration for.
            requestedConfig: Any. The desired SSL enforcement configuration settings to apply.

        Returns:
            dict[str, Any]: The response payload containing the updated SSL enforcement configuration details.

        Raises:
            ValueError: If the 'ref' or 'requestedConfig' argument is None.
            requests.HTTPError: If the HTTP request to update the configuration fails.

        Tags:
            update, ssl-enforcement, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if requestedConfig is None:
            raise ValueError("Missing required parameter 'requestedConfig'")
        request_body = {
            "requestedConfig": requestedConfig,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/ssl-enforcement"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_generate_typescript_types(
        self, ref, included_schemas=None
    ) -> dict[str, Any]:
        """
        Generates TypeScript type definitions for a specified project reference, optionally including specific schemas.

        Args:
            ref: str. The project reference for which TypeScript types are to be generated.
            included_schemas: Optional[list[str]]. List of schema names to include in the generated TypeScript types. If None, all schemas are included.

        Returns:
            dict[str, Any]: A dictionary containing the generated TypeScript type definitions.

        Raises:
            ValueError: If the required 'ref' parameter is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            generate, typescript-types, api, ai
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/types/typescript"
        query_params = {
            k: v for k, v in [("included_schemas", included_schemas)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_vanity_subdomain_config(self, ref) -> dict[str, Any]:
        """
        Retrieve the vanity subdomain configuration for a given project reference.

        Args:
            ref: str. The unique identifier of the project whose vanity subdomain configuration is to be retrieved.

        Returns:
            dict. A dictionary containing the vanity subdomain configuration data for the specified project.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to retrieve the configuration fails.

        Tags:
            get, fetch, vanity-subdomain, project-management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/vanity-subdomain"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_deactivate_vanity_subdomain_config(self, ref) -> Any:
        """
        Deactivates the vanity subdomain configuration for a specified project reference.

        Args:
            ref: The unique reference identifier for the project whose vanity subdomain configuration should be deactivated.

        Returns:
            A dictionary containing the API response data after deactivation.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to deactivate the vanity subdomain configuration fails.

        Tags:
            deactivate, vanity-subdomain, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/vanity-subdomain"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_check_vanity_subdomain_availability(
        self, ref, vanity_subdomain
    ) -> dict[str, Any]:
        """
        Checks the availability of a specified vanity subdomain for a given project reference.

        Args:
            ref: str. The unique reference identifier for the project.
            vanity_subdomain: str. The desired vanity subdomain to check for availability.

        Returns:
            dict[str, Any]: A dictionary containing the availability status and related information for the requested vanity subdomain.

        Raises:
            ValueError: Raised if 'ref' or 'vanity_subdomain' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails or returns an unsuccessful status code.

        Tags:
            check, async-job, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if vanity_subdomain is None:
            raise ValueError("Missing required parameter 'vanity_subdomain'")
        request_body = {
            "vanity_subdomain": vanity_subdomain,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/vanity-subdomain/check-availability"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_activate_vanity_subdomain_config(
        self, ref, vanity_subdomain
    ) -> dict[str, Any]:
        """
        Activates the vanity subdomain configuration for a specified project reference.

        Args:
            ref: str. The unique identifier of the project whose vanity subdomain configuration should be activated.
            vanity_subdomain: str. The vanity subdomain to activate for the given project.

        Returns:
            dict. The JSON response from the API after attempting to activate the vanity subdomain configuration.

        Raises:
            ValueError: Raised if either 'ref' or 'vanity_subdomain' is None.
            HTTPError: Raised if the HTTP request to activate the vanity subdomain configuration fails.

        Tags:
            activate, vanity-subdomain, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if vanity_subdomain is None:
            raise ValueError("Missing required parameter 'vanity_subdomain'")
        request_body = {
            "vanity_subdomain": vanity_subdomain,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/vanity-subdomain/activate"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_upgrade_postgres_version(
        self, ref, release_channel, target_version
    ) -> dict[str, Any]:
        """
        Initiates an upgrade of a PostgreSQL instance to a specified target version via API call.

        Args:
            ref: str. Project or instance reference identifier to specify which PostgreSQL instance to upgrade.
            release_channel: str. Specifies the release channel (e.g., 'stable', 'beta') that determines the upgrade source.
            target_version: str. The desired target PostgreSQL version to upgrade to.

        Returns:
            dict. The API response as a dictionary containing details about the upgrade initiation and status.

        Raises:
            ValueError: If any of 'ref', 'release_channel', or 'target_version' is None.
            requests.HTTPError: If the underlying HTTP request to the upgrade API fails or returns an error response.

        Tags:
            upgrade, postgres, api, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if release_channel is None:
            raise ValueError("Missing required parameter 'release_channel'")
        if target_version is None:
            raise ValueError("Missing required parameter 'target_version'")
        request_body = {
            "release_channel": release_channel,
            "target_version": target_version,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/upgrade"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_postgrest_upgrade_eligibility(self, ref) -> dict[str, Any]:
        """
        Checks the eligibility of a PostgREST upgrade for a specified project reference.

        Args:
            ref: str. The unique project reference identifier for which upgrade eligibility should be checked.

        Returns:
            dict. A dictionary containing the eligibility status and related information for the PostgREST upgrade.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            HTTPError: Raised if the HTTP request to the eligibility endpoint fails.

        Tags:
            check, upgrade, eligibility, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/upgrade/eligibility"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_postgrest_upgrade_status(self, ref) -> dict[str, Any]:
        """
        Retrieves the current upgrade status for a specified PostgREST project.

        Args:
            ref: str. The unique reference ID of the project whose upgrade status is to be retrieved.

        Returns:
            dict. A dictionary containing the upgrade status details for the specified project.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to the upgrade status endpoint fails.

        Tags:
            get, status, postgrest, upgrade, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/upgrade/status"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_readonly_mode_status(self, ref) -> dict[str, Any]:
        """
        Retrieves the read-only mode status for a specified project reference.

        Args:
            ref: The unique identifier (reference) of the project to query for read-only status.

        Returns:
            A dictionary containing the read-only mode status of the specified project.

        Raises:
            ValueError: If the required 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to the server returns an unsuccessful status code.

        Tags:
            get, status, readonly, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/readonly"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_disable_readonly_mode_temporarily(self, ref) -> Any:
        """
        Temporarily disables readonly mode for a specified project reference via a POST request.

        Args:
            ref: The unique reference identifier for the project whose readonly mode should be temporarily disabled. Must not be None.

        Returns:
            The JSON-decoded response from the API indicating the status of the readonly mode disable operation.

        Raises:
            ValueError: If the provided 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to the API fails (e.g., network error, non-2xx response).

        Tags:
            disable, readonly-mode, project-management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/readonly/temporary-disable"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_setup_a_read_replica(self, ref, read_replica_region) -> Any:
        """
        Initiates the setup of a read replica for a specified project in the given region.

        Args:
            ref: The unique identifier or reference for the project for which the read replica is to be set up.
            read_replica_region: The region where the read replica should be created.

        Returns:
            The server response as a parsed JSON object containing details of the read replica setup operation.

        Raises:
            ValueError: Raised if either 'ref' or 'read_replica_region' is None, indicating a required parameter is missing.
            HTTPError: Raised if the server responds with an unsuccessful HTTP status code during the setup operation.

        Tags:
            setup, read-replica, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if read_replica_region is None:
            raise ValueError("Missing required parameter 'read_replica_region'")
        request_body = {
            "read_replica_region": read_replica_region,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/read-replicas/setup"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_remove_a_read_replica(self, ref, database_identifier) -> Any:
        """
        Removes a read replica from a specified database within a project.

        Args:
            ref: str. Project identifier or reference for the operation.
            database_identifier: str. Identifier of the database from which the read replica should be removed.

        Returns:
            dict. The server's JSON response after attempting to remove the read replica.

        Raises:
            ValueError: Raised if 'ref' or 'database_identifier' is None.
            requests.HTTPError: Raised if the HTTP request to remove the read replica fails.

        Tags:
            remove, read-replica, database-management, api-call
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if database_identifier is None:
            raise ValueError("Missing required parameter 'database_identifier'")
        request_body = {
            "database_identifier": database_identifier,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/read-replicas/remove"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_services_health(self, ref, services, timeout_ms=None) -> list[Any]:
        """
        Checks the health status of specified services for a given project reference.

        Args:
            ref: str. The reference identifier for the target project.
            services: list or str. The service or list of services to be checked.
            timeout_ms: Optional[int]. The timeout in milliseconds for the health checks. Defaults to None.

        Returns:
            list. A list containing the health status information for the requested services.

        Raises:
            ValueError: If 'ref' or 'services' is None.
            requests.HTTPError: If the health check HTTP request fails with a non-success response.

        Tags:
            get, health, check, service, status
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if services is None:
            raise ValueError("Missing required parameter 'services'")
        url = f"{self.base_url}/v1/projects/{ref}/health"
        query_params = {
            k: v
            for k, v in [("timeout_ms", timeout_ms), ("services", services)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_postgres_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the PostgreSQL configuration for the specified project reference.

        Args:
            ref: str. The unique reference identifier for the project whose PostgreSQL configuration is to be retrieved.

        Returns:
            dict. The PostgreSQL configuration parameters for the specified project, as returned by the API.

        Raises:
            ValueError: If 'ref' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            get, config, postgres, ai
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/config/database/postgres"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_postgres_config(
        self,
        ref,
        statement_timeout=None,
        effective_cache_size=None,
        maintenance_work_mem=None,
        max_connections=None,
        max_locks_per_transaction=None,
        max_parallel_maintenance_workers=None,
        max_parallel_workers=None,
        max_parallel_workers_per_gather=None,
        max_slot_wal_keep_size=None,
        max_standby_archive_delay=None,
        max_standby_streaming_delay=None,
        max_wal_size=None,
        max_worker_processes=None,
        shared_buffers=None,
        wal_keep_size=None,
        work_mem=None,
        session_replication_role=None,
    ) -> dict[str, Any]:
        """
        Updates PostgreSQL configuration settings for a specified project via a REST API call.

        Args:
            ref: str. The project reference identifier. Required.
            statement_timeout: Optional[int|str]. Sets the maximum allowed duration of any statement.
            effective_cache_size: Optional[int|str]. Estimates the effective size of the disk cache available to a single PostgreSQL process.
            maintenance_work_mem: Optional[int|str]. Sets the maximum memory to be used for maintenance operations.
            max_connections: Optional[int]. Sets the maximum number of concurrent connections.
            max_locks_per_transaction: Optional[int]. Sets the maximum number of locks per transaction.
            max_parallel_maintenance_workers: Optional[int]. Sets the maximum number of parallel workers for maintenance operations.
            max_parallel_workers: Optional[int]. Sets the maximum number of parallel workers for the entire instance.
            max_parallel_workers_per_gather: Optional[int]. Sets the maximum number of parallel workers that can be started by a single Gather node.
            max_slot_wal_keep_size: Optional[int|str]. Maximum size of WAL files kept for replication slots.
            max_standby_archive_delay: Optional[int|str]. Maximum delay a standby server can tolerate for applying WAL data from archive.
            max_standby_streaming_delay: Optional[int|str]. Maximum streaming replication delay on standby.
            max_wal_size: Optional[int|str]. Sets the maximum size to let the WAL grow between automatic WAL checkpoints.
            max_worker_processes: Optional[int]. Maximum number of background processes.
            shared_buffers: Optional[int|str]. Sets the amount of memory the database engine uses for shared memory buffers.
            wal_keep_size: Optional[int|str]. Sets the size of WAL files to keep for standby servers.
            work_mem: Optional[int|str]. Sets the amount of memory to be used by internal sort operations and hash tables before writing to temporary disk files.
            session_replication_role: Optional[str]. Sets the replication role for the session.

        Returns:
            dict[str, Any]: The JSON response from the API after updating the configuration.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request fails or the API responds with an error status code.

        Tags:
            update, postgres-config, management, api, async-job
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        request_body = {
            "statement_timeout": statement_timeout,
            "effective_cache_size": effective_cache_size,
            "maintenance_work_mem": maintenance_work_mem,
            "max_connections": max_connections,
            "max_locks_per_transaction": max_locks_per_transaction,
            "max_parallel_maintenance_workers": max_parallel_maintenance_workers,
            "max_parallel_workers": max_parallel_workers,
            "max_parallel_workers_per_gather": max_parallel_workers_per_gather,
            "max_slot_wal_keep_size": max_slot_wal_keep_size,
            "max_standby_archive_delay": max_standby_archive_delay,
            "max_standby_streaming_delay": max_standby_streaming_delay,
            "max_wal_size": max_wal_size,
            "max_worker_processes": max_worker_processes,
            "shared_buffers": shared_buffers,
            "wal_keep_size": wal_keep_size,
            "work_mem": work_mem,
            "session_replication_role": session_replication_role,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/config/database/postgres"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_project_pgbouncer_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the PgBouncer configuration for a specific project by project reference.

        Args:
            ref: The reference identifier of the project for which to fetch the PgBouncer configuration.

        Returns:
            A dictionary containing the PgBouncer configuration for the specified project.

        Raises:
            ValueError: Raised if the required parameter 'ref' is None.
            requests.HTTPError: Raised if the HTTP request for the configuration fails.

        Tags:
            get, project, pgbouncer, config, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/config/database/pgbouncer"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_supavisor_config(self, ref) -> list[Any]:
        """
        Retrieves the Supavisor configuration for a specified project reference from the configured API.

        Args:
            ref: str. Unique project reference identifier used to construct the request URL. Must not be None.

        Returns:
            list[Any]: The parsed JSON response from the API containing the Supavisor configuration details.

        Raises:
            ValueError: If the required parameter 'ref' is None.
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            get, config, supavisor, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/config/database/pooler"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_supavisor_config(
        self, ref, default_pool_size=None, pool_mode=None
    ) -> dict[str, Any]:
        """
        Updates the Supavisor configuration for a specified project by modifying database pooler settings.

        Args:
            ref: str. The unique reference identifier for the project whose Supavisor configuration is to be updated.
            default_pool_size: Optional[int]. The default size of the database connection pool. If None, this setting is not modified.
            pool_mode: Optional[str]. The mode of the connection pooler (e.g., 'transaction' or 'session'). If None, this setting is not modified.

        Returns:
            dict[str, Any]: The JSON response containing the updated Supavisor configuration details from the API.

        Raises:
            ValueError: If 'ref' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            update, supavisor, config, api, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        request_body = {
            "default_pool_size": default_pool_size,
            "pool_mode": pool_mode,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/config/database/pooler"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_auth_service_config(self, ref) -> dict[str, Any]:
        """
        Retrieves the authentication service configuration for the specified project reference from the API.

        Args:
            ref: str. The unique identifier for the project whose authentication service configuration is to be retrieved.

        Returns:
            dict. A dictionary containing the authentication service configuration details for the specified project.

        Raises:
            ValueError: Raised if 'ref' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns a non-success status code.

        Tags:
            get, auth-service, config, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/config/auth"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_auth_service_config(
        self,
        ref,
        site_url=None,
        disable_signup=None,
        jwt_exp=None,
        smtp_admin_email=None,
        smtp_host=None,
        smtp_port=None,
        smtp_user=None,
        smtp_pass=None,
        smtp_max_frequency=None,
        smtp_sender_name=None,
        mailer_allow_unverified_email_sign_ins=None,
        mailer_autoconfirm=None,
        mailer_subjects_invite=None,
        mailer_subjects_confirmation=None,
        mailer_subjects_recovery=None,
        mailer_subjects_email_change=None,
        mailer_subjects_magic_link=None,
        mailer_subjects_reauthentication=None,
        mailer_templates_invite_content=None,
        mailer_templates_confirmation_content=None,
        mailer_templates_recovery_content=None,
        mailer_templates_email_change_content=None,
        mailer_templates_magic_link_content=None,
        mailer_templates_reauthentication_content=None,
        mfa_max_enrolled_factors=None,
        uri_allow_list=None,
        external_anonymous_users_enabled=None,
        external_email_enabled=None,
        external_phone_enabled=None,
        saml_enabled=None,
        saml_external_url=None,
        security_captcha_enabled=None,
        security_captcha_provider=None,
        security_captcha_secret=None,
        sessions_timebox=None,
        sessions_inactivity_timeout=None,
        sessions_single_per_user=None,
        sessions_tags=None,
        rate_limit_anonymous_users=None,
        rate_limit_email_sent=None,
        rate_limit_sms_sent=None,
        rate_limit_verify=None,
        rate_limit_token_refresh=None,
        rate_limit_otp=None,
        mailer_secure_email_change_enabled=None,
        refresh_token_rotation_enabled=None,
        password_hibp_enabled=None,
        password_min_length=None,
        password_required_characters=None,
        security_manual_linking_enabled=None,
        security_update_password_require_reauthentication=None,
        security_refresh_token_reuse_interval=None,
        mailer_otp_exp=None,
        mailer_otp_length=None,
        sms_autoconfirm=None,
        sms_max_frequency=None,
        sms_otp_exp=None,
        sms_otp_length=None,
        sms_provider=None,
        sms_messagebird_access_key=None,
        sms_messagebird_originator=None,
        sms_test_otp=None,
        sms_test_otp_valid_until=None,
        sms_textlocal_api_key=None,
        sms_textlocal_sender=None,
        sms_twilio_account_sid=None,
        sms_twilio_auth_token=None,
        sms_twilio_content_sid=None,
        sms_twilio_message_service_sid=None,
        sms_twilio_verify_account_sid=None,
        sms_twilio_verify_auth_token=None,
        sms_twilio_verify_message_service_sid=None,
        sms_vonage_api_key=None,
        sms_vonage_api_secret=None,
        sms_vonage_from=None,
        sms_template=None,
        hook_mfa_verification_attempt_enabled=None,
        hook_mfa_verification_attempt_uri=None,
        hook_mfa_verification_attempt_secrets=None,
        hook_password_verification_attempt_enabled=None,
        hook_password_verification_attempt_uri=None,
        hook_password_verification_attempt_secrets=None,
        hook_custom_access_token_enabled=None,
        hook_custom_access_token_uri=None,
        hook_custom_access_token_secrets=None,
        hook_send_sms_enabled=None,
        hook_send_sms_uri=None,
        hook_send_sms_secrets=None,
        hook_send_email_enabled=None,
        hook_send_email_uri=None,
        hook_send_email_secrets=None,
        external_apple_enabled=None,
        external_apple_client_id=None,
        external_apple_secret=None,
        external_apple_additional_client_ids=None,
        external_azure_enabled=None,
        external_azure_client_id=None,
        external_azure_secret=None,
        external_azure_url=None,
        external_bitbucket_enabled=None,
        external_bitbucket_client_id=None,
        external_bitbucket_secret=None,
        external_discord_enabled=None,
        external_discord_client_id=None,
        external_discord_secret=None,
        external_facebook_enabled=None,
        external_facebook_client_id=None,
        external_facebook_secret=None,
        external_figma_enabled=None,
        external_figma_client_id=None,
        external_figma_secret=None,
        external_github_enabled=None,
        external_github_client_id=None,
        external_github_secret=None,
        external_gitlab_enabled=None,
        external_gitlab_client_id=None,
        external_gitlab_secret=None,
        external_gitlab_url=None,
        external_google_enabled=None,
        external_google_client_id=None,
        external_google_secret=None,
        external_google_additional_client_ids=None,
        external_google_skip_nonce_check=None,
        external_kakao_enabled=None,
        external_kakao_client_id=None,
        external_kakao_secret=None,
        external_keycloak_enabled=None,
        external_keycloak_client_id=None,
        external_keycloak_secret=None,
        external_keycloak_url=None,
        external_linkedin_oidc_enabled=None,
        external_linkedin_oidc_client_id=None,
        external_linkedin_oidc_secret=None,
        external_slack_oidc_enabled=None,
        external_slack_oidc_client_id=None,
        external_slack_oidc_secret=None,
        external_notion_enabled=None,
        external_notion_client_id=None,
        external_notion_secret=None,
        external_slack_enabled=None,
        external_slack_client_id=None,
        external_slack_secret=None,
        external_spotify_enabled=None,
        external_spotify_client_id=None,
        external_spotify_secret=None,
        external_twitch_enabled=None,
        external_twitch_client_id=None,
        external_twitch_secret=None,
        external_twitter_enabled=None,
        external_twitter_client_id=None,
        external_twitter_secret=None,
        external_workos_enabled=None,
        external_workos_client_id=None,
        external_workos_secret=None,
        external_workos_url=None,
        external_zoom_enabled=None,
        external_zoom_client_id=None,
        external_zoom_secret=None,
        db_max_pool_size=None,
        api_max_request_duration=None,
        mfa_totp_enroll_enabled=None,
        mfa_totp_verify_enabled=None,
        mfa_web_authn_enroll_enabled=None,
        mfa_web_authn_verify_enabled=None,
        mfa_phone_enroll_enabled=None,
        mfa_phone_verify_enabled=None,
        mfa_phone_max_frequency=None,
        mfa_phone_otp_length=None,
        mfa_phone_template=None,
    ) -> dict[str, Any]:
        """
        Updates the authentication service configuration for a specified project with the provided settings.

        Args:
            ref: str. The unique reference identifier for the target project. Required.
            site_url: Optional[str]. The base URL of the site associated with the authentication service.
            disable_signup: Optional[bool]. If True, disables user sign-ups for the project.
            jwt_exp: Optional[int]. Duration in seconds before issued JWTs expire.
            smtp_admin_email: Optional[str]. Email address used as SMTP admin.
            smtp_host: Optional[str]. Hostname for the SMTP server.
            smtp_port: Optional[int]. Port number for the SMTP server.
            smtp_user: Optional[str]. Username for SMTP authentication.
            smtp_pass: Optional[str]. Password for SMTP authentication.
            smtp_max_frequency: Optional[int]. Maximum frequency at which SMTP emails can be sent.
            smtp_sender_name: Optional[str]. Display name of the SMTP sender.
            mailer_allow_unverified_email_sign_ins: Optional[bool]. Whether to allow sign-ins with unverified email addresses.
            mailer_autoconfirm: Optional[bool]. If True, automatically confirms email sign-ups.
            mailer_subjects_invite: Optional[str]. Subject line for invitation emails.
            mailer_subjects_confirmation: Optional[str]. Subject line for email confirmation.
            mailer_subjects_recovery: Optional[str]. Subject line for account recovery emails.
            mailer_subjects_email_change: Optional[str]. Subject line for email change requests.
            mailer_subjects_magic_link: Optional[str]. Subject line for magic link emails.
            mailer_subjects_reauthentication: Optional[str]. Subject line for reauthentication emails.
            mailer_templates_invite_content: Optional[str]. Email template content for invites.
            mailer_templates_confirmation_content: Optional[str]. Email template content for confirmations.
            mailer_templates_recovery_content: Optional[str]. Email template content for recovery.
            mailer_templates_email_change_content: Optional[str]. Email template content for email changes.
            mailer_templates_magic_link_content: Optional[str]. Email template content for magic links.
            mailer_templates_reauthentication_content: Optional[str]. Email template content for reauthentication.
            mfa_max_enrolled_factors: Optional[int]. Maximum number of multi-factor authentication factors per user.
            uri_allow_list: Optional[list[str]]. List of allowed redirect URIs.
            external_anonymous_users_enabled: Optional[bool]. Enables support for anonymous users.
            external_email_enabled: Optional[bool]. Enables email-based external login.
            external_phone_enabled: Optional[bool]. Enables phone-based external login.
            saml_enabled: Optional[bool]. Enables SAML authentication.
            saml_external_url: Optional[str]. External URL for SAML provider.
            security_captcha_enabled: Optional[bool]. Enables CAPTCHA for added security.
            security_captcha_provider: Optional[str]. Which CAPTCHA provider to use.
            security_captcha_secret: Optional[str]. Secret key for the CAPTCHA provider.
            sessions_timebox: Optional[int]. Maximum session duration in seconds.
            sessions_inactivity_timeout: Optional[int]. Timeout before an inactive session is ended.
            sessions_single_per_user: Optional[bool]. Restricts users to a single active session.
            sessions_tags: Optional[list[str]]. Tags used for session management.
            rate_limit_anonymous_users: Optional[int]. Rate limit for anonymous user operations.
            rate_limit_email_sent: Optional[int]. Rate limit for sending emails.
            rate_limit_sms_sent: Optional[int]. Rate limit for sending SMS messages.
            rate_limit_verify: Optional[int]. Rate limit for verification attempts.
            rate_limit_token_refresh: Optional[int]. Rate limit for token refresh operations.
            rate_limit_otp: Optional[int]. Rate limit for OTP requests.
            mailer_secure_email_change_enabled: Optional[bool]. Enables secure workflow for email change requests.
            refresh_token_rotation_enabled: Optional[bool]. Enables JWT refresh token rotation.
            password_hibp_enabled: Optional[bool]. Enable password checks against Have I Been Pwned (HIBP) database.
            password_min_length: Optional[int]. Minimum password length required.
            password_required_characters: Optional[list[str]]. List of required character types (e.g. uppercase, number).
            security_manual_linking_enabled: Optional[bool]. Enables manual linking of authentication providers.
            security_update_password_require_reauthentication: Optional[bool]. Requires re-authentication to update password.
            security_refresh_token_reuse_interval: Optional[int]. Time interval for refresh token re-use.
            mailer_otp_exp: Optional[int]. Expiry time in seconds for email OTP codes.
            mailer_otp_length: Optional[int]. Length of OTP codes sent via email.
            sms_autoconfirm: Optional[bool]. If True, automatically confirms phone sign-ups.
            sms_max_frequency: Optional[int]. Maximum frequency of SMS sends.
            sms_otp_exp: Optional[int]. Expiry time in seconds for SMS OTP codes.
            sms_otp_length: Optional[int]. Length of OTP codes sent via SMS.
            sms_provider: Optional[str]. Provider used for sending SMS.
            sms_messagebird_access_key: Optional[str]. Access key for MessageBird SMS provider.
            sms_messagebird_originator: Optional[str]. SMS originator for MessageBird.
            sms_test_otp: Optional[str]. Test OTP value for development/testing.
            sms_test_otp_valid_until: Optional[str]. Expiry time for test OTP.
            sms_textlocal_api_key: Optional[str]. API key for TextLocal SMS provider.
            sms_textlocal_sender: Optional[str]. Sender identifier for TextLocal SMS.
            sms_twilio_account_sid: Optional[str]. Twilio Account SID for SMS.
            sms_twilio_auth_token: Optional[str]. Twilio authentication token.
            sms_twilio_content_sid: Optional[str]. Twilio content service identifier.
            sms_twilio_message_service_sid: Optional[str]. Twilio message service SID.
            sms_twilio_verify_account_sid: Optional[str]. Twilio Verify Account SID.
            sms_twilio_verify_auth_token: Optional[str]. Twilio Verify authentication token.
            sms_twilio_verify_message_service_sid: Optional[str]. Twilio Verify message service SID.
            sms_vonage_api_key: Optional[str]. Vonage API key for SMS.
            sms_vonage_api_secret: Optional[str]. Vonage API secret for SMS.
            sms_vonage_from: Optional[str]. Sender identifier for Vonage SMS.
            sms_template: Optional[str]. Template for SMS content.
            hook_mfa_verification_attempt_enabled: Optional[bool]. Enables custom hook on MFA attempt.
            hook_mfa_verification_attempt_uri: Optional[str]. URI for custom MFA verification hook.
            hook_mfa_verification_attempt_secrets: Optional[list[str]]. Secrets for custom MFA verification hook.
            hook_password_verification_attempt_enabled: Optional[bool]. Enables custom hook on password verification attempt.
            hook_password_verification_attempt_uri: Optional[str]. URI for custom password verification hook.
            hook_password_verification_attempt_secrets: Optional[list[str]]. Secrets for custom password verification hook.
            hook_custom_access_token_enabled: Optional[bool]. Enables custom hook for access tokens.
            hook_custom_access_token_uri: Optional[str]. URI for custom access token hook.
            hook_custom_access_token_secrets: Optional[list[str]]. Secrets for custom access token hook.
            hook_send_sms_enabled: Optional[bool]. Enables custom hook for sending SMS.
            hook_send_sms_uri: Optional[str]. URI for custom SMS hook.
            hook_send_sms_secrets: Optional[list[str]]. Secrets for custom SMS hook.
            hook_send_email_enabled: Optional[bool]. Enables custom hook for sending emails.
            hook_send_email_uri: Optional[str]. URI for custom email hook.
            hook_send_email_secrets: Optional[list[str]]. Secrets for custom email hook.
            external_apple_enabled: Optional[bool]. Enables Apple as external authentication provider.
            external_apple_client_id: Optional[str]. Client ID for Apple authentication.
            external_apple_secret: Optional[str]. Secret for Apple authentication.
            external_apple_additional_client_ids: Optional[list[str]]. Additional Apple client IDs.
            external_azure_enabled: Optional[bool]. Enables Azure as external authentication provider.
            external_azure_client_id: Optional[str]. Client ID for Azure authentication.
            external_azure_secret: Optional[str]. Secret for Azure authentication.
            external_azure_url: Optional[str]. Azure authentication URL.
            external_bitbucket_enabled: Optional[bool]. Enables Bitbucket as external authentication provider.
            external_bitbucket_client_id: Optional[str]. Client ID for Bitbucket authentication.
            external_bitbucket_secret: Optional[str]. Secret for Bitbucket authentication.
            external_discord_enabled: Optional[bool]. Enables Discord as external authentication provider.
            external_discord_client_id: Optional[str]. Client ID for Discord authentication.
            external_discord_secret: Optional[str]. Secret for Discord authentication.
            external_facebook_enabled: Optional[bool]. Enables Facebook as external authentication provider.
            external_facebook_client_id: Optional[str]. Client ID for Facebook authentication.
            external_facebook_secret: Optional[str]. Secret for Facebook authentication.
            external_figma_enabled: Optional[bool]. Enables Figma as external authentication provider.
            external_figma_client_id: Optional[str]. Client ID for Figma authentication.
            external_figma_secret: Optional[str]. Secret for Figma authentication.
            external_github_enabled: Optional[bool]. Enables GitHub as external authentication provider.
            external_github_client_id: Optional[str]. Client ID for GitHub authentication.
            external_github_secret: Optional[str]. Secret for GitHub authentication.
            external_gitlab_enabled: Optional[bool]. Enables GitLab as external authentication provider.
            external_gitlab_client_id: Optional[str]. Client ID for GitLab authentication.
            external_gitlab_secret: Optional[str]. Secret for GitLab authentication.
            external_gitlab_url: Optional[str]. GitLab authentication URL.
            external_google_enabled: Optional[bool]. Enables Google as external authentication provider.
            external_google_client_id: Optional[str]. Client ID for Google authentication.
            external_google_secret: Optional[str]. Secret for Google authentication.
            external_google_additional_client_ids: Optional[list[str]]. Additional Google client IDs.
            external_google_skip_nonce_check: Optional[bool]. Skips nonce check for Google authentication.
            external_kakao_enabled: Optional[bool]. Enables Kakao as external authentication provider.
            external_kakao_client_id: Optional[str]. Client ID for Kakao authentication.
            external_kakao_secret: Optional[str]. Secret for Kakao authentication.
            external_keycloak_enabled: Optional[bool]. Enables Keycloak as external authentication provider.
            external_keycloak_client_id: Optional[str]. Client ID for Keycloak authentication.
            external_keycloak_secret: Optional[str]. Secret for Keycloak authentication.
            external_keycloak_url: Optional[str]. Keycloak authentication URL.
            external_linkedin_oidc_enabled: Optional[bool]. Enables LinkedIn OIDC as external authentication provider.
            external_linkedin_oidc_client_id: Optional[str]. Client ID for LinkedIn OIDC.
            external_linkedin_oidc_secret: Optional[str]. Secret for LinkedIn OIDC.
            external_slack_oidc_enabled: Optional[bool]. Enables Slack OIDC as external authentication provider.
            external_slack_oidc_client_id: Optional[str]. Client ID for Slack OIDC.
            external_slack_oidc_secret: Optional[str]. Secret for Slack OIDC.
            external_notion_enabled: Optional[bool]. Enables Notion as external authentication provider.
            external_notion_client_id: Optional[str]. Client ID for Notion authentication.
            external_notion_secret: Optional[str]. Secret for Notion authentication.
            external_slack_enabled: Optional[bool]. Enables Slack as external authentication provider.
            external_slack_client_id: Optional[str]. Client ID for Slack authentication.
            external_slack_secret: Optional[str]. Secret for Slack authentication.
            external_spotify_enabled: Optional[bool]. Enables Spotify as external authentication provider.
            external_spotify_client_id: Optional[str]. Client ID for Spotify authentication.
            external_spotify_secret: Optional[str]. Secret for Spotify authentication.
            external_twitch_enabled: Optional[bool]. Enables Twitch as external authentication provider.
            external_twitch_client_id: Optional[str]. Client ID for Twitch authentication.
            external_twitch_secret: Optional[str]. Secret for Twitch authentication.
            external_twitter_enabled: Optional[bool]. Enables Twitter as external authentication provider.
            external_twitter_client_id: Optional[str]. Client ID for Twitter authentication.
            external_twitter_secret: Optional[str]. Secret for Twitter authentication.
            external_workos_enabled: Optional[bool]. Enables WorkOS as external authentication provider.
            external_workos_client_id: Optional[str]. Client ID for WorkOS authentication.
            external_workos_secret: Optional[str]. Secret for WorkOS authentication.
            external_workos_url: Optional[str]. WorkOS authentication URL.
            external_zoom_enabled: Optional[bool]. Enables Zoom as external authentication provider.
            external_zoom_client_id: Optional[str]. Client ID for Zoom authentication.
            external_zoom_secret: Optional[str]. Secret for Zoom authentication.
            db_max_pool_size: Optional[int]. Maximum database connection pool size.
            api_max_request_duration: Optional[int]. Maximum duration (in seconds) for API requests.
            mfa_totp_enroll_enabled: Optional[bool]. Enables TOTP enrollment for MFA.
            mfa_totp_verify_enabled: Optional[bool]. Enables TOTP verification for MFA.
            mfa_web_authn_enroll_enabled: Optional[bool]. Enables WebAuthn enrollment for MFA.
            mfa_web_authn_verify_enabled: Optional[bool]. Enables WebAuthn verification for MFA.
            mfa_phone_enroll_enabled: Optional[bool]. Enables phone enrollment for MFA.
            mfa_phone_verify_enabled: Optional[bool]. Enables phone verification for MFA.
            mfa_phone_max_frequency: Optional[int]. Maximum frequency of MFA phone attempts.
            mfa_phone_otp_length: Optional[int]. Length of MFA phone OTP.
            mfa_phone_template: Optional[str]. MFA phone OTP template.

        Returns:
            dict[str, Any]: The updated authentication service configuration as returned by the server.

        Raises:
            ValueError: If the required 'ref' parameter is not provided.
            requests.HTTPError: If the HTTP request to update config fails (e.g., network error or non-2xx response).

        Tags:
            update, auth-config, management, http, patch
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        request_body = {
            "site_url": site_url,
            "disable_signup": disable_signup,
            "jwt_exp": jwt_exp,
            "smtp_admin_email": smtp_admin_email,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_pass": smtp_pass,
            "smtp_max_frequency": smtp_max_frequency,
            "smtp_sender_name": smtp_sender_name,
            "mailer_allow_unverified_email_sign_ins": mailer_allow_unverified_email_sign_ins,
            "mailer_autoconfirm": mailer_autoconfirm,
            "mailer_subjects_invite": mailer_subjects_invite,
            "mailer_subjects_confirmation": mailer_subjects_confirmation,
            "mailer_subjects_recovery": mailer_subjects_recovery,
            "mailer_subjects_email_change": mailer_subjects_email_change,
            "mailer_subjects_magic_link": mailer_subjects_magic_link,
            "mailer_subjects_reauthentication": mailer_subjects_reauthentication,
            "mailer_templates_invite_content": mailer_templates_invite_content,
            "mailer_templates_confirmation_content": mailer_templates_confirmation_content,
            "mailer_templates_recovery_content": mailer_templates_recovery_content,
            "mailer_templates_email_change_content": mailer_templates_email_change_content,
            "mailer_templates_magic_link_content": mailer_templates_magic_link_content,
            "mailer_templates_reauthentication_content": mailer_templates_reauthentication_content,
            "mfa_max_enrolled_factors": mfa_max_enrolled_factors,
            "uri_allow_list": uri_allow_list,
            "external_anonymous_users_enabled": external_anonymous_users_enabled,
            "external_email_enabled": external_email_enabled,
            "external_phone_enabled": external_phone_enabled,
            "saml_enabled": saml_enabled,
            "saml_external_url": saml_external_url,
            "security_captcha_enabled": security_captcha_enabled,
            "security_captcha_provider": security_captcha_provider,
            "security_captcha_secret": security_captcha_secret,
            "sessions_timebox": sessions_timebox,
            "sessions_inactivity_timeout": sessions_inactivity_timeout,
            "sessions_single_per_user": sessions_single_per_user,
            "sessions_tags": sessions_tags,
            "rate_limit_anonymous_users": rate_limit_anonymous_users,
            "rate_limit_email_sent": rate_limit_email_sent,
            "rate_limit_sms_sent": rate_limit_sms_sent,
            "rate_limit_verify": rate_limit_verify,
            "rate_limit_token_refresh": rate_limit_token_refresh,
            "rate_limit_otp": rate_limit_otp,
            "mailer_secure_email_change_enabled": mailer_secure_email_change_enabled,
            "refresh_token_rotation_enabled": refresh_token_rotation_enabled,
            "password_hibp_enabled": password_hibp_enabled,
            "password_min_length": password_min_length,
            "password_required_characters": password_required_characters,
            "security_manual_linking_enabled": security_manual_linking_enabled,
            "security_update_password_require_reauthentication": security_update_password_require_reauthentication,
            "security_refresh_token_reuse_interval": security_refresh_token_reuse_interval,
            "mailer_otp_exp": mailer_otp_exp,
            "mailer_otp_length": mailer_otp_length,
            "sms_autoconfirm": sms_autoconfirm,
            "sms_max_frequency": sms_max_frequency,
            "sms_otp_exp": sms_otp_exp,
            "sms_otp_length": sms_otp_length,
            "sms_provider": sms_provider,
            "sms_messagebird_access_key": sms_messagebird_access_key,
            "sms_messagebird_originator": sms_messagebird_originator,
            "sms_test_otp": sms_test_otp,
            "sms_test_otp_valid_until": sms_test_otp_valid_until,
            "sms_textlocal_api_key": sms_textlocal_api_key,
            "sms_textlocal_sender": sms_textlocal_sender,
            "sms_twilio_account_sid": sms_twilio_account_sid,
            "sms_twilio_auth_token": sms_twilio_auth_token,
            "sms_twilio_content_sid": sms_twilio_content_sid,
            "sms_twilio_message_service_sid": sms_twilio_message_service_sid,
            "sms_twilio_verify_account_sid": sms_twilio_verify_account_sid,
            "sms_twilio_verify_auth_token": sms_twilio_verify_auth_token,
            "sms_twilio_verify_message_service_sid": sms_twilio_verify_message_service_sid,
            "sms_vonage_api_key": sms_vonage_api_key,
            "sms_vonage_api_secret": sms_vonage_api_secret,
            "sms_vonage_from": sms_vonage_from,
            "sms_template": sms_template,
            "hook_mfa_verification_attempt_enabled": hook_mfa_verification_attempt_enabled,
            "hook_mfa_verification_attempt_uri": hook_mfa_verification_attempt_uri,
            "hook_mfa_verification_attempt_secrets": hook_mfa_verification_attempt_secrets,
            "hook_password_verification_attempt_enabled": hook_password_verification_attempt_enabled,
            "hook_password_verification_attempt_uri": hook_password_verification_attempt_uri,
            "hook_password_verification_attempt_secrets": hook_password_verification_attempt_secrets,
            "hook_custom_access_token_enabled": hook_custom_access_token_enabled,
            "hook_custom_access_token_uri": hook_custom_access_token_uri,
            "hook_custom_access_token_secrets": hook_custom_access_token_secrets,
            "hook_send_sms_enabled": hook_send_sms_enabled,
            "hook_send_sms_uri": hook_send_sms_uri,
            "hook_send_sms_secrets": hook_send_sms_secrets,
            "hook_send_email_enabled": hook_send_email_enabled,
            "hook_send_email_uri": hook_send_email_uri,
            "hook_send_email_secrets": hook_send_email_secrets,
            "external_apple_enabled": external_apple_enabled,
            "external_apple_client_id": external_apple_client_id,
            "external_apple_secret": external_apple_secret,
            "external_apple_additional_client_ids": external_apple_additional_client_ids,
            "external_azure_enabled": external_azure_enabled,
            "external_azure_client_id": external_azure_client_id,
            "external_azure_secret": external_azure_secret,
            "external_azure_url": external_azure_url,
            "external_bitbucket_enabled": external_bitbucket_enabled,
            "external_bitbucket_client_id": external_bitbucket_client_id,
            "external_bitbucket_secret": external_bitbucket_secret,
            "external_discord_enabled": external_discord_enabled,
            "external_discord_client_id": external_discord_client_id,
            "external_discord_secret": external_discord_secret,
            "external_facebook_enabled": external_facebook_enabled,
            "external_facebook_client_id": external_facebook_client_id,
            "external_facebook_secret": external_facebook_secret,
            "external_figma_enabled": external_figma_enabled,
            "external_figma_client_id": external_figma_client_id,
            "external_figma_secret": external_figma_secret,
            "external_github_enabled": external_github_enabled,
            "external_github_client_id": external_github_client_id,
            "external_github_secret": external_github_secret,
            "external_gitlab_enabled": external_gitlab_enabled,
            "external_gitlab_client_id": external_gitlab_client_id,
            "external_gitlab_secret": external_gitlab_secret,
            "external_gitlab_url": external_gitlab_url,
            "external_google_enabled": external_google_enabled,
            "external_google_client_id": external_google_client_id,
            "external_google_secret": external_google_secret,
            "external_google_additional_client_ids": external_google_additional_client_ids,
            "external_google_skip_nonce_check": external_google_skip_nonce_check,
            "external_kakao_enabled": external_kakao_enabled,
            "external_kakao_client_id": external_kakao_client_id,
            "external_kakao_secret": external_kakao_secret,
            "external_keycloak_enabled": external_keycloak_enabled,
            "external_keycloak_client_id": external_keycloak_client_id,
            "external_keycloak_secret": external_keycloak_secret,
            "external_keycloak_url": external_keycloak_url,
            "external_linkedin_oidc_enabled": external_linkedin_oidc_enabled,
            "external_linkedin_oidc_client_id": external_linkedin_oidc_client_id,
            "external_linkedin_oidc_secret": external_linkedin_oidc_secret,
            "external_slack_oidc_enabled": external_slack_oidc_enabled,
            "external_slack_oidc_client_id": external_slack_oidc_client_id,
            "external_slack_oidc_secret": external_slack_oidc_secret,
            "external_notion_enabled": external_notion_enabled,
            "external_notion_client_id": external_notion_client_id,
            "external_notion_secret": external_notion_secret,
            "external_slack_enabled": external_slack_enabled,
            "external_slack_client_id": external_slack_client_id,
            "external_slack_secret": external_slack_secret,
            "external_spotify_enabled": external_spotify_enabled,
            "external_spotify_client_id": external_spotify_client_id,
            "external_spotify_secret": external_spotify_secret,
            "external_twitch_enabled": external_twitch_enabled,
            "external_twitch_client_id": external_twitch_client_id,
            "external_twitch_secret": external_twitch_secret,
            "external_twitter_enabled": external_twitter_enabled,
            "external_twitter_client_id": external_twitter_client_id,
            "external_twitter_secret": external_twitter_secret,
            "external_workos_enabled": external_workos_enabled,
            "external_workos_client_id": external_workos_client_id,
            "external_workos_secret": external_workos_secret,
            "external_workos_url": external_workos_url,
            "external_zoom_enabled": external_zoom_enabled,
            "external_zoom_client_id": external_zoom_client_id,
            "external_zoom_secret": external_zoom_secret,
            "db_max_pool_size": db_max_pool_size,
            "api_max_request_duration": api_max_request_duration,
            "mfa_totp_enroll_enabled": mfa_totp_enroll_enabled,
            "mfa_totp_verify_enabled": mfa_totp_verify_enabled,
            "mfa_web_authn_enroll_enabled": mfa_web_authn_enroll_enabled,
            "mfa_web_authn_verify_enabled": mfa_web_authn_verify_enabled,
            "mfa_phone_enroll_enabled": mfa_phone_enroll_enabled,
            "mfa_phone_verify_enabled": mfa_phone_verify_enabled,
            "mfa_phone_max_frequency": mfa_phone_max_frequency,
            "mfa_phone_otp_length": mfa_phone_otp_length,
            "mfa_phone_template": mfa_phone_template,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/config/auth"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_tpafor_project(
        self, ref, oidc_issuer_url=None, jwks_url=None, custom_jwks=None
    ) -> dict[str, Any]:
        """
        Creates a third-party authentication (TPA) configuration for a specific project using provided OIDC or JWKS details.

        Args:
            ref: str. The unique identifier of the project for which to create the third-party auth configuration.
            oidc_issuer_url: str, optional. The OpenID Connect (OIDC) issuer URL for the authentication provider. Defaults to None.
            jwks_url: str, optional. The JSON Web Key Set (JWKS) URL for key verification. Defaults to None.
            custom_jwks: Any, optional. Custom JWKS data to use for authentication. Defaults to None.

        Returns:
            dict[str, Any]: The server response containing details of the created third-party authentication configuration.

        Raises:
            ValueError: If the required parameter 'ref' is missing.
            requests.HTTPError: If the HTTP request fails or the server responds with an error status code.

        Tags:
            create, third-party-auth, project-management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        request_body = {
            "oidc_issuer_url": oidc_issuer_url,
            "jwks_url": jwks_url,
            "custom_jwks": custom_jwks,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/config/auth/third-party-auth"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tpafor_project(self, ref) -> list[Any]:
        """
        Retrieves the list of third-party authentication configurations for a specified project.

        Args:
            ref: str. The reference identifier of the project whose third-party authentication configurations are to be listed.

        Returns:
            list[Any]: A list of dictionaries representing the third-party authentication configurations for the given project.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to the backend service returns an unsuccessful status.

        Tags:
            list, third-party-auth, project-management, api-call
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/config/auth/third-party-auth"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_tpafor_project(self, ref, tpa_id) -> dict[str, Any]:
        """
        Deletes a third-party authentication provider configuration for a given project.

        Args:
            ref: str. The project reference or identifier.
            tpa_id: str. The unique identifier of the third-party authentication provider to delete.

        Returns:
            dict. A JSON dictionary containing the API's response to the deletion request.

        Raises:
            ValueError: Raised if 'ref' or 'tpa_id' is None.
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.

        Tags:
            delete, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if tpa_id is None:
            raise ValueError("Missing required parameter 'tpa_id'")
        url = f"{self.base_url}/v1/projects/{ref}/config/auth/third-party-auth/{tpa_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tpafor_project(self, ref, tpa_id) -> dict[str, Any]:
        """
        Retrieve the third-party authentication configuration for a specific project and TPA identifier.

        Args:
            ref: The unique reference or identifier for the project.
            tpa_id: The identifier of the third-party authentication provider to fetch.

        Returns:
            A dictionary containing the third-party authentication configuration details for the specified project and TPA provider.

        Raises:
            ValueError: Raised if the 'ref' or 'tpa_id' parameters are None.
            HTTPError: Raised if the HTTP request to retrieve the configuration fails with a non-success status code.

        Tags:
            get, fetch, third-party-auth, project, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if tpa_id is None:
            raise ValueError("Missing required parameter 'tpa_id'")
        url = f"{self.base_url}/v1/projects/{ref}/config/auth/third-party-auth/{tpa_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_run_a_query(self, ref, query) -> dict[str, Any]:
        """
        Executes a database query for a specified project reference using the provided query string.

        Args:
            ref: The unique project reference identifier (str) for which the database query will be executed.
            query: The query string (str) to be executed against the database.

        Returns:
            A dictionary containing the JSON-decoded result of the query response.

        Raises:
            ValueError: If either 'ref' or 'query' is None.
            HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            query, database, api, execute
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        request_body = {
            "query": query,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/database/query"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_enable_database_webhook(self, ref) -> Any:
        """
        Enables the database webhook for the specified project reference.

        Args:
            ref: The unique identifier of the project for which to enable the database webhook.

        Returns:
            A dictionary containing the JSON response from the server after enabling the database webhook.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to enable the database webhook fails.

        Tags:
            enable, webhook, database, api, async_job
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/database/webhooks/enable"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_functions(self, ref) -> list[Any]:
        """
        Lists all available functions for the specified project reference.

        Args:
            ref: The unique identifier or reference string for the project whose functions should be listed.

        Returns:
            A list containing information about each available function in the specified project.

        Raises:
            ValueError: Raised if the required 'ref' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the backend API fails or returns an error status.

        Tags:
            list, functions, api, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/functions"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_a_function(self, ref, function_slug) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific function from a project using the function's reference and slug.

        Args:
            ref: str. The unique reference ID of the project.
            function_slug: str. The slug identifier of the function to retrieve.

        Returns:
            dict. A dictionary containing the JSON response with the function's details.

        Raises:
            ValueError: Raised if either 'ref' or 'function_slug' is None.
            requests.HTTPError: Raised if the underlying HTTP request returned an unsuccessful status code.

        Tags:
            get, function, ai, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if function_slug is None:
            raise ValueError("Missing required parameter 'function_slug'")
        url = f"{self.base_url}/v1/projects/{ref}/functions/{function_slug}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_a_function(
        self,
        ref,
        function_slug,
        slug=None,
        name=None,
        verify_jwt=None,
        import_map=None,
        entrypoint_path=None,
        import_map_path=None,
        body=None,
    ) -> dict[str, Any]:
        """
        Updates the configuration or code for an existing function in the specified project.

        Args:
            ref: str. The reference ID of the project containing the function.
            function_slug: str. The unique identifier (slug) for the function to update.
            slug: Optional[str]. If provided, updates the function's slug (identifier).
            name: Optional[str]. Optionally updates the function's display name.
            verify_jwt: Optional[bool]. If set, specifies whether to verify JWT tokens for the function.
            import_map: Optional[str]. Specifies the path or identifier for an import map, if updating.
            entrypoint_path: Optional[str]. Path to the function's entrypoint within the project.
            import_map_path: Optional[str]. Path to the import map file.
            body: Optional[str]. The updated function code or body.

        Returns:
            dict[str, Any]: A dictionary containing the updated function's metadata and settings as returned by the API.

        Raises:
            ValueError: If either 'ref' or 'function_slug' is not provided.
            requests.HTTPError: If the API request fails with an HTTP error status.

        Tags:
            update, function-management, api, patch
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if function_slug is None:
            raise ValueError("Missing required parameter 'function_slug'")
        request_body = {
            "name": name,
            "body": body,
            "verify_jwt": verify_jwt,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/functions/{function_slug}"
        query_params = {
            k: v
            for k, v in [
                ("slug", slug),
                ("name", name),
                ("verify_jwt", verify_jwt),
                ("import_map", import_map),
                ("entrypoint_path", entrypoint_path),
                ("import_map_path", import_map_path),
            ]
            if v is not None
        }
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_delete_a_function(self, ref, function_slug) -> Any:
        """
        Deletes a specified function from a project using its reference and function slug.

        Args:
            ref: The unique identifier or reference for the project containing the function.
            function_slug: The unique slug or identifier of the function to delete.

        Returns:
            The JSON-decoded response from the API after attempting to delete the function.

        Raises:
            ValueError: Raised if either 'ref' or 'function_slug' is None.
            HTTPError: Raised if the HTTP request to delete the function fails (non-2xx status code).

        Tags:
            delete, function-management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if function_slug is None:
            raise ValueError("Missing required parameter 'function_slug'")
        url = f"{self.base_url}/v1/projects/{ref}/functions/{function_slug}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_a_function_body(self, ref, function_slug) -> Any:
        """
        Retrieves the body of a specified function from a project via a REST API call.

        Args:
            ref: The unique identifier (string) of the project containing the function.
            function_slug: The unique slug (string) identifying the function whose body is to be retrieved.

        Returns:
            A dictionary (parsed JSON) containing the function body and related metadata.

        Raises:
            ValueError: If 'ref' or 'function_slug' is not provided.
            HTTPError: If the HTTP request to retrieve the function body fails due to a non-success response.

        Tags:
            get, function-body, api, async-job
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if function_slug is None:
            raise ValueError("Missing required parameter 'function_slug'")
        url = f"{self.base_url}/v1/projects/{ref}/functions/{function_slug}/body"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_buckets(self, ref) -> list[Any]:
        """
        Retrieves a list of all storage buckets for the specified project reference.

        Args:
            ref: The identifier of the project for which to list storage buckets. Must not be None.

        Returns:
            A list containing information about each storage bucket associated with the project.

        Raises:
            ValueError: Raised if the 'ref' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the storage buckets endpoint returns an unsuccessful status.

        Tags:
            list, buckets, storage, project, sync
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/storage/buckets"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_create_a_sso_provider(
        self,
        ref,
        type,
        metadata_xml=None,
        metadata_url=None,
        domains=None,
        attribute_mapping=None,
    ) -> dict[str, Any]:
        """
        Creates a new Single Sign-On (SSO) provider configuration for the specified project.

        Args:
            ref: str. Unique reference or ID of the project where the SSO provider will be added.
            type: str. The type of SSO provider (e.g., 'saml', 'oidc'). Required.
            metadata_xml: Optional[str]. The SAML metadata XML. Required for some types of SSO providers.
            metadata_url: Optional[str]. URL pointing to the SSO provider's metadata. Used as an alternative to 'metadata_xml.'
            domains: Optional[list[str]]. List of domains associated with this SSO provider.
            attribute_mapping: Optional[dict[str, str]]. Mapping of user attributes from the SSO provider to internal fields.

        Returns:
            dict[str, Any]: JSON response containing details of the newly created SSO provider configuration.

        Raises:
            ValueError: If either 'ref' or 'type' is missing or None.
            requests.exceptions.HTTPError: If the API request fails or returns an unsuccessful status.

        Tags:
            create, sso, provider, management, auth
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        request_body = {
            "type": type,
            "metadata_xml": metadata_xml,
            "metadata_url": metadata_url,
            "domains": domains,
            "attribute_mapping": attribute_mapping,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/config/auth/sso/providers"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_sso_provider(self, ref) -> dict[str, Any]:
        """
        Retrieves a list of all SSO providers configured for the specified project.

        Args:
            ref: str. The project reference identifier for which to list SSO providers.

        Returns:
            dict. A dictionary containing the SSO provider configuration details for the project.

        Raises:
            ValueError: If the 'ref' parameter is None.
            requests.HTTPError: If the HTTP request to the backend fails.

        Tags:
            list, sso, providers, management, api
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/config/auth/sso/providers"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_a_sso_provider(self, ref, provider_id) -> dict[str, Any]:
        """
        Retrieves details of a specific SSO provider configuration for the given project reference and provider ID.

        Args:
            ref: str. The unique reference identifier for the project.
            provider_id: str. The identifier of the SSO provider to retrieve.

        Returns:
            dict[str, Any]: A dictionary containing the configuration details of the specified SSO provider.

        Raises:
            ValueError: Raised if 'ref' or 'provider_id' is None.
            requests.HTTPError: Raised if the HTTP request to fetch the SSO provider details fails.

        Tags:
            get, sso-provider, configuration, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if provider_id is None:
            raise ValueError("Missing required parameter 'provider_id'")
        url = (
            f"{self.base_url}/v1/projects/{ref}/config/auth/sso/providers/{provider_id}"
        )
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_update_a_sso_provider(
        self,
        ref,
        provider_id,
        metadata_xml=None,
        metadata_url=None,
        domains=None,
        attribute_mapping=None,
    ) -> dict[str, Any]:
        """
        Updates the configuration of an existing SSO provider using the provided metadata and attributes.

        Args:
            ref: str. Unique reference identifier for the project whose SSO provider configuration is being updated.
            provider_id: str. Identifier of the SSO provider to update.
            metadata_xml: str or None. Optional XML metadata for the SSO provider. If not provided, existing metadata is retained.
            metadata_url: str or None. Optional URL pointing to the metadata XML for the SSO provider.
            domains: list[str] or None. Optional list of domains associated with the SSO provider.
            attribute_mapping: dict or None. Optional mapping of SSO attributes to application-specific fields.

        Returns:
            dict. JSON response containing details of the updated SSO provider configuration.

        Raises:
            ValueError: If either 'ref' or 'provider_id' is not provided.
            requests.HTTPError: If the HTTP request to update the SSO provider fails (e.g., server returns an error status).

        Tags:
            update, sso, provider-management, auth, v1
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if provider_id is None:
            raise ValueError("Missing required parameter 'provider_id'")
        request_body = {
            "metadata_xml": metadata_xml,
            "metadata_url": metadata_url,
            "domains": domains,
            "attribute_mapping": attribute_mapping,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = (
            f"{self.base_url}/v1/projects/{ref}/config/auth/sso/providers/{provider_id}"
        )
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_delete_a_sso_provider(self, ref, provider_id) -> dict[str, Any]:
        """
        Deletes a specified SSO provider from the given project configuration.

        Args:
            ref: str. Unique identifier of the project containing the SSO provider.
            provider_id: str. Unique identifier of the SSO provider to be deleted.

        Returns:
            dict. JSON response from the server indicating the outcome of the delete operation.

        Raises:
            ValueError: If 'ref' or 'provider_id' is None.
            requests.HTTPError: If the HTTP request to delete the provider fails.

        Tags:
            delete, sso-provider, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if provider_id is None:
            raise ValueError("Missing required parameter 'provider_id'")
        url = (
            f"{self.base_url}/v1/projects/{ref}/config/auth/sso/providers/{provider_id}"
        )
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_all_backups(self, ref) -> dict[str, Any]:
        """
        Retrieves a list of all database backups for the specified project reference.

        Args:
            ref: str. The unique project reference identifier used to specify the target project for which to list all database backups.

        Returns:
            dict[str, Any]: A dictionary containing details of all database backups for the specified project.

        Raises:
            ValueError: If 'ref' is None.
            requests.HTTPError: If the HTTP request to retrieve backups fails.

        Tags:
            list, backups, database, sync, management
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        url = f"{self.base_url}/v1/projects/{ref}/database/backups"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_restore_pitr_backup(self, ref, recovery_time_target_unix) -> Any:
        """
        Initiates a point-in-time restore operation for a database backup using the specified reference and recovery time target.

        Args:
            ref: str. The reference identifier of the project whose database backup should be restored.
            recovery_time_target_unix: int. The Unix timestamp representing the target point in time to which the database should be restored.

        Returns:
            dict. The JSON-decoded response containing details about the point-in-time restore operation.

        Raises:
            ValueError: If 'ref' or 'recovery_time_target_unix' is None.
            requests.HTTPError: If the HTTP request to initiate the restore fails or returns an error status.

        Tags:
            restore, backup, database, pitr, async-job, ai
        """
        if ref is None:
            raise ValueError("Missing required parameter 'ref'")
        if recovery_time_target_unix is None:
            raise ValueError("Missing required parameter 'recovery_time_target_unix'")
        request_body = {
            "recovery_time_target_unix": recovery_time_target_unix,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{ref}/database/backups/restore-pitr"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_list_organization_members(self, slug) -> list[Any]:
        """
        Retrieves a list of members associated with the specified organization slug via the v1 API.

        Args:
            slug: str. The unique identifier (slug) of the organization whose members are to be listed.

        Returns:
            list[Any]: A list containing the JSON-parsed member data for the specified organization.

        Raises:
            ValueError: Raised if the 'slug' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint returns an error status.

        Tags:
            list, organization, members, api
        """
        if slug is None:
            raise ValueError("Missing required parameter 'slug'")
        url = f"{self.base_url}/v1/organizations/{slug}/members"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def v1_get_an_organization(self, slug) -> dict[str, Any]:
        """
        Retrieves details of a specific organization by its unique slug identifier.

        Args:
            slug: str. The unique slug identifier for the organization to retrieve.

        Returns:
            dict[str, Any]: A dictionary containing the organization's details as returned by the API.

        Raises:
            ValueError: If the 'slug' parameter is None.
            requests.HTTPError: If the HTTP request to the API fails or the server returns an error response.

        Tags:
            get, organization, api
        """
        if slug is None:
            raise ValueError("Missing required parameter 'slug'")
        url = f"{self.base_url}/v1/organizations/{slug}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.v1_get_a_branch_config,
            self.v1_update_a_branch_config,
            self.v1_delete_a_branch,
            self.v1_reset_a_branch,
            self.v1_list_all_projects,
            self.v1_create_a_project,
            self.v1_list_all_organizations,
            self.v1_create_an_organization,
            self.v1_authorize_user,
            self.v1_list_all_snippets,
            self.v1_get_a_snippet,
            self.v1_get_project_api_keys,
            self.create_api_key,
            self.update_api_key,
            self.delete_api_key,
            self.v1_list_all_branches,
            self.v1_create_a_branch,
            self.v1_disable_preview_branching,
            self.v1_get_hostname_config,
            self.v1_verify_dns_config,
            self.v1_activate_custom_hostname,
            self.v1_list_all_network_bans,
            self.v1_delete_network_bans,
            self.v1_get_network_restrictions,
            self.v1_update_network_restrictions,
            self.v1_get_pgsodium_config,
            self.v1_update_pgsodium_config,
            self.v1_get_postgrest_service_config,
            self.v1_update_postgrest_service_config,
            self.v1_delete_a_project,
            self.v1_list_all_secrets,
            self.v1_bulk_create_secrets,
            self.v1_bulk_delete_secrets,
            self.v1_get_ssl_enforcement_config,
            self.v1_update_ssl_enforcement_config,
            self.v1_generate_typescript_types,
            self.v1_get_vanity_subdomain_config,
            self.v1_deactivate_vanity_subdomain_config,
            self.v1_check_vanity_subdomain_availability,
            self.v1_activate_vanity_subdomain_config,
            self.v1_upgrade_postgres_version,
            self.v1_get_postgrest_upgrade_eligibility,
            self.v1_get_postgrest_upgrade_status,
            self.v1_get_readonly_mode_status,
            self.v1_disable_readonly_mode_temporarily,
            self.v1_setup_a_read_replica,
            self.v1_remove_a_read_replica,
            self.v1_get_services_health,
            self.v1_get_postgres_config,
            self.v1_update_postgres_config,
            self.v1_get_project_pgbouncer_config,
            self.v1_get_supavisor_config,
            self.v1_update_supavisor_config,
            self.v1_get_auth_service_config,
            self.v1_update_auth_service_config,
            self.create_tpafor_project,
            self.list_tpafor_project,
            self.delete_tpafor_project,
            self.get_tpafor_project,
            self.v1_run_a_query,
            self.v1_enable_database_webhook,
            self.v1_list_all_functions,
            self.v1_get_a_function,
            self.v1_update_a_function,
            self.v1_delete_a_function,
            self.v1_get_a_function_body,
            self.v1_list_all_buckets,
            self.v1_create_a_sso_provider,
            self.v1_list_all_sso_provider,
            self.v1_get_a_sso_provider,
            self.v1_update_a_sso_provider,
            self.v1_delete_a_sso_provider,
            self.v1_list_all_backups,
            self.v1_restore_pitr_backup,
            self.v1_list_organization_members,
            self.v1_get_an_organization,
        ]
