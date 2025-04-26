import asyncio
import os
from pathlib import Path
import re  # for app name validation

import typer
from rich import print as rprint
from rich.panel import Panel

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_claude,
    install_cursor,
)

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
    add_docstrings: bool = typer.Option(
        True, "--docstrings/--no-docstrings", help="Add docstrings to generated code"
    ),
):
    """Generate API client from OpenAPI schema with optional docstring generation.

    The output filename should match the name of the API in the schema (e.g., 'twitter.py' for Twitter API).
    This name will be used for the folder in applications/.
    """
    # Import here to avoid circular imports
    from universal_mcp.utils.api_generator import generate_api_from_schema

    if not schema_path.exists():
        typer.echo(f"Error: Schema file {schema_path} does not exist", err=True)
        raise typer.Exit(1)

    try:
        # Run the async function in the event loop
        result = asyncio.run(
            generate_api_from_schema(
                schema_path=schema_path,
                output_path=output_path,
                add_docstrings=add_docstrings,
            )
        )

        if not output_path:
            # Print to stdout if no output path
            print(result["code"])
        else:
            typer.echo("API client successfully generated and installed.")
            if "app_file" in result:
                typer.echo(f"Application file: {result['app_file']}")
            if "readme_file" in result and result["readme_file"]:
                typer.echo(f"Documentation: {result['readme_file']}")
    except Exception as e:
        typer.echo(f"Error generating API client: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def docgen(
    file_path: Path = typer.Argument(..., help="Path to the Python file to process"),
    model: str = typer.Option(
        "anthropic/claude-3-5-sonnet-20241022",
        "--model",
        "-m",
        help="Model to use for generating docstrings",
    ),
    api_key: str = typer.Option(
        None,
        "--api-key",
        help="Anthropic API key (can also be set via ANTHROPIC_API_KEY environment variable)",
    ),
):
    """Generate docstrings for Python files using LLMs.

    This command uses litellm with structured output to generate high-quality
    Google-style docstrings for all functions in the specified Python file.
    """
    from universal_mcp.utils.docgen import process_file

    if not file_path.exists():
        typer.echo(f"Error: File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Set API key if provided
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    try:
        processed = process_file(str(file_path), model)
        typer.echo(f"Successfully processed {processed} functions")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def run(
    config_path: Path | None = typer.Option(
        None, "--config", "-c", help="Path to the config file"
    ),
):
    """Run the MCP server"""
    from universal_mcp.config import ServerConfig
    from universal_mcp.logger import setup_logger
    from universal_mcp.servers import server_from_config

    setup_logger()

    if config_path:
        config = ServerConfig.model_validate_json(config_path.read_text())
    else:
        config = ServerConfig()
    server = server_from_config(config)
    server.run(transport=config.transport)


@app.command()
def install(app_name: str = typer.Argument(..., help="Name of app to install")):
    """Install an app"""
    # List of supported apps
    supported_apps = get_supported_apps()

    if app_name not in supported_apps:
        typer.echo("Available apps:")
        for app in supported_apps:
            typer.echo(f"  - {app}")
        typer.echo(f"\nApp '{app_name}' not supported")
        raise typer.Exit(1)

    # Print instructions before asking for API key

    rprint(
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
        if app_name == "claude":
            typer.echo(f"Installing mcp server for: {app_name}")
            install_claude(api_key)
            typer.echo("App installed successfully")
        elif app_name == "cursor":
            typer.echo(f"Installing mcp server for: {app_name}")
            install_cursor(api_key)
            typer.echo("App installed successfully")
    except Exception as e:
        typer.echo(f"Error installing app: {e}", err=True)
        raise typer.Exit(1) from e

@app.command()
def init():
    """Interactively initialize a new MCP project with validation."""
    # Ask for app name
    app_name = typer.prompt("Enter the app name", default="app_name", prompt_suffix=" (e.g., reddit, youtube): ").strip()

    # Validate app_name
    if not re.match(r"^[a-zA-Z0-9_]+$", app_name):
        typer.secho("❌ Error: App name should only contain letters, numbers, and underscores (no spaces or special characters).", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Ask for path
    path_input = typer.prompt("Enter the path to create the project", default=".", prompt_suffix=" (e.g., /home/user/Desktop): ").strip()
    path = Path(path_input)

    # Validate path
    if not path.exists() or not path.is_dir():
        typer.secho(f"❌ Error: Provided path '{path}' does not exist or is not a directory.", fg=typer.colors.RED)
        raise typer.Exit(1)

    base_dir = path / f"universal-mcp-{app_name}"
    src_dir = base_dir / "src" / app_name
    tests_dir = base_dir / "src" / "tests"

    try:
        # Create directories
        src_dir.mkdir(parents=True, exist_ok=False)
        tests_dir.mkdir(parents=True, exist_ok=False)

        # Create files with basic starter content
        (base_dir / "pyproject.toml").write_text(f"[project]\nname = 'universal-mcp-{app_name}'\nversion = '0.1.0'\n")
        (base_dir / "README.md").write_text(f"# Universal MCP {app_name.capitalize()}\n\nGenerated by MCP CLI.")

        (src_dir / "__init__.py").write_text("")
        (src_dir / "__main__.py").write_text(f"from .app import main\n\nif __name__ == '__main__':\n    main()")
        (src_dir / "app.py").write_text(f"def main():\n    print('Hello from {app_name}!')\n")

        (tests_dir / f"test_{app_name}.py").write_text(f"def test_dummy():\n    assert True\n")

        typer.secho(f"✅ Project 'universal-mcp-{app_name}' initialized successfully at {base_dir}!", fg=typer.colors.GREEN)
    except FileExistsError:
        typer.secho(f"❌ Error: Directory '{base_dir}' already exists.", fg=typer.colors.RED)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"❌ Error initializing project: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
