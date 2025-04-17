from markitdown import MarkItDown

from universal_mcp.applications.application import Application


class MarkitdownApp(Application):
    def __init__(self, **kwargs):
        super().__init__(name="markitdown", **kwargs)
        self.markitdown = MarkItDown()

    async def convert_to_markdown(self, uri: str) -> str:
        """Fetches content from a URI and converts its primary textual representation into Markdown.

        This tool aims to extract the main text content from various sources. It supports:
        - Web Pages: General HTML, specific handlers for RSS/Atom feeds, Wikipedia articles (main content), YouTube (transcripts if available), Bing SERPs.
        - Documents: PDF (attempts OCR), DOCX, XLSX, PPTX, XLS, EPUB, Outlook MSG, IPYNB notebooks.
        - Plain Text files.
        - Images: Extracts metadata and attempts OCR to get text.
        - Audio: Extracts metadata and attempts transcription to get text.
        - Archives: ZIP (extracts and attempts to convert supported files within, concatenating results).

        Args:
            uri (str): The URI pointing to the resource. Supported schemes:
                       - http:// or https:// (Web pages, feeds, APIs)
                       - file:// (Local or accessible network files)
                       - data: (Embedded data)

        Returns:
            str: The extracted content converted to Markdown format.
        """
        return self.markitdown.convert_uri(uri).markdown

    def list_tools(self):
        return [
            self.convert_to_markdown,
        ]
