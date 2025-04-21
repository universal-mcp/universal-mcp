
# Coda MCP Server

An MCP Server for the Coda API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Coda API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| list_categories | Retrieves a dictionary of available categories from the API endpoint. |
| list_docs | Retrieves a list of documents based on specified filtering and pagination criteria. |
| create_doc | Creates a new document with the specified properties and returns its metadata as a dictionary. |
| get_doc | Retrieves a document by its unique identifier from the remote service. |
| delete_doc | Deletes a document by its ID from the remote service. |
| update_doc | Updates the metadata of a document, such as its title and icon, using the provided document ID. |
| get_sharing_metadata | Retrieves sharing metadata for the specified document by its ID. |
| get_permissions | Retrieves the list of permissions for a specified document. |
| add_permission | Adds a permission entry for a specified document, granting access to a principal with defined access level. |
| delete_permission | Deletes a specific permission from a document by its identifier. |
| search_principals | Searches for principals in the access control list of a specified document, optionally filtering results by a query string. |
| get_acl_settings | Retrieves the access control settings for a specified document. |
| update_acl_settings | Updates access control settings for a specific document. |
| publish_doc | Publishes a document with the specified docId and optional publication settings. |
| unpublish_doc | Unpublishes a document by revoking its published status using the provided document ID. |
| list_pages | Retrieves a paginated list of pages for a specified document. |
| create_page | Creates a new page within a specified document and returns the page details. |
| get_page | Retrieves details of a specific page within a document by its ID or name. |
| update_page | Updates properties of a specific page within a document, sending changes to the server and returning the updated page data. |
| delete_page | Deletes a specific page from a document identified by docId and pageIdOrName. |
| begin_page_content_export | Initiates an export of a specific page's content from a document in the specified format. |
| get_page_content_export_status | Retrieves the export status of a specific page's content in a document by request ID. |
| list_tables | Retrieves a list of tables from a specified document with optional filtering, pagination, and sorting. |
| get_table | Retrieve table details from a document by table ID or name. |
| list_columns | Retrieves a list of columns for a specified table in a document, with optional filtering and pagination. |
| list_rows | Retrieves a list of rows from a specified table in a document, with optional filtering, sorting, and pagination. |
| upsert_rows | Upserts (inserts or updates) multiple rows in a specified table within a document. |
| delete_rows | Deletes specified rows from a table within a given document. |
| get_row | Retrieves a specific row from a table in a document using the provided identifiers. |
| update_row | Updates an existing row in a specified table within a document by sending the updated row data to the API. |
| delete_row | Deletes a specific row from a table in the given document. |
| push_button | Triggers a button action on a specified cell within a table row in a document and returns the result. |
| list_formulas | Retrieves a list of formulas for a specified document, supporting pagination and sorting options. |
| get_formula | Retrieves details of a specific formula from a document by formula ID or name. |
| list_controls | Retrieves a paginated list of controls associated with a specific document. |
| get_control | Retrieves details for a specific control in a document by its ID or name. |
| list_custom_doc_domains | Retrieve the list of custom domains associated with a specified document. |
| add_custom_doc_domain | Adds a custom document domain to a specified document. |
| delete_custom_doc_domain | Deletes a custom document domain for a specific document by sending a DELETE request to the API. |
| get_custom_doc_domain_provider | Retrieves provider information for a specified custom document domain. |
| whoami | Retrieves information about the current authenticated user from the API. |
| resolve_browser_link | Resolves a browser link for the provided URL, optionally degrading gracefully, and returns the server's JSON response. |
| get_mutation_status | Retrieves the mutation status for a given request ID. |
| trigger_webhook_automation | Triggers a webhook automation for the specified document and rule. |
| list_page_analytics | Retrieves analytics data for the pages of a specific document, supporting optional filtering and pagination. |
| list_doc_analytics_summary | Retrieves a summary of document analytics with optional filtering by publication status, date range, and workspace. |
| list_pack_analytics | Retrieves analytics data for specified content packs with optional filtering and pagination. |
| list_pack_analytics_summary | Retrieves a summary of analytics for one or more packs, optionally filtered by pack IDs, workspace, publication status, and date range. |
| list_pack_formula_analytics | Retrieves analytics data for formulas within a specified pack, supporting various filtering and pagination options. |
| get_analytics_last_updated | Retrieves the timestamp indicating when analytics data was last updated from the analytics API endpoint. |
| list_workspace_members | Lists members of the specified workspace, optionally filtered by roles and paginated. |
| change_user_role | Change the role of a user within a specific workspace. |
| list_workspace_role_activity | Retrieves activity details and permissions for all roles within a specified workspace. |
| list_packs | Retrieves a list of packs with optional filtering, sorting, and pagination parameters. |
| create_pack | Creates a new pack in the specified workspace, optionally cloning from an existing source pack. |
| get_pack | Retrieves the details of a specific pack by its ID from the API. |
| update_pack | Updates the properties of an existing pack using the specified parameters. |
| delete_pack | Deletes a pack by its unique identifier and returns the response from the server. |
| get_pack_configuration_schema | Retrieves the configuration schema for a given pack by its identifier. |
| list_pack_versions | Retrieves a paginated list of versions for the specified pack. |
| get_next_pack_version | Determines the next available version for a given pack based on proposed metadata and optional SDK version. |
| get_pack_version_diffs | Retrieves the differences between two specific versions of a given pack. |
| register_pack_version | Registers a new version of a pack with the given identifiers and bundle hash. |
| pack_version_upload_complete | Marks a pack version upload as complete and notifies the server with optional metadata. |
| create_pack_release | Creates a new release for the specified pack with the given version and optional release notes. |
| list_pack_releases | Retrieves a list of releases for a specified pack, supporting pagination. |
| update_pack_release | Updates the release information for a specific pack, including optional release notes. |
| set_pack_oauth_config | Configures or updates the OAuth settings for a specific pack by sending the provided client credentials and redirect URI to the server. |
| get_pack_oauth_config | Retrieves the OAuth configuration for a specific pack identified by packId. |
| set_pack_system_connection | Sets the system connection for a specified pack using provided credentials. |
| get_pack_system_connection | Retrieves the system connection information for a specified pack by its ID. |
| get_pack_permissions | Retrieves the permissions associated with the specified pack. |
| add_pack_permission | Adds a permission for a specified principal to a pack. |
| delete_pack_permission | Deletes a specific permission from a pack using the provided pack and permission IDs. |
| list_pack_makers | Retrieves a list of makers associated with the specified pack. |
| add_pack_maker | Adds a maker to a specified pack using the provided login ID. |
| delete_pack_maker | Deletes a maker from a specified pack using the provided pack and login IDs. |
| list_pack_categories | Retrieves the list of categories associated with a specific pack. |
| add_pack_category | Adds a new category to the specified pack by sending a POST request to the API. |
| delete_pack_category | Deletes a specific category from a pack by pack ID and category name. |
| upload_pack_asset | Uploads an asset file to the specified pack and returns the server response. |
| upload_pack_source_code | Uploads the source code for a specified pack by sending the provided file information and payload hash to the server. |
| pack_asset_upload_complete | Marks an asset upload as complete for a given pack and asset type by sending a POST request to the server. |
| pack_source_code_upload_complete | Marks the completion of a source code upload for a pack version by notifying the backend service. |
| get_pack_source_code | Retrieves the source code for a specified pack version from the server. |
| list_pack_listings | Retrieves a list of available pack listings based on specified filtering, sorting, and access control criteria. |
| get_pack_listing | Retrieves the listing details for a specified pack, optionally filtered by workspace, document, install context, or release channel. |
| list_pack_logs | Retrieves a paginated list of logs for a specified document in a pack, with advanced filtering and sorting options. |
| list_ingestion_logs | Retrieves a list of ingestion logs for a specified pack, organization, and root ingestion, with support for filtering and pagination. |
| list_grouped_pack_logs | Retrieves a paginated and filtered list of grouped logs for a specific pack and document. |
| list_grouped_ingestion_logs | Retrieves grouped ingestion log entries for a specified pack, organization, and root ingestion, supporting filtering and pagination options. |
| list_ingestion_executions | Retrieves a paginated list of ingestion execution records for a specified pack, organization, and root ingestion, with optional filtering and sorting parameters. |
| list_ingestion_execution_attempts | Lists execution attempts for a specific ingestion execution within a pack and organization. |
| get_pack_log_details | Retrieves detailed log information for a specific pack ingestion process by querying the remote service. |
| list_pack_featured_docs | Fetches the featured documents for a specified pack by its ID. |
| update_pack_featured_docs | Updates the featured documents for a specific pack by sending the provided items to the server. |
| add_go_link | Creates a new Go Link resource for the specified organization. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Coda app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
