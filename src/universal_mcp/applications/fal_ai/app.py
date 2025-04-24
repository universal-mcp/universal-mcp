# universal_mcp/applications/fal_ai/app.py

import asyncio
import logging  # Used for standard library logging, aligning with fal_client if needed, but loguru is preferred for tool logging.
from typing import Any, Optional, Literal, Dict
from pathlib import Path

# Import necessary components from the fal_client library
# The fal_client library is assumed to be installed and handle its own auth
from fal_client import (
    AsyncClient,
    AsyncRequestHandle,
    Status,
    Queued,
    InProgress,
    Completed,
)

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from universal_mcp.exceptions import ToolError
from loguru import logger # Using loguru for consistent tool logging

# Setup logging for the fal_client itself to be visible via loguru
# This pipes fal_client's internal logs through loguru
logging.basicConfig(handlers=[logger.sink], level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING) # Suppress chatty httpx logs
logging.getLogger("httpx_sse").setLevel(logging.WARNING) # Suppress chatty httpx_sse logs

Priority = Literal["normal", "low"]

class FalAiApp(APIApplication):
    """
    Application for interacting with the Fal AI platform.

    Provides tools to run, submit, check status, retrieve results, cancel jobs,
    upload files to the Fal CDN, and a specialized tool for generating images.

    Authentication is handled by the underlying fal_client library, typically
    via the FAL_KEY environment variable.
    """

    def __init__(self, integration: Optional[Integration] = None, **kwargs) -> None:
        """
        Initialize the Fal AI Application.

        Args:
            integration: The integration instance (ignored by FalClient which uses env vars).
            **kwargs: Additional keyword arguments passed to APIApplication.
        """
        # The Fal client handles its own authentication via env vars (FAL_KEY etc.).
        # So, we initialize it without passing explicit credentials from the integration.
        # The `integration` parameter exists here to match the expected signature
        # for APIApplication subclasses, but its value isn't directly used by self._fal_client.
        super().__init__(name="fal_ai", integration=integration, **kwargs)
        self._fal_client = AsyncClient()  # Instantiate the async client

        logger.info("FalAIApp initialized with AsyncClient.")

    async def run(
        self,
        arguments: Any,
        application: str = "fal-ai/flux/dev", 
        path: str = "",
        timeout: Optional[float] = None,
        hint: Optional[str] = None,
    ) -> Any:
        """
        Run a Fal AI application directly and wait for the result.

        This is suitable for short-running applications. Execution is synchronous
        from the caller's perspective, but the tool itself uses Fal's async client.

        Args:
            application: The name or ID of the Fal application. Currently limited
                         to "fal-ai/flux/dev" by the tool's Literal type hint.
            arguments: A dictionary of arguments for the application.
            path: Optional subpath for the application endpoint.
            timeout: Optional timeout in seconds for the request.
            hint: Optional hint for runner selection.

        Returns:
            Any: The result of the application execution (JSON response converted to Python dict/list).

        Raises:
            ToolError: If the Fal API request fails.

        Tags:
            fal, ai, run, important
        """
        logger.info(f"Running Fal application: {application}") # Log arguments less verbosely
        try:
            result = await self._fal_client.run(
                application=application,
                arguments=arguments,
                path=path,
                timeout=timeout,
                hint=hint,
            )
            logger.info(f"Fal application {application} run completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error running Fal application {application}: {e}", exc_info=True)
            raise ToolError(f"Failed to run Fal application {application}: {e}") from e


    async def submit(
        self,
        arguments: Any,
        application: str = "fal-ai/flux/dev", 
        path: str = "",
        hint: Optional[str] = None,
        webhook_url: Optional[str] = None,
        priority: Optional[Priority] = None,
    ) -> str:
        """
        Submit a request to the Fal AI queue for asynchronous processing.

        This is suitable for long-running applications. The tool returns the request ID
        immediately. Use the `status` and `result` tools with this ID to monitor
        and retrieve the result.

        Args:
            application: The name or ID of the Fal application. Currently limited
                         to "fal-ai/flux/dev" by the tool's Literal type hint.
            arguments: A dictionary of arguments for the application.
            path: Optional subpath for the application endpoint.
            hint: Optional hint for runner selection.
            webhook_url: Optional URL to receive a webhook when the request completes.
            priority: Optional queue priority ('normal' or 'low').

        Returns:
            str: The request ID of the submitted job.

        Raises:
            ToolError: If the Fal API request fails.

        Tags:
            fal, ai, submit, async_job, start, important
        """
        logger.info(f"Submitting Fal application: {application}") # Log arguments less verbosely
        try:
            handle: AsyncRequestHandle = await self._fal_client.submit(
                application=application,
                arguments=arguments,
                path=path,
                hint=hint,
                webhook_url=webhook_url,
                priority=priority, # Pass priority
            )
            request_id = handle.request_id
            logger.info(f"Fal application {application} submitted with request_id: {request_id}")
            return request_id
        except Exception as e:
            logger.error(f"Error submitting Fal application {application}: {e}", exc_info=True)
            raise ToolError(f"Failed to submit Fal application {application}: {e}") from e

    async def status(
        self,
        request_id: str,
        application: str = "fal-ai/flux/dev",
        with_logs: bool = False
    ) -> Status:
        """
        Check the status of a submitted Fal AI request.

        Args:
            application: The name or ID of the Fal application. Currently limited
                         to "fal-ai/flux/dev" by the tool's Literal type hint.
            request_id: The ID of the submitted request obtained from `submit`.
            with_logs: Whether to include logs in the status response.

        Returns:
            Status: An object indicating the status (Queued, InProgress, or Completed).

        Raises:
            ToolError: If the Fal API request fails or the request ID is invalid.

        Tags:
            fal, ai, status, async_job
        """
        logger.info(f"Checking status for Fal request_id: {request_id} (App: {application})")
        try:
            handle = self._fal_client.get_handle(application=application, request_id=request_id)
            status = await handle.status(with_logs=with_logs)
            logger.info(f"Status for request_id {request_id}: {type(status).__name__}")
            return status
        except Exception as e:
            logger.error(f"Error getting status for Fal request_id {request_id}: {e}", exc_info=True)
            raise ToolError(f"Failed to get status for Fal request_id {request_id}: {e}") from e

    async def result(
        self,
        request_id: str,
        application: str = "fal-ai/flux/dev"
    ) -> Any:
        """
        Retrieve the result of a completed Fal AI request.

        This tool will wait until the request is completed if it's still running.

        Args:
            application: The name or ID of the Fal application. Currently limited
                         to "fal-ai/flux/dev" by the tool's Literal type hint.
            request_id: The ID of the submitted request.

        Returns:
            Any: The result of the application execution (JSON response converted to Python dict/list).

        Raises:
            ToolError: If the Fal API request fails or the request did not complete successfully.

        Tags:
            fal, ai, result, async_job
        """
        logger.info(f"Getting result for Fal request_id: {request_id} (App: {application})")
        try:
            handle = self._fal_client.get_handle(application=application, request_id=request_id)
            result = await handle.get()
            logger.info(f"Result retrieved for request_id {request_id} successfully.")
            return result
        except Exception as e:
            logger.error(f"Error getting result for Fal request_id {request_id}: {e}", exc_info=True)
            raise ToolError(f"Failed to get result for Fal request_id {request_id}: {e}") from e

    async def cancel(
        self,
        request_id: str,
        application: str = "fal-ai/flux/dev"
    ) -> None:
        """
        Cancel a submitted Fal AI request.

        Args:
            application: The name or ID of the Fal application. Currently limited
                         to "fal-ai/flux/dev" by the tool's Literal type hint.
            request_id: The ID of the submitted request.

        Raises:
            ToolError: If the Fal API request fails or the request cannot be cancelled.

        Tags:
            fal, ai, cancel, async_job
        """
        logger.info(f"Cancelling Fal request_id: {request_id} (App: {application})")
        try:
            handle = self._fal_client.get_handle(application=application, request_id=request_id)
            await handle.cancel()
            logger.info(f"Request_id {request_id} cancelled successfully.")
            return None
        except Exception as e:
            logger.error(f"Error cancelling Fal request_id {request_id}: {e}", exc_info=True)
            raise ToolError(f"Failed to cancel Fal request_id {request_id}: {e}") from e

    async def upload_file(self, path: str) -> str:
        """
        Upload a local file to the Fal CDN.

        Note: The file must be accessible from the machine running the Universal MCP server.

        Args:
            path: The absolute or relative path to the local file.

        Returns:
            str: The public URL of the uploaded file on the CDN.

        Raises:
            ToolError: If the file is not found or the upload fails.

        Tags:
            fal, upload, file, important
        """
        logger.info(f"Uploading file to Fal CDN: {path}")
        try:
            # Use Path object as expected by fal_client.upload_file
            file_url = await self._fal_client.upload_file(Path(path))
            logger.info(f"File {path} uploaded successfully to {file_url}")
            return file_url
        except FileNotFoundError:
            logger.error(f"File not found for upload: {path}", exc_info=True)
            raise ToolError(f"File not found: {path}")
        except Exception as e:
            logger.error(f"Error uploading file {path} to Fal CDN: {e}", exc_info=True)
            raise ToolError(f"Failed to upload file {path}: {e}") from e

    async def generate_image(
        self,
        prompt: str,
        seed: Optional[int] = 6252023,
        image_size: Optional[str] = "landscape_4_3",
        num_images: Optional[int] = 1,
        extra_arguments: Optional[Dict[str, Any]] = None,
        # Pass-through arguments for the underlying fal_client.run call
        path: str = "",
        timeout: Optional[float] = None,
        hint: Optional[str] = None,
    ) -> Any:
        """
        Generate an image using the 'fal-ai/flux/dev' application.

        This tool simplifies the process of generating an image by providing default
        values for common arguments like seed, image size, and number of images.
        It uses the `run` method internally, waiting for the result.

        Args:
            prompt: The text prompt to use for image generation.
            seed: Optional random seed for reproducibility. Defaults to 6252023.
            image_size: Optional image size. Defaults to "landscape_4_3".
            num_images: Optional number of images to generate. Defaults to 1.
            extra_arguments: Optional dictionary of additional arguments to pass
                             to the 'fal-ai/flux/dev' application, potentially
                             overriding the defaults (seed, image_size, num_images)
                             or adding others.
            path: Optional subpath for the application endpoint (rarely needed for Flux).
            timeout: Optional timeout in seconds for the request.
            hint: Optional hint for runner selection.

        Returns:
            Any: The result of the image generation, typically a dictionary
                 containing the generated image URLs.

        Raises:
            ToolError: If the image generation request fails.

        Tags:
            fal, ai, generate, image, important, default
        """
        application = "fal-ai/flux/dev"

        # Build the arguments dictionary
        arguments = {
            "prompt": prompt,
            "seed": seed,
            "image_size": image_size,
            "num_images": num_images,
        }

        # Merge extra arguments, allowing them to override defaults
        if extra_arguments:
            arguments.update(extra_arguments)
            logger.debug(f"Merged extra_arguments. Final arguments: {arguments}")

        try:
            # Call the underlying run method
            result = await self.run(
                application=application,
                arguments=arguments,
                path=path,
                timeout=timeout,
                hint=hint,
            )
            logger.info(f"Image generation completed successfully for prompt: '{prompt[:50]}...'")
            return result
        except Exception as e:
             raise # Re-raise the ToolError from self.run

    def list_tools(self) -> list[callable]:
        """
        List the available tools from the Fal AI application.

        These tools wrap methods of the fal_client.AsyncClient.

        Returns:
            list[callable]: A list of callable tool functions/methods.
        """
        return [
            self.run,
            self.submit,
            self.status,
            self.result,
            self.cancel,
            self.upload_file,
            self.generate_image,
        ]