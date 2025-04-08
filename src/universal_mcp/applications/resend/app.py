from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class ResendApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="resend", integration=integration)

    def _get_headers(self):
        credentials = self.integration.get_credentials()
        if not credentials:
            raise ValueError("No credentials found")
        return {
            "Authorization": f"Bearer {credentials['api_key']}",
        }

    def send_email(self, to: str, subject: str, content: str) -> str:
        """Send an email using the Resend API

        Args:
            to: The email address to send the email to
            subject: The subject of the email
            content: The content of the email

        Returns:
            A message indicating that the email was sent successfully
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
