import yaml

from universal_mcp.applications import app_from_slug
from universal_mcp.tools.tools import Tool


def load_yaml():
    with open("applications.yaml") as f:
        data = yaml.safe_load(f)
    if data is None:
        data = {}
    return data


def write_yaml(data):
    with open("applications.yaml", "w") as f:
        yaml.dump(data, f)


apps = [
    "ahrefs",
    "cal-com-v2",
    "calendly",
    "clickup",
    "coda",
    "crustdata",
    "e2b",
    "elevenlabs",
    "falai",
    "figma",
    "firecrawl",
    "github",
    "gong",
    "google-calendar",
    "google-docs",
    "google-drive",
    "google-mail",
    "google-sheet",
    "hashnode",
    "heygen",
    "klaviyo",
    "mailchimp",
    "markitdown",
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
    "shortcut",
    "spotify",
    "supabase",
    "tavily",
    "wrike",
    "youtube",
    "zenquotes",
]

for app in apps:
    app = app_from_slug(app)
    app_instance = app(integration=None)
    tools = app_instance.list_tools()
    data = load_yaml()
    tools_data = []
    for tool in tools:
        tool_instance = Tool.from_function(tool)
        tools_data.append(
            {
                "name": tool_instance.name,
                "description": tool_instance.description,
                "important": "important" in tool_instance.tags,
            }
        )
    data[app_instance.name] = tools_data
    write_yaml(data)
