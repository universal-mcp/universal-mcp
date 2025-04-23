# universal_mcp/applications/fal_ai/app.py

import os
import mimetypes
import aiofiles
import json
from typing import Dict, Any, Optional, List

import httpx

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration
from universal_mcp.exceptions import NotAuthorizedError, ToolError

# Define fal.ai API base URLs based on the mcp-fal config
FAL_BASE_URL = "https://fal.ai/api"
FAL_QUEUE_URL = "https://queue.fal.run"
FAL_DIRECT_URL = "https://fal.run"
FAL_REST_URL = "https://rest.alpha.fal.ai"

class FalAiApp(APIApplication):
    """
    Application for interacting with the fal.ai platform to list models,
    generate content, manage queued requests, and upload files.
    Requires a fal.ai API key configured via integration for most operations.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="fal_ai", integration=integration)
        self.default_timeout = 180.0 # Use a reasonable default timeout

    async def _authenticated_request(
        self,
        url: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None,
        content: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        require_auth: bool = True # Controls if Authorization header is added
    ) -> Dict[str, Any]:
        """
        Helper for making authenticated (or optionally unauthenticated)
        requests to fal.ai API. Includes default browser-like headers
        to potentially bypass Cloudflare. Handles potential decoding errors.
        """
        # Start with default browser-like headers to help with Cloudflare
        request_headers = {
            # Use a common browser User-Agent
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", # Example Chrome UA
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br", # Standard encoding header
            "Accept-Language": "en-US,en;q=0.9", # Standard language header
            # "Referer": "https://fal.ai/", # Sometimes helpful, but might not be appropriate for all calls
        }

        if require_auth:
            if not self.integration:
                raise NotAuthorizedError("Integration not configured for FalAiApp.")

            try:
                credentials = self.integration.get_credentials()
                api_key = credentials.get("api_key")
            except NotAuthorizedError as e:
                raise NotAuthorizedError(
                    "Fal.ai API key not found in credentials. "
                    "Please ensure the 'fal_ai' integration is configured correctly. "
                    f"Details: {e.message}"
                ) from e

            if not api_key:
                raise NotAuthorizedError(
                    "Fal.ai API key not found in credentials obtained from integration. "
                    "Please ensure the 'fal_ai' integration is configured with a valid API key."
                )

            # Add the mandatory Authorization header required by Fal.ai API for protected endpoints
            request_headers["Authorization"] = f"Key {api_key}"

        # Override default headers with any user-provided headers
        if headers:
             request_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=timeout or self.default_timeout) as client:
                response = await client.request(
                    method.upper(),
                    url,
                    json=json_data,
                    content=content,
                    headers=request_headers, # Use the combined headers
                    params=params # Pass params dictionary to httpx
                )

                # Attempt to decode response content for potential error reporting before raise_for_status
                response_body_decoded = "Could not decode response body."
                response_body_hex = ""
                try:
                   # Attempt decoding with error replacement
                   response_body_decoded = response.content.decode(response.encoding or 'utf-8', errors='replace')
                   response_body_info = f"Response body (decoded, potentially incomplete/replaced): {response_body_decoded[:500]}..."
                except Exception as decode_exc:
                    # If decoding fails, report raw bytes hex
                    response_body_hex = response.content[:200].hex()
                    response_body_info = f"Could not decode response body. Raw content (truncated hex): {response_body_hex}..."


                # Check status and raise if 4xx/5xx
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    # Handle HTTP errors (4xx/5xx)
                    message = f"HTTP error {e.response.status_code}"
                    details = {}

                    try:
                        # Try parsing error details if the body is JSON
                        error_details = e.response.json()
                        message = error_details.get("message", message)
                        details = error_details
                        # If JSON parsing succeeded, use the original response text for info if available
                        response_body_info = f"Response body (from .text): {e.response.text[:500]}..."
                    except json.JSONDecodeError:
                        # If body was not JSON, use the already attempted decoded/hex info
                        details["response_body_decoded"] = response_body_decoded[:500]
                        if response_body_hex: details["response_content_hex"] = response_body_hex
                        details["response_encoding_attempted"] = response.encoding or 'utf-8'


                    # Ensure details dictionary is serializable for the error message
                    details_str = json.dumps(details) if isinstance(details, dict) else str(details)

                    # Raise ToolError with status code, message, and body info/details
                    raise ToolError(f"Fal.ai API error calling {url}: {message} (Status: {e.response.status_code}). {response_body_info}. Details: {details_str}") from e

                # If status is OK (2xx) and no HTTPStatusError was raised, attempt JSON decoding
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # If 2xx but not JSON, this is unexpected for standard API responses.
                    # Use the already attempted decoded/hex info for the error message.
                    details = {}
                    details["response_body_decoded"] = response_body_decoded[:500]
                    if response_body_hex: details["response_content_hex"] = response_body_hex
                    details["response_encoding_attempted"] = response.encoding or 'utf-8'


                    details_str = json.dumps(details) if isinstance(details, dict) else str(details)
                    raise ToolError(f"Fal.ai API response from {url} was not valid JSON (HTTP status {response.status_code}). {response_body_info}. Details: {details_str}") from e

        except httpx.RequestError as e:
            # Wrap request-level errors (like network issues, timeouts) in ToolError
            raise ToolError(f"Fal.ai request failed for {url}: {str(e)}") from e
        except UnicodeDecodeError as e:
             # Specifically catch UnicodeDecodeError if it happens outside of my manual decoding attempts
             # This likely means httpx tried to decode automatically and failed.
             # We don't have the response object directly here, so we report the error itself.
             # If we could access response.content here, we would, but the error happens during response processing.
             raise ToolError(f"An unexpected decoding error occurred during Fal.ai API request to {url}: {e}") from e
        except Exception as e:
             # Catch any other unexpected errors
             raise ToolError(f"An unexpected error occurred calling Fal.ai API at {url}: {e}") from e


    def _sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
         """Removes None values from parameters."""
         sanitized = params.copy()
         sanitized = {k: v for k, v in sanitized.items() if v is not None}
         return sanitized

    async def list_models(self, page: Optional[int] = None, total: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List available models on fal.ai with optional pagination.

        Args:
            page: The page number of models to retrieve. Defaults to None.
            total: The total number of models to retrieve per page. Defaults to None.

        Returns:
            A list of models with their metadata.

        Raises:
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            list, models, fal-ai, read-only, pagination, important
        """
        url = f"{FAL_BASE_URL}/models"
        params = {}
        if page is not None:
            params["page"] = page
        if total is not None:
            params["total"] = total

        # Call _authenticated_request with require_auth=False, but browser headers added by helper
        return await self._authenticated_request(url, method="GET", params=params, require_auth=False)


    async def search_models(self, keywords: str) -> List[Dict[str, Any]]:
        """
        Search for models on fal.ai based on keywords.

        Args:
            keywords: The search terms to find models.

        Returns:
            A list of models matching the search criteria.

        Raises:
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            search, models, fal-ai, read-only, important
        """
        url = f"{FAL_BASE_URL}/models" # Query param 'keywords' is added by _authenticated_request
        # Call _authenticated_request with require_auth=False, but browser headers added by helper
        return await self._authenticated_request(url, method="GET", params={"keywords": keywords}, require_auth=False)

    async def get_model_schema(self, model_id: str) -> Dict[str, Any]:
        """
        Get the OpenAPI schema for a specific fal.ai model.

        Args:
            model_id: The ID of the model (e.g., "fal-ai/flux/dev").

        Returns:
            The OpenAPI schema for the model.

        Raises:
            NotAuthorizedError: If the fal.ai API key is not found (authentication recommended).
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            get, schema, models, fal-ai, read-only
        """
        url = f"{FAL_BASE_URL}/openapi/queue/openapi.json" # Query param 'endpoint_id' is added by _authenticated_request
         # Keep require_auth=True as a safer default.
        return await self._authenticated_request(url, method="GET", params={"endpoint_id": model_id}, require_auth=True)

    async def generate_content(
        self,
        model: str,
        parameters: Dict[str, Any],
        queue: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content using a fal.ai model.

        Args:
            model: The model ID to use (e.g., "fal-ai/flux/dev").
            parameters: Model-specific parameters as a dictionary.
            queue: Whether to use the queuing system for asynchronous execution.
                   Defaults to False (direct execution).

        Returns:
            The model's response. If queue=True, returns a response with status_url
            and response_url for checking job progress and results.

        Raises:
            NotAuthorizedError: If the fal.ai API key is not found.
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            generate, content, ai, fal-ai, important, async_job
        """
        if queue:
            url = f"{FAL_QUEUE_URL}/{model}"
        else:
            url = f"{FAL_DIRECT_URL}/{model}"

        sanitized_parameters = self._sanitize_parameters(parameters)

        # Generation definitely requires authentication
        return await self._authenticated_request(url, method="POST", json_data=sanitized_parameters, require_auth=True)


    async def get_queued_result(self, url: str) -> Dict[str, Any]:
        """
        Get the result of a previously initiated queued request using its response URL.

        Args:
            url: The 'response_url' obtained from the result of a queued 'generate_content' call.

        Returns:
            The generation result from the completed queued job.

        Raises:
            NotAuthorizedError: If the fal.ai API key is not found.
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            get, result, queued, async_job, fal-ai
        """
        # Accessing job results requires authentication
        return await self._authenticated_request(url, method="GET", require_auth=True)


    async def check_queued_status(self, url: str) -> Dict[str, Any]:
        """
        Check the status of a previously initiated queued request using its status URL.

        Args:
            url: The 'status_url' obtained from the result of a queued 'generate_content' call.

        Returns:
            A dictionary containing the current status of the queued request.

        Raises:
            NotAuthorizedError: If the fal.ai API key is not found.
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            check, status, queued, async_job, fal-ai
        """
        # Checking job status requires authentication
        return await self._authenticated_request(url, method="GET", require_auth=True)

    async def cancel_queued_request(self, url: str) -> Dict[str, Any]:
        """
        Cancel a currently running queued request using its cancel URL.

        Args:
            url: The 'cancel_url' obtained from the result of a queued 'generate_content' call.

        Returns:
            The result of the cancellation attempt, usually a status confirmation.

        Raises:
            NotAuthorizedError: If the fal.ai API key is not found.
            ToolError: If the API request fails (likely due to Cloudflare block or server issue).

        Tags:
            cancel, queued, async_job, fal-ai, management
        """
        # Cancelling a job requires authentication
        return await self._authenticated_request(url, method="PUT", require_auth=True)

    async def upload_file(self, path: str) -> Dict[str, Any]:
        """
        Upload a local file to fal.ai storage (CDN).

        Args:
            path: The absolute path to the file on the local filesystem.

        Returns:
            Information about the uploaded file, including the 'file_url' which can be used
            in subsequent fal.ai API calls (e.g., image generation).

        Raises:
            FileNotFoundError: If the file does not exist at the specified path.
            NotAuthorizedError: If the fal.ai API key is not found.
            ToolError: If the API request(s) for initiating or performing the upload fail.

        Tags:
            upload, file, storage, fal-ai, important
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        filename = os.path.basename(path)
        file_size = os.path.getsize(path)

        content_type = mimetypes.guess_type(path)[0]
        if not content_type:
            content_type = "application/octet-stream"

        # Step 1: Initiate the upload - This step *requires* authentication
        initiate_url = f"{FAL_REST_URL}/storage/upload/initiate" # Query param 'storage_type' added by _authenticated_request
        initiate_payload = {
            "content_type": content_type,
            "file_name": filename
        }

        # Use authenticated request for initiation, which also gets our browser-like headers
        initiate_response = await self._authenticated_request(
            url=initiate_url,
            method="POST",
            json_data=initiate_payload,
            params={"storage_type": "fal-cdn-v3"},
            timeout=30.0, # Use a shorter timeout for initiation
            require_auth=True # Requires authentication
        )

        file_url = initiate_response.get("file_url")
        upload_url = initiate_response.get("upload_url")

        if not file_url or not upload_url:
             raise ToolError(f"Fal.ai upload initiation failed for {filename}: Missing file_url or upload_url in response. Response: {initiate_response}")

        # Step 2: Upload the file content
        try:
            async with aiofiles.open(path, "rb") as file:
                file_content = await file.read()

                # This PUT request to the upload_url obtained from step 1 typically does NOT
                # use the Authorization header, as it's a temporary signed URL.
                # So we correctly use a standard httpx.AsyncClient here without our custom helper.
                # We still add Content-Type, which is necessary for the upload.
                async with httpx.AsyncClient(timeout=self.default_timeout) as client:
                     upload_response = await client.put(
                         upload_url,
                         content=file_content,
                         headers={"Content-Type": content_type} # Important to set the content type
                     )
                     upload_response.raise_for_status() # Check for upload errors

            # Return metadata including the final file_url provided by the initiate step
            return {
                "file_url": file_url,
                "file_name": filename,
                "file_size": file_size,
                "content_type": content_type
            }
        except FileNotFoundError: # Defensive check, should be caught earlier
             raise FileNotFoundError(f"File not found during upload process: {path}")
        except httpx.HTTPStatusError as e:
             # Specific error handling for the PUT request
             # Include response text/content info for better debugging
             response_body_info = f"HTTP error {e.response.status_code} at {upload_url}"
             response_body_hex = ""
             try:
                 decoded_text = e.response.content.decode(e.response.encoding or 'utf-8', errors='replace')
                 response_body_info += f" - Body (decoded, potentially incomplete/replaced): {decoded_text[:500]}..."
             except Exception:
                 response_body_hex = e.response.content[:200].hex()
                 response_body_info += f" - Raw content (truncated hex): {response_body_hex}..."

             details = {"response_body_decoded": decoded_text[:500] if 'decoded_text' in locals() else None,
                        "response_content_hex": response_body_hex if response_body_hex else None,
                        "response_encoding_attempted": e.response.encoding or 'utf-8'}

             details_str = json.dumps(details) if isinstance(details, dict) else str(details)

             raise ToolError(f"Fal.ai file upload (PUT) failed for {filename}: {response_body_info}. Details: {details_str}") from e
        except httpx.RequestError as e:
             # Specific error handling for network issues during PUT
             raise ToolError(f"Fal.ai file upload (PUT) request failed for {filename} at {upload_url}: Request error - {str(e)}") from e
        except UnicodeDecodeError as e:
             # Specifically catch UnicodeDecodeError during upload PUT if it happens
             # This is less likely for a PUT of binary data, but included for robustness.
             raise ToolError(f"An unexpected decoding error occurred during Fal.ai file upload (PUT) request to {upload_url}: {e}") from e
        except Exception as e:
             # Catch any other unexpected errors during file reading or PUT
             raise ToolError(f"An unexpected error occurred during Fal.ai file upload for {filename}: {e}") from e


    def list_tools(self):
        """Returns a list of methods exposed as tools by the FalAiApp."""
        return [
            self.list_models,
            self.search_models,
            self.get_model_schema,
            self.generate_content,
            self.get_queued_result,
            self.check_queued_status,
            self.cancel_queued_request,
            self.upload_file,
        ]