import yaml
from loguru import logger
from tqdm import tqdm

from universal_mcp.applications import app_from_slug
from universal_mcp.tools.tools import Tool

file_path = "actions.yaml"


def load_yaml():
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        data = {}
    return data


def write_yaml(data):
    with open(file_path, "w") as f:
        yaml.dump(data, f)


apps = [
    "ahrefs",
    "airtable",
    "apollo",
    "asana",
    "braze",
    "cal-com-v2",
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

for app in tqdm(apps, desc="Processing applications", unit="app"):
    try:
        # Load application class and create instance
        app_class = app_from_slug(app)
        app_instance = app_class(integration=None)

        # Get tools and prepare data
        tools = app_instance.list_tools()
        data = load_yaml()
        tools_data = []

        # Process each tool
        for tool in tools:
            tool_instance = Tool.from_function(tool)
            tool_data = {
                "id": f"{app}_{tool_instance.name}",
                "app_id": app,
                "name": tool_instance.name,
                "description": tool_instance.description,
                "important": "important" in tool_instance.tags,
            }
            tools_data.append(tool_data)

        # Update and save data
        data[app_instance.name] = tools_data
        write_yaml(data)

    except Exception as e:
        logger.error(f"Error processing {app}: {str(e)}")
        continue
