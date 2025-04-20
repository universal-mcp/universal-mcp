
# Wrike MCP Server

An MCP Server for the Wrike API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Wrike API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| get_contacts | Retrieves a list of contacts from the server, with optional filtering and field selection. |
| get_contacts_by_contactid | Retrieves contact information for a specific contact ID, optionally returning only specified fields. |
| put_contacts_by_contactid | Updates an existing contact by contact ID with provided details such as metadata, billing and cost rates, job role, custom fields, or additional fields. |
| get_users_by_userid | Retrieves user information for a given user ID from the API endpoint. |
| put_users_by_userid | Updates a user's profile information by user ID using a PUT request. |
| get_groups | Retrieves a list of groups from the API, applying optional filtering and pagination parameters. |
| post_groups | Creates a new group with the specified title and optional details, sending a POST request to the groups endpoint. |
| get_groups_by_groupid | Retrieves details for a specific group by its group ID, optionally returning only specified fields. |
| put_groups_by_groupid | Updates an existing group identified by groupId with new properties and membership changes via a PUT request. |
| delete_groups_by_groupid | Deletes a group resource identified by the provided groupId using an HTTP DELETE request. |
| put_groups_bulk | Updates multiple group memberships in bulk by sending a PUT request with the given members data. |
| get_invitations | Retrieves all invitations from the server using a GET request. |
| post_invitations | Sends an invitation email to a user with optional details such as name, role, and custom message. |
| put_invitations_by_invitationid | Updates an existing invitation by invitation ID with optional fields such as resend, role, external, and user type ID. |
| delete_invitations_by_invitationid | Deletes an invitation specified by its invitation ID. |
| get_a_ccount | Retrieves account information from the API, optionally including only specified fields. |
| put_a_ccount | Sends a PUT request to update or create an account with the provided metadata and returns the server response as a JSON object. |
| get_workflows | Retrieves all workflows from the server using a GET request. |
| post_workflows | Creates a new workflow by sending a POST request to the workflows endpoint. |
| put_workflows_by_workflowid | Updates an existing workflow by workflow ID with optional name, hidden status, and request body data. |
| get_customfields | Retrieves all custom fields from the API and returns them as a parsed JSON object. |
| post_customfields | Creates a custom field by sending a POST request with the specified parameters to the customfields endpoint and returns the created field's data. |
| get_customfields_by_customfieldid | Retrieves details for a custom field by its unique identifier from the API. |
| put_customfields_by_customfieldid | Updates a custom field specified by its ID with the provided parameters using an HTTP PUT request. |
| delete_customfields_by_customfieldid | Deletes a custom field resource identified by its custom field ID. |
| get_folders | Retrieves a list of folders from the API, supporting extensive filtering, pagination, and field selection. |
| get_folders_by_folderid_folders | Retrieves subfolders of a specified folder, applying optional filters and pagination parameters. |
| post_folders_by_folderid_folders | Creates a new subfolder within a specified folder by folder ID, with configurable attributes such as title, description, sharing, metadata, and permissions. |
| delete_folders_by_folderid | Deletes a folder resource identified by its folder ID via an HTTP DELETE request. |
| put_folders_by_folderid | Updates a folder's properties and relationships by folder ID using a PUT request. |
| get_tasks | Retrieves tasks from the API with optional filtering, sorting, pagination, and field selection parameters. |
| get_tasks_by_taskid | Retrieves a task by its ID from the remote service, optionally returning only specified fields. |
| put_tasks_by_taskid | Updates the properties and relationships of a task specified by its ID, applying the given changes and returning the updated task data as a JSON object. |
| delete_tasks_by_taskid | Deletes a task identified by the given task ID via an HTTP DELETE request and returns the response as a JSON object. |
| post_folders_by_folderid_tasks | Creates a new task within a specified folder by folder ID, with configurable attributes such as title, description, status, importance, dates, assigned users, metadata, custom fields, and other options. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Wrike app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
