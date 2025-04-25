from typing import Any, Literal

from loguru import logger

# Import the base APIApplication class
from universal_mcp.applications.application import APIApplication

# Import the Integration class
from universal_mcp.integrations import Integration


class ReplicateApp(APIApplication):
    """
    Application for interacting with the Replicate HTTP API.

    Exposes Replicate operations as tools, allowing interaction with models,
    predictions, trainings, deployments, etc.
    """

    def __init__(self, integration: Integration = None) -> None:
        """
        Initializes the ReplicateApp.

        Args:
            integration: The integration object providing authentication credentials.
                         Expected to provide a Replicate API token as 'api_key'.
        """
        # Call the parent constructor with the application name and integration
        super().__init__(name="replicate", integration=integration)

        # Set the base URL for the Replicate API (from the OpenAPI schema's servers section)
        self.base_url = "https://api.replicate.com/v1"
        logger.debug(f"ReplicateApp initialized with base_url: {self.base_url}")

    # --- Account Operations ---

    def account_get(self) -> dict[str, Any]:
        """
        Gets information about the authenticated account.

        Args:
            None: This function takes no parameters.

        Returns:
            Dict[str, Any]: A dictionary containing account details including type, username, name, and other account-related information.

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or other request-related problems

        Tags:
            account, get, read, api, authentication, important
        """
        url = f"{self.base_url}/account"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    # --- Collection Operations ---

    def collections_list(self) -> dict[str, Any]:
        """
        Lists collections of models available on Replicate, returning a paginated list of collection objects.

        Args:
            None: This function takes no arguments other than self

        Returns:
            A dictionary containing a paginated list of collection objects from the Replicate API

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code

        Tags:
            list, collections, read, api, important, fetch, models
        """
        url = f"{self.base_url}/collections"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def collections_get(self, collection_slug: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific model collection, with automatic truncation of large model lists to manage response size.

        Args:
            collection_slug: The unique identifier (slug) for the collection to retrieve (e.g., 'super-resolution')

        Returns:
            A dictionary containing collection details and its associated models. If the model list exceeds the truncation threshold (15), returns a modified dictionary with the model list replaced by a summary count and message.

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code
            RequestException: Raised when there's a network-related error during the API request

        Tags:
            get, read, collections, api, data-retrieval, important, truncation
        """
        url = f"{self.base_url}/collections/{collection_slug}"
        response = self._get(url)
        response.raise_for_status()
        collection_data = response.json()
        if "models" in collection_data and isinstance(collection_data["models"], list):
            original_model_count = len(collection_data["models"])

            # Define a threshold for truncation.
            # This is a heuristic value. You might need to adjust this number
            # based on how many model objects typically fit within your LLM's context,
            # considering the size of each model object description.
            TRUNCATION_THRESHOLD = 10  # Example: Truncate if more than 15 models

            if original_model_count > TRUNCATION_THRESHOLD:
                logger.warning(
                    f"Truncating model list for collection '{collection_slug}'. Found {original_model_count} models, exceeding threshold {TRUNCATION_THRESHOLD}."
                )

                # Create a new dictionary with essential collection data
                # and replace the 'models' list with a summary.
                truncated_data = {
                    k: v
                    for k, v in collection_data.items()
                    if k != "models"  # Exclude the full models list
                }
                # Add information about the models list being truncated
                truncated_data["model_count"] = original_model_count
                truncated_data["models"] = (
                    f"List of {original_model_count} models omitted due to size. Use models_get for details on individual models by owner/name."
                )
                # Optionally, include a small number of models as a preview, but this adds size.
                # For maximum reduction, just provide the count and message.
                # truncated_data['models_preview'] = collection_data['models'][:5] # Example: include first 5 models

                return truncated_data
            else:
                # If the list is not too large, return the full data
                return collection_data
        else:
            # If 'models' key is missing or not a list, return the data as is
            # (This handles cases where the structure is unexpected, or an error occurred before this point)
            return collection_data

    # --- Deployment Operations ---

    def deployments_list(self) -> dict[str, Any]:
        """
        Lists all deployments associated with the authenticated account.

        Args:
            None: This function takes no arguments.

        Returns:
            Dict[str, Any]: A dictionary containing a paginated list of deployment objects with deployment details and metadata.

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or API communication errors

        Tags:
            list, read, deployments, api, management, important
        """
        url = f"{self.base_url}/deployments"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def deployments_create(
        self,
        name: str,
        model: str,
        version: str,
        hardware: str,
        min_instances: int,
        max_instances: int,
    ) -> dict[str, Any]:
        """
        Creates a new model deployment with specified configuration parameters.

        Args:
            name: The name of the deployment
            model: The full name of the model (e.g., 'stability-ai/sdxl')
            version: The 64-character string ID of the model version
            hardware: The SKU for the hardware (e.g., 'gpu-t4')
            min_instances: The minimum number of instances, ranging from 0 to 5
            max_instances: The maximum number of instances, ranging from 0 to 20

        Returns:
            Dictionary containing the details of the newly created deployment

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code

        Tags:
            create, deployment, configuration, api, infrastructure, scaling, important
        """
        url = f"{self.base_url}/deployments"
        request_body = {
            "name": name,
            "model": model,
            "version": version,
            "hardware": hardware,
            "min_instances": min_instances,
            "max_instances": max_instances,
        }
        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    def deployments_get(
        self, deployment_owner: str, deployment_name: str
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific deployment by its owner and name.

        Args:
            deployment_owner: The owner's username or organization name associated with the deployment
            deployment_name: The unique name identifier of the deployment

        Returns:
            A dictionary containing detailed information about the requested deployment

        Raises:
            HTTPError: When the HTTP request fails or returns a non-200 status code

        Tags:
            get, read, deployments, api, fetch, important
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def deployments_update(
        self,
        deployment_owner: str,
        deployment_name: str,
        hardware: str = None,
        max_instances: int = None,
        min_instances: int = None,
        version: str = None,
    ) -> dict[str, Any]:
        """
        Updates configurable properties of an existing deployment, such as hardware specifications and instance scaling parameters.

        Args:
            deployment_owner: The owner's username or organization name
            deployment_name: The name of the deployment to be updated
            hardware: Optional. The new SKU for the hardware specification
            max_instances: Optional. The new maximum number of instances for scaling
            min_instances: Optional. The new minimum number of instances for scaling
            version: Optional. The new ID of the model version to deploy

        Returns:
            Dictionary containing the updated deployment configuration details or a message if no updates were provided

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            update, deployments, configuration, scaling, management, important
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}"
        update_data = {
            "hardware": hardware,
            "max_instances": max_instances,
            "min_instances": min_instances,
            "version": version,
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if not update_data:
            return {"message": "No update parameters provided."}
        response = self._patch(url, data=update_data)
        response.raise_for_status()
        return response.json()

    def deployments_delete(self, deployment_owner: str, deployment_name: str) -> str:
        """
        Deletes a specified deployment associated with a given owner or organization

        Args:
            deployment_owner: The username or organization name that owns the deployment
            deployment_name: The unique identifier/name of the deployment to be deleted

        Returns:
            A string containing a success message confirming the deployment deletion

        Raises:
            HTTPError: If the deletion request fails due to server error, invalid permissions, deployment being in use, or deployment not found

        Tags:
            delete, deployments, management, important, infrastructure, resource-management
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}"
        response = self._delete(url)
        response.raise_for_status()
        return f"Deployment '{deployment_owner}/{deployment_name}' deleted successfully."  # Assuming 204 No Content

    # --- Deployments Predictions Operations ---
    # Note: The 'Prefer: wait' header is not directly supported by default _post.
    # The response will likely be 201 or 202, requiring polling via predictions_get.

    def deployments_predictions_create(
        self,
        deployment_owner: str,
        deployment_name: str,
        input: dict[str, Any],
        stream: bool = None,  # Deprecated according to schema
        webhook: str = None,
        webhook_events_filter: list[
            Literal["start", "output", "logs", "completed"]
        ] = None,
    ) -> dict[str, Any]:
        """
        Creates an asynchronous prediction using a specified deployment, optionally configuring webhook notifications for status updates.

        Args:
            deployment_owner: The owner's username or organization name of the deployment
            deployment_name: The name of the deployment to use for prediction
            input: Dictionary containing the model's input data as a JSON-serializable object
            stream: Deprecated parameter for requesting streaming output URL
            webhook: HTTPS URL where prediction status updates will be sent
            webhook_events_filter: List of specific events to trigger webhook notifications ('start', 'output', 'logs', 'completed')

        Returns:
            Dictionary containing the initial prediction state, including a prediction ID for status polling

        Raises:
            HTTPError: When the API request fails or returns an error status code
            JSONDecodeError: When the API response contains invalid JSON

        Tags:
            create, predict, async, deployments, webhook, http-request, important
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}/predictions"
        request_body = {
            "input": input,
            "stream": stream,  # Included for completeness, though deprecated
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    # --- Hardware Operations ---

    def hardware_list(self) -> list[dict[str, Any]]:
        """
        Retrieves a list of available hardware options for running models.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a hardware option containing 'name' and 'sku' keys.

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code

        Tags:
            list, hardware, read, api, configuration, important
        """
        url = f"{self.base_url}/hardware"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    # --- Model Operations ---

    def models_list(self) -> dict[str, Any]:
        """
        Retrieves a paginated list of publicly available models from the Replicate API.

        Returns:
            Dict[str, Any]: A dictionary containing the paginated list of model objects with their metadata and configurations.

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or other request-related problems

        Tags:
            list, models, read, api, fetch, important
        """
        url = f"{self.base_url}/models"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_create(
        self,
        owner: str,
        name: str,
        visibility: Literal["public", "private"],
        hardware: str,
        cover_image_url: str = None,
        description: str = None,
        github_url: str = None,
        license_url: str = None,
        paper_url: str = None,
    ) -> dict[str, Any]:
        """
        Creates a new model in the system with specified parameters and metadata.

        Args:
            owner: The username or organization name that will own the model
            name: The name of the model (must be unique for the owner)
            visibility: Visibility setting for the model ('public' or 'private')
            hardware: The SKU for the hardware requirements
            cover_image_url: Optional URL for the model's cover image
            description: Optional text description of the model
            github_url: Optional URL for the model's source code repository
            license_url: Optional URL for the model's license documentation
            paper_url: Optional URL for the associated research paper

        Returns:
            Dictionary containing the details and metadata of the newly created model

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            create, models, management, api, important
        """
        url = f"{self.base_url}/models"
        request_body = {
            "owner": owner,
            "name": name,
            "visibility": visibility,
            "hardware": hardware,
            "cover_image_url": cover_image_url,
            "description": description,
            "github_url": github_url,
            "license_url": license_url,
            "paper_url": paper_url,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    def models_search(self, query: str) -> dict[str, Any]:
        """
        Searches for public models based on a provided query string

        Args:
            query: A string containing the search query to filter models

        Returns:
            A dictionary containing paginated search results with matching model objects

        Raises:
            Exception: When the HTTP request fails or encounters network/server errors
            HTTPStatusError: When the API returns a non-successful status code

        Tags:
            search, models, query, read, api, http, important
        """
        url = f"{self.base_url}/models"
        headers = self._get_headers()
        headers["Content-Type"] = "text/plain"
        try:
            # Use httpx directly to send raw text body
            response = self.client.post(
                url, content=query, headers=headers, timeout=self.client.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error during models_search: {e}")
            raise

    def models_get(self, model_owner: str, model_name: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific AI model by its owner and name

        Args:
            model_owner: The owner's username or organization name who owns the model
            model_name: The unique name identifier of the model

        Returns:
            A dictionary containing detailed model information, including its latest version and usage examples

        Raises:
            HTTPError: Raised when the API request fails, such as when the model doesn't exist or there are authentication issues

        Tags:
            get, read, models, api, metadata, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_delete(self, model_owner: str, model_name: str) -> str:
        """
        Deletes a private model from the system, provided it has no existing versions.

        Args:
            model_owner: The owner's username or organization name of the model
            model_name: The name of the model to be deleted

        Returns:
            A success message string confirming the model deletion

        Raises:
            HTTPError: When deletion fails due to model being public, having existing versions, or other API restrictions

        Tags:
            delete, models, management, important, api, cleanup
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}"
        response = self._delete(url)
        response.raise_for_status()  # Expecting 204 No Content
        return f"Model '{model_owner}/{model_name}' deleted successfully."

    # --- Model Examples Operations ---

    def models_examples_list(self, model_owner: str, model_name: str) -> dict[str, Any]:
        """
        Retrieves a list of example predictions associated with a specific model.

        Args:
            model_owner: The owner's username or organization name of the model
            model_name: The name of the model to retrieve examples for

        Returns:
            A dictionary containing a paginated list of example prediction objects for the specified model

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or API communication errors

        Tags:
            list, read, models, examples, api, pagination, prediction
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/examples"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    # --- Model Predictions Operations ---
    # Note: The 'Prefer: wait' header is not directly supported by default _post.
    # The response will likely be 201 or 202, requiring polling via predictions_get.

    def models_predictions_create(
        self,
        model_owner: str,
        model_name: str,
        input: dict[str, Any],
        stream: bool = None,  # Deprecated according to schema
        webhook: str = None,
        webhook_events_filter: list[
            Literal["start", "output", "logs", "completed"]
        ] = None,
    ) -> dict[str, Any]:
        """
        Creates an asynchronous prediction request using a specified machine learning model.

        Args:
            model_owner: The owner's username or organization name
            model_name: The name of the model to use for prediction
            input: Dictionary containing the model's input parameters
            stream: DEPRECATED. Boolean flag to request a streaming output URL
            webhook: HTTPS URL for receiving prediction status updates and results
            webhook_events_filter: List of events to trigger webhook notifications ('start', 'output', 'logs', 'completed')

        Returns:
            Dictionary containing the initial prediction state and metadata. Includes prediction ID for status polling.

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            predict, create, async, models, webhook, api, ml, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/predictions"
        request_body = {
            "input": input,
            "stream": stream,  # Included for completeness, though deprecated
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    # --- Model Readme Operations ---

    def models_readme_get(self, model_owner: str, model_name: str) -> str:
        """
        Retrieves the README content for a specified model in Markdown format.

        Args:
            model_owner: The owner's username or organization name
            model_name: The name of the model

        Returns:
            A string containing the README content in Markdown format

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or other request-related problems

        Tags:
            get, read, models, documentation, markdown, api, metadata
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/readme"
        response = self._get(url)
        response.raise_for_status()
        return response.text  # README is text/plain

    # --- Model Versions Operations ---

    def models_versions_list(self, model_owner: str, model_name: str) -> dict[str, Any]:
        """
        Lists all available versions of a specified model.

        Args:
            model_owner: The username or organization name that owns the model
            model_name: The name of the model whose versions are to be listed

        Returns:
            A dictionary containing a paginated list of model version objects with version details

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code

        Tags:
            list, read, models, versions, api, management, paginated, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_versions_get(
        self, model_owner: str, model_name: str, version_id: str
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific version of a model by querying the API.

        Args:
            model_owner: The owner's username or organization name who owns the model
            model_name: The name of the model to query
            version_id: The unique identifier of the specific model version

        Returns:
            A dictionary containing detailed information about the model version, including its OpenAPI schema and metadata

        Raises:
            HTTPError: Raised when the API request fails, such as when the model version doesn't exist or there are authentication issues

        Tags:
            get, read, models, versions, api, metadata, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_versions_delete(
        self, model_owner: str, model_name: str, version_id: str
    ) -> str:
        """
        Deletes a specific version of a model and its associated predictions/output.

        Args:
            model_owner: The owner's username or organization name
            model_name: The name of the model
            version_id: The ID of the version to be deleted

        Returns:
            A success message confirming the deletion request was accepted

        Raises:
            HTTPError: If the deletion request fails due to API restrictions or permissions

        Tags:
            delete, models, versions, management, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}"
        response = self._delete(url)
        response.raise_for_status()  # Expecting 202 Accepted or 204 No Content
        return f"Deletion request for version '{version_id}' of model '{model_owner}/{model_name}' accepted."

    # --- Training Operations (via Model Version) ---

    def trainings_create(
        self,
        model_owner: str,
        model_name: str,
        version_id: str,
        destination: str,
        input: dict[str, Any],
        webhook: str = None,
        webhook_events_filter: list[
            Literal["start", "output", "logs", "completed"]
        ] = None,
    ) -> dict[str, Any]:
        """
        Initiates a new asynchronous training job for a specific model version, with optional webhook notifications for progress updates.

        Args:
            model_owner: The owner's username or organization name of the base model
            model_name: The name of the base model
            version_id: The ID of the model version to train from
            destination: The target model identifier string in '{new_owner}/{new_name}' format
            input: Dictionary containing inputs for the training function
            webhook: Optional HTTPS URL for receiving training updates
            webhook_events_filter: Optional list of events to trigger webhooks ('start', 'output', 'logs', 'completed')

        Returns:
            Dictionary containing the initial state of the training job

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            training, create, async-job, start, model-management, webhook, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}/trainings"
        request_body = {
            "destination": destination,
            "input": input,
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    # --- Prediction Operations ---

    def predictions_list(
        self,
        created_after: str = None,  # ISO 8601 date-time
        created_before: str = None,  # ISO 8601 date-time
    ) -> dict[str, Any]:
        """
        Lists all predictions created by the authenticated account within an optional time range.

        Args:
            created_after: ISO 8601 date-time string specifying the lower bound for prediction creation time (inclusive)
            created_before: ISO 8601 date-time string specifying the upper bound for prediction creation time (exclusive)

        Returns:
            Dictionary containing a paginated list of prediction objects with their associated metadata

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or invalid request parameters

        Tags:
            list, read, predictions, query, filter, pagination, important
        """
        url = f"{self.base_url}/predictions"
        query_params = {
            "created_after": created_after,
            "created_before": created_before,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    # Note: The 'Prefer: wait' header is not directly supported by default _post.
    # The response will likely be 201 or 202, requiring polling via predictions_get.

    def predictions_create(
        self,
        version: str,
        input: dict[str, Any],
        stream: bool = None,  # Deprecated according to schema
        webhook: str = None,
        webhook_events_filter: list[
            Literal["start", "output", "logs", "completed"]
        ] = None,
    ) -> dict[str, Any]:
        """
        Creates an asynchronous prediction request using a specified model version.

        Args:
            version: The ID of the model version to execute the prediction
            input: A dictionary containing the input data for the model prediction
            stream: Deprecated parameter - Previously used for requesting streaming output URL
            webhook: Optional HTTPS URL to receive prediction status updates and results
            webhook_events_filter: Optional list of event types to trigger webhook notifications. Valid events: 'start', 'output', 'logs', 'completed'

        Returns:
            A dictionary containing the initial prediction state, including a prediction ID for status tracking

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            predictions, create, async, api, model, important, webhook, ml
        """
        url = f"{self.base_url}/predictions"
        request_body = {
            "version": version,
            "input": input,
            "stream": stream,  # Included for completeness, though deprecated
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    def predictions_get(self, prediction_id: str) -> dict[str, Any]:
        """
        Retrieves the current state and details of a prediction by its ID.

        Args:
            prediction_id: String identifier of the prediction to retrieve

        Returns:
            Dictionary containing the prediction's current state and associated details

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there are network connectivity issues or invalid URL

        Tags:
            get, read, status, predictions, retrieve, api, important
        """
        url = f"{self.base_url}/predictions/{prediction_id}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def predictions_cancel(
        self, prediction_id: str
    ) -> str:  # Schema shows no content for 200 success
        """
        Cancels a running prediction job identified by its ID.

        Args:
            prediction_id: The unique identifier of the prediction job to cancel

        Returns:
            A string message confirming successful cancellation of the prediction

        Raises:
            HTTPError: When the API request fails or returns an error status code
            RequestException: When there are network connectivity issues or other request-related problems

        Tags:
            cancel, predictions, management, api, async-job, important
        """
        url = f"{self.base_url}/predictions/{prediction_id}/cancel"
        response = self._post(
            url, data={}
        )  # POST with empty body for cancel according to typical patterns
        response.raise_for_status()  # Expecting 200 Success or similar
        return f"Prediction '{prediction_id}' cancelled successfully."

    # --- Training Operations ---

    def trainings_list(self) -> dict[str, Any]:
        """
        Lists all training jobs created by the authenticated account.

        Returns:
            Dict[str, Any]: A dictionary containing a paginated list of training objects with their details and metadata.

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code
            RequestException: When there's a network error or connection issue

        Tags:
            list, read, trainings, management, important
        """
        url = f"{self.base_url}/trainings"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def trainings_get(self, training_id: str) -> dict[str, Any]:
        """
        Retrieves the current state of a training job by its ID.

        Args:
            training_id: A string identifier for the training job

        Returns:
            A dictionary containing the current state and details of the training job

        Raises:
            HTTPError: When the API request fails or returns a non-200 status code

        Tags:
            get, read, status, training, api, fetch, monitor, important
        """
        url = f"{self.base_url}/trainings/{training_id}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def trainings_cancel(self, training_id: str) -> dict[str, Any]:
        """
        Cancels a specific training job in progress.

        Args:
            training_id: String identifier of the training job to be cancelled

        Returns:
            Dictionary containing the updated state and details of the cancelled training job

        Raises:
            HTTPError: When the cancellation request fails or the server returns an error response
            RequestException: When network issues or connection problems occur during the API call

        Tags:
            cancel, trainings, management, async-job, important
        """
        url = f"{self.base_url}/trainings/{training_id}/cancel"
        response = self._post(url, data={})  # POST with empty body for cancel
        response.raise_for_status()
        return response.json()

    # --- Webhooks Operations ---

    def webhooks_default_secret_get(self) -> dict[str, str]:
        """
        Retrieves the signing secret for the default webhook endpoint.

        Returns:
            Dict[str, str]: A dictionary containing the 'key' field with the signing secret value.

        Raises:
            HTTPError: If the API request fails or returns a non-200 status code.
            RequestException: If there are network connectivity issues or other request-related problems.

        Tags:
            get, read, webhooks, security, secret, authentication, api, important
        """
        url = f"{self.base_url}/webhooks/default/secret"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    # --- Required list_tools method ---

    def list_tools(self):
        """
        Returns a list of methods exposed as tools by this application.
        """
        return [
            self.account_get,
            self.collections_list,
            self.collections_get,
            self.deployments_list,
            self.deployments_create,
            self.deployments_get,
            self.deployments_update,
            self.deployments_delete,
            self.deployments_predictions_create,
            self.hardware_list,
            self.models_list,
            self.models_create,
            self.models_search,
            self.models_get,
            self.models_delete,
            self.models_examples_list,
            self.models_predictions_create,
            self.models_readme_get,
            self.models_versions_list,
            self.models_versions_get,
            self.models_versions_delete,
            self.trainings_create,  # Training is started via model version path
            self.predictions_list,
            self.predictions_create,
            self.predictions_get,
            self.predictions_cancel,
            self.trainings_list,
            self.trainings_get,
            self.trainings_cancel,
            self.webhooks_default_secret_get,
        ]
