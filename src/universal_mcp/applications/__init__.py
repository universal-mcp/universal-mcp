from universal_mcp.applications.application import APIApplication, Application
from universal_mcp.applications.github.app import GithubApp
from universal_mcp.applications.google_calendar.app import GoogleCalendarApp
from universal_mcp.applications.google_mail.app import GmailApp
from universal_mcp.applications.markitdown.app import MarkitdownApp
from universal_mcp.applications.reddit.app import RedditApp
from universal_mcp.applications.resend.app import ResendApp
from universal_mcp.applications.tavily.app import TavilyApp
from universal_mcp.applications.zenquotes.app import ZenQuoteApp


def app_from_name(name: str):
    name = name.lower().strip()
    name = name.replace(" ", "-")
    if name == "zenquotes":
        return ZenQuoteApp
    elif name == "tavily":
        return TavilyApp
    elif name == "github":
        return GithubApp
    elif name == "google-calendar":
        return GoogleCalendarApp
    elif name == "google-mail":
        return GmailApp
    elif name == "resend":
        return ResendApp
    elif name == "reddit":
        return RedditApp
    elif name == "markitdown":
        return MarkitdownApp
    else:
        raise ValueError(f"App {name} not found")


__all__ = ["app_from_name", "Application", "APIApplication"]
