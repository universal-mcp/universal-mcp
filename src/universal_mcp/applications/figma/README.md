
# Figma MCP Server

An MCP Server for the Figma API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Figma API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| get_design | Retrieves the design data for a specified file key from the external API. |
| get_design_node | Retrieves specific design node data from a file using the provided file key and optional node IDs. |
| get_images | Retrieves the list of images associated with the specified file key from the remote service. |
| get_image_node | Retrieves image node data for a specified file key, optionally filtering by image IDs. |
| get_file_comments | Retrieves the list of comments associated with a specified file. |
| post_anew_comment | Posts a new comment to a file, or replies to an existing comment if a comment ID is provided. |
| get_team_projects | Retrieves the list of projects associated with a specified team. |
| get_project_files | Retrieves the list of files associated with the specified project. |
| create_variable_collection | Creates a new collection of variables for a specified file by sending a POST request to the server. |
| get_dev_resources | Retrieves development resources associated with a specific file key from the server. |
| post_dev_resource | Posts developer resource data to the remote API endpoint and returns the parsed JSON response. |
| get_library_analytics | Retrieves analytics usage data for a specific library file by its key. |
| get_actions_analytics | Retrieves analytics data about actions associated with a specified library file key. |
| get_all_webhooks_for_team | Retrieves all webhooks configured for the team by sending a GET request to the API. |
| add_webhook | Sends a POST request to register a new webhook and returns the response data. |
| delete_webhook | Deletes a webhook with the specified webhook ID from the service. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Figma app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
