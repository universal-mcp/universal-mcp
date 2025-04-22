from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class CodaApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="coda", integration=integration, **kwargs)
        self.base_url = "https://coda.io/apis/v1"

    def list_categories(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a dictionary of available categories from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary representing the categories data from the server response.

        Raises:
            HTTPError: If the HTTP request to the categories endpoint fails or returns an error status code.

        Tags:
            list, categories, api, important
        """
        url = f"{self.base_url}/categories"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_docs(
        self,
        isOwner=None,
        isPublished=None,
        query=None,
        sourceDoc=None,
        isStarred=None,
        inGallery=None,
        workspaceId=None,
        folderId=None,
        limit=None,
        pageToken=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of documents based on specified filtering and pagination criteria.

        Args:
            isOwner: Optional[bool]. If True, filters to documents owned by the current user.
            isPublished: Optional[bool]. If True, filters to only published documents.
            query: Optional[str]. Text search query to filter documents by title or content.
            sourceDoc: Optional[str]. ID of the source document to filter derivative documents.
            isStarred: Optional[bool]. If True, filters to starred documents.
            inGallery: Optional[bool]. If True, filters to documents shown in the gallery.
            workspaceId: Optional[str]. Filters documents belonging to a specific workspace.
            folderId: Optional[str]. Filters documents within a particular folder.
            limit: Optional[int]. Maximum number of documents to return.
            pageToken: Optional[str]. Token for pagination to retrieve the next page of results.

        Returns:
            dict[str, Any]: A dictionary containing the list of documents and pagination metadata.

        Raises:
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            list, docs, filter, pagination, management, important
        """
        url = f"{self.base_url}/docs"
        query_params = {
            k: v
            for k, v in [
                ("isOwner", isOwner),
                ("isPublished", isPublished),
                ("query", query),
                ("sourceDoc", sourceDoc),
                ("isStarred", isStarred),
                ("inGallery", inGallery),
                ("workspaceId", workspaceId),
                ("folderId", folderId),
                ("limit", limit),
                ("pageToken", pageToken),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_doc(
        self, title=None, sourceDoc=None, timezone=None, folderId=None, initialPage=None
    ) -> dict[str, Any]:
        """
        Creates a new document with the specified properties and returns its metadata as a dictionary.

        Args:
            title: Optional[str]. The title of the new document.
            sourceDoc: Optional[str]. Identifier for a source document to duplicate or base the new document on.
            timezone: Optional[str]. Timezone setting for the document, if applicable.
            folderId: Optional[str]. Identifier of the folder where the document will be created.
            initialPage: Optional[dict]. Content or configuration for the initial page of the document.

        Returns:
            dict[str, Any]: A dictionary containing the metadata and details of the newly created document.

        Raises:
            requests.HTTPError: If the HTTP request to create the document fails or the server responds with an error status.

        Tags:
            create, document, api, management, important
        """
        request_body = {
            "title": title,
            "sourceDoc": sourceDoc,
            "timezone": timezone,
            "folderId": folderId,
            "initialPage": initialPage,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_doc(self, docId) -> dict[str, Any]:
        """
        Retrieves a document by its unique identifier from the remote service.

        Args:
            docId: The unique identifier of the document to retrieve. Must not be None.

        Returns:
            A dictionary containing the JSON representation of the requested document.

        Raises:
            ValueError: If 'docId' is None.
            requests.exceptions.HTTPError: If the HTTP request to retrieve the document fails.

        Tags:
            get, fetch, document, remote-access, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_doc(self, docId) -> dict[str, Any]:
        """
        Deletes a document by its ID from the remote service.

        Args:
            docId: The unique identifier of the document to delete.

        Returns:
            A dictionary containing the response data from the delete operation.

        Raises:
            ValueError: If 'docId' is None.
            HTTPError: If the HTTP request to delete the document fails.

        Tags:
            delete, document, management, important, api, http
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_doc(self, docId, title=None, iconName=None) -> dict[str, Any]:
        """
        Updates the metadata of a document, such as its title and icon, using the provided document ID.

        Args:
            docId: str. The unique identifier of the document to update. Must not be None.
            title: str, optional. The new title for the document. If None, the title is not updated.
            iconName: str, optional. The new icon name for the document. If None, the icon is not updated.

        Returns:
            dict[str, Any]: The JSON response from the API containing the updated document metadata.

        Raises:
            ValueError: Raised if 'docId' is None.
            requests.HTTPError: Raised if the HTTP request to update the document fails.

        Tags:
            update, document, api, metadata, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        request_body = {
            "title": title,
            "iconName": iconName,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sharing_metadata(self, docId) -> dict[str, Any]:
        """
        Retrieves sharing metadata for the specified document by its ID.

        Args:
            docId: str. The unique identifier of the document whose sharing metadata is to be retrieved.

        Returns:
            dict. A dictionary containing the sharing metadata of the specified document.

        Raises:
            ValueError: If the required parameter 'docId' is None.
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            get, sharing-metadata, document, api-call, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/acl/metadata"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_permissions(self, docId, limit=None, pageToken=None) -> dict[str, Any]:
        """
        Retrieves the list of permissions for a specified document.

        Args:
            docId: The unique identifier of the document whose permissions are to be fetched.
            limit: Optional; maximum number of permission records to return.
            pageToken: Optional; token indicating the page of results to retrieve for pagination.

        Returns:
            A dictionary containing the document's permissions and optional pagination data.

        Raises:
            ValueError: If 'docId' is not provided.
            requests.HTTPError: If the HTTP request to fetch permissions fails (non-success status code).

        Tags:
            get, permissions, document-management, api-call, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/acl/permissions"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_permission(
        self, docId, access, principal, suppressEmail=None
    ) -> dict[str, Any]:
        """
        Adds a permission entry for a specified document, granting access to a principal with defined access level.

        Args:
            docId: str. The unique identifier of the document to which the permission will be added.
            access: str. The type of access to grant (e.g., 'read', 'write', 'admin').
            principal: str. The identifier (email, group, or user ID) of the principal receiving access.
            suppressEmail: Optional[bool]. If True, suppresses notification emails about the permission grant. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response from the API containing details of the newly added permission.

        Raises:
            ValueError: If any of the required parameters ('docId', 'access', or 'principal') are missing or None.
            requests.HTTPError: If the HTTP request to the backend API fails or returns an error response.

        Tags:
            add, permission, management, important, api, post
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if access is None:
            raise ValueError("Missing required parameter 'access'")
        if principal is None:
            raise ValueError("Missing required parameter 'principal'")
        request_body = {
            "access": access,
            "principal": principal,
            "suppressEmail": suppressEmail,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/acl/permissions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_permission(self, docId, permissionId) -> dict[str, Any]:
        """
        Deletes a specific permission from a document by its identifier.

        Args:
            docId: str. The unique identifier of the document from which the permission will be deleted.
            permissionId: str. The unique identifier of the permission to delete from the document.

        Returns:
            dict[str, Any]: JSON response containing the result of the delete operation.

        Raises:
            ValueError: Raised if 'docId' or 'permissionId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the permission fails or returns an error response.

        Tags:
            delete, permission-management, document, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if permissionId is None:
            raise ValueError("Missing required parameter 'permissionId'")
        url = f"{self.base_url}/docs/{docId}/acl/permissions/{permissionId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_principals(self, docId, query=None) -> dict[str, Any]:
        """
        Searches for principals in the access control list of a specified document, optionally filtering results by a query string.

        Args:
            docId: str. The unique identifier of the document whose principals are to be searched.
            query: Optional[str]. A search string to filter principals. If None, all principals are returned.

        Returns:
            dict[str, Any]: The JSON response containing the list of principals matching the search criteria.

        Raises:
            ValueError: Raised if the required 'docId' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the server fails or returns an unsuccessful status code.

        Tags:
            search, acl, principals, document, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/acl/principals/search"
        query_params = {k: v for k, v in [("query", query)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_acl_settings(self, docId) -> dict[str, Any]:
        """
        Retrieves the access control settings for a specified document.

        Args:
            docId: The unique identifier of the document whose ACL settings are to be retrieved.

        Returns:
            A dictionary containing the access control settings of the specified document.

        Raises:
            ValueError: Raised when 'docId' is None.
            HTTPError: Raised if the HTTP request to retrieve ACL settings fails.

        Tags:
            get, acl, settings, document, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/acl/settings"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_acl_settings(
        self,
        docId,
        allowEditorsToChangePermissions=None,
        allowCopying=None,
        allowViewersToRequestEditing=None,
    ) -> dict[str, Any]:
        """
        Updates access control settings for a specific document.

        Args:
            docId: str. The unique identifier of the document whose ACL settings are to be updated.
            allowEditorsToChangePermissions: Optional[bool]. If set, specifies whether editors can change sharing permissions.
            allowCopying: Optional[bool]. If set, determines if viewers and commenters can copy, print, or download the document.
            allowViewersToRequestEditing: Optional[bool]. If set, indicates whether viewers can request edit access to the document.

        Returns:
            dict[str, Any]: A dictionary containing the updated ACL settings returned by the server.

        Raises:
            ValueError: If 'docId' is None.
            requests.HTTPError: If the HTTP request fails (e.g., due to invalid permissions, network errors, or the document does not exist).

        Tags:
            update, acl, settings, document, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        request_body = {
            "allowEditorsToChangePermissions": allowEditorsToChangePermissions,
            "allowCopying": allowCopying,
            "allowViewersToRequestEditing": allowViewersToRequestEditing,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/acl/settings"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def publish_doc(
        self,
        docId,
        slug=None,
        discoverable=None,
        earnCredit=None,
        categoryNames=None,
        mode=None,
    ) -> dict[str, Any]:
        """
        Publishes a document with the specified docId and optional publication settings.

        Args:
            docId: str. The unique identifier of the document to publish. Required.
            slug: str or None. Optional custom slug for the published document.
            discoverable: bool or None. Whether the document should be discoverable. Optional.
            earnCredit: bool or None. Whether publishing the document grants credit. Optional.
            categoryNames: list[str] or None. Categories to associate with the document. Optional.
            mode: str or None. The publication mode or workflow to use (if applicable). Optional.

        Returns:
            dict[str, Any]: The response from the publish API containing information about the published document.

        Raises:
            ValueError: If 'docId' is not provided.
            requests.HTTPError: If the HTTP request to publish the document fails.

        Tags:
            publish, document, api, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        request_body = {
            "slug": slug,
            "discoverable": discoverable,
            "earnCredit": earnCredit,
            "categoryNames": categoryNames,
            "mode": mode,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/publish"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def unpublish_doc(self, docId) -> dict[str, Any]:
        """
        Unpublishes a document by revoking its published status using the provided document ID.

        Args:
            docId: str. The unique identifier of the document to be unpublished.

        Returns:
            dict[str, Any]: A dictionary containing the API's response to the unpublish operation.

        Raises:
            ValueError: If 'docId' is None.
            requests.HTTPError: If the HTTP DELETE request fails with an error status code.

        Tags:
            unpublish, document-management, delete, async-job, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/publish"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pages(self, docId, limit=None, pageToken=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of pages for a specified document.

        Args:
            docId: str. The unique identifier of the document whose pages are to be listed.
            limit: Optional[int]. The maximum number of pages to return in a single response.
            pageToken: Optional[str]. The token indicating the starting point for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the paginated list of pages and any pagination metadata.

        Raises:
            ValueError: If the 'docId' parameter is not provided.
            requests.HTTPError: If the HTTP request to the API fails.

        Tags:
            list, pages, pagination, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/pages"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_page(
        self,
        docId,
        name=None,
        subtitle=None,
        iconName=None,
        imageUrl=None,
        parentPageId=None,
        pageContent=None,
    ) -> dict[str, Any]:
        """
        Creates a new page within a specified document and returns the page details.

        Args:
            docId: str. The unique identifier of the document in which the page should be created. Required.
            name: str, optional. The name of the new page.
            subtitle: str, optional. The subtitle of the new page.
            iconName: str, optional. The name of the icon to associate with the page.
            imageUrl: str, optional. The URL of an image to use for the page.
            parentPageId: str, optional. The unique identifier of the parent page, if creating a subpage.
            pageContent: Any, optional. The content to populate the new page with.

        Returns:
            dict[str, Any]: A dictionary representing the details of the created page as returned by the API.

        Raises:
            ValueError: If 'docId' is None.
            requests.HTTPError: If the API request fails or responds with an unsuccessful status code.

        Tags:
            create, page, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        request_body = {
            "name": name,
            "subtitle": subtitle,
            "iconName": iconName,
            "imageUrl": imageUrl,
            "parentPageId": parentPageId,
            "pageContent": pageContent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/pages"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_page(self, docId, pageIdOrName) -> dict[str, Any]:
        """
        Retrieves details of a specific page within a document by its ID or name.

        Args:
            docId: str. The unique identifier of the document containing the desired page.
            pageIdOrName: str. The unique identifier or name of the page to retrieve.

        Returns:
            dict[str, Any]: A dictionary containing the data for the specified page.

        Raises:
            ValueError: Raised if either 'docId' or 'pageIdOrName' is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to fetch the page fails.

        Tags:
            get, page, document, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if pageIdOrName is None:
            raise ValueError("Missing required parameter 'pageIdOrName'")
        url = f"{self.base_url}/docs/{docId}/pages/{pageIdOrName}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_page(
        self,
        docId,
        pageIdOrName,
        name=None,
        subtitle=None,
        iconName=None,
        imageUrl=None,
        isHidden=None,
        contentUpdate=None,
    ) -> dict[str, Any]:
        """
        Updates properties of a specific page within a document, sending changes to the server and returning the updated page data.

        Args:
            docId: str. Unique identifier of the document containing the page to update.
            pageIdOrName: str. Identifier or name of the page to update.
            name: str, optional. New name for the page.
            subtitle: str, optional. New subtitle for the page.
            iconName: str, optional. Icon to associate with the page.
            imageUrl: str, optional. Image URL to represent the page.
            isHidden: bool, optional. Whether the page should be hidden.
            contentUpdate: Any, optional. Content data or structure to update the page with.

        Returns:
            dict. JSON response containing the updated page data as returned by the API.

        Raises:
            ValueError: If 'docId' or 'pageIdOrName' is not provided.
            requests.HTTPError: If the HTTP request to update the page fails (non-2xx response).

        Tags:
            update, page-management, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if pageIdOrName is None:
            raise ValueError("Missing required parameter 'pageIdOrName'")
        request_body = {
            "name": name,
            "subtitle": subtitle,
            "iconName": iconName,
            "imageUrl": imageUrl,
            "isHidden": isHidden,
            "contentUpdate": contentUpdate,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/pages/{pageIdOrName}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_page(self, docId, pageIdOrName) -> dict[str, Any]:
        """
        Deletes a specific page from a document identified by docId and pageIdOrName.

        Args:
            docId: str. The unique identifier of the document from which to delete the page.
            pageIdOrName: str. The ID or name of the page to be deleted from the document.

        Returns:
            dict[str, Any]: The API response as a dictionary representing the result of the deletion.

        Raises:
            ValueError: Raised if docId or pageIdOrName is None.
            HTTPError: Raised if the HTTP request fails or returns an unsuccessful status code.

        Tags:
            delete, page-management, api, operation, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if pageIdOrName is None:
            raise ValueError("Missing required parameter 'pageIdOrName'")
        url = f"{self.base_url}/docs/{docId}/pages/{pageIdOrName}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def begin_page_content_export(
        self, docId, pageIdOrName, outputFormat
    ) -> dict[str, Any]:
        """
        Initiates an export of a specific page's content from a document in the specified format.

        Args:
            docId: The unique identifier of the document containing the page to export.
            pageIdOrName: The ID or name of the page to be exported from the document.
            outputFormat: The desired format for the exported page content (e.g., 'pdf', 'docx').

        Returns:
            A dictionary containing the response data from the export operation, typically including information about the export job or downloaded content.

        Raises:
            ValueError: Raised if 'docId', 'pageIdOrName', or 'outputFormat' is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to start the export fails (e.g., due to network issues or invalid parameters).

        Tags:
            export, async-job, start, page, document, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if pageIdOrName is None:
            raise ValueError("Missing required parameter 'pageIdOrName'")
        if outputFormat is None:
            raise ValueError("Missing required parameter 'outputFormat'")
        request_body = {
            "outputFormat": outputFormat,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/pages/{pageIdOrName}/export"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_page_content_export_status(
        self, docId, pageIdOrName, requestId
    ) -> dict[str, Any]:
        """
        Retrieves the export status of a specific page's content in a document by request ID.

        Args:
            docId: str. The unique identifier of the document.
            pageIdOrName: str. The ID or name of the page whose export status is being queried.
            requestId: str. The unique identifier for the export request.

        Returns:
            dict. A dictionary containing the status and details of the page content export request.

        Raises:
            ValueError: Raised if any of 'docId', 'pageIdOrName', or 'requestId' is None.
            requests.HTTPError: Raised if the HTTP request to fetch the export status fails with a non-success status code.

        Tags:
            get, status, export, page, document, ai, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if pageIdOrName is None:
            raise ValueError("Missing required parameter 'pageIdOrName'")
        if requestId is None:
            raise ValueError("Missing required parameter 'requestId'")
        url = f"{self.base_url}/docs/{docId}/pages/{pageIdOrName}/export/{requestId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tables(
        self, docId, limit=None, pageToken=None, sortBy=None, tableTypes=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of tables from a specified document with optional filtering, pagination, and sorting.

        Args:
            docId: str. The unique identifier of the document to retrieve tables from.
            limit: Optional[int]. The maximum number of tables to return.
            pageToken: Optional[str]. Token for fetching a specific results page.
            sortBy: Optional[str]. Field to sort tables by.
            tableTypes: Optional[str]. Comma-separated list of table types to filter results.

        Returns:
            dict[str, Any]: A dictionary containing the tables and related metadata retrieved from the document.

        Raises:
            ValueError: Raised if 'docId' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails.

        Tags:
            list, tables, document-management, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/tables"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("sortBy", sortBy),
                ("tableTypes", tableTypes),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_table(
        self, docId, tableIdOrName, useUpdatedTableLayouts=None
    ) -> dict[str, Any]:
        """
        Retrieve table details from a document by table ID or name.

        Args:
            docId: The unique identifier of the document containing the table.
            tableIdOrName: The unique ID or name of the table to retrieve.
            useUpdatedTableLayouts: Optional; whether to use updated table layout formatting. Defaults to None.

        Returns:
            A dictionary containing the JSON response with table details.

        Raises:
            ValueError: If 'docId' or 'tableIdOrName' is not provided.
            requests.HTTPError: If the HTTP request for the table details fails.

        Tags:
            get, table, ai, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}"
        query_params = {
            k: v
            for k, v in [("useUpdatedTableLayouts", useUpdatedTableLayouts)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_columns(
        self, docId, tableIdOrName, limit=None, pageToken=None, visibleOnly=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of columns for a specified table in a document, with optional filtering and pagination.

        Args:
            docId: str. The unique identifier of the document containing the table.
            tableIdOrName: str. The ID or name of the target table within the document.
            limit: Optional[int]. The maximum number of columns to return in the response.
            pageToken: Optional[str]. A token to retrieve the next page of results, for pagination.
            visibleOnly: Optional[bool]. If True, only returns columns that are currently visible.

        Returns:
            dict[str, Any]: A dictionary containing metadata and data about the columns in the specified table.

        Raises:
            ValueError: Raised if 'docId' or 'tableIdOrName' is not provided.
            requests.HTTPError: Raised if the HTTP request to retrieve columns fails with a non-success status code.

        Tags:
            list, columns, table, document, api, metadata, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/columns"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("visibleOnly", visibleOnly),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_rows(
        self,
        docId,
        tableIdOrName,
        query=None,
        sortBy=None,
        useColumnNames=None,
        valueFormat=None,
        visibleOnly=None,
        limit=None,
        pageToken=None,
        syncToken=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of rows from a specified table in a document, with optional filtering, sorting, and pagination.

        Args:
            docId: str. The unique identifier of the document containing the target table.
            tableIdOrName: str. The ID or name of the table from which to fetch rows.
            query: str or None. An optional query string to filter rows based on specific conditions.
            sortBy: str or None. Optional parameter to specify column(s) by which to sort the results.
            useColumnNames: bool or None. If True, uses column names in the returned data instead of IDs.
            valueFormat: str or None. Specifies how cell values should be formatted (e.g., display, raw).
            visibleOnly: bool or None. If True, returns only visible rows.
            limit: int or None. The maximum number of rows to return in the response.
            pageToken: str or None. A token indicating the page of results to retrieve for pagination.
            syncToken: str or None. A token to synchronize and fetch only new or changed rows since the last call.

        Returns:
            dict[str, Any]: A dictionary containing the list of rows, and possibly metadata such as pagination tokens.

        Raises:
            ValueError: Raised if 'docId' or 'tableIdOrName' is not provided.
            requests.HTTPError: Raised if the HTTP request to fetch rows fails with a response error status.

        Tags:
            list, rows, table, document, api-call, filtering, pagination, fetch, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows"
        query_params = {
            k: v
            for k, v in [
                ("query", query),
                ("sortBy", sortBy),
                ("useColumnNames", useColumnNames),
                ("valueFormat", valueFormat),
                ("visibleOnly", visibleOnly),
                ("limit", limit),
                ("pageToken", pageToken),
                ("syncToken", syncToken),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def upsert_rows(
        self, docId, tableIdOrName, rows, disableParsing=None, keyColumns=None
    ) -> dict[str, Any]:
        """
        Upserts (inserts or updates) multiple rows in a specified table within a document.

        Args:
            docId: str. The unique identifier of the document containing the target table.
            tableIdOrName: str. The identifier or name of the table where rows will be upserted.
            rows: list[dict]. A list of row data to insert or update in the table.
            disableParsing: Optional[bool]. If True, disables automatic parsing of cell values. Defaults to None.
            keyColumns: Optional[list[str]]. Columns used as keys to determine if a row should be inserted or updated. Defaults to None.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the result details of the upsert operation.

        Raises:
            ValueError: Raised if any of the required parameters 'docId', 'tableIdOrName', or 'rows' is None.
            requests.HTTPError: Raised if the API request fails with a non-success status code.

        Tags:
            upsert, rows, batch, table-management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        if rows is None:
            raise ValueError("Missing required parameter 'rows'")
        request_body = {
            "rows": rows,
            "keyColumns": keyColumns,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows"
        query_params = {
            k: v for k, v in [("disableParsing", disableParsing)] if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_rows(self, docId, tableIdOrName, rowIds) -> dict[str, Any]:
        """
        Deletes specified rows from a table within a given document.

        Args:
            docId: str. The unique identifier of the document containing the table.
            tableIdOrName: str. The unique identifier or name of the table from which rows will be deleted.
            rowIds: list. A list of string or integer row IDs specifying which rows to delete.

        Returns:
            dict. The JSON response from the API after the deletion operation.

        Raises:
            ValueError: Raised if 'docId', 'tableIdOrName', or 'rowIds' is None.
            requests.HTTPError: Raised if the HTTP response indicates an unsuccessful status.

        Tags:
            delete, rows, batch, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        if rowIds is None:
            raise ValueError("Missing required parameter 'rowIds'")
        request_body = {
            "rowIds": rowIds,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_row(
        self, docId, tableIdOrName, rowIdOrName, useColumnNames=None, valueFormat=None
    ) -> dict[str, Any]:
        """
        Retrieves a specific row from a table in a document using the provided identifiers.

        Args:
            docId: str. The unique identifier of the document containing the table.
            tableIdOrName: str. The unique ID or name of the table from which to retrieve the row.
            rowIdOrName: str. The unique ID or name of the row to retrieve.
            useColumnNames: Optional[bool]. If True, use column names instead of IDs in the response. Defaults to None.
            valueFormat: Optional[str]. Format in which to return cell values (e.g., 'formattedValue'). Defaults to None.

        Returns:
            dict[str, Any]: A dictionary representing the JSON response containing the requested row's data.

        Raises:
            ValueError: If any of 'docId', 'tableIdOrName', or 'rowIdOrName' is None.
            requests.HTTPError: If the HTTP request to retrieve the row fails or the server returns an error response.

        Tags:
            get, row, table, fetch, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        if rowIdOrName is None:
            raise ValueError("Missing required parameter 'rowIdOrName'")
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}"
        query_params = {
            k: v
            for k, v in [
                ("useColumnNames", useColumnNames),
                ("valueFormat", valueFormat),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_row(
        self, docId, tableIdOrName, rowIdOrName, row, disableParsing=None
    ) -> dict[str, Any]:
        """
        Updates an existing row in a specified table within a document by sending the updated row data to the API.

        Args:
            docId: The unique identifier of the document containing the target table (str).
            tableIdOrName: The unique identifier or name of the table containing the row to update (str).
            rowIdOrName: The unique identifier or name of the row to update within the table (str).
            row: A dictionary representing the new row data to be applied (dict).
            disableParsing: Optional flag to disable response parsing when set (Any, optional).

        Returns:
            A dictionary containing the JSON response from the API after the row update.

        Raises:
            ValueError: Raised if any required parameter ('docId', 'tableIdOrName', 'rowIdOrName', or 'row') is missing.

        Tags:
            update, row, api, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        if rowIdOrName is None:
            raise ValueError("Missing required parameter 'rowIdOrName'")
        if row is None:
            raise ValueError("Missing required parameter 'row'")
        request_body = {
            "row": row,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}"
        query_params = {
            k: v for k, v in [("disableParsing", disableParsing)] if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_row(self, docId, tableIdOrName, rowIdOrName) -> dict[str, Any]:
        """
        Deletes a specific row from a table in the given document.

        Args:
            docId: str. Unique identifier of the document containing the target table.
            tableIdOrName: str. Identifier or name of the table from which to delete the row.
            rowIdOrName: str. Identifier or name of the row to be deleted.

        Returns:
            dict[str, Any]: JSON response from the API after deleting the row.

        Raises:
            ValueError: Raised if any of 'docId', 'tableIdOrName', or 'rowIdOrName' is None.
            requests.HTTPError: Raised if the HTTP request to delete the row fails.

        Tags:
            delete, row-management, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        if rowIdOrName is None:
            raise ValueError("Missing required parameter 'rowIdOrName'")
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def push_button(
        self, docId, tableIdOrName, rowIdOrName, columnIdOrName
    ) -> dict[str, Any]:
        """
        Triggers a button action on a specified cell within a table row in a document and returns the result.

        Args:
            docId: str. The unique identifier of the document containing the table.
            tableIdOrName: str. The ID or name of the target table within the document.
            rowIdOrName: str. The ID or name of the specific row in the table.
            columnIdOrName: str. The ID or name of the column representing the button to be pressed.

        Returns:
            dict[str, Any]: The response from the API as a dictionary representing the result of the button action.

        Raises:
            ValueError: If any of the required parameters ('docId', 'tableIdOrName', 'rowIdOrName', 'columnIdOrName') are None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            trigger, button-action, table, api, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if tableIdOrName is None:
            raise ValueError("Missing required parameter 'tableIdOrName'")
        if rowIdOrName is None:
            raise ValueError("Missing required parameter 'rowIdOrName'")
        if columnIdOrName is None:
            raise ValueError("Missing required parameter 'columnIdOrName'")
        url = f"{self.base_url}/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}/buttons/{columnIdOrName}"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_formulas(
        self, docId, limit=None, pageToken=None, sortBy=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of formulas for a specified document, supporting pagination and sorting options.

        Args:
            docId: str. The unique identifier of the document whose formulas are to be listed. Required.
            limit: int, optional. Maximum number of formulas to return in the response.
            pageToken: str, optional. Token indicating the page of results to retrieve for pagination.
            sortBy: str, optional. Field by which to sort the formulas.

        Returns:
            dict[str, Any]: A dictionary containing the list of formulas and related pagination data from the API response.

        Raises:
            ValueError: If 'docId' is not provided.
            requests.HTTPError: If the API request fails due to an HTTP error.

        Tags:
            list, formulas, document-management, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/formulas"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken), ("sortBy", sortBy)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_formula(self, docId, formulaIdOrName) -> dict[str, Any]:
        """
        Retrieves details of a specific formula from a document by formula ID or name.

        Args:
            docId: The unique identifier of the document containing the formula.
            formulaIdOrName: The unique identifier or name of the formula to retrieve.

        Returns:
            A dictionary containing the formula details as returned by the API.

        Raises:
            ValueError: If either 'docId' or 'formulaIdOrName' is not provided.
            requests.HTTPError: If the HTTP request to fetch the formula fails.

        Tags:
            get, formula, ai, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if formulaIdOrName is None:
            raise ValueError("Missing required parameter 'formulaIdOrName'")
        url = f"{self.base_url}/docs/{docId}/formulas/{formulaIdOrName}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_controls(
        self, docId, limit=None, pageToken=None, sortBy=None
    ) -> dict[str, Any]:
        """
        Retrieves a paginated list of controls associated with a specific document.

        Args:
            docId: str. The unique identifier of the document whose controls are to be listed.
            limit: Optional[int]. Maximum number of controls to return. If None, the server default is used.
            pageToken: Optional[str]. Token indicating the page of results to retrieve, for pagination.
            sortBy: Optional[str]. Field by which to sort the results. If None, uses the server default sorting.

        Returns:
            dict[str, Any]: A dictionary containing the list of controls and associated metadata.

        Raises:
            ValueError: If 'docId' is not provided.
            requests.HTTPError: If the HTTP request fails with an error response from the server.

        Tags:
            list, controls, management, pagination, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/{docId}/controls"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken), ("sortBy", sortBy)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_control(self, docId, controlIdOrName) -> dict[str, Any]:
        """
        Retrieves details for a specific control in a document by its ID or name.

        Args:
            docId: The unique identifier of the document containing the control.
            controlIdOrName: The unique identifier or name of the control to retrieve.

        Returns:
            A dictionary containing the JSON representation of the control's details.

        Raises:
            ValueError: Raised if 'docId' or 'controlIdOrName' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the control fails.

        Tags:
            get, control, document, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if controlIdOrName is None:
            raise ValueError("Missing required parameter 'controlIdOrName'")
        url = f"{self.base_url}/docs/{docId}/controls/{controlIdOrName}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_custom_doc_domains(self, docId) -> dict[str, Any]:
        """
        Retrieve the list of custom domains associated with a specified document.

        Args:
            docId: The unique identifier of the document for which to list custom domains.

        Returns:
            A dictionary containing the custom domain information for the specified document.

        Raises:
            ValueError: If 'docId' is None.
            requests.HTTPError: If the HTTP request to retrieve domain information fails.

        Tags:
            list, domains, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/docs/${docId}/domains"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_custom_doc_domain(self, docId, customDocDomain) -> dict[str, Any]:
        """
        Adds a custom document domain to a specified document.

        Args:
            docId: The unique identifier of the document to which the custom domain will be added.
            customDocDomain: A dictionary containing the custom domain details to associate with the document.

        Returns:
            A dictionary representing the server's JSON response after adding the custom domain.

        Raises:
            ValueError: Raised if 'docId' or 'customDocDomain' is None.
            requests.HTTPError: Raised if the HTTP request to add the custom document domain fails.

        Tags:
            add, custom-domain, document-management, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if customDocDomain is None:
            raise ValueError("Missing required parameter 'customDocDomain'")
        request_body = {
            "customDocDomain": customDocDomain,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/docs/${docId}/domains"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_custom_doc_domain(self, docId, customDocDomain) -> dict[str, Any]:
        """
        Deletes a custom document domain for a specific document by sending a DELETE request to the API.

        Args:
            docId: str. The unique identifier of the document whose custom domain is to be deleted.
            customDocDomain: str. The name of the custom domain associated with the document to be removed.

        Returns:
            dict[str, Any]: The JSON response from the API after the custom domain is deleted.

        Raises:
            ValueError: Raised if 'docId' or 'customDocDomain' is None.
            requests.HTTPError: Raised if the API response status code indicates an error.

        Tags:
            delete, management, api, doc-domain, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if customDocDomain is None:
            raise ValueError("Missing required parameter 'customDocDomain'")
        url = f"{self.base_url}/docs/{docId}/domains/{customDocDomain}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_custom_doc_domain_provider(self, customDocDomain) -> dict[str, Any]:
        """
        Retrieves provider information for a specified custom document domain.

        Args:
            customDocDomain: The identifier of the custom document domain for which provider information is requested. Must not be None.

        Returns:
            A dictionary containing the provider details for the specified custom document domain.

        Raises:
            ValueError: Raised if 'customDocDomain' is None.
            requests.HTTPError: Raised if the HTTP request to fetch provider data fails with a non-success status code.

        Tags:
            get, domain, provider, ai, management, important
        """
        if customDocDomain is None:
            raise ValueError("Missing required parameter 'customDocDomain'")
        url = f"{self.base_url}/domains/provider/{customDocDomain}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def whoami(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves information about the current authenticated user from the API.

        Returns:
            dict[str, Any]: A dictionary containing details about the authenticated user as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the /whoami endpoint fails or returns an unsuccessful status code.

        Tags:
            whoami, user-info, fetch, api, important
        """
        url = f"{self.base_url}/whoami"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def resolve_browser_link(self, url, degradeGracefully=None) -> dict[str, Any]:
        """
        Resolves a browser link for the provided URL, optionally degrading gracefully, and returns the server's JSON response.

        Args:
            url: str. The target URL to be resolved. Must not be None.
            degradeGracefully: Optional[bool]. Whether to degrade gracefully on failure. If None, uses default behavior.

        Returns:
            dict[str, Any]: The JSON response from the server containing the resolved browser link information.

        Raises:
            ValueError: If the 'url' parameter is None.
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            resolve, browser-link, get, api, important
        """
        if url is None:
            raise ValueError("Missing required parameter 'url'")
        url = f"{self.base_url}/resolveBrowserLink"
        query_params = {
            k: v
            for k, v in [("url", url), ("degradeGracefully", degradeGracefully)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_mutation_status(self, requestId) -> dict[str, Any]:
        """
        Retrieves the mutation status for a given request ID.

        Args:
            requestId: str. The unique identifier of the mutation request for which to retrieve status.

        Returns:
            dict[str, Any]: The status information of the mutation request retrieved from the API.

        Raises:
            ValueError: Raised if requestId is None.
            requests.HTTPError: Raised if the HTTP request to the mutation status endpoint fails.

        Tags:
            get, status, mutation, api, important
        """
        if requestId is None:
            raise ValueError("Missing required parameter 'requestId'")
        url = f"{self.base_url}/mutationStatus/{requestId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def trigger_webhook_automation(
        self, docId, ruleId, request_body=None
    ) -> dict[str, Any]:
        """
        Triggers a webhook automation for the specified document and rule.

        Args:
            docId: str. The unique identifier of the document for which the webhook automation is to be triggered.
            ruleId: str. The unique identifier of the automation rule to trigger.
            request_body: Optional[dict]. The payload to be sent with the webhook automation request. Defaults to None.

        Returns:
            dict. The JSON response from the triggered webhook automation.

        Raises:
            ValueError: Raised if 'docId' or 'ruleId' is None.
            requests.exceptions.HTTPError: Raised if the HTTP request fails with a status error.

        Tags:
            trigger, webhook, automation, api, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        if ruleId is None:
            raise ValueError("Missing required parameter 'ruleId'")
        url = f"{self.base_url}/docs/{docId}/hooks/automation/{ruleId}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_page_analytics(
        self, docId, sinceDate=None, untilDate=None, pageToken=None, limit=None
    ) -> dict[str, Any]:
        """
        Retrieves analytics data for the pages of a specific document, supporting optional filtering and pagination.

        Args:
            docId: str. The unique identifier of the document for which to retrieve page analytics. Required.
            sinceDate: Optional[str]. ISO-8601 formatted date string to filter analytics from this date onward.
            untilDate: Optional[str]. ISO-8601 formatted date string to filter analytics up to this date.
            pageToken: Optional[str]. Token for pagination to retrieve the next set of results.
            limit: Optional[int]. Maximum number of analytics records to return.

        Returns:
            dict[str, Any]: A dictionary containing page analytics data for the specified document, possibly including pagination information.

        Raises:
            ValueError: If 'docId' is not provided.
            HTTPError: If the HTTP request for page analytics fails.

        Tags:
            list, analytics, pages, management, important
        """
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/analytics/docs/{docId}/pages"
        query_params = {
            k: v
            for k, v in [
                ("sinceDate", sinceDate),
                ("untilDate", untilDate),
                ("pageToken", pageToken),
                ("limit", limit),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_doc_analytics_summary(
        self, isPublished=None, sinceDate=None, untilDate=None, workspaceId=None
    ) -> dict[str, Any]:
        """
        Retrieves a summary of document analytics with optional filtering by publication status, date range, and workspace.

        Args:
            isPublished: Optional[bool]. If provided, filters results to include only published or unpublished documents.
            sinceDate: Optional[str]. ISO 8601 formatted date string representing the start of the summary period.
            untilDate: Optional[str]. ISO 8601 formatted date string representing the end of the summary period.
            workspaceId: Optional[str]. If provided, limits results to documents in the specified workspace.

        Returns:
            dict[str, Any]: A dictionary containing the analytics summary for documents matching the specified filters.

        Raises:
            requests.HTTPError: If the HTTP request fails or returns a non-success status code.

        Tags:
            list, analytics, summary, docs, api, important
        """
        url = f"{self.base_url}/analytics/docs/summary"
        query_params = {
            k: v
            for k, v in [
                ("isPublished", isPublished),
                ("sinceDate", sinceDate),
                ("untilDate", untilDate),
                ("workspaceId", workspaceId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_analytics(
        self,
        packIds=None,
        workspaceId=None,
        query=None,
        sinceDate=None,
        untilDate=None,
        scale=None,
        pageToken=None,
        orderBy=None,
        direction=None,
        isPublished=None,
        limit=None,
    ) -> dict[str, Any]:
        """
        Retrieves analytics data for specified content packs with optional filtering and pagination.

        Args:
            packIds: Optional[list[str]]. List of pack IDs to filter analytics data for specific packs.
            workspaceId: Optional[str]. Workspace identifier to filter analytics by workspace scope.
            query: Optional[str]. Search query to filter results by text matching.
            sinceDate: Optional[str]. Start date for filtering analytics data (inclusive, in ISO format).
            untilDate: Optional[str]. End date for filtering analytics data (inclusive, in ISO format).
            scale: Optional[str]. Aggregation scale (e.g., 'daily', 'monthly') for analytics data.
            pageToken: Optional[str]. Token to retrieve the next page of results for pagination.
            orderBy: Optional[str]. Field name to order the results by.
            direction: Optional[str]. Sorting direction, typically 'asc' or 'desc'.
            isPublished: Optional[bool]. Filter for published or unpublished packs.
            limit: Optional[int]. Maximum number of results to return per page.

        Returns:
            dict[str, Any]: A dictionary containing the analytics data for the requested packs, with metadata and results as provided by the API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the analytics API fails or returns a non-success status code.

        Tags:
            list, analytics, pack, filter, pagination, management, important
        """
        url = f"{self.base_url}/analytics/packs"
        query_params = {
            k: v
            for k, v in [
                ("packIds", packIds),
                ("workspaceId", workspaceId),
                ("query", query),
                ("sinceDate", sinceDate),
                ("untilDate", untilDate),
                ("scale", scale),
                ("pageToken", pageToken),
                ("orderBy", orderBy),
                ("direction", direction),
                ("isPublished", isPublished),
                ("limit", limit),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_analytics_summary(
        self,
        packIds=None,
        workspaceId=None,
        isPublished=None,
        sinceDate=None,
        untilDate=None,
    ) -> dict[str, Any]:
        """
        Retrieves a summary of analytics for one or more packs, optionally filtered by pack IDs, workspace, publication status, and date range.

        Args:
            packIds: Optional list of pack IDs to filter the analytics summary. If None, includes all packs.
            workspaceId: Optional ID of the workspace to filter results. If None, results are not limited by workspace.
            isPublished: Optional boolean to filter packs by publication status. If None, both published and unpublished packs are included.
            sinceDate: Optional ISO8601 string representing the start date for analytics data. If None, no lower date bound is applied.
            untilDate: Optional ISO8601 string representing the end date for analytics data. If None, no upper date bound is applied.

        Returns:
            dict: A dictionary containing the analytics summary for the specified packs and filters.

        Raises:
            requests.HTTPError: If the HTTP request to the analytics endpoint returns an unsuccessful status code.

        Tags:
            list, analytics, summary, pack, filter, important
        """
        url = f"{self.base_url}/analytics/packs/summary"
        query_params = {
            k: v
            for k, v in [
                ("packIds", packIds),
                ("workspaceId", workspaceId),
                ("isPublished", isPublished),
                ("sinceDate", sinceDate),
                ("untilDate", untilDate),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_formula_analytics(
        self,
        packId,
        packFormulaNames=None,
        packFormulaTypes=None,
        sinceDate=None,
        untilDate=None,
        scale=None,
        pageToken=None,
        orderBy=None,
        direction=None,
        limit=None,
    ) -> dict[str, Any]:
        """
        Retrieves analytics data for formulas within a specified pack, supporting various filtering and pagination options.

        Args:
            packId: str. The unique identifier of the pack whose formula analytics are to be listed. Required.
            packFormulaNames: Optional[list[str]]. Filter formulas by their names.
            packFormulaTypes: Optional[list[str]]. Filter formulas by their types.
            sinceDate: Optional[str]. Restrict analytics to those recorded on or after this date (ISO 8601 format).
            untilDate: Optional[str]. Restrict analytics to those recorded before this date (ISO 8601 format).
            scale: Optional[str]. Specify granularity of analytics (e.g., 'daily', 'monthly').
            pageToken: Optional[str]. Continuation token for paginated results.
            orderBy: Optional[str]. Field by which to order results.
            direction: Optional[str]. Sort direction for ordered results ('asc' or 'desc').
            limit: Optional[int]. Maximum number of results to return.

        Returns:
            dict[str, Any]: A dictionary containing the analytics data for the pack formulas, including pagination fields and the analytics records.

        Raises:
            ValueError: If 'packId' is not provided.
            requests.HTTPError: If the underlying HTTP request to the analytics endpoint fails.

        Tags:
            list, analytics, batch, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/analytics/packs/{packId}/formulas"
        query_params = {
            k: v
            for k, v in [
                ("packFormulaNames", packFormulaNames),
                ("packFormulaTypes", packFormulaTypes),
                ("sinceDate", sinceDate),
                ("untilDate", untilDate),
                ("scale", scale),
                ("pageToken", pageToken),
                ("orderBy", orderBy),
                ("direction", direction),
                ("limit", limit),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_analytics_last_updated(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the timestamp indicating when analytics data was last updated from the analytics API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing information about the last analytics update, as parsed from the server's JSON response.

        Raises:
            requests.HTTPError: If the HTTP request to the analytics endpoint fails or returns an error status code.

        Tags:
            get, analytics, status, management, http, important
        """
        url = f"{self.base_url}/analytics/updated"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_workspace_members(
        self, workspaceId, includedRoles=None, pageToken=None
    ) -> dict[str, Any]:
        """
        Lists members of the specified workspace, optionally filtered by roles and paginated.

        Args:
            workspaceId: The unique identifier of the workspace whose members are to be listed.
            includedRoles: Optional. A list or comma-separated string of roles to filter the listed members.
            pageToken: Optional. A token string for fetching the next page of results in paginated responses.

        Returns:
            A dictionary containing details of the workspace members, which may include user information and pagination data.

        Raises:
            ValueError: Raised if 'workspaceId' is None.
            requests.HTTPError: Raised if the HTTP request to fetch workspace members fails.

        Tags:
            list, workspace, members, management, api, important
        """
        if workspaceId is None:
            raise ValueError("Missing required parameter 'workspaceId'")
        url = f"{self.base_url}/workspaces/{workspaceId}/users"
        query_params = {
            k: v
            for k, v in [("includedRoles", includedRoles), ("pageToken", pageToken)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def change_user_role(self, workspaceId, email, newRole) -> dict[str, Any]:
        """
        Change the role of a user within a specific workspace.

        Args:
            workspaceId: The unique identifier of the workspace where the user's role will be changed.
            email: The email address of the user whose role is to be modified.
            newRole: The new role to assign to the user within the workspace.

        Returns:
            A dictionary containing the server's response with updated user information and role details.

        Raises:
            ValueError: Raised if 'workspaceId', 'email', or 'newRole' are missing or None.
            requests.HTTPError: Raised if the HTTP request to change the user's role fails with an error response from the server.

        Tags:
            change, user-management, role-assignment, api, important
        """
        if workspaceId is None:
            raise ValueError("Missing required parameter 'workspaceId'")
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        if newRole is None:
            raise ValueError("Missing required parameter 'newRole'")
        request_body = {
            "email": email,
            "newRole": newRole,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/workspaces/{workspaceId}/users/role"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_workspace_role_activity(self, workspaceId) -> dict[str, Any]:
        """
        Retrieves activity details and permissions for all roles within a specified workspace.

        Args:
            workspaceId: The unique identifier of the workspace for which to list role activity.

        Returns:
            A dictionary containing activity and permission information for each role in the workspace.

        Raises:
            ValueError: Raised if 'workspaceId' is None, indicating a required parameter is missing.
            requests.HTTPError: Raised if the HTTP request to the backend API fails or returns an error status.

        Tags:
            list, roles, permissions, workspace, management, important
        """
        if workspaceId is None:
            raise ValueError("Missing required parameter 'workspaceId'")
        url = f"{self.base_url}/workspaces/{workspaceId}/roles"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_packs(
        self,
        accessType=None,
        accessTypes=None,
        sortBy=None,
        limit=None,
        direction=None,
        pageToken=None,
        onlyWorkspaceId=None,
        parentWorkspaceIds=None,
        excludePublicPacks=None,
        excludeIndividualAcls=None,
        excludeWorkspaceAcls=None,
        includeBrainOnlyPacks=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of packs with optional filtering, sorting, and pagination parameters.

        Args:
            accessType: Optional[str]. Specifies a single access type to filter packs.
            accessTypes: Optional[list[str]]. List of access types to filter packs.
            sortBy: Optional[str]. Field by which to sort the results.
            limit: Optional[int]. Maximum number of packs to return.
            direction: Optional[str]. Direction to sort the results (e.g., 'asc' or 'desc').
            pageToken: Optional[str]. Token to retrieve a specific page of results.
            onlyWorkspaceId: Optional[str]. Restricts results to packs belonging only to the specified workspace.
            parentWorkspaceIds: Optional[list[str]]. Filters packs by parent workspace IDs.
            excludePublicPacks: Optional[bool]. If True, excludes public packs from the results.
            excludeIndividualAcls: Optional[bool]. If True, excludes packs with individual ACLs.
            excludeWorkspaceAcls: Optional[bool]. If True, excludes packs with workspace-level ACLs.
            includeBrainOnlyPacks: Optional[bool]. If True, includes only 'brain-only' packs in the result.

        Returns:
            dict[str, Any]: A dictionary containing the list of packs and associated metadata.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request fails or the server responds with an error status code.

        Tags:
            list, packs, filter, sort, pagination, management, important
        """
        url = f"{self.base_url}/packs"
        query_params = {
            k: v
            for k, v in [
                ("accessType", accessType),
                ("accessTypes", accessTypes),
                ("sortBy", sortBy),
                ("limit", limit),
                ("direction", direction),
                ("pageToken", pageToken),
                ("onlyWorkspaceId", onlyWorkspaceId),
                ("parentWorkspaceIds", parentWorkspaceIds),
                ("excludePublicPacks", excludePublicPacks),
                ("excludeIndividualAcls", excludeIndividualAcls),
                ("excludeWorkspaceAcls", excludeWorkspaceAcls),
                ("includeBrainOnlyPacks", includeBrainOnlyPacks),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_pack(
        self, workspaceId=None, name=None, description=None, sourcePackId=None
    ) -> dict[str, Any]:
        """
        Creates a new pack in the specified workspace, optionally cloning from an existing source pack.

        Args:
            workspaceId: Optional; The unique identifier for the workspace in which to create the pack.
            name: Optional; The name of the new pack.
            description: Optional; A description for the new pack.
            sourcePackId: Optional; The identifier of an existing pack to use as a source for cloning.

        Returns:
            A dictionary containing the details of the created pack as returned by the API.

        Raises:
            HTTPError: Raised if the API request fails with an HTTP error response.

        Tags:
            create, pack, management, api, important
        """
        request_body = {
            "workspaceId": workspaceId,
            "name": name,
            "description": description,
            "sourcePackId": sourcePackId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack(self, packId) -> dict[str, Any]:
        """
        Retrieves the details of a specific pack by its ID from the API.

        Args:
            packId: The unique identifier of the pack to retrieve. Must not be None.

        Returns:
            A dictionary containing the pack details returned by the API.

        Raises:
            ValueError: If 'packId' is None.
            HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            get, pack, api, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_pack(
        self,
        packId,
        overallRateLimit=None,
        perConnectionRateLimit=None,
        logoAssetId=None,
        coverAssetId=None,
        exampleImages=None,
        sourceCodeVisibility=None,
        name=None,
        description=None,
        shortDescription=None,
        supportEmail=None,
        termsOfServiceUrl=None,
        privacyPolicyUrl=None,
    ) -> dict[str, Any]:
        """
        Updates the properties of an existing pack using the specified parameters.

        Args:
            packId: str. The unique identifier of the pack to update. Required.
            overallRateLimit: Optional[int]. The maximum allowed requests per time period across all connections.
            perConnectionRateLimit: Optional[int]. The maximum allowed requests per time period per connection.
            logoAssetId: Optional[str]. The asset ID for the pack's logo image.
            coverAssetId: Optional[str]. The asset ID for the pack's cover image.
            exampleImages: Optional[list]. A list of example image asset IDs for the pack.
            sourceCodeVisibility: Optional[str]. The visibility setting for the pack's source code.
            name: Optional[str]. The display name of the pack.
            description: Optional[str]. The full description of the pack.
            shortDescription: Optional[str]. The short description of the pack.
            supportEmail: Optional[str]. A support email address for the pack.
            termsOfServiceUrl: Optional[str]. URL to the pack's terms of service.
            privacyPolicyUrl: Optional[str]. URL to the pack's privacy policy.

        Returns:
            dict. A dictionary containing the updated pack's data returned by the server.

        Raises:
            ValueError: If 'packId' is not provided.
            requests.HTTPError: If the HTTP request to update the pack fails.

        Tags:
            update, pack-management, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        request_body = {
            "overallRateLimit": overallRateLimit,
            "perConnectionRateLimit": perConnectionRateLimit,
            "logoAssetId": logoAssetId,
            "coverAssetId": coverAssetId,
            "exampleImages": exampleImages,
            "sourceCodeVisibility": sourceCodeVisibility,
            "name": name,
            "description": description,
            "shortDescription": shortDescription,
            "supportEmail": supportEmail,
            "termsOfServiceUrl": termsOfServiceUrl,
            "privacyPolicyUrl": privacyPolicyUrl,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_pack(self, packId) -> dict[str, Any]:
        """
        Deletes a pack by its unique identifier and returns the response from the server.

        Args:
            packId: str. The unique identifier of the pack to be deleted.

        Returns:
            dict[str, Any]: The server response parsed as a dictionary containing the result of the delete operation.

        Raises:
            ValueError: If 'packId' is None.
            HTTPError: If the HTTP request to delete the pack fails with an error status code.

        Tags:
            delete, pack-management, async-job, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_configuration_schema(self, packId) -> dict[str, Any]:
        """
        Retrieves the configuration schema for a given pack by its identifier.

        Args:
            packId: str. The unique identifier of the pack whose configuration schema is to be retrieved.

        Returns:
            dict[str, Any]: The configuration schema of the specified pack as a dictionary.

        Raises:
            ValueError: If 'packId' is None.
            requests.HTTPError: If the HTTP request to fetch the schema fails (e.g., network issues, non-2xx response).

        Tags:
            get, configuration, schema, pack, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/configurations/schema"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_versions(self, packId, limit=None, pageToken=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of versions for the specified pack.

        Args:
            packId: The unique identifier of the pack whose versions are to be listed.
            limit: Optional; maximum number of versions to return in the response.
            pageToken: Optional; token indicating the page of results to retrieve for pagination.

        Returns:
            A dictionary containing the list of pack versions and pagination metadata as returned by the API.

        Raises:
            ValueError: Raised if 'packId' is not provided.
            HTTPError: Raised if the HTTP request to the API fails.

        Tags:
            list, versions, api, management, paginated, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/versions"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_next_pack_version(
        self, packId, proposedMetadata, sdkVersion=None
    ) -> dict[str, Any]:
        """
        Determines the next available version for a given pack based on proposed metadata and optional SDK version.

        Args:
            packId: str. The unique identifier of the pack for which the next version is to be determined.
            proposedMetadata: dict. Metadata describing the proposed changes or updates for the pack.
            sdkVersion: str, optional. The SDK version to use when determining the next pack version. If not provided, defaults to None.

        Returns:
            dict. A dictionary containing information about the next available pack version, as returned by the server.

        Raises:
            ValueError: If 'packId' or 'proposedMetadata' is not provided.
            requests.HTTPError: If the HTTP request to the server fails or returns a non-success status.

        Tags:
            get, version, pack-management, important, ai
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if proposedMetadata is None:
            raise ValueError("Missing required parameter 'proposedMetadata'")
        request_body = {
            "proposedMetadata": proposedMetadata,
            "sdkVersion": sdkVersion,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/nextVersion"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_version_diffs(
        self, packId, basePackVersion, targetPackVersion
    ) -> dict[str, Any]:
        """
        Retrieves the differences between two specific versions of a given pack.

        Args:
            packId: The unique identifier of the pack to compare.
            basePackVersion: The base version of the pack to compare from.
            targetPackVersion: The target version of the pack to compare to.

        Returns:
            A dictionary containing the differences between the specified pack versions.

        Raises:
            ValueError: Raised if 'packId', 'basePackVersion', or 'targetPackVersion' is None.
            HTTPError: Raised if the HTTP request to retrieve the version differences fails.

        Tags:
            get, diff, pack-management, version-control, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if basePackVersion is None:
            raise ValueError("Missing required parameter 'basePackVersion'")
        if targetPackVersion is None:
            raise ValueError("Missing required parameter 'targetPackVersion'")
        url = f"{self.base_url}/packs/{packId}/versions/{basePackVersion}/diff/{targetPackVersion}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def register_pack_version(self, packId, packVersion, bundleHash) -> dict[str, Any]:
        """
        Registers a new version of a pack with the given identifiers and bundle hash.

        Args:
            packId: str. Unique identifier of the pack to register the version for.
            packVersion: str. Semantic version string of the pack to register.
            bundleHash: str. Hash representing the specific bundle/content for this version.

        Returns:
            dict. The server response as a dictionary containing registration details for the pack version.

        Raises:
            ValueError: If any of 'packId', 'packVersion', or 'bundleHash' is None.
            HTTPError: If the HTTP request to register the pack version fails (e.g., non-2xx response).

        Tags:
            register, pack-management, async-job, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packVersion is None:
            raise ValueError("Missing required parameter 'packVersion'")
        if bundleHash is None:
            raise ValueError("Missing required parameter 'bundleHash'")
        request_body = {
            "bundleHash": bundleHash,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/versions/{packVersion}/register"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def pack_version_upload_complete(
        self, packId, packVersion, notes=None, source=None, allowOlderSdkVersion=None
    ) -> dict[str, Any]:
        """
        Marks a pack version upload as complete and notifies the server with optional metadata.

        Args:
            packId: str. Unique identifier of the pack whose version upload is being completed. Required.
            packVersion: str. Version string of the pack being marked as uploaded. Required.
            notes: Optional[str]. Additional notes about the upload or the version. Defaults to None.
            source: Optional[str]. Source identifier or metadata for the upload. Defaults to None.
            allowOlderSdkVersion: Optional[bool]. Whether to allow this pack version to specify an older SDK version. Defaults to None.

        Returns:
            dict[str, Any]: JSON response from the server after upload completion notification.

        Raises:
            ValueError: If 'packId' or 'packVersion' is not provided.
            requests.HTTPError: If the HTTP request fails or an error response is returned by the server.

        Tags:
            upload-complete, pack-management, post, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packVersion is None:
            raise ValueError("Missing required parameter 'packVersion'")
        request_body = {
            "notes": notes,
            "source": source,
            "allowOlderSdkVersion": allowOlderSdkVersion,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/versions/{packVersion}/uploadComplete"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_pack_release(
        self, packId, packVersion, releaseNotes=None
    ) -> dict[str, Any]:
        """
        Creates a new release for the specified pack with the given version and optional release notes.

        Args:
            packId: str. Unique identifier of the pack for which the release is created.
            packVersion: str. Version number of the pack being released.
            releaseNotes: Optional[str]. Additional notes describing the release. Defaults to None.

        Returns:
            dict. The JSON response from the server containing details about the created pack release.

        Raises:
            ValueError: Raised if 'packId' or 'packVersion' is not provided.
            requests.HTTPError: Raised if the HTTP request to create the release fails.

        Tags:
            create, pack-release, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packVersion is None:
            raise ValueError("Missing required parameter 'packVersion'")
        request_body = {
            "packVersion": packVersion,
            "releaseNotes": releaseNotes,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/releases"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_releases(self, packId, limit=None, pageToken=None) -> dict[str, Any]:
        """
        Retrieves a list of releases for a specified pack, supporting pagination.

        Args:
            packId: str. Unique identifier of the pack whose releases are to be listed.
            limit: Optional[int]. Maximum number of releases to return per page. If not specified, the default backend limit is used.
            pageToken: Optional[str]. Token for pagination to retrieve the next page of results.

        Returns:
            dict[str, Any]: A dictionary containing release data and pagination metadata as returned by the backend API.

        Raises:
            ValueError: Raised if 'packId' is None.
            requests.HTTPError: Raised if the HTTP request to the backend API fails.

        Tags:
            list, pack-releases, api, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/releases"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_pack_release(
        self, packId, packReleaseId, releaseNotes=None
    ) -> dict[str, Any]:
        """
        Updates the release information for a specific pack, including optional release notes.

        Args:
            packId: str. Unique identifier for the pack whose release is being updated.
            packReleaseId: str. Unique identifier for the release within the specified pack.
            releaseNotes: Optional[str]. Additional notes or description for the release. Defaults to None.

        Returns:
            dict[str, Any]: Parsed JSON response from the server containing updated release details.

        Raises:
            ValueError: If 'packId' or 'packReleaseId' is not provided.
            HTTPError: If the HTTP request fails or returns a non-success status code.

        Tags:
            update, pack-management, release, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packReleaseId is None:
            raise ValueError("Missing required parameter 'packReleaseId'")
        request_body = {
            "releaseNotes": releaseNotes,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/releases/{packReleaseId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def set_pack_oauth_config(
        self, packId, clientId=None, clientSecret=None, redirectUri=None
    ) -> dict[str, Any]:
        """
        Configures or updates the OAuth settings for a specific pack by sending the provided client credentials and redirect URI to the server.

        Args:
            packId: str. The unique identifier of the pack whose OAuth configuration is to be set. Required.
            clientId: str, optional. The OAuth client ID to be associated with the pack.
            clientSecret: str, optional. The OAuth client secret to be associated with the pack.
            redirectUri: str, optional. The redirect URI to be used for OAuth callbacks.

        Returns:
            dict[str, Any]: The server's JSON response containing the updated OAuth configuration for the pack.

        Raises:
            ValueError: Raised if 'packId' is not provided or is None.
            requests.HTTPError: Raised if the HTTP request to update the OAuth configuration fails.

        Tags:
            set, oauth-config, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        request_body = {
            "clientId": clientId,
            "clientSecret": clientSecret,
            "redirectUri": redirectUri,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/oauthConfig"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_oauth_config(self, packId) -> dict[str, Any]:
        """
        Retrieves the OAuth configuration for a specific pack identified by packId.

        Args:
            packId: str. The unique identifier of the pack for which to fetch the OAuth configuration.

        Returns:
            dict[str, Any]: A dictionary containing the OAuth configuration data for the specified pack.

        Raises:
            ValueError: Raised when the 'packId' parameter is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the OAuth configuration fails (non-success status code).

        Tags:
            get, oauth-config, pack, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/oauthConfig"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def set_pack_system_connection(self, packId, credentials) -> dict[str, Any]:
        """
        Sets the system connection for a specified pack using provided credentials.

        Args:
            packId: str. Unique identifier of the pack for which the system connection is being set.
            credentials: Any. Credentials required to establish the system connection.

        Returns:
            dict. JSON response from the API after setting the system connection.

        Raises:
            ValueError: Raised if 'packId' or 'credentials' is None.
            requests.HTTPError: Raised if the HTTP request to set the system connection fails.

        Tags:
            set, system-connection, pack, management, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if credentials is None:
            raise ValueError("Missing required parameter 'credentials'")
        request_body = {
            "credentials": credentials,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/systemConnection"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_system_connection(self, packId) -> dict[str, Any]:
        """
        Retrieves the system connection information for a specified pack by its ID.

        Args:
            packId: str. The unique identifier of the pack whose system connection details are to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the system connection information for the specified pack.

        Raises:
            ValueError: Raised if 'packId' is None.
            requests.HTTPError: Raised if the HTTP request to the backend fails or returns an error status.

        Tags:
            get, system-connection, pack, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/systemConnection"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_permissions(self, packId) -> dict[str, Any]:
        """
        Retrieves the permissions associated with the specified pack.

        Args:
            packId: str. The unique identifier of the pack whose permissions are to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the permissions data for the specified pack.

        Raises:
            ValueError: If 'packId' is None.
            requests.HTTPError: If the HTTP request to retrieve permissions fails.

        Tags:
            get, permissions, pack, important, ai, management
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/permissions"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_pack_permission(self, packId, principal, access) -> dict[str, Any]:
        """
        Adds a permission for a specified principal to a pack.

        Args:
            packId: The unique identifier of the pack to which the permission will be added.
            principal: The user or group to whom the permission is being granted.
            access: The type of access being granted (e.g., 'read', 'write').

        Returns:
            A dictionary containing the API response data from adding the pack permission.

        Raises:
            ValueError: Raised if any of the parameters 'packId', 'principal', or 'access' is None.
            requests.HTTPError: Raised if the API request fails with an HTTP error status.

        Tags:
            add, permission, pack-management, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if principal is None:
            raise ValueError("Missing required parameter 'principal'")
        if access is None:
            raise ValueError("Missing required parameter 'access'")
        request_body = {
            "principal": principal,
            "access": access,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/permissions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_pack_permission(self, packId, permissionId) -> dict[str, Any]:
        """
        Deletes a specific permission from a pack using the provided pack and permission IDs.

        Args:
            packId: str. The unique identifier of the pack from which the permission will be deleted.
            permissionId: str. The unique identifier of the permission to be deleted.

        Returns:
            dict[str, Any]: The server response as a dictionary containing confirmation or details of the deleted permission.

        Raises:
            ValueError: Raised if either 'packId' or 'permissionId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the permission fails.

        Tags:
            delete, permission-management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if permissionId is None:
            raise ValueError("Missing required parameter 'permissionId'")
        url = f"{self.base_url}/packs/{packId}/permissions/{permissionId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_makers(self, packId) -> dict[str, Any]:
        """
        Retrieves a list of makers associated with the specified pack.

        Args:
            packId: The unique identifier of the pack whose makers are to be listed.

        Returns:
            A dictionary containing the makers for the specified pack as returned by the API.

        Raises:
            ValueError: If 'packId' is None.
            HTTPError: If the HTTP request to retrieve makers fails.

        Tags:
            list, pack, makers, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/makers"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_pack_maker(self, packId, loginId) -> dict[str, Any]:
        """
        Adds a maker to a specified pack using the provided login ID.

        Args:
            packId: The unique identifier of the pack to which the maker will be added.
            loginId: The login ID of the maker to be added to the pack.

        Returns:
            A dictionary containing the server's JSON response with details about the added maker.

        Raises:
            ValueError: Raised if 'packId' or 'loginId' is None.
            HTTPError: Raised if the POST request to the server returns an unsuccessful status code.

        Tags:
            add, maker, packs, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if loginId is None:
            raise ValueError("Missing required parameter 'loginId'")
        request_body = {
            "loginId": loginId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/maker"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_pack_maker(self, packId, loginId) -> dict[str, Any]:
        """
        Deletes a maker from a specified pack using the provided pack and login IDs.

        Args:
            packId: The unique identifier of the pack from which the maker will be deleted.
            loginId: The login identifier of the maker to be deleted from the pack.

        Returns:
            A dictionary containing the server's JSON response indicating the result of the delete operation.

        Raises:
            ValueError: Raised if 'packId' or 'loginId' is None.
            requests.HTTPError: Raised if the HTTP request fails or returns an unsuccessful status code.

        Tags:
            delete, pack-management, maker-management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if loginId is None:
            raise ValueError("Missing required parameter 'loginId'")
        url = f"{self.base_url}/packs/{packId}/maker/{loginId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_categories(self, packId) -> dict[str, Any]:
        """
        Retrieves the list of categories associated with a specific pack.

        Args:
            packId: The unique identifier of the pack for which categories are to be listed.

        Returns:
            A dictionary containing the categories data for the specified pack.

        Raises:
            ValueError: If 'packId' is None.
            requests.HTTPError: If the HTTP request to retrieve categories fails.

        Tags:
            list, categories, pack, api, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/categories"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_pack_category(self, packId, categoryName) -> dict[str, Any]:
        """
        Adds a new category to the specified pack by sending a POST request to the API.

        Args:
            packId: str. Unique identifier of the pack to which the category will be added.
            categoryName: str. Name of the new category to add to the pack.

        Returns:
            dict[str, Any]: The JSON response from the API containing details of the added category.

        Raises:
            ValueError: Raised if 'packId' or 'categoryName' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status.

        Tags:
            add, category, pack-management, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if categoryName is None:
            raise ValueError("Missing required parameter 'categoryName'")
        request_body = {
            "categoryName": categoryName,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/category"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_pack_category(self, packId, categoryName) -> dict[str, Any]:
        """
        Deletes a specific category from a pack by pack ID and category name.

        Args:
            packId: The unique identifier of the pack from which the category will be deleted. Must not be None.
            categoryName: The name of the category to delete from the specified pack. Must not be None.

        Returns:
            A dictionary containing the JSON response from the server after the category is deleted.

        Raises:
            ValueError: Raised if 'packId' or 'categoryName' is None.
            requests.HTTPError: Raised if the HTTP request to delete the category fails.

        Tags:
            delete, management, category, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if categoryName is None:
            raise ValueError("Missing required parameter 'categoryName'")
        url = f"{self.base_url}/packs/{packId}/category/{categoryName}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def upload_pack_asset(
        self, packId, packAssetType, imageHash, mimeType, filename
    ) -> dict[str, Any]:
        """
        Uploads an asset file to the specified pack and returns the server response.

        Args:
            packId: str. The unique identifier of the pack to which the asset is being uploaded.
            packAssetType: str. The type of asset (e.g., 'image', 'icon') being uploaded to the pack.
            imageHash: str. The unique hash value of the image asset for verification or deduplication.
            mimeType: str. The MIME type of the file being uploaded (e.g., 'image/png').
            filename: str. The name of the file to be uploaded.

        Returns:
            dict[str, Any]: Parsed JSON response containing details about the uploaded asset or server-side status.

        Raises:
            ValueError: Raised if any required parameter ('packId', 'packAssetType', 'imageHash', 'mimeType', 'filename') is missing or None.
            HTTPError: Raised if the server returns a non-successful status code in response to the upload request.

        Tags:
            upload, asset-management, pack, async-job, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packAssetType is None:
            raise ValueError("Missing required parameter 'packAssetType'")
        if imageHash is None:
            raise ValueError("Missing required parameter 'imageHash'")
        if mimeType is None:
            raise ValueError("Missing required parameter 'mimeType'")
        if filename is None:
            raise ValueError("Missing required parameter 'filename'")
        request_body = {
            "packAssetType": packAssetType,
            "imageHash": imageHash,
            "mimeType": mimeType,
            "filename": filename,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/uploadAsset"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def upload_pack_source_code(
        self, packId, payloadHash, filename, packVersion=None
    ) -> dict[str, Any]:
        """
        Uploads the source code for a specified pack by sending the provided file information and payload hash to the server.

        Args:
            packId: str. The unique identifier of the pack to which the source code should be uploaded.
            payloadHash: str. The hash of the source code payload to ensure data integrity.
            filename: str. The name of the file being uploaded as source code.
            packVersion: str, optional. The version of the pack associated with the source code upload. Defaults to None.

        Returns:
            dict[str, Any]: The server response as a dictionary, typically containing upload status and metadata.

        Raises:
            ValueError: If any of 'packId', 'payloadHash', or 'filename' are None.
            requests.HTTPError: If the HTTP request to upload source code fails (e.g., network issues or server errors).

        Tags:
            upload, pack-management, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if payloadHash is None:
            raise ValueError("Missing required parameter 'payloadHash'")
        if filename is None:
            raise ValueError("Missing required parameter 'filename'")
        request_body = {
            "payloadHash": payloadHash,
            "filename": filename,
            "packVersion": packVersion,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/uploadSourceCode"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def pack_asset_upload_complete(
        self, packId, packAssetId, packAssetType
    ) -> dict[str, Any]:
        """
        Marks an asset upload as complete for a given pack and asset type by sending a POST request to the server.

        Args:
            packId: The unique identifier of the pack containing the asset.
            packAssetId: The unique identifier of the asset within the pack.
            packAssetType: The type of the asset being uploaded (e.g., image, audio, etc.).

        Returns:
            A dictionary containing the server's JSON response indicating the result of the upload completion process.

        Raises:
            ValueError: Raised if any of 'packId', 'packAssetId', or 'packAssetType' is None.
            requests.HTTPError: Raised if the HTTP request to mark the upload complete fails.

        Tags:
            mark-complete, upload, asset-management, post-request, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packAssetId is None:
            raise ValueError("Missing required parameter 'packAssetId'")
        if packAssetType is None:
            raise ValueError("Missing required parameter 'packAssetType'")
        url = f"{self.base_url}/packs/{packId}/assets/{packAssetId}/assetType/{packAssetType}/uploadComplete"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def pack_source_code_upload_complete(
        self, packId, packVersion, filename, codeHash
    ) -> dict[str, Any]:
        """
        Marks the completion of a source code upload for a pack version by notifying the backend service.

        Args:
            packId: The unique identifier of the pack.
            packVersion: The version string of the pack.
            filename: The name of the source code file that was uploaded.
            codeHash: The hash of the uploaded source code for verification.

        Returns:
            A dictionary containing the response data from the backend after successfully marking the upload as complete.

        Raises:
            ValueError: If any of the required parameters ('packId', 'packVersion', 'filename', 'codeHash') are None.
            requests.HTTPError: If the HTTP request to the backend fails or returns an error status code.

        Tags:
            upload-complete, pack-management, ai, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packVersion is None:
            raise ValueError("Missing required parameter 'packVersion'")
        if filename is None:
            raise ValueError("Missing required parameter 'filename'")
        if codeHash is None:
            raise ValueError("Missing required parameter 'codeHash'")
        request_body = {
            "filename": filename,
            "codeHash": codeHash,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/versions/{packVersion}/sourceCode/uploadComplete"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_source_code(self, packId, packVersion) -> dict[str, Any]:
        """
        Retrieves the source code for a specified pack version from the server.

        Args:
            packId: str. The unique identifier of the pack whose source code is to be retrieved.
            packVersion: str. The specific version of the pack for which the source code is requested.

        Returns:
            dict. A dictionary containing the source code and related metadata for the specified pack version.

        Raises:
            ValueError: Raised if 'packId' or 'packVersion' is None.
            requests.HTTPError: Raised if the HTTP request to the server fails.

        Tags:
            get, source-code, packs, version-management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if packVersion is None:
            raise ValueError("Missing required parameter 'packVersion'")
        url = f"{self.base_url}/packs/{packId}/versions/{packVersion}/sourceCode"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_listings(
        self,
        packAccessTypes=None,
        packIds=None,
        onlyWorkspaceId=None,
        parentWorkspaceIds=None,
        excludePublicPacks=None,
        excludeWorkspaceAcls=None,
        excludeIndividualAcls=None,
        includeBrainOnlyPacks=None,
        sortBy=None,
        orderBy=None,
        direction=None,
        limit=None,
        pageToken=None,
        installContext=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of available pack listings based on specified filtering, sorting, and access control criteria.

        Args:
            packAccessTypes: Optional; list of access type strings to filter packs by user permissions.
            packIds: Optional; list of pack IDs to retrieve specific packs.
            onlyWorkspaceId: Optional; string indicating a specific workspace to restrict results to.
            parentWorkspaceIds: Optional; list of parent workspace IDs to include packs from these workspaces.
            excludePublicPacks: Optional; boolean to exclude public packs from the results.
            excludeWorkspaceAcls: Optional; boolean to exclude packs with workspace-level ACLs.
            excludeIndividualAcls: Optional; boolean to exclude packs with individual-level ACLs.
            includeBrainOnlyPacks: Optional; boolean to include packs designated as 'brain-only'.
            sortBy: Optional; string specifying the field to sort results by.
            orderBy: Optional; string specifying the order of sorting (e.g., 'asc', 'desc').
            direction: Optional; string specifying sorting direction, typically 'asc' or 'desc'.
            limit: Optional; integer to limit the number of results returned.
            pageToken: Optional; string token for paginated results to fetch subsequent pages.
            installContext: Optional; string specifying the context for installation filtering.

        Returns:
            dict[str, Any]: A dictionary containing the filtered list of pack listings and associated metadata, as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the packs listing endpoint returns an unsuccessful status code.

        Tags:
            list, packs, filter, search, api, management, important
        """
        url = f"{self.base_url}/packs/listings"
        query_params = {
            k: v
            for k, v in [
                ("packAccessTypes", packAccessTypes),
                ("packIds", packIds),
                ("onlyWorkspaceId", onlyWorkspaceId),
                ("parentWorkspaceIds", parentWorkspaceIds),
                ("excludePublicPacks", excludePublicPacks),
                ("excludeWorkspaceAcls", excludeWorkspaceAcls),
                ("excludeIndividualAcls", excludeIndividualAcls),
                ("includeBrainOnlyPacks", includeBrainOnlyPacks),
                ("sortBy", sortBy),
                ("orderBy", orderBy),
                ("direction", direction),
                ("limit", limit),
                ("pageToken", pageToken),
                ("installContext", installContext),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_listing(
        self,
        packId,
        workspaceId=None,
        docId=None,
        installContext=None,
        releaseChannel=None,
    ) -> dict[str, Any]:
        """
        Retrieves the listing details for a specified pack, optionally filtered by workspace, document, install context, or release channel.

        Args:
            packId: str. The unique identifier of the pack to retrieve the listing for. Required.
            workspaceId: str or None. Optional workspace identifier to scope the pack listing.
            docId: str or None. Optional document identifier to further filter the pack listing.
            installContext: str or None. Optional installation context to refine the results.
            releaseChannel: str or None. Optional release channel (e.g., 'beta', 'stable') to select the listing version.

        Returns:
            dict[str, Any]: A dictionary containing the pack listing details as returned by the API.

        Raises:
            ValueError: If 'packId' is not provided.
            HTTPError: If the HTTP request to retrieve the pack listing fails.

        Tags:
            get, listing, packs, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/listing"
        query_params = {
            k: v
            for k, v in [
                ("workspaceId", workspaceId),
                ("docId", docId),
                ("installContext", installContext),
                ("releaseChannel", releaseChannel),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_logs(
        self,
        packId,
        docId,
        limit=None,
        pageToken=None,
        logTypes=None,
        beforeTimestamp=None,
        afterTimestamp=None,
        order=None,
        q=None,
        requestIds=None,
    ) -> dict[str, Any]:
        """
        Retrieves a paginated list of logs for a specified document in a pack, with advanced filtering and sorting options.

        Args:
            packId: str. Unique identifier of the pack containing the document. Required.
            docId: str. Unique identifier of the document whose logs are to be retrieved. Required.
            limit: int, optional. Maximum number of log entries to return per page.
            pageToken: str, optional. Token for fetching a specific results page in paginated responses.
            logTypes: list or str, optional. Filter logs by type(s) (e.g., 'error', 'info').
            beforeTimestamp: str or int, optional. Retrieve logs generated before this timestamp.
            afterTimestamp: str or int, optional. Retrieve logs generated after this timestamp.
            order: str, optional. Sort order for the logs (e.g., 'asc', 'desc').
            q: str, optional. Search query to filter log entries.
            requestIds: list or str, optional. Filter logs by one or more request IDs.

        Returns:
            dict[str, Any]: A dictionary containing the paginated list of logs and associated response metadata.

        Raises:
            ValueError: If either 'packId' or 'docId' is not provided.
            requests.HTTPError: If the HTTP request to retrieve logs fails (e.g., due to network error or server rejection).

        Tags:
            list, logs, pack-management, filter, pagination, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/packs/{packId}/docs/{docId}/logs"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("logTypes", logTypes),
                ("beforeTimestamp", beforeTimestamp),
                ("afterTimestamp", afterTimestamp),
                ("order", order),
                ("q", q),
                ("requestIds", requestIds),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_ingestion_logs(
        self,
        packId,
        organizationId,
        rootIngestionId,
        limit=None,
        pageToken=None,
        logTypes=None,
        ingestionExecutionId=None,
        beforeTimestamp=None,
        afterTimestamp=None,
        order=None,
        q=None,
        requestIds=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of ingestion logs for a specified pack, organization, and root ingestion, with support for filtering and pagination.

        Args:
            packId: The unique identifier of the pack for which to retrieve logs.
            organizationId: The unique identifier of the organization associated with the logs.
            rootIngestionId: The root ingestion ID to filter logs by.
            limit: Optional; maximum number of log entries to return.
            pageToken: Optional; token for retrieving the next page of results.
            logTypes: Optional; list or comma-separated string specifying log types to filter by.
            ingestionExecutionId: Optional; filter logs by a specific ingestion execution ID.
            beforeTimestamp: Optional; return logs created before this timestamp (ISO 8601 or epoch format).
            afterTimestamp: Optional; return logs created after this timestamp (ISO 8601 or epoch format).
            order: Optional; sorting order of the results ('asc' or 'desc').
            q: Optional; query string to filter logs by content.
            requestIds: Optional; list or comma-separated string of request IDs to filter logs by.

        Returns:
            A dictionary containing the retrieved ingestion logs and any associated metadata (such as pagination information).

        Raises:
            ValueError: Raised if any of the required parameters ('packId', 'organizationId', or 'rootIngestionId') are missing.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails with a non-success status code.

        Tags:
            list, logs, management, async-job, filter, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if organizationId is None:
            raise ValueError("Missing required parameter 'organizationId'")
        if rootIngestionId is None:
            raise ValueError("Missing required parameter 'rootIngestionId'")
        url = f"{self.base_url}/packs/{packId}/organizationId/{organizationId}/rootIngestionId/{rootIngestionId}/logs"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("logTypes", logTypes),
                ("ingestionExecutionId", ingestionExecutionId),
                ("beforeTimestamp", beforeTimestamp),
                ("afterTimestamp", afterTimestamp),
                ("order", order),
                ("q", q),
                ("requestIds", requestIds),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_grouped_pack_logs(
        self,
        packId,
        docId,
        limit=None,
        pageToken=None,
        beforeTimestamp=None,
        afterTimestamp=None,
        order=None,
        q=None,
    ) -> dict[str, Any]:
        """
        Retrieves a paginated and filtered list of grouped logs for a specific pack and document.

        Args:
            packId: str. The unique identifier of the pack. Required.
            docId: str. The unique identifier of the document within the pack. Required.
            limit: Optional[int]. The maximum number of log groups to return per page.
            pageToken: Optional[str]. A token indicating the page of results to retrieve.
            beforeTimestamp: Optional[str|int]. Only logs before this timestamp are returned.
            afterTimestamp: Optional[str|int]. Only logs after this timestamp are returned.
            order: Optional[str]. The sort order of logs (e.g., 'asc', 'desc').
            q: Optional[str]. Query string to filter logs.

        Returns:
            dict[str, Any]: A JSON-compatible dictionary containing the grouped log data and pagination information.

        Raises:
            ValueError: If 'packId' or 'docId' is not provided.
            requests.HTTPError: If the underlying HTTP request fails or returns an unsuccessful status code.

        Tags:
            list, logs, grouped, filter, pagination, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if docId is None:
            raise ValueError("Missing required parameter 'docId'")
        url = f"{self.base_url}/packs/{packId}/docs/{docId}/groupedLogs"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("beforeTimestamp", beforeTimestamp),
                ("afterTimestamp", afterTimestamp),
                ("order", order),
                ("q", q),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_grouped_ingestion_logs(
        self,
        packId,
        organizationId,
        rootIngestionId,
        limit=None,
        pageToken=None,
        ingestionExecutionId=None,
        beforeTimestamp=None,
        afterTimestamp=None,
        order=None,
        q=None,
    ) -> dict[str, Any]:
        """
        Retrieves grouped ingestion log entries for a specified pack, organization, and root ingestion, supporting filtering and pagination options.

        Args:
            packId: str. Unique identifier of the pack whose logs are to be retrieved.
            organizationId: str. Unique identifier of the organization associated with the pack.
            rootIngestionId: str. Unique identifier for the root ingestion of interest.
            limit: Optional[int]. Maximum number of log entries to return per page.
            pageToken: Optional[str]. Token to retrieve the next page of results in a paginated response.
            ingestionExecutionId: Optional[str]. Identifier to filter logs by a specific ingestion execution.
            beforeTimestamp: Optional[str]. Only return logs created before this timestamp (ISO 8601 format).
            afterTimestamp: Optional[str]. Only return logs created after this timestamp (ISO 8601 format).
            order: Optional[str]. Sort order of the logs, such as 'asc' or 'desc'.
            q: Optional[str]. Query string to filter logs by custom criteria.

        Returns:
            dict[str, Any]: A dictionary containing grouped ingestion log entries and associated metadata.

        Raises:
            ValueError: If any of the required parameters 'packId', 'organizationId', or 'rootIngestionId' is None.
            requests.HTTPError: If the HTTP request to the server fails or returns an unsuccessful status code.

        Tags:
            list, ingestion-logs, filter, pagination, ai, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if organizationId is None:
            raise ValueError("Missing required parameter 'organizationId'")
        if rootIngestionId is None:
            raise ValueError("Missing required parameter 'rootIngestionId'")
        url = f"{self.base_url}/packs/{packId}/organizationId/{organizationId}/rootIngestionId/{rootIngestionId}/groupedLogs"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("ingestionExecutionId", ingestionExecutionId),
                ("beforeTimestamp", beforeTimestamp),
                ("afterTimestamp", afterTimestamp),
                ("order", order),
                ("q", q),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_ingestion_executions(
        self,
        packId,
        organizationId,
        rootIngestionId,
        limit=None,
        pageToken=None,
        beforeTimestamp=None,
        afterTimestamp=None,
        order=None,
        ingestionStatus=None,
        datasource=None,
        executionType=None,
        includeDeletedIngestions=None,
        csbIngestionId=None,
        csbIngestionExecutionId=None,
    ) -> dict[str, Any]:
        """
        Retrieves a paginated list of ingestion execution records for a specified pack, organization, and root ingestion, with optional filtering and sorting parameters.

        Args:
            packId: str. Unique identifier of the ingestion pack.
            organizationId: str. Identifier for the organization owning the ingestion.
            rootIngestionId: str. Root identifier for the ingestion batch or group.
            limit: Optional[int]. Maximum number of records to return per page.
            pageToken: Optional[str]. Token to fetch a specific page of results.
            beforeTimestamp: Optional[str]. Return executions created before this timestamp (ISO 8601 format).
            afterTimestamp: Optional[str]. Return executions created after this timestamp (ISO 8601 format).
            order: Optional[str]. Sort order for the results (e.g., 'asc' or 'desc').
            ingestionStatus: Optional[str]. Filter results by ingestion execution status.
            datasource: Optional[str]. Filter by the data source of the ingestion.
            executionType: Optional[str]. Filter by the type of ingestion execution.
            includeDeletedIngestions: Optional[bool]. Whether to include deleted ingestions in the results.
            csbIngestionId: Optional[str]. Filter by Cloud Service Broker ingestion ID.
            csbIngestionExecutionId: Optional[str]. Filter by Cloud Service Broker ingestion execution ID.

        Returns:
            dict[str, Any]: A dictionary containing the paginated list of ingestion executions and associated metadata.

        Raises:
            ValueError: If any of the required parameters 'packId', 'organizationId', or 'rootIngestionId' are missing.
            requests.HTTPError: If the HTTP request to the backend service fails or returns a non-2xx status code.

        Tags:
            list, ingestion, executions, batch, search, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if organizationId is None:
            raise ValueError("Missing required parameter 'organizationId'")
        if rootIngestionId is None:
            raise ValueError("Missing required parameter 'rootIngestionId'")
        url = f"{self.base_url}/packs/{packId}/organizationId/{organizationId}/rootIngestionId/{rootIngestionId}/ingestionExecutions"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("pageToken", pageToken),
                ("beforeTimestamp", beforeTimestamp),
                ("afterTimestamp", afterTimestamp),
                ("order", order),
                ("ingestionStatus", ingestionStatus),
                ("datasource", datasource),
                ("executionType", executionType),
                ("includeDeletedIngestions", includeDeletedIngestions),
                ("csbIngestionId", csbIngestionId),
                ("csbIngestionExecutionId", csbIngestionExecutionId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_ingestion_execution_attempts(
        self,
        packId,
        organizationId,
        rootIngestionId,
        ingestionExecutionId,
        limit=None,
        pageToken=None,
        order=None,
    ) -> dict[str, Any]:
        """
        Lists execution attempts for a specific ingestion execution within a pack and organization.

        Args:
            packId: str. Identifier for the pack associated with the ingestion execution.
            organizationId: str. Identifier for the organization within which the pack operates.
            rootIngestionId: str. Identifier for the root ingestion job.
            ingestionExecutionId: str. Identifier for the specific ingestion execution whose attempts are being listed.
            limit: Optional[int]. Maximum number of attempt records to return in the response.
            pageToken: Optional[str]. Token for pagination to retrieve the next set of results.
            order: Optional[str]. Sort order of the listed attempts.

        Returns:
            dict. JSON response containing attempt records and relevant metadata for the specified ingestion execution.

        Raises:
            ValueError: Raised if any of the required parameters ('packId', 'organizationId', 'rootIngestionId', 'ingestionExecutionId') is None.
            HTTPError: Raised if the HTTP request for the execution attempts fails.

        Tags:
            list, ingestion, execution-attempts, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if organizationId is None:
            raise ValueError("Missing required parameter 'organizationId'")
        if rootIngestionId is None:
            raise ValueError("Missing required parameter 'rootIngestionId'")
        if ingestionExecutionId is None:
            raise ValueError("Missing required parameter 'ingestionExecutionId'")
        url = f"{self.base_url}/packs/{packId}/organizationId/{organizationId}/rootIngestionId/{rootIngestionId}/ingestionExecutionId/{ingestionExecutionId}/attempts"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("pageToken", pageToken), ("order", order)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pack_log_details(
        self, packId, organizationId, rootIngestionId, logId, detailsKey
    ) -> dict[str, Any]:
        """
        Retrieves detailed log information for a specific pack ingestion process by querying the remote service.

        Args:
            packId: str. Unique identifier of the pack whose log details are to be fetched.
            organizationId: str. Identifier for the organization associated with the pack.
            rootIngestionId: str. Root identifier for the ingestion process.
            logId: str. Unique identifier for the specific log entry.
            detailsKey: str. Key specifying the set of details to retrieve from the log.

        Returns:
            dict. JSON object containing the requested log details from the remote service.

        Raises:
            ValueError: Raised if any of the required parameters (packId, organizationId, rootIngestionId, logId, detailsKey) is None.
            requests.HTTPError: Raised if the HTTP request to fetch log details fails or returns a non-2xx response.

        Tags:
            get, log, details, fetch, ai, management, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if organizationId is None:
            raise ValueError("Missing required parameter 'organizationId'")
        if rootIngestionId is None:
            raise ValueError("Missing required parameter 'rootIngestionId'")
        if logId is None:
            raise ValueError("Missing required parameter 'logId'")
        if detailsKey is None:
            raise ValueError("Missing required parameter 'detailsKey'")
        url = f"{self.base_url}/packs/{packId}/organizationId/{organizationId}/rootIngestionId/{rootIngestionId}/logs/{logId}"
        query_params = {k: v for k, v in [("detailsKey", detailsKey)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_pack_featured_docs(self, packId) -> dict[str, Any]:
        """
        Fetches the featured documents for a specified pack by its ID.

        Args:
            packId: str. The unique identifier of the pack whose featured documents are to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the featured documents associated with the specified pack.

        Raises:
            ValueError: If 'packId' is None.

        Tags:
            list, featured-docs, packs, api-call, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        url = f"{self.base_url}/packs/{packId}/featuredDocs"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_pack_featured_docs(self, packId, items) -> dict[str, Any]:
        """
        Updates the featured documents for a specific pack by sending the provided items to the server.

        Args:
            packId: str. The unique identifier of the pack whose featured documents are to be updated.
            items: Any. A collection of items representing the featured documents to set for the pack.

        Returns:
            dict[str, Any]: The server's JSON response confirming the update of featured documents.

        Raises:
            ValueError: Raised if either 'packId' or 'items' is None.
            requests.HTTPError: Raised if the HTTP request to update the featured documents fails.

        Tags:
            update, featured-docs, pack-management, api, important
        """
        if packId is None:
            raise ValueError("Missing required parameter 'packId'")
        if items is None:
            raise ValueError("Missing required parameter 'items'")
        request_body = {
            "items": items,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/packs/{packId}/featuredDocs"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_go_link(
        self,
        organizationId,
        name,
        destinationUrl,
        description=None,
        urlPattern=None,
        creatorEmail=None,
    ) -> dict[str, Any]:
        """
        Creates a new Go Link resource for the specified organization.

        Args:
            organizationId: str. Unique identifier of the organization where the Go Link will be added.
            name: str. The name to assign to the Go Link resource.
            destinationUrl: str. The URL that the Go Link should redirect to.
            description: Optional[str]. A text description of the Go Link (default: None).
            urlPattern: Optional[str]. An explicit URL pattern for the Go Link, if applicable (default: None).
            creatorEmail: Optional[str]. The email address of the Go Link's creator (default: None).

        Returns:
            dict[str, Any]: A dictionary containing the details of the created Go Link resource as returned by the API.

        Raises:
            ValueError: Raised if organizationId, name, or destinationUrl are not provided.
            requests.HTTPError: Raised if the HTTP request to create the Go Link fails (e.g., due to network errors or API validation errors).

        Tags:
            add, go-link, management, api, important
        """
        if organizationId is None:
            raise ValueError("Missing required parameter 'organizationId'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if destinationUrl is None:
            raise ValueError("Missing required parameter 'destinationUrl'")
        request_body = {
            "name": name,
            "destinationUrl": destinationUrl,
            "description": description,
            "urlPattern": urlPattern,
            "creatorEmail": creatorEmail,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/organizations/{organizationId}/goLinks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.list_categories,
            self.list_docs,
            self.create_doc,
            self.get_doc,
            self.delete_doc,
            self.update_doc,
            self.get_sharing_metadata,
            self.get_permissions,
            self.add_permission,
            self.delete_permission,
            self.search_principals,
            self.get_acl_settings,
            self.update_acl_settings,
            self.publish_doc,
            self.unpublish_doc,
            self.list_pages,
            self.create_page,
            self.get_page,
            self.update_page,
            self.delete_page,
            self.begin_page_content_export,
            self.get_page_content_export_status,
            self.list_tables,
            self.get_table,
            self.list_columns,
            self.list_rows,
            self.upsert_rows,
            self.delete_rows,
            self.get_row,
            self.update_row,
            self.delete_row,
            self.push_button,
            self.list_formulas,
            self.get_formula,
            self.list_controls,
            self.get_control,
            self.list_custom_doc_domains,
            self.add_custom_doc_domain,
            self.delete_custom_doc_domain,
            self.get_custom_doc_domain_provider,
            self.whoami,
            self.resolve_browser_link,
            self.get_mutation_status,
            self.trigger_webhook_automation,
            self.list_page_analytics,
            self.list_doc_analytics_summary,
            self.list_pack_analytics,
            self.list_pack_analytics_summary,
            self.list_pack_formula_analytics,
            self.get_analytics_last_updated,
            self.list_workspace_members,
            self.change_user_role,
            self.list_workspace_role_activity,
            self.list_packs,
            self.create_pack,
            self.get_pack,
            self.update_pack,
            self.delete_pack,
            self.get_pack_configuration_schema,
            self.list_pack_versions,
            self.get_next_pack_version,
            self.get_pack_version_diffs,
            self.register_pack_version,
            self.pack_version_upload_complete,
            self.create_pack_release,
            self.list_pack_releases,
            self.update_pack_release,
            self.set_pack_oauth_config,
            self.get_pack_oauth_config,
            self.set_pack_system_connection,
            self.get_pack_system_connection,
            self.get_pack_permissions,
            self.add_pack_permission,
            self.delete_pack_permission,
            self.list_pack_makers,
            self.add_pack_maker,
            self.delete_pack_maker,
            self.list_pack_categories,
            self.add_pack_category,
            self.delete_pack_category,
            self.upload_pack_asset,
            self.upload_pack_source_code,
            self.pack_asset_upload_complete,
            self.pack_source_code_upload_complete,
            self.get_pack_source_code,
            self.list_pack_listings,
            self.get_pack_listing,
            self.list_pack_logs,
            self.list_ingestion_logs,
            self.list_grouped_pack_logs,
            self.list_grouped_ingestion_logs,
            self.list_ingestion_executions,
            self.list_ingestion_execution_attempts,
            self.get_pack_log_details,
            self.list_pack_featured_docs,
            self.update_pack_featured_docs,
            self.add_go_link,
        ]
