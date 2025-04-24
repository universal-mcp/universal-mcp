
# Falai MCP Server

An MCP Server for the Falai API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Falai API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| run | Run a Fal AI application directly and wait for the result. Suitable for short-running applications with synchronous execution from the caller's perspective. |
| submit | Submits a request to the Fal AI queue for asynchronous processing and returns a request ID for tracking the job. |
| status | Checks the status of a previously submitted Fal AI request and retrieves its current execution state |
| result | Retrieves the result of a completed Fal AI request, waiting for completion if the request is still running. |
| cancel | Asynchronously cancels a running or queued Fal AI request. |
| upload_file | Uploads a local file to the Fal CDN and returns its public URL |
| generate_image | Asynchronously generates images using the 'fal-ai/flux/dev' application with customizable parameters and default settings |


## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Falai app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
