from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class TavilyApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        name = "tavily"
        self.base_url = "https://api.tavily.com"
        super().__init__(name=name, integration=integration)
        self.api_key = None

    def _get_headers(self):
        if not self.api_key:
            credentials = self.integration.get_credentials()
            if not credentials:
                raise ValueError("No credentials found")
            api_key = (
                credentials.get("api_key")
                or credentials.get("API_KEY")
                or credentials.get("apiKey")
            )
            if not api_key:
                raise ValueError("No API key found")
            self.api_key = api_key
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def search(self, query: str) -> str:
        """Search the web using Tavily's search API

        Args:
            query: The search query

        Returns:
            str: A summary of search results
        """
        self.validate()
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

        # Fallback to combining top results if no direct answer
        summaries = []
        for item in result.get("results", [])[:3]:
            summaries.append(f"• {item['title']}: {item['snippet']}")

        return "\n".join(summaries)

    def list_tools(self):
        return [self.search]
