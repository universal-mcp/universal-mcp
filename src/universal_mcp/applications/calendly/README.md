
# Calendly MCP Server

An MCP Server for the Calendly API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Calendly API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| list_event_invitees | Retrieves a list of invitees for a specific scheduled event, optionally filtered and paginated by status, email, sorting order, and paging parameters. |
| get_event | Retrieves the details of a scheduled event given its UUID. |
| get_event_invitee | Retrieves details about a specific invitee for a given scheduled event. |
| list_events | Retrieves a list of scheduled events filtered by optional user, organization, invitee email, status, date range, sorting, and pagination criteria. |
| get_event_type | Retrieves the event type details for the specified UUID from the API. |
| list_user_sevent_types | Retrieves a list of user event types with optional filtering, sorting, and pagination parameters. |
| get_user | Retrieves detailed user information for a given UUID from the remote API. |
| get_current_user | Retrieves information about the currently authenticated user from the API. |
| list_organization_invitations | Retrieves a paginated list of invitations for a specified organization, with optional filtering and sorting. |
| invite_user_to_organization | Sends an invitation to a specified email address to join an organization identified by its UUID. |
| get_organization_invitation | Retrieves a specific invitation for an organization using its unique identifiers. |
| revoke_user_sorganization_invitation | Revokes a user's invitation to an organization by deleting the specified invitation resource. |
| get_organization_membership | Retrieves the membership information for a specified organization membership UUID. |
| remove_user_from_organization | Removes a user from the organization by deleting their membership using the specified UUID. |
| list_organization_memberships | Retrieves a list of organization memberships, optionally filtered by pagination, email, organization, or user parameters. |
| get_webhook_subscription | Retrieves the details of a webhook subscription identified by its UUID. |
| delete_webhook_subscription | Deletes a webhook subscription identified by its UUID. |
| list_webhook_subscriptions | Retrieves a list of webhook subscriptions, optionally filtered and paginated based on input criteria. |
| create_webhook_subscription | Creates a new webhook subscription with the specified parameters and returns the subscription details as a dictionary. |
| create_single_use_scheduling_link | Creates a single-use scheduling link by sending a POST request with optional restrictions. |
| delete_invitee_data | Deletes invitee data for the specified email addresses by sending a POST request to the data compliance API. |
| delete_scheduled_event_data | Deletes scheduled event data within the specified time range by sending a deletion request to the data compliance service. |
| get_invitee_no_show | Retrieves details about an invitee who did not show up for a scheduled event, identified by a unique UUID. |
| delete_invitee_no_show | Deletes an invitee no-show record identified by the given UUID. |
| create_invitee_no_show | Creates an invitee no-show record by sending a POST request to the invitee_no_shows endpoint. |
| get_group | Retrieves information for a group identified by its UUID from the server. |
| list_groups | Retrieves a list of groups from the API, optionally filtered by organization and paginated using a page token and count. |
| get_group_relationship | Retrieves the relationship information for a group specified by UUID from the API. |
| list_group_relationships | Retrieves a list of group relationships from the server, optionally filtered by pagination and various group ownership parameters. |
| get_routing_form | Retrieves a routing form by its unique identifier from the server. |
| list_routing_forms | Retrieves a paginated list of routing forms from the API, optionally filtered and sorted by organization, count, page token, or sort order. |
| get_routing_form_submission | Retrieves a routing form submission by its unique identifier (UUID) from the configured API endpoint. |
| list_routing_form_submissions | Retrieves a list of routing form submissions, optionally filtered and paginated based on provided parameters. |
| list_event_type_available_times | Retrieves available times for a specified event type within an optional date and time range. |
| list_activity_log_entries | Retrieves a list of activity log entries with optional filtering, sorting, and pagination. |
| create_share | Creates a new share with the specified configuration parameters by making a POST request to the shares API endpoint. |
| list_user_busy_times | Retrieves a list of busy time intervals for a specified user within an optional date range. |
| get_user_availability_schedule | Retrieves the availability schedule for a user identified by the given UUID. |
| list_user_availability_schedules | Retrieves a list of user availability schedules from the API, optionally filtering by a specific user. |
| list_event_type_hosts | Retrieves a list of event type hosts based on provided filter, count, and pagination parameters. |
| create_one_off_event_type | Creates a one-off event type with specified parameters and returns the created event type details. |
| get_sample_webhook_data | Retrieves sample webhook data from the API using optional filtering parameters. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Calendly app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
