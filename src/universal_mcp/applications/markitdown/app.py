from markitdown import MarkItDown

from universal_mcp.applications.application import Application


class MarkitdownApp(Application):
    def __init__(self, **kwargs):
        super().__init__(name="markitdown", **kwargs)
        self.markitdown = MarkItDown()

    async def convert_to_markdown(self, uri: str) -> str:
        """Convert a web page, file, or data URI to markdown format.

        Args:
            uri (str): The URI to convert. Supported URI schemes:
                - http:// or https:// for web pages
                - file:// for local files
                - data: for data URIs

        Returns:
            str: The markdown representation of the resource content.

        Example:
            >>> await convert_to_markdown("https://example.com")
            "# Example Domain\n\nThis domain is for use in illustrative examples..."
        """
        return self.markitdown.convert_uri(uri).markdown

    def list_tools(self):
        return [
            self.convert_to_markdown,
        ]
