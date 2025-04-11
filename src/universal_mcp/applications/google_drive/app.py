from typing import Any
import json
import uuid

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
    
    def _send_content(self, method, url, content, content_type=None, params=None):
        """
        Helper method to send raw content using httpx.
        Only used internally by this class.
        
        Args:
            method: HTTP method to use ('post', 'patch', etc.)
            url: The URL to send to
            content: The raw content to send
            content_type: The content type to use
            params: Optional query parameters
        
        Returns:
            The httpx Response object
        """
        try:
            headers = self._get_headers()
            if content_type:
                headers["Content-Type"] = content_type
                
            if method.lower() == 'post':
                response = httpx.post(url, headers=headers, content=content, params=params)
            elif method.lower() == 'patch':
                response = httpx.patch(url, headers=headers, content=content, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error sending content to {url}: {e}")
            raise e
            
    def _send_multipart(self, url, metadata, content, mime_type):
        """
        Helper method to upload both metadata and content in a single multipart request.
        
        Args:
            url: The URL to send to
            metadata: The metadata for the file
            content: The content of the file
            mime_type: The MIME type of the content
            
        Returns:
            The httpx Response object
        """
        try:
            # Generate a unique boundary for the multipart request
            boundary = f"boundary_{uuid.uuid4().hex}"
            
            # Get the authorization header
            auth_headers = self._get_headers()
            
            # Create the multipart request
            headers = {
                "Authorization": auth_headers["Authorization"],
                "Content-Type": f"multipart/related; boundary={boundary}"
            }
            
            # Prepare the multipart body
            body = []
            
            # Add the metadata part
            body.append(f"--{boundary}")
            body.append("Content-Type: application/json; charset=UTF-8")
            body.append("")
            body.append(json.dumps(metadata))
            
            # Add the media part
            body.append(f"--{boundary}")
            body.append(f"Content-Type: {mime_type}")
            body.append("")
            
            # Convert body to string and append content
            body_str = "\r\n".join(body) + "\r\n"
            
            # Convert content to bytes if it's a string
            if isinstance(content, str):
                content = content.encode("utf-8")
                
            # Create the full request body
            full_body = body_str.encode("utf-8") + content + f"\r\n--{boundary}--".encode("utf-8")
            
            # Send the request
            response = httpx.post(url, headers=headers, content=full_body)
            response.raise_for_status()
            return response
            
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Error sending multipart request to {url}: {e}")
            raise e

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
                       For Google Workspace files use:
                       - application/vnd.google-apps.document (Google Doc)
                       - application/vnd.google-apps.spreadsheet (Google Sheet)
                       - application/vnd.google-apps.presentation (Google Slides)
                       For images use: image/jpeg, image/png, etc.
            parent_folder_id: ID of the parent folder (optional)
        
        Returns:
            A dictionary containing the created file's metadata.
        """
        # Prepare metadata
        metadata = {"name": name, "mimeType": mime_type}
        
        if parent_folder_id:
            metadata["parents"] = [parent_folder_id]
        
        # If we don't have content, just create a file with metadata
        if content is None or content == "":
            url = f"{self.base_url}/files"
            response = self._post(url, data=metadata)
            return response.json()
        
        # Case 2: Two-step approach for text content (create empty file first, then update content)
        # This is more reliable for some Google Drive operations
        if isinstance(content, str) and mime_type.startswith('text/'):
            # Step 1: Create an empty file with metadata
            create_url = f"{self.base_url}/files"
            create_response = self._post(create_url, data=metadata)
            file_data = create_response.json()
            file_id = file_data.get("id")
            
            # Step 2: Update the file with content
            upload_url = f"{self.base_url}/upload/drive/v3/files/{file_id}?uploadType=media"
            upload_headers = self._get_headers()
            upload_headers["Content-Type"] = f"{mime_type}; charset=utf-8"
            
            upload_response = httpx.patch(
                upload_url,
                headers=upload_headers,
                content=content.encode("utf-8")
            )
            upload_response.raise_for_status()
            return upload_response.json()
        
        # Case 3: Multipart upload for binary data or more complex uploads
        url = f"{self.base_url}/files?uploadType=multipart"
        response = self._send_multipart(url, metadata, content, mime_type)
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
            
        if mime_type:
            metadata["mimeType"] = mime_type
            
        if add_parent_folder_id:
            query_params["addParents"] = add_parent_folder_id
        if remove_parent_folder_id:
            query_params["removeParents"] = remove_parent_folder_id
        
        # Step 1: Update the file content if provided
        media_response = None
        if content is not None:
            url = f"{self.base_url}/files/{file_id}?uploadType=media"
            content_type = mime_type if mime_type else "text/plain"
            
            if isinstance(content, str) and content_type.startswith('text/'):
                content = content.encode('utf-8')
            
            # Use our helper method for content upload
            media_response = self._send_content('patch', url, content, content_type=content_type)
        
        # Step 2: Update metadata if needed
        if metadata or query_params:
            metadata_url = f"{self.base_url}/files/{file_id}"
            
            if query_params:
                metadata_url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
            
            patch_response = self._patch(metadata_url, data=metadata)
            return patch_response.json()
        
        return media_response.json() if media_response else {"id": file_id, "status": "No changes made"}

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
            self.create_file,
            self.create_file_from_text,
            self.get_file,
            self.update_file,
            self.delete_file,
        ]