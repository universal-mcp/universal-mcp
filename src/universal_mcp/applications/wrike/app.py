from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class WrikeApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes the OfficialWrikeCollectionV21App with a specified integration and additional keyword arguments.

        Args:
            integration: Integration, optional. The integration instance to associate with this app. Defaults to None.
            **kwargs: Additional keyword arguments passed to the superclass initializer.

        Returns:
            None. This constructor initializes the instance in place.
        """
        super().__init__(name="wrike", integration=integration, **kwargs)
        self.base_url = "https://www.wrike.com/api/v4"

    def get_contacts(self, deleted=None, fields=None, metadata=None) -> Any:
        """
        Retrieves a list of contacts from the server, with optional filtering and field selection.

        Args:
            deleted: Optional[bool]. If set, filters contacts by their deleted status. Only contacts matching the specified deleted state are returned.
            fields: Optional[str]. Comma-separated list of fields to include in the response for each contact. Limits the contact fields returned.
            metadata: Optional[str]. Comma-separated list of metadata fields to include in the response. Filters which metadata is returned for each contact.

        Returns:
            The JSON-decoded response from the server containing contact information, as a Python object (such as a list or dictionary) depending on the backend API response structure.
        """
        url = f"{self.base_url}/contacts"
        query_params = {
            k: v
            for k, v in [
                ("deleted", deleted),
                ("fields", fields),
                ("metadata", metadata),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_contacts_by_contactid(self, contactId, fields=None) -> Any:
        """
        Retrieves contact information for a specific contact ID, optionally returning only specified fields.

        Args:
            contactId: The unique identifier of the contact to retrieve. Must not be None.
            fields: Optional; a comma-separated string specifying which fields to include in the response. If None, all fields are returned.

        Returns:
            A JSON-decoded object containing the contact's details as returned by the API.
        """
        if contactId is None:
            raise ValueError("Missing required parameter 'contactId'")
        url = f"{self.base_url}/contacts/{contactId}"
        query_params = {k: v for k, v in [("fields", fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_contacts_by_contactid(
        self,
        contactId,
        metadata=None,
        currentBillRate=None,
        currentCostRate=None,
        jobRoleId=None,
        customFields=None,
        fields=None,
    ) -> Any:
        """
        Updates an existing contact by contact ID with provided details such as metadata, billing and cost rates, job role, custom fields, or additional fields.

        Args:
            contactId: The unique identifier of the contact to update. Must not be None.
            metadata: Optional metadata dictionary for the contact (default is None).
            currentBillRate: Optional current bill rate for the contact (default is None).
            currentCostRate: Optional current cost rate for the contact (default is None).
            jobRoleId: Optional job role identifier associated with the contact (default is None).
            customFields: Optional dictionary of custom contact fields (default is None).
            fields: Optional list of specific fields to include in the response (default is None).

        Returns:
            The JSON-decoded response containing the updated contact details.
        """
        if contactId is None:
            raise ValueError("Missing required parameter 'contactId'")
        request_body = {
            "metadata": metadata,
            "currentBillRate": currentBillRate,
            "currentCostRate": currentCostRate,
            "jobRoleId": jobRoleId,
            "customFields": customFields,
            "fields": fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/contacts/{contactId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_by_userid(self, userId) -> Any:
        """
        Retrieves user information for a given user ID from the API endpoint.

        Args:
            userId: The unique identifier of the user whose information is to be retrieved.

        Returns:
            A JSON-decoded object containing user details as returned by the API.
        """
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/users/{userId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_users_by_userid(self, userId, profile=None) -> Any:
        """
        Updates a user's profile information by user ID using a PUT request.

        Args:
            userId: str. The unique identifier of the user. Must not be None.
            profile: dict or None. Optional. The profile information to update for the user. If None, no profile data is sent.

        Returns:
            Any. The parsed JSON response from the server after updating the user's information.
        """
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        request_body = {
            "profile": profile,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/{userId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups(
        self, metadata=None, pageSize=None, pageToken=None, fields=None
    ) -> Any:
        """
        Retrieves a list of groups from the API, applying optional filtering and pagination parameters.

        Args:
            metadata: Optional. Specifies additional metadata to include or filter by in the group results.
            pageSize: Optional. The maximum number of groups to return in the response.
            pageToken: Optional. A token identifying the page of results to return, for pagination.
            fields: Optional. Selector specifying a subset of fields to include in the response.

        Returns:
            The API response parsed as a JSON-compatible object, typically a dictionary containing group information.
        """
        url = f"{self.base_url}/groups"
        query_params = {
            k: v
            for k, v in [
                ("metadata", metadata),
                ("pageSize", pageSize),
                ("pageToken", pageToken),
                ("fields", fields),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_groups(
        self, title, members=None, parent=None, avatar=None, metadata=None
    ) -> Any:
        """
        Creates a new group with the specified title and optional details, sending a POST request to the groups endpoint.

        Args:
            title: str. The name of the group to create. This parameter is required.
            members: Optional[list]. List of member identifiers to include in the group.
            parent: Optional[str]. Identifier of the parent group, if applicable.
            avatar: Optional[Any]. Avatar image or data to associate with the group.
            metadata: Optional[dict]. Additional metadata or custom fields for the group.

        Returns:
            Any. A dictionary containing the response data representing the created group.
        """
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        request_body = {
            "title": title,
            "members": members,
            "parent": parent,
            "avatar": avatar,
            "metadata": metadata,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/groups"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_groups_by_groupid(self, groupId, fields=None) -> Any:
        """
        Retrieves details for a specific group by its group ID, optionally returning only specified fields.

        Args:
            groupId: str. The unique identifier of the group to retrieve. Must not be None.
            fields: Optional[str]. A comma-separated list of fields to include in the response. If None, all fields are returned.

        Returns:
            dict. A dictionary containing the group details as returned by the API.
        """
        if groupId is None:
            raise ValueError("Missing required parameter 'groupId'")
        url = f"{self.base_url}/groups/{groupId}"
        query_params = {k: v for k, v in [("fields", fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_groups_by_groupid(
        self,
        groupId,
        title=None,
        addMembers=None,
        removeMembers=None,
        addInvitations=None,
        removeInvitations=None,
        parent=None,
        avatar=None,
        metadata=None,
    ) -> Any:
        """
        Updates an existing group identified by groupId with new properties and membership changes via a PUT request.

        Args:
            groupId: str. The unique identifier of the group to update. Required.
            title: str, optional. The new title for the group.
            addMembers: list or None, optional. List of member identifiers to add to the group.
            removeMembers: list or None, optional. List of member identifiers to remove from the group.
            addInvitations: list or None, optional. List of invitations to add to the group.
            removeInvitations: list or None, optional. List of invitations to remove from the group.
            parent: str or None, optional. The new parent group identifier, if setting or changing the hierarchy.
            avatar: str or None, optional. New avatar for the group, typically a URL or encoded image data.
            metadata: dict or None, optional. Additional metadata to attach to the group.

        Returns:
            dict. The JSON response from the server containing the updated group details.
        """
        if groupId is None:
            raise ValueError("Missing required parameter 'groupId'")
        request_body = {
            "title": title,
            "addMembers": addMembers,
            "removeMembers": removeMembers,
            "addInvitations": addInvitations,
            "removeInvitations": removeInvitations,
            "parent": parent,
            "avatar": avatar,
            "metadata": metadata,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/groups/{groupId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_groups_by_groupid(self, groupId) -> Any:
        """
        Deletes a group resource identified by the provided groupId using an HTTP DELETE request.

        Args:
            groupId: str. The unique identifier of the group to be deleted. Must not be None.

        Returns:
            Any. The JSON-decoded response from the API after deleting the group.
        """
        if groupId is None:
            raise ValueError("Missing required parameter 'groupId'")
        url = f"{self.base_url}/groups/{groupId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_groups_bulk(self, members) -> Any:
        """
        Updates multiple group memberships in bulk by sending a PUT request with the given members data.

        Args:
            members: List or collection of member data to be processed in bulk. Must not be None.

        Returns:
            Parsed JSON response from the API containing the result of the bulk update operation.
        """
        if members is None:
            raise ValueError("Missing required parameter 'members'")
        request_body = {
            "members": members,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/groups_bulk"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_invitations(
        self,
    ) -> Any:
        """
        Retrieves all invitations from the server using a GET request.

        Args:
            None: This function takes no arguments

        Returns:
            The JSON-decoded response containing invitation data from the server.
        """
        url = f"{self.base_url}/invitations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_invitations(
        self,
        email,
        firstName=None,
        lastName=None,
        role=None,
        external=None,
        subject=None,
        message=None,
        userTypeId=None,
    ) -> Any:
        """
        Sends an invitation email to a user with optional details such as name, role, and custom message.

        Args:
            email: str. The email address of the user to invite. Required.
            firstName: str, optional. The first name of the invitee.
            lastName: str, optional. The last name of the invitee.
            role: str, optional. The role to assign to the invited user.
            external: bool, optional. Indicates if the invitation is for an external user.
            subject: str, optional. Custom subject line for the invitation email.
            message: str, optional. Custom message to include in the invitation.
            userTypeId: Any, optional. The user type identifier to associate with the invitation.

        Returns:
            Any. The server's parsed JSON response to the invitation request.
        """
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        request_body = {
            "email": email,
            "firstName": firstName,
            "lastName": lastName,
            "role": role,
            "external": external,
            "subject": subject,
            "message": message,
            "userTypeId": userTypeId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/invitations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_invitations_by_invitationid(
        self, invitationId, resend=None, role=None, external=None, userTypeId=None
    ) -> Any:
        """
        Updates an existing invitation by invitation ID with optional fields such as resend, role, external, and user type ID.

        Args:
            invitationId: The unique identifier of the invitation to update. Required.
            resend: Optional; whether to resend the invitation (boolean or compatible type).
            role: Optional; the role to assign with the invitation (string or compatible type).
            external: Optional; indicates if the invitation is for an external recipient (boolean or compatible type).
            userTypeId: Optional; the user type identifier to associate with the invitation (string, int, or compatible type).

        Returns:
            A dictionary representing the updated invitation resource as returned by the API.
        """
        if invitationId is None:
            raise ValueError("Missing required parameter 'invitationId'")
        request_body = {
            "resend": resend,
            "role": role,
            "external": external,
            "userTypeId": userTypeId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/invitations/{invitationId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_invitations_by_invitationid(self, invitationId) -> Any:
        """
        Deletes an invitation specified by its invitation ID.

        Args:
            invitationId: The unique identifier of the invitation to delete.

        Returns:
            A JSON-decoded response from the API after deleting the invitation.
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
        Retrieves account information from the API, optionally including only specified fields.

        Args:
            fields: Optional[str]. A comma-separated string of field names to include in the response. If None, all default fields are returned.

        Returns:
            Any. The JSON-decoded response from the API containing account details.
        """
        url = f"{self.base_url}/account"
        query_params = {k: v for k, v in [("fields", fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_a_ccount(self, metadata=None) -> Any:
        """
        Sends a PUT request to update or create an account with the provided metadata and returns the server response as a JSON object.

        Args:
            metadata: Optional metadata to associate with the account. If provided, this will be included in the request body. The format should match the server's expected schema. Defaults to None.

        Returns:
            A JSON-decoded Python object representing the response from the account API endpoint.
        """
        request_body = {
            "metadata": metadata,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/account"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_workflows(
        self,
    ) -> Any:
        """
        Retrieves all workflows from the server using a GET request.

        Args:
            None: This function takes no arguments

        Returns:
            The parsed JSON response containing the list of workflows.
        """
        url = f"{self.base_url}/workflows"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_workflows(self, name=None, request_body=None) -> Any:
        """
        Creates a new workflow by sending a POST request to the workflows endpoint.

        Args:
            name: Optional; the name of the workflow to create. Included as a query parameter if provided.
            request_body: Optional; the request body containing workflow details, provided as the data payload for the POST request.

        Returns:
            The JSON-decoded response from the server containing details of the created workflow.
        """
        url = f"{self.base_url}/workflows"
        query_params = {k: v for k, v in [("name", name)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_workflows_by_workflowid(
        self, workflowId, name=None, hidden=None, request_body=None
    ) -> Any:
        """
        Updates an existing workflow by workflow ID with optional name, hidden status, and request body data.

        Args:
            workflowId: The unique identifier of the workflow to update. Required.
            name: An optional new name for the workflow. If provided, updates the workflow's name.
            hidden: An optional boolean indicating whether the workflow should be hidden.
            request_body: Optional data to include in the request body when updating the workflow.

        Returns:
            The updated workflow as a JSON-decoded Python object.
        """
        if workflowId is None:
            raise ValueError("Missing required parameter 'workflowId'")
        url = f"{self.base_url}/workflows/{workflowId}"
        query_params = {
            k: v for k, v in [("name", name), ("hidden", hidden)] if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_customfields(
        self,
    ) -> Any:
        """
        Retrieves all custom fields from the API and returns them as a parsed JSON object.

        Args:
            None: This function takes no arguments

        Returns:
            The JSON-decoded response content containing the list of custom fields, typically as a Python dict or list, depending on the API response structure.
        """
        url = f"{self.base_url}/customfields"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_customfields(
        self,
        title,
        type,
        spaceId=None,
        sharing=None,
        shareds=None,
        settings=None,
        request_body=None,
    ) -> Any:
        """
        Creates a custom field by sending a POST request with the specified parameters to the customfields endpoint and returns the created field's data.

        Args:
            title: str. The name of the custom field to be created. Required.
            type: str. The type of the custom field to be created. Required.
            spaceId: Optional[str]. Identifier of the space to associate with the custom field.
            sharing: Optional[str]. Determines the sharing settings for the custom field.
            shareds: Optional[str]. Specifies users or groups the custom field is shared with.
            settings: Optional[str]. Additional settings for the custom field in string or JSON format.
            request_body: Optional[Any]. The request body payload to include in the POST request.

        Returns:
            Any. The JSON response data representing the created custom field.
        """
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        url = f"{self.base_url}/customfields"
        query_params = {
            k: v
            for k, v in [
                ("title", title),
                ("type", type),
                ("spaceId", spaceId),
                ("sharing", sharing),
                ("shareds", shareds),
                ("settings", settings),
            ]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_customfields_by_customfieldid(self, customFieldId) -> Any:
        """
        Retrieves details for a custom field by its unique identifier from the API.

        Args:
            customFieldId: The unique identifier of the custom field to retrieve.

        Returns:
            A JSON-decoded response containing the custom field details.
        """
        if customFieldId is None:
            raise ValueError("Missing required parameter 'customFieldId'")
        url = f"{self.base_url}/customfields/{customFieldId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_customfields_by_customfieldid(
        self,
        customFieldId,
        title=None,
        type=None,
        changeScope=None,
        spaceId=None,
        sharing=None,
        addShareds=None,
        removeShareds=None,
        settings=None,
        addMirrors=None,
        removeMirrors=None,
    ) -> Any:
        """
        Updates a custom field specified by its ID with the provided parameters using an HTTP PUT request.

        Args:
            customFieldId: The unique identifier of the custom field to update.
            title: Optional new title for the custom field (default is None).
            type: Optional new field type (default is None).
            changeScope: Optional scope for tracking or permission changes (default is None).
            spaceId: Optional identifier of the space associated with the custom field (default is None).
            sharing: Optional sharing configuration or permissions (default is None).
            addShareds: Optional list of users or entities to add to the shared list (default is None).
            removeShareds: Optional list of users or entities to remove from the shared list (default is None).
            settings: Optional dictionary with additional settings for the custom field (default is None).
            addMirrors: Optional list of entities to add as mirrors (default is None).
            removeMirrors: Optional list of entities to remove as mirrors (default is None).

        Returns:
            The server response as a JSON-decoded object containing the updated custom field data.
        """
        if customFieldId is None:
            raise ValueError("Missing required parameter 'customFieldId'")
        url = f"{self.base_url}/customfields/{customFieldId}"
        query_params = {
            k: v
            for k, v in [
                ("title", title),
                ("type", type),
                ("changeScope", changeScope),
                ("spaceId", spaceId),
                ("sharing", sharing),
                ("addShareds", addShareds),
                ("removeShareds", removeShareds),
                ("settings", settings),
                ("addMirrors", addMirrors),
                ("removeMirrors", removeMirrors),
            ]
            if v is not None
        }
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_customfields_by_customfieldid(self, customFieldId) -> Any:
        """
        Deletes a custom field resource identified by its custom field ID.

        Args:
            customFieldId: The unique identifier of the custom field to delete.

        Returns:
            The server response as a deserialized JSON object, typically containing the result of the delete operation.
        """
        if customFieldId is None:
            raise ValueError("Missing required parameter 'customFieldId'")
        url = f"{self.base_url}/customfields/{customFieldId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders(
        self,
        permalink=None,
        descendants=None,
        metadata=None,
        customFields=None,
        updatedDate=None,
        withInvitations=None,
        project=None,
        deleted=None,
        contractTypes=None,
        plainTextCustomFields=None,
        customItemTypes=None,
        pageSize=None,
        nextPageToken=None,
        fields=None,
    ) -> Any:
        """
        Retrieves a list of folders from the API, supporting extensive filtering, pagination, and field selection.

        Args:
            permalink: str or None. Filter results by folder permalink.
            descendants: bool or None. If True, include descendant folders in the results.
            metadata: dict or None. Filter folders by matching metadata fields.
            customFields: dict or None. Filter results by custom field values.
            updatedDate: str or None. Only return folders updated on or after this date (ISO 8601 format).
            withInvitations: bool or None. If True, include folders with active invitations.
            project: str or None. Filter folders by associated project identifier.
            deleted: bool or None. If True, include deleted folders in the response.
            contractTypes: list or None. Filter folders by contract types.
            plainTextCustomFields: dict or None. Filter by plain text custom fields.
            customItemTypes: list or None. Filter folders by custom item types.
            pageSize: int or None. Maximum number of results to return per page.
            nextPageToken: str or None. Token to retrieve the next page of results.
            fields: list or None. Specify which fields to include in the response.

        Returns:
            dict. The JSON-decoded response from the API containing folder data and related metadata.
        """
        url = f"{self.base_url}/folders"
        query_params = {
            k: v
            for k, v in [
                ("permalink", permalink),
                ("descendants", descendants),
                ("metadata", metadata),
                ("customFields", customFields),
                ("updatedDate", updatedDate),
                ("withInvitations", withInvitations),
                ("project", project),
                ("deleted", deleted),
                ("contractTypes", contractTypes),
                ("plainTextCustomFields", plainTextCustomFields),
                ("customItemTypes", customItemTypes),
                ("pageSize", pageSize),
                ("nextPageToken", nextPageToken),
                ("fields", fields),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_folders_by_folderid_folders(
        self,
        folderId,
        permalink=None,
        descendants=None,
        metadata=None,
        customFields=None,
        updatedDate=None,
        withInvitations=None,
        project=None,
        contractTypes=None,
        plainTextCustomFields=None,
        customItemTypes=None,
        pageSize=None,
        nextPageToken=None,
        fields=None,
    ) -> Any:
        """
        Retrieves subfolders of a specified folder, applying optional filters and pagination parameters.

        Args:
            folderId: str. The unique identifier of the parent folder whose subfolders are to be retrieved. Required.
            permalink: str, optional. Filter results to subfolders with the specified permalink.
            descendants: bool, optional. If True, include descendant folders recursively in the results.
            metadata: str or dict, optional. Filter subfolders by associated metadata.
            customFields: str, list, or dict, optional. Filter subfolders by custom field values.
            updatedDate: str or datetime, optional. Filter subfolders updated on or after the specified date.
            withInvitations: bool, optional. If True, include invitation information with subfolders.
            project: str or int, optional. Filter subfolders belonging to a specific project.
            contractTypes: str, list, or dict, optional. Filter subfolders by contract types.
            plainTextCustomFields: str, list, or dict, optional. Filter subfolders by plain text custom fields.
            customItemTypes: str, list, or dict, optional. Filter subfolders by custom item types.
            pageSize: int, optional. Maximum number of subfolders to return per request, for pagination.
            nextPageToken: str, optional. Token for retrieving the next page of results.
            fields: str or list, optional. Specify fields to include in the response for each folder.

        Returns:
            dict. A JSON object containing the list of subfolders matching the criteria, along with pagination tokens and any requested metadata.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        url = f"{self.base_url}/folders/{folderId}/folders"
        query_params = {
            k: v
            for k, v in [
                ("permalink", permalink),
                ("descendants", descendants),
                ("metadata", metadata),
                ("customFields", customFields),
                ("updatedDate", updatedDate),
                ("withInvitations", withInvitations),
                ("project", project),
                ("contractTypes", contractTypes),
                ("plainTextCustomFields", plainTextCustomFields),
                ("customItemTypes", customItemTypes),
                ("pageSize", pageSize),
                ("nextPageToken", nextPageToken),
                ("fields", fields),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_by_folderid_folders(
        self,
        folderId,
        title,
        description=None,
        shareds=None,
        metadata=None,
        customFields=None,
        customColumns=None,
        project=None,
        userAccessRoles=None,
        withInvitations=None,
        customItemTypeId=None,
        plainTextCustomFields=None,
        fields=None,
    ) -> Any:
        """
        Creates a new subfolder within a specified folder by folder ID, with configurable attributes such as title, description, sharing, metadata, and permissions.

        Args:
            folderId: str. The ID of the parent folder in which to create the new subfolder. Required.
            title: str. The title of the new subfolder. Required.
            description: str, optional. An optional description for the subfolder.
            shareds: list or None. Optional list of user or group IDs to share the subfolder with.
            metadata: dict or None. Optional metadata to associate with the subfolder.
            customFields: dict or None. Optional custom fields to set for the subfolder.
            customColumns: dict or None. Optional custom columns configuration.
            project: str or None. Optional project identifier to associate with the subfolder.
            userAccessRoles: list or None. Optional list of user access roles to assign to the subfolder.
            withInvitations: bool or None. If True, send invitations to shared users or groups. Optional.
            customItemTypeId: str or None. Optional custom item type identifier for the subfolder.
            plainTextCustomFields: dict or None. Optional plain text custom fields to set for the subfolder.
            fields: list or None. Optional list of specific fields to include in the response.

        Returns:
            dict. The newly created subfolder object as returned by the API.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        request_body = {
            "title": title,
            "description": description,
            "shareds": shareds,
            "metadata": metadata,
            "customFields": customFields,
            "customColumns": customColumns,
            "project": project,
            "userAccessRoles": userAccessRoles,
            "withInvitations": withInvitations,
            "customItemTypeId": customItemTypeId,
            "plainTextCustomFields": plainTextCustomFields,
            "fields": fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folderId}/folders"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_folders_by_folderid(self, folderId) -> Any:
        """
        Deletes a folder resource identified by its folder ID via an HTTP DELETE request.

        Args:
            folderId: The unique identifier of the folder to delete. Must not be None.

        Returns:
            The parsed JSON response from the server if the deletion is successful.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        url = f"{self.base_url}/folders/{folderId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_folders_by_folderid(
        self,
        folderId,
        title=None,
        description=None,
        addParents=None,
        removeParents=None,
        addShareds=None,
        removeShareds=None,
        metadata=None,
        restore=None,
        customFields=None,
        customColumns=None,
        clearCustomColumns=None,
        project=None,
        addAccessRoles=None,
        removeAccessRoles=None,
        withInvitations=None,
        convertToCustomItemType=None,
        plainTextCustomFields=None,
        fields=None,
    ) -> Any:
        """
        Updates a folder's properties and relationships by folder ID using a PUT request.

        Args:
            folderId: str. The unique identifier of the folder to update. Required.
            title: str, optional. The new title for the folder.
            description: str, optional. The updated description of the folder.
            addParents: list or str, optional. Parent folder IDs to add as parents to this folder.
            removeParents: list or str, optional. Parent folder IDs to remove from this folder.
            addShareds: list or str, optional. Accounts to share this folder with.
            removeShareds: list or str, optional. Shared accounts to remove from this folder.
            metadata: dict, optional. Additional metadata to update for the folder.
            restore: bool, optional. Whether to restore the folder if it was deleted.
            customFields: dict, optional. Custom fields and their values to set or update.
            customColumns: dict, optional. Custom columns and their values to set or update.
            clearCustomColumns: list or str, optional. Custom column fields to clear.
            project: str, optional. Associated project identifier for the folder.
            addAccessRoles: list or str, optional. Access role IDs to add to the folder.
            removeAccessRoles: list or str, optional. Access role IDs to remove from the folder.
            withInvitations: bool, optional. Whether to send invitations on access role changes.
            convertToCustomItemType: str, optional. Converts the folder to a specific custom item type.
            plainTextCustomFields: dict, optional. Plain text fields to update.
            fields: str or list, optional. Specific fields to include in the response.

        Returns:
            dict. The JSON response containing updated folder information from the API.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        request_body = {
            "title": title,
            "description": description,
            "addParents": addParents,
            "removeParents": removeParents,
            "addShareds": addShareds,
            "removeShareds": removeShareds,
            "metadata": metadata,
            "restore": restore,
            "customFields": customFields,
            "customColumns": customColumns,
            "clearCustomColumns": clearCustomColumns,
            "project": project,
            "addAccessRoles": addAccessRoles,
            "removeAccessRoles": removeAccessRoles,
            "withInvitations": withInvitations,
            "convertToCustomItemType": convertToCustomItemType,
            "plainTextCustomFields": plainTextCustomFields,
            "fields": fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folderId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tasks(
        self,
        descendants=None,
        title=None,
        status=None,
        importance=None,
        startDate=None,
        dueDate=None,
        scheduledDate=None,
        createdDate=None,
        updatedDate=None,
        completedDate=None,
        authors=None,
        responsibles=None,
        responsiblePlaceholders=None,
        permalink=None,
        type=None,
        limit=None,
        sortField=None,
        sortOrder=None,
        subTasks=None,
        pageSize=None,
        nextPageToken=None,
        metadata=None,
        customField=None,
        customFields=None,
        customStatuses=None,
        withInvitations=None,
        billingTypes=None,
        plainTextCustomFields=None,
        customItemTypes=None,
        fields=None,
    ) -> Any:
        """
        Retrieves tasks from the API with optional filtering, sorting, pagination, and field selection parameters.

        Args:
            descendants: Optional; filter tasks by descendant items or folders.
            title: Optional; filter tasks by title.
            status: Optional; filter tasks by their status (e.g., active, completed).
            importance: Optional; filter tasks by importance level.
            startDate: Optional; filter tasks by their start date.
            dueDate: Optional; filter tasks by due date.
            scheduledDate: Optional; filter tasks by scheduled date.
            createdDate: Optional; filter tasks by creation date.
            updatedDate: Optional; filter tasks by last updated date.
            completedDate: Optional; filter tasks by completion date.
            authors: Optional; filter tasks by author(s).
            responsibles: Optional; filter tasks by responsible user(s).
            responsiblePlaceholders: Optional; filter by responsible placeholders.
            permalink: Optional; filter tasks by their permalink.
            type: Optional; filter tasks by type.
            limit: Optional; limit the number of returned tasks.
            sortField: Optional; field to sort the tasks by.
            sortOrder: Optional; sort order ('asc' or 'desc').
            subTasks: Optional; filter tasks by whether they are sub-tasks.
            pageSize: Optional; number of tasks per page.
            nextPageToken: Optional; token for retrieving the next page of results.
            metadata: Optional; include or filter by metadata.
            customField: Optional; filter by a specific custom field.
            customFields: Optional; filter tasks by custom fields.
            customStatuses: Optional; filter tasks by custom workflow statuses.
            withInvitations: Optional; include tasks with invitations.
            billingTypes: Optional; filter tasks by billing types.
            plainTextCustomFields: Optional; specify if custom fields should be plain text.
            customItemTypes: Optional; filter by custom item types.
            fields: Optional; select specific fields to include in the result.

        Returns:
            The JSON-decoded API response containing a list of tasks and related metadata.
        """
        url = f"{self.base_url}/tasks"
        query_params = {
            k: v
            for k, v in [
                ("descendants", descendants),
                ("title", title),
                ("status", status),
                ("importance", importance),
                ("startDate", startDate),
                ("dueDate", dueDate),
                ("scheduledDate", scheduledDate),
                ("createdDate", createdDate),
                ("updatedDate", updatedDate),
                ("completedDate", completedDate),
                ("authors", authors),
                ("responsibles", responsibles),
                ("responsiblePlaceholders", responsiblePlaceholders),
                ("permalink", permalink),
                ("type", type),
                ("limit", limit),
                ("sortField", sortField),
                ("sortOrder", sortOrder),
                ("subTasks", subTasks),
                ("pageSize", pageSize),
                ("nextPageToken", nextPageToken),
                ("metadata", metadata),
                ("customField", customField),
                ("customFields", customFields),
                ("customStatuses", customStatuses),
                ("withInvitations", withInvitations),
                ("billingTypes", billingTypes),
                ("plainTextCustomFields", plainTextCustomFields),
                ("customItemTypes", customItemTypes),
                ("fields", fields),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_tasks_by_taskid(self, taskId, fields=None) -> Any:
        """
        Retrieves a task by its ID from the remote service, optionally returning only specified fields.

        Args:
            taskId: The unique identifier of the task to retrieve.
            fields: Optional. A comma-separated string specifying which fields to include in the response. If None, all available fields are returned.

        Returns:
            The JSON-decoded response data containing task details, as returned by the remote API.
        """
        if taskId is None:
            raise ValueError("Missing required parameter 'taskId'")
        url = f"{self.base_url}/tasks/{taskId}"
        query_params = {k: v for k, v in [("fields", fields)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def put_tasks_by_taskid(
        self,
        taskId,
        title=None,
        description=None,
        status=None,
        importance=None,
        dates=None,
        addParents=None,
        removeParents=None,
        addShareds=None,
        removeShareds=None,
        addResponsibles=None,
        removeResponsibles=None,
        addResponsiblePlaceholders=None,
        removeResponsiblePlaceholders=None,
        addFollowers=None,
        follow=None,
        priorityBefore=None,
        priorityAfter=None,
        addSuperTasks=None,
        removeSuperTasks=None,
        metadata=None,
        customFields=None,
        customStatus=None,
        restore=None,
        effortAllocation=None,
        billingType=None,
        withInvitations=None,
        convertToCustomItemType=None,
        plainTextCustomFields=None,
        fields=None,
    ) -> Any:
        """
        Updates the properties and relationships of a task specified by its ID, applying the given changes and returning the updated task data as a JSON object.

        Args:
            taskId: str. The unique identifier of the task to update. Must not be None.
            title: Optional[str]. The new title for the task.
            description: Optional[str]. The new description for the task.
            status: Optional[str]. The new status for the task.
            importance: Optional[str]. The importance level to assign to the task.
            dates: Optional[dict]. Task dates to update (e.g., due date, start date).
            addParents: Optional[list]. List of parent task IDs to add as parents to this task.
            removeParents: Optional[list]. List of parent task IDs to remove from this task.
            addShareds: Optional[list]. List of user IDs to add as shared users for this task.
            removeShareds: Optional[list]. List of user IDs to remove from shared users.
            addResponsibles: Optional[list]. List of user IDs to add as responsible for this task.
            removeResponsibles: Optional[list]. List of user IDs to remove from responsibles.
            addResponsiblePlaceholders: Optional[list]. Placeholder IDs to add to the responsible list.
            removeResponsiblePlaceholders: Optional[list]. Placeholder IDs to remove from responsibles.
            addFollowers: Optional[list]. User IDs to add as followers of this task.
            follow: Optional[bool]. If set, follows or unfollows the task.
            priorityBefore: Optional[str]. Task ID before which this task should be prioritized.
            priorityAfter: Optional[str]. Task ID after which this task should be prioritized.
            addSuperTasks: Optional[list]. Task IDs to add as super tasks.
            removeSuperTasks: Optional[list]. Task IDs to remove from super tasks.
            metadata: Optional[dict]. Arbitrary metadata to associate with the task.
            customFields: Optional[list]. List of custom field updates for the task.
            customStatus: Optional[str]. Custom status identifier to apply.
            restore: Optional[bool]. If True, restores a deleted task.
            effortAllocation: Optional[list]. List of effort allocation data objects.
            billingType: Optional[str]. Billing type identifier to set for the task.
            withInvitations: Optional[bool]. If True, send invitations to new shared/responsible users.
            convertToCustomItemType: Optional[str]. Identifier to convert the task to a custom item type.
            plainTextCustomFields: Optional[dict]. Plain text values for custom fields.
            fields: Optional[list]. List of fields to include in the response.

        Returns:
            dict. The JSON response containing updated task details as returned by the server.
        """
        if taskId is None:
            raise ValueError("Missing required parameter 'taskId'")
        request_body = {
            "title": title,
            "description": description,
            "status": status,
            "importance": importance,
            "dates": dates,
            "addParents": addParents,
            "removeParents": removeParents,
            "addShareds": addShareds,
            "removeShareds": removeShareds,
            "addResponsibles": addResponsibles,
            "removeResponsibles": removeResponsibles,
            "addResponsiblePlaceholders": addResponsiblePlaceholders,
            "removeResponsiblePlaceholders": removeResponsiblePlaceholders,
            "addFollowers": addFollowers,
            "follow": follow,
            "priorityBefore": priorityBefore,
            "priorityAfter": priorityAfter,
            "addSuperTasks": addSuperTasks,
            "removeSuperTasks": removeSuperTasks,
            "metadata": metadata,
            "customFields": customFields,
            "customStatus": customStatus,
            "restore": restore,
            "effortAllocation": effortAllocation,
            "billingType": billingType,
            "withInvitations": withInvitations,
            "convertToCustomItemType": convertToCustomItemType,
            "plainTextCustomFields": plainTextCustomFields,
            "fields": fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/tasks/{taskId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_tasks_by_taskid(self, taskId) -> Any:
        """
        Deletes a task identified by the given task ID via an HTTP DELETE request and returns the response as a JSON object.

        Args:
            taskId: The unique identifier of the task to be deleted. Must not be None.

        Returns:
            A JSON object containing the API response to the delete operation.
        """
        if taskId is None:
            raise ValueError("Missing required parameter 'taskId'")
        url = f"{self.base_url}/tasks/{taskId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_folders_by_folderid_tasks(
        self,
        folderId,
        title,
        description=None,
        status=None,
        importance=None,
        dates=None,
        shareds=None,
        parents=None,
        responsibles=None,
        responsiblePlaceholders=None,
        followers=None,
        follow=None,
        priorityBefore=None,
        priorityAfter=None,
        superTasks=None,
        metadata=None,
        customFields=None,
        customStatus=None,
        effortAllocation=None,
        billingType=None,
        withInvitations=None,
        customItemTypeId=None,
        plainTextCustomFields=None,
        fields=None,
    ) -> Any:
        """
        Creates a new task within a specified folder by folder ID, with configurable attributes such as title, description, status, importance, dates, assigned users, metadata, custom fields, and other options.

        Args:
            folderId: str or int. The unique identifier of the folder in which to create the new task. Required.
            title: str. The title of the task to be created. Required.
            description: str, optional. A detailed description of the task.
            status: str, optional. The status of the task (e.g., active, completed).
            importance: str or int, optional. The importance level of the task.
            dates: dict or list, optional. Date-related information for the task, such as start and due dates.
            shareds: list, optional. Users or user IDs to share the task with.
            parents: list, optional. Parent task IDs or references, if this task is a subtask.
            responsibles: list, optional. Users or user IDs responsible for this task.
            responsiblePlaceholders: list, optional. Placeholder users assigned as responsible.
            followers: list, optional. Users or user IDs who will follow task updates.
            follow: bool, optional. Whether the current user should follow the task.
            priorityBefore: str or int, optional. Task ID before which this task should be prioritized.
            priorityAfter: str or int, optional. Task ID after which this task should be prioritized.
            superTasks: list, optional. IDs of super tasks this task belongs to.
            metadata: dict, optional. Arbitrary metadata to attach to the task.
            customFields: dict or list, optional. Custom field values for the task.
            customStatus: str, optional. Custom status value for the task.
            effortAllocation: dict or list, optional. Effort allocation details (e.g., estimated time, allocation per responsible).
            billingType: str, optional. Billing details or billing type for the task.
            withInvitations: bool, optional. Whether to send invitations to newly added users.
            customItemTypeId: str or int, optional. Custom item type identifier.
            plainTextCustomFields: dict or list, optional. Custom fields in plain text format.
            fields: list or str, optional. Specifies which fields should be included in the API response.

        Returns:
            dict. The JSON response from the server containing details of the newly created task.
        """
        if folderId is None:
            raise ValueError("Missing required parameter 'folderId'")
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        request_body = {
            "title": title,
            "description": description,
            "status": status,
            "importance": importance,
            "dates": dates,
            "shareds": shareds,
            "parents": parents,
            "responsibles": responsibles,
            "responsiblePlaceholders": responsiblePlaceholders,
            "followers": followers,
            "follow": follow,
            "priorityBefore": priorityBefore,
            "priorityAfter": priorityAfter,
            "superTasks": superTasks,
            "metadata": metadata,
            "customFields": customFields,
            "customStatus": customStatus,
            "effortAllocation": effortAllocation,
            "billingType": billingType,
            "withInvitations": withInvitations,
            "customItemTypeId": customItemTypeId,
            "plainTextCustomFields": plainTextCustomFields,
            "fields": fields,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folders/{folderId}/tasks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of references to tool-related instance methods for managing contacts, users, groups, invitations, accounts, workflows, custom fields, folders, and tasks.

        Args:
            None: This method does not take any arguments.

        Returns:
            list: A list of method references corresponding to various instance-level API operations for managing organizational entities such as contacts, users, groups, invitations, accounts, workflows, custom fields, folders, and tasks.
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
            self.post_folders_by_folderid_tasks,
        ]
