# universal_mcp/applications/fal_ai/app.py

import asyncio  # Needed for async operations
from typing import Any, Optional, Literal
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
from universal_mcp.exceptions import ToolError  # Use universal-mcp's ToolError for expected tool failures
from loguru import logger # Use loguru for logging consistency

Priority = Literal["normal", "low"]
class FalAiApp(APIApplication):
    """
    Application for interacting with the Fal AI platform.

    Provides tools to run, submit, check status, retrieve results, cancel jobs,
    and upload files to the Fal CDN.

    Authentication is handled by the underlying fal_client library, typically
    via the FAL_KEY environment variable.
    """

    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initialize the Fal AI Application.

        Args:
            integration: The integration instance (ignored by FalClient which uses env vars).
            **kwargs: Additional keyword arguments.
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
        application: Literal["fal-ai/flux/dev"] , # Set default value here
        arguments: Any,
        path: str = "",
        timeout: Optional[float] = None,
        hint: Optional[str] = None,
    ) -> Any:
        """
        Run a Fal AI application directly and wait for the result.

        This is suitable for short-running applications. Execution is synchronous
        from the caller's perspective, but the tool itself uses Fal's async client.

        Args:
            application: The name or ID of the Fal application.
                         Defaults to "fal-ai/flux/dev" for text-to-image.
            arguments: A dictionary of arguments for the application.
            path: Optional subpath for the application endpoint.
            timeout: Optional timeout in seconds for the request.
            hint: Optional hint for runner selection.

        Returns:
            Any: The result of the application execution (JSON response converted to Python dict/list).

        Tags:
            fal, ai, run, important
        """
        logger.info(f"Running Fal application: {application} with args: {arguments}")
        try:
            result = await self._fal_client.run(
                application=application,
                arguments=arguments,
                path=path,
                timeout=timeout,
                hint=hint,
            )
            logger.info(f"Fal application {application} run completed.")
            return result
        except Exception as e:
            logger.error(f"Error running Fal application {application}: {e}")
            # Raise as ToolError to provide context within MCP
            raise ToolError(f"Failed to run Fal application {application}: {e}") from e


    async def submit(
        self,
        application: Literal["fal-ai/flux/dev"],
        arguments: Any,
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
            application: The name or ID of the Fal application (e.g., "110602490-stable-diffusion-v1-5").
                         Defaults to "fal-ai/flux/dev" for text-to-image.
            arguments: A dictionary of arguments for the application.
            path: Optional subpath for the application endpoint.
            hint: Optional hint for runner selection.
            webhook_url: Optional URL to receive a webhook when the request completes.
            priority: Optional queue priority ('normal' or 'low').

        Returns:
            str: The request ID of the submitted job.

        Tags:
            fal, ai, submit, async_job, start, important
        """
        logger.info(f"Submitting Fal application: {application} with args: {arguments}")
        try:
            handle: AsyncRequestHandle = await self._fal_client.submit(
                application=application,
                arguments=arguments,
                path=path,
                hint=hint,
                webhook_url=webhook_url,
            )
            request_id = handle.request_id
            logger.info(f"Fal application {application} submitted with request_id: {request_id}")
            return request_id # Return just the ID
        except Exception as e:
            logger.error(f"Error submitting Fal application {application}: {e}")
            raise ToolError(f"Failed to submit Fal application {application}: {e}") from e

    async def status(
        self,
        application: Literal["fal-ai/flux/dev"],
        request_id: str,
        with_logs: bool = False
    ) -> Status:
        """
        Check the status of a submitted Fal AI request.

        Args:
            application: The name or ID of the Fal application (e.g., "110602490-stable-diffusion-v1-5").
            request_id: The ID of the submitted request obtained from `submit`.
            with_logs: Whether to include logs in the status response.

        Returns:
            Status: An object indicating the status (Queued, InProgress, or Completed).
                    This will be a Pydantic model instance.

        Tags:
            fal, ai, status, async_job, important
        """
        logger.info(f"Checking status for Fal request_id: {request_id} (App: {application})")
        try:
            # Need to get the handle first
            handle = self._fal_client.get_handle(application=application, request_id=request_id)
            status = await handle.status(with_logs=with_logs)
            logger.info(f"Status for request_id {request_id}: {type(status).__name__}")
            # Returning the dataclass object directly should work with Pydantic/JSON serialization
            return status
        except Exception as e:
            logger.error(f"Error getting status for Fal request_id {request_id}: {e}")
            raise ToolError(f"Failed to get status for Fal request_id {request_id}: {e}") from e

    async def result(
        self,
        application: Literal["fal-ai/flux/dev"],
        request_id: str
    ) -> Any:
        """
        Retrieve the result of a completed Fal AI request.

        This tool will wait until the request is completed if it's still running.

        Args:
            application: The name or ID of the Fal application (e.g., "110602490-stable-diffusion-v1-5").
            request_id: The ID of the submitted request.

        Returns:
            Any: The result of the application execution (JSON response converted to Python dict/list).

        Tags:
            fal, ai, result, async_job, important
        """
        logger.info(f"Getting result for Fal request_id: {request_id} (App: {application})")
        try:
            # Need to get the handle first
            handle = self._fal_client.get_handle(application=application, request_id=request_id)
            # .get() method of the handle waits for completion internally
            result = await handle.get()
            logger.info(f"Result retrieved for request_id {request_id}.")
            return result
        except Exception as e:
            logger.error(f"Error getting result for Fal request_id {request_id}: {e}")
            raise ToolError(f"Failed to get result for Fal request_id {request_id}: {e}") from e

    async def cancel(
        self,
        application: Literal["fal-ai/flux/dev"],
        request_id: str
    ) -> None:
        """
        Cancel a submitted Fal AI request.

        Args:
            application: The name or ID of the Fal application (e.g., "110602490-stable-diffusion-v1-5").
            request_id: The ID of the submitted request.

        Tags:
            fal, ai, cancel, async_job, important
        """
        logger.info(f"Cancelling Fal request_id: {request_id} (App: {application})")
        try:
            # Need to get the handle first
            handle = self._fal_client.get_handle(application=application, request_id=request_id)
            await handle.cancel()
            logger.info(f"Request_id {request_id} cancelled.")
            # No specific return value for cancellation success
            return None
        except Exception as e:
            logger.error(f"Error cancelling Fal request_id {request_id}: {e}")
            raise ToolError(f"Failed to cancel Fal request_id {request_id}: {e}") from e

    async def upload_file(self, path: str) -> str:
        """
        Upload a local file to the Fal CDN.

        Note: The file must be accessible from the machine running the Universal MCP server.

        Args:
            path: The absolute or relative path to the local file.

        Returns:
            str: The public URL of the uploaded file on the CDN.

        Tags:
            fal, upload, file, important
        """
        logger.info(f"Uploading file to Fal CDN: {path}")
        try:
            # Use Path object as expected by fal_client.upload_file
            file_url = await self._fal_client.upload_file(Path(path))
            logger.info(f"File {path} uploaded to {file_url}")
            return file_url
        except FileNotFoundError:
            logger.error(f"File not found for upload: {path}")
            raise ToolError(f"File not found: {path}")
        except Exception as e:
            logger.error(f"Error uploading file {path} to Fal CDN: {e}")
            raise ToolError(f"Failed to upload file {path}: {e}") from e
        
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
        ]