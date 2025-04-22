from typing import Any

import httpx
from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GoogleDriveApp(APIApplication):
    """
    Application for interacting with Google Drive API.
    Provides tools to manage files, folders, and access Drive information.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="google-drive", integration=integration)
        self.base_url = "https://www.googleapis.com/drive/v3"

    def get_drive_info(self) -> dict[str, Any]:
        """
        Retrieves detailed information about the user's Google Drive storage and account.

        Returns:
            A dictionary containing Drive information including storage quota (usage, limit) and user details (name, email, etc.).

        Raises:
            HTTPError: If the API request fails or returns an error status code
            ConnectionError: If there are network connectivity issues
            AuthenticationError: If the authentication credentials are invalid or expired

        Tags:
            get, info, storage, drive, quota, user, api, important
        """
        url = f"{self.base_url}/about"
        params = {"fields": "storageQuota,user"}
        response = self._get(url, params=params)
        return response.json()

    def list_files(
        self, page_size: int = 10, query: str = None, order_by: str = None
    ) -> dict[str, Any]:
        """
        Lists and retrieves files from Google Drive with optional filtering, pagination, and sorting.

        Args:
            page_size: Maximum number of files to return per page (default: 10)
            query: Optional search query string using Google Drive query syntax (e.g., "mimeType='image/jpeg'")
            order_by: Optional field name to sort results by, with optional direction (e.g., "modifiedTime desc")

        Returns:
            Dictionary containing a list of files and metadata, including 'files' array and optional 'nextPageToken' for pagination

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code
            RequestException: Raised when network connectivity issues occur during the API request

        Tags:
            list, files, search, google-drive, pagination, important
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

    def get_file(self, file_id: str) -> dict[str, Any]:
        """
        Retrieves detailed metadata for a specific file using its ID.

        Args:
            file_id: String identifier of the file whose metadata should be retrieved

        Returns:
            Dictionary containing the file's metadata including properties such as name, size, type, and other attributes

        Raises:
            HTTPError: When the API request fails due to invalid file_id or network issues
            JSONDecodeError: When the API response cannot be parsed as JSON

        Tags:
            retrieve, file, metadata, get, api, important
        """
        url = f"{self.base_url}/files/{file_id}"
        response = self._get(url)
        return response.json()

    def delete_file(self, file_id: str) -> dict[str, Any]:
        """
        Deletes a specified file from Google Drive and returns a status message.

        Args:
            file_id: The unique identifier string of the file to be deleted from Google Drive

        Returns:
            A dictionary containing either a success message {'message': 'File deleted successfully'} or an error message {'error': 'error description'}

        Raises:
            Exception: When the DELETE request fails due to network issues, invalid file_id, insufficient permissions, or other API errors

        Tags:
            delete, file-management, google-drive, api, important
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
        mime_type: str = "text/plain",
    ) -> dict[str, Any]:
        """
        Creates a new file in Google Drive with specified text content and returns the file's metadata.

        Args:
            file_name: Name of the file to create on Google Drive
            text_content: Plain text content to be written to the file
            parent_id: Optional ID of the parent folder where the file will be created
            mime_type: MIME type of the file (defaults to 'text/plain')

        Returns:
            Dictionary containing metadata of the created file including ID, name, and other Google Drive file properties

        Raises:
            HTTPStatusError: Raised when the API request fails during file creation or content upload
            UnicodeEncodeError: Raised when the text_content cannot be encoded in UTF-8

        Tags:
            create, file, upload, drive, text, important, storage, document
        """
        metadata = {"name": file_name, "mimeType": mime_type}
        if parent_id:
            metadata["parents"] = [parent_id]
        create_url = f"{self.base_url}/files"
        create_response = self._post(create_url, data=metadata)
        file_data = create_response.json()
        file_id = file_data.get("id")
        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        upload_headers = self._get_headers()
        upload_headers["Content-Type"] = f"{mime_type}; charset=utf-8"
        upload_response = httpx.patch(
            upload_url, headers=upload_headers, content=text_content.encode("utf-8")
        )
        upload_response.raise_for_status()
        response_data = upload_response.json()
        return response_data

    def find_folder_id_by_name(self, folder_name: str) -> str | None:
        """
        Searches for and retrieves a Google Drive folder's ID using its name.

        Args:
            folder_name: The name of the folder to search for in Google Drive

        Returns:
            str | None: The folder's ID if a matching folder is found, None if no folder is found or if an error occurs

        Raises:
            Exception: Caught internally and logged when API requests fail or response parsing errors occur

        Tags:
            search, find, google-drive, folder, query, api, utility
        """
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        try:
            response = self._get(
                f"{self.base_url}/files",
                params={"q": query, "fields": "files(id,name)"},
            )
            files = response.json().get("files", [])
            return files[0]["id"] if files else None
        except Exception as e:
            logger.error(f"Error finding folder ID by name: {e}")
            return None

    def create_folder(self, folder_name: str, parent_id: str = None) -> dict[str, Any]:
        """
        Creates a new folder in Google Drive with optional parent folder specification

        Args:
            folder_name: Name of the folder to create
            parent_id: ID or name of the parent folder. Can be either a folder ID string or a folder name that will be automatically looked up

        Returns:
            Dictionary containing the created folder's metadata including its ID, name, and other Drive-specific information

        Raises:
            ValueError: Raised when a parent folder name is provided but cannot be found in Google Drive

        Tags:
            create, folder, drive, storage, important, management
        """
        import re

        metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            if not re.match(r"^[a-zA-Z0-9_-]{28,33}$", parent_id):
                found_id = self.find_folder_id_by_name(parent_id)
                if found_id:
                    metadata["parents"] = [found_id]
                else:
                    raise ValueError(
                        f"Could not find parent folder with name: {parent_id}"
                    )
            else:
                metadata["parents"] = [parent_id]
        url = f"{self.base_url}/files"
        params = {"supportsAllDrives": "true"}
        response = self._post(url, data=metadata, params=params)
        return response.json()

    def upload_a_file(
        self,
        file_name: str,
        file_path: str,
        parent_id: str = None,
        mime_type: str = None,
    ) -> dict[str, Any]:
        """
        Uploads a file to Google Drive by creating a file metadata entry and uploading the binary content.

        Args:
            file_name: Name to give the file on Google Drive
            file_path: Path to the local file to upload
            parent_id: Optional ID of the parent folder to create the file in
            mime_type: MIME type of the file (e.g., 'image/jpeg', 'image/png', 'application/pdf')

        Returns:
            Dictionary containing the uploaded file's metadata from Google Drive

        Raises:
            FileNotFoundError: When the specified file_path does not exist or is not accessible
            HTTPError: When the API request fails or returns an error status code
            IOError: When there are issues reading the file content

        Tags:
            upload, file-handling, google-drive, api, important, binary, storage
        """
        metadata = {"name": file_name, "mimeType": mime_type}
        if parent_id:
            metadata["parents"] = [parent_id]
        create_url = f"{self.base_url}/files"
        create_response = self._post(create_url, data=metadata)
        file_data = create_response.json()
        file_id = file_data.get("id")
        with open(file_path, "rb") as file_content:
            binary_content = file_content.read()

            upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
            upload_headers = self._get_headers()
            upload_headers["Content-Type"] = mime_type

            upload_response = httpx.patch(
                upload_url, headers=upload_headers, content=binary_content
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
            self.upload_a_file,
            self.find_folder_id_by_name,
            self.create_folder,
            self.get_file,
            self.delete_file,
        ]
