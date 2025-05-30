import pytest

from universal_mcp.applications import app_from_slug
from universal_mcp.utils.testing import check_application_instance

ALL_APPS = [
    "ahrefs",
    "airtable",
    "apollo",
    "asana",
    "box",
    # "braze",
    # "cal-com-v2",
    "confluence",
    "calendly",
    "canva",
    # "clickup",
    "coda",
    "crustdata",
    "e2b",
    # "elevenlabs",
    "exa",
    "falai",
    "figma",
    "firecrawl",
    "github",
    "gong",
    "google-calendar",
    "google-docs",
    # "google-drive",
    "google-gemini",
    "google-mail",
    "google-sheet",
    "hashnode",
    "heygen",
    "hubspot",
    # "jira",
    "klaviyo",
    "mailchimp",
    "markitdown",
    "miro",
    "neon",
    "notion",
    "perplexity",
    # "pipedrive",
    "posthog",
    "reddit",
    "replicate",
    "resend",
    "retell",
    "rocketlane",
    "serpapi",
    # "shopify",
    "shortcut",
    "spotify",
    "supabase",
    "tavily",
    "trello",
    "unipile",
    # "whatsapp-business",
    "wrike",
    "youtube",
    "zenquotes",
]


@pytest.mark.parametrize("app_name", ALL_APPS)
def test_application(app_name):
    app = app_from_slug(app_name)
    app_instance = app(integration=None)
    check_application_instance(app_instance, app_name)
