from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class OfficialWrikeCollectionV21App(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes the Official Wrike Collection V2.1 application with the specified integration and configuration options.
        
        Args:
            integration: Integration, optional. The Integration instance to associate with this application. Defaults to None.
            **kwargs: Additional keyword arguments passed to the parent class initializer.
        
        Returns:
            None. This constructor initializes the instance in place.
        """
        super().__init__(name='wrike', integration=integration, **kwargs)
        self.base_url = "https://www.wrike.com/api/v4"

    def _get_headers(self):
        if not self.integration:
            raise ValueError("Integration not configured for GmailApp")
        credentials = self.integration.get_credentials()

        if "headers" in credentials:
            return credentials["headers"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json",
        }   


    def get_contacts(self, deleted=None, fields=None, metadata=None) -> Any:
        """
        Retrieves a list of contacts from the server, optionally filtering by deletion status, specific fields, or metadata.
        
        Args:
            deleted: Optional[bool]. If provided, filters contacts by their deletion status.
            fields: Optional[str or list]. If provided, specifies which fields to include in the returned contact data.
            metadata: Optional[dict or str]. If provided, adds additional metadata parameters to the request.
        
        Returns:
            The server's JSON response as a Python object, typically containing a list of contacts matching the specified filters.
        """
        url = f"{self.base_url}/contacts"
        query_params = {k: v for k, v in [('deleted', deleted), ('fields', fields), ('metadata', metadata)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_contacts_by_contactid(self, contactId, fields=None) -> Any:
        """
        Retrieves contact details by contact ID from the API, allowing optional selection of specific fields.
        
        Args:
            contactId: The unique identifier of the contact to retrieve.
            fields: Optional. A comma-separated string specifying which contact fields to include in the response. If None, all fields are returned.
        
        Returns:
            A JSON-decoded object containing the contact's details as returned by the API.
        """
        if contactId is None:
            raise ValueError("Missing required parameter 'contactId'")
        url = f"{self.base_url}/contacts/{contactId}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_contacts_by_contactid(self, contactId, request_body) -> Any:
        """
        Updates a contact with the specified contact ID using the provided data.
        
        Args:
            contactId: str. The unique identifier of the contact to update.
            request_body: dict. The data to update the contact with.
        
        Returns:
            dict. The JSON response from the server after updating the contact.
        """
        if contactId is None:
            raise ValueError("Missing required parameter 'contactId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/contacts/{contactId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_by_userid(self, userId) -> Any:
        """
        Retrieves user information for a given user ID using a GET request to the '/users/{userId}' endpoint.
        
        Args:
            userId: The unique identifier of the user to retrieve.
        
        Returns:
            The deserialized JSON response containing user information as returned by the API.
        """
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/users/{userId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_users_by_userid(self, userId, request_body) -> Any:
        """
        Updates a user resource identified by userId with the provided request body via an HTTP PUT request.
        
        Args:
            userId: The unique identifier of the user to update.
            request_body: The data to update the user with, typically a dictionary representing the user's updated information.
        
        Returns:
            The response data from the server as a deserialized JSON object.
        """
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/users/{userId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups(self, metadata=None, pageSize=None, pageToken=None, fields=None) -> Any:
        """
        Retrieves a list of groups from the API, applying optional filters and pagination parameters.
        
        Args:
            metadata: Optional metadata to filter returned groups. If specified, only groups matching the provided metadata will be included.
            pageSize: Optional integer specifying the maximum number of groups to return in the response.
            pageToken: Optional token for pagination, indicating where to continue listing groups after a previous request.
            fields: Optional string specifying a comma-separated list of fields to include in a partial response.
        
        Returns:
            A JSON-decoded object containing the list of groups and any additional metadata as returned by the API.
        """
        url = f"{self.base_url}/groups"
        query_params = {k: v for k, v in [('metadata', metadata), ('pageSize', pageSize), ('pageToken', pageToken), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_groups(self, request_body) -> Any:
        """
        Creates a new group by sending a POST request with the provided request body.
        
        Args:
            request_body: The data to include in the POST request body, defining the group to be created. Must not be None.
        
        Returns:
            The parsed JSON response from the server as a Python object.
        """
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/groups"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups_by_groupid(self, groupId, fields=None) -> Any:
        """
        Retrieves group information by group ID from the API, optionally including only specified fields.
        
        Args:
            groupId: The unique identifier of the group to retrieve.
            fields: Optional; a comma-separated string specifying which fields to include in the response.
        
        Returns:
            A deserialized JSON object containing the group details as returned by the API.
        """
        if groupId is None:
            raise ValueError("Missing required parameter 'groupId'")
        url = f"{self.base_url}/groups/{groupId}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_groups_by_groupid(self, groupId, request_body) -> Any:
        """
        Updates a group's details by group ID using a PUT request and returns the server response as a JSON object.
        
        Args:
            groupId: str. The unique identifier of the group to update. Must not be None.
            request_body: Any. The data payload to update the group with. Typically a dictionary representing the new group details. Must not be None.
        
        Returns:
            Any. The parsed JSON response from the server after the group update request is completed.
        """
        if groupId is None:
            raise ValueError("Missing required parameter 'groupId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/groups/{groupId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_groups_by_groupid(self, groupId) -> Any:
        """
        Deletes a group by its unique group ID via an HTTP DELETE request and returns the server's JSON response.
        
        Args:
            groupId: The unique identifier of the group to be deleted. Must not be None.
        
        Returns:
            Parsed JSON data from the server's response, typically containing the result of the deletion operation.
        """
        if groupId is None:
            raise ValueError("Missing required parameter 'groupId'")
        url = f"{self.base_url}/groups/{groupId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_groups_bulk(self, request_body) -> Any:
        """
        Sends a bulk update request for groups using a PUT HTTP request.
        
        Args:
            request_body: The payload for the bulk group update, typically a dictionary representing the data to be sent. Must not be None.
        
        Returns:
            The parsed JSON response from the server as returned by the bulk groups update API.
        """
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/groups_bulk"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_invitations(self, ) -> Any:
        """
        Retrieves a list of invitation objects from the server using a GET request.
        
        Args:
            self: The instance of the class containing configuration such as base_url and authentication.
        
        Returns:
            The server response parsed as JSON, typically a list of invitations or an object containing invitation data.
        """
        url = f"{self.base_url}/invitations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_invitations(self, request_body) -> Any:
        """
        Sends a POST request to create invitations using the given request body.
        
        Args:
            request_body: The data to include in the body of the invitation creation request. Must not be None.
        
        Returns:
            The parsed JSON response from the server after posting the invitations.
        """
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/invitations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_invitations_by_invitationid(self, invitationId, request_body) -> Any:
        """
        Updates an invitation resource identified by invitationId with the provided request body using an HTTP PUT request.
        
        Args:
            invitationId: str. Unique identifier of the invitation to update.
            request_body: Any. The data to update the invitation resource with, typically as a dictionary or JSON-serializable object.
        
        Returns:
            Any. The parsed JSON response from the server after updating the invitation.
        """
        if invitationId is None:
            raise ValueError("Missing required parameter 'invitationId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/invitations/{invitationId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_invitations_by_invitationid(self, invitationId) -> Any:
        """
        Deletes an invitation identified by the given invitation ID.
        
        Args:
            invitationId: The unique identifier of the invitation to delete. Must not be None.
        
        Returns:
            The JSON-decoded response from the API after the invitation has been deleted.
        """
        if invitationId is None:
            raise ValueError("Missing required parameter 'invitationId'")
        url = f"{self.base_url}/invitations/{invitationId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_ccount(self, fields=None) -> Any:
        """
        Retrieves account information from the API, optionally filtering the fields returned.
        
        Args:
            fields: Optional parameter specifying which account fields to include in the response. If None, all available fields are returned.
        
        Returns:
            A JSON-deserialized object containing the account details as returned by the API.
        """
        url = f"{self.base_url}/account"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_a_ccount(self, request_body) -> Any:
        """
        Updates an account by sending a PUT request with the provided request body to the account endpoint.
        
        Args:
            request_body: The data to be sent in the PUT request body for updating the account. Must not be None.
        
        Returns:
            The JSON-decoded response from the account update request.
        """
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/account"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_workflows(self, ) -> Any:
        """
        Retrieves all workflows from the server as a JSON object.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A JSON-decoded object representing the list of workflows returned by the server.
        """
        url = f"{self.base_url}/workflows"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_workflows(self, name=None, request_body=None) -> Any:
        """
        Creates a new workflow by sending a POST request with optional name and request body.
        
        Args:
            name: Optional; str. The name of the workflow to be created. Included as a query parameter if provided.
            request_body: Optional; dict or compatible object. The request body containing workflow data to create.
        
        Returns:
            The parsed JSON response from the server as a Python object.
        """
        url = f"{self.base_url}/workflows"
        query_params = {k: v for k, v in [('name', name)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_workflows_by_workflowid(self, workflowId, name=None, hidden=None, request_body=None) -> Any:
        """
        Updates a workflow's details by workflow ID using a PUT request.
        
        Args:
            workflowId: str. The unique identifier of the workflow to update. This parameter is required.
            name: Optional[str]. The new name of the workflow. If not provided, the name will not be changed.
            hidden: Optional[bool]. Whether the workflow should be hidden. If not provided, the value will not be changed.
            request_body: Optional[Any]. The request payload containing workflow details to be updated.
        
        Returns:
            Any. The parsed JSON response from the API after updating the workflow.
        """
        if workflowId is None:
            raise ValueError("Missing required parameter 'workflowId'")
        url = f"{self.base_url}/workflows/{workflowId}"
        query_params = {k: v for k, v in [('name', name), ('hidden', hidden)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_customfields(self, ) -> Any:
        """
        Retrieves all custom fields from the API endpoint as a JSON object.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            The response from the API parsed as a JSON-compatible object containing the custom fields.
        """
        url = f"{self.base_url}/customfields"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_customfields(self, title, type, spaceId=None, sharing=None, shareds=None, settings=None, request_body=None) -> Any:
        """
        Creates a custom field by sending a POST request with the specified parameters and request body.
        
        Args:
            title: str. The name of the custom field to be created. Required.
            type: str. The type of the custom field (e.g., 'text', 'number'). Required.
            spaceId: Optional[str]. The ID of the space where the custom field will be added. Default is None.
            sharing: Optional[str]. Determines the sharing settings for the custom field. Default is None.
            shareds: Optional[str]. Comma-separated IDs the custom field is shared with. Default is None.
            settings: Optional[str]. Additional settings for the custom field as a JSON-encoded string. Default is None.
            request_body: Optional[Any]. The request body payload to be sent with the POST request. Default is None.
        
        Returns:
            Any. The JSON-decoded response from the API after creating the custom field.
        """
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        url = f"{self.base_url}/customfields"
        query_params = {k: v for k, v in [('title', title), ('type', type), ('spaceId', spaceId), ('sharing', sharing), ('shareds', shareds), ('settings', settings)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_customfields_by_customfieldid(self, customFieldId) -> Any:
        """
        Retrieves the details of a custom field by its unique custom field ID.
        
        Args:
            customFieldId: The unique identifier of the custom field to retrieve. Must not be None.
        
        Returns:
            A dictionary containing the details of the requested custom field retrieved from the API.
        """
        if customFieldId is None:
            raise ValueError("Missing required parameter 'customFieldId'")
        url = f"{self.base_url}/customfields/{customFieldId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_customfields_by_customfieldid(self, customFieldId, title=None, type=None, changeScope=None, spaceId=None, sharing=None, addShareds=None, removeShareds=None, settings=None, addMirrors=None, removeMirrors=None) -> Any:
        """
        Updates the properties of a custom field identified by its ID using the provided parameters.
        
        Args:
            customFieldId: The unique identifier of the custom field to update. Required.
            title: The new title for the custom field. Optional.
            type: The field type to set. Optional.
            changeScope: Specifies the scope of the changes. Optional.
            spaceId: ID of the space related to the custom field. Optional.
            sharing: Configures sharing settings for the custom field. Optional.
            addShareds: List of identities to share the custom field with. Optional.
            removeShareds: List of identities to remove from sharing. Optional.
            settings: Additional settings for the custom field. Optional.
            addMirrors: List of IDs to mirror on the custom field. Optional.
            removeMirrors: List of IDs to remove from mirroring. Optional.
        
        Returns:
            The JSON-decoded server response containing the updated custom field details.
        """
        if customFieldId is None:
            raise ValueError("Missing required parameter 'customFieldId'")
        url = f"{self.base_url}/customfields/{customFieldId}"
        query_params = {k: v for k, v in [('title', title), ('type', type), ('changeScope', changeScope), ('spaceId', spaceId), ('sharing', sharing), ('addShareds', addShareds), ('removeShareds', removeShareds), ('settings', settings), ('addMirrors', addMirrors), ('removeMirrors', removeMirrors)] if v is not None}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_customfields_by_customfieldid(self, customFieldId) -> Any:
        """
        Deletes a custom field by its unique custom field ID.
        
        Args:
            customFieldId: The unique identifier of the custom field to be deleted.
        
        Returns:
            A dictionary containing the API response data after the custom field has been deleted.
        """
        if customFieldId is None:
            raise ValueError("Missing required parameter 'customFieldId'")
        url = f"{self.base_url}/customfields/{customFieldId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders(self, permalink=None, descendants=None, metadata=None, customFields=None, updatedDate=None, withInvitations=None, project=None, deleted=None, contractTypes=None, plainTextCustomFields=None, customItemTypes=None, pageSize=None, nextPageToken=None, fields=None) -> Any:
        """
        Retrieves a list of folders from the API, filtered by optional query parameters.
        
        Args:
            permalink: Optional; str. A folder permalink to filter results.
            descendants: Optional; bool or str. Whether to include descendant folders.
            metadata: Optional; dict or list. Metadata to filter folders by specific key-value pairs.
            customFields: Optional; dict or list. Custom fields to filter folders.
            updatedDate: Optional; str or datetime. Only return folders updated on or after this date.
            withInvitations: Optional; bool or str. Whether to include folders with invitations.
            project: Optional; str or int. Project identifier to filter folders.
            deleted: Optional; bool or str. Whether to include deleted folders.
            contractTypes: Optional; list or str. Filter folders by contract types.
            plainTextCustomFields: Optional; bool or str. Whether to treat custom fields as plain text.
            customItemTypes: Optional; list or str. Filter by custom item types.
            pageSize: Optional; int. The maximum number of items to return per page.
            nextPageToken: Optional; str. Token for fetching the next page of results.
            fields: Optional; str or list. Specific fields to include in the response.
        
        Returns:
            dict. The JSON-decoded response from the API containing the list of folders and additional pagination data as provided by the backend.
        """
        url = f"{self.base_url}/folders"
        query_params = {k: v for k, v in [('permalink', permalink), ('descendants', descendants), ('metadata', metadata), ('customFields', customFields), ('updatedDate', updatedDate), ('withInvitations', withInvitations), ('project', project), ('deleted', deleted), ('contractTypes', contractTypes), ('plainTextCustomFields', plainTextCustomFields), ('customItemTypes', customItemTypes), ('pageSize', pageSize), ('nextPageToken', nextPageToken), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_by_folderid_folders(self, folderId, permalink=None, descendants=None, metadata=None, customFields=None, updatedDate=None, withInvitations=None, project=None, contractTypes=None, plainTextCustomFields=None, customItemTypes=None, pageSize=None, nextPageToken=None, fields=None) -> Any:
        """
        Retrieves a list of subfolders within a specified folder, applying optional filters such as metadata, custom fields, invitations, project, contract types, pagination, and response fields.
        
        Args:
            folderId: str. The unique identifier of the parent folder whose subfolders are to be retrieved.
            permalink: str, optional. Filter folders by permalink value.
            descendants: bool, optional. If True, include all descendant folders recursively.
            metadata: str or dict, optional. Filter folders by specific metadata.
            customFields: str or dict, optional. Filter folders by custom field values.
            updatedDate: str, optional. Filter folders updated since this date (ISO 8601 format).
            withInvitations: bool, optional. If True, include folders with invitations.
            project: str, optional. Filter folders by associated project.
            contractTypes: str or list, optional. Filter folders by contract type(s).
            plainTextCustomFields: bool, optional. If True, treat custom fields as plain text.
            customItemTypes: str or list, optional. Filter folders by custom item types.
            pageSize: int, optional. The maximum number of results to return in a single page.
            nextPageToken: str, optional. Token for fetching the next page of results.
            fields: str or list, optional. Specifies which fields to include in the response.
        
        Returns:
            dict. The JSON-decoded response containing the list of subfolders matching the provided criteria.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        url = f"{self.base_url}/folders/{folderId}/folders"
        query_params = {k: v for k, v in [('permalink', permalink), ('descendants', descendants), ('metadata', metadata), ('customFields', customFields), ('updatedDate', updatedDate), ('withInvitations', withInvitations), ('project', project), ('contractTypes', contractTypes), ('plainTextCustomFields', plainTextCustomFields), ('customItemTypes', customItemTypes), ('pageSize', pageSize), ('nextPageToken', nextPageToken), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_by_folderid_folders(self, folderId, request_body) -> Any:
        """
        Creates a subfolder within a specified parent folder by sending a POST request with the provided request body.
        
        Args:
            folderId: str. The unique identifier of the parent folder in which to create the subfolder.
            request_body: dict. The request payload containing the properties of the subfolder to be created.
        
        Returns:
            dict. The JSON response from the API representing the newly created subfolder.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/folders/{folderId}/folders"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_folders_by_folderid(self, folderId) -> Any:
        """
        Deletes a folder specified by its folder ID via an HTTP DELETE request.
        
        Args:
            folderId: The unique identifier of the folder to be deleted. Must not be None.
        
        Returns:
            The parsed JSON response from the API after the folder is deleted.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        url = f"{self.base_url}/folders/{folderId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_by_folderid(self, folderId, request_body) -> Any:
        """
        Updates a folder resource by its folder ID using the provided request body.
        
        Args:
            folderId: str. The unique identifier of the folder to update.
            request_body: Any. The data to be sent in the request body for updating the folder.
        
        Returns:
            Any. The parsed JSON response from the server after the folder update request.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/folders/{folderId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tasks(self, descendants=None, title=None, status=None, importance=None, startDate=None, dueDate=None, scheduledDate=None, createdDate=None, updatedDate=None, completedDate=None, authors=None, responsibles=None, responsiblePlaceholders=None, permalink=None, type=None, limit=None, sortField=None, sortOrder=None, subTasks=None, pageSize=None, nextPageToken=None, metadata=None, customField=None, customFields=None, customStatuses=None, withInvitations=None, billingTypes=None, plainTextCustomFields=None, customItemTypes=None, fields=None) -> Any:
        """
        Retrieves a list of tasks from the server with optional filters and pagination parameters.
        
        Args:
            descendants: Optional[bool]. If True, include descendant tasks in the results.
            title: Optional[str]. Filter tasks by their title.
            status: Optional[str or list]. Filter tasks by status or statuses.
            importance: Optional[str or int]. Filter tasks by importance level.
            startDate: Optional[str or date]. Filter tasks by their start date.
            dueDate: Optional[str or date]. Filter tasks by their due date.
            scheduledDate: Optional[str or date]. Filter tasks by their scheduled date.
            createdDate: Optional[str or date]. Filter tasks by creation date.
            updatedDate: Optional[str or date]. Filter tasks by last update date.
            completedDate: Optional[str or date]. Filter tasks by completion date.
            authors: Optional[str or list]. Filter tasks by author(s).
            responsibles: Optional[str or list]. Filter tasks by responsible user(s).
            responsiblePlaceholders: Optional[str or list]. Filter by responsible placeholders.
            permalink: Optional[str]. Filter tasks by permalink.
            type: Optional[str]. Filter tasks by type.
            limit: Optional[int]. Maximum number of tasks to return.
            sortField: Optional[str]. Field name to sort tasks by.
            sortOrder: Optional[str]. Sort order: 'asc' or 'desc'.
            subTasks: Optional[bool]. If True, include subtasks.
            pageSize: Optional[int]. Number of tasks per page.
            nextPageToken: Optional[str]. Token for retrieving the next page of results.
            metadata: Optional[bool]. If True, include metadata in the response.
            customField: Optional[str or dict]. Filter tasks by a specific custom field.
            customFields: Optional[list or dict]. Filter tasks by multiple custom fields.
            customStatuses: Optional[list]. Filter tasks by custom statuses.
            withInvitations: Optional[bool]. If True, include tasks with invitations.
            billingTypes: Optional[list or str]. Filter tasks by billing types.
            plainTextCustomFields: Optional[bool]. If True, return custom fields as plain text.
            customItemTypes: Optional[list or str]. Filter by custom item types.
            fields: Optional[list or str]. Specify which fields to include in the response.
        
        Returns:
            A JSON-decoded object containing the list of tasks and related metadata as provided by the server.
        """
        url = f"{self.base_url}/tasks"
        query_params = {k: v for k, v in [('descendants', descendants), ('title', title), ('status', status), ('importance', importance), ('startDate', startDate), ('dueDate', dueDate), ('scheduledDate', scheduledDate), ('createdDate', createdDate), ('updatedDate', updatedDate), ('completedDate', completedDate), ('authors', authors), ('responsibles', responsibles), ('responsiblePlaceholders', responsiblePlaceholders), ('permalink', permalink), ('type', type), ('limit', limit), ('sortField', sortField), ('sortOrder', sortOrder), ('subTasks', subTasks), ('pageSize', pageSize), ('nextPageToken', nextPageToken), ('metadata', metadata), ('customField', customField), ('customFields', customFields), ('customStatuses', customStatuses), ('withInvitations', withInvitations), ('billingTypes', billingTypes), ('plainTextCustomFields', plainTextCustomFields), ('customItemTypes', customItemTypes), ('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tasks_by_taskid(self, taskId, fields=None) -> Any:
        """
        Retrieve detailed information about a specific task by its task ID from the remote API.
        
        Args:
            taskId: The unique identifier of the task to retrieve. Must not be None.
            fields: Optional; a comma-separated string specifying the fields to include in the response. If None, all default fields are returned.
        
        Returns:
            A JSON-deserialized object containing the task details as returned by the API.
        """
        if taskId is None:
            raise ValueError("Missing required parameter 'taskId'")
        url = f"{self.base_url}/tasks/{taskId}"
        query_params = {k: v for k, v in [('fields', fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_tasks_by_taskid(self, taskId, request_body) -> Any:
        """
        Updates a task by its task ID using a PUT request and returns the updated task data as JSON.
        
        Args:
            taskId: str. The unique identifier of the task to update.
            request_body: dict. The request payload containing updated task data.
        
        Returns:
            dict. The JSON-decoded response containing the updated task information.
        """
        if taskId is None:
            raise ValueError("Missing required parameter 'taskId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/tasks/{taskId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_tasks_by_taskid(self, taskId) -> Any:
        """
        Deletes a task identified by its task ID from the remote server and returns the server response.
        
        Args:
            taskId: The unique identifier of the task to be deleted. Must not be None.
        
        Returns:
            A JSON-decoded object containing the response data from the server after the task is deleted.
        """
        if taskId is None:
            raise ValueError("Missing required parameter 'taskId'")
        url = f"{self.base_url}/tasks/{taskId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_by_folderid_tasks(self, folderId, request_body) -> Any:
        """
        No documentation available
        
        Args:
            None: This function takes no arguments
        
        Returns:
            None
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        if request_body is None:
            raise ValueError("Missing required request body")
        url = f"{self.base_url}/folders/{folderId}/tasks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of tool method references for managing contacts, users, groups, invitations, accounts, workflows, custom fields, folders, and tasks in the system.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            list: A list of method references providing various tool operations, such as retrieving, updating, creating, or deleting contacts, users, groups, invitations, accounts, workflows, custom fields, folders, and tasks.
        """
        return [
            self.get_contacts,
            self.get_contacts_by_contactid,
            self.put_contacts_by_contactid,
            self.get_users_by_userid,
            self.put_users_by_userid,
            self.get_groups,
            self.post_groups,
            self.get_groups_by_groupid,
            self.put_groups_by_groupid,
            self.delete_groups_by_groupid,
            self.put_groups_bulk,
            self.get_invitations,
            self.post_invitations,
            self.put_invitations_by_invitationid,
            self.delete_invitations_by_invitationid,
            self.get_a_ccount,
            self.put_a_ccount,
            self.get_workflows,
            self.post_workflows,
            self.put_workflows_by_workflowid,
            self.get_customfields,
            self.post_customfields,
            self.get_customfields_by_customfieldid,
            self.put_customfields_by_customfieldid,
            self.delete_customfields_by_customfieldid,
            self.get_folders,
            self.get_folders_by_folderid_folders,
            self.post_folders_by_folderid_folders,
            self.delete_folders_by_folderid,
            self.put_folders_by_folderid,
            self.get_tasks,
            self.get_tasks_by_taskid,
            self.put_tasks_by_taskid,
            self.delete_tasks_by_taskid,
            self.post_folders_by_folderid_tasks
        ]
