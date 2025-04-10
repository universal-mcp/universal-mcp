from typing import Any

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
            raise ValueError("Integration not configured for GmailApp")
        credentials = self.integration.get_credentials()
        if not credentials:
            logger.warning("No Gmail credentials found via integration.")
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
        response.raise_for_status()
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
        response.raise_for_status()
        return response.json()

    def create_file(
        self, 
        name: str, 
        content: str | bytes = None,
        mime_type: str = "text/plain",
        parent_folder_id: str = None
    ) -> dict[str, Any]:
        """
        Create a new file in Google Drive.
        
        Args:
            name: Name of the file to create
            content: Content of the file as text string or binary data (for images/PDFs/etc)
                    Do NOT Base64 encode binary content - pass the raw bytes directly
            mime_type: MIME type of the file (default: text/plain)
                       For images use: image/jpeg, image/png, etc.
            parent_folder_id: ID of the parent folder (optional)
        
        Returns:
            A dictionary containing the created file's metadata.
        """
        metadata = {"name": name}
        
        if mime_type:
            metadata["mimeType"] = mime_type
        
        if parent_folder_id:
            metadata["parents"] = [parent_folder_id]
        
       
        
        url = f"{self.base_url}/files?uploadType=media"
        headers = self._get_headers()
        
        from requests import Session
        session = Session()
        media_response = session.post(
            url,
            headers={
                "Authorization": headers["Authorization"],
                "Content-Type": mime_type
            },
            data=content  
        )
        media_response.raise_for_status()
        file_id = media_response.json().get('id')
        
        if file_id:
            metadata_url = f"{self.base_url}/files/{file_id}"
            patch_response = session.patch(
                metadata_url,
                headers={
                    "Authorization": headers["Authorization"],
                    "Content-Type": "application/json"
                },
                json=metadata
            )
            patch_response.raise_for_status()
            return patch_response.json()
        
        return media_response.json()

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
        response.raise_for_status()
        return response.json()

    def update_file(
        self, 
        file_id: str, 
        content: str | bytes = None,
        name: str = None,
        mime_type: str = None,
        add_parent_folder_id: str = None,
        remove_parent_folder_id: str = None
    ) -> dict[str, Any]:
        """
        Update an existing file in Google Drive.
        
        Args:
            file_id: ID of the file to update
            content: New content for the file as string or binary data
            name: New name for the file (if None, name remains unchanged)
            mime_type: New MIME type for the file (for content updates)
            add_parent_folder_id: ID of the parent folder to add
            remove_parent_folder_id: ID of the parent folder to remove
        
        Returns:
            A dictionary containing the updated file's metadata.
        """
        metadata = {}
        query_params = {}
        
        if name:
            metadata["name"] = name
            
        if add_parent_folder_id:
            query_params["addParents"] = add_parent_folder_id
        if remove_parent_folder_id:
            query_params["removeParents"] = remove_parent_folder_id
        
      
        
        url = f"{self.base_url}/files/{file_id}?uploadType=media"
        content_type = mime_type if mime_type else "text/plain"
        
        if isinstance(content, str) and content_type.startswith('text/'):
            content = content.encode('utf-8')
        
        from requests import Session
        session = Session()
        
        headers = self._get_headers()
        headers["Content-Type"] = content_type
        
        media_response = session.patch(
            url,
            headers=headers,
            data=content
        )
        media_response.raise_for_status()
        
        if metadata or query_params:
            metadata_url = f"{self.base_url}/files/{file_id}"
            
            if query_params:
                metadata_url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
            
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
                
            patch_response = session.patch(
                metadata_url,
                headers=headers,
                json=metadata
            )
            patch_response.raise_for_status()
            return patch_response.json()
        
        return media_response.json()

    def list_tools(self):
        """Returns a list of methods exposed as tools."""
        return [
            self.get_drive_info,
            self.list_files,
            self.create_file,
            self.get_file,
            self.update_file,
        ]