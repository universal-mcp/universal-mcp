
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
| get_contacts | Retrieves a list of contacts from the server, optionally filtering by deletion status, specific fields, or metadata. |
| get_contacts_by_contactid | Retrieves contact details by contact ID from the API, allowing optional selection of specific fields. |
| put_contacts_by_contactid | Updates a contact with the specified contact ID using the provided data. |
| get_users_by_userid | Retrieves user information for a given user ID using a GET request to the '/users/{userId}' endpoint. |
| put_users_by_userid | Updates a user resource identified by userId with the provided request body via an HTTP PUT request. |
| get_groups | Retrieves a list of groups from the API, applying optional filters and pagination parameters. |
| post_groups | Creates a new group by sending a POST request with the provided request body. |
| get_groups_by_groupid | Retrieves group information by group ID from the API, optionally including only specified fields. |
| put_groups_by_groupid | Updates a group's details by group ID using a PUT request and returns the server response as a JSON object. |
| delete_groups_by_groupid | Deletes a group by its unique group ID via an HTTP DELETE request and returns the server's JSON response. |
| put_groups_bulk | Sends a bulk update request for groups using a PUT HTTP request. |
| get_invitations | Retrieves a list of invitation objects from the server using a GET request. |
| post_invitations | Sends a POST request to create invitations using the given request body. |
| put_invitations_by_invitationid | Updates an invitation resource identified by invitationId with the provided request body using an HTTP PUT request. |
| delete_invitations_by_invitationid | Deletes an invitation identified by the given invitation ID. |
| get_a_ccount | Retrieves account information from the API, optionally filtering the fields returned. |
| put_a_ccount | Updates an account by sending a PUT request with the provided request body to the account endpoint. |
| get_workflows | Retrieves all workflows from the server as a JSON object. |
| post_workflows | Creates a new workflow by sending a POST request with optional name and request body. |
| put_workflows_by_workflowid | Updates a workflow's details by workflow ID using a PUT request. |
| get_customfields | Retrieves all custom fields from the API endpoint as a JSON object. |
| post_customfields | Creates a custom field by sending a POST request with the specified parameters and request body. |
| get_customfields_by_customfieldid | Retrieves the details of a custom field by its unique custom field ID. |
| put_customfields_by_customfieldid | Updates the properties of a custom field identified by its ID using the provided parameters. |
| delete_customfields_by_customfieldid | Deletes a custom field by its unique custom field ID. |
| get_folders | Retrieves a list of folders from the API, filtered by optional query parameters. |
| get_folders_by_folderid_folders | Retrieves a list of subfolders within a specified folder, applying optional filters such as metadata, custom fields, invitations, project, contract types, pagination, and response fields. |
| post_folders_by_folderid_folders | Creates a subfolder within a specified parent folder by sending a POST request with the provided request body. |
| delete_folders_by_folderid | Deletes a folder specified by its folder ID via an HTTP DELETE request. |
| put_folders_by_folderid | Updates a folder resource by its folder ID using the provided request body. |
| get_tasks | Retrieves a list of tasks from the server with optional filters and pagination parameters. |
| get_tasks_by_taskid | Retrieve detailed information about a specific task by its task ID from the remote API. |
| put_tasks_by_taskid | Updates a task by its task ID using a PUT request and returns the updated task data as JSON. |
| delete_tasks_by_taskid | Deletes a task identified by its task ID from the remote server and returns the server response. |
| post_folders_by_folderid_tasks | No documentation available |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Wrike app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
