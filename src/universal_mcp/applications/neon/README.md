
# Neon MCP Server

An MCP Server for the Neon API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Neon API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| list_api_keys | Retrieves a list of API keys from the server associated with the current client. |
| create_api_key | Creates a new API key with the specified name. |
| revoke_api_key | Revokes an API key by its identifier. |
| get_project_operation | Retrieves details of a specific operation for a given project from the API. |
| list_projects | Retrieves a list of projects with optional pagination, filtering, and organizational scoping. |
| create_project | Creates a new project by sending a POST request to the projects endpoint with the given project details. |
| list_shared_projects | Retrieves a list of shared projects with optional pagination and search filtering. |
| get_project | Retrieves detailed information for a specific project by its project ID. |
| update_project | Updates an existing project with new information using a PATCH request. |
| delete_project | Deletes a project identified by the given project_id. |
| list_project_operations | Retrieves a paginated list of operations for a specified project. |
| list_project_permissions | Retrieves the permissions assigned to a specific project. |
| grant_permission_to_project | Grants a user permission to a specified project by sending a POST request with the user's email. |
| revoke_permission_from_project | Revokes a specific permission from a project by sending a DELETE request to the appropriate API endpoint. |
| get_project_jwks | Retrieves the JSON Web Key Set (JWKS) for a specified project from the server. |
| add_project_jwks | Adds a JWKS (JSON Web Key Set) provider to the specified project for authentication integration. |
| delete_project_jwks | Deletes a JSON Web Key Set (JWKS) associated with a specific project. |
| get_connection_uri | Retrieves the connection URI details for a specified database and role within a project. |
| get_project_branch | Retrieves details of a specific branch within a project by project and branch ID. |
| delete_project_branch | Deletes a specific branch from the given project using the API. |
| update_project_branch | Updates a branch in the specified project. |
| restore_project_branch | Restores a project branch from a given source branch, allowing optional point-in-time recovery and name preservation. |
| get_project_branch_schema | Retrieves the schema information for a specific project branch database, optionally at a given LSN or timestamp. |
| set_default_project_branch | Sets the specified branch as the default branch for a given project. |
| list_project_branch_endpoints | Retrieves a list of endpoint configurations for a specific branch within a project. |
| list_project_branch_databases | Retrieves a list of databases for a specific branch within a project. |
| create_project_branch_database | Creates a new database in the specified branch of a project and returns the resulting database object. |
| get_project_branch_database | Retrieves details of a specific database from a given project branch. |
| update_project_branch_database | Updates the specified database configuration for a given branch in a project. |
| delete_project_branch_database | Deletes a specific database from a project's branch and returns the response details. |
| list_project_branch_roles | Retrieve the list of roles associated with a specific branch in a given project. |
| create_project_branch_role | Creates a new role for a specific branch within a project and returns the created role information. |
| get_project_branch_role | Retrieves a specific role from a project branch. |
| delete_project_branch_role | Deletes a specific role from a branch within a project. |
| get_project_branch_role_password | Retrieves the revealed password for a specified role within a project branch. |
| reset_project_branch_role_password | Resets the password for a specific role in a project branch. |
| list_project_vpcendpoints | Retrieves a list of VPC endpoints associated with a specific project. |
| assign_project_vpcendpoint | Assigns a VPC endpoint to a project with a specified label and returns the server response. |
| delete_project_vpcendpoint | Deletes a VPC endpoint associated with a given project. |
| create_project_endpoint | Creates a new endpoint for the specified project by sending a POST request to the project endpoint API. |
| list_project_endpoints | Retrieves a list of API endpoints associated with a specified project. |
| get_project_endpoint | Retrieves the details of a specific endpoint within a project. |
| delete_project_endpoint | Deletes a specific endpoint from a given project. |
| update_project_endpoint | Updates the configuration of a specific endpoint within a project. |
| start_project_endpoint | Starts the specified endpoint for a given project by making a POST request to the API. |
| suspend_project_endpoint | Suspends a specific endpoint within a project by issuing a POST request to the suspend endpoint API. |
| restart_project_endpoint | Restarts a specific project endpoint by sending a POST request to the server. |
| get_organization | Retrieves the details of a specific organization using its unique organization ID. |
| revoke_org_api_key | Revokes an API key for a specific organization by sending a DELETE request. |
| get_organization_members | Retrieves the list of members belonging to a specified organization by organization ID. |
| get_organization_member | Retrieves information about a specific member within an organization by their identifiers. |
| update_organization_member | Updates the role of a specific member within an organization. |
| remove_organization_member | Removes a specified member from an organization. |
| get_organization_invitations | Retrieves the list of invitations for a specified organization. |
| create_organization_invitations | Creates new invitations for users to join an organization by sending a POST request to the organization's invitations endpoint. |
| list_organization_vpcendpoints | Retrieves a list of VPC endpoints for a specified organization and region. |
| get_organization_vpcendpoint_details | Retrieves details about a specific VPC endpoint for an organization in a given region. |
| assign_organization_vpcendpoint | Assigns a label to a specified organization VPC endpoint in a given region. |
| delete_organization_vpcendpoint | Deletes a specific VPC endpoint associated with an organization and region. |
| get_active_regions | Retrieves a list of active regions available in the system. |
| get_current_user_info | Retrieves information about the currently authenticated user from the API. |
| get_current_user_organizations | Retrieves a list of organizations associated with the current authenticated user. |
| transfer_projects_from_user_to_org | Transfers ownership of specified projects from the authenticated user to a target organization. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Neon app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
