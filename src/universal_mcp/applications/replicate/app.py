# universal_mcp/applications/replicate/app.py

import base64
import httpx
from typing import Any, Dict, Optional, Literal

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration

QUALITY_PRESETS = {
    "id": "quality-presets",
    "name": "Quality Presets",
    "description": "Common quality presets for different generation scenarios",
    "model_type": "any",
    "presets": {
        "draft": {
            "description": "Fast draft quality for quick iterations",
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 5.0,
                "width": 512,
                "height": 512,
            },
        },
        "balanced": {
            "description": "Balanced quality and speed for most use cases",
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 768,
                "height": 768,
            },
        },
        "quality": {
            "description": "High quality for final outputs",
            "parameters": {
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024,
            },
        },
        "extreme": {
            "description": "Maximum quality, very slow",
            "parameters": {
                "num_inference_steps": 150,
                "guidance_scale": 8.0,
                "width": 1536,
                "height": 1536,
            },
        },
    },
    "version": "1.0.0",
}

STYLE_PRESETS = {
    "id": "style-presets",
    "name": "Style Presets",
    "description": "Common style presets for different artistic looks",
    "model_type": "any",
    "presets": {
        "photorealistic": {
            "description": "Highly detailed photorealistic style",
            "parameters": {
                "prompt_prefix": "professional photograph, photorealistic, highly detailed, 8k uhd",
                "negative_prompt": "painting, drawing, illustration, anime, cartoon, artistic, unrealistic",
                "guidance_scale": 8.0,
            },
        },
        "cinematic": {
            "description": "Dramatic cinematic style",
            "parameters": {
                "prompt_prefix": "cinematic shot, dramatic lighting, movie scene, high budget film",
                "negative_prompt": "low quality, amateur, poorly lit",
                "guidance_scale": 7.5,
            },
        },
        "anime": {
            "description": "Anime/manga style",
            "parameters": {
                "prompt_prefix": "anime style, manga art, clean lines, vibrant colors",
                "negative_prompt": "photorealistic, 3d render, photograph, western art style",
                "guidance_scale": 7.0,
            },
        },
        "digital_art": {
            "description": "Digital art style",
            "parameters": {
                "prompt_prefix": "digital art, vibrant colors, detailed illustration",
                "negative_prompt": "photograph, realistic, grainy, noisy",
                "guidance_scale": 7.0,
            },
        },
        "oil_painting": {
            "description": "Oil painting style",
            "parameters": {
                "prompt_prefix": "oil painting, textured brushstrokes, artistic, rich colors",
                "negative_prompt": "photograph, digital art, 3d render, smooth",
                "guidance_scale": 7.0,
            },
        },
    },
    "version": "1.0.0",
}

# Hardcoded SDXL version ID used in the original server's generate_image tool
# This should be defined consistently or made configurable if other models are needed for generate_image
SDXL_V1_0_VERSION = "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

# --- Replicate Application ---

class ReplicateApp(APIApplication):
    """
    Application for interacting with the Replicate API for running models and generating content.

    Requires a Replicate API token configured via integration (e.g., ApiKeyIntegration).
    The integration name should match the expected environment variable or store key, e.g., 'REPLICATE_API_TOKEN'.
    """

    def __init__(self, integration: Integration | None = None, **kwargs) -> None:
        # The integration name should ideally align with the required API key env var name (e.g., REPLICATE_API_TOKEN)
        super().__init__(name="replicate", integration=integration, **kwargs)
        self.base_url = "https://api.replicate.com/v1"
        # The APIApplication base class handles setting self.client with headers using integration credentials


    def list_models(self, owner: str | None = None) -> dict[str, Any]:
        """
        Lists available models on Replicate with optional filtering by owner.

        Args:
            owner: Optional owner username to filter models.

        Returns:
            A dictionary containing a list of models and pagination info.

        Raises:
            httpx.HTTPStatusError: If the API request fails.

        Tags:
            list, models, replicate, read, api, important
        """
        params = {}
        if owner:
            params["owner"] = owner
        response = self._get("/models", params=params)
        return response.json()

    def search_models(self, query: str) -> dict[str, Any]:
        """
        Searches for models on Replicate using a query.

        Note: Replicate uses a specific endpoint/method for semantic search.
        This implementation uses the standard GET /models endpoint with a 'q' parameter
        if available, otherwise it would require a custom request type not
        standard in APIApplication.

        Args:
            query: Search query string.

        Returns:
            A dictionary containing the search results.

        Raises:
            httpx.HTTPStatusError: If the API request fails.

        Tags:
            search, models, replicate, read, api, query, important
        """
        # The original ReplicateClient used a 'QUERY' method which is non-standard.
        # Standard REST search is often GET /models/search?q=... or POST /models/search with body.
        # Using GET /models with 'q' parameter as a likely alternative if supported.
        # If this doesn't work, a custom request using self.client.request might be needed.
        response = self._get("/models", params={"q": query})
        return response.json()

    def get_model_details(self, model_id: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific model.

        Args:
            model_id: Model identifier in format owner/name (e.g., 'stability-ai/sdxl').

        Returns:
            A dictionary containing detailed model information.

        Raises:
            httpx.HTTPStatusError: If the model is not found or API request fails.

        Tags:
            get, models, replicate, read, api, details, important
        """
        response = self._get(f"/models/{model_id}")
        return response.json()

    def get_model_versions(self, model_id: str) -> list[dict[str, Any]]:
        """
        Retrieves available versions for a specific model.

        Args:
            model_id: Model identifier in format owner/name.

        Returns:
            A list of dictionaries, each representing a model version.

        Raises:
            httpx.HTTPStatusError: If the model is not found or API request fails.

        Tags:
            list, versions, models, replicate, read, api, important
        """
        response = self._get(f"/models/{model_id}/versions")
        return response.json()

    def list_hardware(self) -> list[dict[str, str]]:
        """
        Lists available hardware options for running models on Replicate.

        Returns:
            A list of dictionaries, each representing a hardware option.

        Raises:
            httpx.HTTPStatusError: If the API request fails.

        Tags:
            list, hardware, replicate, read, api
        """
        response = self._get("/hardware")
        return response.json()

    def list_collections(self) -> list[dict[str, Any]]:
        """
        Lists available model collections on Replicate.

        Returns:
            A list of dictionaries, each representing a model collection.

        Raises:
            httpx.HTTPStatusError: If the API request fails.

        Tags:
            list, collections, replicate, read, api
        """
        response = self._get("/collections")
        return response.json().get("results", []) # API returns a result object

    def get_collection_details(self, collection_slug: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific collection.

        Args:
            collection_slug: The slug identifier of the collection (e.g., 'text-to-image').

        Returns:
            A dictionary containing detailed collection information including its models.

        Raises:
            httpx.HTTPStatusError: If the collection is not found or API request fails.

        Tags:
            get, collections, replicate, read, api, details
        """
        response = self._get(f"/collections/{collection_slug}")
        return response.json()

    def create_prediction(
        self,
        version: str,
        input: Dict[str, Any],
        webhook: Optional[str] = None,
        # webhook_events: Optional[List[Literal["start", "output", "logs", "completed"]]] = None # Enum typing requires Pydantic model in args
    ) -> dict[str, Any]:
        """
        Creates a new prediction using a specific model version on Replicate.

        Args:
            version: Model version ID (a hash like '39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b').
            input: Model-specific input parameters as a dictionary. Refer to the model's documentation for schema.
            webhook: Optional webhook URL for prediction updates.
            # webhook_events: Optional list of event types to trigger the webhook.

        Returns:
            A dictionary containing the initial prediction details (status, ID, URLs etc.).

        Raises:
            httpx.HTTPStatusError: If the API request fails (e.g., invalid version, bad input).

        Tags:
            create, prediction, replicate, write, api, async_job, start, important
        """
        payload = {
            "version": version,
            "input": input,
        }
        if webhook:
            payload["webhook"] = webhook
        # if webhook_events: # Needs Pydantic model for args
        #     payload["webhook_events"] = webhook_events

        response = self._post("/predictions", data=payload)
        return response.json()

    def get_prediction(self, prediction_id: str) -> dict[str, Any]:
        """
        Retrieves the status and results of a specific prediction.

        Args:
            prediction_id: The unique identifier for the prediction.

        Returns:
            A dictionary containing the prediction details (status, output, logs, etc.).

        Raises:
            httpx.HTTPStatusError: If the prediction ID is not found or API request fails.

        Tags:
            get, prediction, replicate, read, api, async_job, status, important
        """
        response = self._get(f"/predictions/{prediction_id}")
        return response.json()

    def cancel_prediction(self, prediction_id: str) -> dict[str, Any]:
        """
        Cancels a running prediction.

        Args:
            prediction_id: The unique identifier for the prediction to cancel.

        Returns:
            A dictionary containing the updated prediction details (status should be 'canceled').

        Raises:
            httpx.HTTPStatusError: If the prediction ID is not found or API request fails.

        Tags:
            cancel, prediction, replicate, write, api, async_job, management, important
        """
        response = self._post(f"/predictions/{prediction_id}/cancel", data={})
        return response.json()

    def list_predictions(
        self, status: Literal["starting", "processing", "succeeded", "failed", "canceled"] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Lists recent predictions with optional filtering by status.

        Args:
            status: Optional status to filter predictions by.
            limit: Maximum number of predictions to return (1-100). Defaults to 10.

        Returns:
            A list of dictionaries, each representing a prediction.

        Raises:
            ValueError: If limit is outside the range 1-100.
            httpx.HTTPStatusError: If the API request fails.

        Tags:
            list, predictions, replicate, read, api, filter, pagination, important
        """
        if not 1 <= limit <= 100:
             raise ValueError("limit must be between 1 and 100")

        params = {"limit": limit}
        if status:
            params["status"] = status

        response = self._get("/predictions", params=params)
        return response.json()

    def generate_image(
        self,
        prompt: str,
        style: str | None = None,
        quality: Literal["draft", "balanced", "quality", "extreme"] = "balanced",
        width: int | None = None,
        height: int | None = None,
        num_outputs: int = 1,
        seed: int | None = None,
        negative_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Generates an image using the SDXL model with various presets and parameters.

        This is a higher-level helper tool that wraps the create_prediction call
        for a specific common image generation model (SDXL v1.0).

        Args:
            prompt: The positive text prompt for the image generation.
            style: Optional style preset ('photorealistic', 'cinematic', 'anime', 'digital_art', 'oil_painting'). Applies prefix/negative prompt modifications.
            quality: Quality preset ('draft', 'balanced', 'quality', 'extreme'). Adjusts steps, scale, and size. Defaults to 'balanced'.
            width: Optional image width in pixels. Overrides the quality preset size. Must be a multiple of 8.
            height: Optional image height in pixels. Overrides the quality preset size. Must be a multiple of 8.
            num_outputs: Number of images to generate in parallel (1-4). Defaults to 1.
            seed: Random seed for reproducible generation. Use None for random.
            negative_prompt: Text prompt for elements to avoid in the image. Overrides negative prompts from style presets.

        Returns:
            A dictionary containing the initial prediction details, including the prediction ID.
            The image URL/data will be available once the prediction is completed via get_prediction or get_generation_image.

        Raises:
            ValueError: If invalid quality or style preset is provided.
            httpx.HTTPStatusError: If the prediction creation API request fails.

        Tags:
            generate, image, replicate, ai, sdxl, create, important
        """
        # Get quality preset parameters
        quality_preset = QUALITY_PRESETS["presets"].get(
            quality, QUALITY_PRESETS["presets"]["balanced"]
        )
        parameters = quality_preset["parameters"].copy()

        # Apply style preset if specified
        processed_prompt = prompt # Start with the base prompt
        effective_negative_prompt = negative_prompt # Use provided negative prompt if any

        if style:
            style_preset = STYLE_PRESETS["presets"].get(style.lower())
            if style_preset:
                style_params = style_preset["parameters"]
                # Merge prompt prefixes
                if "prompt_prefix" in style_params:
                    processed_prompt = f"{style_params['prompt_prefix']}, {prompt}"
                # Merge negative prompts - provided negative prompt takes precedence
                if "negative_prompt" in style_params and effective_negative_prompt is None:
                     effective_negative_prompt = style_params["negative_prompt"]

                # Copy other parameters from style preset (e.g., guidance_scale)
                for k, v in style_params.items():
                    if k not in ("prompt_prefix", "negative_prompt"):
                         parameters[k] = v

        # Override size if specified
        if width is not None:
            if width % 8 != 0:
                 raise ValueError("Width must be a multiple of 8")
            parameters["width"] = width
        if height is not None:
            if height % 8 != 0:
                 raise ValueError("Height must be a multiple of 8")
            parameters["height"] = height

        # Add mandatory and optional parameters
        parameters.update(
            {
                "prompt": processed_prompt,
                "num_outputs": num_outputs,
            }
        )
        if effective_negative_prompt is not None:
            parameters["negative_prompt"] = effective_negative_prompt
        if seed is not None:
            parameters["seed"] = seed


        # Create prediction using the hardcoded SDXL model version
        result = self.create_prediction(
            version=SDXL_V1_0_VERSION,
            input=parameters,
            # Note: webhook is not exposed in this helper tool
        )

        # Return the initial prediction result
        return result # This includes the 'id' which is the prediction_id


    def get_generation_image(self, prediction_id: str) -> dict[str, Any] | str:
        """
        Retrieves the image data for a completed generation.

        Args:
            prediction_id: The unique identifier for the completed prediction.

        Returns:
            A dictionary containing 'mimeType' (str) and 'blob' (str, base64 encoded image data)
            if the generation succeeded and has output. Returns a status message string otherwise.

        Raises:
            httpx.HTTPStatusError: If the prediction ID is not found or API request fails.
            ValueError: If the generation did not succeed or has no output.

        Tags:
            get, image, replicate, read, api, data
        """
        prediction = self.get_prediction(prediction_id)

        if prediction["status"] != "succeeded":
            return f"Generation {prediction_id} is not completed. Current status: {prediction['status']}"

        if not prediction.get("output"):
            return f"Generation {prediction_id} succeeded but has no image output."

        # Get image URL
        # Output is typically a list for image models, but could be a single string
        image_url = prediction["output"][0] if isinstance(prediction["output"], list) else prediction["output"]

        try:
            # Download image using the shared httpx client instance
            img_response = self.client.get(image_url)
            img_response.raise_for_status()

            # Determine mime type from URL extension
            ext = image_url.split(".")[-1].lower()
            mime_type = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "gif": "image/gif",
                "webp": "image/webp",
            }.get(ext, "application/octet-stream") # Default to generic if unknown

            # Return blob contents (base64 encoded)
            return {
                "mimeType": mime_type,
                "blob": base64.b64encode(img_response.content).decode("ascii"),
                "url": image_url, # Also include the URL for convenience
            }
        except httpx.HTTPStatusError as e:
             return f"Failed to download image from {image_url}: HTTP Error {e.response.status_code}"
        except Exception as e:
            # Catch other potential errors during download or base64 encoding
            return f"An error occurred while processing the image from {image_url}: {type(e).__name__} - {e}"


    # The get_webhook_secret and verify_webhook tools are related to webhook *receiving*
    # by the server, not typically called by an agent *using* the application.
    # The original server had get_webhook_secret as a tool, which an agent *could* call
    # to configure their own webhook sender. verify_webhook is server-side verification.
    # Let's include get_webhook_secret as it's an API call.

    def get_webhook_secret(self) -> dict[str, str]:
        """
        Retrieves the signing secret for verifying webhook requests from Replicate.

        This secret is used to ensure webhook requests are authentic.

        Returns:
            A dictionary containing the webhook signing secret with key 'key'.

        Raises:
            httpx.HTTPStatusError: If the API request fails.

        Tags:
            get, webhook, replicate, read, api, security
        """
        # Note: The endpoint /webhooks/default/secret might be specific to some Replicate setups
        # or tools. The standard API docs don't explicitly list this. Based on replicate_client.py.
        response = self._get("/webhooks/default/secret")
        return response.json()


    def list_tools(self):
        """
        Returns a list of methods exposed as tools.
        """
        return [
            self.list_models,
            self.search_models,
            self.get_model_details,
            self.get_model_versions,
            self.list_hardware,
            self.list_collections,
            self.get_collection_details,
            self.create_prediction,
            self.get_prediction,
            self.cancel_prediction,
            self.list_predictions,
            self.generate_image, # High-level image generation helper
            self.get_generation_image, # Get image data after completion
            self.get_webhook_secret, # Tool to get webhook secret
            # verify_webhook is a local utility, not an API tool
            # Subscription tools are server-side and not part of the app
            # Template/parameter tools are local data/validation, not API tools
            # open_image_with_system is a local system action, not an API tool
        ]