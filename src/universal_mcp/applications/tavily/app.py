from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class TavilyApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        name = "tavily"
        self.base_url = "https://api.tavily.com"
        super().__init__(name=name, integration=integration)

    def search(self, query: str) -> str:
        """
        Performs a web search using Tavily's search API and returns either a direct answer or a summary of top results.

        Args:
            query: The search query string to be processed by Tavily's search engine

        Returns:
            A string containing either a direct answer from Tavily's AI or a formatted summary of the top 3 search results, with each result containing the title and snippet

        Raises:
            ValueError: When authentication credentials are invalid or missing (via validate() method)
            HTTPError: When the API request fails or returns an error response

        Tags:
            search, ai, web, query, important, api-client, text-processing
        """
        url = f"{self.base_url}/search"
        payload = {
            "query": query,
            "topic": "general",
            "search_depth": "basic",
            "max_results": 3,
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False,
            "include_image_descriptions": False,
            "include_domains": [],
            "exclude_domains": [],
        }
        response = self._post(url, payload)
        result = response.json()
        if "answer" in result:
            return result["answer"]
        summaries = []
        for item in result.get("results", [])[:3]:
            summaries.append(f"• {item['title']}: {item['snippet']}")
        return "\n".join(summaries)

    def list_tools(self):
        return [self.search]
