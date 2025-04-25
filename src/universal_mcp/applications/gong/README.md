
# Gong MCP Server

An MCP Server for the Gong API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Gong API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| list_calls | Retrieves a list of call records within the specified date range, with optional pagination and workspace filtering. |
| add_call | Creates and submits a new call record with detailed metadata to the remote service. |
| get_call | Retrieves details for a specific call by its identifier. |
| list_calls_extensive | Retrieves a list of extensive call records matching the specified filter criteria, with optional pagination and content selection. |
| get_permission_profile | Retrieve the details of a permission profile by its profile ID. |
| update_permission_profile | Updates an existing permission profile with the specified access settings and permissions. |
| create_permission_profile | Creates a new permission profile in the specified workspace with customizable access and permission settings. |
| update_meeting | Updates the details of an existing meeting with new information such as time, invitees, and title. |
| delete_meeting | Deletes a meeting by its ID, optionally specifying the organizer's email. |
| content_viewed | Reports a content view event to the customer engagement system with detailed metadata about the event and content. |
| content_shared | Reports a content sharing event to the customer engagement system with detailed metadata about the shared content, sharer, and recipients. |
| custom_action | Submits a custom customer engagement action event with detailed reporting and context information to the server. |
| list_generic_crm_integration | Retrieves a list of generic CRM integrations from the API. |
| register_generic_crm_integration | Registers a generic CRM integration for a given owner email and integration name. |
| delete_generic_crm_integration | Deletes a generic CRM integration using the provided integration and client request IDs. |
| add_users_access_to_calls | Updates user access permissions for calls by sending a PUT request with the specified access list. |
| get_users_access_to_calls | Retrieves user access information for calls based on the provided filter criteria. |
| delete_users_access_to_calls | Deletes a list of users' access permissions to calls. |
| list_multiple_users | Retrieves a list of users based on a provided filter and optional pagination cursor. |
| list_interaction_stats | Retrieves interaction statistics based on specified filter criteria, with optional pagination support. |
| list_answered_scorecards | Retrieves a paginated list of answered scorecards based on the provided filter criteria. |
| list_multiple_users_day_by_day_activity | Retrieves day-by-day activity statistics for multiple users based on a provided filter. |
| list_multiple_users_aggregate_activity | Aggregates and returns activity statistics for multiple users based on specified filters. |
| list_multiple_users_aggregate_by_period | Aggregates activity statistics for multiple users over a specified period using given filter criteria. |
| add_meeting | Creates a new meeting with the specified details and returns the server's response as a dictionary. |
| integration_status | Retrieves the integration status for specified email addresses via the meetings API. |
| integration_settings | Sends integration type settings to the integration settings API endpoint and returns the server's response as a dictionary. |
| get_flows_for_prospects | Fetches flow data for the specified CRM prospect IDs from the API. |
| assign_prospects | Assigns a list of CRM prospect IDs to a specified flow instance and owner via an API POST request. |
| add_digital_interaction | Submits a digital interaction event record to the API with required metadata and content. |
| purge_phone_number | Erases all data associated with the specified phone number via the data privacy API. |
| purge_email_address | Permanently erases all data associated with the specified email address from the system. |
| list_crm_schema_fields | Retrieves the schema fields for a specified CRM object type associated with a given integration. |
| upload_crm_schema_field | Uploads CRM entity schema fields to the integration service for the specified CRM object type. |
| get_crm_objects | Retrieves CRM objects by their CRM IDs from a specified integration and object type. |
| get_call_transcripts | Retrieves call transcripts based on the specified filter and optional pagination cursor. |
| list_workspaces | Retrieves a list of all available workspaces from the API. |
| list_users | Retrieves a paginated list of users from the API, with optional filtering by cursor and inclusion of avatar data. |
| get_user | Retrieves user information by user ID from the API. |
| get_user_history | Retrieves the settings history for a specific user by user ID. |
| list_trackers | Retrieves a list of trackers for the specified workspace from the API. |
| list_scorecards | Retrieves a list of scorecard settings from the API. |
| list_permission_profile_users | Retrieves a list of users associated with a specified permission profile. |
| list_logs | Retrieves a list of logs for the specified log type and time range, with optional cursor-based pagination. |
| get_library_structure | Retrieves the hierarchical structure of library folders, optionally filtered by workspace ID. |
| get_calls_in_specific_folder | Retrieves the list of calls contained within a specified folder from the remote library API. |
| list_flows | Retrieves a list of flows owned by the specified user, with optional pagination and workspace filtering. |
| find_all_references_to_phone_number | Fetches all references to a specified phone number from the data privacy API. |
| find_all_references_to_email_address | Finds and returns all data references associated with a given email address. |
| get_request_status | Retrieves the status of a CRM request using the provided integration and client request IDs. |
| list_crmcalls_manual_association | Retrieves a list of manually associated CRM call records, with optional filtering by date and pagination. |
| list_permission_profile | Retrieves the list of permission profiles for the specified workspace. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Gong app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
