from typing import Any

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GoogleSheetApp(APIApplication):
    """
    Application for interacting with Google Sheets API.
    Provides tools to create and manage Google Spreadsheets.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="google-sheet", integration=integration)
        self.base_api_url = "https://sheets.googleapis.com/v4/spreadsheets"

    def create_spreadsheet(self, title: str) -> dict[str, Any]:
        """
        Creates a new blank Google Spreadsheet with the specified title and returns the API response.

        Args:
            title: String representing the desired title for the new spreadsheet

        Returns:
            Dictionary containing the full response from the Google Sheets API, including the spreadsheet's metadata and properties

        Raises:
            HTTPError: When the API request fails due to invalid authentication, network issues, or API limitations
            ValueError: When the title parameter is empty or contains invalid characters

        Tags:
            create, spreadsheet, google-sheets, api, important
        """
        url = self.base_api_url
        spreadsheet_data = {"properties": {"title": title}}
        response = self._post(url, data=spreadsheet_data)
        return response.json()

    def get_spreadsheet(self, spreadsheet_id: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific Google Spreadsheet using its ID.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to retrieve (found in the spreadsheet's URL)

        Returns:
            A dictionary containing the full spreadsheet metadata and contents, including properties, sheets, named ranges, and other spreadsheet-specific information from the Google Sheets API

        Raises:
            HTTPError: When the API request fails due to invalid spreadsheet_id or insufficient permissions
            ConnectionError: When there's a network connectivity issue
            ValueError: When the response cannot be parsed as JSON

        Tags:
            get, retrieve, spreadsheet, api, metadata, read, important
        """
        url = f"{self.base_api_url}/{spreadsheet_id}"
        response = self._get(url)
        return response.json()

    def batch_get_values(
        self, spreadsheet_id: str, ranges: list[str] = None
    ) -> dict[str, Any]:
        """
        Retrieves multiple ranges of values from a Google Spreadsheet in a single batch request.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to retrieve values from
            ranges: Optional list of A1 notation or R1C1 notation range strings (e.g., ['Sheet1!A1:B2', 'Sheet2!C3:D4']). If None, returns values from the entire spreadsheet

        Returns:
            A dictionary containing the API response with the requested spreadsheet values and metadata

        Raises:
            HTTPError: If the API request fails due to invalid spreadsheet_id, insufficient permissions, or invalid range format
            ValueError: If the spreadsheet_id is empty or invalid

        Tags:
            get, batch, read, spreadsheet, values, important
        """
        url = f"{self.base_api_url}/{spreadsheet_id}/values:batchGet"
        params = {}
        if ranges:
            params["ranges"] = ranges
        response = self._get(url, params=params)
        return response.json()

    def clear_values(self, spreadsheet_id: str, range: str) -> dict[str, Any]:
        """
        Clears all values from a specified range in a Google Spreadsheet while preserving cell formatting and other properties

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            range: The A1 or R1C1 notation range of cells to clear (e.g., 'Sheet1!A1:B2')

        Returns:
            A dictionary containing the Google Sheets API response

        Raises:
            HttpError: When the API request fails due to invalid spreadsheet_id, invalid range format, or insufficient permissions
            ValueError: When spreadsheet_id is empty or range is in invalid format

        Tags:
            clear, modify, spreadsheet, api, sheets, data-management, important
        """
        url = f"{self.base_api_url}/{spreadsheet_id}/values/{range}:clear"
        response = self._post(url, data={})
        return response.json()

    def update_values(
        self,
        spreadsheet_id: str,
        range: str,
        values: list[list[Any]],
        value_input_option: str = "RAW",
    ) -> dict[str, Any]:
        """
        Updates cell values in a specified range of a Google Spreadsheet using the Sheets API

        Args:
            spreadsheet_id: The unique identifier of the target Google Spreadsheet
            range: The A1 notation range where values will be updated (e.g., 'Sheet1!A1:B2')
            values: A list of lists containing the data to write, where each inner list represents a row of values
            value_input_option: Determines how input data should be interpreted: 'RAW' (as-is) or 'USER_ENTERED' (parsed as UI input). Defaults to 'RAW'

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            RequestError: When the API request fails due to invalid parameters or network issues
            AuthenticationError: When authentication with the Google Sheets API fails

        Tags:
            update, write, sheets, api, important, data-modification, google-sheets
        """
        url = f"{self.base_api_url}/{spreadsheet_id}/values/{range}"
        params = {"valueInputOption": value_input_option}
        data = {"range": range, "values": values}
        response = self._put(url, data=data, params=params)
        return response.json()

    def list_tools(self):
        """Returns a list of methods exposed as tools."""
        return [
            self.create_spreadsheet,
            self.get_spreadsheet,
            self.batch_get_values,
            self.clear_values,
            self.update_values,
        ]
