from universal_mcp.applications.application import APIApplication


class ZenquotesApp(APIApplication):
    def __init__(self, **kwargs) -> None:
        super().__init__(name="zenquote", **kwargs)

    def get_quote(self) -> str:
        """Get an inspirational quote from the Zen Quotes API

        Returns:
            A random inspirational quote
        """
        url = "https://zenquotes.io/api/random"
        response = self._get(url)
        data = response.json()
        quote_data = data[0]
        return f"{quote_data['q']} - {quote_data['a']}"

    def list_tools(self):
        return [self.get_quote]
