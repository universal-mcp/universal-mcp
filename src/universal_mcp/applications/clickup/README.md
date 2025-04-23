
# Clickup MCP Server

An MCP Server for the Clickup API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Clickup API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| authorization_get_access_token | Exchanges an authorization code for an access token using OAuth2 credentials. |
| authorization_view_account_details | Retrieves the current authenticated user's account details from the authorization service. |
| authorization_get_workspace_list | Retrieves a list of workspaces accessible to the authorized user from the authorization service. |
| task_checklists_create_new_checklist | Creates a new checklist for a given task and returns the created checklist details as a dictionary. |
| task_checklists_update_checklist | Updates a checklist's name and/or position by sending a PUT request to the checklist API endpoint. |
| task_checklists_remove_checklist | Removes a checklist by its ID using a DELETE request to the API. |
| task_checklists_add_line_item | Adds a new line item to a specified task checklist. |
| task_checklists_update_checklist_item | Updates a checklist item with new details such as name, assignee, resolution status, or parent within a specified checklist. |
| task_checklists_remove_checklist_item | Removes a specific checklist item from a checklist by issuing a DELETE request to the appropriate API endpoint. |
| comments_get_task_comments | Retrieve all comments associated with a specific task. |
| comments_create_new_task_comment | Creates a new comment on the specified task, assigning it to a user and controlling notification behavior. |
| comments_get_view_comments | Retrieve comments for a specific view, supporting optional pagination parameters. |
| comments_create_chat_view_comment | Creates a new comment on a chat view and optionally notifies all participants. |
| comments_get_list_comments | Retrieve a list of comments associated with a specific list, supporting optional pagination. |
| comments_add_to_list_comment | Adds a comment to a specified list, assigns it to a given user, and optionally notifies all stakeholders. |
| comments_update_task_comment | Updates an existing task comment with new text, assignee, and resolution status. |
| comments_delete_task_comment | Deletes a task comment by its ID. |
| custom_fields_get_list_fields | Retrieves a list of custom fields associated with a specified list by its ID. |
| custom_fields_remove_field_value | Removes a specific custom field value from a given task. |
| task_relationships_add_dependency | Adds a dependency relationship to a specified task, allowing you to define predecessor or dependent tasks within a project management system. |
| task_relationships_remove_dependency | Removes a dependency relationship between tasks by calling the API endpoint. |
| task_relationships_link_tasks | Links one task to another by creating a relationship between the source and target task IDs, with optional custom task and team identifiers. |
| task_relationships_remove_link_between_tasks | Removes a link between two specified tasks within the task management system. |
| folders_get_contents_of | Retrieves the contents of all folders within a specified space, with optional filtering for archived folders. |
| folders_create_new_folder | Creates a new folder within a specified space. |
| folders_get_folder_content | Retrieves the contents of a specified folder by its ID. |
| folders_rename_folder | Renames an existing folder by updating its name using the specified folder ID. |
| folders_remove_folder | Removes a folder with the specified folder ID by sending a DELETE request to the API. |
| goals_get_workspace_goals | Retrieves all workspace goals for a specified team, optionally including completed goals. |
| goals_add_new_goal_to_workspace | Adds a new goal to the specified team workspace. |
| goals_get_details | Retrieves detailed information about a goal based on the provided goal ID. |
| goals_update_goal_details | Updates the details of an existing goal with new information, including description, name, due date, owners, and color. |
| goals_remove_goal | Removes a goal from the system using the specified goal ID. |
| goals_add_key_result | Creates and adds a new key result to a specified goal with the provided details and associated tasks/lists. |
| goals_update_key_result | Updates the current number of steps and note for a specific key result. |
| goals_remove_target | Removes the target associated with a specified key result by sending a DELETE request to the API. |
| guests_invite_to_workspace | Invites a guest to a workspace with specific permissions. |
| guests_get_guest_information | Fetches guest information for a specific guest in a team. |
| guests_edit_guest_on_workspace | Edits a guest user's permissions and role within a specified workspace team. |
| guests_revoke_guest_access_to_workspace | Revokes a guest's access to a workspace for a specified team. |
| guests_add_to_task | Adds a guest to a task with specified permission level and optional parameters. |
| guests_revoke_access_to_task | Revokes a guest user's access to a specific task, with options to customize the revocation scope. |
| guests_share_list_with | Shares a list with a specified guest by assigning a permission level and optionally including shared items. |
| guests_remove_from_list | Removes a guest from a specified list, optionally including shared guests in the operation. |
| guests_add_guest_to_folder | Adds a guest to a specified folder with a given permission level, optionally including shared folders. |
| guests_revoke_access_from_folder | Revokes a guest's access from a specified folder, with optional inclusion of shared resources. |
| lists_get_folder_lists | Retrieves all lists contained within a specified folder, with optional filtering for archived lists. |
| lists_add_to_folder | Creates a new list in the specified folder with the given name and optional attributes. |
| lists_get_folderless | Retrieves all lists within the specified space that are not associated with a folder. |
| lists_create_folderless_list | Creates a new list within a specified space without associating it with a folder. |
| lists_get_list_details | Retrieves the details of a specific list by its unique identifier. |
| lists_update_list_info_due_date_priority_assignee_color | Updates the information of a list, including name, content, due date, priority, assignee, status, and color attributes. |
| lists_remove_list | Removes a list with the specified list ID via an HTTP DELETE request and returns the API response as a dictionary. |
| lists_add_task_to_list | Adds a task to a specified list. |
| lists_remove_task_from_list | Removes a specific task from a list by sending a DELETE request to the appropriate API endpoint. |
| members_get_task_access | Retrieves a list of members who have access to the specified task. |
| members_get_list_users | Retrieves the list of users who are members of the specified list. |
| roles_list_available_custom_roles | Retrieves a list of available custom roles for a specified team, optionally including role members. |
| shared_hierarchy_view_tasks_lists_folders | Retrieves the shared hierarchy view including tasks, lists, and folders for a specified team. |
| spaces_get_space_details | Retrieves details about spaces within a specified team, optionally filtering by archived status. |
| spaces_add_new_space_to_workspace | Creates a new space within a specified workspace team, configuring assignment settings and desired features. |
| spaces_get_details | Retrieves the details of a specified space by its unique identifier. |
| spaces_update_details_and_enable_click_apps | Updates the details of a specific space and enables click apps by sending a PUT request with the provided attributes. |
| spaces_remove_space | Removes a space identified by the given space_id. |
| tags_get_space | Retrieves all tags associated with a specific space by its unique identifier. |
| tags_create_space_tag | Creates a new tag for a specified space by sending a POST request to the space tag API endpoint. |
| tags_update_space_tag | Updates a tag for a specified space by sending a PUT request with the provided tag data. |
| tags_remove_space_tag | Removes a specified tag from a given space by tag name. |
| tags_add_to_task | Adds a tag to a specific task. |
| tags_remove_from_task | Removes a specific tag from a task by ID, with optional filtering by custom task IDs and team ID. |
| tasks_get_list_tasks | Retrieves a list of tasks from a specified list with optional filters such as archived status, pagination, sorting, subtask inclusion, status, assignees, tags, date ranges, and custom fields. |
| tasks_create_new_task | Creates a new task in the specified list with optional attributes including tags, assignees, status, priority, dates, and custom fields. |
| tasks_get_task_details | Retrieves detailed information about a specific task, with options to include subtasks, use custom task IDs, filter by team, and specify description formatting. |
| tasks_update_task_fields | Updates specified fields of an existing task with provided values. |
| tasks_remove_task_by_id | Removes a specific task by its unique task ID, optionally filtering by custom task IDs and team ID. |
| tasks_filter_team_tasks | Retrieves a filtered list of tasks assigned to a specific team, supporting various filtering options such as assignees, statuses, lists, projects, tags, due dates, custom fields, and more. |
| tasks_get_time_in_status | Retrieves the amount of time a specified task has spent in each status, with optional filters for custom task IDs and team ID. |
| tasks_get_time_in_status_bulk | Retrieves the time each specified task has spent in various statuses, in bulk, based on provided task identifiers. |
| task_templates_get_templates | Retrieves a paginated list of task templates for a given team. |
| task_templates_create_from_template | Creates a new task template instance in a specific list by cloning from an existing task template. |
| teams_workspaces_get_workspace_seats | Retrieves detailed seat allocation information for a specific workspace team. |
| teams_workspaces_get_workspace_plan | Retrieves the plan details for a workspace associated with the specified team. |
| teams_user_groups_create_team | Creates a new team user group with the specified name and members under the given team. |
| custom_task_types_get_available_task_types | Retrieves the available custom task types for a specified team. |
| teams_user_groups_update_user_group | Updates the attributes of a user group in the Teams system. |
| teams_user_groups_remove_group | Removes a user group from the Teams service by group ID. |
| teams_user_groups_get_user_groups | Retrieves user group information for a specified team and/or group IDs from the remote service. |
| time_tracking_legacy_get_tracked_time | Retrieves time tracking data for a specific task. |
| time_tracking_legacy_record_time_for_task | Records time for a task in the legacy system. |
| time_tracking_legacy_edit_time_tracked | Edits a tracked time interval for a specific task using legacy time tracking, updating start, end, and time values. |
| time_tracking_legacy_remove_tracked_time | Removes tracked time from a time-tracking interval associated with a specific task. |
| time_tracking_get_time_entries_within_date_range | Retrieves time entries for a specified team within an optional date range and optional filters such as assignee, tags, locations, spaces, folders, lists, or tasks. |
| time_tracking_create_time_entry | Creates a time tracking entry for a specified team. |
| time_tracking_get_single_time_entry | Retrieves a single time entry by team and timer ID. |
| time_tracking_remove_entry | Removes a specific time tracking entry for a team by deleting the corresponding timer record. |
| time_tracking_update_time_entry_details | Updates time entry details by sending a PUT request to the server. |
| time_tracking_get_time_entry_history | Retrieves the history of a specific time entry for a given team from the time tracking service. |
| time_tracking_get_current_time_entry | Retrieves the current time entry for a specified team, optionally filtered by assignee. |
| time_tracking_remove_tags_from_time_entries | Removes specified tags from multiple time entries for a given team. |
| time_tracking_get_all_tags_from_time_entries | Retrieves all tags associated with time entries for a specified team. |
| time_tracking_add_tags_from_time_entries | Adds tags to specified time entries for a team. |
| time_tracking_change_tag_names | Updates the name and visual properties of a time tracking tag for a specified team. |
| time_tracking_start_timer | Starts a new time tracking timer for a specified team and task with optional metadata such as tags, description, and billable status. |
| time_tracking_stop_time_entry | Stops the currently active time entry for the specified team. |
| users_invite_user_to_workspace | Invites a user to a workspace by sending an invitation to their email address. |
| users_get_user_details | Retrieves detailed information about a specific user within a given team. |
| users_update_user_details | Updates the details of a user in a specified team. |
| users_deactivate_from_workspace | Deactivates a user from the specified workspace (team) by sending a DELETE request to the API. |
| views_get_everything_level | Retrieves all view-level data for a specified team. |
| views_create_workspace_view_everything_level | Creates a new 'everything-level' view within a specified workspace team with custom configuration options. |
| views_space_views_get | Retrieves the view details for a specified space by its ID. |
| views_add_view_to_space | Creates a new view in the specified space with the given configuration parameters. |
| views_folder_views_get | Retrieves the views associated with a specified folder by its folder ID. |
| views_add_view_to_folder | Adds a new view to a specified folder with the provided configuration details. |
| views_get_list_views | Retrieves all views associated with the specified list. |
| views_add_view_to_list | Creates a new view for a specified list with the provided configuration and returns the resulting view data. |
| views_get_view_info | Retrieves detailed information about a specific view by its identifier. |
| views_update_view_details | Updates the details of an existing view with the specified parameters. |
| views_delete_view_by_id | Deletes a view by its ID. |
| views_get_tasks_in_view | Retrieves a paginated list of tasks associated with a specific view. |
| webhooks_workspace_get | Retrieves webhook configurations for a specified workspace team. |
| webhooks_create_webhook | Creates a webhook for a team by sending a POST request to the specified endpoint. |
| webhooks_update_events_to_monitor | Updates the monitored events, endpoint, and status for a specified webhook. |
| webhooks_remove_webhook_by_id | Removes a webhook by ID. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Clickup app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
