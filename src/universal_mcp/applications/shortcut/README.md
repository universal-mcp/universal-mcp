
# Shortcut MCP Server

An MCP Server for the Shortcut API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Shortcut API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| list_categories | Retrieves a list of categories from the API. |
| create_category | Creates a new category with the specified parameters. |
| get_category | Fetches a category by its public ID. |
| update_category | Updates a category with the specified attributes. |
| delete_category | Deletes a category by its public ID. |
| list_category_milestones | Lists all milestones associated with a specified category. |
| list_category_objectives | Fetches and lists objectives for a given category based on its public ID. |
| list_custom_fields | Retrieves a list of custom fields from the API. |
| get_custom_field | Retrieves a custom field by its public ID. |
| update_custom_field | Updates an existing custom field's attributes with the provided values. |
| delete_custom_field | Deletes a custom field specified by its public identifier. |
| list_entity_templates | Retrieves a list of entity templates from an API endpoint. |
| create_entity_template | Creates an entity template with the provided name, story contents, and optional author ID. |
| disable_story_templates | Disables story entity templates by sending a PUT request to the API endpoint. |
| enable_story_templates | Enables story templates by making a PUT request to the entity-templates endpoint. |
| get_entity_template | Retrieves a specific entity template by its public ID. |
| update_entity_template | Updates an entity template using the provided public ID, optionally setting its name and story contents. |
| delete_entity_template | Deletes an entity template by its public ID. |
| get_epic_workflow | Retrieves the epic workflow configuration from the API. |
| list_epics | Fetches a list of epics from the API. |
| create_epic | Creates a new epic in the project management system with the specified properties. |
| get_epic | Fetches an epic by its public ID |
| update_epic | Updates an epic with the provided details. |
| delete_epic | Deletes an epic by its public ID. |
| list_epic_comments | Retrieves a list of comments for a specified epic. |
| create_epic_comment | Creates a comment on an epic with the specified details. |
| get_epic_comment | Retrieves a specific comment from an epic by their respective public IDs. |
| update_epic_comment | Updates the text of an existing comment on a specified epic. |
| create_epic_comment_comment | Creates a reply to an existing comment on a specified epic, sending the reply to the backend API and returning the created comment data. |
| delete_epic_comment | Deletes a specific comment from an epic using its public identifiers. |
| list_epic_stories | Retrieves a list of stories associated with a specific epic. |
| unlink_productboard_from_epic | Unlinks a ProductBoard integration from an epic in the system. |
| get_external_link_stories | Retrieves stories associated with an external link. |
| list_files | Retrieves a list of files from the remote API endpoint. |
| get_file | Retrieves a file based on its public ID, returning a dictionary containing file information. |
| update_file | Updates metadata for a file identified by its public ID. |
| delete_file | Deletes a file identified by a public ID from the server. |
| list_groups | Retrieves a list of all groups from the API. |
| create_group | Creates a new group with the specified configuration and returns the group's details. |
| get_group | Retrieves information about a specific group using its public ID. |
| update_group | Updates the properties of an existing group by its public ID. |
| list_group_stories | Retrieves a list of stories from a specific group. |
| list_iterations | Lists all available iterations from the API. |
| create_iteration | Creates a new iteration with the specified details and returns the server's response as a dictionary. |
| disable_iterations | Disables iterations by making a PUT request to the iterations API endpoint. |
| enable_iterations | Enable iterations for the API service. |
| get_iteration | Retrieves iteration details using the specified public ID. |
| update_iteration | Updates an existing iteration with the provided attributes. |
| delete_iteration | Deletes a specific iteration identified by its public ID. |
| list_iteration_stories | Retrieves a list of stories for a specified iteration, optionally including their descriptions. |
| get_key_result | Retrieves detailed information for a specific key result using its public identifier. |
| update_key_result | Updates a key result with the provided details. |
| list_labels | Fetches a list of labels from the API. |
| create_label | Creates a new label with the specified attributes. |
| get_label | Retrieves a label's details from the API using its public identifier. |
| update_label | Updates a label with the specified information. |
| delete_label | Deletes a label identified by its public ID via an HTTP DELETE request. |
| list_label_epics | Retrieves a list of epics associated with a specific label. |
| list_label_stories | Retrieves a list of stories associated with a specific label. |
| list_linked_files | Retrieve a list of all linked files. |
| create_linked_file | Creates a linked file with the specified attributes. |
| get_linked_file | Fetches details for a linked file by its public identifier. |
| update_linked_file | Updates a linked file with the specified parameters. |
| delete_linked_file | Deletes a linked file by its public ID using the API. |
| get_current_member_info | Retrieves information about the current authenticated member. |
| list_milestones | Lists milestones by fetching them from a specified API endpoint. |
| create_milestone | Creates a new milestone with the specified parameters. |
| get_milestone | Retrieves a milestone resource by its public identifier. |
| update_milestone | Updates the properties of an existing milestone with the given parameters. |
| delete_milestone | Deletes a milestone by its public ID. |
| list_milestone_epics | Retrieves a list of epics associated with a specified milestone. |
| list_objectives | Retrieves a list of all objectives from the API endpoint. |
| create_objective | Creates a new objective resource with the specified attributes and returns the created objective's data. |
| get_objective | Retrieves an objective by its public ID from the API. |
| update_objective | Updates an objective by its public ID with new values for fields such as description, archived status, completion and start timestamps, name, state, categories, and relative ordering. |
| delete_objective | Deletes an objective by its public ID using an HTTP DELETE request. |
| list_objective_epics | Retrieves a list of epics associated with a specific objective. |
| list_projects | Retrieves and lists all available projects from the API. |
| create_project | Creates a new project with the specified parameters. |
| get_project | Retrieves project information by its public ID. |
| update_project | Updates a project with the provided parameters. |
| delete_project | Deletes a project using its public ID. |
| list_stories | Retrieves a list of stories for a specific project, with optional inclusion of story descriptions. |
| list_repositories | Lists all repositories from the API. |
| get_repository | Retrieves detailed information about a repository by its public ID. |
| search | Performs a search operation based on the provided query string and optional parameters like page size and entity types. |
| search_epics | Searches for epics based on the provided query parameters. |
| search_iterations | Searches for iterations based on a query and additional parameters. |
| search_milestones | Searches for milestones matching the provided query and returns the results as a dictionary. |
| search_objectives | Searches for objectives based on the specified query and returns the search results. |
| search_stories | Searches for stories matching the given query and optional filters, returning paginated results from the stories API. |
| create_story | Creates a new story with the specified attributes and returns the created story's data. |
| update_multiple_stories | Updates multiple stories in bulk with various fields and configuration changes. |
| create_multiple_stories | Creates multiple stories in bulk using the API. |
| create_story_from_template | Creates a new story from an existing story template. |
| search_stories_old | Searches for stories based on various filter criteria. |
| get_story | Retrieves a story from the API based on its public ID |
| update_story | Updates a story in the project management system with the specified attributes. |
| delete_story | Deletes a story using its public ID. |
| list_story_comment | Retrieves a list of comments for a specific story. |
| create_story_comment | Creates a new comment on a story by sending a POST request with the comment details to the specified API endpoint. |
| get_story_comment | Retrieves a specific comment from a story using the API. |
| update_story_comment | Updates a story comment with new text based on the provided story and comment public IDs. |
| delete_story_comment | Deletes a specific comment from a story using the provided story and comment public IDs. |
| create_story_reaction | Creates a reaction with an emoji to a comment on a story. |
| unlink_comment_thread_from_slack | Unlinks a comment thread from Slack for a specific story. |
| story_history | Retrieves the full change history for a specified story by its public ID. |
| create_task | Creates a task within a specified story. |
| get_task | Gets task details for a specific task within a story. |
| update_task | Updates the specified task within a story, modifying fields such as description, owners, completion status, and position. |
| delete_task | Deletes a task associated with a story based on their respective public IDs. |
| create_story_link | Creates a story link between a subject and an object with the specified verb by sending a POST request to the story-links API endpoint. |
| get_story_link | Retrieves a specific story link by its public ID. |
| update_story_link | Updates an existing story link with new attributes. |
| delete_story_link | Deletes a story link by its public ID. |
| list_workflows | Retrieves a list of available workflows from the API. |
| get_workflow | Retrieves detailed information about a workflow given its public ID. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Shortcut app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
