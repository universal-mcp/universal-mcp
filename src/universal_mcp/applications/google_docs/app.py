from typing import Any

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GoogleDocsApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="google-docs", integration=integration)
        self.base_api_url = "https://docs.googleapis.com/v1/documents"

    def create_document(self, title: str) -> dict[str, Any]:
        """
        Creates a new blank Google Document with the specified title and returns the API response.

        Args:
            title: The title for the new Google Document to be created

        Returns:
            A dictionary containing the Google Docs API response with document details and metadata

        Raises:
            HTTPError: If the API request fails due to network issues, authentication errors, or invalid parameters
            RequestException: If there are connection errors or timeout issues during the API request

        Tags:
            create, document, api, important, google-docs, http
        """
        url = self.base_api_url
        document_data = {"title": title}
        response = self._post(url, data=document_data)
        response.raise_for_status()
        return response.json()

    def get_document(self, document_id: str) -> dict[str, Any]:
        """
        Retrieves the latest version of a specified document from the Google Docs API.

        Args:
            document_id: The unique identifier of the document to retrieve

        Returns:
            A dictionary containing the document data from the Google Docs API response

        Raises:
            HTTPError: If the API request fails or the document is not found
            JSONDecodeError: If the API response cannot be parsed as JSON

        Tags:
            retrieve, read, api, document, google-docs, important
        """
        url = f"{self.base_api_url}/{document_id}"
        response = self._get(url)
        return response.json()

    def add_content(
        self, document_id: str, content: str, index: int = 1
    ) -> dict[str, Any]:
        """
        Adds text content at a specified position in an existing Google Document via the Google Docs API.

        Args:
            document_id: The unique identifier of the Google Document to be updated
            content: The text content to be inserted into the document
            index: The zero-based position in the document where the text should be inserted (default: 1)

        Returns:
            A dictionary containing the Google Docs API response after performing the batch update operation

        Raises:
            HTTPError: When the API request fails, such as invalid document_id or insufficient permissions
            RequestException: When there are network connectivity issues or API endpoint problems

        Tags:
            update, insert, document, api, google-docs, batch, content-management, important
        """
        url = f"{self.base_api_url}/{document_id}:batchUpdate"
        batch_update_data = {
            "requests": [
                {"insertText": {"location": {"index": index}, "text": content}}
            ]
        }
        response = self._post(url, data=batch_update_data)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [self.create_document, self.get_document, self.add_content]
