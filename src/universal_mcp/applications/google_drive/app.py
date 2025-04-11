from typing import Any
import json

import httpx
from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import Integration


class GoogleDriveApp(APIApplication):
    """
    Application for interacting with Google Drive API.
    Provides tools to manage files, folders, and access Drive information.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="google-drive", integration=integration)
        self.base_url = "https://www.googleapis.com/drive/v3"

    def _get_headers(self):
        if not self.integration:
            raise ValueError("Integration not configured for GoogleDriveApp")
        credentials = self.integration.get_credentials()
        if not credentials:
            logger.warning("No Google Drive credentials found via integration.")
            action = self.integration.authorize()
            raise NotAuthorizedError(action)

        if "headers" in credentials:
            return credentials["headers"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json",
        }

    def get_drive_info(self) -> dict[str, Any]:
        """
        Get information about the user's Google Drive, including storage quota and user info.
        
        Returns:
            A dictionary containing information about the user's Drive.
            Includes details like storage quota, user information, and features.
        """
        url = f"{self.base_url}/about"
        params = {"fields": "storageQuota,user"}
        
        response = self._get(url, params=params)
        return response.json()

    def list_files(self, page_size: int = 10, query: str = None, order_by: str = None) -> dict[str, Any]:
        """
        List files in the user's Google Drive.
        
        Args:
            page_size: Maximum number of files to return (default: 10)
            query: Search query using Google Drive query syntax (e.g., "mimeType='image/jpeg'")
            order_by: Field to sort by (e.g., "modifiedTime desc")
        
        Returns:
            A dictionary containing the list of files and possibly a nextPageToken.
        """
        url = f"{self.base_url}/files"
        params = {
            "pageSize": page_size,
        }
        
        if query:
            params["q"] = query
        
        if order_by:
            params["orderBy"] = order_by
        
        response = self._get(url, params=params)
        return response.json()

    def get_file(self, file_id: str) -> dict[str, Any]:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: The ID of the file to retrieve
        
        Returns:
            A dictionary containing the file's metadata.
        """
        url = f"{self.base_url}/files/{file_id}"
        response = self._get(url)
        return response.json()

    def delete_file(self, file_id: str) -> dict[str, Any]:
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: The ID of the file to delete
        
        Returns:
            A simple success message dictionary
        """
        url = f"{self.base_url}/files/{file_id}"
        try:
            self._delete(url)
            return {"message": "File deleted successfully"}
        except Exception as e:
            return {"error": str(e)}
    
    def create_file_from_text(
        self,
        file_name: str,
        text_content: str,
        parent_id: str = None,
        mime_type: str = "text/plain"
    ) -> dict[str, Any]:
        """
        Create a new file from text content in Google Drive.
        
        Args:
            file_name: Name of the file to create on Google Drive
            text_content: Plain text content to be written to the file
            parent_id: ID of the parent folder to create the file in (optional)
            mime_type: MIME type of the file (default: text/plain)
        
        Returns:
            A dictionary containing the created file's metadata.
        """
        metadata = {
            "name": file_name,
            "mimeType": mime_type
        }
        
        if parent_id:
            metadata["parents"] = [parent_id]
            
        create_url = f"{self.base_url}/files"
        create_response = self._post(create_url, data=metadata)
        file_data = create_response.json()
        file_id = file_data.get("id")
        
        # Step 2: Update the file with text content
        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        upload_headers = self._get_headers()
        upload_headers["Content-Type"] = f"{mime_type}; charset=utf-8"
        
        upload_response = httpx.patch(
            upload_url,
            headers=upload_headers,
            content=text_content.encode("utf-8")
        )
        upload_response.raise_for_status()
        
        response_data = upload_response.json()
        return response_data

    def list_tools(self):
        """Returns a list of methods exposed as tools."""
        return [
            self.get_drive_info,
            self.list_files,
            self.create_file_from_text,
            self.get_file,
            self.delete_file,
        ]