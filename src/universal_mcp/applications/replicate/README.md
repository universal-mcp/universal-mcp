# Replicate MCP Server

An MCP Server for the Replicate API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Replicate API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| account_get | Gets information about the authenticated account. |
| collections_list | Lists collections of models available on Replicate, returning a paginated list of collection objects. |
| collections_get | Retrieves detailed information about a specific model collection, with automatic truncation of large model lists to manage response size. |
| deployments_list | Lists all deployments associated with the authenticated account. |
| deployments_create | Creates a new model deployment with specified configuration parameters. |
| deployments_get | Retrieves detailed information about a specific deployment by its owner and name. |
| deployments_update | Updates configurable properties of an existing deployment, such as hardware specifications and instance scaling parameters. |
| deployments_delete | Deletes a specified deployment associated with a given owner or organization |
| deployments_predictions_create | Creates an asynchronous prediction using a specified deployment, optionally configuring webhook notifications for status updates. |
| hardware_list | Retrieves a list of available hardware options for running models. |
| models_list | Retrieves a paginated list of publicly available models from the Replicate API. |
| models_create | Creates a new model in the system with specified parameters and metadata. |
| models_search | Searches for public models based on a provided query string |
| models_get | Retrieves detailed information about a specific AI model by its owner and name |
| models_delete | Deletes a private model from the system, provided it has no existing versions. |
| models_examples_list | Retrieves a list of example predictions associated with a specific model. |
| models_predictions_create | Creates an asynchronous prediction request using a specified model version. |
| models_readme_get | Retrieves the README content for a specified model in Markdown format. |
| models_versions_list | Lists all available versions of a specified model. |
| models_versions_get | Retrieves detailed information about a specific version of a model by querying the API. |
| models_versions_delete | Deletes a specific version of a model and its associated predictions/output. |
| trainings_create | Initiates a new asynchronous training job for a specific model version, with optional webhook notifications for progress updates. |
| predictions_list | Lists all predictions created by the authenticated account within an optional time range. |
| predictions_create | Creates an asynchronous prediction request using a specified model version. |
| predictions_get | Retrieves the current state and details of a prediction by its ID. |
| predictions_cancel | Cancels a running prediction job identified by its ID. |
| trainings_list | Lists all training jobs created by the authenticated account. |
| trainings_get | Retrieves the current state of a training job by its ID. |
| trainings_cancel | Cancels a specific training job in progress. |
| webhooks_default_secret_get | Retrieves the signing secret for the default webhook endpoint. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Replicate app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
