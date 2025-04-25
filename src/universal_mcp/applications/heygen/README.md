
# Heygen MCP Server

An MCP Server for the Heygen API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Heygen API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| get_v1_voice_list | Retrieves the list of available voices from the v1 voice API endpoint. |
| get_v1_avatar_list | Retrieves a list of available avatars from the v1 API endpoint. |
| get_v2_voices | Retrieves the list of available v2 voices from the API endpoint. |
| get_v2_avatars | Retrieves a list of avatar objects from the /v2/avatars API endpoint. |
| get_v1_video_list | Retrieves a list of videos from the v1 API endpoint. |
| post_v2_video_generate | Submits a request to generate a video using specified input parameters via the v2 video generate API endpoint. |
| delete_v1_video | Deletes a video using the v1 API endpoint with the specified video ID. |
| get_v2_templates | Retrieves the list of v2 templates from the API endpoint. |
| get_v2_template_by_id | Retrieves a v2 template resource by its unique identifier. |
| post_v2_template_generate_by_id | Generates content from a template specified by ID using the provided title and variables, and returns the generation result. |
| get_v2_video_translate_target_languages | Retrieves the list of supported target languages for video translation via the v2 API. |
| post_v2_video_translate | Submits a video translation request and returns the API response as JSON. |
| get_v2_video_translate_status_by_id | Retrieves the status of a video translation job by its unique identifier. |
| post_streaming_new | Initiates a new streaming session with optional quality parameter and returns the server's JSON response. |
| get_streaming_list | Retrieves the list of available streaming resources from the remote API. |
| post_streaming_ice | Sends an ICE candidate for a streaming session to the server and returns the JSON response. |
| post_streaming_task | Submits a streaming task for the specified session and text input, returning the response from the remote API. |
| post_streaming_stop | Stops an ongoing streaming session by sending a stop request for the specified session ID. |
| post_streaming_interrupt | Sends a request to interrupt an active streaming session identified by the given session ID. |
| post_streaming_create_token | Creates a new streaming token with an optional expiry time by sending a POST request to the streaming token API endpoint. |
| get_streaming_avatar_list | Retrieves a list of available streaming avatars from the API endpoint. |
| get_v1_webhook_list | Retrieves a list of all registered webhooks via the v1 API endpoint. |
| post_v1_webhook_endpoint_add | Registers a new webhook endpoint with the specified URL and events. |
| delete_v1_webhook_endpoint_by_id | Deletes a webhook endpoint identified by its ID via a DELETE request to the v1 API. |
| get_v1_webhook_endpoint_list | Retrieves a list of webhook endpoints from the v1 API. |
| get_v1_talking_photo_list | Retrieves the list of talking photos from the v1 API endpoint. |
| delete_v2_talking_photo_by_id | Deletes a v2 talking photo resource identified by its unique ID. |
| post_personalized_video_add_contact | Adds a new contact to a personalized video project by sending the contact variables to the server. |
| get_personalized_video_audience_detail | Retrieves detailed information about a personalized video audience by ID. |
| get_personalized_video_project_detail | Retrieves the details of a personalized video project by its unique identifier. |
| get_v2_user_remaining_quota | Retrieves the current remaining quota information for the user from the v2 API endpoint. |
| post_v1_asset_upload | Uploads an asset to the server using a POST request to the '/v1/asset' endpoint. |
| get_v1_video_status | Retrieves the status of a video by making a GET request to the v1 video_status endpoint. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Heygen app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
