import re
import json
from pathlib import Path
from typing import Optional, Dict
import asyncio

import typer
from rich.console import Console
from rich.panel import Panel

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_app,
)
# New imports for agent and refactored client
from universal_mcp.agents.cli_agent import CLIAgent
from universal_mcp.client.chat_client import RichCLIClient
# Import MultiClientServer if it's to be instantiated here
from universal_mcp.client.client import MultiClientServer
from universal_mcp.config import ClientTransportConfig # For MultiClientServer


# Setup rich console and logging
console = Console()

app = typer.Typer()


@app.command()
def generate(
    schema_path: Path = typer.Option(..., "--schema", "-s"),
    output_path: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path - should match the API name (e.g., 'twitter.py' for Twitter API)",
    ),
    class_name: str = typer.Option(
        None,
        "--class-name",
        "-c",
        help="Class name to use for the API client",
    ),
):
    """Generate API client from OpenAPI schema with optional docstring generation.

    The output filename should match the name of the API in the schema (e.g., 'twitter.py' for Twitter API).
    This name will be used for the folder in applications/.
    """
    # Import here to avoid circular imports
    from universal_mcp.utils.openapi.api_generator import generate_api_from_schema

    if not schema_path.exists():
        console.print(f"[red]Error: Schema file {schema_path} does not exist[/red]")
        raise typer.Exit(1)

    try:
        app_file_data = generate_api_from_schema(
            schema_path=schema_path,
            output_path=output_path,
            class_name=class_name,
        )
        if isinstance(app_file_data, dict) and "code" in app_file_data:
            console.print("[yellow]No output path specified, printing generated code to console:[/yellow]")
            console.print(app_file_data["code"])
        elif isinstance(app_file_data, Path):
            console.print("[green]API client successfully generated and installed.[/green]")
            console.print(f"[blue]Application file: {app_file_data}[/blue]")
        else:
            # Handle the error case from api_generator if validation fails
            if isinstance(app_file_data, dict) and "error" in app_file_data:
                console.print(f"[red]{app_file_data['error']}[/red]")
                raise typer.Exit(1)
            else:
                console.print("[red]Unexpected return value from API generator.[/red]")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error generating API client: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def readme(
    file_path: Path = typer.Argument(..., help="Path to the Python file to process"),
):
    """Generate a README.md file for the API client."""
    from universal_mcp.utils.openapi.readme import generate_readme

    readme_file = generate_readme(file_path)
    console.print(f"[green]README.md file generated at: {readme_file}[/green]")


@app.command()
def docgen(
    file_path: Path = typer.Argument(..., help="Path to the Python file to process"),
    model: str = typer.Option(
        "perplexity/sonar",
        "--model",
        "-m",
        help="Model to use for generating docstrings",
    ),
):
    """Generate docstrings for Python files using LLMs.

    This command uses litellm with structured output to generate high-quality
    Google-style docstrings for all functions in the specified Python file.
    """
    from universal_mcp.utils.openapi.docgen import process_file

    if not file_path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        raise typer.Exit(1)

    try:
        processed = process_file(str(file_path), model)
        console.print(f"[green]Successfully processed {processed} functions[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def run(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to the config file"),
):
    """Run the MCP server"""
    from universal_mcp.config import ServerConfig
    from universal_mcp.logger import setup_logger
    from universal_mcp.servers import server_from_config

    config = ServerConfig.model_validate_json(config_path.read_text()) if config_path else ServerConfig()
    setup_logger(level=config.log_level)
    server = server_from_config(config)
    server.run(transport=config.transport)


@app.command()
def install(app_name: str = typer.Argument(..., help="Name of app to install")):
    """Install an app"""
    # List of supported apps
    supported_apps = get_supported_apps()

    if app_name not in supported_apps:
        console.print("[yellow]Available apps:[/yellow]")
        for app in supported_apps:
            console.print(f"  - {app}")
        console.print(f"\n[red]App '{app_name}' not supported[/red]")
        raise typer.Exit(1)

    # Print instructions before asking for API key
    console.print(
        Panel(
            "API key is required. Visit [link]https://agentr.dev[/link] to create an API key.",
            title="Instruction",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Prompt for API key
    api_key = typer.prompt(
        "Enter your AgentR API key",
        hide_input=False,
        show_default=False,
        type=str,
    )
    try:
        install_app(app_name, api_key)
    except Exception as e:
        console.print(f"[red]Error installing app: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def init(
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for the project (must exist)",
    ),
    app_name: str | None = typer.Option(
        None,
        "--app-name",
        "-a",
        help="App name (letters, numbers, hyphens, underscores only)",
    ),
    integration_type: str | None = typer.Option(
        None,
        "--integration-type",
        "-i",
        help="Integration type (api_key, oauth, agentr, none)",
        case_sensitive=False,
        show_choices=True,
    ),
):
    """Initialize a new MCP project using the cookiecutter template."""
    from cookiecutter.main import cookiecutter

    NAME_PATTERN = r"^[a-zA-Z0-9_-]+$"

    def validate_pattern(value: str, field_name: str) -> None:
        if not re.match(NAME_PATTERN, value):
            console.print(
                f"[red]❌ Invalid {field_name}; only letters, numbers, hyphens, and underscores allowed.[/red]"
            )
            raise typer.Exit(code=1)

    # App name
    if not app_name:
        app_name = typer.prompt(
            "Enter the app name",
            default="app_name",
            prompt_suffix=" (e.g., reddit, youtube): ",
        ).strip()
    validate_pattern(app_name, "app name")
    app_name = app_name.lower()
    if not output_dir:
        path_str = typer.prompt(
            "Enter the output directory for the project",
            default=str(Path.cwd()),
            prompt_suffix=": ",
        ).strip()
        output_dir = Path(path_str)

    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✅ Created output directory at '{output_dir}'[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to create output directory '{output_dir}': {e}[/red]")
            raise typer.Exit(code=1) from e
    elif not output_dir.is_dir():
        console.print(f"[red]❌ Output path '{output_dir}' exists but is not a directory.[/red]")
        raise typer.Exit(code=1)

    # Integration type
    if not integration_type:
        integration_type = typer.prompt(
            "Choose the integration type",
            default="agentr",
            prompt_suffix=" (api_key, oauth, agentr, none): ",
        ).lower()
    if integration_type not in ("api_key", "oauth", "agentr", "none"):
        console.print("[red]❌ Integration type must be one of: api_key, oauth, agentr, none[/red]")
        raise typer.Exit(code=1)

    console.print("[blue]🚀 Generating project using cookiecutter...[/blue]")
    try:
        cookiecutter(
            "https://github.com/AgentrDev/universal-mcp-app-template.git",
            output_dir=str(output_dir),
            no_input=True,
            extra_context={
                "app_name": app_name,
                "integration_type": integration_type,
            },
        )
    except Exception as exc:
        console.print(f"❌ Project generation failed: {exc}")
        raise typer.Exit(code=1) from exc

    project_dir = output_dir / f"{app_name}"
    console.print(f"✅ Project created at {project_dir}")


@app.command()
def preprocess(
    schema_path: Path = typer.Option(None, "--schema", "-s", help="Path to the OpenAPI schema file."),
    output_path: Path = typer.Option(None, "--output", "-o", help="Path to save the processed schema."),
):
    from universal_mcp.utils.openapi.preprocessor import run_preprocessing

    """Preprocess an OpenAPI schema using LLM to fill or enhance descriptions."""
    run_preprocessing(schema_path, output_path)


@app.command()
def split_api(
    input_app_file: Path = typer.Argument(..., help="Path to the generated app.py file to split"),
    output_dir: Path = typer.Option(..., "--output-dir", "-o", help="Directory to save the split files"),
    package_name: str = typer.Option(None, "--package-name", "-p", help="Package name for absolute imports (e.g., 'hubspot')"),
):
    """Splits a single generated API client file into multiple files based on path groups."""
    from universal_mcp.utils.openapi.api_splitter import split_generated_app_file

    if not input_app_file.exists() or not input_app_file.is_file():
        console.print(f"[red]Error: Input file {input_app_file} does not exist or is not a file.[/red]")
        raise typer.Exit(1)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]Created output directory: {output_dir}[/green]")
    elif not output_dir.is_dir():
        console.print(f"[red]Error: Output path {output_dir} is not a directory.[/red]")
        raise typer.Exit(1)

    try:
        split_generated_app_file(input_app_file, output_dir, package_name)
        console.print(f"[green]Successfully split {input_app_file} into {output_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Error splitting API client: {e}[/red]")

        raise typer.Exit(1) from e

# New chat command
@app.command()
def chat(
    servers_json_path: Optional[Path] = typer.Option(
        None,
        "--servers-json",
        "-j",
        help=(
            "Path to a JSON configuration file. "
            "Expected structure: \n"
            "{ \n"
            "  \"agent_sse_url\": \"http://<agent_host>:<port>/sse\", \n"
            "  \"tool_servers\": { \n"
            "    \"<server_name>\": { \"url\": \"...\", \"transport\": \"sse\", ... } \n"
            "  } \n"
            "}\n"
            "If 'agent_sse_url' is present, it overrides the --url option for the agent's connection. "
            "'tool_servers' configures the MultiClientServer for external tools."
        ),
        rich_help_panel="Configuration",
    ),
    url: str = typer.Option(
        "http://localhost:8005/sse",
        "--url",
        help="URL of the primary Agent's SSE endpoint. This is overridden if 'agent_sse_url' is specified in the --servers-json file.",
        rich_help_panel="Configuration",
    ),
    # Consider adding a log level option here if useful for debugging client/agent later
):
    """
    Initiates an interactive chat session with an AI agent.

    The client connects to an agent's Server-Sent Events (SSE) endpoint for
    streaming responses. You can specify the agent's SSE URL using the --url
    option or through a configuration file with --servers-json.

    The --servers-json file can also define connection details for external
    tool servers, which the agent might use.
    """

    console.print("[info]Initializing chat environment...[/info]")

    agent_sse_url = url  # Default to the command line --url argument
    tool_server_configs: Dict[str, ClientTransportConfig] = {}

    if servers_json_path:
        console.print(f"[info]Attempting to load server configurations from: {servers_json_path}[/info]")
        if servers_json_path.exists() and servers_json_path.is_file():
            try:
                with open(servers_json_path, 'r') as f:
                    config_data = json.load(f)

                if isinstance(config_data, dict):
                    # Determine Agent SSE URL: servers_json_path["agent_sse_url"] > servers_json_path["url"] > --url CLI > default
                    if "agent_sse_url" in config_data and isinstance(config_data["agent_sse_url"], str):
                        agent_sse_url = config_data["agent_sse_url"]
                        console.print(f"[info]Using Agent SSE URL from JSON (key 'agent_sse_url'): {agent_sse_url}[/info]")
                    elif "url" in config_data and isinstance(config_data["url"], str):
                        # Fallback to 'url' key in JSON if 'agent_sse_url' is not present
                        agent_sse_url = config_data["url"]
                        console.print(f"[info]Using Agent SSE URL from JSON (key 'url'): {agent_sse_url}[/info]")
                    else:
                        console.print(f"[info]No 'agent_sse_url' or 'url' key for agent in {servers_json_path}. Using --url value: {agent_sse_url}[/info]")

                    # Parse tool_servers
                    raw_tool_servers = config_data.get("tool_servers", {})
                    if isinstance(raw_tool_servers, dict):
                        for name, conf_dict in raw_tool_servers.items():
                            if isinstance(conf_dict, dict):
                                try:
                                    # Ensure essential keys for ClientTransportConfig are present
                                    # url and transport are typically required.
                                    # ClientTransportConfig will validate further.
                                    cfg = ClientTransportConfig(**conf_dict)
                                    tool_server_configs[name] = cfg
                                    console.print(f"[info]Loaded tool server config: '{name}'[/info]")
                                except TypeError as te: # Catches missing required args for ClientTransportConfig
                                     console.print(f"[red]Error parsing tool server '{name}' from {servers_json_path}: Missing required fields for ClientTransportConfig ({te}). Skipping.[/red]")
                                except Exception as e:
                                    console.print(f"[red]Error parsing tool server '{name}' from {servers_json_path}: {e}. Skipping.[/red]")
                            else:
                                console.print(f"[yellow]Warning: Tool server entry '{name}' in {servers_json_path} is not a valid dictionary. Skipping.[/yellow]")
                        if not tool_server_configs and raw_tool_servers: # check if raw_tool_servers was not empty
                             console.print(f"[info]'tool_servers' in {servers_json_path} was present but all entries were invalid or empty.[/info]")
                    elif raw_tool_servers: # If it exists but is not a dict
                        console.print(f"[yellow]Warning: 'tool_servers' in {servers_json_path} is not a dictionary. Skipping tool server configuration.[/yellow]")
                    else: # 'tool_servers' key is missing
                        console.print(f"[info]No 'tool_servers' key found in {servers_json_path}. No external tool servers will be configured.[/info]")

                else: # config_data is not a dict
                    console.print(f"[yellow]Warning: Invalid format in {servers_json_path}. Expected a JSON object. Using --url for agent: {agent_sse_url}[/yellow]")

            except json.JSONDecodeError:
                console.print(f"[red]Error: Could not decode JSON from {servers_json_path}. Using --url for agent: {agent_sse_url}[/red]")
            except Exception as e:
                console.print(f"[red]Error reading {servers_json_path}: {e}. Using --url for agent: {agent_sse_url}[/red]")
        else: # path doesn't exist or not a file
            console.print(f"[yellow]Warning: Config file not found or is not a regular file: {servers_json_path}. Using --url for agent: {agent_sse_url}[/yellow]")
    else: # servers_json_path not provided
        console.print(f"[info]No --servers-json provided. Using --url for Agent SSE: {agent_sse_url}[/info]")
        console.print(f"[info]No external tool servers will be configured.[/info]")


    mcp_multiclient = None
    if tool_server_configs:
        try:
            mcp_multiclient = MultiClientServer(clients=tool_server_configs)
            console.print(f"[info]MultiClientServer instantiated with {len(tool_server_configs)} tool server(s).[/info]")
        except Exception as e:
            console.print(f"[red]Failed to instantiate MultiClientServer: {e}. Proceeding without it.[/red]")
            mcp_multiclient = None # Ensure it's None if instantiation fails
    else:
        console.print("[info]MultiClientServer not instantiated as no valid tool server configurations were loaded.[/info]")

    # Instantiate Agent and UI Client
    try:
        cli_agent = CLIAgent(agent_sse_url=agent_sse_url, mcp_multiclient=mcp_multiclient)
        console.print(f"[info]CLIAgent instantiated for SSE endpoint: {agent_sse_url}[/info]")

        chat_ui = RichCLIClient(agent=cli_agent) # Loop is handled by RichCLIClient's default
        console.print("[info]RichCLIClient UI instantiated.[/info]")
    except Exception as e:
        console.print(f"[red]Fatal Error: Could not initialize agent or UI: {e}[/red]")
        # console.print_exception(show_locals=True) # For more detailed debugging
        raise typer.Exit(code=1)

    loop = asyncio.get_event_loop()
    try:
        console.print("[info]Starting chat session... Type 'exit' or Ctrl+D to quit.[/info]")
        loop.run_until_complete(chat_ui.chat_loop())
    except KeyboardInterrupt:
        console.print("\n[bold red]CLI chat session terminated by user.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred during the chat session: {e}[/bold red]")
        # console.print_exception(show_locals=True) # For more detailed debugging
    finally:
        # Perform any explicit cleanup if necessary, though most is handled by context managers or GC
        console.print("[info]Chat session finished.[/info]")


if __name__ == "__main__":
    app()
