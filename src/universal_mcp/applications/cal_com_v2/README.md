
# Cal MCP Server

An MCP Server for the Cal API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Cal API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| cal_provider_controller_verify_client_id | Verifies the validity of the provided client ID by sending a GET request to the provider verification endpoint. |
| cal_provider_controller_verify_access_token | Verifies the validity of a provider's access token for the specified client ID by making an authenticated request to the provider API. |
| gcal_controller_redirect | Retrieves the Google Calendar OAuth authorization URL by making a GET request to the API and returns the response as a dictionary. |
| gcal_controller_save | Saves Google Calendar OAuth credentials by exchanging the provided state and code via an authenticated API request. |
| gcal_controller_check | Checks the connection status of Google Calendar integration via the API. |
| oauth_client_users_controller_get_managed_users | Retrieves a list of managed users for a specified OAuth client. |
| oauth_client_users_controller_create_user | Creates a new user for a specified OAuth client by sending user details to the OAuth service. |
| oauth_client_users_controller_get_user_by_id | Retrieves user information for a specific OAuth client and user ID. |
| oauth_client_users_controller_update_user | Updates a user's details for a specific OAuth client by sending a PATCH request with provided user information. |
| oauth_client_users_controller_delete_user | Deletes a specific user associated with an OAuth client by client and user ID. |
| oauth_client_users_controller_force_refresh | Forces a token refresh for a specific OAuth client user by issuing a POST request to the relevant API endpoint. |
| oauth_flow_controller_refresh_tokens | Requests a new access token using the provided client ID and refresh token through the OAuth flow. |
| oauth_client_webhooks_controller_create_oauth_client_webhook | Creates a new webhook for an OAuth client with the specified configuration parameters. |
| oauth_client_webhooks_controller_get_oauth_client_webhooks | Retrieves a list of webhook configurations associated with a specified OAuth client. |
| oauth_client_webhooks_controller_delete_all_oauth_client_webhooks | Deletes all OAuth client webhooks for the specified client ID. |
| oauth_client_webhooks_controller_update_oauth_client_webhook | Updates an existing OAuth client webhook with new configuration parameters. |
| oauth_client_webhooks_controller_get_oauth_client_webhook | Retrieves the details of a specific OAuth client webhook by client and webhook ID. |
| oauth_client_webhooks_controller_delete_oauth_client_webhook | Deletes a specific webhook associated with an OAuth client. |
| organizations_attributes_controller_get_organization_attributes | Retrieves the attributes of a specified organization using its organization ID, with optional pagination parameters. |
| organizations_attributes_controller_create_organization_attribute | Creates a new organization attribute by sending a POST request with the specified parameters to the organization's attributes endpoint. |
| organizations_attributes_controller_get_organization_attribute | Retrieves a specific attribute for an organization by organization and attribute IDs. |
| organizations_attributes_controller_update_organization_attribute | Updates a specific attribute of an organization using the provided parameters. |
| organizations_attributes_controller_delete_organization_attribute | Deletes an attribute from a specific organization by its organization ID and attribute ID. |
| organizations_options_attributes_controller_create_organization_attribute_option | Creates a new attribute option for a specific organization attribute. |
| organizations_options_attributes_controller_get_organization_attribute_options | Retrieves the available options for a specific organization attribute by organization and attribute IDs. |
| organizations_options_attributes_controller_delete_organization_attribute_option | Deletes a specific attribute option from an organization's attributes via the API. |
| organizations_options_attributes_controller_update_organization_attribute_option | Updates an existing organization attribute option with new values for 'value' and/or 'slug'. |
| organizations_options_attributes_controller_assign_organization_attribute_option_to_user | Assigns a specific organization attribute option to a user within the given organization. |
| organizations_options_attributes_controller_get_organization_attribute_options_for_user | Retrieves available attribute options for a user within a specified organization. |
| organizations_options_attributes_controller_unassign_organization_attribute_option_from_user | Unassigns a specific organization attribute option from a user within the given organization. |
| organizations_event_types_controller_create_team_event_type | Creates a new event type for a specified team within an organization. |
| organizations_event_types_controller_get_team_event_types | Retrieves the event types available for a specific team within an organization. |
| organizations_event_types_controller_get_team_event_type | Retrieves detailed information about a specific event type within a team for a given organization. |
| organizations_event_types_controller_create_phone_call | Creates a phone call event type for a specific organization, team, and event type using provided phone and template details. |
| organizations_event_types_controller_get_teams_event_types | Retrieves a list of event types associated with all teams in a specified organization. |
| organizations_memberships_controller_get_all_memberships | Retrieves all membership records for a specified organization, with optional pagination. |
| organizations_memberships_controller_create_membership | Creates a new organization membership by sending a POST request with the specified user ID, role, and optional parameters. |
| organizations_memberships_controller_get_org_membership | Retrieves the details of a specific organization membership by organization and membership IDs. |
| organizations_memberships_controller_delete_membership | Deletes a membership from an organization using the specified organization and membership IDs. |
| organizations_memberships_controller_update_membership | Updates an organization's membership with specified fields such as acceptance status, role, or impersonation settings. |
| organizations_schedules_controller_get_organization_schedules | Retrieves a paginated list of schedules for the specified organization. |
| organizations_schedules_controller_create_user_schedule | Creates a new user schedule for a specified user within an organization. |
| organizations_schedules_controller_get_user_schedules | Retrieves the schedule data for a specific user within an organization. |
| organizations_schedules_controller_get_user_schedule | Retrieves a specific user's schedule from an organization by schedule ID. |
| organizations_schedules_controller_update_user_schedule | Updates a user's schedule within an organization with the provided details. |
| organizations_schedules_controller_delete_user_schedule | Deletes a specific user schedule from an organization by schedule ID. |
| organizations_teams_controller_get_all_teams | Retrieves a list of teams for a specified organization, with optional pagination. |
| organizations_teams_controller_create_team | Creates a new team within the specified organization with customizable details and branding options. |
| organizations_teams_controller_get_my_teams | Retrieves the list of teams for the current user within a specified organization. |
| organizations_teams_controller_get_team | Retrieves detailed information about a specific team within an organization by team and organization ID. |
| organizations_teams_controller_delete_team | Deletes a specific team from an organization by its organization and team IDs. |
| organizations_teams_controller_update_team | Updates the details of an existing team in an organization with the specified parameters. |
| organizations_teams_memberships_controller_get_all_org_team_memberships | Retrieves all memberships for a specific team within an organization, with optional pagination. |
| organizations_teams_memberships_controller_create_org_team_membership | Creates a team membership for a user within an organization, assigning a specified role and optional attributes. |
| organizations_teams_memberships_controller_get_org_team_membership | Retrieve details of a specific team membership within an organization. |
| organizations_teams_memberships_controller_delete_org_team_membership | Deletes a specific team membership from an organization by its identifiers. |
| organizations_teams_memberships_controller_update_org_team_membership | Updates a specific team membership within an organization, modifying attributes such as acceptance status, role, and impersonation settings. |
| organizations_teams_schedules_controller_get_user_schedules | Retrieves the schedule information for a specific user within a team and organization. |
| organizations_users_controller_get_organizations_users | Retrieves a list of user information for a given organization, with optional filtering and pagination. |
| organizations_users_controller_create_organization_user | Creates a new user within a specified organization by sending a POST request with the provided user details. |
| organizations_users_controller_delete_organization_user | Deletes a user from the specified organization. |
| organizations_webhooks_controller_get_all_organization_webhooks | Retrieves all webhooks configured for the specified organization, with optional pagination. |
| organizations_webhooks_controller_create_organization_webhook | Creates a new webhook for an organization with specified parameters. |
| organizations_webhooks_controller_get_organization_webhook | Retrieves details for a specific webhook associated with an organization. |
| organizations_webhooks_controller_delete_webhook | Deletes a webhook from the specified organization by its webhook ID. |
| organizations_webhooks_controller_update_org_webhook | Updates an organization's webhook configuration. |
| bookings_controller_2024_08_13_get_bookings | Retrieves a list of bookings filtered by various query parameters such as status, attendee details, event type, team, and date ranges. |
| bookings_controller_2024_08_13_get_booking | Retrieves the details of a booking by its unique identifier. |
| bookings_controller_2024_08_13_reschedule_booking | Reschedules an existing booking by sending a reschedule request for the specified booking UID. |
| bookings_controller_2024_08_13_cancel_booking | Cancels an existing booking identified by the provided booking UID. |
| bookings_controller_2024_08_13_mark_no_show | Marks a booking as a no-show (absent) for the specified booking UID, optionally specifying host and attendee information. |
| bookings_controller_2024_08_13_reassign_booking | Reassigns an existing booking identified by its unique identifier. |
| bookings_controller_2024_08_13_reassign_booking_to_user | Reassigns a booking to a different user with an optional reason. |
| bookings_controller_2024_08_13_confirm_booking | Confirms a booking identified by its unique UID via a POST request to the bookings API. |
| bookings_controller_2024_08_13_decline_booking | Declines a booking identified by its unique UID, providing an optional reason for the decline. |
| calendars_controller_create_ics_feed | Creates or updates an ICS feed for multiple calendar URLs with optional read-only access. |
| calendars_controller_check_ics_feed | Checks the status and validity of the ICS calendar feed using the calendar service API. |
| calendars_controller_get_busy_times | Fetches the busy time slots from a calendar provider for a specified external calendar within an optional date range. |
| calendars_controller_get_calendars | Retrieves a list of available calendars from the API endpoint. |
| calendars_controller_redirect | Redirects to the calendar connection endpoint and returns the response as a dictionary. |
| calendars_controller_save | Saves the state of a specified calendar by sending a request to the API endpoint with given parameters. |
| calendars_controller_sync_credentials | Synchronizes calendar credentials by sending a POST request for the specified calendar. |
| calendars_controller_check | Checks the status or validity of a specified calendar by making a GET request to the corresponding API endpoint. |
| calendars_controller_delete_calendar_credentials | Disconnects and deletes calendar credentials for a specified calendar by sending a POST request to the external service. |
| conferencing_controller_connect | Connects to the conferencing service for the specified application and returns the response data. |
| conferencing_controller_redirect | Constructs and requests an OAuth conferencing redirect URL for the specified app, handling success and error redirects. |
| conferencing_controller_save | Handles an OAuth callback by sending the provided authorization code and state to the conferencing app's endpoint and returns the resulting authentication data. |
| conferencing_controller_list_installed_conferencing_apps | Retrieves a list of all installed conferencing applications from the conferencing API endpoint. |
| conferencing_controller_default | Retrieves the default conferencing configuration for a specified application. |
| conferencing_controller_get_default | Retrieves the default conferencing settings from the server. |
| conferencing_controller_disconnect | Disconnects an active conferencing session for the specified application. |
| destination_calendars_controller_update_destination_calendars | Updates destination calendar information using the provided integration and external ID. |
| event_types_controller_2024_06_14_get_event_types | Retrieves a list of event types from the API using optional filtering parameters. |
| event_types_controller_2024_06_14_get_event_type_by_id | Retrieves detailed information for a specific event type by its unique identifier. |
| event_types_controller_2024_06_14_delete_event_type | Deletes an event type specified by its ID from the event types resource. |
| event_type_webhooks_controller_create_event_type_webhook | Creates a new webhook for a specific event type, registering a subscriber endpoint to receive event notifications based on defined triggers. |
| event_type_webhooks_controller_get_event_type_webhooks | Retrieves a list of webhooks associated with a specific event type, supporting optional pagination. |
| event_type_webhooks_controller_delete_all_event_type_webhooks | Deletes all webhooks associated with a specific event type. |
| event_type_webhooks_controller_update_event_type_webhook | Updates an existing webhook for a specific event type with the provided parameters. |
| event_type_webhooks_controller_get_event_type_webhook | Retrieves details of a specific webhook configured for a given event type. |
| event_type_webhooks_controller_delete_event_type_webhook | Deletes a webhook associated with a specific event type by sending a DELETE request to the corresponding API endpoint. |
| me_controller_get_me | Retrieves the authenticated user's profile information from the API. |
| me_controller_update_me | Updates the current user's profile information with the provided fields. |
| schedules_controller_2024_06_11_create_schedule | Creates a new schedule with the specified name, time zone, and settings. |
| schedules_controller_2024_06_11_get_schedules | Retrieves the current list of schedules from the remote API. |
| schedules_controller_2024_06_11_get_default_schedule | Retrieves the default schedule configuration from the API. |
| schedules_controller_2024_06_11_get_schedule | Retrieves the details of a specific schedule by its ID. |
| schedules_controller_2024_06_11_update_schedule | Updates an existing schedule with new details such as name, time zone, availability, default status, or overrides. |
| schedules_controller_2024_06_11_delete_schedule | Deletes a schedule by its unique identifier. |
| selected_calendars_controller_add_selected_calendar | Adds a selected calendar to the user's account using the specified integration, external calendar ID, and credential ID. |
| selected_calendars_controller_remove_selected_calendar | Removes a selected calendar integration by sending a DELETE request with the provided identifiers. |
| slots_controller_reserve_slot | Reserves a timeslot for a specified event type and returns the reservation details. |
| slots_controller_delete_selected_slot | Deletes the selected slot identified by the given UID using a DELETE request to the slots API. |
| slots_controller_get_available_slots | Fetches available time slots for a specified event type between given start and end times, with optional filters such as users, duration, timezone, and organization. |
| stripe_controller_redirect | Initiates a redirect to the Stripe Connect endpoint and returns the response as a JSON dictionary. |
| stripe_controller_save | Saves the Stripe connection state and authorization code by making a request to the Stripe save endpoint. |
| stripe_controller_check | Checks the Stripe integration status by querying the Stripe check endpoint and returns the response as a dictionary. |
| stripe_controller_check_team_stripe_connection | Checks whether a Stripe connection exists for the specified team by making a GET request to the Stripe service endpoint. |
| teams_controller_create_team | Creates a new team with the specified attributes and returns the created team's details as a dictionary. |
| teams_controller_get_teams | Retrieves a list of teams from the API using a GET request. |
| teams_controller_get_team | Retrieves details about a specific team by its unique identifier. |
| teams_controller_update_team | Updates the details of an existing team with the provided attributes. |
| teams_controller_delete_team | Deletes a team by its unique identifier using an HTTP DELETE request. |
| teams_event_types_controller_create_team_event_type | Creates a new team event type by sending a POST request with the specified configuration parameters. |
| teams_event_types_controller_get_team_event_types | Retrieves event type details for a specified team, optionally filtering by event slug. |
| teams_event_types_controller_get_team_event_type | Retrieves details of a specific event type for a given team. |
| teams_event_types_controller_delete_team_event_type | Deletes an event type from a specified team using the given team and event type IDs. |
| teams_event_types_controller_create_phone_call | Creates a new phone call event type for a specific team and event type by sending a POST request with the provided call and template details. |
| teams_memberships_controller_create_team_membership | Creates a membership for a user in the specified team with optional role, acceptance, and impersonation settings. |
| teams_memberships_controller_get_team_memberships | Retrieves the list of team memberships for a specified team, supporting optional pagination. |
| teams_memberships_controller_get_team_membership | Retrieves a specific team membership's details by team and membership ID. |
| teams_memberships_controller_update_team_membership | Updates a team membership's properties, such as acceptance status, role, or impersonation settings, for a given team and membership ID. |
| teams_memberships_controller_delete_team_membership | Deletes a specific team membership by membership and team identifiers. |
| timezones_controller_get_time_zones | Retrieves the list of available time zones from the API. |
| webhooks_controller_create_webhook | Creates a new webhook subscription with the specified configuration. |
| webhooks_controller_get_webhooks | Retrieves a list of registered webhooks from the API with optional pagination parameters. |
| webhooks_controller_update_webhook | Updates the specified webhook's configuration with provided parameters. |
| webhooks_controller_get_webhook | Retrieves details of a specific webhook using its unique identifier. |
| webhooks_controller_delete_webhook | Deletes a webhook by its unique identifier. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Cal app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
