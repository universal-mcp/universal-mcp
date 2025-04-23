import json
from typing import Any, Dict, List, Literal, Union

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

    def account_get(self) -> Dict[str, Any]:
        """
        [IMPORTANT] Gets information about the authenticated account.

        Returns:
            A dictionary containing account details (type, username, name, etc.).

        Tags:
            account, get, read, important
        """
        url = f"{self.base_url}/account"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    # --- Collection Operations ---

    def collections_list(self) -> Dict[str, Any]:
        """
        Lists collections of models on Replicate.

        Returns:
            A dictionary containing a paginated list of collection objects.

        Tags:
            collections, list, read
        """
        url = f"{self.base_url}/collections"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def collections_get(self, collection_slug: str) -> Dict[str, Any]:
        """
        Gets a specific collection of models by its slug.

        Args:
            collection_slug: The slug of the collection (e.g., 'super-resolution').

        Returns:
            A dictionary containing the collection object and a list of models.

        Tags:
            collections, get, read
        """
        url = f"{self.base_url}/collections/{collection_slug}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    # --- Deployment Operations ---

    def deployments_list(self) -> Dict[str, Any]:
        """
        Lists deployments associated with the authenticated account.

        Returns:
            A dictionary containing a paginated list of deployment objects.

        Tags:
            deployments, list, read
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
    ) -> Dict[str, Any]:
        """
        Creates a new deployment.

        Args:
            name: The name of the deployment.
            model: The full name of the model (e.g., 'stability-ai/sdxl').
            version: The 64-character string ID of the model version.
            hardware: The SKU for the hardware (e.g., 'gpu-t4').
            min_instances: The minimum number of instances (0-5).
            max_instances: The maximum number of instances (0-20).

        Returns:
            A dictionary describing the created deployment.

        Tags:
            deployments, create, write, important
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

    def deployments_get(self, deployment_owner: str, deployment_name: str) -> Dict[str, Any]:
        """
        Gets information about a specific deployment by name.

        Args:
            deployment_owner: The owner's username or organization name.
            deployment_name: The name of the deployment.

        Returns:
            A dictionary describing the deployment.

        Tags:
            deployments, get, read, important
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
    ) -> Dict[str, Any]:
        """
        Updates properties of an existing deployment.

        Args:
            deployment_owner: The owner's username or organization name.
            deployment_name: The name of the deployment.
            hardware: The new SKU for the hardware (optional).
            max_instances: The new maximum number of instances (optional).
            min_instances: The new minimum number of instances (optional).
            version: The new ID of the model version (optional).

        Returns:
            A dictionary describing the updated deployment.

        Tags:
            deployments, update, write, important
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}"
        update_data = {
            "hardware": hardware,
            "max_instances": max_instances,
            "min_instances": min_instances,
            "version": version,
        }
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
             return {"message": "No update parameters provided."}

        response = self._patch(url, data=update_data)
        response.raise_for_status()
        return response.json()

    def deployments_delete(self, deployment_owner: str, deployment_name: str) -> str:
        """
        Deletes a deployment.

        Args:
            deployment_owner: The owner's username or organization name.
            deployment_name: The name of the deployment.

        Returns:
            A success message if deletion is successful.

        Raises:
            HTTPError: If deletion fails (e.g., deployment is in use).

        Tags:
            deployments, delete, management
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}"
        response = self._delete(url)
        response.raise_for_status()
        return f"Deployment '{deployment_owner}/{deployment_name}' deleted successfully." # Assuming 204 No Content


    # --- Deployments Predictions Operations ---
    # Note: The 'Prefer: wait' header is not directly supported by default _post.
    # The response will likely be 201 or 202, requiring polling via predictions_get.

    def deployments_predictions_create(
        self,
        deployment_owner: str,
        deployment_name: str,
        input: Dict[str, Any],
        stream: bool = None, # Deprecated according to schema
        webhook: str = None,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] = None,
    ) -> Dict[str, Any]:
        """
        [IMPORTANT] Creates a prediction using a specific deployment.

        Args:
            deployment_owner: The owner's username or organization name.
            deployment_name: The name of the deployment.
            input: The model's input as a JSON object.
            stream: DEPRECATED. Request a URL for streaming output (optional).
            webhook: An HTTPS URL for receiving prediction updates (optional).
            webhook_events_filter: List of events to trigger webhooks (optional).

        Returns:
            A dictionary describing the initial state of the prediction.
            Poll the prediction ID using predictions_get for the final result.

        Tags:
            deployments, predictions, create, write, async, important
        """
        url = f"{self.base_url}/deployments/{deployment_owner}/{deployment_name}/predictions"
        request_body = {
            "input": input,
            "stream": stream, # Included for completeness, though deprecated
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        # Remove None values, but keep False/empty lists if explicitly set
        request_body = {k: v for k, v in request_body.items() if v is not None}

        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()


    # --- Hardware Operations ---

    def hardware_list(self) -> List[Dict[str, Any]]:
        """
        Lists available hardware options for running models.

        Returns:
            A list of hardware objects, each with 'name' and 'sku'.

        Tags:
            hardware, list, read
        """
        url = f"{self.base_url}/hardware"
        response = self._get(url)
        response.raise_for_status()
        return response.json()


    # --- Model Operations ---

    def models_list(self) -> Dict[str, Any]:
        """
        Lists public models on Replicate.

        Returns:
            A dictionary containing a paginated list of model objects.

        Tags:
            models, list, read
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
    ) -> Dict[str, Any]:
        """
        Creates a new model.

        Args:
            owner: The username or organization name that will own the model.
            name: The name of the model (must be unique for the owner).
            visibility: Whether the model is 'public' or 'private'.
            hardware: The SKU for the hardware.
            cover_image_url: URL for the model's cover image (optional).
            description: A description of the model (optional).
            github_url: URL for the source code (optional).
            license_url: URL for the license (optional).
            paper_url: URL for the paper (optional).

        Returns:
            A dictionary describing the created model.

        Tags:
            models, create, write, management
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
         # Remove None values
        request_body = {k: v for k, v in request_body.items() if v is not None}

        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()

    def models_search(self, query: str) -> Dict[str, Any]:
        """
        Searches public models matching a query.

        Args:
            query: The search query string.

        Returns:
            A dictionary containing a paginated list of matching model objects.

        Tags:
            models, search, query, read
        """
        url = f"{self.base_url}/models"
        # The OpenAPI uses a custom 'QUERY' method, which the generator
        # translates to a POST with text/plain body. Emulate this.
        headers = self._get_headers()
        # Need to explicitly set Content-Type for text/plain
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


    def models_get(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        Gets information about a specific model by name.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.

        Returns:
            A dictionary describing the model, including latest version and example.

        Tags:
            models, get, read, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_delete(self, model_owner: str, model_name: str) -> str:
        """
        Deletes a model. Requires the model to be private and have no versions.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.

        Returns:
            A success message if deletion is successful.

        Raises:
            HTTPError: If deletion fails due to restrictions.

        Tags:
            models, delete, management
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}"
        response = self._delete(url)
        response.raise_for_status() # Expecting 204 No Content
        return f"Model '{model_owner}/{model_name}' deleted successfully."


    # --- Model Examples Operations ---

    def models_examples_list(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        Lists example predictions for a model.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.

        Returns:
            A dictionary containing a paginated list of example prediction objects.

        Tags:
            models, examples, list, read
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
        input: Dict[str, Any],
        stream: bool = None, # Deprecated according to schema
        webhook: str = None,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] = None,
    ) -> Dict[str, Any]:
        """
        [IMPORTANT] Creates a prediction using a specific official model.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.
            input: The model's input as a JSON object.
            stream: DEPRECATED. Request a URL for streaming output (optional).
            webhook: An HTTPS URL for receiving prediction updates (optional).
            webhook_events_filter: List of events to trigger webhooks (optional).

        Returns:
            A dictionary describing the initial state of the prediction.
            Poll the prediction ID using predictions_get for the final result.

        Tags:
            models, predictions, create, write, async, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/predictions"
        request_body = {
            "input": input,
            "stream": stream, # Included for completeness, though deprecated
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        # Remove None values, but keep False/empty lists if explicitly set
        request_body = {k: v for k, v in request_body.items() if v is not None}

        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()


    # --- Model Readme Operations ---

    def models_readme_get(self, model_owner: str, model_name: str) -> str:
        """
        Gets the README content for a model in Markdown format.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.

        Returns:
            A string containing the README content in Markdown.

        Tags:
            models, readme, get, read
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/readme"
        response = self._get(url)
        response.raise_for_status()
        return response.text # README is text/plain


    # --- Model Versions Operations ---

    def models_versions_list(self, model_owner: str, model_name: str) -> Dict[str, Any]:
        """
        Lists versions for a model.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.

        Returns:
            A dictionary containing a paginated list of model version objects.

        Tags:
            models, versions, list, read
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_versions_get(self, model_owner: str, model_name: str, version_id: str) -> Dict[str, Any]:
        """
        Gets information about a specific model version.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.
            version_id: The ID of the version.

        Returns:
            A dictionary describing the model version, including its OpenAPI schema.

        Tags:
            models, versions, get, read
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def models_versions_delete(self, model_owner: str, model_name: str, version_id: str) -> str:
        """
        Deletes a model version and its associated predictions/output.

        Args:
            model_owner: The owner's username or organization name.
            model_name: The name of the model.
            version_id: The ID of the version.

        Returns:
            A success message indicating the deletion request was accepted.

        Raises:
            HTTPError: If deletion fails due to restrictions.

        Tags:
            models, versions, delete, management
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}"
        response = self._delete(url)
        response.raise_for_status() # Expecting 202 Accepted or 204 No Content
        return f"Deletion request for version '{version_id}' of model '{model_owner}/{model_name}' accepted."


    # --- Training Operations (via Model Version) ---

    def trainings_create(
        self,
        model_owner: str,
        model_name: str,
        version_id: str,
        destination: str,
        input: Dict[str, Any],
        webhook: str = None,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] = None,
    ) -> Dict[str, Any]:
        """
        [IMPORTANT] Starts a new training job for a specific model version.

        Args:
            model_owner: The owner's username or organization name of the base model.
            model_name: The name of the base model.
            version_id: The ID of the model version to train from.
            destination: The target model identifier string in '{new_owner}/{new_name}' format.
            input: An object containing inputs for the training function.
            webhook: An HTTPS URL for receiving training updates (optional).
            webhook_events_filter: List of events to trigger webhooks (optional).

        Returns:
            A dictionary describing the initial state of the training.
            Poll the training ID using trainings_get for the final result.

        Tags:
            trainings, create, write, async, important
        """
        url = f"{self.base_url}/models/{model_owner}/{model_name}/versions/{version_id}/trainings"
        request_body = {
            "destination": destination,
            "input": input,
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        # Remove None values, but keep False/empty lists if explicitly set
        request_body = {k: v for k, v in request_body.items() if v is not None}

        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()


    # --- Prediction Operations ---

    def predictions_list(
        self,
        created_after: str = None, # ISO 8601 date-time
        created_before: str = None, # ISO 8601 date-time
    ) -> Dict[str, Any]:
        """
        Lists all predictions created by the authenticated account.

        Args:
            created_after: Include predictions created at or after this time (optional).
            created_before: Include predictions created before this time (optional).

        Returns:
            A dictionary containing a paginated list of prediction objects.

        Tags:
            predictions, list, read
        """
        url = f"{self.base_url}/predictions"
        query_params = {
            "created_after": created_after,
            "created_before": created_before,
        }
        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}

        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    # Note: The 'Prefer: wait' header is not directly supported by default _post.
    # The response will likely be 201 or 202, requiring polling via predictions_get.

    def predictions_create(
        self,
        version: str,
        input: Dict[str, Any],
        stream: bool = None, # Deprecated according to schema
        webhook: str = None,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] = None,
    ) -> Dict[str, Any]:
        """
        [IMPORTANT] Creates a prediction using a specific model version.

        Args:
            version: The ID of the model version to run.
            input: The model's input as a JSON object.
            stream: DEPRECATED. Request a URL for streaming output (optional).
            webhook: An HTTPS URL for receiving prediction updates (optional).
            webhook_events_filter: List of events to trigger webhooks (optional).

        Returns:
            A dictionary describing the initial state of the prediction.
            Poll the prediction ID using predictions_get for the final result.

        Tags:
            predictions, create, write, async, important
        """
        url = f"{self.base_url}/predictions"
        request_body = {
            "version": version,
            "input": input,
            "stream": stream, # Included for completeness, though deprecated
            "webhook": webhook,
            "webhook_events_filter": webhook_events_filter,
        }
        # Remove None values, but keep False/empty lists if explicitly set
        request_body = {k: v for k, v in request_body.items() if v is not None}

        response = self._post(url, data=request_body)
        response.raise_for_status()
        return response.json()


    def predictions_get(self, prediction_id: str) -> Dict[str, Any]:
        """
        [IMPORTANT] Gets the current state of a prediction by ID.

        Args:
            prediction_id: The ID of the prediction.

        Returns:
            A dictionary describing the prediction's current state.

        Tags:
            predictions, get, read, status, important
        """
        url = f"{self.base_url}/predictions/{prediction_id}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def predictions_cancel(self, prediction_id: str) -> str: # Schema shows no content for 200 success
        """
        Cancels a prediction by ID.

        Args:
            prediction_id: The ID of the prediction to cancel.

        Returns:
            A success message indicating the prediction was cancelled.

        Tags:
            predictions, cancel, management
        """
        url = f"{self.base_url}/predictions/{prediction_id}/cancel"
        response = self._post(url, data={}) # POST with empty body for cancel according to typical patterns
        response.raise_for_status() # Expecting 200 Success or similar
        return f"Prediction '{prediction_id}' cancelled successfully."

    # --- Training Operations ---

    def trainings_list(self) -> Dict[str, Any]:
        """
        Lists all training jobs created by the authenticated account.

        Returns:
            A dictionary containing a paginated list of training objects.

        Tags:
            trainings, list, read
        """
        url = f"{self.base_url}/trainings"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def trainings_get(self, training_id: str) -> Dict[str, Any]:
        """
        [IMPORTANT] Gets the current state of a training job by ID.

        Args:
            training_id: The ID of the training.

        Returns:
            A dictionary describing the training's current state.

        Tags:
            trainings, get, read, status, important
        """
        url = f"{self.base_url}/trainings/{training_id}"
        response = self._get(url)
        response.raise_for_status()
        return response.json()

    def trainings_cancel(self, training_id: str) -> Dict[str, Any]:
        """
        Cancels a training job by ID.

        Args:
            training_id: The ID of the training to cancel.

        Returns:
            A dictionary describing the training's state after cancellation attempt.

        Tags:
            trainings, cancel, management
        """
        url = f"{self.base_url}/trainings/{training_id}/cancel"
        response = self._post(url, data={}) # POST with empty body for cancel
        response.raise_for_status()
        return response.json()

    # --- Webhooks Operations ---

    def webhooks_default_secret_get(self) -> Dict[str, str]:
        """
        Gets the signing secret for the default webhook endpoint.

        Returns:
            A dictionary containing the 'key' for the signing secret.

        Tags:
            webhooks, secret, get, read, security
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
            self.trainings_create, # Training is started via model version path
            self.predictions_list,
            self.predictions_create,
            self.predictions_get,
            self.predictions_cancel,
            self.trainings_list,
            self.trainings_get,
            self.trainings_cancel,
            self.webhooks_default_secret_get,
        ]