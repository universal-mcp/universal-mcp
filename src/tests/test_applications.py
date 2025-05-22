import pytest
from loguru import logger

from universal_mcp.applications import app_from_slug
from universal_mcp.tools.tools import Tool

ALL_APPS = [
    "ahrefs",
    "airtable",
    "apollo",
    "asana",
    "box",
    "braze",
    "cal-com-v2",
    "confluence",
    "calendly",
    "canva",
    "clickup",
    "coda",
    "crustdata",
    "e2b",
    "elevenlabs",
    "exa",
    "falai",
    "figma",
    "firecrawl",
    "github",
    "gong",
    "google-calendar",
    "google-docs",
    "google-drive",
    "google-gemini",
    "google-mail",
    "google-sheet",
    "hashnode",
    "heygen",
    "jira",
    "klaviyo",
    "mailchimp",
    "markitdown",
    "miro",
    "neon",
    "notion",
    "perplexity",
    "pipedrive",
    "posthog",
    "reddit",
    "replicate",
    "resend",
    "retell",
    "rocketlane",
    "serpapi",
    "shopify",
    "shortcut",
    "spotify",
    "supabase",
    "tavily",
    "trello",
    "whatsapp-business",
    "wrike",
    "youtube",
    "zenquotes",
]


@pytest.fixture
def app(app_name):
    return app_from_slug(app_name)


class TestApplications:
    @pytest.mark.parametrize(
        "app_name",
        ALL_APPS,
    )
    def test_application(self, app, app_name):
        assert app is not None
        app_instance = app(integration=None)
        assert app_instance.name == app_name
        tools = app_instance.list_tools()
        logger.info(f"Tools for {app_name}: {len(tools)}")
        assert len(tools) > 0, f"No tools found for {app_name}"
        tools = [Tool.from_function(tool) for tool in tools]
        important_tools = []
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            if "important" in tool.tags:
                important_tools.append(tool.name)
        assert len(important_tools) > 0, f"No important tools found for {app_name}"
