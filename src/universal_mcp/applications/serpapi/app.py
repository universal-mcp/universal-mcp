import httpx
from serpapi import SerpApiClient as SerpApiSearch

from universal_mcp.applications.application import APIApplication


class SerpapiApp(APIApplication):
    def __init__(self, **kwargs):
        super().__init__(name="serpapi", **kwargs)

    async def search(self, params: dict[str, any] = None) -> str:
        """
        Performs an asynchronous search using the SerpApi service and returns formatted search results.

        Args:
            params: Dictionary of engine-specific parameters (e.g., {'q': 'Coffee', 'engine': 'google_light', 'location': 'Austin, TX'}). Defaults to None.

        Returns:
            A formatted string containing search results with titles, links, and snippets, or an error message if the search fails.

        Raises:
            httpx.HTTPStatusError: Raised when the API request fails due to HTTP errors (401 for invalid API key, 429 for rate limiting)
            Exception: Raised for general errors such as network issues or invalid parameters

        Tags:
            search, async, web-scraping, api, serpapi, important
        """
        if params is None:
            params = {}
        api_key = self.integration.get_credentials().get("api_key")
        params = {
            "api_key": api_key,
            "engine": "google_light",  # Fastest engine by default
            **params,  # Include any additional parameters
        }
        try:
            search = SerpApiSearch(params)
            data = search.get_dict()

            # Process organic search results if available
            if "organic_results" in data:
                formatted_results = []
                for result in data.get("organic_results", []):
                    title = result.get("title", "No title")
                    link = result.get("link", "No link")
                    snippet = result.get("snippet", "No snippet")
                    formatted_results.append(
                        f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n"
                    )
                return (
                    "\n".join(formatted_results)
                    if formatted_results
                    else "No organic results found"
                )
            else:
                return "No organic results found"

        # Handle HTTP-specific errors
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return "Error: Rate limit exceeded. Please try again later."
            elif e.response.status_code == 401:
                return "Error: Invalid API key. Please check your SERPAPI_API_KEY."
            else:
                return f"Error: {e.response.status_code} - {e.response.text}"
        # Handle other exceptions (e.g., network issues)
        except Exception as e:
            return f"Error: {str(e)}"

    def list_tools(self):
        return [
            self.search,
        ]
