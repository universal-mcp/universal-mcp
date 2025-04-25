from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class ClickupApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="clickup", integration=integration, **kwargs)
        self.base_url = "https://api.clickup.com/api/v2"

    def authorization_get_access_token(
        self, client_id, client_secret, code
    ) -> dict[str, Any]:
        """
        Exchanges an authorization code for an access token using OAuth2 credentials.

        Args:
            client_id: The client identifier string obtained from the OAuth provider.
            client_secret: The client secret string associated with the client_id.
            code: The authorization code received after user consent.

        Returns:
            A dictionary containing the access token and related response data from the OAuth provider.

        Raises:
            ValueError: If 'client_id', 'client_secret', or 'code' is missing or None.
            HTTPError: If the HTTP request to the OAuth token endpoint fails with a non-success status code.

        Tags:
            authorization, oauth2, get, access-token
        """
        if client_id is None:
            raise ValueError("Missing required parameter 'client_id'")
        if client_secret is None:
            raise ValueError("Missing required parameter 'client_secret'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        url = f"{self.base_url}/oauth/token"
        query_params = {
            k: v
            for k, v in [
                ("client_id", client_id),
                ("client_secret", client_secret),
                ("code", code),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def authorization_view_account_details(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the current authenticated user's account details from the authorization service.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing the authenticated user's account information as returned by the authorization service.

        Raises:
            requests.HTTPError: If the GET request to fetch user details returns an unsuccessful HTTP status code.

        Tags:
            authorization, view, account, details, api
        """
        url = f"{self.base_url}/user"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def authorization_get_workspace_list(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of workspaces accessible to the authorized user from the authorization service.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing workspace information for the user, as returned by the authorization service.

        Raises:
            requests.HTTPError: If the HTTP request to the authorization service fails or returns a non-success status code.

        Tags:
            get, list, workspaces, authorization
        """
        url = f"{self.base_url}/team"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_checklists_create_new_checklist(
        self, task_id, name, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Creates a new checklist for a given task and returns the created checklist details as a dictionary.

        Args:
            task_id: str. The unique identifier of the task for which the checklist will be created.
            name: str. The name of the new checklist.
            custom_task_ids: Optional[list[str]]. A list of custom task IDs to associate with the checklist. Defaults to None.
            team_id: Optional[str]. The ID of the team to associate with the checklist. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created checklist from the API response.

        Raises:
            ValueError: If 'task_id' or 'name' is not provided.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            create, checklist, task-management, api
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}/checklist"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_checklists_update_checklist(
        self, checklist_id, name=None, position=None
    ) -> dict[str, Any]:
        """
        Updates a checklist's name and/or position by sending a PUT request to the checklist API endpoint.

        Args:
            checklist_id: str. The unique identifier of the checklist to update. Required.
            name: str or None. The new name for the checklist. Optional.
            position: int or None. The new position of the checklist. Optional.

        Returns:
            dict[str, Any]: A dictionary containing the updated checklist data returned by the API.

        Raises:
            ValueError: Raised if the required parameter 'checklist_id' is None.
            HTTPError: Raised if the HTTP response contains an unsuccessful status code.

        Tags:
            update, checklist, management, api
        """
        if checklist_id is None:
            raise ValueError("Missing required parameter 'checklist_id'")
        request_body = {
            "name": name,
            "position": position,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/checklist/{checklist_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_checklists_remove_checklist(self, checklist_id) -> dict[str, Any]:
        """
        Removes a checklist by its ID using a DELETE request to the API.

        Args:
            checklist_id: The unique identifier of the checklist to be removed. Must not be None.

        Returns:
            A dictionary containing the JSON response from the API after the checklist has been removed.

        Raises:
            ValueError: If 'checklist_id' is None.
            HTTPError: If the HTTP request to delete the checklist fails (non-2xx status code).

        Tags:
            remove, checklist, delete, management
        """
        if checklist_id is None:
            raise ValueError("Missing required parameter 'checklist_id'")
        url = f"{self.base_url}/checklist/{checklist_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_checklists_add_line_item(
        self, checklist_id, name=None, assignee=None
    ) -> dict[str, Any]:
        """
        Adds a new line item to a specified task checklist.

        Args:
            checklist_id: str. Unique identifier of the checklist to which the line item will be added.
            name: Optional[str]. Name of the checklist line item to be added.
            assignee: Optional[str]. Identifier of the user to assign the line item to.

        Returns:
            dict[str, Any]: Dictionary containing the details of the newly created checklist line item as returned by the API.

        Raises:
            ValueError: Raised if the required parameter 'checklist_id' is not provided.
            requests.HTTPError: Raised if the HTTP request to add the checklist item fails.

        Tags:
            add, checklist, line-item, management
        """
        if checklist_id is None:
            raise ValueError("Missing required parameter 'checklist_id'")
        request_body = {
            "name": name,
            "assignee": assignee,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/checklist/{checklist_id}/checklist_item"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_checklists_update_checklist_item(
        self,
        checklist_id,
        checklist_item_id,
        name=None,
        assignee=None,
        resolved=None,
        parent=None,
    ) -> dict[str, Any]:
        """
        Updates a checklist item with new details such as name, assignee, resolution status, or parent within a specified checklist.

        Args:
            checklist_id: str. Unique identifier for the checklist containing the item to update.
            checklist_item_id: str. Unique identifier for the checklist item to be updated.
            name: str, optional. New name for the checklist item. If None, the name remains unchanged.
            assignee: str, optional. Identifier of the user assigned to this checklist item. If None, the assignee remains unchanged.
            resolved: bool, optional. Resolution status to set for the checklist item. If None, the resolved status remains unchanged.
            parent: str, optional. Identifier of the parent checklist item, if setting or updating a parent-child relationship. If None, the parent remains unchanged.

        Returns:
            dict[str, Any]: The updated checklist item as a dictionary parsed from the server response.

        Raises:
            ValueError: Raised if either 'checklist_id' or 'checklist_item_id' is None.
            requests.HTTPError: Raised if the API request fails or the server returns an unsuccessful status code.

        Tags:
            update, checklist, management, item
        """
        if checklist_id is None:
            raise ValueError("Missing required parameter 'checklist_id'")
        if checklist_item_id is None:
            raise ValueError("Missing required parameter 'checklist_item_id'")
        request_body = {
            "name": name,
            "assignee": assignee,
            "resolved": resolved,
            "parent": parent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/checklist/{checklist_id}/checklist_item/{checklist_item_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_checklists_remove_checklist_item(
        self, checklist_id, checklist_item_id
    ) -> dict[str, Any]:
        """
        Removes a specific checklist item from a checklist by issuing a DELETE request to the appropriate API endpoint.

        Args:
            checklist_id: The unique identifier of the checklist containing the item to remove.
            checklist_item_id: The unique identifier of the checklist item to be removed.

        Returns:
            A dictionary containing the API response data after attempting to remove the checklist item.

        Raises:
            ValueError: Raised if either 'checklist_id' or 'checklist_item_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the checklist item fails (e.g., due to network issues, authorization problems, or the item not existing).

        Tags:
            remove, checklist, delete, management
        """
        if checklist_id is None:
            raise ValueError("Missing required parameter 'checklist_id'")
        if checklist_item_id is None:
            raise ValueError("Missing required parameter 'checklist_item_id'")
        url = f"{self.base_url}/checklist/{checklist_id}/checklist_item/{checklist_item_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_get_task_comments(
        self, task_id, custom_task_ids=None, team_id=None, start=None, start_id=None
    ) -> dict[str, Any]:
        """
        Retrieve all comments associated with a specific task.

        Args:
            task_id: str. The unique identifier for the task whose comments are to be retrieved. Required.
            custom_task_ids: Optional[str]. An alternative unique identifier for the task, useful when using custom task ID schemes. Defaults to None.
            team_id: Optional[str]. The identifier of the team associated with the task. Used to limit the search to a specific team. Defaults to None.
            start: Optional[int]. The position offset for pagination, specifying where to start retrieving comments. Defaults to None.
            start_id: Optional[str]. The ID of the first comment from which to start retrieving (for pagination). Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the list of comments and associated metadata for the specified task.

        Raises:
            ValueError: If 'task_id' is not provided.
            requests.HTTPError: If the HTTP request to retrieve comments fails (e.g., due to network errors or server-side issues).

        Tags:
            list, comments, task, search, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/task/{task_id}/comment"
        query_params = {
            k: v
            for k, v in [
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
                ("start", start),
                ("start_id", start_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_create_new_task_comment(
        self,
        task_id,
        comment_text,
        assignee,
        notify_all,
        custom_task_ids=None,
        team_id=None,
    ) -> dict[str, Any]:
        """
        Creates a new comment on the specified task, assigning it to a user and controlling notification behavior.

        Args:
            task_id: str. Unique identifier of the task to comment on.
            comment_text: str. The text content of the comment to be added.
            assignee: str. Identifier of the user to assign the comment or task.
            notify_all: bool. Determines whether all users associated with the task should be notified.
            custom_task_ids: Optional[str]. Custom identifier for the task, if applicable.
            team_id: Optional[str]. Identifier of the team to which the task belongs, if applicable.

        Returns:
            dict[str, Any]: A dictionary containing the created comment data as returned by the API.

        Raises:
            ValueError: Raised if any of the required parameters ('task_id', 'comment_text', 'assignee', or 'notify_all') are missing.
            requests.HTTPError: Raised if the HTTP request to create the comment fails or the response status indicates an error.

        Tags:
            create, comment, task, api, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if comment_text is None:
            raise ValueError("Missing required parameter 'comment_text'")
        if assignee is None:
            raise ValueError("Missing required parameter 'assignee'")
        if notify_all is None:
            raise ValueError("Missing required parameter 'notify_all'")
        request_body = {
            "comment_text": comment_text,
            "assignee": assignee,
            "notify_all": notify_all,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}/comment"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_get_view_comments(
        self, view_id, start=None, start_id=None
    ) -> dict[str, Any]:
        """
        Retrieve comments for a specific view, supporting optional pagination parameters.

        Args:
            view_id: The unique identifier of the view to retrieve comments for.
            start: Optional; the zero-based index or offset for pagination (default is None).
            start_id: Optional; the comment ID to start pagination from (default is None).

        Returns:
            A dictionary containing the list of comments and associated metadata for the specified view.

        Raises:
            ValueError: Raised if 'view_id' is None.
            requests.HTTPError: Raised if the HTTP request for comments fails (e.g., connection errors, non-2xx response).

        Tags:
            get, comments, view, api, pagination
        """
        if view_id is None:
            raise ValueError("Missing required parameter 'view_id'")
        url = f"{self.base_url}/view/{view_id}/comment"
        query_params = {
            k: v for k, v in [("start", start), ("start_id", start_id)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_create_chat_view_comment(
        self, view_id, comment_text, notify_all
    ) -> dict[str, Any]:
        """
        Creates a new comment on a chat view and optionally notifies all participants.

        Args:
            view_id: str. The unique identifier of the chat view to which the comment will be added.
            comment_text: str. The text content of the comment to post.
            notify_all: bool. Whether to notify all participants in the chat about the new comment.

        Returns:
            dict. The response from the API containing details about the created comment.

        Raises:
            ValueError: If any of 'view_id', 'comment_text', or 'notify_all' is None.
            requests.HTTPError: If the HTTP request to create the comment fails.

        Tags:
            comments, create, chat, api
        """
        if view_id is None:
            raise ValueError("Missing required parameter 'view_id'")
        if comment_text is None:
            raise ValueError("Missing required parameter 'comment_text'")
        if notify_all is None:
            raise ValueError("Missing required parameter 'notify_all'")
        request_body = {
            "comment_text": comment_text,
            "notify_all": notify_all,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/view/{view_id}/comment"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_get_list_comments(
        self, list_id, start=None, start_id=None
    ) -> dict[str, Any]:
        """
        Retrieve a list of comments associated with a specific list, supporting optional pagination.

        Args:
            list_id: The unique identifier of the list for which comments are to be retrieved.
            start: Optional; An integer specifying the offset from which to start returning comments.
            start_id: Optional; An identifier to continue retrieving comments from a specific comment onward.

        Returns:
            A dictionary containing the list of comments and associated metadata as returned by the API.

        Raises:
            ValueError: If 'list_id' is not provided.
            requests.HTTPError: If the HTTP request to the API fails with an error status code.

        Tags:
            comments, list, retrieve, api, batch
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}/comment"
        query_params = {
            k: v for k, v in [("start", start), ("start_id", start_id)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_add_to_list_comment(
        self, list_id, comment_text, assignee, notify_all
    ) -> dict[str, Any]:
        """
        Adds a comment to a specified list, assigns it to a given user, and optionally notifies all stakeholders.

        Args:
            list_id: The unique identifier of the list to which the comment will be added.
            comment_text: The text of the comment to be posted.
            assignee: The user assigned to the comment.
            notify_all: Boolean indicating whether all stakeholders should be notified of the new comment.

        Returns:
            A dictionary containing the response data from the API after adding the comment.

        Raises:
            ValueError: If any of the required parameters ('list_id', 'comment_text', 'assignee', or 'notify_all') are None.
            requests.HTTPError: If the HTTP request to the API fails or an unsuccessful status code is returned.

        Tags:
            add, comment, list, assignment, notify, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if comment_text is None:
            raise ValueError("Missing required parameter 'comment_text'")
        if assignee is None:
            raise ValueError("Missing required parameter 'assignee'")
        if notify_all is None:
            raise ValueError("Missing required parameter 'notify_all'")
        request_body = {
            "comment_text": comment_text,
            "assignee": assignee,
            "notify_all": notify_all,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/list/{list_id}/comment"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_update_task_comment(
        self, comment_id, comment_text, assignee, resolved
    ) -> dict[str, Any]:
        """
        Updates an existing task comment with new text, assignee, and resolution status.

        Args:
            comment_id: str. The unique identifier of the comment to update.
            comment_text: str. The new text content for the comment.
            assignee: str. The user assigned to the comment.
            resolved: bool. Indicates whether the comment has been marked as resolved.

        Returns:
            dict[str, Any]: The updated comment details as returned by the server.

        Raises:
            ValueError: Raised if any of the required parameters ('comment_id', 'comment_text', 'assignee', 'resolved') are None.
            requests.HTTPError: Raised if the HTTP request to update the comment fails.

        Tags:
            update, comment, task-management, api
        """
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        if comment_text is None:
            raise ValueError("Missing required parameter 'comment_text'")
        if assignee is None:
            raise ValueError("Missing required parameter 'assignee'")
        if resolved is None:
            raise ValueError("Missing required parameter 'resolved'")
        request_body = {
            "comment_text": comment_text,
            "assignee": assignee,
            "resolved": resolved,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/comment/{comment_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def comments_delete_task_comment(self, comment_id) -> dict[str, Any]:
        """
        Deletes a task comment by its ID.

        Args:
            comment_id: The unique identifier of the comment to be deleted.

        Returns:
            Dictionary containing the response data from the server after deleting the comment.

        Raises:
            ValueError: When the required parameter 'comment_id' is None.
            HTTPError: When the HTTP request to delete the comment fails.

        Tags:
            delete, comment, task-management, api
        """
        if comment_id is None:
            raise ValueError("Missing required parameter 'comment_id'")
        url = f"{self.base_url}/comment/{comment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def custom_fields_get_list_fields(self, list_id) -> dict[str, Any]:
        """
        Retrieves a list of custom fields associated with a specified list by its ID.

        Args:
            list_id: The unique identifier of the list for which to fetch custom fields. Must not be None.

        Returns:
            A dictionary containing the custom fields for the specified list, as returned by the API.

        Raises:
            ValueError: Raised if 'list_id' is None.
            requests.HTTPError: Raised if the HTTP request fails with an error status code.

        Tags:
            get, list, custom-fields, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}/field"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def custom_fields_remove_field_value(
        self, task_id, field_id, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Removes a specific custom field value from a given task.

        Args:
            task_id: str. The unique identifier of the task from which the field value will be removed.
            field_id: str. The unique identifier of the custom field to remove.
            custom_task_ids: Optional[list or str]. Additional task IDs to include in the operation. Defaults to None.
            team_id: Optional[str]. The ID of the team context for the operation. Defaults to None.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the result of the remove operation.

        Raises:
            ValueError: If either 'task_id' or 'field_id' is not provided.
            requests.HTTPError: If the HTTP request to remove the field value fails.

        Tags:
            custom-fields, remove, task-management, api
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if field_id is None:
            raise ValueError("Missing required parameter 'field_id'")
        url = f"{self.base_url}/task/{task_id}/field/{field_id}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_relationships_add_dependency(
        self,
        task_id,
        custom_task_ids=None,
        team_id=None,
        depends_on=None,
        depedency_of=None,
    ) -> dict[str, Any]:
        """
        Adds a dependency relationship to a specified task, allowing you to define predecessor or dependent tasks within a project management system.

        Args:
            task_id: str. The ID of the task for which the dependency is being added. Must not be None.
            custom_task_ids: Optional[list[str]]. List of custom task IDs, if applicable, to use for the operation.
            team_id: Optional[str]. Identifier for the team, if restricting the dependency operation to a specific team context.
            depends_on: Optional[list[str]]. List of task IDs that the specified task depends on.
            depedency_of: Optional[list[str]]. List of task IDs that depend on the specified task.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the updated dependency information for the task.

        Raises:
            ValueError: Raised if 'task_id' is None.
            requests.HTTPError: Raised if the HTTP request to add the dependency fails or returns an error status.

        Tags:
            add, task-relationship, dependency, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        request_body = {
            "depends_on": depends_on,
            "depedency_of": depedency_of,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}/dependency"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_relationships_remove_dependency(
        self, task_id, depends_on, dependency_of, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Removes a dependency relationship between tasks by calling the API endpoint.

        Args:
            task_id: The ID of the task from which the dependency is being removed.
            depends_on: The ID of the task that the main task depends on.
            dependency_of: The ID of the task that depends on the main task.
            custom_task_ids: Optional flag to indicate if the provided IDs are custom task IDs.
            team_id: Optional team ID to specify which team the tasks belong to.

        Returns:
            A dictionary containing the API response after removing the dependency.

        Raises:
            ValueError: Raised when any of the required parameters (task_id, depends_on, dependency_of) are None.
            HTTPError: Raised when the API request fails based on the call to raise_for_status().

        Tags:
            remove, dependency, task-management, relationship
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if depends_on is None:
            raise ValueError("Missing required parameter 'depends_on'")
        if dependency_of is None:
            raise ValueError("Missing required parameter 'dependency_of'")
        url = f"{self.base_url}/task/{task_id}/dependency"
        query_params = {
            k: v
            for k, v in [
                ("depends_on", depends_on),
                ("dependency_of", dependency_of),
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_relationships_link_tasks(
        self, task_id, links_to, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Links one task to another by creating a relationship between the source and target task IDs, with optional custom task and team identifiers.

        Args:
            task_id: str. ID of the source task to be linked. Required.
            links_to: str. ID of the target task to which the source task will be linked. Required.
            custom_task_ids: Optional[list[str]]. List of custom task IDs to use for identification within a broader context. Defaults to None.
            team_id: Optional[str]. ID of the team associated with the tasks. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the API response data for the task linking operation.

        Raises:
            ValueError: If 'task_id' or 'links_to' is None.
            HTTPError: If the HTTP request to link tasks fails (non-2xx response).

        Tags:
            link, task-relationship, api, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if links_to is None:
            raise ValueError("Missing required parameter 'links_to'")
        url = f"{self.base_url}/task/{task_id}/link/{links_to}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_relationships_remove_link_between_tasks(
        self, task_id, links_to, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Removes a link between two specified tasks within the task management system.

        Args:
            task_id: str. The unique identifier of the source task whose link is to be removed.
            links_to: str. The unique identifier of the linked task to be unlinked.
            custom_task_ids: Optional[list[str]]. A list of custom task IDs to be used in the request, if applicable.
            team_id: Optional[str]. The team ID associated with the tasks, if applicable.

        Returns:
            dict[str, Any]: The JSON response from the API after removing the link, parsed into a dictionary.

        Raises:
            ValueError: Raised if 'task_id' or 'links_to' is not provided.
            requests.HTTPError: Raised if the HTTP request fails or the API returns an error status code.

        Tags:
            remove, task-relationships, api, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if links_to is None:
            raise ValueError("Missing required parameter 'links_to'")
        url = f"{self.base_url}/task/{task_id}/link/{links_to}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def folders_get_contents_of(self, space_id, archived=None) -> dict[str, Any]:
        """
        Retrieves the contents of all folders within a specified space, with optional filtering for archived folders.

        Args:
            space_id: str. The unique identifier of the space whose folders' contents are to be retrieved.
            archived: Optional[bool]. If set, filters folders by their archived status. If None, retrieves all folders regardless of archived state.

        Returns:
            dict[str, Any]: A dictionary containing the contents of each folder in the specified space, as returned by the API.

        Raises:
            ValueError: Raised if 'space_id' is None.
            requests.HTTPError: Raised if the HTTP request to the backend API fails.

        Tags:
            get, list, folders, contents, management, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        url = f"{self.base_url}/space/{space_id}/folder"
        query_params = {k: v for k, v in [("archived", archived)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def folders_create_new_folder(self, space_id, name) -> dict[str, Any]:
        """
        Creates a new folder within a specified space.

        Args:
            space_id: The unique identifier of the space where the folder will be created.
            name: The name to be assigned to the new folder.

        Returns:
            A dictionary containing information about the newly created folder.

        Raises:
            ValueError: Raised when either 'space_id' or 'name' parameter is None.
            HTTPError: Raised when the HTTP request to create the folder fails.

        Tags:
            create, folder, management
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}/folder"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def folders_get_folder_content(self, folder_id) -> dict[str, Any]:
        """
        Retrieves the contents of a specified folder by its ID.

        Args:
            folder_id: str. The unique identifier of the folder whose content is to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the contents of the specified folder as returned by the API.

        Raises:
            ValueError: Raised if 'folder_id' is None, indicating a required parameter is missing.
            requests.HTTPError: Raised if the HTTP request to retrieve the folder content fails with an unsuccessful status code.

        Tags:
            get, folder, content, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folder/{folder_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def folders_rename_folder(self, folder_id, name) -> dict[str, Any]:
        """
        Renames an existing folder by updating its name using the specified folder ID.

        Args:
            folder_id: str. The unique identifier of the folder to be renamed.
            name: str. The new name to assign to the folder.

        Returns:
            dict[str, Any]: The JSON response from the API containing updated folder information.

        Raises:
            ValueError: If 'folder_id' or 'name' is None.
            requests.HTTPError: If the HTTP request to update the folder fails.

        Tags:
            rename, folder-management, put, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folder/{folder_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def folders_remove_folder(self, folder_id) -> dict[str, Any]:
        """
        Removes a folder with the specified folder ID by sending a DELETE request to the API.

        Args:
            folder_id: The unique identifier of the folder to be removed. Must not be None.

        Returns:
            A dictionary containing the JSON response from the API after the folder is deleted.

        Raises:
            ValueError: If 'folder_id' is None.
            requests.HTTPError: If the API response contains an HTTP error status code.

        Tags:
            remove, folder-management, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folder/{folder_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_get_workspace_goals(
        self, team_id, include_completed=None
    ) -> dict[str, Any]:
        """
        Retrieves all workspace goals for a specified team, optionally including completed goals.

        Args:
            team_id: str. Unique identifier of the team whose workspace goals are to be retrieved.
            include_completed: Optional[bool]. Whether to include completed goals in the results. If None, only active goals are returned.

        Returns:
            dict[str, Any]: A dictionary containing the workspace goals data for the specified team.

        Raises:
            ValueError: Raised when the required parameter 'team_id' is None.
            requests.HTTPError: Raised if the HTTP request to the backend API fails with a non-success status.

        Tags:
            get, list, goal-management, fetch
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/goal"
        query_params = {
            k: v for k, v in [("include_completed", include_completed)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_add_new_goal_to_workspace(
        self, team_id, description, name, due_date, multiple_owners, owners, color
    ) -> dict[str, Any]:
        """
        Adds a new goal to the specified team workspace.

        Args:
            team_id: The ID of the team to which the new goal is added.
            description: A brief description of the goal.
            name: The name of the goal.
            due_date: The due date for the goal.
            multiple_owners: Indicates whether the goal can have multiple owners.
            owners: A list of owners for the goal.
            color: The color associated with the goal.

        Returns:
            A dictionary containing the newly added goal's details.

        Raises:
            ValueError: Raised when any required parameter ('team_id', 'description', 'name', 'due_date', 'multiple_owners', 'owners', 'color') is missing.

        Tags:
            manage, goals, create, team-management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if description is None:
            raise ValueError("Missing required parameter 'description'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if due_date is None:
            raise ValueError("Missing required parameter 'due_date'")
        if multiple_owners is None:
            raise ValueError("Missing required parameter 'multiple_owners'")
        if owners is None:
            raise ValueError("Missing required parameter 'owners'")
        if color is None:
            raise ValueError("Missing required parameter 'color'")
        request_body = {
            "description": description,
            "name": name,
            "due_date": due_date,
            "multiple_owners": multiple_owners,
            "owners": owners,
            "color": color,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/goal"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_get_details(self, goal_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a goal based on the provided goal ID.

        Args:
            goal_id: ID of the goal to retrieve details for.

        Returns:
            A dictionary containing detailed information about the goal.

        Raises:
            ValueError: Raised when the goal_id parameter is missing.

        Tags:
            get, details, management
        """
        if goal_id is None:
            raise ValueError("Missing required parameter 'goal_id'")
        url = f"{self.base_url}/goal/{goal_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_update_goal_details(
        self, goal_id, description, name, due_date, rem_owners, add_owners, color
    ) -> dict[str, Any]:
        """
        Updates the details of an existing goal with new information, including description, name, due date, owners, and color.

        Args:
            goal_id: str. The unique identifier of the goal to update.
            description: str. The updated description for the goal.
            name: str. The new name for the goal.
            due_date: str. The new due date for the goal, typically in ISO 8601 format.
            rem_owners: list. List of owner identifiers to remove from the goal.
            add_owners: list. List of owner identifiers to add to the goal.
            color: str. The color code or name representing the goal's new color.

        Returns:
            dict[str, Any]: A dictionary containing the updated goal details as returned by the server.

        Raises:
            ValueError: If any of the required parameters ('goal_id', 'description', 'name', 'due_date', 'rem_owners', 'add_owners', 'color') is None.
            requests.HTTPError: If the server returns an unsuccessful status code during the update request.

        Tags:
            update, goal-management, async_job
        """
        if goal_id is None:
            raise ValueError("Missing required parameter 'goal_id'")
        if description is None:
            raise ValueError("Missing required parameter 'description'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if due_date is None:
            raise ValueError("Missing required parameter 'due_date'")
        if rem_owners is None:
            raise ValueError("Missing required parameter 'rem_owners'")
        if add_owners is None:
            raise ValueError("Missing required parameter 'add_owners'")
        if color is None:
            raise ValueError("Missing required parameter 'color'")
        request_body = {
            "description": description,
            "name": name,
            "due_date": due_date,
            "rem_owners": rem_owners,
            "add_owners": add_owners,
            "color": color,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/goal/{goal_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_remove_goal(self, goal_id) -> dict[str, Any]:
        """
        Removes a goal from the system using the specified goal ID.

        Args:
            goal_id: The unique identifier of the goal to be removed. Cannot be None.

        Returns:
            A dictionary containing the API response after goal deletion.

        Raises:
            ValueError: Raised when the required goal_id parameter is None.
            HTTPError: Raised when the HTTP request to delete the goal fails.

        Tags:
            remove, delete, goal, management
        """
        if goal_id is None:
            raise ValueError("Missing required parameter 'goal_id'")
        url = f"{self.base_url}/goal/{goal_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_add_key_result(
        self,
        goal_id,
        name,
        owners,
        type,
        steps_start,
        steps_end,
        unit,
        task_ids,
        list_ids,
    ) -> dict[str, Any]:
        """
        Creates and adds a new key result to a specified goal with the provided details and associated tasks/lists.

        Args:
            goal_id: str. Unique identifier of the goal to which the key result will be added.
            name: str. Name of the key result.
            owners: list. List of user identifiers who own the key result.
            type: str. Type or category of the key result.
            steps_start: int or float. The starting value or progress metric for the key result.
            steps_end: int or float. The target value or ending progress metric for the key result.
            unit: str. Unit of measurement for the key result's progress (e.g., 'percent', 'tasks').
            task_ids: list. List of task IDs associated with the key result.
            list_ids: list. List of list IDs to associate with the key result.

        Returns:
            dict. The JSON response containing details of the newly created key result.

        Raises:
            ValueError: Raised if any required parameter (goal_id, name, owners, type, steps_start, steps_end, unit, task_ids, list_ids) is None.
            requests.HTTPError: Raised if the HTTP request fails (non-success response status).

        Tags:
            add, key-result, goals, management
        """
        if goal_id is None:
            raise ValueError("Missing required parameter 'goal_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if owners is None:
            raise ValueError("Missing required parameter 'owners'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if steps_start is None:
            raise ValueError("Missing required parameter 'steps_start'")
        if steps_end is None:
            raise ValueError("Missing required parameter 'steps_end'")
        if unit is None:
            raise ValueError("Missing required parameter 'unit'")
        if task_ids is None:
            raise ValueError("Missing required parameter 'task_ids'")
        if list_ids is None:
            raise ValueError("Missing required parameter 'list_ids'")
        request_body = {
            "name": name,
            "owners": owners,
            "type": type,
            "steps_start": steps_start,
            "steps_end": steps_end,
            "unit": unit,
            "task_ids": task_ids,
            "list_ids": list_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/goal/{goal_id}/key_result"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_update_key_result(
        self, key_result_id, steps_current, note
    ) -> dict[str, Any]:
        """
        Updates the current number of steps and note for a specific key result.

        Args:
            key_result_id: The unique identifier of the key result to update.
            steps_current: The current number of steps achieved for the key result.
            note: A note or comment associated with the update.

        Returns:
            A dictionary containing the updated key result data as returned by the server.

        Raises:
            ValueError: If any of 'key_result_id', 'steps_current', or 'note' is None.
            requests.HTTPError: If the HTTP PUT request fails (non-success response from the server).

        Tags:
            update, goals, management, key-result
        """
        if key_result_id is None:
            raise ValueError("Missing required parameter 'key_result_id'")
        if steps_current is None:
            raise ValueError("Missing required parameter 'steps_current'")
        if note is None:
            raise ValueError("Missing required parameter 'note'")
        request_body = {
            "steps_current": steps_current,
            "note": note,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/key_result/{key_result_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def goals_remove_target(self, key_result_id) -> dict[str, Any]:
        """
        Removes the target associated with a specified key result by sending a DELETE request to the API.

        Args:
            key_result_id: The unique identifier of the key result whose target is to be removed.

        Returns:
            A dictionary representing the JSON response from the API after the target is removed.

        Raises:
            ValueError: If 'key_result_id' is None.
            requests.HTTPError: If the DELETE HTTP request fails or returns an error status.

        Tags:
            remove, management, api
        """
        if key_result_id is None:
            raise ValueError("Missing required parameter 'key_result_id'")
        url = f"{self.base_url}/key_result/{key_result_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_invite_to_workspace(
        self,
        team_id,
        email,
        can_edit_tags,
        can_see_time_spent,
        can_see_time_estimated,
        can_create_views,
        custom_role_id,
    ) -> dict[str, Any]:
        """
        Invites a guest to a workspace with specific permissions.

        Args:
            team_id: The unique identifier of the team/workspace.
            email: Email address of the guest to invite.
            can_edit_tags: Boolean indicating if the guest can edit tags.
            can_see_time_spent: Boolean indicating if the guest can see time spent on tasks.
            can_see_time_estimated: Boolean indicating if the guest can see estimated time for tasks.
            can_create_views: Boolean indicating if the guest can create views.
            custom_role_id: The ID of the custom role to assign to the guest.

        Returns:
            A dictionary containing the response data from the API.

        Raises:
            ValueError: Raised when any required parameter is None.
            HTTPError: Raised when the API request fails.

        Tags:
            invite, guest, workspace, permission, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        if can_edit_tags is None:
            raise ValueError("Missing required parameter 'can_edit_tags'")
        if can_see_time_spent is None:
            raise ValueError("Missing required parameter 'can_see_time_spent'")
        if can_see_time_estimated is None:
            raise ValueError("Missing required parameter 'can_see_time_estimated'")
        if can_create_views is None:
            raise ValueError("Missing required parameter 'can_create_views'")
        if custom_role_id is None:
            raise ValueError("Missing required parameter 'custom_role_id'")
        request_body = {
            "email": email,
            "can_edit_tags": can_edit_tags,
            "can_see_time_spent": can_see_time_spent,
            "can_see_time_estimated": can_see_time_estimated,
            "can_create_views": can_create_views,
            "custom_role_id": custom_role_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/guest"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_get_guest_information(self, team_id, guest_id) -> dict[str, Any]:
        """
        Fetches guest information for a specific guest in a team.

        Args:
            team_id: The ID of the team.
            guest_id: The ID of the guest.

        Returns:
            A dictionary containing the guest information.

        Raises:
            ValueError: Raised when either team_id or guest_id is missing.

        Tags:
            fetch, guest, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        url = f"{self.base_url}/team/{team_id}/guest/{guest_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_edit_guest_on_workspace(
        self,
        team_id,
        guest_id,
        username,
        can_edit_tags,
        can_see_time_spent,
        can_see_time_estimated,
        can_create_views,
        custom_role_id,
    ) -> dict[str, Any]:
        """
        Edits a guest user's permissions and role within a specified workspace team.

        Args:
            team_id: str. The unique identifier of the workspace team.
            guest_id: str. The unique identifier of the guest user to edit.
            username: str. The guest user's username.
            can_edit_tags: bool. Whether the guest can edit tags in the workspace.
            can_see_time_spent: bool. Whether the guest can view time spent information.
            can_see_time_estimated: bool. Whether the guest can view estimated time information.
            can_create_views: bool. Whether the guest can create new views in the workspace.
            custom_role_id: str. Identifier for a custom role to assign to the guest user.

        Returns:
            dict[str, Any]: A dictionary representing the updated guest user resource as returned by the workspace API.

        Raises:
            ValueError: If any of the required parameters ('team_id', 'guest_id', 'username', 'can_edit_tags', 'can_see_time_spent', 'can_see_time_estimated', 'can_create_views', 'custom_role_id') are None.
            requests.HTTPError: If the HTTP request to update the guest fails (e.g., due to network errors or unsuccessful response status).

        Tags:
            edit, guest-management, workspace, api, permissions
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        if can_edit_tags is None:
            raise ValueError("Missing required parameter 'can_edit_tags'")
        if can_see_time_spent is None:
            raise ValueError("Missing required parameter 'can_see_time_spent'")
        if can_see_time_estimated is None:
            raise ValueError("Missing required parameter 'can_see_time_estimated'")
        if can_create_views is None:
            raise ValueError("Missing required parameter 'can_create_views'")
        if custom_role_id is None:
            raise ValueError("Missing required parameter 'custom_role_id'")
        request_body = {
            "username": username,
            "can_edit_tags": can_edit_tags,
            "can_see_time_spent": can_see_time_spent,
            "can_see_time_estimated": can_see_time_estimated,
            "can_create_views": can_create_views,
            "custom_role_id": custom_role_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/guest/{guest_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_revoke_guest_access_to_workspace(
        self, team_id, guest_id
    ) -> dict[str, Any]:
        """
        Revokes a guest's access to a workspace for a specified team.

        Args:
            team_id: str. The unique identifier of the team whose workspace the guest will lose access to.
            guest_id: str. The unique identifier of the guest whose access is being revoked.

        Returns:
            dict[str, Any]: The response data from the API, typically containing details about the revoked guest access.

        Raises:
            ValueError: Raised if 'team_id' or 'guest_id' is None.
            requests.HTTPError: Raised if the HTTP request fails (non-2xx response).

        Tags:
            revoke, access-control, guest-management, workspace
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        url = f"{self.base_url}/team/{team_id}/guest/{guest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_add_to_task(
        self,
        task_id,
        guest_id,
        permission_level,
        include_shared=None,
        custom_task_ids=None,
        team_id=None,
    ) -> dict[str, Any]:
        """
        Adds a guest to a task with specified permission level and optional parameters.

        Args:
            task_id: The ID of the task to which the guest is being added.
            guest_id: The ID of the guest to add to the task.
            permission_level: The permission level granted to the guest.
            include_shared: Optional parameter to include shared tasks.
            custom_task_ids: Optional list of custom task IDs.
            team_id: Optional ID of the team related to the task.

        Returns:
            A dictionary containing the response from adding a guest to the task.

        Raises:
            ValueError: Raised when task_id, guest_id, or permission_level is missing.

        Tags:
            add, manage, task, guest, permission, async_job
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        if permission_level is None:
            raise ValueError("Missing required parameter 'permission_level'")
        request_body = {
            "permission_level": permission_level,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}/guest/{guest_id}"
        query_params = {
            k: v
            for k, v in [
                ("include_shared", include_shared),
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
            ]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_revoke_access_to_task(
        self, task_id, guest_id, include_shared=None, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Revokes a guest user's access to a specific task, with options to customize the revocation scope.

        Args:
            task_id: str. The unique identifier of the task from which guest access is being revoked.
            guest_id: str. The unique identifier of the guest whose access will be revoked.
            include_shared: Optional[bool]. Whether to include shared tasks in the revocation process.
            custom_task_ids: Optional[list or str]. Custom task identifiers to further specify which tasks to affect.
            team_id: Optional[str]. The identifier of the team if the task is associated with a team context.

        Returns:
            dict[str, Any]: A dictionary containing the API response data after revoking access.

        Raises:
            ValueError: If either 'task_id' or 'guest_id' is not provided.
            HTTPError: If the API request to revoke access fails.

        Tags:
            guests, revoke, access, task, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        url = f"{self.base_url}/task/{task_id}/guest/{guest_id}"
        query_params = {
            k: v
            for k, v in [
                ("include_shared", include_shared),
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_share_list_with(
        self, list_id, guest_id, permission_level, include_shared=None
    ) -> dict[str, Any]:
        """
        Shares a list with a specified guest by assigning a permission level and optionally including shared items.

        Args:
            list_id: The unique identifier of the list to be shared.
            guest_id: The unique identifier of the guest with whom the list will be shared.
            permission_level: The access level to grant the guest (e.g., 'read', 'edit').
            include_shared: Optional; if provided, specifies whether to include items already shared with the guest.

        Returns:
            A dictionary containing the response data from the share operation, typically including sharing status and permissions.

        Raises:
            ValueError: If any of the required parameters ('list_id', 'guest_id', or 'permission_level') are missing.
            requests.HTTPError: If the HTTP request to share the list fails (e.g., due to network issues or invalid input).

        Tags:
            share, list, permission-management, guest
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        if permission_level is None:
            raise ValueError("Missing required parameter 'permission_level'")
        request_body = {
            "permission_level": permission_level,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/list/{list_id}/guest/{guest_id}"
        query_params = {
            k: v for k, v in [("include_shared", include_shared)] if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_remove_from_list(
        self, list_id, guest_id, include_shared=None
    ) -> dict[str, Any]:
        """
        Removes a guest from a specified list, optionally including shared guests in the operation.

        Args:
            list_id: The unique identifier of the list from which the guest will be removed. Must not be None.
            guest_id: The unique identifier of the guest to remove. Must not be None.
            include_shared: Optional; if provided, determines whether shared guests should be included in the removal.

        Returns:
            A dictionary containing the response data from the removal operation.

        Raises:
            ValueError: Raised if 'list_id' or 'guest_id' is None.
            requests.HTTPError: Raised if the HTTP request to remove the guest fails.

        Tags:
            guests, remove, management, list
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        url = f"{self.base_url}/list/{list_id}/guest/{guest_id}"
        query_params = {
            k: v for k, v in [("include_shared", include_shared)] if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_add_guest_to_folder(
        self, folder_id, guest_id, permission_level, include_shared=None
    ) -> dict[str, Any]:
        """
        Adds a guest to a specified folder with a given permission level, optionally including shared folders.

        Args:
            folder_id: str. The unique identifier of the folder to which the guest will be added.
            guest_id: str. The unique identifier of the guest user to add to the folder.
            permission_level: str. The permission level to assign to the guest (e.g., 'read', 'write').
            include_shared: Optional[bool]. If True, includes shared folders in the operation. Defaults to None.

        Returns:
            dict[str, Any]: The server response as a dictionary containing the details of the updated folder and guest permissions.

        Raises:
            ValueError: If 'folder_id', 'guest_id', or 'permission_level' is None.
            requests.HTTPError: If the HTTP request to the server fails or returns an error status.

        Tags:
            add, guest-management, folder-permissions, api-call
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        if permission_level is None:
            raise ValueError("Missing required parameter 'permission_level'")
        request_body = {
            "permission_level": permission_level,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folder/{folder_id}/guest/{guest_id}"
        query_params = {
            k: v for k, v in [("include_shared", include_shared)] if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def guests_revoke_access_from_folder(
        self, folder_id, guest_id, include_shared=None
    ) -> dict[str, Any]:
        """
        Revokes a guest's access from a specified folder, with optional inclusion of shared resources.

        Args:
            folder_id: str. The unique identifier of the folder from which to revoke access.
            guest_id: str. The unique identifier of the guest whose access will be revoked.
            include_shared: Optional[bool]. If True, also revokes access from shared resources. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the API response to the revoke operation.

        Raises:
            ValueError: Raised if 'folder_id' or 'guest_id' is not provided.
            requests.HTTPError: Raised if the HTTP request to revoke access fails.

        Tags:
            guests, revoke, access, folder-management, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if guest_id is None:
            raise ValueError("Missing required parameter 'guest_id'")
        url = f"{self.base_url}/folder/{folder_id}/guest/{guest_id}"
        query_params = {
            k: v for k, v in [("include_shared", include_shared)] if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_folder_lists(self, folder_id, archived=None) -> dict[str, Any]:
        """
        Retrieves all lists contained within a specified folder, with optional filtering for archived lists.

        Args:
            folder_id: The unique identifier of the folder whose lists are to be retrieved.
            archived: Optional; if provided, filters lists by their archived status (e.g., True for archived, False for active, None for all).

        Returns:
            A dictionary containing the folder's lists and associated metadata as provided by the API.

        Raises:
            ValueError: Raised if 'folder_id' is not provided.
            requests.HTTPError: Raised if the HTTP request to fetch the folder's lists fails (e.g., non-2xx response).

        Tags:
            list, get, folder, search, api , important
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folder/{folder_id}/list"
        query_params = {k: v for k, v in [("archived", archived)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_to_folder(
        self,
        folder_id,
        name,
        content=None,
        due_date=None,
        due_date_time=None,
        priority=None,
        assignee=None,
        status=None,
    ) -> dict[str, Any]:
        """
        Creates a new list in the specified folder with the given name and optional attributes.

        Args:
            folder_id: str. Unique identifier of the folder to which the list will be added.
            name: str. Name of the list to create in the folder.
            content: Optional[str]. Additional content or description for the list.
            due_date: Optional[str]. Due date for the list, if applicable.
            due_date_time: Optional[str]. Due date and time for the list, if applicable.
            priority: Optional[int]. Priority level assigned to the list.
            assignee: Optional[str]. User assigned to the list.
            status: Optional[str]. Status of the list (e.g., 'active', 'completed').

        Returns:
            dict. The API response containing details of the newly created list.

        Raises:
            ValueError: If 'folder_id' or 'name' is not provided.
            HTTPError: If the API request fails or returns an error status code.

        Tags:
            list, add, folder, management, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "content": content,
            "due_date": due_date,
            "due_date_time": due_date_time,
            "priority": priority,
            "assignee": assignee,
            "status": status,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folder/{folder_id}/list"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_folderless(self, space_id, archived=None) -> dict[str, Any]:
        """
        Retrieves all lists within the specified space that are not associated with a folder.

        Args:
            space_id: str. The unique identifier for the space from which to fetch folderless lists.
            archived: Optional[bool]. If provided, filters the results to include only archived or non-archived lists.

        Returns:
            dict[str, Any]: A dictionary containing the API response with details of folderless lists for the specified space.

        Raises:
            ValueError: Raised if 'space_id' is None.
            HTTPError: Raised if the HTTP request to the API fails with a status error.

        Tags:
            list, fetch, management, api, important
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        url = f"{self.base_url}/space/{space_id}/list"
        query_params = {k: v for k, v in [("archived", archived)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_create_folderless_list(
        self,
        space_id,
        name,
        content=None,
        due_date=None,
        due_date_time=None,
        priority=None,
        assignee=None,
        status=None,
    ) -> dict[str, Any]:
        """
        Creates a new list within a specified space without associating it with a folder.

        Args:
            space_id: str. The unique identifier of the space in which to create the list.
            name: str. The name of the list to be created.
            content: Optional[str]. Additional description or content for the list.
            due_date: Optional[str]. The due date for the list, if any (format may vary by system).
            due_date_time: Optional[str]. The due date and time for the list, if required (format may vary by system).
            priority: Optional[int]. Numeric priority value for the list, where higher values indicate higher priority.
            assignee: Optional[str]. Identifier of the user assigned to the list, if any.
            status: Optional[str]. Status of the list (e.g., 'active', 'completed').

        Returns:
            dict[str, Any]: The JSON response from the API containing the details of the newly created list.

        Raises:
            ValueError: If 'space_id' or 'name' is not provided.
            requests.HTTPError: If the API request fails with an HTTP error status.

        Tags:
            list, create, management, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "content": content,
            "due_date": due_date,
            "due_date_time": due_date_time,
            "priority": priority,
            "assignee": assignee,
            "status": status,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}/list"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_list_details(self, list_id) -> dict[str, Any]:
        """
        Retrieves the details of a specific list by its unique identifier.

        Args:
            list_id: The unique identifier of the list to retrieve details for.

        Returns:
            A dictionary containing the details of the specified list as returned by the API.

        Raises:
            ValueError: If 'list_id' is None.
            requests.HTTPError: If the HTTP request fails or the response contains an unsuccessful status code.

        Tags:
            get, list, details, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_list_info_due_date_priority_assignee_color(
        self,
        list_id,
        name,
        content,
        due_date,
        due_date_time,
        priority,
        assignee,
        status,
        unset_status,
    ) -> dict[str, Any]:
        """
        Updates the information of a list, including name, content, due date, priority, assignee, status, and color attributes.

        Args:
            list_id: The unique identifier of the list to update.
            name: The new name of the list.
            content: The updated content or description of the list.
            due_date: The due date for the list item (string, typically in ISO format).
            due_date_time: The due date and time for the list item (string, typically in ISO format).
            priority: The priority level assigned to the list item.
            assignee: The user or entity assigned to the list item.
            status: The status to set for the list item.
            unset_status: Whether to unset the current status (boolean or flag).

        Returns:
            A dictionary containing the updated list information as returned by the API.

        Raises:
            ValueError: If any required parameter is missing.
            requests.HTTPError: If the HTTP request fails or returns an error status code.

        Tags:
            update, list-management, async-job, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if content is None:
            raise ValueError("Missing required parameter 'content'")
        if due_date is None:
            raise ValueError("Missing required parameter 'due_date'")
        if due_date_time is None:
            raise ValueError("Missing required parameter 'due_date_time'")
        if priority is None:
            raise ValueError("Missing required parameter 'priority'")
        if assignee is None:
            raise ValueError("Missing required parameter 'assignee'")
        if status is None:
            raise ValueError("Missing required parameter 'status'")
        if unset_status is None:
            raise ValueError("Missing required parameter 'unset_status'")
        request_body = {
            "name": name,
            "content": content,
            "due_date": due_date,
            "due_date_time": due_date_time,
            "priority": priority,
            "assignee": assignee,
            "status": status,
            "unset_status": unset_status,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/list/{list_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_remove_list(self, list_id) -> dict[str, Any]:
        """
        Removes a list with the specified list ID via an HTTP DELETE request and returns the API response as a dictionary.

        Args:
            list_id: The unique identifier of the list to remove. Must not be None.

        Returns:
            A dictionary representing the JSON response from the API after deleting the specified list.

        Raises:
            ValueError: If 'list_id' is None.
            HTTPError: If the HTTP DELETE request fails with an error status code.

        Tags:
            remove, list, delete, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_task_to_list(self, list_id, task_id) -> dict[str, Any]:
        """
        Adds a task to a specified list.

        Args:
            list_id: The unique identifier of the list to which the task will be added.
            task_id: The unique identifier of the task to be added to the list.

        Returns:
            A dictionary containing the API response data after the task has been added to the list.

        Raises:
            ValueError: If either list_id or task_id is None.
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            add, task, list, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/list/{list_id}/task/{task_id}"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_remove_task_from_list(self, list_id, task_id) -> dict[str, Any]:
        """
        Removes a specific task from a list by sending a DELETE request to the appropriate API endpoint.

        Args:
            list_id: The unique identifier of the list from which the task will be removed.
            task_id: The unique identifier of the task to be removed from the list.

        Returns:
            A dictionary containing the API response data after removing the task.

        Raises:
            ValueError: Raised if 'list_id' or 'task_id' is None.
            requests.HTTPError: Raised if the HTTP request to remove the task fails.

        Tags:
            remove, task, list, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/list/{list_id}/task/{task_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def members_get_task_access(self, task_id) -> dict[str, Any]:
        """
        Retrieves a list of members who have access to the specified task.

        Args:
            task_id: The unique identifier of the task for which to fetch member access (str or int).

        Returns:
            A dictionary containing information about the members with access to the specified task.

        Raises:
            ValueError: Raised if 'task_id' is None.
            HTTPError: Raised if the HTTP request to retrieve the task members fails.

        Tags:
            members, get, task, access, fetch
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/task/{task_id}/member"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def members_get_list_users(self, list_id) -> dict[str, Any]:
        """
        Retrieves the list of users who are members of the specified list.

        Args:
            list_id: The unique identifier of the list for which to retrieve member users.

        Returns:
            A dictionary containing the response data with user membership details for the specified list.

        Raises:
            ValueError: If 'list_id' is None.
            requests.HTTPError: If the HTTP request to fetch the list members fails.

        Tags:
            get, list, users, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}/member"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def roles_list_available_custom_roles(
        self, team_id, include_members=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of available custom roles for a specified team, optionally including role members.

        Args:
            team_id: The ID of the team for which to retrieve custom roles.
            include_members: Optional flag indicating whether to include role members in the response. Defaults to None.

        Returns:
            A dictionary containing custom roles with optional member details.

        Raises:
            ValueError: Raised when the 'team_id' parameter is missing.

        Tags:
            list, custom-roles, team-management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/customroles"
        query_params = {
            k: v for k, v in [("include_members", include_members)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def shared_hierarchy_view_tasks_lists_folders(self, team_id) -> dict[str, Any]:
        """
        Retrieves the shared hierarchy view including tasks, lists, and folders for a specified team.

        Args:
            team_id: The unique identifier of the team whose shared hierarchy is being retrieved. Cannot be None.

        Returns:
            A dictionary containing the shared hierarchy data with tasks, lists, and folders for the specified team.

        Raises:
            ValueError: Raised when the required team_id parameter is None.
            HTTPError: Raised when the HTTP request fails (via raise_for_status()).

        Tags:
            retrieve, view, hierarchy, team, shared
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/shared"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def spaces_get_space_details(self, team_id, archived=None) -> dict[str, Any]:
        """
        Retrieves details about spaces within a specified team, optionally filtering by archived status.

        Args:
            team_id: str. Unique identifier for the team whose space details are to be retrieved.
            archived: Optional[bool]. If provided, filters the results to include only archived or non-archived spaces.

        Returns:
            dict[str, Any]: A dictionary containing the space details returned by the API.

        Raises:
            ValueError: Raised if 'team_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails.

        Tags:
            get, spaces, team-management, api-call
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/space"
        query_params = {k: v for k, v in [("archived", archived)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def spaces_add_new_space_to_workspace(
        self, team_id, name, multiple_assignees, features
    ) -> dict[str, Any]:
        """
        Creates a new space within a specified workspace team, configuring assignment settings and desired features.

        Args:
            team_id: str. The unique identifier of the workspace team in which to create the new space.
            name: str. The name to assign to the new space.
            multiple_assignees: bool. Indicates whether tasks in the new space can have multiple assignees.
            features: Any. Features to enable for the new space. The exact type and structure may depend on the underlying API.

        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created space, as returned by the API.

        Raises:
            ValueError: Raised if any of the required parameters ('team_id', 'name', 'multiple_assignees', or 'features') is None.
            requests.HTTPError: Raised if the POST request to the API endpoint fails or returns an unsuccessful status code.

        Tags:
            add, create, space, workspace, management, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if multiple_assignees is None:
            raise ValueError("Missing required parameter 'multiple_assignees'")
        if features is None:
            raise ValueError("Missing required parameter 'features'")
        request_body = {
            "name": name,
            "multiple_assignees": multiple_assignees,
            "features": features,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/space"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def spaces_get_details(self, space_id) -> dict[str, Any]:
        """
        Retrieves the details of a specified space by its unique identifier.

        Args:
            space_id: str. The unique identifier of the space to retrieve details for.

        Returns:
            dict[str, Any]. A dictionary containing the details of the requested space as returned by the API.

        Raises:
            ValueError: If the 'space_id' parameter is None.
            requests.HTTPError: If the HTTP request to retrieve the space details fails.

        Tags:
            get, details, space, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        url = f"{self.base_url}/space/{space_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def spaces_update_details_and_enable_click_apps(
        self,
        space_id,
        name,
        color,
        private,
        admin_can_manage,
        multiple_assignees,
        features,
    ) -> dict[str, Any]:
        """
        Updates the details of a specific space and enables click apps by sending a PUT request with the provided attributes.

        Args:
            space_id: str. The unique identifier of the space to update.
            name: str. The new name to assign to the space.
            color: str. The color code or name for the space.
            private: bool. Whether the space should be private.
            admin_can_manage: bool. Specifies if admins can manage the space.
            multiple_assignees: bool. Allow multiple users to be assigned to tasks in the space.
            features: Any. Additional features or settings to enable for the space.

        Returns:
            dict[str, Any]: The updated space details as returned by the server.

        Raises:
            ValueError: If any required parameter (space_id, name, color, private, admin_can_manage, multiple_assignees, or features) is None.
            requests.HTTPError: If the server returns an error response status.

        Tags:
            update, spaces, management, http, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if color is None:
            raise ValueError("Missing required parameter 'color'")
        if private is None:
            raise ValueError("Missing required parameter 'private'")
        if admin_can_manage is None:
            raise ValueError("Missing required parameter 'admin_can_manage'")
        if multiple_assignees is None:
            raise ValueError("Missing required parameter 'multiple_assignees'")
        if features is None:
            raise ValueError("Missing required parameter 'features'")
        request_body = {
            "name": name,
            "color": color,
            "private": private,
            "admin_can_manage": admin_can_manage,
            "multiple_assignees": multiple_assignees,
            "features": features,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def spaces_remove_space(self, space_id) -> dict[str, Any]:
        """
        Removes a space identified by the given space_id.

        Args:
            space_id: The unique identifier of the space to be removed. Cannot be None.

        Returns:
            A dictionary containing the JSON response from the server after space deletion.

        Raises:
            ValueError: Raised when space_id is None.
            HTTPError: Raised when the HTTP request fails or returns an error status code.

        Tags:
            remove, delete, space, management
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        url = f"{self.base_url}/space/{space_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tags_get_space(self, space_id) -> dict[str, Any]:
        """
        Retrieves all tags associated with a specific space by its unique identifier.

        Args:
            space_id: str. The unique identifier of the space whose tags are to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the tags for the specified space, as parsed from the JSON response.

        Raises:
            ValueError: If the 'space_id' parameter is None.
            requests.HTTPError: If the HTTP request to retrieve tags fails (non-2xx response).

        Tags:
            get, list, space, tags, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        url = f"{self.base_url}/space/{space_id}/tag"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tags_create_space_tag(self, space_id, tag) -> dict[str, Any]:
        """
        Creates a new tag for a specified space by sending a POST request to the space tag API endpoint.

        Args:
            space_id: The unique identifier of the space to which the tag will be added. Must not be None.
            tag: The tag to associate with the specified space. Must not be None.

        Returns:
            A dictionary containing the API response representing the created tag.

        Raises:
            ValueError: If 'space_id' or 'tag' is None.
            requests.HTTPError: If the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            create, tag, space, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if tag is None:
            raise ValueError("Missing required parameter 'tag'")
        request_body = {
            "tag": tag,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}/tag"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def tags_update_space_tag(self, space_id, tag_name, tag) -> dict[str, Any]:
        """
        Updates a tag for a specified space by sending a PUT request with the provided tag data.

        Args:
            space_id: str. The unique identifier of the space whose tag is to be updated.
            tag_name: str. The name of the tag to update for the specified space.
            tag: Any. The new value or data for the tag to be updated.

        Returns:
            dict[str, Any]: The response payload from the API after updating the tag, parsed as a dictionary.

        Raises:
            ValueError: If 'space_id', 'tag_name', or 'tag' is None.
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            update, tag, api, space-management
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if tag_name is None:
            raise ValueError("Missing required parameter 'tag_name'")
        if tag is None:
            raise ValueError("Missing required parameter 'tag'")
        request_body = {
            "tag": tag,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}/tag/{tag_name}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def tags_remove_space_tag(self, space_id, tag_name, tag) -> dict[str, Any]:
        """
        Removes a specified tag from a given space by tag name.

        Args:
            space_id: The unique identifier of the space from which the tag will be removed.
            tag_name: The name of the tag group or category under which the tag exists.
            tag: The tag to be removed from the specified space.

        Returns:
            A dictionary containing the response data from the API after removing the tag.

        Raises:
            ValueError: Raised if 'space_id', 'tag_name', or 'tag' is None.
            requests.HTTPError: Raised if the HTTP request to remove the tag fails (non-2xx response).

        Tags:
            tag-remove, space-management, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if tag_name is None:
            raise ValueError("Missing required parameter 'tag_name'")
        if tag is None:
            raise ValueError("Missing required parameter 'tag'")
        request_body = {
            "tag": tag,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}/tag/{tag_name}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tags_add_to_task(
        self, task_id, tag_name, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Adds a tag to a specific task.

        Args:
            task_id: The unique identifier of the task to which the tag will be added.
            tag_name: The name of the tag to add to the task.
            custom_task_ids: Optional flag to indicate if task_id is a custom identifier rather than a system-generated ID.
            team_id: Optional identifier for a specific team context.

        Returns:
            A dictionary containing the response data from the API about the tag operation.

        Raises:
            ValueError: Raised when required parameters 'task_id' or 'tag_name' are None.
            HTTPError: Raised when the API request fails.

        Tags:
            add, tag, task, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if tag_name is None:
            raise ValueError("Missing required parameter 'tag_name'")
        url = f"{self.base_url}/task/{task_id}/tag/{tag_name}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def tags_remove_from_task(
        self, task_id, tag_name, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Removes a specific tag from a task by ID, with optional filtering by custom task IDs and team ID.

        Args:
            task_id: The ID of the task from which the tag is to be removed.
            tag_name: The name of the tag to be removed.
            custom_task_ids: Optional; a list of custom task IDs to filter by.
            team_id: Optional; the ID of the team to which the task belongs.

        Returns:
            A dictionary containing the response after removing the tag from the task.

        Raises:
            ValueError: Raised when either 'task_id' or 'tag_name' is missing.

        Tags:
            remove, task, management, tag
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if tag_name is None:
            raise ValueError("Missing required parameter 'tag_name'")
        url = f"{self.base_url}/task/{task_id}/tag/{tag_name}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_get_list_tasks(
        self,
        list_id,
        archived=None,
        include_markdown_description=None,
        page=None,
        order_by=None,
        reverse=None,
        subtasks=None,
        statuses=None,
        include_closed=None,
        assignees=None,
        tags=None,
        due_date_gt=None,
        due_date_lt=None,
        date_created_gt=None,
        date_created_lt=None,
        date_updated_gt=None,
        date_updated_lt=None,
        date_done_gt=None,
        date_done_lt=None,
        custom_fields=None,
        custom_items=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of tasks from a specified list with optional filters such as archived status, pagination, sorting, subtask inclusion, status, assignees, tags, date ranges, and custom fields.

        Args:
            list_id: str. The unique identifier of the list from which to retrieve tasks. Required.
            archived: Optional[bool]. If set, filter tasks by archived status.
            include_markdown_description: Optional[bool]. If True, include the markdown description in the response.
            page: Optional[int]. The page number for paginated results.
            order_by: Optional[str]. Field to order the results by.
            reverse: Optional[bool]. If True, reverse the ordering of the results.
            subtasks: Optional[bool]. If True, include subtasks in the response.
            statuses: Optional[list[str]]. Filter tasks by their statuses.
            include_closed: Optional[bool]. If True, include closed tasks in the results.
            assignees: Optional[list[str]]. Filter tasks by assignee(s).
            tags: Optional[list[str]]. Filter tasks by associated tags.
            due_date_gt: Optional[str]. Include tasks with a due date greater than this value (ISO 8601 format).
            due_date_lt: Optional[str]. Include tasks with a due date less than this value (ISO 8601 format).
            date_created_gt: Optional[str]. Include tasks created after this date (ISO 8601 format).
            date_created_lt: Optional[str]. Include tasks created before this date (ISO 8601 format).
            date_updated_gt: Optional[str]. Include tasks updated after this date (ISO 8601 format).
            date_updated_lt: Optional[str]. Include tasks updated before this date (ISO 8601 format).
            date_done_gt: Optional[str]. Include tasks completed after this date (ISO 8601 format).
            date_done_lt: Optional[str]. Include tasks completed before this date (ISO 8601 format).
            custom_fields: Optional[dict[str, Any]]. Filter tasks by specified custom fields.
            custom_items: Optional[list[str]]. Filter tasks by custom items.

        Returns:
            dict[str, Any]: A dictionary containing the list of tasks matching the filters and additional metadata as provided by the API response.

        Raises:
            ValueError: If 'list_id' is not provided.
            requests.HTTPError: If the HTTP request fails or the API responds with an error status code.

        Tags:
            list, tasks, fetch, filter, api, management, important
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}/task"
        query_params = {
            k: v
            for k, v in [
                ("archived", archived),
                ("include_markdown_description", include_markdown_description),
                ("page", page),
                ("order_by", order_by),
                ("reverse", reverse),
                ("subtasks", subtasks),
                ("statuses", statuses),
                ("include_closed", include_closed),
                ("assignees", assignees),
                ("tags", tags),
                ("due_date_gt", due_date_gt),
                ("due_date_lt", due_date_lt),
                ("date_created_gt", date_created_gt),
                ("date_created_lt", date_created_lt),
                ("date_updated_gt", date_updated_gt),
                ("date_updated_lt", date_updated_lt),
                ("date_done_gt", date_done_gt),
                ("date_done_lt", date_done_lt),
                ("custom_fields", custom_fields),
                ("custom_items", custom_items),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_create_new_task(
        self,
        list_id,
        name,
        custom_task_ids=None,
        team_id=None,
        tags=None,
        description=None,
        assignees=None,
        status=None,
        priority=None,
        due_date=None,
        due_date_time=None,
        time_estimate=None,
        start_date=None,
        start_date_time=None,
        notify_all=None,
        parent=None,
        links_to=None,
        check_required_custom_fields=None,
        custom_fields=None,
        custom_item_id=None,
    ) -> dict[str, Any]:
        """
        Creates a new task in the specified list with optional attributes including tags, assignees, status, priority, dates, and custom fields.

        Args:
            list_id: str. The unique identifier of the list where the task will be created. Required.
            name: str. The name or title of the new task. Required.
            custom_task_ids: Optional[str]. Custom task identifiers for the request, if applicable.
            team_id: Optional[str]. Identifier of the team associated with the task.
            tags: Optional[list[str]]. List of tag identifiers to associate with the task.
            description: Optional[str]. Description text for the task.
            assignees: Optional[list[str]]. List of user identifiers to assign to the task.
            status: Optional[str]. Status of the task (e.g., 'to do', 'in progress').
            priority: Optional[int]. Priority level of the task.
            due_date: Optional[str]. Due date for the task, typically as an ISO date string.
            due_date_time: Optional[str]. Due date and time for the task, as an ISO datetime string.
            time_estimate: Optional[int]. Estimated time to complete the task, in minutes.
            start_date: Optional[str]. Start date for the task, as an ISO date string.
            start_date_time: Optional[str]. Start date and time for the task, as an ISO datetime string.
            notify_all: Optional[bool]. If True, notifies all assignees when the task is created.
            parent: Optional[str]. Identifier of the parent task, if this task is a subtask.
            links_to: Optional[list[str]]. List of task IDs that this task links to.
            check_required_custom_fields: Optional[bool]. If True, validates that all required custom fields are set.
            custom_fields: Optional[dict]. Dictionary of custom field values for the task.
            custom_item_id: Optional[str]. Identifier for a custom item type.

        Returns:
            dict[str, Any]: The JSON response representing the created task.

        Raises:
            ValueError: Raised if 'list_id' or 'name' is None.
            requests.HTTPError: Raised if the HTTP request to create the task fails.

        Tags:
            create, task, management, api, important
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "tags": tags,
            "description": description,
            "name": name,
            "assignees": assignees,
            "status": status,
            "priority": priority,
            "due_date": due_date,
            "due_date_time": due_date_time,
            "time_estimate": time_estimate,
            "start_date": start_date,
            "start_date_time": start_date_time,
            "notify_all": notify_all,
            "parent": parent,
            "links_to": links_to,
            "check_required_custom_fields": check_required_custom_fields,
            "custom_fields": custom_fields,
            "custom_item_id": custom_item_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/list/{list_id}/task"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_get_task_details(
        self,
        task_id,
        custom_task_ids=None,
        team_id=None,
        include_subtasks=None,
        include_markdown_description=None,
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific task, with options to include subtasks, use custom task IDs, filter by team, and specify description formatting.

        Args:
            task_id: The unique identifier of the task to retrieve. Required.
            custom_task_ids: Optional; a list or string of custom task IDs to use for lookup instead of standard IDs.
            team_id: Optional; the ID of the team to filter task lookup by team context.
            include_subtasks: Optional; if True, include details of subtasks in the response.
            include_markdown_description: Optional; if True, return the task description in Markdown format.

        Returns:
            A dictionary containing the details of the requested task, including optional subtasks and formatted description if requested.

        Raises:
            ValueError: Raised if 'task_id' is not provided.
            requests.HTTPError: Raised if the HTTP request for task details fails due to a client or server error.

        Tags:
            get, task, details, status, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/task/{task_id}"
        query_params = {
            k: v
            for k, v in [
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
                ("include_subtasks", include_subtasks),
                ("include_markdown_description", include_markdown_description),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_update_task_fields(
        self,
        task_id,
        custom_task_ids=None,
        team_id=None,
        description=None,
        custom_item_id=None,
        name=None,
        status=None,
        priority=None,
        due_date=None,
        due_date_time=None,
        parent=None,
        time_estimate=None,
        start_date=None,
        start_date_time=None,
        assignees=None,
        archived=None,
    ) -> dict[str, Any]:
        """
        Updates specified fields of an existing task with provided values.

        Args:
            task_id: str. The unique identifier of the task to update. Required.
            custom_task_ids: Optional[str]. Specifies whether custom task IDs are used. Defaults to None.
            team_id: Optional[str]. The ID of the team the task belongs to. Defaults to None.
            description: Optional[str]. The updated description for the task. Defaults to None.
            custom_item_id: Optional[str]. The custom item ID to associate with the task. Defaults to None.
            name: Optional[str]. The new name for the task. Defaults to None.
            status: Optional[str]. The new status of the task. Defaults to None.
            priority: Optional[int]. The priority level of the task. Defaults to None.
            due_date: Optional[str]. The due date for the task in 'YYYY-MM-DD' format. Defaults to None.
            due_date_time: Optional[str]. The due date and time in ISO 8601 format. Defaults to None.
            parent: Optional[str]. The parent task ID if this task is a subtask. Defaults to None.
            time_estimate: Optional[int]. The estimated time to complete the task in seconds. Defaults to None.
            start_date: Optional[str]. The start date for the task in 'YYYY-MM-DD' format. Defaults to None.
            start_date_time: Optional[str]. The start date and time in ISO 8601 format. Defaults to None.
            assignees: Optional[list[str]]. A list of user IDs to assign to the task. Defaults to None.
            archived: Optional[bool]. Whether the task should be archived. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the updated task details as returned by the API.

        Raises:
            ValueError: If the 'task_id' parameter is not provided or is None.
            requests.HTTPError: If the HTTP request to update the task fails.

        Tags:
            update, task, management, api
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        request_body = {
            "description": description,
            "custom_item_id": custom_item_id,
            "name": name,
            "status": status,
            "priority": priority,
            "due_date": due_date,
            "due_date_time": due_date_time,
            "parent": parent,
            "time_estimate": time_estimate,
            "start_date": start_date,
            "start_date_time": start_date_time,
            "assignees": assignees,
            "archived": archived,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_remove_task_by_id(
        self, task_id, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Removes a specific task by its unique task ID, optionally filtering by custom task IDs and team ID.

        Args:
            task_id: str. The unique identifier of the task to remove. Required.
            custom_task_ids: Optional[List[str]]. A list of custom task IDs to further specify which tasks to remove. Defaults to None.
            team_id: Optional[str]. The team identifier to specify the context for task removal. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the JSON response from the API after task removal.

        Raises:
            ValueError: If 'task_id' is not provided.
            requests.HTTPError: If the HTTP request to remove the task fails (non-success response status).

        Tags:
            remove, task, management, api
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/task/{task_id}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_filter_team_tasks(
        self,
        team_Id,
        page=None,
        order_by=None,
        reverse=None,
        subtasks=None,
        space_ids=None,
        project_ids=None,
        list_ids=None,
        statuses=None,
        include_closed=None,
        assignees=None,
        tags=None,
        due_date_gt=None,
        due_date_lt=None,
        date_created_gt=None,
        date_created_lt=None,
        date_updated_gt=None,
        date_updated_lt=None,
        date_done_gt=None,
        date_done_lt=None,
        custom_fields=None,
        custom_task_ids=None,
        team_id=None,
        parent=None,
        include_markdown_description=None,
        custom_items=None,
    ) -> dict[str, Any]:
        """
        Retrieves a filtered list of tasks assigned to a specific team, supporting various filtering options such as assignees, statuses, lists, projects, tags, due dates, custom fields, and more.

        Args:
            team_Id: str. The unique identifier of the team for which to filter tasks. Required.
            page: Optional[int]. The page number for paginated results.
            order_by: Optional[str]. Field used to order the result set.
            reverse: Optional[bool]. Whether to reverse the sort order.
            subtasks: Optional[bool]. Whether to include subtasks in the results.
            space_ids: Optional[list[str]]. List of space IDs to filter tasks by.
            project_ids: Optional[list[str]]. List of project IDs to filter tasks by.
            list_ids: Optional[list[str]]. List of list IDs to filter tasks by.
            statuses: Optional[list[str]]. List of task statuses to filter by.
            include_closed: Optional[bool]. Whether to include closed tasks.
            assignees: Optional[list[str]]. List of assignee user IDs to filter tasks by.
            tags: Optional[list[str]]. List of tag IDs to filter tasks by.
            due_date_gt: Optional[str]. ISO formatted string; filters tasks with due date greater than this value.
            due_date_lt: Optional[str]. ISO formatted string; filters tasks with due date less than this value.
            date_created_gt: Optional[str]. ISO formatted string; filters tasks created after this date.
            date_created_lt: Optional[str]. ISO formatted string; filters tasks created before this date.
            date_updated_gt: Optional[str]. ISO formatted string; filters tasks updated after this date.
            date_updated_lt: Optional[str]. ISO formatted string; filters tasks updated before this date.
            date_done_gt: Optional[str]. ISO formatted string; filters tasks completed after this date.
            date_done_lt: Optional[str]. ISO formatted string; filters tasks completed before this date.
            custom_fields: Optional[dict]. Dictionary of custom field filters.
            custom_task_ids: Optional[bool]. Whether to use custom task IDs in the results.
            team_id: Optional[str]. Deprecated. Use 'team_Id' instead.
            parent: Optional[str]. Filter tasks by a parent task ID.
            include_markdown_description: Optional[bool]. Whether to include the markdown-formatted description in tasks.
            custom_items: Optional[bool]. Whether to include custom items in the response.

        Returns:
            dict[str, Any]: The parsed JSON response from the API containing filtered team tasks.

        Raises:
            ValueError: If the required 'team_Id' parameter is not provided.
            HTTPError: If the HTTP request fails or the API returns an unsuccessful status code.

        Tags:
            filter, tasks, list, team, management, api
        """
        if team_Id is None:
            raise ValueError("Missing required parameter 'team_Id'")
        url = f"{self.base_url}/team/{team_Id}/task"
        query_params = {
            k: v
            for k, v in [
                ("page", page),
                ("order_by", order_by),
                ("reverse", reverse),
                ("subtasks", subtasks),
                ("space_ids", space_ids),
                ("project_ids", project_ids),
                ("list_ids", list_ids),
                ("statuses", statuses),
                ("include_closed", include_closed),
                ("assignees", assignees),
                ("tags", tags),
                ("due_date_gt", due_date_gt),
                ("due_date_lt", due_date_lt),
                ("date_created_gt", date_created_gt),
                ("date_created_lt", date_created_lt),
                ("date_updated_gt", date_updated_gt),
                ("date_updated_lt", date_updated_lt),
                ("date_done_gt", date_done_gt),
                ("date_done_lt", date_done_lt),
                ("custom_fields", custom_fields),
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
                ("parent", parent),
                ("include_markdown_description", include_markdown_description),
                ("custom_items", custom_items),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_get_time_in_status(
        self, task_id, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Retrieves the amount of time a specified task has spent in each status, with optional filters for custom task IDs and team ID.

        Args:
            task_id: str. The unique identifier of the task whose time in status is to be retrieved.
            custom_task_ids: Optional[str]. Custom identifiers for filtering tasks; if provided, limits results to these IDs.
            team_id: Optional[str]. The unique identifier of the team; if provided, filters results to this team.

        Returns:
            dict[str, Any]: A dictionary containing the time spent by the specified task in each status.

        Raises:
            ValueError: If 'task_id' is not provided.
            requests.HTTPError: If the HTTP request to the server fails or returns an unsuccessful status code.

        Tags:
            get, task, status, management
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/task/{task_id}/time_in_status"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def tasks_get_time_in_status_bulk(
        self, task_ids, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Retrieves the time each specified task has spent in various statuses, in bulk, based on provided task identifiers.

        Args:
            task_ids: list or str. A list of task IDs or a comma-separated string of task IDs to query. Required.
            custom_task_ids: list or str, optional. A list or comma-separated string of custom task identifiers to filter the tasks.
            team_id: str, optional. The team ID to scope the task status retrieval.

        Returns:
            dict. A dictionary mapping each requested task ID to a breakdown of time spent in each status.

        Raises:
            ValueError: Raised if 'task_ids' is None.
            HTTPError: Raised if the HTTP request to the API fails (e.g., non-2xx response code).

        Tags:
            get, task-management, status, bulk
        """
        if task_ids is None:
            raise ValueError("Missing required parameter 'task_ids'")
        url = f"{self.base_url}/task/bulk_time_in_status/task_ids"
        query_params = {
            k: v
            for k, v in [
                ("task_ids", task_ids),
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_templates_get_templates(self, team_id, page) -> dict[str, Any]:
        """
        Retrieves a paginated list of task templates for a given team.

        Args:
            team_id: str. The unique identifier of the team for which to fetch task templates.
            page: int. The page number of task templates to retrieve.

        Returns:
            dict[str, Any]: A dictionary containing the paginated task template data for the specified team.

        Raises:
            ValueError: Raised if 'team_id' or 'page' is None.
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.

        Tags:
            get, list, task-templates, team
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if page is None:
            raise ValueError("Missing required parameter 'page'")
        url = f"{self.base_url}/team/{team_id}/taskTemplate"
        query_params = {k: v for k, v in [("page", page)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def task_templates_create_from_template(
        self, list_id, template_id, name
    ) -> dict[str, Any]:
        """
        Creates a new task template instance in a specific list by cloning from an existing task template.

        Args:
            list_id: The unique identifier of the list in which to create the new task template (str).
            template_id: The unique identifier of the task template to clone from (str).
            name: The name to assign to the newly created task template (str).

        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created task template as returned by the API.

        Raises:
            ValueError: Raised if any of the required parameters ('list_id', 'template_id', or 'name') are None.
            requests.HTTPError: Raised if the HTTP request to create the task template fails.

        Tags:
            create, task-template, list, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/list/{list_id}/taskTemplate/{template_id}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_workspaces_get_workspace_seats(self, team_id) -> dict[str, Any]:
        """
        Retrieves detailed seat allocation information for a specific workspace team.

        Args:
            team_id: The unique identifier of the team whose workspace seats are to be fetched.

        Returns:
            A dictionary containing seat allocation details for the specified team.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to fetch seat information fails.

        Tags:
            get, workspace, seats, team, api, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/seats"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_workspaces_get_workspace_plan(self, team_id) -> dict[str, Any]:
        """
        Retrieves the plan details for a workspace associated with the specified team.

        Args:
            team_id: The unique identifier of the team whose workspace plan is to be retrieved.

        Returns:
            A dictionary containing the workspace plan details for the given team.

        Raises:
            ValueError: Raised if the team_id parameter is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the plan details fails.

        Tags:
            get, workspace-plan, team-management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/plan"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_user_groups_create_team(self, team_id, name, members) -> dict[str, Any]:
        """
        Creates a new team user group with the specified name and members under the given team.

        Args:
            team_id: str. The unique identifier of the team under which the group will be created.
            name: str. The name of the new user group.
            members: list. The list of members to be added to the group.

        Returns:
            dict[str, Any]: The response data containing details of the newly created team user group.

        Raises:
            ValueError: Raised if any of the required parameters ('team_id', 'name', or 'members') are missing.
            requests.HTTPError: Raised if the HTTP request to create the group fails.

        Tags:
            create, team-user-group, management, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if members is None:
            raise ValueError("Missing required parameter 'members'")
        request_body = {
            "name": name,
            "members": members,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/group"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def custom_task_types_get_available_task_types(self, team_id) -> dict[str, Any]:
        """
        Retrieves the available custom task types for a specified team.

        Args:
            team_id: The unique identifier of the team for which to fetch available custom task types.

        Returns:
            A dictionary containing the available custom task types for the specified team.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to the server fails or returns a non-successful status code.

        Tags:
            get, custom-task-types, list, api, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/custom_item"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_user_groups_update_user_group(
        self, group_id, name=None, handle=None, members=None
    ) -> dict[str, Any]:
        """
        Updates the attributes of a user group in the Teams system.

        Args:
            group_id: The unique identifier of the user group to update.
            name: Optional; The new name for the user group.
            handle: Optional; The new handle (identifier) for the user group.
            members: Optional; A list of user identifiers to set as members of the group.

        Returns:
            A dictionary containing the updated user group details as returned by the API.

        Raises:
            ValueError: If 'group_id' is None.
            requests.HTTPError: If the HTTP request to update the group fails.

        Tags:
            update, group-management, teams, user-groups, api
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        request_body = {
            "name": name,
            "handle": handle,
            "members": members,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/group/{group_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_user_groups_remove_group(self, group_id) -> dict[str, Any]:
        """
        Removes a user group from the Teams service by group ID.

        Args:
            group_id: str. The unique identifier of the group to be removed.

        Returns:
            dict[str, Any]: The JSON response from the server after the group deletion.

        Raises:
            ValueError: If the 'group_id' parameter is None.
            requests.HTTPError: If the HTTP request to delete the group fails with an error status code.

        Tags:
            remove, group-management, teams, http-delete
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group_id'")
        url = f"{self.base_url}/group/{group_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_user_groups_get_user_groups(
        self, team_id=None, group_ids=None
    ) -> dict[str, Any]:
        """
        Retrieves user group information for a specified team and/or group IDs from the remote service.

        Args:
            team_id: Optional; the identifier of the team to filter user groups (str or None).
            group_ids: Optional; a list of group IDs to filter the results (iterable or None).

        Returns:
            A dictionary containing the JSON response with user group details from the remote service.

        Raises:
            requests.HTTPError: If the HTTP request fails or the response status indicates an error.

        Tags:
            get, user-groups, team-management, api
        """
        url = f"{self.base_url}/group"
        query_params = {
            k: v
            for k, v in [("team_id", team_id), ("group_ids", group_ids)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_legacy_get_tracked_time(
        self, task_id, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Retrieves time tracking data for a specific task.

        Args:
            task_id: The unique identifier of the task for which time tracking data is requested. Required.
            custom_task_ids: Optional flag to include custom task identifiers in the response.
            team_id: Optional team identifier to filter the time tracking data by team.

        Returns:
            A dictionary containing time tracking information for the specified task.

        Raises:
            ValueError: Raised when the required 'task_id' parameter is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).

        Tags:
            get, retrieve, time-tracking, task, legacy
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        url = f"{self.base_url}/task/{task_id}/time"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_legacy_record_time_for_task(
        self, task_id, start, end, time, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Records time for a task in the legacy system.

        Args:
            task_id: The ID of the task to record time for.
            start: The start time of the time entry.
            end: The end time of the time entry.
            time: The duration of the time entry.
            custom_task_ids: Optional list of custom task IDs.
            team_id: Optional team ID.

        Returns:
            A dictionary containing the response from the server.

        Raises:
            ValueError: Raised if any of the required parameters (task_id, start, end, time) are missing.

        Tags:
            record, time-tracking, legacy
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if start is None:
            raise ValueError("Missing required parameter 'start'")
        if end is None:
            raise ValueError("Missing required parameter 'end'")
        if time is None:
            raise ValueError("Missing required parameter 'time'")
        request_body = {
            "start": start,
            "end": end,
            "time": time,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}/time"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_legacy_edit_time_tracked(
        self, task_id, interval_id, start, end, time, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Edits a tracked time interval for a specific task using legacy time tracking, updating start, end, and time values.

        Args:
            task_id: str. Unique identifier of the task whose time interval is being edited.
            interval_id: str. Identifier of the specific time interval to edit.
            start: str. The new start time for the time interval (in ISO 8601 format or equivalent).
            end: str. The new end time for the time interval (in ISO 8601 format or equivalent).
            time: int. The updated duration for the time interval, typically in seconds.
            custom_task_ids: Optional[str]. Custom task identifier(s), if applicable. Defaults to None.
            team_id: Optional[str]. Team identifier, if relevant to the time tracking operation. Defaults to None.

        Returns:
            dict[str, Any]: The response from the server as a dictionary containing the updated interval information.

        Raises:
            ValueError: If any of the required parameters (task_id, interval_id, start, end, time) are missing.
            requests.HTTPError: If the HTTP request fails or the server responds with an error status code.

        Tags:
            edit, time-tracking, task-management, api, update
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if interval_id is None:
            raise ValueError("Missing required parameter 'interval_id'")
        if start is None:
            raise ValueError("Missing required parameter 'start'")
        if end is None:
            raise ValueError("Missing required parameter 'end'")
        if time is None:
            raise ValueError("Missing required parameter 'time'")
        request_body = {
            "start": start,
            "end": end,
            "time": time,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/task/{task_id}/time/{interval_id}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_legacy_remove_tracked_time(
        self, task_id, interval_id, custom_task_ids=None, team_id=None
    ) -> dict[str, Any]:
        """
        Removes tracked time from a time-tracking interval associated with a specific task.

        Args:
            task_id: The ID of the task from which tracked time will be removed.
            interval_id: The ID of the time interval to remove tracked time from.
            custom_task_ids: Optional list of custom task IDs for filtering.
            team_id: Optional team ID for filtering.

        Returns:
            A dictionary containing the result of removing tracked time.

        Raises:
            ValueError: Raised if either 'task_id' or 'interval_id' is missing.

        Tags:
            remove, time-tracking, task-management, async_job
        """
        if task_id is None:
            raise ValueError("Missing required parameter 'task_id'")
        if interval_id is None:
            raise ValueError("Missing required parameter 'interval_id'")
        url = f"{self.base_url}/task/{task_id}/time/{interval_id}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_get_time_entries_within_date_range(
        self,
        team_Id,
        start_date=None,
        end_date=None,
        assignee=None,
        include_task_tags=None,
        include_location_names=None,
        space_id=None,
        folder_id=None,
        list_id=None,
        task_id=None,
        custom_task_ids=None,
        team_id=None,
    ) -> dict[str, Any]:
        """
        Retrieves time entries for a specified team within an optional date range and optional filters such as assignee, tags, locations, spaces, folders, lists, or tasks.

        Args:
            team_Id: str. The unique identifier of the team whose time entries are to be retrieved. Required.
            start_date: str or None. The start date for filtering time entries (ISO 8601 format). Optional.
            end_date: str or None. The end date for filtering time entries (ISO 8601 format). Optional.
            assignee: str or None. Filter time entries by the assignee's user ID. Optional.
            include_task_tags: str or None. Include associated task tags in the results if set. Optional.
            include_location_names: str or None. Include location names in the results if set. Optional.
            space_id: str or None. Filter time entries by a specific space ID. Optional.
            folder_id: str or None. Filter time entries by a specific folder ID. Optional.
            list_id: str or None. Filter time entries by a specific list ID. Optional.
            task_id: str or None. Filter time entries by a specific task ID. Optional.
            custom_task_ids: str or None. Filter time entries using custom task IDs. Optional.
            team_id: str or None. Filter time entries by an alternative team ID (if distinct from team_Id). Optional.

        Returns:
            dict[str, Any]: A dictionary containing the queried time entry data for the specified team and filters.

        Raises:
            ValueError: Raised if the required parameter 'team_Id' is not provided.
            requests.HTTPError: Raised if the HTTP request to the API fails (e.g., due to network issues or API errors).

        Tags:
            get, list, time-tracking, management, filter, api
        """
        if team_Id is None:
            raise ValueError("Missing required parameter 'team_Id'")
        url = f"{self.base_url}/team/{team_Id}/time_entries"
        query_params = {
            k: v
            for k, v in [
                ("start_date", start_date),
                ("end_date", end_date),
                ("assignee", assignee),
                ("include_task_tags", include_task_tags),
                ("include_location_names", include_location_names),
                ("space_id", space_id),
                ("folder_id", folder_id),
                ("list_id", list_id),
                ("task_id", task_id),
                ("custom_task_ids", custom_task_ids),
                ("team_id", team_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_create_time_entry(
        self,
        team_Id,
        start,
        duration,
        custom_task_ids=None,
        team_id=None,
        tags=None,
        description=None,
        stop=None,
        end=None,
        billable=None,
        assignee=None,
        tid=None,
    ) -> dict[str, Any]:
        """
        Creates a time tracking entry for a specified team.

        Args:
            team_Id: Required. The unique identifier of the team for which the time entry is being created.
            start: Required. The start time of the time entry.
            duration: Required. The duration of the time entry.
            custom_task_ids: Optional. Custom task identifiers associated with the time entry.
            team_id: Optional. An alternative team identifier parameter (note: redundant with team_Id).
            tags: Optional. List of tags associated with the time entry.
            description: Optional. Description of the time entry.
            stop: Optional. The stop time of the time entry.
            end: Optional. The end time of the time entry.
            billable: Optional. Boolean indicating if the time entry is billable.
            assignee: Optional. The user to whom the time entry is assigned.
            tid: Optional. Task identifier associated with the time entry.

        Returns:
            Dictionary containing the created time entry data from the API response.

        Raises:
            ValueError: Raised when required parameters (team_Id, start, or duration) are missing.
            HTTPError: Raised when the API request fails.

        Tags:
            create, time-entry, tracking, api-interaction, team
        """
        if team_Id is None:
            raise ValueError("Missing required parameter 'team_Id'")
        if start is None:
            raise ValueError("Missing required parameter 'start'")
        if duration is None:
            raise ValueError("Missing required parameter 'duration'")
        request_body = {
            "tags": tags,
            "description": description,
            "start": start,
            "stop": stop,
            "end": end,
            "billable": billable,
            "duration": duration,
            "assignee": assignee,
            "tid": tid,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_Id}/time_entries"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_get_single_time_entry(
        self, team_id, timer_id, include_task_=None, include_location_names=None
    ) -> dict[str, Any]:
        """
        Retrieves a single time entry by team and timer ID.

        Args:
            team_id: The ID of the team for which to retrieve the time entry.
            timer_id: The ID of the timer for which to retrieve the time entry.
            include_task_: Optional flag to include task details in the response.
            include_location_names: Optional flag to include location names in the response.

        Returns:
            A dictionary containing the time entry details.

        Raises:
            ValueError: Raised if 'team_id' or 'timer_id' is None.

        Tags:
            time-tracking, get, async-job, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if timer_id is None:
            raise ValueError("Missing required parameter 'timer_id'")
        url = f"{self.base_url}/team/{team_id}/time_entries/{timer_id}"
        query_params = {
            k: v
            for k, v in [
                ("include_task_", include_task_),
                ("include_location_names", include_location_names),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_remove_entry(self, team_id, timer_id) -> dict[str, Any]:
        """
        Removes a specific time tracking entry for a team by deleting the corresponding timer record.

        Args:
            team_id: The unique identifier of the team from which the time entry will be removed.
            timer_id: The unique identifier of the time entry (timer) to be deleted.

        Returns:
            A dictionary containing the JSON response from the API after successful removal of the time entry.

        Raises:
            ValueError: Raised if either 'team_id' or 'timer_id' is None.
            requests.HTTPError: Raised if the API request to delete the time entry fails.

        Tags:
            remove, time-tracking, management, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if timer_id is None:
            raise ValueError("Missing required parameter 'timer_id'")
        url = f"{self.base_url}/team/{team_id}/time_entries/{timer_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_update_time_entry_details(
        self,
        team_id,
        timer_id,
        tags,
        custom_task_ids=None,
        description=None,
        tag_action=None,
        start=None,
        end=None,
        tid=None,
        billable=None,
        duration=None,
    ) -> dict[str, Any]:
        """
        Updates time entry details by sending a PUT request to the server.

        Args:
            team_id: ID of the team for which the time entry is being updated
            timer_id: ID of the time entry to update
            tags: Tags to apply to the time entry
            custom_task_ids: Optional custom task IDs associated with the time entry
            description: Optional description of the time entry
            tag_action: Optional action to perform on the tags
            start: Optional start time of the time entry
            end: Optional end time of the time entry
            tid: Optional TID associated with the time entry
            billable: Optional billability status of the time entry
            duration: Optional duration of the time entry

        Returns:
            Dictionary containing the updated time entry details

        Raises:
            ValueError: Raised when required parameters (team_id, timer_id, tags) are missing

        Tags:
            update, time-entry, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if timer_id is None:
            raise ValueError("Missing required parameter 'timer_id'")
        if tags is None:
            raise ValueError("Missing required parameter 'tags'")
        request_body = {
            "tags": tags,
            "description": description,
            "tag_action": tag_action,
            "start": start,
            "end": end,
            "tid": tid,
            "billable": billable,
            "duration": duration,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/time_entries/{timer_id}"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_get_time_entry_history(self, team_id, timer_id) -> dict[str, Any]:
        """
        Retrieves the history of a specific time entry for a given team from the time tracking service.

        Args:
            team_id: The unique identifier of the team whose time entry history is to be retrieved.
            timer_id: The unique identifier of the time entry (timer) for which the history is requested.

        Returns:
            A dictionary containing the historical records of the specified time entry.

        Raises:
            ValueError: Raised if 'team_id' or 'timer_id' is None.
            requests.HTTPError: Raised if the HTTP request to the time tracking service fails with an error status.

        Tags:
            get, time-tracking, history, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if timer_id is None:
            raise ValueError("Missing required parameter 'timer_id'")
        url = f"{self.base_url}/team/{team_id}/time_entries/{timer_id}/history"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_get_current_time_entry(
        self, team_id, assignee=None
    ) -> dict[str, Any]:
        """
        Retrieves the current time entry for a specified team, optionally filtered by assignee.

        Args:
            team_id: The unique identifier of the team to fetch the current time entry for.
            assignee: Optional; the identifier of the assignee to filter the current time entry.

        Returns:
            A dictionary containing the current time entry details for the specified team and, if provided, assignee.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to the API fails with an unsuccessful status code.

        Tags:
            get, time-tracking, current-status, api, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/time_entries/current"
        query_params = {k: v for k, v in [("assignee", assignee)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_remove_tags_from_time_entries(
        self, team_id, tags, time_entry_ids
    ) -> dict[str, Any]:
        """
        Removes specified tags from multiple time entries for a given team.

        Args:
            team_id: str. Unique identifier of the team whose time entries will be updated.
            tags: list[str]. List of tag names to remove from the specified time entries.
            time_entry_ids: list[str]. List of time entry IDs from which the tags will be removed.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the result of the tag removal operation.

        Raises:
            ValueError: Raised if 'team_id', 'tags', or 'time_entry_ids' are None.
            requests.HTTPError: Raised if the API request fails or returns an unsuccessful HTTP status.

        Tags:
            remove, tags, time-entries, management, batch
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if tags is None:
            raise ValueError("Missing required parameter 'tags'")
        if time_entry_ids is None:
            raise ValueError("Missing required parameter 'time_entry_ids'")
        request_body = {
            "tags": tags,
            "time_entry_ids": time_entry_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/time_entries/tags"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_get_all_tags_from_time_entries(self, team_id) -> dict[str, Any]:
        """
        Retrieves all tags associated with time entries for a specified team.

        Args:
            team_id: str. The unique identifier of the team whose time entry tags are to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the tags extracted from the team's time entries.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to the server fails or returns an unsuccessful status code.

        Tags:
            get, list, tags, time-tracking, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/time_entries/tags"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_add_tags_from_time_entries(
        self, team_id, tags, time_entry_ids
    ) -> dict[str, Any]:
        """
        Adds tags to specified time entries for a team.

        Args:
            team_id: The unique identifier of the team.
            tags: List of tags to be added to the time entries.
            time_entry_ids: List of time entry identifiers to which tags will be added.

        Returns:
            Dictionary containing the API response after adding tags to time entries.

        Raises:
            ValueError: Raised when any of the required parameters (team_id, tags, or time_entry_ids) is None.
            HTTPError: Raised when the API request fails.

        Tags:
            add, tags, time-entries, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if tags is None:
            raise ValueError("Missing required parameter 'tags'")
        if time_entry_ids is None:
            raise ValueError("Missing required parameter 'time_entry_ids'")
        request_body = {
            "tags": tags,
            "time_entry_ids": time_entry_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/time_entries/tags"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_change_tag_names(
        self, team_id, name, new_name, tag_bg, tag_fg
    ) -> dict[str, Any]:
        """
        Updates the name and visual properties of a time tracking tag for a specified team.

        Args:
            team_id: str. The unique identifier of the team whose tag is to be updated.
            name: str. The current name of the tag to be changed.
            new_name: str. The new name to assign to the tag.
            tag_bg: str. The new background color for the tag, typically in hexadecimal format.
            tag_fg: str. The new foreground (text) color for the tag, typically in hexadecimal format.

        Returns:
            dict. The server response containing the updated tag details.

        Raises:
            ValueError: If any required parameter ('team_id', 'name', 'new_name', 'tag_bg', or 'tag_fg') is None.
            requests.HTTPError: If the HTTP request to update the tag fails.

        Tags:
            update, tag-management, time-tracking, team, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if new_name is None:
            raise ValueError("Missing required parameter 'new_name'")
        if tag_bg is None:
            raise ValueError("Missing required parameter 'tag_bg'")
        if tag_fg is None:
            raise ValueError("Missing required parameter 'tag_fg'")
        request_body = {
            "name": name,
            "new_name": new_name,
            "tag_bg": tag_bg,
            "tag_fg": tag_fg,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/time_entries/tags"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_start_timer(
        self,
        team_Id,
        custom_task_ids=None,
        team_id=None,
        tags=None,
        description=None,
        tid=None,
        billable=None,
    ) -> dict[str, Any]:
        """
        Starts a new time tracking timer for a specified team and task with optional metadata such as tags, description, and billable status.

        Args:
            team_Id: str. The unique identifier of the team for which to start the timer. This parameter is required.
            custom_task_ids: Optional[list[str]]. A list of custom task IDs to associate with the timer entry.
            team_id: Optional[str]. An additional team identifier used as a query parameter, if different from 'team_Id'.
            tags: Optional[list[str]]. A list of tags to attach to the time entry for categorization or filtering.
            description: Optional[str]. A text description for the time entry providing further details.
            tid: Optional[str]. The task identifier to be tracked.
            billable: Optional[bool]. Indicates whether the time entry should be marked as billable.

        Returns:
            dict[str, Any]: A dictionary containing the response data of the newly started time entry from the API.

        Raises:
            ValueError: Raised if the required parameter 'team_Id' is not provided.
            requests.HTTPError: Raised if the API request fails or returns a non-success status code.

        Tags:
            start, timer, time-tracking, async-job, team-management
        """
        if team_Id is None:
            raise ValueError("Missing required parameter 'team_Id'")
        request_body = {
            "tags": tags,
            "description": description,
            "tid": tid,
            "billable": billable,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_Id}/time_entries/start"
        query_params = {
            k: v
            for k, v in [("custom_task_ids", custom_task_ids), ("team_id", team_id)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def time_tracking_stop_time_entry(self, team_id) -> dict[str, Any]:
        """
        Stops the currently active time entry for the specified team.

        Args:
            team_id: The unique identifier of the team whose active time entry should be stopped.

        Returns:
            A dictionary containing the response data from the stop time entry request.

        Raises:
            ValueError: Raised if 'team_id' is None.
            requests.HTTPError: Raised if the HTTP request to stop the time entry fails.

        Tags:
            time-tracking, stop, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/time_entries/stop"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def users_invite_user_to_workspace(
        self, team_id, email, admin, custom_role_id=None
    ) -> dict[str, Any]:
        """
        Invites a user to a workspace by sending an invitation to their email address.

        Args:
            team_id: The unique identifier of the workspace/team to invite the user to.
            email: The email address of the user being invited to the workspace.
            admin: Boolean flag indicating whether the user should have admin privileges.
            custom_role_id: Optional. The ID of a custom role to assign to the invited user.

        Returns:
            A dictionary containing the API response with details of the created invitation.

        Raises:
            ValueError: Raised when any of the required parameters (team_id, email, admin) are None.
            HTTPError: Raised when the API request fails or returns an error status code.

        Tags:
            invite, user, workspace, team, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        if admin is None:
            raise ValueError("Missing required parameter 'admin'")
        request_body = {
            "email": email,
            "admin": admin,
            "custom_role_id": custom_role_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/user"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def users_get_user_details(self, team_id, user_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific user within a given team.

        Args:
            team_id: The unique identifier of the team to which the user belongs. Must not be None.
            user_id: The unique identifier of the user whose details are to be retrieved. Must not be None.

        Returns:
            A dictionary containing the user's details as returned by the API.

        Raises:
            ValueError: Raised if either 'team_id' or 'user_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails with a response error status.

        Tags:
            get, user-details, api, management, important
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/team/{team_id}/user/{user_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def users_update_user_details(
        self, team_id, user_id, username, admin, custom_role_id
    ) -> dict[str, Any]:
        """
        Updates the details of a user in a specified team.

        Args:
            team_id: str. The unique identifier of the team containing the user to update.
            user_id: str. The unique identifier of the user whose details will be updated.
            username: str. The new username to assign to the user.
            admin: bool. Whether the user should have admin privileges.
            custom_role_id: str. The identifier of a custom role to assign to the user.

        Returns:
            dict[str, Any]: A dictionary containing the updated user details as returned by the server.

        Raises:
            ValueError: If any of the required parameters ('team_id', 'user_id', 'username', 'admin', or 'custom_role_id') are None.
            requests.HTTPError: If the HTTP request to update the user fails.

        Tags:
            update, user-management, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        if admin is None:
            raise ValueError("Missing required parameter 'admin'")
        if custom_role_id is None:
            raise ValueError("Missing required parameter 'custom_role_id'")
        request_body = {
            "username": username,
            "admin": admin,
            "custom_role_id": custom_role_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/user/{user_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def users_deactivate_from_workspace(self, team_id, user_id) -> dict[str, Any]:
        """
        Deactivates a user from the specified workspace (team) by sending a DELETE request to the API.

        Args:
            team_id: The unique identifier of the team (workspace) from which the user will be deactivated.
            user_id: The unique identifier of the user to deactivate from the workspace.

        Returns:
            A dictionary containing the response data from the API after the user has been deactivated.

        Raises:
            ValueError: Raised if either 'team_id' or 'user_id' is None.
            HTTPError: Raised if the API request fails (non-2xx status code).

        Tags:
            deactivate, user-management, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/team/{team_id}/user/{user_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_get_everything_level(self, team_id) -> dict[str, Any]:
        """
        Retrieves all view-level data for a specified team.

        Args:
            team_id: The unique identifier of the team for which to fetch all view data.

        Returns:
            A dictionary containing all data at the 'view' level for the specified team.

        Raises:
            ValueError: If 'team_id' is None.
            requests.HTTPError: If the HTTP request to fetch the data fails.

        Tags:
            get, views, team, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/view"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_create_workspace_view_everything_level(
        self,
        team_id,
        name,
        type,
        grouping,
        divide,
        sorting,
        filters,
        columns,
        team_sidebar,
        settings,
    ) -> dict[str, Any]:
        """
        Creates a new 'everything-level' view within a specified workspace team with custom configuration options.

        Args:
            team_id: str. Unique identifier of the team where the view will be created.
            name: str. Name of the new workspace view.
            type: str. Type of the view to create.
            grouping: Any. Defines how items in the view are grouped.
            divide: Any. Specifies division or partitioning within the view.
            sorting: Any. Sorting rules for items in the view.
            filters: Any. Filters to apply to items in the view.
            columns: Any. Specifies which columns will be included in the view.
            team_sidebar: Any. Configuration for the team sidebar appearance or content.
            settings: Any. Additional settings for the workspace view.

        Returns:
            dict[str, Any]: A dictionary representing the API response containing details of the newly created workspace view.

        Raises:
            ValueError: Raised if any required parameter is None.
            requests.HTTPError: Raised if the HTTP request to the backend fails (e.g., non-2xx response code).

        Tags:
            create, workspace-view, management, api
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if grouping is None:
            raise ValueError("Missing required parameter 'grouping'")
        if divide is None:
            raise ValueError("Missing required parameter 'divide'")
        if sorting is None:
            raise ValueError("Missing required parameter 'sorting'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if columns is None:
            raise ValueError("Missing required parameter 'columns'")
        if team_sidebar is None:
            raise ValueError("Missing required parameter 'team_sidebar'")
        if settings is None:
            raise ValueError("Missing required parameter 'settings'")
        request_body = {
            "name": name,
            "type": type,
            "grouping": grouping,
            "divide": divide,
            "sorting": sorting,
            "filters": filters,
            "columns": columns,
            "team_sidebar": team_sidebar,
            "settings": settings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/view"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_space_views_get(self, space_id) -> dict[str, Any]:
        """
        Retrieves the view details for a specified space by its ID.

        Args:
            space_id: str. The unique identifier of the space whose view information is to be fetched.

        Returns:
            dict[str, Any]: A dictionary containing the space view information returned by the API.

        Raises:
            ValueError: If 'space_id' is None.
            requests.HTTPError: If the HTTP request to the API endpoint fails or returns an unsuccessful status code.

        Tags:
            get, view, space, management, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        url = f"{self.base_url}/space/{space_id}/view"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_add_view_to_space(
        self,
        space_id,
        name,
        type,
        grouping,
        divide,
        sorting,
        filters,
        columns,
        team_sidebar,
        settings,
    ) -> dict[str, Any]:
        """
        Creates a new view in the specified space with the given configuration parameters.

        Args:
            space_id: str. The unique identifier of the space where the view will be added.
            name: str. The name of the new view.
            type: str. The type of the view to be created.
            grouping: Any. Grouping configuration for the view (structure depends on implementation).
            divide: Any. Division configuration for the view (structure depends on implementation).
            sorting: Any. Sorting configuration for the view (structure depends on implementation).
            filters: Any. Filter criteria for the view (structure depends on implementation).
            columns: Any. Column configuration for the view (structure depends on implementation).
            team_sidebar: Any. Team sidebar configuration for the view (structure depends on implementation).
            settings: Any. Additional settings for the view (structure depends on implementation).

        Returns:
            dict[str, Any]: The JSON response from the server containing details of the newly created view.

        Raises:
            ValueError: If any required parameter is missing (i.e., any of the arguments is None).
            requests.HTTPError: If the HTTP request to create the view fails (non-2xx response).

        Tags:
            add, view, space, management, api
        """
        if space_id is None:
            raise ValueError("Missing required parameter 'space_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if grouping is None:
            raise ValueError("Missing required parameter 'grouping'")
        if divide is None:
            raise ValueError("Missing required parameter 'divide'")
        if sorting is None:
            raise ValueError("Missing required parameter 'sorting'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if columns is None:
            raise ValueError("Missing required parameter 'columns'")
        if team_sidebar is None:
            raise ValueError("Missing required parameter 'team_sidebar'")
        if settings is None:
            raise ValueError("Missing required parameter 'settings'")
        request_body = {
            "name": name,
            "type": type,
            "grouping": grouping,
            "divide": divide,
            "sorting": sorting,
            "filters": filters,
            "columns": columns,
            "team_sidebar": team_sidebar,
            "settings": settings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/space/{space_id}/view"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_folder_views_get(self, folder_id) -> dict[str, Any]:
        """
        Retrieves the views associated with a specified folder by its folder ID.

        Args:
            folder_id: The unique identifier of the folder to retrieve views for.

        Returns:
            A dictionary containing the JSON response with the folder's views data.

        Raises:
            ValueError: Raised if the required parameter 'folder_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the folder views fails.

        Tags:
            get, views, folder, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/folder/{folder_id}/view"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_add_view_to_folder(
        self,
        folder_id,
        name,
        type,
        grouping,
        divide,
        sorting,
        filters,
        columns,
        team_sidebar,
        settings,
    ) -> dict[str, Any]:
        """
        Adds a new view to a specified folder with the provided configuration details.

        Args:
            folder_id: The unique identifier of the folder to which the view will be added.
            name: The name of the view to create.
            type: The type of the view (e.g., list, board, etc.).
            grouping: Configuration for how items are grouped in the view.
            divide: Configuration for dividing items within the view.
            sorting: Sorting specifications for items in the view.
            filters: Filters to apply to items in the view.
            columns: Column definitions to display in the view.
            team_sidebar: Sidebar configuration for team access and visibility.
            settings: Additional view settings and preferences.

        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created view as returned by the API.

        Raises:
            ValueError: Raised if any required parameter is missing (i.e., has the value None).
            requests.HTTPError: Raised if the HTTP request to the API fails.

        Tags:
            add, view, management, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if grouping is None:
            raise ValueError("Missing required parameter 'grouping'")
        if divide is None:
            raise ValueError("Missing required parameter 'divide'")
        if sorting is None:
            raise ValueError("Missing required parameter 'sorting'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if columns is None:
            raise ValueError("Missing required parameter 'columns'")
        if team_sidebar is None:
            raise ValueError("Missing required parameter 'team_sidebar'")
        if settings is None:
            raise ValueError("Missing required parameter 'settings'")
        request_body = {
            "name": name,
            "type": type,
            "grouping": grouping,
            "divide": divide,
            "sorting": sorting,
            "filters": filters,
            "columns": columns,
            "team_sidebar": team_sidebar,
            "settings": settings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/folder/{folder_id}/view"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_get_list_views(self, list_id) -> dict[str, Any]:
        """
        Retrieves all views associated with the specified list.

        Args:
            list_id: The unique identifier of the list whose views are to be fetched.

        Returns:
            A dictionary containing data for all views related to the given list.

        Raises:
            ValueError: Raised when 'list_id' is None.
            requests.HTTPError: Raised if the HTTP request to fetch views fails.

        Tags:
            list, views, fetch, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/list/{list_id}/view"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_add_view_to_list(
        self,
        list_id,
        name,
        type,
        grouping,
        divide,
        sorting,
        filters,
        columns,
        team_sidebar,
        settings,
    ) -> dict[str, Any]:
        """
        Creates a new view for a specified list with the provided configuration and returns the resulting view data.

        Args:
            list_id: The unique identifier of the list to which the new view will be added.
            name: The name of the new view.
            type: The type/category of the view to be created.
            grouping: Grouping settings for organizing items in the view.
            divide: Division options determining how content is split in the view.
            sorting: Sorting configuration for ordering items in the view.
            filters: Filters to be applied for displaying relevant items in the view.
            columns: Columns to be displayed in the view.
            team_sidebar: Configuration determining if or how the view appears in the team sidebar.
            settings: Additional settings and options for the new view.

        Returns:
            A dictionary containing the details of the newly created view as returned by the API.

        Raises:
            ValueError: Raised if any required parameter is missing (i.e., if one of the parameters is None).
            requests.HTTPError: Raised if the HTTP request to create the view fails (e.g., due to a network error or invalid response).

        Tags:
            add, view, list, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if grouping is None:
            raise ValueError("Missing required parameter 'grouping'")
        if divide is None:
            raise ValueError("Missing required parameter 'divide'")
        if sorting is None:
            raise ValueError("Missing required parameter 'sorting'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if columns is None:
            raise ValueError("Missing required parameter 'columns'")
        if team_sidebar is None:
            raise ValueError("Missing required parameter 'team_sidebar'")
        if settings is None:
            raise ValueError("Missing required parameter 'settings'")
        request_body = {
            "name": name,
            "type": type,
            "grouping": grouping,
            "divide": divide,
            "sorting": sorting,
            "filters": filters,
            "columns": columns,
            "team_sidebar": team_sidebar,
            "settings": settings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/list/{list_id}/view"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_get_view_info(self, view_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific view by its identifier.

        Args:
            view_id: str. The unique identifier of the view to retrieve information for.

        Returns:
            dict[str, Any]: A dictionary containing the view's information as returned by the API.

        Raises:
            ValueError: Raised if 'view_id' is None.
            requests.HTTPError: Raised if the HTTP request to fetch the view information fails with a non-success status code.

        Tags:
            get, view-info, api
        """
        if view_id is None:
            raise ValueError("Missing required parameter 'view_id'")
        url = f"{self.base_url}/view/{view_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_update_view_details(
        self,
        view_id,
        name,
        type,
        parent,
        grouping,
        divide,
        sorting,
        filters,
        columns,
        team_sidebar,
        settings,
    ) -> dict[str, Any]:
        """
        Updates the details of an existing view with the specified parameters.

        Args:
            view_id: str. The unique identifier of the view to update.
            name: str. The new name for the view.
            type: str. The type of the view.
            parent: str. The parent identifier or reference for the view.
            grouping: Any. The grouping configuration for the view.
            divide: Any. The divide configuration for the view.
            sorting: Any. The sorting configuration for the view.
            filters: Any. The filter settings applied to the view.
            columns: Any. The column configurations for the view.
            team_sidebar: Any. The sidebar settings for team visibility in the view.
            settings: Any. Additional settings or metadata for the view.

        Returns:
            dict[str, Any]: The updated view details as returned by the API.

        Raises:
            ValueError: If any required parameter is None.
            HTTPError: If the API request fails and returns a non-success status code.

        Tags:
            update, view-management, api
        """
        if view_id is None:
            raise ValueError("Missing required parameter 'view_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if parent is None:
            raise ValueError("Missing required parameter 'parent'")
        if grouping is None:
            raise ValueError("Missing required parameter 'grouping'")
        if divide is None:
            raise ValueError("Missing required parameter 'divide'")
        if sorting is None:
            raise ValueError("Missing required parameter 'sorting'")
        if filters is None:
            raise ValueError("Missing required parameter 'filters'")
        if columns is None:
            raise ValueError("Missing required parameter 'columns'")
        if team_sidebar is None:
            raise ValueError("Missing required parameter 'team_sidebar'")
        if settings is None:
            raise ValueError("Missing required parameter 'settings'")
        request_body = {
            "name": name,
            "type": type,
            "parent": parent,
            "grouping": grouping,
            "divide": divide,
            "sorting": sorting,
            "filters": filters,
            "columns": columns,
            "team_sidebar": team_sidebar,
            "settings": settings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/view/{view_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_delete_view_by_id(self, view_id) -> dict[str, Any]:
        """
        Deletes a view by its ID.

        Args:
            view_id: The unique identifier of the view to be deleted.

        Returns:
            A dictionary containing the API response data from the deletion operation.

        Raises:
            ValueError: Raised when the required parameter 'view_id' is None.
            HTTPError: Raised when the API request fails or returns an error status code.

        Tags:
            delete, view, management
        """
        if view_id is None:
            raise ValueError("Missing required parameter 'view_id'")
        url = f"{self.base_url}/view/{view_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def views_get_tasks_in_view(self, view_id, page) -> dict[str, Any]:
        """
        Retrieves a paginated list of tasks associated with a specific view.

        Args:
            view_id: The unique identifier of the view to retrieve tasks for. Must not be None.
            page: The page number of tasks to retrieve. Must not be None.

        Ret
            A dictionary containing the JSON response with the tasks for the specified view and page.

        Raises:
            ValueError: Raised if either 'view_id' or 'page' is None.
            HTTPError: Raised if the HTTP request to retrieve tasks fails.

        Tags:
            get, list, tasks, view, pagination
        """
        if view_id is None:
            raise ValueError("Missing required parameter 'view_id'")
        if page is None:
            raise ValueError("Missing required parameter 'page'")
        url = f"{self.base_url}/view/{view_id}/task"
        query_params = {k: v for k, v in [("page", page)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_workspace_get(self, team_id) -> dict[str, Any]:
        """
        Retrieves webhook configurations for a specified workspace team.

        Args:
            team_id: str. The unique identifier of the workspace team whose webhooks are to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the webhook configuration data associated with the given team.

        Raises:
            ValueError: Raised if 'team_id' is None.
            requests.HTTPError: Raised if the HTTP request to the server fails or an error response is received.

        Tags:
            get, webhooks, workspace, management
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        url = f"{self.base_url}/team/{team_id}/webhook"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_create_webhook(
        self,
        team_id,
        endpoint,
        events,
        space_id=None,
        folder_id=None,
        list_id=None,
        task_id=None,
    ) -> dict[str, Any]:
        """
        Creates a webhook for a team by sending a POST request to the specified endpoint.

        Args:
            team_id: The ID of the team for which the webhook is being created.
            endpoint: The URL where events will be posted.
            events: The events that will be sent to the webhook endpoint.
            space_id: Optional space ID to which the webhook is associated.
            folder_id: Optional folder ID to which the webhook is associated.
            list_id: Optional list ID to which the webhook is associated.
            task_id: Optional task ID to which the webhook is associated.

        Returns:
            A dictionary containing the created webhook details.

        Raises:
            ValueError: Raised when required parameters 'team_id', 'endpoint', or 'events' are missing.

        Tags:
            webhook, create, api-call
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        if endpoint is None:
            raise ValueError("Missing required parameter 'endpoint'")
        if events is None:
            raise ValueError("Missing required parameter 'events'")
        request_body = {
            "endpoint": endpoint,
            "events": events,
            "space_id": space_id,
            "folder_id": folder_id,
            "list_id": list_id,
            "task_id": task_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/team/{team_id}/webhook"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_update_events_to_monitor(
        self, webhook_id, endpoint, events, status
    ) -> dict[str, Any]:
        """
        Updates the monitored events, endpoint, and status for a specified webhook.

        Args:
            webhook_id: str. Unique identifier of the webhook to update.
            endpoint: str. The URL endpoint where webhook notifications will be sent.
            events: list or str. Events to monitor for this webhook.
            status: str. The desired status for the webhook (e.g., 'active', 'inactive').

        Returns:
            dict. Parsed JSON response from the server after updating the webhook.

        Raises:
            ValueError: Raised if any of 'webhook_id', 'endpoint', 'events', or 'status' is None.
            requests.HTTPError: Raised if the HTTP request to update the webhook fails (non-2xx status code).

        Tags:
            update, webhook, management
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        if endpoint is None:
            raise ValueError("Missing required parameter 'endpoint'")
        if events is None:
            raise ValueError("Missing required parameter 'events'")
        if status is None:
            raise ValueError("Missing required parameter 'status'")
        request_body = {
            "endpoint": endpoint,
            "events": events,
            "status": status,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/webhook/{webhook_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_remove_webhook_by_id(self, webhook_id) -> dict[str, Any]:
        """
        Removes a webhook by ID.

        Args:
            webhook_id: The unique identifier of the webhook to be removed.

        Returns:
            A dictionary containing the API response after webhook deletion.

        Raises:
            ValueError: If webhook_id is None or not provided.
            HTTPError: If the API request fails or returns an error status code.

        Tags:
            remove, delete, webhook, management
        """
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/webhook/{webhook_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.authorization_get_access_token,
            self.authorization_view_account_details,
            self.authorization_get_workspace_list,
            self.task_checklists_create_new_checklist,
            self.task_checklists_update_checklist,
            self.task_checklists_remove_checklist,
            self.task_checklists_add_line_item,
            self.task_checklists_update_checklist_item,
            self.task_checklists_remove_checklist_item,
            self.comments_get_task_comments,
            self.comments_create_new_task_comment,
            self.comments_get_view_comments,
            self.comments_create_chat_view_comment,
            self.comments_get_list_comments,
            self.comments_add_to_list_comment,
            self.comments_update_task_comment,
            self.comments_delete_task_comment,
            self.custom_fields_get_list_fields,
            self.custom_fields_remove_field_value,
            self.task_relationships_add_dependency,
            self.task_relationships_remove_dependency,
            self.task_relationships_link_tasks,
            self.task_relationships_remove_link_between_tasks,
            self.folders_get_contents_of,
            self.folders_create_new_folder,
            self.folders_get_folder_content,
            self.folders_rename_folder,
            self.folders_remove_folder,
            self.goals_get_workspace_goals,
            self.goals_add_new_goal_to_workspace,
            self.goals_get_details,
            self.goals_update_goal_details,
            self.goals_remove_goal,
            self.goals_add_key_result,
            self.goals_update_key_result,
            self.goals_remove_target,
            self.guests_invite_to_workspace,
            self.guests_get_guest_information,
            self.guests_edit_guest_on_workspace,
            self.guests_revoke_guest_access_to_workspace,
            self.guests_add_to_task,
            self.guests_revoke_access_to_task,
            self.guests_share_list_with,
            self.guests_remove_from_list,
            self.guests_add_guest_to_folder,
            self.guests_revoke_access_from_folder,
            self.lists_get_folder_lists,
            self.lists_add_to_folder,
            self.lists_get_folderless,
            self.lists_create_folderless_list,
            self.lists_get_list_details,
            self.lists_update_list_info_due_date_priority_assignee_color,
            self.lists_remove_list,
            self.lists_add_task_to_list,
            self.lists_remove_task_from_list,
            self.members_get_task_access,
            self.members_get_list_users,
            self.roles_list_available_custom_roles,
            self.shared_hierarchy_view_tasks_lists_folders,
            self.spaces_get_space_details,
            self.spaces_add_new_space_to_workspace,
            self.spaces_get_details,
            self.spaces_update_details_and_enable_click_apps,
            self.spaces_remove_space,
            self.tags_get_space,
            self.tags_create_space_tag,
            self.tags_update_space_tag,
            self.tags_remove_space_tag,
            self.tags_add_to_task,
            self.tags_remove_from_task,
            self.tasks_get_list_tasks,
            self.tasks_create_new_task,
            self.tasks_get_task_details,
            self.tasks_update_task_fields,
            self.tasks_remove_task_by_id,
            self.tasks_filter_team_tasks,
            self.tasks_get_time_in_status,
            self.tasks_get_time_in_status_bulk,
            self.task_templates_get_templates,
            self.task_templates_create_from_template,
            self.teams_workspaces_get_workspace_seats,
            self.teams_workspaces_get_workspace_plan,
            self.teams_user_groups_create_team,
            self.custom_task_types_get_available_task_types,
            self.teams_user_groups_update_user_group,
            self.teams_user_groups_remove_group,
            self.teams_user_groups_get_user_groups,
            self.time_tracking_legacy_get_tracked_time,
            self.time_tracking_legacy_record_time_for_task,
            self.time_tracking_legacy_edit_time_tracked,
            self.time_tracking_legacy_remove_tracked_time,
            self.time_tracking_get_time_entries_within_date_range,
            self.time_tracking_create_time_entry,
            self.time_tracking_get_single_time_entry,
            self.time_tracking_remove_entry,
            self.time_tracking_update_time_entry_details,
            self.time_tracking_get_time_entry_history,
            self.time_tracking_get_current_time_entry,
            self.time_tracking_remove_tags_from_time_entries,
            self.time_tracking_get_all_tags_from_time_entries,
            self.time_tracking_add_tags_from_time_entries,
            self.time_tracking_change_tag_names,
            self.time_tracking_start_timer,
            self.time_tracking_stop_time_entry,
            self.users_invite_user_to_workspace,
            self.users_get_user_details,
            self.users_update_user_details,
            self.users_deactivate_from_workspace,
            self.views_get_everything_level,
            self.views_create_workspace_view_everything_level,
            self.views_space_views_get,
            self.views_add_view_to_space,
            self.views_folder_views_get,
            self.views_add_view_to_folder,
            self.views_get_list_views,
            self.views_add_view_to_list,
            self.views_get_view_info,
            self.views_update_view_details,
            self.views_delete_view_by_id,
            self.views_get_tasks_in_view,
            self.webhooks_workspace_get,
            self.webhooks_create_webhook,
            self.webhooks_update_events_to_monitor,
            self.webhooks_remove_webhook_by_id,
        ]
