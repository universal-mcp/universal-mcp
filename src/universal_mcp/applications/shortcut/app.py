from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class ShortcutApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='shortcut', integration=integration, **kwargs)
        self.base_url = "https://api.app.shortcut.com"

    def  _get_headers(self) -> dict[str, Any]:
        api_key = self.integration.get_credentials().get("api_key")
        return {
            "Shortcut-Token": f"{api_key}",
            "Content-Type": "application/json",
        }

    def list_categories(self, ) -> list[Any]:
        """
        Retrieves a list of categories from the API.
        
        Returns:
            A list of category objects retrieved from the API endpoint.
        
        Raises:
            HTTPError: If the HTTP request returns a non-successful status code.
        
        Tags:
            list, categories, api, get, important   
        """
        url = f"{self.base_url}/api/v3/categories"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_category(self, name, color=None, external_id=None, type=None) -> dict[str, Any]:
        """
        Creates a new category with the specified parameters.
        
        Args:
            name: Required string representing the name of the category.
            color: Optional string representing the color of the category.
            external_id: Optional identifier for external reference.
            type: Optional string indicating the category type.
        
        Returns:
            Dictionary containing the created category details as returned by the API.
        
        Raises:
            ValueError: Raised when the required parameter 'name' is None.
            HTTPError: Raised when the HTTP request fails.
        
        Tags:
            create, category, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'name': name,
            'color': color,
            'external_id': external_id,
            'type': type,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/categories"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_category(self, category_public_id) -> dict[str, Any]:
        """
        Fetches a category by its public ID.
        
        Args:
            category_public_id: The public ID of the category to fetch.
        
        Returns:
            A dictionary containing category details.
        
        Raises:
            ValueError: Raised when the required 'category_public_id' is missing.
        
        Tags:
            fetch, category, request, 
        """
        if category_public_id is None:
            raise ValueError("Missing required parameter 'category-public-id'")
        url = f"{self.base_url}/api/v3/categories/{category_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_category(self, category_public_id, name=None, color=None, archived=None) -> dict[str, Any]:
        """
        Updates a category with the specified attributes.
        
        Args:
            category_public_id: The unique public identifier of the category to update.
            name: Optional; The new name for the category.
            color: Optional; The new color for the category.
            archived: Optional; Boolean indicating whether the category should be archived.
        
        Returns:
            A dictionary containing the updated category information.
        
        Raises:
            ValueError: When category_public_id is None.
            HTTPError: When the API request fails.
        
        Tags:
            update, category, management, 
        """
        if category_public_id is None:
            raise ValueError("Missing required parameter 'category-public-id'")
        request_body = {
            'name': name,
            'color': color,
            'archived': archived,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/categories/{category_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_category(self, category_public_id) -> Any:
        """
        Deletes a category by its public ID.
        
        Args:
            category_public_id: The public ID of the category to be deleted.
        
        Returns:
            JSON response from the server after deletion.
        
        Raises:
            ValueError: Raised if the 'category_public_id' is None.
            requests.HTTPError: Raised if the HTTP request fails (e.g., server errors).
        
        Tags:
            delete, category-management, 
        """
        if category_public_id is None:
            raise ValueError("Missing required parameter 'category-public-id'")
        url = f"{self.base_url}/api/v3/categories/{category_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_category_milestones(self, category_public_id) -> list[Any]:
        """
        Lists all milestones associated with a specified category.
        
        Args:
            category_public_id: The unique public identifier of the category for which to retrieve milestones.
        
        Returns:
            A list of dictionaries containing milestone data for the specified category.
        
        Raises:
            ValueError: When the required parameter 'category_public_id' is None.
            HTTPError: When the API request fails.
        
        Tags:
            list, milestones, category, api, retrieve, 
        """
        if category_public_id is None:
            raise ValueError("Missing required parameter 'category-public-id'")
        url = f"{self.base_url}/api/v3/categories/{category_public_id}/milestones"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_category_objectives(self, category_public_id) -> list[Any]:
        """
        Fetches and lists objectives for a given category based on its public ID.
        
        Args:
            category_public_id: The public ID of the category for which to retrieve objectives.
        
        Returns:
            A list of objectives for the specified category.
        
        Raises:
            ValueError: Raised if the 'category_public_id' is missing.
        
        Tags:
            list, objectives, category-management, 
        """
        if category_public_id is None:
            raise ValueError("Missing required parameter 'category-public-id'")
        url = f"{self.base_url}/api/v3/categories/{category_public_id}/objectives"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_custom_fields(self, ) -> list[Any]:
        """
        Retrieves a list of custom fields from the API.
        
        Returns:
            A list of dictionaries containing custom field information.
        
        Raises:
            HTTPError: If the API request fails or returns a non-success status code.
        
        Tags:
            list, custom-fields, api, 
        """
        url = f"{self.base_url}/api/v3/custom-fields"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_custom_field(self, custom_field_public_id) -> dict[str, Any]:
        """
        Retrieves a custom field by its public ID.
        
        Args:
            custom_field_public_id: The public ID of the custom field to retrieve.
        
        Returns:
            A dictionary containing the custom field data.
        
        Raises:
            ValueError: When the required custom_field_public_id parameter is None.
            HTTPError: When the API request fails or returns a non-success status code.
        
        Tags:
            get, retrieve, api, custom-field, 
        """
        if custom_field_public_id is None:
            raise ValueError("Missing required parameter 'custom-field-public-id'")
        url = f"{self.base_url}/api/v3/custom-fields/{custom_field_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_custom_field(self, custom_field_public_id, enabled=None, name=None, values=None, icon_set_identifier=None, description=None, before_id=None, after_id=None) -> dict[str, Any]:
        """
        Updates an existing custom field's attributes with the provided values.
        
        Args:
            custom_field_public_id: The public identifier of the custom field to update.
            enabled: Optional; whether the custom field should be enabled.
            name: Optional; the new name for the custom field.
            values: Optional; a list of new values for the custom field, if applicable.
            icon_set_identifier: Optional; the identifier for the icon set to associate with the custom field.
            description: Optional; a new description for the custom field.
            before_id: Optional; if specified, places the field before this custom field ID in display order.
            after_id: Optional; if specified, places the field after this custom field ID in display order.
        
        Returns:
            A dictionary containing the updated custom field information as returned by the API.
        
        Raises:
            ValueError: If 'custom_field_public_id' is None.
            requests.HTTPError: If the HTTP request fails, e.g., due to network issues or invalid parameters.
        
        Tags:
            update, custom-field, management, api, 
        """
        if custom_field_public_id is None:
            raise ValueError("Missing required parameter 'custom-field-public-id'")
        request_body = {
            'enabled': enabled,
            'name': name,
            'values': values,
            'icon_set_identifier': icon_set_identifier,
            'description': description,
            'before_id': before_id,
            'after_id': after_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/custom-fields/{custom_field_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_custom_field(self, custom_field_public_id) -> Any:
        """
        Deletes a custom field specified by its public identifier.
        
        Args:
            custom_field_public_id: The public identifier of the custom field to delete.
        
        Returns:
            A dictionary representing the JSON response from the API after deleting the custom field.
        
        Raises:
            ValueError: If 'custom_field_public_id' is None.
            requests.HTTPError: If the HTTP request to delete the custom field fails.
        
        Tags:
            delete, custom-field, management, api, 
        """
        if custom_field_public_id is None:
            raise ValueError("Missing required parameter 'custom-field-public-id'")
        url = f"{self.base_url}/api/v3/custom-fields/{custom_field_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_entity_templates(self, ) -> list[Any]:
        """
        Retrieves a list of entity templates from an API endpoint.
        
        Args:
            None: This function takes no arguments.
        
        Returns:
            A list of JSON objects representing entity templates.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            list, entity-templates, api-call, management, 
        """
        url = f"{self.base_url}/api/v3/entity-templates"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_entity_template(self, name, story_contents, author_id=None) -> dict[str, Any]:
        """
        Creates an entity template with the provided name, story contents, and optional author ID.
        
        Args:
            name: Required string representing the name of the entity template.
            story_contents: Required object containing the story contents for the entity template.
            author_id: Optional string identifying the author of the entity template.
        
        Returns:
            A dictionary containing the created entity template data from the API response.
        
        Raises:
            ValueError: Raised when the required parameters 'name' or 'story_contents' are None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            create, template, entity, api, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if story_contents is None:
            raise ValueError("Missing required parameter 'story_contents'")
        request_body = {
            'name': name,
            'author_id': author_id,
            'story_contents': story_contents,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/entity-templates"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def disable_story_templates(self, ) -> Any:
        """
        Disables story entity templates by sending a PUT request to the API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            The parsed JSON response from the API indicating the result of the disable operation.
        
        Raises:
            HTTPError: If the HTTP request to disable the story templates fails or returns an error status.
        
        Tags:
            disable, story-templates, api, management, 
        """
        url = f"{self.base_url}/api/v3/entity-templates/disable"
        query_params = {}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def enable_story_templates(self, ) -> Any:
        """
        Enables story templates by making a PUT request to the entity-templates endpoint.
        
        Returns:
            The JSON response from enabling story templates.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            enable, templates, management, http-put, 
        """
        url = f"{self.base_url}/api/v3/entity-templates/enable"
        query_params = {}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_entity_template(self, entity_template_public_id) -> dict[str, Any]:
        """
        Retrieves a specific entity template by its public ID.
        
        Args:
            entity_template_public_id: The public identifier of the entity template to retrieve.
        
        Returns:
            A dictionary containing the entity template data.
        
        Raises:
            ValueError: Raised when the required entity_template_public_id parameter is None.
            HTTPError: Raised when the HTTP request fails.
        
        Tags:
            get, retrieve, entity, template, api, 
        """
        if entity_template_public_id is None:
            raise ValueError("Missing required parameter 'entity-template-public-id'")
        url = f"{self.base_url}/api/v3/entity-templates/{entity_template_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_entity_template(self, entity_template_public_id, name=None, story_contents=None) -> dict[str, Any]:
        """
        Updates an entity template using the provided public ID, optionally setting its name and story contents.
        
        Args:
            entity_template_public_id: The public ID of the entity template to be updated
            name: Optional name for the entity template
            story_contents: Optional story contents for the entity template
        
        Returns:
            A dictionary containing the updated entity template details
        
        Raises:
            ValueError: Raised when the required 'entity_template_public_id' parameter is missing.
        
        Tags:
            update, entity-template, management, 
        """
        if entity_template_public_id is None:
            raise ValueError("Missing required parameter 'entity-template-public-id'")
        request_body = {
            'name': name,
            'story_contents': story_contents,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/entity-templates/{entity_template_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_entity_template(self, entity_template_public_id) -> Any:
        """
        Deletes an entity template by its public ID.
        
        Args:
            entity_template_public_id: The public ID of the entity template to delete.
        
        Returns:
            The JSON response from the server after deletion.
        
        Raises:
            ValueError: Raised if the entity template public ID is missing.
        
        Tags:
            delete, entity-management, 
        """
        if entity_template_public_id is None:
            raise ValueError("Missing required parameter 'entity-template-public-id'")
        url = f"{self.base_url}/api/v3/entity-templates/{entity_template_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_epic_workflow(self, ) -> dict[str, Any]:
        """
        Retrieves the epic workflow configuration from the API.
        
        Returns:
            A dictionary containing the epic workflow configuration data from the API response.
        
        Raises:
            HTTPError: Raised when the API request fails, as triggered by raise_for_status().
        
        Tags:
            get, retrieve, api, workflow, epic, configuration, 
        """
        url = f"{self.base_url}/api/v3/epic-workflow"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_epics(self, includes_description=None) -> list[Any]:
        """
        Fetches a list of epics from the API.
        
        Args:
            includes_description: Optional flag to include the description of epics in the response. Defaults to None.
        
        Returns:
            A list of epics.
        
        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            list, epics, async-job, management, important
        """
        url = f"{self.base_url}/api/v3/epics"
        query_params = {k: v for k, v in [('includes_description', includes_description)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_epic(self, name, description=None, labels=None, completed_at_override=None, objective_ids=None, planned_start_date=None, state=None, milestone_id=None, requested_by_id=None, epic_state_id=None, started_at_override=None, group_id=None, updated_at=None, follower_ids=None, group_ids=None, owner_ids=None, external_id=None, deadline=None, created_at=None) -> dict[str, Any]:
        """
        Creates a new epic in the project management system with the specified properties.
        
        Args:
            name: The name of the epic. Required parameter.
            description: A detailed description of the epic.
            labels: Tags or categories associated with the epic.
            completed_at_override: Custom completion date for the epic.
            objective_ids: List of objective IDs associated with this epic.
            planned_start_date: The date when work on the epic is planned to start.
            state: Current state of the epic (e.g., 'in_progress', 'completed').
            milestone_id: ID of the milestone associated with this epic.
            requested_by_id: ID of the user who requested the epic.
            epic_state_id: ID representing the custom workflow state of the epic.
            started_at_override: Custom start date for the epic.
            group_id: ID of the primary group associated with the epic.
            updated_at: Timestamp when the epic was last updated.
            follower_ids: List of user IDs following this epic.
            group_ids: List of group IDs associated with this epic.
            owner_ids: List of user IDs who own this epic.
            external_id: External identifier for integration with other systems.
            deadline: Due date for the epic completion.
            created_at: Timestamp when the epic was created.
        
        Returns:
            A dictionary containing the created epic data as returned by the API.
        
        Raises:
            ValueError: Raised when the required parameter 'name' is not provided.
            HTTPError: Raised when the API request fails.
        
        Tags:
            create, epic, project-management, api, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'description': description,
            'labels': labels,
            'completed_at_override': completed_at_override,
            'objective_ids': objective_ids,
            'name': name,
            'planned_start_date': planned_start_date,
            'state': state,
            'milestone_id': milestone_id,
            'requested_by_id': requested_by_id,
            'epic_state_id': epic_state_id,
            'started_at_override': started_at_override,
            'group_id': group_id,
            'updated_at': updated_at,
            'follower_ids': follower_ids,
            'group_ids': group_ids,
            'owner_ids': owner_ids,
            'external_id': external_id,
            'deadline': deadline,
            'created_at': created_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/epics"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_epic(self, epic_public_id) -> dict[str, Any]:
        """
        Fetches an epic by its public ID
        
        Args:
            epic_public_id: The public ID of the epic to retrieve
        
        Returns:
            A dictionary containing the details of the retrieved epic
        
        Raises:
            ValueError: Raised if the epic_public_id is missing
        
        Tags:
            fetch, epic, management, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_epic(self, epic_public_id, description=None, archived=None, labels=None, completed_at_override=None, objective_ids=None, name=None, planned_start_date=None, state=None, milestone_id=None, requested_by_id=None, epic_state_id=None, started_at_override=None, group_id=None, follower_ids=None, group_ids=None, owner_ids=None, external_id=None, before_id=None, after_id=None, deadline=None) -> dict[str, Any]:
        """
        Updates an epic with the provided details.
        
        Args:
            epic_public_id: The public ID of the epic to be updated.
            description: Optional description of the epic.
            archived: Optional flag indicating if the epic is archived.
            labels: Optional list of labels for the epic.
            completed_at_override: Optional override date for when the epic was completed.
            objective_ids: Optional list of objective IDs.
            name: Optional new name for the epic.
            planned_start_date: Optional planned start date.
            state: Optional state of the epic (e.g., 'to-do', 'in-progress', 'done').
            milestone_id: Optional ID of a milestone associated with the epic.
            requested_by_id: Optional ID of the user who requested the epic.
            epic_state_id: Optional ID of the epic state.
            started_at_override: Optional override date for when the epic started.
            group_id: Optional ID of a group associated with the epic.
            follower_ids: Optional list of follower IDs.
            group_ids: Optional list of group IDs.
            owner_ids: Optional list of owner IDs.
            external_id: Optional external ID for the epic.
            before_id: Optional placement parameter indicating where the epic should be placed relative to other epics.
            after_id: Optional placement parameter for ordering the epic.
            deadline: Optional deadline for the epic.
        
        Returns:
            A dictionary containing the updated epic details.
        
        Raises:
            ValueError: Raised if the required 'epic_public_id' parameter is missing.
            requests.exceptions.HTTPError: Raised if there are issues with the HTTP request.
        
        Tags:
            update, epic, management, , async-job
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        request_body = {
            'description': description,
            'archived': archived,
            'labels': labels,
            'completed_at_override': completed_at_override,
            'objective_ids': objective_ids,
            'name': name,
            'planned_start_date': planned_start_date,
            'state': state,
            'milestone_id': milestone_id,
            'requested_by_id': requested_by_id,
            'epic_state_id': epic_state_id,
            'started_at_override': started_at_override,
            'group_id': group_id,
            'follower_ids': follower_ids,
            'group_ids': group_ids,
            'owner_ids': owner_ids,
            'external_id': external_id,
            'before_id': before_id,
            'after_id': after_id,
            'deadline': deadline,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_epic(self, epic_public_id) -> Any:
        """
        Deletes an epic by its public ID.
        
        Args:
            epic_public_id: The public identifier of the epic to be deleted.
        
        Returns:
            The JSON response from the API after successfully deleting the epic.
        
        Raises:
            ValueError: When the required parameter 'epic-public-id' is None.
            HTTPError: When the HTTP request returns an unsuccessful status code.
        
        Tags:
            delete, epic, api, management, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_epic_comments(self, epic_public_id) -> list[Any]:
        """
        Retrieves a list of comments for a specified epic.
        
        Args:
            epic_public_id: The public identifier of the epic whose comments are to be retrieved.
        
        Returns:
            A list of comment objects associated with the specified epic.
        
        Raises:
            ValueError: When the required epic_public_id parameter is None.
            HTTPError: When the HTTP request to retrieve comments fails.
        
        Tags:
            list, retrieve, comments, epic, api
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/comments"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_epic_comment(self, epic_public_id, text, author_id=None, created_at=None, updated_at=None, external_id=None) -> dict[str, Any]:
        """
        Creates a comment on an epic with the specified details.
        
        Args:
            epic_public_id: The public identifier of the epic to which the comment will be added.
            text: The content of the comment to be created.
            author_id: Optional. The identifier of the author creating the comment.
            created_at: Optional. The timestamp when the comment was created.
            updated_at: Optional. The timestamp when the comment was last updated.
            external_id: Optional. An external identifier for the comment.
        
        Returns:
            A dictionary containing the created comment's details.
        
        Raises:
            ValueError: Raised when either epic_public_id or text is None.
        
        Tags:
            create, comment, epic, api, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
            'author_id': author_id,
            'created_at': created_at,
            'updated_at': updated_at,
            'external_id': external_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/comments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_epic_comment(self, epic_public_id, comment_public_id) -> dict[str, Any]:
        """
        Retrieves a specific comment from an epic by their respective public IDs.
        
        Args:
            epic_public_id: The public identifier of the epic containing the comment.
            comment_public_id: The public identifier of the comment to retrieve.
        
        Returns:
            A dictionary containing the comment data from the API response.
        
        Raises:
            ValueError: When either epic_public_id or comment_public_id is None.
            HTTPError: When the API request fails.
        
        Tags:
            get, retrieve, epic, comment, api
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_epic_comment(self, epic_public_id, comment_public_id, text) -> dict[str, Any]:
        """
        Updates the text of an existing comment on a specified epic.
        
        Args:
            epic_public_id: str. The public identifier of the epic containing the comment to update.
            comment_public_id: str. The public identifier of the comment to update.
            text: str. The new text content for the comment.
        
        Returns:
            dict[str, Any]: A dictionary representing the updated comment resource as returned by the API.
        
        Raises:
            ValueError: Raised if any of the required parameters ('epic_public_id', 'comment_public_id', or 'text') are None.
            HTTPError: Raised if the HTTP request to update the comment fails (non-2xx response).
        
        Tags:
            update, comment, epic, management, api, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_epic_comment_comment(self, epic_public_id, comment_public_id, text, author_id=None, created_at=None, updated_at=None, external_id=None) -> dict[str, Any]:
        """
        Creates a reply to an existing comment on a specified epic, sending the reply to the backend API and returning the created comment data.
        
        Args:
            epic_public_id: str. The public identifier for the epic (required).
            comment_public_id: str. The public identifier for the parent comment being replied to (required).
            text: str. The content of the reply comment (required).
            author_id: Optional[str]. The public identifier for the author of the reply.
            created_at: Optional[str]. The creation timestamp of the comment, in ISO 8601 format.
            updated_at: Optional[str]. The last updated timestamp of the comment, in ISO 8601 format.
            external_id: Optional[str]. An external system identifier for the comment.
        
        Returns:
            dict[str, Any]: The created comment object as returned by the API.
        
        Raises:
            ValueError: If any of 'epic_public_id', 'comment_public_id', or 'text' is None.
            requests.HTTPError: If the API response status indicates an HTTP error.
        
        Tags:
            create, comment, epic, reply, api, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
            'author_id': author_id,
            'created_at': created_at,
            'updated_at': updated_at,
            'external_id': external_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_epic_comment(self, epic_public_id, comment_public_id) -> Any:
        """
        Deletes a specific comment from an epic using its public identifiers.
        
        Args:
            epic_public_id: The public identifier of the epic containing the comment to delete.
            comment_public_id: The public identifier of the comment to be deleted.
        
        Returns:
            The server's response as a parsed JSON object, typically containing details of the deletion result.
        
        Raises:
            ValueError: Raised if either 'epic_public_id' or 'comment_public_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the comment fails.
        
        Tags:
            delete, comment-management, epic, api, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_epic_stories(self, epic_public_id, includes_description=None) -> list[Any]:
        """
        Retrieves a list of stories associated with a specific epic.
        
        Args:
            epic_public_id: The unique identifier of the epic whose stories are to be retrieved.
            includes_description: Boolean flag indicating whether to include story descriptions in the response. If None, descriptions are not included.
        
        Returns:
            A list of story objects associated with the specified epic, with each story represented as a dictionary.
        
        Raises:
            ValueError: Raised when the required parameter 'epic_public_id' is None.
            HTTPError: Raised when the HTTP request to the API endpoint fails.
        
        Tags:
            list, retrieve, epic, stories, management, 
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/stories"
        query_params = {k: v for k, v in [('includes_description', includes_description)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def unlink_productboard_from_epic(self, epic_public_id) -> Any:
        """
        Unlinks a ProductBoard integration from an epic in the system.
        
        Args:
            epic_public_id: The public identifier of the epic to unlink from ProductBoard.
        
        Returns:
            JSON response containing the result of the unlink operation.
        
        Raises:
            ValueError: Raised when the required epic_public_id parameter is None.
            HTTPError: Raised when the API request fails or returns an error status code.
        
        Tags:
            unlink, epic, productboard, integration, api
        """
        if epic_public_id is None:
            raise ValueError("Missing required parameter 'epic-public-id'")
        url = f"{self.base_url}/api/v3/epics/{epic_public_id}/unlink-productboard"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_external_link_stories(self, external_link) -> list[Any]:
        """
        Retrieves stories associated with an external link.
        
        Args:
            external_link: The URL of the external link to query for associated stories. Must not be None.
        
        Returns:
            A list of story objects associated with the provided external link.
        
        Raises:
            ValueError: Raised when the 'external_link' parameter is None.
            HTTPError: Raised when the HTTP request fails (via raise_for_status()).
        
        Tags:
            retrieve, stories, external-link, api, get, query, 
        """
        if external_link is None:
            raise ValueError("Missing required parameter 'external_link'")
        url = f"{self.base_url}/api/v3/external-link/stories"
        query_params = {k: v for k, v in [('external_link', external_link)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_files(self, ) -> list[Any]:
        """
        Retrieves a list of files from the remote API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A list containing file objects deserialized from the API response.
        
        Raises:
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.
        
        Tags:
            list, files, api, 
        """
        url = f"{self.base_url}/api/v3/files"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_file(self, file_public_id) -> dict[str, Any]:
        """
        Retrieves a file based on its public ID, returning a dictionary containing file information.
        
        Args:
            file_public_id: The public ID of the file to retrieve; must be a string.
        
        Returns:
            A dictionary containing file information retrieved from the API.
        
        Raises:
            ValueError: Raised if the 'file_public_id' parameter is missing.
        
        Tags:
            fetch, management, 
        """
        if file_public_id is None:
            raise ValueError("Missing required parameter 'file-public-id'")
        url = f"{self.base_url}/api/v3/files/{file_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_file(self, file_public_id, description=None, created_at=None, updated_at=None, name=None, uploader_id=None, external_id=None) -> dict[str, Any]:
        """
        Updates metadata for a file identified by its public ID.
        
        Args:
            file_public_id: The public ID of the file to update. Must not be None.
            description: Optional. New description for the file.
            created_at: Optional. New creation timestamp for the file.
            updated_at: Optional. New update timestamp for the file.
            name: Optional. New name for the file.
            uploader_id: Optional. ID of the user who uploaded the file.
            external_id: Optional. External identifier for the file.
        
        Returns:
            Dictionary containing the updated file information from the API response.
        
        Raises:
            ValueError: Raised when file_public_id is None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            update, file, api, metadata, 
        """
        if file_public_id is None:
            raise ValueError("Missing required parameter 'file-public-id'")
        request_body = {
            'description': description,
            'created_at': created_at,
            'updated_at': updated_at,
            'name': name,
            'uploader_id': uploader_id,
            'external_id': external_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/files/{file_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_file(self, file_public_id) -> Any:
        """
        Deletes a file identified by a public ID from the server.
        
        Args:
            file_public_id: String representing the unique public identifier of the file to be deleted.
        
        Returns:
            JSON representation of the server's response after deletion.
        
        Raises:
            ValueError: Raised when file_public_id is None, as it's a required parameter.
            HTTPError: Raised when the server returns an error status code.
        
        Tags:
            delete, file, management, 
        """
        if file_public_id is None:
            raise ValueError("Missing required parameter 'file-public-id'")
        url = f"{self.base_url}/api/v3/files/{file_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_groups(self, ) -> list[Any]:
        """
        Retrieves a list of all groups from the API.
        
        Returns:
            A list of dictionaries containing group information from the API response.
        
        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.
        
        Tags:
            list, groups, api, get, 
        """
        url = f"{self.base_url}/api/v3/groups"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_group(self, name, mention_name, description=None, member_ids=None, workflow_ids=None, color=None, color_key=None, display_icon_id=None) -> dict[str, Any]:
        """
        Creates a new group with the specified configuration and returns the group's details.
        
        Args:
            name: str. The display name of the group. This parameter is required.
            mention_name: str. The mention identifier for the group (e.g., @groupname). This parameter is required.
            description: Optional[str]. A description of the group.
            member_ids: Optional[list[str]]. A list of user IDs to be added as group members.
            workflow_ids: Optional[list[str]]. A list of workflow IDs to associate with the group.
            color: Optional[str]. The display color for the group in hexadecimal or named format.
            color_key: Optional[str]. A predefined key representing the group's color.
            display_icon_id: Optional[str]. The ID of the icon to be displayed for the group.
        
        Returns:
            dict[str, Any]: A dictionary containing the details of the newly created group as returned by the backend API.
        
        Raises:
            ValueError: Raised if the required parameters 'name' or 'mention_name' are missing.
            requests.HTTPError: Raised if the HTTP request to create the group fails (non-2xx status code).
        
        Tags:
            create, group, management, api, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if mention_name is None:
            raise ValueError("Missing required parameter 'mention_name'")
        request_body = {
            'description': description,
            'member_ids': member_ids,
            'workflow_ids': workflow_ids,
            'name': name,
            'mention_name': mention_name,
            'color': color,
            'color_key': color_key,
            'display_icon_id': display_icon_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/groups"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_group(self, group_public_id) -> dict[str, Any]:
        """
        Retrieves information about a specific group using its public ID.
        
        Args:
            group_public_id: The public identifier of the group to retrieve.
        
        Returns:
            A dictionary containing the group's information from the API response.
        
        Raises:
            ValueError: When the required parameter 'group_public_id' is None.
            HTTPError: When the API request fails or returns an error status code.
        
        Tags:
            get, retrieve, group, api, 
        """
        if group_public_id is None:
            raise ValueError("Missing required parameter 'group-public-id'")
        url = f"{self.base_url}/api/v3/groups/{group_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_group(self, group_public_id, description=None, archived=None, color=None, display_icon_id=None, mention_name=None, name=None, color_key=None, member_ids=None, workflow_ids=None) -> dict[str, Any]:
        """
        Updates the properties of an existing group by its public ID.
        
        Args:
            group_public_id: str. The unique public identifier of the group to update.
            description: str or None. The new description for the group.
            archived: bool or None. Whether the group should be archived.
            color: str or None. The new color for the group.
            display_icon_id: str or None. Identifier of the display icon for the group.
            mention_name: str or None. The mention name for the group.
            name: str or None. The new name for the group.
            color_key: str or None. The color key for the group.
            member_ids: list[str] or None. List of member IDs to assign to the group.
            workflow_ids: list[str] or None. List of workflow IDs to associate with the group.
        
        Returns:
            dict[str, Any]: The updated group data as returned by the API.
        
        Raises:
            ValueError: If 'group_public_id' is not provided.
            requests.HTTPError: If the HTTP request to update the group fails.
        
        Tags:
            update, management, group, api, 
        """
        if group_public_id is None:
            raise ValueError("Missing required parameter 'group-public-id'")
        request_body = {
            'description': description,
            'archived': archived,
            'color': color,
            'display_icon_id': display_icon_id,
            'mention_name': mention_name,
            'name': name,
            'color_key': color_key,
            'member_ids': member_ids,
            'workflow_ids': workflow_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/groups/{group_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_group_stories(self, group_public_id, limit=None, offset=None) -> list[Any]:
        """
        Retrieves a list of stories from a specific group.
        
        Args:
            group_public_id: The public identifier of the group to retrieve stories from.
            limit: The maximum number of stories to return. If None, returns all available stories.
            offset: The number of stories to skip before starting to collect the result set. If None, starts from the beginning.
        
        Returns:
            A list of story objects in JSON format.
        
        Raises:
            ValueError: When the required parameter 'group_public_id' is None.
            HTTPError: When the HTTP request fails or returns an error status code.
        
        Tags:
            list, retrieve, stories, group, api, 
        """
        if group_public_id is None:
            raise ValueError("Missing required parameter 'group-public-id'")
        url = f"{self.base_url}/api/v3/groups/{group_public_id}/stories"
        query_params = {k: v for k, v in [('limit', limit), ('offset', offset)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_iterations(self, ) -> list[Any]:
        """
        Lists all available iterations from the API.
        
        Args:
            None: This function takes no parameters.
        
        Returns:
            A list of iteration objects retrieved from the API endpoint.
        
        Raises:
            HTTPError: Raised when the HTTP request fails due to an error status code.
        
        Tags:
            list, iterations, api, retrieve, 
        """
        url = f"{self.base_url}/api/v3/iterations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_iteration(self, name, start_date, end_date, follower_ids=None, group_ids=None, labels=None, description=None) -> dict[str, Any]:
        """
        Creates a new iteration with the specified details and returns the server's response as a dictionary.
        
        Args:
            name: str. The name of the iteration to create. Required.
            start_date: str. The starting date of the iteration in ISO format. Required.
            end_date: str. The ending date of the iteration in ISO format. Required.
            follower_ids: Optional[list[str]]. List of user IDs to assign as followers for the iteration.
            group_ids: Optional[list[str]]. List of group IDs associated with the iteration.
            labels: Optional[list[str]]. List of labels to tag the iteration.
            description: Optional[str]. Additional description for the iteration.
        
        Returns:
            dict[str, Any]: The JSON response from the server containing details of the created iteration.
        
        Raises:
            ValueError: If any required parameter ('name', 'start_date', 'end_date') is missing.
            requests.HTTPError: If the HTTP request to create the iteration fails (non-2xx response).
        
        Tags:
            create, iteration, api, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if start_date is None:
            raise ValueError("Missing required parameter 'start_date'")
        if end_date is None:
            raise ValueError("Missing required parameter 'end_date'")
        request_body = {
            'follower_ids': follower_ids,
            'group_ids': group_ids,
            'labels': labels,
            'description': description,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/iterations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def disable_iterations(self, ) -> Any:
        """
        Disables iterations by making a PUT request to the iterations API endpoint.
        
        Returns:
            JSON response from the server after disabling iterations.
        
        Raises:
            HTTPError: Raised when the HTTP request returns an unsuccessful status code.
        
        Tags:
            disable, iterations, api, management, 
        """
        url = f"{self.base_url}/api/v3/iterations/disable"
        query_params = {}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def enable_iterations(self, ) -> Any:
        """
        Enable iterations for the API service.
        
        Returns:
            JSON response from the API containing the result of enabling iterations.
        
        Raises:
            HTTPError: Raised when the HTTP request returns an unsuccessful status code.
        
        Tags:
            enable, iterations, api, management, 
        """
        url = f"{self.base_url}/api/v3/iterations/enable"
        query_params = {}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_iteration(self, iteration_public_id) -> dict[str, Any]:
        """
        Retrieves iteration details using the specified public ID.
        
        Args:
            iteration_public_id: The public ID of the iteration to retrieve.
        
        Returns:
            A dictionary containing the iteration details from the API response.
        
        Raises:
            ValueError: Raised when the required parameter 'iteration-public-id' is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).
        
        Tags:
            get, retrieve, iteration, api, 
        """
        if iteration_public_id is None:
            raise ValueError("Missing required parameter 'iteration-public-id'")
        url = f"{self.base_url}/api/v3/iterations/{iteration_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_iteration(self, iteration_public_id, follower_ids=None, group_ids=None, labels=None, description=None, name=None, start_date=None, end_date=None) -> dict[str, Any]:
        """
        Updates an existing iteration with the provided attributes.
        
        Args:
            iteration_public_id: The unique identifier for the iteration to be updated.
            follower_ids: Optional list of user IDs to follow the iteration.
            group_ids: Optional list of group IDs associated with the iteration.
            labels: Optional list of labels to apply to the iteration.
            description: Optional text describing the iteration.
            name: Optional name for the iteration.
            start_date: Optional start date for the iteration.
            end_date: Optional end date for the iteration.
        
        Returns:
            A dictionary containing the updated iteration data.
        
        Raises:
            ValueError: When the required parameter 'iteration_public_id' is None.
            HTTPError: When the API request fails.
        
        Tags:
            update, iteration, management, 
        """
        if iteration_public_id is None:
            raise ValueError("Missing required parameter 'iteration-public-id'")
        request_body = {
            'follower_ids': follower_ids,
            'group_ids': group_ids,
            'labels': labels,
            'description': description,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/iterations/{iteration_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_iteration(self, iteration_public_id) -> Any:
        """
        Deletes a specific iteration identified by its public ID.
        
        Args:
            iteration_public_id: String representing the public ID of the iteration to be deleted.
        
        Returns:
            JSON response from the API containing information about the deleted iteration.
        
        Raises:
            ValueError: Raised when the required 'iteration_public_id' parameter is None.
            HTTPError: Raised when the API request fails or returns an error status code.
        
        Tags:
            delete, management, api, iteration, 
        """
        if iteration_public_id is None:
            raise ValueError("Missing required parameter 'iteration-public-id'")
        url = f"{self.base_url}/api/v3/iterations/{iteration_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_iteration_stories(self, iteration_public_id, includes_description=None) -> list[Any]:
        """
        Retrieves a list of stories for a specified iteration, optionally including their descriptions.
        
        Args:
            iteration_public_id: str. The public identifier of the iteration whose stories are to be listed.
            includes_description: Optional[bool]. Whether to include story descriptions in the response. If None, descriptions are not included.
        
        Returns:
            list[Any]: A list containing story data dictionaries for the specified iteration.
        
        Raises:
            ValueError: Raised if 'iteration_public_id' is None.
            HTTPError: Raised if the HTTP request returns an unsuccessful status code.
        
        Tags:
            list, stories, iteration, api, 
        """
        if iteration_public_id is None:
            raise ValueError("Missing required parameter 'iteration-public-id'")
        url = f"{self.base_url}/api/v3/iterations/{iteration_public_id}/stories"
        query_params = {k: v for k, v in [('includes_description', includes_description)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_key_result(self, key_result_public_id) -> dict[str, Any]:
        """
        Retrieves detailed information for a specific key result using its public identifier.
        
        Args:
            key_result_public_id: The public identifier (str) of the key result to retrieve.
        
        Returns:
            A dictionary containing the key result's data as returned by the API.
        
        Raises:
            ValueError: If the key_result_public_id parameter is None.
            requests.exceptions.HTTPError: If the underlying HTTP request fails or returns a bad status code.
        
        Tags:
            get, key-result, api, management, 
        """
        if key_result_public_id is None:
            raise ValueError("Missing required parameter 'key-result-public-id'")
        url = f"{self.base_url}/api/v3/key-results/{key_result_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_key_result(self, key_result_public_id, name=None, initial_observed_value=None, observed_value=None, target_value=None) -> dict[str, Any]:
        """
        Updates a key result with the provided details.
        
        Args:
            key_result_public_id: The public ID of the key result to update.
            name: Optional new name for the key result.
            initial_observed_value: Optional new initial observed value for the key result.
            observed_value: Optional new observed value for the key result.
            target_value: Optional new target value for the key result.
        
        Returns:
            A dictionary containing the details of the updated key result.
        
        Raises:
            ValueError: Raised if the 'key_result_public_id' parameter is missing.
        
        Tags:
            update, management, 
        """
        if key_result_public_id is None:
            raise ValueError("Missing required parameter 'key-result-public-id'")
        request_body = {
            'name': name,
            'initial_observed_value': initial_observed_value,
            'observed_value': observed_value,
            'target_value': target_value,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/key-results/{key_result_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_labels(self, slim=None) -> list[Any]:
        """
        Fetches a list of labels from the API.
        
        Args:
            slim: Boolean flag that when set to True returns a simplified version of labels. If None, the default API behavior is used.
        
        Returns:
            A list of label objects (dictionaries) containing label information returned by the API.
        
        Raises:
            HTTPError: Raised when the API request fails or returns an error status code.
        
        Tags:
            list, fetch, labels, api, data-retrieval, 
        """
        url = f"{self.base_url}/api/v3/labels"
        query_params = {k: v for k, v in [('slim', slim)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_label(self, name, description=None, color=None, external_id=None) -> dict[str, Any]:
        """
        Creates a new label with the specified attributes.
        
        Args:
            name: The name of the label (required).
            description: Optional description of the label.
            color: Optional color specification for the label.
            external_id: Optional external identifier for the label.
        
        Returns:
            A dictionary containing the created label's data as returned by the API.
        
        Raises:
            ValueError: Raised when the required 'name' parameter is None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            create, label, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'name': name,
            'description': description,
            'color': color,
            'external_id': external_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/labels"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_label(self, label_public_id) -> dict[str, Any]:
        """
        Retrieves a label's details from the API using its public identifier.
        
        Args:
            label_public_id: str. The public identifier of the label to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing label details as returned by the API.
        
        Raises:
            ValueError: If 'label_public_id' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error response.
        
        Tags:
            get, label, fetch, api, management, 
        """
        if label_public_id is None:
            raise ValueError("Missing required parameter 'label-public-id'")
        url = f"{self.base_url}/api/v3/labels/{label_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_label(self, label_public_id, name=None, description=None, color=None, archived=None) -> dict[str, Any]:
        """
        Updates a label with the specified information.
        
        Args:
            label_public_id: The public ID of the label to update.
            name: Optional. The new name for the label.
            description: Optional. The new description for the label.
            color: Optional. The new color for the label.
            archived: Optional. Boolean indicating whether the label should be archived.
        
        Returns:
            A dictionary containing the updated label information.
        
        Raises:
            ValueError: If label_public_id is None.
            HTTPError: If the request to update the label fails.
        
        Tags:
            update, label, management, 
        """
        if label_public_id is None:
            raise ValueError("Missing required parameter 'label-public-id'")
        request_body = {
            'name': name,
            'description': description,
            'color': color,
            'archived': archived,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/labels/{label_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_label(self, label_public_id) -> Any:
        """
        Deletes a label identified by its public ID via an HTTP DELETE request.
        
        Args:
            label_public_id: The public unique identifier of the label to be deleted.
        
        Returns:
            The parsed JSON response from the API after deleting the label.
        
        Raises:
            ValueError: If 'label_public_id' is None.
            HTTPError: If the HTTP request to delete the label fails (e.g., network issues, 4xx/5xx response from the server).
        
        Tags:
            delete, label-management, api, 
        """
        if label_public_id is None:
            raise ValueError("Missing required parameter 'label-public-id'")
        url = f"{self.base_url}/api/v3/labels/{label_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_label_epics(self, label_public_id) -> list[Any]:
        """
        Retrieves a list of epics associated with a specific label.
        
        Args:
            label_public_id: The unique identifier of the label whose associated epics are to be retrieved.
        
        Returns:
            A list of epic objects associated with the specified label.
        
        Raises:
            ValueError: Raised when the required parameter 'label_public_id' is None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            list, retrieve, epics, label, api
        """
        if label_public_id is None:
            raise ValueError("Missing required parameter 'label-public-id'")
        url = f"{self.base_url}/api/v3/labels/{label_public_id}/epics"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_label_stories(self, label_public_id, includes_description=None) -> list[Any]:
        """
        Retrieves a list of stories associated with a specific label.
        
        Args:
            label_public_id: The public identifier of the label whose stories are to be retrieved.
            includes_description: Optional flag to include story descriptions in the response.
        
        Returns:
            A list of story objects associated with the specified label.
        
        Raises:
            ValueError: Raised when the required parameter 'label_public_id' is None.
            HTTPError: Raised when the HTTP request to the API fails.
        
        Tags:
            list, stories, labels, retrieve, api, 
        """
        if label_public_id is None:
            raise ValueError("Missing required parameter 'label-public-id'")
        url = f"{self.base_url}/api/v3/labels/{label_public_id}/stories"
        query_params = {k: v for k, v in [('includes_description', includes_description)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_linked_files(self, ) -> list[Any]:
        """
        Retrieve a list of all linked files.
        
        Returns:
            A list of dictionaries, where each dictionary contains information about a linked file.
        
        Raises:
            HTTPError: Raised when the HTTP request returns an unsuccessful status code.
        
        Tags:
            list, linked-files, api, get, 
        """
        url = f"{self.base_url}/api/v3/linked-files"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_linked_file(self, name, type, url, description=None, story_id=None, thumbnail_url=None, size=None, uploader_id=None, content_type=None) -> dict[str, Any]:
        """
        Creates a linked file with the specified attributes.
        
        Args:
            name: The name of the linked file (required).
            type: The type of the linked file (required).
            url: The URL of the linked file (required).
            description: Optional description of the linked file.
            story_id: Optional ID of the story this file is linked to.
            thumbnail_url: Optional URL for the thumbnail of the linked file.
            size: Optional size of the linked file.
            uploader_id: Optional ID of the user who uploaded the file.
            content_type: Optional content type of the linked file.
        
        Returns:
            Dictionary containing the created linked file information.
        
        Raises:
            ValueError: Raised when required parameters 'name', 'type', or 'url' are None.
            HTTPError: Raised when the HTTP request fails.
        
        Tags:
            create, file, linked, api, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if url is None:
            raise ValueError("Missing required parameter 'url'")
        request_body = {
            'description': description,
            'story_id': story_id,
            'name': name,
            'thumbnail_url': thumbnail_url,
            'type': type,
            'size': size,
            'uploader_id': uploader_id,
            'content_type': content_type,
            'url': url,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/linked-files"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_linked_file(self, linked_file_public_id) -> dict[str, Any]:
        """
        Fetches details for a linked file by its public identifier.
        
        Args:
            linked_file_public_id: The public identifier (string) of the linked file to retrieve.
        
        Returns:
            A dictionary containing metadata and details of the requested linked file.
        
        Raises:
            ValueError: If 'linked_file_public_id' is None.
            HTTPError: If the HTTP request to fetch the linked file fails.
        
        Tags:
            fetch, linked-files, api, http, 
        """
        if linked_file_public_id is None:
            raise ValueError("Missing required parameter 'linked-file-public-id'")
        url = f"{self.base_url}/api/v3/linked-files/{linked_file_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_linked_file(self, linked_file_public_id, description=None, story_id=None, name=None, thumbnail_url=None, type=None, size=None, uploader_id=None, url=None) -> dict[str, Any]:
        """
        Updates a linked file with the specified parameters.
        
        Args:
            linked_file_public_id: The unique identifier of the linked file to update. Required.
            description: Optional new description for the linked file.
            story_id: Optional story ID to associate with the linked file.
            name: Optional new name for the linked file.
            thumbnail_url: Optional URL for the linked file's thumbnail image.
            type: Optional type classification for the linked file.
            size: Optional size specification for the linked file.
            uploader_id: Optional ID of the user who uploaded the file.
            url: Optional URL where the linked file can be accessed.
        
        Returns:
            A dictionary containing the updated linked file data.
        
        Raises:
            ValueError: Raised when the required parameter 'linked-file-public-id' is None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            update, file, api, linked-file, management, 
        """
        if linked_file_public_id is None:
            raise ValueError("Missing required parameter 'linked-file-public-id'")
        request_body = {
            'description': description,
            'story_id': story_id,
            'name': name,
            'thumbnail_url': thumbnail_url,
            'type': type,
            'size': size,
            'uploader_id': uploader_id,
            'url': url,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/linked-files/{linked_file_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_linked_file(self, linked_file_public_id) -> Any:
        """
        Deletes a linked file by its public ID using the API.
        
        Args:
            linked_file_public_id: The public identifier of the linked file to be deleted.
        
        Returns:
            The JSON response from the API as returned by the DELETE operation.
        
        Raises:
            ValueError: If 'linked_file_public_id' is None.
            requests.HTTPError: If the HTTP request to delete the linked file fails.
        
        Tags:
            delete, linked-file, api, management, 
        """
        if linked_file_public_id is None:
            raise ValueError("Missing required parameter 'linked-file-public-id'")
        url = f"{self.base_url}/api/v3/linked-files/{linked_file_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_current_member_info(self, ) -> dict[str, Any]:
        """
        Retrieves information about the current authenticated member.
        
        Returns:
            A dictionary containing information about the current member.
        
        Raises:
            HTTPError: When the API request fails or returns a non-successful status code.
        
        Tags:
            get, retrieve, member, information, api, 
        """
        url = f"{self.base_url}/api/v3/member"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_milestones(self, ) -> list[Any]:
        """
        Lists milestones by fetching them from a specified API endpoint.
        
        Args:
            None: This function takes no parameters.
        
        Returns:
            A list of milestones in JSON format.
        
        Raises:
            requests.exceptions.HTTPError: Raised when the HTTP request returns a status code indicating a client or server error.
        
        Tags:
            list, api, 
        """
        url = f"{self.base_url}/api/v3/milestones"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_milestone(self, name, description=None, state=None, started_at_override=None, completed_at_override=None, categories=None) -> dict[str, Any]:
        """
        Creates a new milestone with the specified parameters.
        
        Args:
            name: Required string representing the name of the milestone.
            description: Optional string describing the milestone.
            state: Optional string indicating the current state of the milestone.
            started_at_override: Optional datetime or string representing when the milestone was started.
            completed_at_override: Optional datetime or string representing when the milestone was completed.
            categories: Optional list or array of categories to associate with the milestone.
        
        Returns:
            A dictionary containing the created milestone data as returned by the API.
        
        Raises:
            ValueError: Raised when the required 'name' parameter is not provided or is None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            create, milestone, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'name': name,
            'description': description,
            'state': state,
            'started_at_override': started_at_override,
            'completed_at_override': completed_at_override,
            'categories': categories,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/milestones"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_milestone(self, milestone_public_id) -> dict[str, Any]:
        """
        Retrieves a milestone resource by its public identifier.
        
        Args:
            milestone_public_id: The public identifier of the milestone to retrieve.
        
        Returns:
            A dictionary containing the milestone details as returned by the API.
        
        Raises:
            ValueError: If 'milestone_public_id' is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.
        
        Tags:
            get, milestone, api, fetch, 
        """
        if milestone_public_id is None:
            raise ValueError("Missing required parameter 'milestone-public-id'")
        url = f"{self.base_url}/api/v3/milestones/{milestone_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_milestone(self, milestone_public_id, description=None, archived=None, completed_at_override=None, name=None, state=None, started_at_override=None, categories=None, before_id=None, after_id=None) -> dict[str, Any]:
        """
        Updates the properties of an existing milestone with the given parameters.
        
        Args:
            milestone_public_id: str. The unique public identifier of the milestone to update.
            description: str, optional. The new description for the milestone.
            archived: bool, optional. Whether to archive the milestone.
            completed_at_override: str or datetime, optional. Override value for the milestone's completion timestamp.
            name: str, optional. The new name for the milestone.
            state: str, optional. The new state of the milestone.
            started_at_override: str or datetime, optional. Override value for the milestone's start timestamp.
            categories: list or None, optional. A list of categories to associate with the milestone.
            before_id: str, optional. Insert this milestone before the specified milestone ID.
            after_id: str, optional. Insert this milestone after the specified milestone ID.
        
        Returns:
            dict. The updated milestone data as returned by the API.
        
        Raises:
            ValueError: If 'milestone_public_id' is not provided.
            requests.HTTPError: If the API request fails or returns an error status.
        
        Tags:
            update, milestone-management, api, 
        """
        if milestone_public_id is None:
            raise ValueError("Missing required parameter 'milestone-public-id'")
        request_body = {
            'description': description,
            'archived': archived,
            'completed_at_override': completed_at_override,
            'name': name,
            'state': state,
            'started_at_override': started_at_override,
            'categories': categories,
            'before_id': before_id,
            'after_id': after_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/milestones/{milestone_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_milestone(self, milestone_public_id) -> Any:
        """
        Deletes a milestone by its public ID.
        
        Args:
            milestone_public_id: The public ID of the milestone to be deleted.
        
        Returns:
            The JSON response from the API after successful deletion.
        
        Raises:
            ValueError: Raised when the milestone_public_id parameter is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).
        
        Tags:
            delete, milestone, api, 
        """
        if milestone_public_id is None:
            raise ValueError("Missing required parameter 'milestone-public-id'")
        url = f"{self.base_url}/api/v3/milestones/{milestone_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_milestone_epics(self, milestone_public_id) -> list[Any]:
        """
        Retrieves a list of epics associated with a specified milestone.
        
        Args:
            milestone_public_id: The public identifier of the milestone whose epics are to be listed.
        
        Returns:
            A list containing the epics related to the given milestone.
        
        Raises:
            ValueError: If 'milestone_public_id' is None.
            requests.HTTPError: If the HTTP request to fetch epics fails with a client or server error.
        
        Tags:
            list, epics, milestone, management, 
        """
        if milestone_public_id is None:
            raise ValueError("Missing required parameter 'milestone-public-id'")
        url = f"{self.base_url}/api/v3/milestones/{milestone_public_id}/epics"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_objectives(self, ) -> list[Any]:
        """
        Retrieves a list of all objectives from the API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A list containing the objectives returned by the API. Each item in the list represents an objective as parsed from the JSON response.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.
        
        Tags:
            list, objectives, api, management, 
        """
        url = f"{self.base_url}/api/v3/objectives"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_objective(self, name, description=None, state=None, started_at_override=None, completed_at_override=None, categories=None) -> dict[str, Any]:
        """
        Creates a new objective resource with the specified attributes and returns the created objective's data.
        
        Args:
            name: str. The name of the objective. This parameter is required.
            description: Optional[str]. A short description of the objective.
            state: Optional[str]. The current state of the objective.
            started_at_override: Optional[Any]. An override value for the start timestamp of the objective.
            completed_at_override: Optional[Any]. An override value for the completion timestamp of the objective.
            categories: Optional[Any]. Categories to associate with the objective.
        
        Returns:
            dict[str, Any]: A dictionary containing the data of the newly created objective as returned by the API.
        
        Raises:
            ValueError: Raised if the required parameter 'name' is missing.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns a non-success status code.
        
        Tags:
            create, objective, api, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'name': name,
            'description': description,
            'state': state,
            'started_at_override': started_at_override,
            'completed_at_override': completed_at_override,
            'categories': categories,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/objectives"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_objective(self, objective_public_id) -> dict[str, Any]:
        """
        Retrieves an objective by its public ID from the API.
        
        Args:
            objective_public_id: The unique public identifier of the objective to retrieve.
        
        Returns:
            A dictionary containing the objective data retrieved from the API.
        
        Raises:
            ValueError: When the objective_public_id parameter is None.
            HTTPError: When the API request fails or returns an error status code.
        
        Tags:
            get, retrieve, objective, api, 
        """
        if objective_public_id is None:
            raise ValueError("Missing required parameter 'objective-public-id'")
        url = f"{self.base_url}/api/v3/objectives/{objective_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_objective(self, objective_public_id, description=None, archived=None, completed_at_override=None, name=None, state=None, started_at_override=None, categories=None, before_id=None, after_id=None) -> dict[str, Any]:
        """
        Updates an objective by its public ID with new values for fields such as description, archived status, completion and start timestamps, name, state, categories, and relative ordering.
        
        Args:
            objective_public_id: str. The unique identifier of the objective to update. Required.
            description: str | None. The new description for the objective. Optional.
            archived: bool | None. Whether the objective is archived. Optional.
            completed_at_override: str | None. A custom completion timestamp for the objective, in ISO 8601 format. Optional.
            name: str | None. The new name of the objective. Optional.
            state: str | None. The new state of the objective. Optional.
            started_at_override: str | None. A custom start timestamp for the objective, in ISO 8601 format. Optional.
            categories: list[str] | None. A list of category names to associate with the objective. Optional.
            before_id: str | None. The public ID of another objective to place this one before. Optional.
            after_id: str | None. The public ID of another objective to place this one after. Optional.
        
        Returns:
            dict[str, Any]: The updated objective as returned by the API.
        
        Raises:
            ValueError: If 'objective_public_id' is None.
            requests.HTTPError: If the API responds with an error status code.
        
        Tags:
            update, objective, api, management, 
        """
        if objective_public_id is None:
            raise ValueError("Missing required parameter 'objective-public-id'")
        request_body = {
            'description': description,
            'archived': archived,
            'completed_at_override': completed_at_override,
            'name': name,
            'state': state,
            'started_at_override': started_at_override,
            'categories': categories,
            'before_id': before_id,
            'after_id': after_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/objectives/{objective_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_objective(self, objective_public_id) -> Any:
        """
        Deletes an objective by its public ID using an HTTP DELETE request.
        
        Args:
            objective_public_id: The public identifier of the objective to delete.
        
        Returns:
            The JSON-decoded response from the API if the deletion is successful.
        
        Raises:
            ValueError: If 'objective_public_id' is None.
            requests.HTTPError: If the HTTP DELETE request returns an unsuccessful status code.
        
        Tags:
            delete, objectives, api, http, 
        """
        if objective_public_id is None:
            raise ValueError("Missing required parameter 'objective-public-id'")
        url = f"{self.base_url}/api/v3/objectives/{objective_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_objective_epics(self, objective_public_id) -> list[Any]:
        """
        Retrieves a list of epics associated with a specific objective.
        
        Args:
            objective_public_id: The unique public identifier of the objective for which to list epics. Cannot be None.
        
        Returns:
            A list of epic objects associated with the specified objective, parsed from the JSON response.
        
        Raises:
            ValueError: Raised when the required parameter 'objective_public_id' is None.
            HTTPError: Raised when the HTTP request fails or returns an error status code.
        
        Tags:
            list, retrieve, epics, objectives, api, 
        """
        if objective_public_id is None:
            raise ValueError("Missing required parameter 'objective-public-id'")
        url = f"{self.base_url}/api/v3/objectives/{objective_public_id}/epics"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_projects(self, ) -> list[Any]:
        """
        Retrieves and lists all available projects from the API.
        
        Returns:
            A list of all projects retrieved from the API.
        
        Raises:
            requests.exceptions.HTTPError: Raised if there is a 4xx or 5xx status response from the server.
        
        Tags:
            list, projects, , api-call
        """
        url = f"{self.base_url}/api/v3/projects"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_project(self, name, team_id, description=None, color=None, start_time=None, updated_at=None, follower_ids=None, external_id=None, iteration_length=None, abbreviation=None, created_at=None) -> dict[str, Any]:
        """
        Creates a new project with the specified parameters.
        
        Args:
            name: Required. The name of the project.
            team_id: Required. The ID of the team the project belongs to.
            description: Optional. The description of the project.
            color: Optional. The color associated with the project.
            start_time: Optional. The start time of the project.
            updated_at: Optional. The timestamp when the project was last updated.
            follower_ids: Optional. List of IDs of users following the project.
            external_id: Optional. An external identifier for the project.
            iteration_length: Optional. The length of iteration for the project.
            abbreviation: Optional. A short abbreviation for the project.
            created_at: Optional. The timestamp when the project was created.
        
        Returns:
            A dictionary containing the created project's information.
        
        Raises:
            ValueError: Raised when the required parameters 'name' or 'team_id' are not provided.
        
        Tags:
            create, project, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if team_id is None:
            raise ValueError("Missing required parameter 'team_id'")
        request_body = {
            'description': description,
            'color': color,
            'name': name,
            'start_time': start_time,
            'updated_at': updated_at,
            'follower_ids': follower_ids,
            'external_id': external_id,
            'team_id': team_id,
            'iteration_length': iteration_length,
            'abbreviation': abbreviation,
            'created_at': created_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/projects"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project(self, project_public_id) -> dict[str, Any]:
        """
        Retrieves project information by its public ID.
        
        Args:
            project_public_id: The public identifier of the project to retrieve
        
        Returns:
            A dictionary containing project information retrieved from the API
        
        Raises:
            ValueError: When the required project_public_id parameter is None
            HTTPError: When the HTTP request fails (via raise_for_status)
        
        Tags:
            get, retrieve, project, api, 
        """
        if project_public_id is None:
            raise ValueError("Missing required parameter 'project-public-id'")
        url = f"{self.base_url}/api/v3/projects/{project_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_project(self, project_public_id, description=None, archived=None, days_to_thermometer=None, color=None, name=None, follower_ids=None, show_thermometer=None, team_id=None, abbreviation=None) -> dict[str, Any]:
        """
        Updates a project with the provided parameters.
        
        Args:
            project_public_id: The unique identifier of the project to update.
            description: Optional. New description for the project.
            archived: Optional. Boolean indicating whether the project should be archived.
            days_to_thermometer: Optional. Number of days for the thermometer display.
            color: Optional. Color code for the project.
            name: Optional. New name for the project.
            follower_ids: Optional. List of user IDs who follow this project.
            show_thermometer: Optional. Boolean indicating whether to show the thermometer.
            team_id: Optional. ID of the team associated with this project.
            abbreviation: Optional. Short form abbreviation for the project.
        
        Returns:
            A dictionary containing the updated project information.
        
        Raises:
            ValueError: When project_public_id is None.
            HTTPError: When the API request fails.
        
        Tags:
            update, project, management, 
        """
        if project_public_id is None:
            raise ValueError("Missing required parameter 'project-public-id'")
        request_body = {
            'description': description,
            'archived': archived,
            'days_to_thermometer': days_to_thermometer,
            'color': color,
            'name': name,
            'follower_ids': follower_ids,
            'show_thermometer': show_thermometer,
            'team_id': team_id,
            'abbreviation': abbreviation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/projects/{project_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project(self, project_public_id) -> Any:
        """
        Deletes a project using its public ID.
        
        Args:
            project_public_id: The unique public identifier of the project to be deleted.
        
        Returns:
            The JSON response from the API after successful deletion.
        
        Raises:
            ValueError: Raised when the required project_public_id parameter is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).
        
        Tags:
            delete, project, management, 
        """
        if project_public_id is None:
            raise ValueError("Missing required parameter 'project-public-id'")
        url = f"{self.base_url}/api/v3/projects/{project_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_stories(self, project_public_id, includes_description=None) -> list[Any]:
        """
        Retrieves a list of stories for a specific project, with optional inclusion of story descriptions.
        
        Args:
            project_public_id: The public identifier of the project to list stories for.
            includes_description: Optional; If provided and truthy, includes the description of each story in the response.
        
        Returns:
            A list of story objects for the specified project, as returned by the API.
        
        Raises:
            ValueError: Raised if 'project_public_id' is not provided (None).
            HTTPError: Raised if the HTTP request to the stories API endpoint fails.
        
        Tags:
            list, stories, project, api, 
        """
        if project_public_id is None:
            raise ValueError("Missing required parameter 'project-public-id'")
        url = f"{self.base_url}/api/v3/projects/{project_public_id}/stories"
        query_params = {k: v for k, v in [('includes_description', includes_description)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_repositories(self, ) -> list[Any]:
        """
        Lists all repositories from the API.
        
        Returns:
            A list of repository objects containing repository metadata.
        
        Raises:
            HTTPError: If the HTTP request fails or returns an error status code.
        
        Tags:
            list, repositories, api, get, 
        """
        url = f"{self.base_url}/api/v3/repositories"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_repository(self, repo_public_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a repository by its public ID.
        
        Args:
            repo_public_id: String representing the public ID of the repository to retrieve.
        
        Returns:
            Dictionary containing repository information with string keys and values of various types.
        
        Raises:
            ValueError: When the required repo_public_id parameter is None.
            HTTPError: When the API request fails (via raise_for_status()).
        
        Tags:
            retrieve, repository, api, get, 
        """
        if repo_public_id is None:
            raise ValueError("Missing required parameter 'repo-public-id'")
        url = f"{self.base_url}/api/v3/repositories/{repo_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search(self, query, page_size=None, detail=None, next=None, entity_types=None) -> dict[str, Any]:
        """
        Performs a search operation based on the provided query string and optional parameters like page size and entity types.
        
        Args:
            query: The search query string. This is a required parameter.
            page_size: The number of results to return per page.
            detail: Optional detail parameter for search.
            next: The next page token for pagination.
            entity_types: List of entity types to filter results by.
        
        Returns:
            A JSON response from the search query as a dictionary.
        
        Raises:
            ValueError: Raised if the 'query' parameter is missing.
        
        Tags:
            search, management, 
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/api/v3/search"
        query_params = {k: v for k, v in [('query', query), ('page_size', page_size), ('detail', detail), ('next', next), ('entity_types', entity_types)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_epics(self, query, page_size=None, detail=None, next=None, entity_types=None) -> dict[str, Any]:
        """
        Searches for epics based on the provided query parameters.
        
        Args:
            query: String containing the search query for epics.
            page_size: Optional integer specifying the number of results to return per page.
            detail: Optional parameter determining the level of detail in the response.
            next: Optional parameter for pagination, used to fetch the next page of results.
            entity_types: Optional parameter to filter results by specific entity types.
        
        Returns:
            A dictionary containing the search results with various metadata and epic information.
        
        Raises:
            ValueError: Raised when the required 'query' parameter is None.
            HTTPError: Raised when the HTTP request fails (via raise_for_status()).
        
        Tags:
            search, epics, pagination, api, 
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/api/v3/search/epics"
        query_params = {k: v for k, v in [('query', query), ('page_size', page_size), ('detail', detail), ('next', next), ('entity_types', entity_types)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_iterations(self, query, page_size=None, detail=None, next=None, entity_types=None) -> dict[str, Any]:
        """
        Searches for iterations based on a query and additional parameters.
        
        Args:
            query: The search query string to find iterations. Required parameter.
            page_size: The number of results to return per page. Optional parameter.
            detail: The level of detail to include in the results. Optional parameter.
            next: Token for pagination to get the next page of results. Optional parameter.
            entity_types: Filter results by specific entity types. Optional parameter.
        
        Returns:
            A dictionary containing the search results including iteration data and pagination information.
        
        Raises:
            ValueError: Raised when the required 'query' parameter is None.
            HTTPError: Raised when the HTTP request fails.
        
        Tags:
            search, iterations, pagination, 
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/api/v3/search/iterations"
        query_params = {k: v for k, v in [('query', query), ('page_size', page_size), ('detail', detail), ('next', next), ('entity_types', entity_types)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_milestones(self, query, page_size=None, detail=None, next=None, entity_types=None) -> dict[str, Any]:
        """
        Searches for milestones matching the provided query and returns the results as a dictionary.
        
        Args:
            query: str. The search query used to match milestones. Required.
            page_size: Optional[int]. The maximum number of results to return per page.
            detail: Optional[str]. The level of detail to include in the results.
            next: Optional[str]. A token to retrieve the next page of results.
            entity_types: Optional[str|list[str]]. Filter milestones by specific entity types.
        
        Returns:
            dict[str, Any]: A dictionary containing the search results for milestones.
        
        Raises:
            ValueError: If the 'query' parameter is None.
            requests.HTTPError: If the HTTP request to the milestones API fails.
        
        Tags:
            search, milestones, api, async-job, management, 
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/api/v3/search/milestones"
        query_params = {k: v for k, v in [('query', query), ('page_size', page_size), ('detail', detail), ('next', next), ('entity_types', entity_types)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_objectives(self, query, page_size=None, detail=None, next=None, entity_types=None) -> dict[str, Any]:
        """
        Searches for objectives based on the specified query and returns the search results.
        
        Args:
            query: str. The search string to query objectives. This parameter is required.
            page_size: Optional[int]. The maximum number of results to return per page.
            detail: Optional[bool]. Whether to include detailed information in the results.
            next: Optional[str]. A token to retrieve the next page of results.
            entity_types: Optional[list[str] or str]. Specifies the types of entities to include in the search.
        
        Returns:
            dict[str, Any]: A dictionary containing the search results for objectives.
        
        Raises:
            ValueError: Raised if the required 'query' parameter is missing.
            HTTPError: Raised if the HTTP request to the search API returns an unsuccessful status code.
        
        Tags:
            search, objectives, api, 
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/api/v3/search/objectives"
        query_params = {k: v for k, v in [('query', query), ('page_size', page_size), ('detail', detail), ('next', next), ('entity_types', entity_types)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_stories(self, query, page_size=None, detail=None, next=None, entity_types=None) -> dict[str, Any]:
        """
        Searches for stories matching the given query and optional filters, returning paginated results from the stories API.
        
        Args:
            query: str. The search query string to filter stories. Required.
            page_size: Optional[int]. Maximum number of stories to return per page. Defaults to API settings if not provided.
            detail: Optional[Any]. Specifies the level of detail to include in the returned stories.
            next: Optional[str]. A token for fetching the next page of results.
            entity_types: Optional[Any]. Filter stories by specific entity types.
        
        Returns:
            dict[str, Any]: Parsed JSON response containing search results and pagination data.
        
        Raises:
            ValueError: If the required parameter 'query' is not provided.
            requests.HTTPError: If the HTTP request to the stories API fails with a non-success status code.
        
        Tags:
            search, stories, api, 
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/api/v3/search/stories"
        query_params = {k: v for k, v in [('query', query), ('page_size', page_size), ('detail', detail), ('next', next), ('entity_types', entity_types)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_story(self, name, description=None, archived=None, story_links=None, labels=None, story_type=None, custom_fields=None, move_to=None, file_ids=None, source_task_id=None, completed_at_override=None, comments=None, epic_id=None, story_template_id=None, external_links=None, sub_tasks=None, requested_by_id=None, iteration_id=None, tasks=None, started_at_override=None, group_id=None, workflow_state_id=None, updated_at=None, follower_ids=None, owner_ids=None, external_id=None, estimate=None, project_id=None, linked_file_ids=None, deadline=None, created_at=None) -> dict[str, Any]:
        """
        Creates a new story with the specified attributes and returns the created story's data.
        
        Args:
            name: str. The name or title of the story. This parameter is required.
            description: Optional[str]. The description or details of the story.
            archived: Optional[bool]. Indicates if the story is archived.
            story_links: Optional[list]. List of linked stories or references.
            labels: Optional[list]. List of label IDs or names to associate with the story.
            story_type: Optional[str]. The type of story (e.g., feature, bug, chore).
            custom_fields: Optional[dict]. Dictionary of custom field values for the story.
            move_to: Optional[str]. The workflow state to move the story to upon creation.
            file_ids: Optional[list]. IDs of files attached to the story.
            source_task_id: Optional[str]. The ID of the source task if the story is created from a task.
            completed_at_override: Optional[str]. Datetime string to override the completed timestamp.
            comments: Optional[list]. List of comments to add to the story upon creation.
            epic_id: Optional[str]. The ID of the epic to associate with the story.
            story_template_id: Optional[str]. The ID of the story template to use.
            external_links: Optional[list]. List of external links to associate with the story.
            sub_tasks: Optional[list]. List of sub-tasks for the story.
            requested_by_id: Optional[str]. ID of the user who requested the story.
            iteration_id: Optional[str]. The ID of the iteration associated with the story.
            tasks: Optional[list]. List of tasks linked to the story.
            started_at_override: Optional[str]. Datetime string to override the started timestamp.
            group_id: Optional[str]. The ID of the group associated with the story.
            workflow_state_id: Optional[str]. The workflow state ID for the story.
            updated_at: Optional[str]. Datetime string to override the updated timestamp.
            follower_ids: Optional[list]. IDs of users following the story.
            owner_ids: Optional[list]. IDs of users owning the story.
            external_id: Optional[str]. External reference ID for the story.
            estimate: Optional[int]. Estimated effort or points for the story.
            project_id: Optional[str]. The ID of the project this story belongs to.
            linked_file_ids: Optional[list]. IDs of files linked to the story.
            deadline: Optional[str]. Deadline datetime for the story.
            created_at: Optional[str]. Datetime string to override the created timestamp.
        
        Returns:
            dict[str, Any]: A dictionary representing the created story's data as returned by the API.
        
        Raises:
            ValueError: If the required parameter 'name' is not provided.
            requests.HTTPError: If the API request fails or returns an error response.
        
        Tags:
            create, story, api, management, 
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            'description': description,
            'archived': archived,
            'story_links': story_links,
            'labels': labels,
            'story_type': story_type,
            'custom_fields': custom_fields,
            'move_to': move_to,
            'file_ids': file_ids,
            'source_task_id': source_task_id,
            'completed_at_override': completed_at_override,
            'name': name,
            'comments': comments,
            'epic_id': epic_id,
            'story_template_id': story_template_id,
            'external_links': external_links,
            'sub_tasks': sub_tasks,
            'requested_by_id': requested_by_id,
            'iteration_id': iteration_id,
            'tasks': tasks,
            'started_at_override': started_at_override,
            'group_id': group_id,
            'workflow_state_id': workflow_state_id,
            'updated_at': updated_at,
            'follower_ids': follower_ids,
            'owner_ids': owner_ids,
            'external_id': external_id,
            'estimate': estimate,
            'project_id': project_id,
            'linked_file_ids': linked_file_ids,
            'deadline': deadline,
            'created_at': created_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_multiple_stories(self, story_ids, archived=None, story_type=None, move_to=None, follower_ids_add=None, epic_id=None, external_links=None, follower_ids_remove=None, requested_by_id=None, iteration_id=None, custom_fields_remove=None, labels_add=None, group_id=None, workflow_state_id=None, before_id=None, estimate=None, after_id=None, owner_ids_remove=None, custom_fields_add=None, project_id=None, labels_remove=None, deadline=None, owner_ids_add=None) -> list[Any]:
        """
        Updates multiple stories in bulk with various fields and configuration changes.
        
        Args:
            story_ids: List of story IDs to update. Must not be None.
            archived: Whether to archive the stories (optional).
            story_type: The type to assign to the stories (optional).
            move_to: Identifier to move stories to a different grouping, such as a workflow state (optional).
            follower_ids_add: List of follower IDs to add to the stories (optional).
            epic_id: Epic ID to associate the stories with (optional).
            external_links: List of external links to add to the stories (optional).
            follower_ids_remove: List of follower IDs to remove from the stories (optional).
            requested_by_id: ID of the user making the request (optional).
            iteration_id: Iteration ID to move the stories into (optional).
            custom_fields_remove: Custom field IDs to remove from the stories (optional).
            labels_add: List of label IDs to add to the stories (optional).
            group_id: Group ID to associate with the stories (optional).
            workflow_state_id: Workflow state ID to move the stories to (optional).
            before_id: ID of the story that the updated stories should be placed before (optional).
            estimate: Estimate value to set on the stories (optional).
            after_id: ID of the story that the updated stories should be placed after (optional).
            owner_ids_remove: List of owner IDs to remove from the stories (optional).
            custom_fields_add: Custom field values to add to the stories (optional).
            project_id: Project ID to associate the stories with (optional).
            labels_remove: List of label IDs to remove from the stories (optional).
            deadline: Deadline datetime to set for the stories (optional).
            owner_ids_add: List of owner IDs to add to the stories (optional).
        
        Returns:
            A list of story objects representing the updated stories.
        
        Raises:
            ValueError: If 'story_ids' is None.
            requests.HTTPError: If the HTTP request to update the stories fails.
        
        Tags:
            update, stories, bulk, management, api, 
        """
        if story_ids is None:
            raise ValueError("Missing required parameter 'story_ids'")
        request_body = {
            'archived': archived,
            'story_ids': story_ids,
            'story_type': story_type,
            'move_to': move_to,
            'follower_ids_add': follower_ids_add,
            'epic_id': epic_id,
            'external_links': external_links,
            'follower_ids_remove': follower_ids_remove,
            'requested_by_id': requested_by_id,
            'iteration_id': iteration_id,
            'custom_fields_remove': custom_fields_remove,
            'labels_add': labels_add,
            'group_id': group_id,
            'workflow_state_id': workflow_state_id,
            'before_id': before_id,
            'estimate': estimate,
            'after_id': after_id,
            'owner_ids_remove': owner_ids_remove,
            'custom_fields_add': custom_fields_add,
            'project_id': project_id,
            'labels_remove': labels_remove,
            'deadline': deadline,
            'owner_ids_add': owner_ids_add,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/bulk"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_multiple_stories(self, stories) -> list[Any]:
        """
        Creates multiple stories in bulk using the API.
        
        Args:
            stories: A list of story objects to be created in bulk.
        
        Returns:
            A list containing the created stories' data as returned by the API.
        
        Raises:
            ValueError: Raised when the required 'stories' parameter is None.
            HTTPError: Raised when the API request fails with a non-2xx status code.
        
        Tags:
            create, bulk, stories, api, 
        """
        if stories is None:
            raise ValueError("Missing required parameter 'stories'")
        request_body = {
            'stories': stories,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/bulk"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_story_from_template(self, story_template_id, description=None, archived=None, story_links=None, labels=None, external_links_add=None, story_type=None, custom_fields=None, move_to=None, file_ids=None, source_task_id=None, completed_at_override=None, name=None, file_ids_add=None, file_ids_remove=None, comments=None, follower_ids_add=None, epic_id=None, external_links=None, follower_ids_remove=None, sub_tasks=None, linked_file_ids_remove=None, requested_by_id=None, iteration_id=None, custom_fields_remove=None, tasks=None, started_at_override=None, labels_add=None, group_id=None, workflow_state_id=None, updated_at=None, follower_ids=None, owner_ids=None, external_id=None, estimate=None, owner_ids_remove=None, custom_fields_add=None, project_id=None, linked_file_ids_add=None, linked_file_ids=None, labels_remove=None, deadline=None, owner_ids_add=None, created_at=None, external_links_remove=None) -> dict[str, Any]:
        """
        Creates a new story from an existing story template.
        
        Args:
            story_template_id: The ID of the story template to use as a base for the new story. Required.
            description: The description of the story.
            archived: Whether the story is archived or not.
            story_links: Links to other stories.
            labels: Labels to associate with the story.
            external_links_add: External links to add to the story.
            story_type: The type of the story.
            custom_fields: Custom fields for the story.
            move_to: Position to move the story to.
            file_ids: IDs of files attached to the story.
            source_task_id: ID of the source task.
            completed_at_override: Override for the completion date.
            name: The name of the story.
            file_ids_add: File IDs to add to the story.
            file_ids_remove: File IDs to remove from the story.
            comments: Comments on the story.
            follower_ids_add: IDs of followers to add to the story.
            epic_id: ID of the epic this story belongs to.
            external_links: External links associated with the story.
            follower_ids_remove: IDs of followers to remove from the story.
            sub_tasks: Sub-tasks of the story.
            linked_file_ids_remove: IDs of linked files to remove.
            requested_by_id: ID of the user who requested the story.
            iteration_id: ID of the iteration this story belongs to.
            custom_fields_remove: Custom fields to remove from the story.
            tasks: Tasks associated with the story.
            started_at_override: Override for the start date.
            labels_add: Labels to add to the story.
            group_id: ID of the group this story belongs to.
            workflow_state_id: ID of the workflow state for this story.
            updated_at: Timestamp of when the story was last updated.
            follower_ids: IDs of users following this story.
            owner_ids: IDs of the story owners.
            external_id: External identifier for the story.
            estimate: Estimate value for the story.
            owner_ids_remove: IDs of owners to remove from the story.
            custom_fields_add: Custom fields to add to the story.
            project_id: ID of the project this story belongs to.
            linked_file_ids_add: IDs of linked files to add.
            linked_file_ids: IDs of files linked to the story.
            labels_remove: Labels to remove from the story.
            deadline: Deadline for the story.
            owner_ids_add: IDs of owners to add to the story.
            created_at: Timestamp of when the story was created.
            external_links_remove: External links to remove from the story.
        
        Returns:
            A dictionary containing the created story data.
        
        Raises:
            ValueError: Raised when the required parameter 'story_template_id' is None.
        
        Tags:
            create, template, story, 
        """
        if story_template_id is None:
            raise ValueError("Missing required parameter 'story_template_id'")
        request_body = {
            'description': description,
            'archived': archived,
            'story_links': story_links,
            'labels': labels,
            'external_links_add': external_links_add,
            'story_type': story_type,
            'custom_fields': custom_fields,
            'move_to': move_to,
            'file_ids': file_ids,
            'source_task_id': source_task_id,
            'completed_at_override': completed_at_override,
            'name': name,
            'file_ids_add': file_ids_add,
            'file_ids_remove': file_ids_remove,
            'comments': comments,
            'follower_ids_add': follower_ids_add,
            'epic_id': epic_id,
            'story_template_id': story_template_id,
            'external_links': external_links,
            'follower_ids_remove': follower_ids_remove,
            'sub_tasks': sub_tasks,
            'linked_file_ids_remove': linked_file_ids_remove,
            'requested_by_id': requested_by_id,
            'iteration_id': iteration_id,
            'custom_fields_remove': custom_fields_remove,
            'tasks': tasks,
            'started_at_override': started_at_override,
            'labels_add': labels_add,
            'group_id': group_id,
            'workflow_state_id': workflow_state_id,
            'updated_at': updated_at,
            'follower_ids': follower_ids,
            'owner_ids': owner_ids,
            'external_id': external_id,
            'estimate': estimate,
            'owner_ids_remove': owner_ids_remove,
            'custom_fields_add': custom_fields_add,
            'project_id': project_id,
            'linked_file_ids_add': linked_file_ids_add,
            'linked_file_ids': linked_file_ids,
            'labels_remove': labels_remove,
            'deadline': deadline,
            'owner_ids_add': owner_ids_add,
            'created_at': created_at,
            'external_links_remove': external_links_remove,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/from-template"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_stories_old(self, archived=None, owner_id=None, story_type=None, epic_ids=None, project_ids=None, updated_at_end=None, completed_at_end=None, workflow_state_types=None, deadline_end=None, created_at_start=None, epic_id=None, label_name=None, requested_by_id=None, iteration_id=None, label_ids=None, group_id=None, workflow_state_id=None, iteration_ids=None, created_at_end=None, deadline_start=None, group_ids=None, owner_ids=None, external_id=None, includes_description=None, estimate=None, project_id=None, completed_at_start=None, updated_at_start=None) -> list[Any]:
        """
        Searches for stories based on various filter criteria.
        
        Args:
            archived: Whether to include archived stories.
            owner_id: ID of the story owner.
            story_type: Type of story to search for.
            epic_ids: List of epic IDs.
            project_ids: List of project IDs.
            updated_at_end: End timestamp for story updates.
            completed_at_end: End timestamp for story completion.
            workflow_state_types: Types of workflow states.
            deadline_end: End deadline for stories.
            created_at_start: Start timestamp for story creation.
            epic_id: Single epic ID.
            label_name: Name of the label to filter by.
            requested_by_id: ID of the user who requested the story.
            iteration_id: Single iteration ID.
            label_ids: List of label IDs.
            group_id: Single group ID.
            workflow_state_id: Single workflow state ID.
            iteration_ids: List of iteration IDs.
            created_at_end: End timestamp for story creation.
            deadline_start: Start deadline for stories.
            group_ids: List of group IDs.
            owner_ids: List of owner IDs.
            external_id: External ID of the story.
            includes_description: Whether the story includes a description.
            estimate: Estimate of the story.
            project_id: Single project ID.
            completed_at_start: Start timestamp for story completion.
            updated_at_start: Start timestamp for story updates.
        
        Returns:
            A list of stories matching the specified criteria.
        
        Raises:
            HTTPError: Raised if the HTTP request to the API fails.
        
        Tags:
            search, story, management, 
        """
        request_body = {
            'archived': archived,
            'owner_id': owner_id,
            'story_type': story_type,
            'epic_ids': epic_ids,
            'project_ids': project_ids,
            'updated_at_end': updated_at_end,
            'completed_at_end': completed_at_end,
            'workflow_state_types': workflow_state_types,
            'deadline_end': deadline_end,
            'created_at_start': created_at_start,
            'epic_id': epic_id,
            'label_name': label_name,
            'requested_by_id': requested_by_id,
            'iteration_id': iteration_id,
            'label_ids': label_ids,
            'group_id': group_id,
            'workflow_state_id': workflow_state_id,
            'iteration_ids': iteration_ids,
            'created_at_end': created_at_end,
            'deadline_start': deadline_start,
            'group_ids': group_ids,
            'owner_ids': owner_ids,
            'external_id': external_id,
            'includes_description': includes_description,
            'estimate': estimate,
            'project_id': project_id,
            'completed_at_start': completed_at_start,
            'updated_at_start': updated_at_start,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/search"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_story(self, story_public_id) -> dict[str, Any]:
        """
        Retrieves a story from the API based on its public ID
        
        Args:
            story_public_id: The public ID of the story to fetch
        
        Returns:
            A dictionary containing the story data
        
        Raises:
            ValueError: Raised when the required 'story_public_id' parameter is missing
        
        Tags:
            fetch, story-management, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_story(self, story_public_id, description=None, archived=None, labels=None, pull_request_ids=None, story_type=None, custom_fields=None, move_to=None, file_ids=None, completed_at_override=None, name=None, epic_id=None, external_links=None, branch_ids=None, commit_ids=None, requested_by_id=None, iteration_id=None, started_at_override=None, group_id=None, workflow_state_id=None, follower_ids=None, owner_ids=None, before_id=None, estimate=None, after_id=None, project_id=None, linked_file_ids=None, deadline=None) -> dict[str, Any]:
        """
        Updates a story in the project management system with the specified attributes.
        
        Args:
            story_public_id: The unique identifier of the story to update.
            description: Optional description text for the story.
            archived: Optional boolean indicating whether the story is archived.
            labels: Optional list of labels to assign to the story.
            pull_request_ids: Optional list of associated pull request IDs.
            story_type: Optional type of the story (e.g., feature, bug, chore).
            custom_fields: Optional dictionary of custom field values.
            move_to: Optional location identifier to move the story to.
            file_ids: Optional list of file IDs to attach to the story.
            completed_at_override: Optional timestamp to override the completion date.
            name: Optional new name/title for the story.
            epic_id: Optional ID of the epic to associate this story with.
            external_links: Optional list of external links related to the story.
            branch_ids: Optional list of branch IDs associated with the story.
            commit_ids: Optional list of commit IDs associated with the story.
            requested_by_id: Optional ID of the user who requested the story.
            iteration_id: Optional ID of the iteration to assign this story to.
            started_at_override: Optional timestamp to override the start date.
            group_id: Optional ID of the group to assign this story to.
            workflow_state_id: Optional ID of the workflow state to assign.
            follower_ids: Optional list of user IDs to follow the story.
            owner_ids: Optional list of user IDs to own the story.
            before_id: Optional story ID to position this story before.
            estimate: Optional estimate value for the story.
            after_id: Optional story ID to position this story after.
            project_id: Optional ID of the project to move the story to.
            linked_file_ids: Optional list of linked file IDs.
            deadline: Optional deadline date for the story.
        
        Returns:
            A dictionary containing the updated story data from the API response.
        
        Raises:
            ValueError: When the required parameter 'story_public_id' is None.
            HTTPError: When the API request fails or returns an error status code.
        
        Tags:
            update, story, management, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        request_body = {
            'description': description,
            'archived': archived,
            'labels': labels,
            'pull_request_ids': pull_request_ids,
            'story_type': story_type,
            'custom_fields': custom_fields,
            'move_to': move_to,
            'file_ids': file_ids,
            'completed_at_override': completed_at_override,
            'name': name,
            'epic_id': epic_id,
            'external_links': external_links,
            'branch_ids': branch_ids,
            'commit_ids': commit_ids,
            'requested_by_id': requested_by_id,
            'iteration_id': iteration_id,
            'started_at_override': started_at_override,
            'group_id': group_id,
            'workflow_state_id': workflow_state_id,
            'follower_ids': follower_ids,
            'owner_ids': owner_ids,
            'before_id': before_id,
            'estimate': estimate,
            'after_id': after_id,
            'project_id': project_id,
            'linked_file_ids': linked_file_ids,
            'deadline': deadline,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/{story_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_story(self, story_public_id) -> Any:
        """
        Deletes a story using its public ID.
        
        Args:
            story_public_id: The public identifier of the story to be deleted.
        
        Returns:
            The JSON response from the API after successful deletion.
        
        Raises:
            ValueError: Raised when the required story_public_id parameter is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).
        
        Tags:
            delete, story, api, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_story_comment(self, story_public_id) -> list[Any]:
        """
        Retrieves a list of comments for a specific story.
        
        Args:
            story_public_id: The public identifier of the story for which to retrieve comments.
        
        Returns:
            A list of comment objects associated with the specified story.
        
        Raises:
            ValueError: When the required 'story_public_id' parameter is None.
            HTTPError: When the server returns an error response.
        
        Tags:
            list, retrieve, comments, story
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_story_comment(self, story_public_id, text, author_id=None, created_at=None, updated_at=None, external_id=None, parent_id=None) -> dict[str, Any]:
        """
        Creates a new comment on a story by sending a POST request with the comment details to the specified API endpoint.
        
        Args:
            story_public_id: The public ID of the story to which the comment is to be added.
            text: The content of the comment.
            author_id: Optional: The ID of the author of the comment.
            created_at: Optional: The timestamp when the comment was created.
            updated_at: Optional: The timestamp when the comment was last updated.
            external_id: Optional: An external identifier for the comment.
            parent_id: Optional: The ID of the parent comment if this is a reply.
        
        Returns:
            A dictionary containing the details of the newly created comment.
        
        Raises:
            ValueError: Raised if either 'story_public_id' or 'text' is missing.
        
        Tags:
            create, story-comment, async-job, management, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
            'author_id': author_id,
            'created_at': created_at,
            'updated_at': updated_at,
            'external_id': external_id,
            'parent_id': parent_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_story_comment(self, story_public_id, comment_public_id) -> dict[str, Any]:
        """
        Retrieves a specific comment from a story using the API.
        
        Args:
            story_public_id: The unique public identifier of the story containing the comment.
            comment_public_id: The unique public identifier of the comment to retrieve.
        
        Returns:
            A dictionary containing the comment data from the API response.
        
        Raises:
            ValueError: If story_public_id or comment_public_id is None.
            HTTPError: If the API request fails.
        
        Tags:
            retrieve, comment, story, api, get
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_story_comment(self, story_public_id, comment_public_id, text) -> dict[str, Any]:
        """
        Updates a story comment with new text based on the provided story and comment public IDs.
        
        Args:
            story_public_id: The public ID of the story the comment belongs to.
            comment_public_id: The public ID of the comment to be updated.
            text: The new text for the comment.
        
        Returns:
            A dictionary containing the updated comment data.
        
        Raises:
            ValueError: Raised when any of the required parameters (story_public_id, comment_public_id, or text) are missing.
        
        Tags:
            update, management, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_story_comment(self, story_public_id, comment_public_id) -> Any:
        """
        Deletes a specific comment from a story using the provided story and comment public IDs.
        
        Args:
            story_public_id: The public identifier of the story containing the comment to delete.
            comment_public_id: The public identifier of the comment to be deleted.
        
        Returns:
            A JSON object containing the server's response to the delete operation.
        
        Raises:
            ValueError: Raised if either 'story_public_id' or 'comment_public_id' is None.
            HTTPError: Raised if the HTTP request to delete the comment fails (non-success status code).
        
        Tags:
            delete, comment-management, api, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments/{comment_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_story_reaction(self, story_public_id, comment_public_id, emoji) -> list[Any]:
        """
        Creates a reaction with an emoji to a comment on a story.
        
        Args:
            story_public_id: Public ID of the story containing the comment to react to.
            comment_public_id: Public ID of the comment to add the reaction to.
            emoji: The emoji to use as the reaction.
        
        Returns:
            A list containing details of the created reaction.
        
        Raises:
            ValueError: If any of the required parameters (story_public_id, comment_public_id, or emoji) is None.
        
        Tags:
            create, reaction, comment, story, emoji, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        if emoji is None:
            raise ValueError("Missing required parameter 'emoji'")
        request_body = {
            'emoji': emoji,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments/{comment_public_id}/reactions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def unlink_comment_thread_from_slack(self, story_public_id, comment_public_id) -> dict[str, Any]:
        """
        Unlinks a comment thread from Slack for a specific story.
        
        Args:
            story_public_id: The public ID of the story containing the comment thread.
            comment_public_id: The public ID of the comment thread to unlink from Slack.
        
        Returns:
            A dictionary containing the API response data after unlinking the comment thread.
        
        Raises:
            ValueError: When either story_public_id or comment_public_id is None.
            HTTPError: When the API request fails.
        
        Tags:
            unlink, comment, slack, api, management, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if comment_public_id is None:
            raise ValueError("Missing required parameter 'comment-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/comments/{comment_public_id}/unlink-from-slack"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def story_history(self, story_public_id) -> list[Any]:
        """
        Retrieves the full change history for a specified story by its public ID.
        
        Args:
            story_public_id: The public identifier of the story whose history is to be fetched. Must not be None.
        
        Returns:
            A list of history records for the specified story, as returned from the API.
        
        Raises:
            ValueError: If 'story_public_id' is None.
            HTTPError: If the HTTP request to the history API fails or returns an unsuccessful status code.
        
        Tags:
            get, history, story, , api, management
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/history"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_task(self, story_public_id, description, complete=None, owner_ids=None, external_id=None, created_at=None, updated_at=None) -> dict[str, Any]:
        """
        Creates a task within a specified story.
        
        Args:
            story_public_id: The public identifier of the story to which the task will be added.
            description: The text description of the task.
            complete: Optional boolean indicating if the task is complete.
            owner_ids: Optional list of user IDs who own this task.
            external_id: Optional external identifier for the task.
            created_at: Optional timestamp when the task was created.
            updated_at: Optional timestamp when the task was last updated.
        
        Returns:
            Dictionary containing the created task data returned from the API.
        
        Raises:
            ValueError: Raised when required parameters 'story_public_id' or 'description' are None.
            HTTPError: Raised when the API request fails.
        
        Tags:
            create, task, story, api, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if description is None:
            raise ValueError("Missing required parameter 'description'")
        request_body = {
            'description': description,
            'complete': complete,
            'owner_ids': owner_ids,
            'external_id': external_id,
            'created_at': created_at,
            'updated_at': updated_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/tasks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_task(self, story_public_id, task_public_id) -> dict[str, Any]:
        """
        Gets task details for a specific task within a story.
        
        Args:
            story_public_id: The public identifier for the story containing the task.
            task_public_id: The public identifier for the task to retrieve.
        
        Returns:
            A dictionary containing the task details and metadata.
        
        Raises:
            ValueError: When either story_public_id or task_public_id is None.
            HTTPError: When the API request fails.
        
        Tags:
            get, retrieve, task, api, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if task_public_id is None:
            raise ValueError("Missing required parameter 'task-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/tasks/{task_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_task(self, story_public_id, task_public_id, description=None, owner_ids=None, complete=None, before_id=None, after_id=None) -> dict[str, Any]:
        """
        Updates the specified task within a story, modifying fields such as description, owners, completion status, and position.
        
        Args:
            story_public_id: The unique public identifier of the story containing the task.
            task_public_id: The unique public identifier of the task to update.
            description: Optional; the new description for the task.
            owner_ids: Optional; a list of user IDs to be set as owners of the task.
            complete: Optional; a boolean indicating whether the task is complete.
            before_id: Optional; the public ID of a task before which this task should be moved.
            after_id: Optional; the public ID of a task after which this task should be moved.
        
        Returns:
            A dictionary containing the updated task's data as returned by the API.
        
        Raises:
            ValueError: If either 'story_public_id' or 'task_public_id' is not provided.
            HTTPError: If the API response contains an HTTP error status.
        
        Tags:
            update, task-management, api, story, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if task_public_id is None:
            raise ValueError("Missing required parameter 'task-public-id'")
        request_body = {
            'description': description,
            'owner_ids': owner_ids,
            'complete': complete,
            'before_id': before_id,
            'after_id': after_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/tasks/{task_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_task(self, story_public_id, task_public_id) -> Any:
        """
        Deletes a task associated with a story based on their respective public IDs.
        
        Args:
            story_public_id: The public ID of the story containing the task
            task_public_id: The public ID of the task to be deleted
        
        Returns:
            JSON response from the server after the deletion operation
        
        Raises:
            ValueError: Raised if either 'story_public_id' or 'task_public_id' is None
        
        Tags:
            delete, task-management, story-management, 
        """
        if story_public_id is None:
            raise ValueError("Missing required parameter 'story-public-id'")
        if task_public_id is None:
            raise ValueError("Missing required parameter 'task-public-id'")
        url = f"{self.base_url}/api/v3/stories/{story_public_id}/tasks/{task_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_story_link(self, verb, subject_id, object_id) -> dict[str, Any]:
        """
        Creates a story link between a subject and an object with the specified verb by sending a POST request to the story-links API endpoint.
        
        Args:
            verb: str. Action describing the relationship between subject and object (e.g., 'like', 'comment', 'share').
            subject_id: Any. Unique identifier of the subject entity initiating the action.
            object_id: Any. Unique identifier of the object entity receiving the action.
        
        Returns:
            dict. The JSON response from the API as a dictionary containing details of the created story link.
        
        Raises:
            ValueError: If any of the required parameters ('verb', 'subject_id', or 'object_id') is None.
            requests.HTTPError: If the underlying HTTP request fails or the API response contains an error status code.
        
        Tags:
            create, story-link, api, management, 
        """
        if verb is None:
            raise ValueError("Missing required parameter 'verb'")
        if subject_id is None:
            raise ValueError("Missing required parameter 'subject_id'")
        if object_id is None:
            raise ValueError("Missing required parameter 'object_id'")
        request_body = {
            'verb': verb,
            'subject_id': subject_id,
            'object_id': object_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/story-links"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_story_link(self, story_link_public_id) -> dict[str, Any]:
        """
        Retrieves a specific story link by its public ID.
        
        Args:
            story_link_public_id: The unique public identifier for the story link to retrieve.
        
        Returns:
            A dictionary containing the story link data retrieved from the API.
        
        Raises:
            ValueError: If the story_link_public_id parameter is None.
            HTTPError: If the API request fails.
        
        Tags:
            retrieve, get, story-link, api, 
        """
        if story_link_public_id is None:
            raise ValueError("Missing required parameter 'story-link-public-id'")
        url = f"{self.base_url}/api/v3/story-links/{story_link_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_story_link(self, story_link_public_id, verb=None, subject_id=None, object_id=None) -> dict[str, Any]:
        """
        Updates an existing story link with new attributes.
        
        Args:
            story_link_public_id: The public ID of the story link to update.
            verb: Optional. The new verb to assign to the story link.
            subject_id: Optional. The new subject ID to assign to the story link.
            object_id: Optional. The new object ID to assign to the story link.
        
        Returns:
            A dictionary containing the updated story link data.
        
        Raises:
            ValueError: When the required story_link_public_id parameter is None.
            HTTPError: When the API request fails.
        
        Tags:
            update, story-link, api, 
        """
        if story_link_public_id is None:
            raise ValueError("Missing required parameter 'story-link-public-id'")
        request_body = {
            'verb': verb,
            'subject_id': subject_id,
            'object_id': object_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/api/v3/story-links/{story_link_public_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_story_link(self, story_link_public_id) -> Any:
        """
        Deletes a story link by its public ID.
        
        Args:
            story_link_public_id: The public ID of the story link to be deleted.
        
        Returns:
            JSON response containing the result of the deletion operation.
        
        Raises:
            ValueError: Raised when the required story_link_public_id parameter is None.
            HTTPError: Raised when the HTTP request fails or returns an error status code.
        
        Tags:
            delete, management, story-link, 
        """
        if story_link_public_id is None:
            raise ValueError("Missing required parameter 'story-link-public-id'")
        url = f"{self.base_url}/api/v3/story-links/{story_link_public_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_workflows(self, ) -> list[Any]:
        """
        Retrieves a list of available workflows from the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            list: A list of workflow objects parsed from the JSON response.
        
        Raises:
            HTTPError: If the HTTP request to the workflow API endpoint fails or returns an error status.
        
        Tags:
            list, workflows, api, management, 
        """
        url = f"{self.base_url}/api/v3/workflows"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_workflow(self, workflow_public_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a workflow given its public ID.
        
        Args:
            workflow_public_id: The public identifier of the workflow to retrieve.
        
        Returns:
            A dictionary containing the workflow details as returned by the API.
        
        Raises:
            ValueError: If 'workflow_public_id' is None.
            requests.HTTPError: If the HTTP request to the workflow API fails with an error status.
        
        Tags:
            get, workflow, api, management, 
        """
        if workflow_public_id is None:
            raise ValueError("Missing required parameter 'workflow-public-id'")
        url = f"{self.base_url}/api/v3/workflows/{workflow_public_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.list_categories,
            self.create_category,
            self.get_category,
            self.update_category,
            self.delete_category,
            self.list_category_milestones,
            self.list_category_objectives,
            self.list_custom_fields,
            self.get_custom_field,
            self.update_custom_field,
            self.delete_custom_field,
            self.list_entity_templates,
            self.create_entity_template,
            self.disable_story_templates,
            self.enable_story_templates,
            self.get_entity_template,
            self.update_entity_template,
            self.delete_entity_template,
            self.get_epic_workflow,
            self.list_epics,
            self.create_epic,
            self.get_epic,
            self.update_epic,
            self.delete_epic,
            self.list_epic_comments,
            self.create_epic_comment,
            self.get_epic_comment,
            self.update_epic_comment,
            self.create_epic_comment_comment,
            self.delete_epic_comment,
            self.list_epic_stories,
            self.unlink_productboard_from_epic,
            self.get_external_link_stories,
            self.list_files,
            self.get_file,
            self.update_file,
            self.delete_file,
            self.list_groups,
            self.create_group,
            self.get_group,
            self.update_group,
            self.list_group_stories,
            self.list_iterations,
            self.create_iteration,
            self.disable_iterations,
            self.enable_iterations,
            self.get_iteration,
            self.update_iteration,
            self.delete_iteration,
            self.list_iteration_stories,
            self.get_key_result,
            self.update_key_result,
            self.list_labels,
            self.create_label,
            self.get_label,
            self.update_label,
            self.delete_label,
            self.list_label_epics,
            self.list_label_stories,
            self.list_linked_files,
            self.create_linked_file,
            self.get_linked_file,
            self.update_linked_file,
            self.delete_linked_file,
            self.get_current_member_info,
            self.list_milestones,
            self.create_milestone,
            self.get_milestone,
            self.update_milestone,
            self.delete_milestone,
            self.list_milestone_epics,
            self.list_objectives,
            self.create_objective,
            self.get_objective,
            self.update_objective,
            self.delete_objective,
            self.list_objective_epics,
            self.list_projects,
            self.create_project,
            self.get_project,
            self.update_project,
            self.delete_project,
            self.list_stories,
            self.list_repositories,
            self.get_repository,
            self.search,
            self.search_epics,
            self.search_iterations,
            self.search_milestones,
            self.search_objectives,
            self.search_stories,
            self.create_story,
            self.update_multiple_stories,
            self.create_multiple_stories,
            self.create_story_from_template,
            self.search_stories_old,
            self.get_story,
            self.update_story,
            self.delete_story,
            self.list_story_comment,
            self.create_story_comment,
            self.get_story_comment,
            self.update_story_comment,
            self.delete_story_comment,
            self.create_story_reaction,
            self.unlink_comment_thread_from_slack,
            self.story_history,
            self.create_task,
            self.get_task,
            self.update_task,
            self.delete_task,
            self.create_story_link,
            self.get_story_link,
            self.update_story_link,
            self.delete_story_link,
            self.list_workflows,
            self.get_workflow
        ]
