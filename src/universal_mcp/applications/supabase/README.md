
# Supabase MCP Server

An MCP Server for the Supabase API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Supabase API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| v1_get_a_branch_config | Retrieves the configuration details for a specific branch by branch ID. |
| v1_update_a_branch_config | Updates the configuration of a specified branch by sending a PATCH request with provided configuration fields. |
| v1_delete_a_branch | Deletes a branch with the specified branch ID using a DELETE request to the API. |
| v1_reset_a_branch | Resets the specified branch by making a POST request to the branch reset endpoint. |
| v1_list_all_projects | Retrieves a list of all projects from the v1 API endpoint. |
| v1_create_a_project | Creates a new project with the specified configuration and returns the project details. |
| v1_list_all_organizations | Retrieves a list of all organizations from the API endpoint. |
| v1_create_an_organization | Creates a new organization using the provided name and returns the organization details. |
| v1_authorize_user | Initiates the OAuth 2.0 authorization flow by constructing and sending an authorization request to the identity provider. |
| v1_list_all_snippets | Retrieves all code snippets for the specified project, or for all projects if no project reference is provided. |
| v1_get_a_snippet | Retrieves a snippet resource by its unique identifier using a GET request to the v1 endpoint. |
| v1_get_project_api_keys | Retrieves the list of API keys associated with a specified project reference. |
| create_api_key | Creates a new API key for the specified project with optional description and secret JWT template. |
| update_api_key | Updates an existing API key identified by its project reference and key ID, allowing optional update of description and secret JWT template. |
| delete_api_key | Deletes an API key associated with a project using the provided reference and key ID. |
| v1_list_all_branches | Retrieves a list of all branches for the specified project reference using the v1 API. |
| v1_create_a_branch | Creates a new branch for a specified project, configuring options such as instance size, release channel, and region. |
| v1_disable_preview_branching | Disables preview branching for a specified project reference by sending a DELETE request to the corresponding API endpoint. |
| v1_get_hostname_config | Retrieves the configuration for a custom hostname associated with a given project reference. |
| v1_verify_dns_config | Triggers DNS configuration verification for a specified project reference via a POST request. |
| v1_activate_custom_hostname | Activates a custom hostname for the specified project reference using the v1 API endpoint. |
| v1_list_all_network_bans | Retrieves all network bans associated with the specified project reference. |
| v1_delete_network_bans | Deletes specified IPv4 addresses from the network ban list for a given project reference. |
| v1_get_network_restrictions | Retrieves network restriction settings for a given project reference. |
| v1_update_network_restrictions | Updates network access restrictions for the specified project by applying the given allowed IPv4 and IPv6 CIDR ranges. |
| v1_get_pgsodium_config | Retrieves the pgSodium configuration for a specified project reference from the v1 API endpoint. |
| v1_update_pgsodium_config | Updates the pgsodium configuration for a specified project reference using the provided root key. |
| v1_get_postgrest_service_config | Retrieves the configuration details for the PostgREST service associated with the specified project reference. |
| v1_update_postgrest_service_config | Updates the configuration settings for a PostgREST service for a specified project. |
| v1_delete_a_project | Deletes a project identified by its reference and returns the API response as a dictionary. |
| v1_list_all_secrets | Lists all secrets for the specified project reference via the v1 API. |
| v1_bulk_create_secrets | Creates multiple secrets for a specified project reference in a single batch request. |
| v1_bulk_delete_secrets | Deletes multiple secrets from a given project by making a bulk delete request. |
| v1_get_ssl_enforcement_config | Retrieves the SSL enforcement configuration for the specified project. |
| v1_update_ssl_enforcement_config | Updates the SSL enforcement configuration for the specified project reference. |
| v1_generate_typescript_types | Generates TypeScript type definitions for a specified project reference, optionally including specific schemas. |
| v1_get_vanity_subdomain_config | Retrieve the vanity subdomain configuration for a given project reference. |
| v1_deactivate_vanity_subdomain_config | Deactivates the vanity subdomain configuration for a specified project reference. |
| v1_check_vanity_subdomain_availability | Checks the availability of a specified vanity subdomain for a given project reference. |
| v1_activate_vanity_subdomain_config | Activates the vanity subdomain configuration for a specified project reference. |
| v1_upgrade_postgres_version | Initiates an upgrade of a PostgreSQL instance to a specified target version via API call. |
| v1_get_postgrest_upgrade_eligibility | Checks the eligibility of a PostgREST upgrade for a specified project reference. |
| v1_get_postgrest_upgrade_status | Retrieves the current upgrade status for a specified PostgREST project. |
| v1_get_readonly_mode_status | Retrieves the read-only mode status for a specified project reference. |
| v1_disable_readonly_mode_temporarily | Temporarily disables readonly mode for a specified project reference via a POST request. |
| v1_setup_a_read_replica | Initiates the setup of a read replica for a specified project in the given region. |
| v1_remove_a_read_replica | Removes a read replica from a specified database within a project. |
| v1_get_services_health | Checks the health status of specified services for a given project reference. |
| v1_get_postgres_config | Retrieves the PostgreSQL configuration for the specified project reference. |
| v1_update_postgres_config | Updates PostgreSQL configuration settings for a specified project via a REST API call. |
| v1_get_project_pgbouncer_config | Retrieves the PgBouncer configuration for a specific project by project reference. |
| v1_get_supavisor_config | Retrieves the Supavisor configuration for a specified project reference from the configured API. |
| v1_update_supavisor_config | Updates the Supavisor configuration for a specified project by modifying database pooler settings. |
| v1_get_auth_service_config | Retrieves the authentication service configuration for the specified project reference from the API. |
| v1_update_auth_service_config | Updates the authentication service configuration for a specified project with the provided settings. |
| create_tpafor_project | Creates a third-party authentication (TPA) configuration for a specific project using provided OIDC or JWKS details. |
| list_tpafor_project | Retrieves the list of third-party authentication configurations for a specified project. |
| delete_tpafor_project | Deletes a third-party authentication provider configuration for a given project. |
| get_tpafor_project | Retrieve the third-party authentication configuration for a specific project and TPA identifier. |
| v1_run_a_query | Executes a database query for a specified project reference using the provided query string. |
| v1_enable_database_webhook | Enables the database webhook for the specified project reference. |
| v1_list_all_functions | Lists all available functions for the specified project reference. |
| v1_get_a_function | Retrieves detailed information about a specific function from a project using the function's reference and slug. |
| v1_update_a_function | Updates the configuration or code for an existing function in the specified project. |
| v1_delete_a_function | Deletes a specified function from a project using its reference and function slug. |
| v1_get_a_function_body | Retrieves the body of a specified function from a project via a REST API call. |
| v1_list_all_buckets | Retrieves a list of all storage buckets for the specified project reference. |
| v1_create_a_sso_provider | Creates a new Single Sign-On (SSO) provider configuration for the specified project. |
| v1_list_all_sso_provider | Retrieves a list of all SSO providers configured for the specified project. |
| v1_get_a_sso_provider | Retrieves details of a specific SSO provider configuration for the given project reference and provider ID. |
| v1_update_a_sso_provider | Updates the configuration of an existing SSO provider using the provided metadata and attributes. |
| v1_delete_a_sso_provider | Deletes a specified SSO provider from the given project configuration. |
| v1_list_all_backups | Retrieves a list of all database backups for the specified project reference. |
| v1_restore_pitr_backup | Initiates a point-in-time restore operation for a database backup using the specified reference and recovery time target. |
| v1_list_organization_members | Retrieves a list of members associated with the specified organization slug via the v1 API. |
| v1_get_an_organization | Retrieves details of a specific organization by its unique slug identifier. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Supabase app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
