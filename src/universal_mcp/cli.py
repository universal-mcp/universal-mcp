import re
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_app,
)

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
        # Run the async function in the event loop
        app_file = generate_api_from_schema(
            schema_path=schema_path,
            output_path=output_path,
            class_name=class_name,
        )
        console.print("[green]API client successfully generated and installed.[/green]")
        console.print(f"[blue]Application file: {app_file}[/blue]")
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

    setup_logger()

    config = ServerConfig.model_validate_json(config_path.read_text()) if config_path else ServerConfig()
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


if __name__ == "__main__":
    app()
