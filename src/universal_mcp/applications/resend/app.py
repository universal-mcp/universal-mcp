from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class ResendApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="resend", integration=integration)

    def send_email(self, to: str, subject: str, content: str) -> str:
        """
        Sends an email using the Resend API with specified recipient, subject, and content

        Args:
            to: Email address of the recipient
            subject: Subject line of the email
            content: Main body text content of the email

        Returns:
            String message confirming successful email delivery ('Sent Successfully')

        Raises:
            ValueError: Raised when no valid credentials are found for the API

        Tags:
            send, email, api, communication, important
        """
        credentials = self.integration.get_credentials()
        if not credentials:
            raise ValueError("No credentials found")
        from_email = credentials.get("from_email", "Manoj <manoj@agentr.dev>")
        url = "https://api.resend.com/emails"
        body = {"from": from_email, "to": [to], "subject": subject, "text": content}
        self._post(url, body)
        return "Sent Successfully"

    def list_tools(self):
        return [self.send_email]
