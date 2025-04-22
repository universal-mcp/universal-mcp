
# Amplitude MCP Server

An MCP Server for the Amplitude API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Amplitude API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| post_attribution | Sends an attribution event to the server using a POST request and returns the server's JSON response. |
| post_batch | Posts a batch request to the API. |
| get_cohorts | Retrieves a list of cohorts from the API. |
| get_cohorts_request_by_id | Retrieve the details of a cohort request by its unique identifier. |
| get_cohorts_request_status | Retrieves the status of a cohort request by request ID. |
| get_cohorts_request_file | Retrieves a file for a specific cohorts request based on the provided request ID. |
| post_cohorts_upload | Uploads cohorts to the specified endpoint. |
| post_cohorts_membership | Create or update cohort membership information by sending a POST request to the designated API endpoint. |
| post_dsar_requests | Submits a new DSAR (Data Subject Access Request) using the provided request body and returns the server's response as a dictionary. |
| get_dsar_requests_by_id | Retrieves DSAR requests by a specified ID from the API. |
| get_dsar_requests_output | Retrieves the output of a specific Data Subject Access Request (DSAR) by request and output ID from the remote API. |
| post_annotations | Sends a POST request to create a new annotation with the specified parameters in the target application. |
| get_annotations | Retrieves all annotation data from the API endpoint. |
| get_funnels | Retrieves funnel data from the server based on provided filter parameters. |
| get_retention | Fetches user retention statistics from the API with optional query filters. |
| get_user_activity | Retrieve a user's activity records from the server with optional filtering and pagination. |
| get_composition | Retrieve composition data from the API within an optional time range and/or filter. |
| get_users | Retrieves a list of users from the API, filtered by optional query parameters. |
| get_sessions_length | Retrieves session length data with optional time filtering and histogram configuration. |
| get_sessions_per_user | Retrieves the number of sessions per user within an optional time range. |
| get_sessions_average | Retrieve the average session metrics within an optional start and end date range. |
| get_user_search | Fetches user search data from the server based on an optional user identifier. |
| get_segmentation | Retrieve segmentation data from the API based on provided filter parameters. |
| get_events_list | Retrieves a list of events from the remote API. |
| get_chart_query | Retrieves the query details for a specific chart by its ID from the API. |
| get_base | Retrieves the base resource information from the API and returns it as a dictionary. |
| get_revenue_ltv | Retrieves lifetime value (LTV) revenue data for a specified period and set of filtering parameters. |
| get_event_streaming_delivery_metrics_summary | Retrieves a summary of event streaming delivery metrics for the specified sync and time period. |
| get_export | Retrieves export data from the API within an optional date range. |
| post_group_identify | Sends a POST request to the group identification API endpoint with optional authentication and identification parameters. |
| post_2_http_api | Sends a POST request to the /2/httpapi endpoint and returns the parsed JSON response. |
| post_identify | Sends a POST request to the '/identify' endpoint with the given request body and returns the parsed JSON response. |
| get_identify | Retrieve identification information from the API using the provided credentials. |
| get_lookup_table | Retrieves a lookup table from the API. |
| get_lookup_table_name | Retrieves the details of a lookup table by its name from the remote API. |
| post_lookup_table_name | Posts a new lookup table with the specified name and optional file data, returning the API response as a dictionary. |
| patch_lookup_table_name | Updates the name of a lookup table by sending a PATCH request with the specified parameters. |
| delete_lookup_table_name | Deletes a lookup table resource by its name from the remote API. |
| post_release | Sends a POST request to the release endpoint and returns the response data as a dictionary. |
| get_scim_1_users | Retrieves SCIM 1 users based on specified query parameters. |
| get_scim_1_users_id | Retrieves a SCIM user resource by user ID from the SCIM 1.0 API endpoint. |
| put_scim_1_users_id | Updates a SCIM user resource with the specified ID using the provided request body. |
| patch_scim_1_users_id | Partially updates a SCIM user resource identified by user ID using a PATCH request. |
| delete_scim_1_users_id | Deletes a SCIM user with the specified ID from the system. |
| post_scim_1_users | Creates a new SCIM user by sending a POST request to the SCIM 1.0 Users endpoint. |
| get_scim_1_groups | Fetches SCIM 1 groups from the Anthropic API. |
| post_scim_1_groups | Creates a new SCIM group by sending a POST request to the /scim/1/Groups endpoint. |
| get_scim_1_groups_id | Retrieves details of a SCIM 1 group by its unique identifier. |
| patch_scim_1_groups_id | Partially updates a SCIM group resource by its ID using a PATCH request. |
| delete_scim_1_groups_id | Deletes a SCIM group resource with the specified ID. |
| post_taxonomy_category | Creates a new taxonomy category by sending a POST request to the taxonomy API. |
| get_taxonomy_category | Retrieves the taxonomy category from the API. |
| get_taxonomy_category_category_name | Retrieves taxonomy category details for a given category name from the API. |
| put_taxonomy_category_category_id | Updates a taxonomy category specified by its category_id. |
| delete_taxonomy_category_category_id | Deletes a taxonomy category by its unique category ID. |
| post_taxonomy_event | Posts a taxonomy event to the server and returns the JSON response. |
| get_taxonomy_event | Retrieves taxonomy event data from the API endpoint. |
| get_taxonomy_event_event_type | Retrieves taxonomy details for a specific event type from the API. |
| put_taxonomy_event_event_type | Updates the event type in the taxonomy system by sending a PUT request with the provided request body. |
| delete_taxonomy_event_event_type | Deletes a taxonomy event identified by the given event type. |
| post_taxonomy_event_property | Creates a new taxonomy event property using the API. |
| get_taxonomy_event_property | Retrieves taxonomy event property data from the remote API endpoint. |
| post_taxonomy_user_property | Creates or updates a user property in the taxonomy via a POST request to the API. |
| get_taxonomy_user_property | Retrieves the user property taxonomy from the backend API. |
| get_taxonomy_user_property_user_property | Retrieves information about a user property from the taxonomy service. |
| put_taxonomy_user_property_user_property | Updates a user property in the taxonomy using the specified user property identifier and optional request body. |
| delete_taxonomy_user_property_user_property | Deletes a user property from the taxonomy via the API. |
| post_user_map | Posts a user map to the specified endpoint, optionally including a mapping and API key. |
| post_api_2_deletions_users | Submits a user deletion request to the API and returns the server's JSON response. |
| get_api_2_deletions_users | Retrieves user deletion information between a specified date range via the API endpoint '/api/2/deletions/users'. |
| delete_api_2_deletions_users_amplitude_id_or_user_id_date | Deletes user data from API 2 deletions endpoint using either Amplitude ID or user ID and a specific date. |
| get_v1_user_profile | Retrieves a user profile from the v1 API endpoint, optionally including recommendations or a specific recommendation ID. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Amplitude app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
