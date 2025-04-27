import asyncio
import os
import re
import subprocess
from pathlib import Path

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
    output_folder_name: str = typer.Option(..., "--name", "-n", help="Name of the output folder (should be the same as the API name, eg. twitter for Twitter API)"),
    output_folder_path: Path = typer.Option(..., "--path", "-p", help="Path where the output folder should be created"),
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
                output_folder_path=output_folder_path,
                output_folder_name=output_folder_name,
                add_docstrings=add_docstrings,
            )
        )

        if not output_folder_path:
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
    """Interactively initialize a new MCP project with populated __main__.py and README."""
    from universal_mcp.utils.templates import (
        extract_class_name,
        generate_app_py_template,
        generate_main_py_template,
        generate_push_script_template,
        generate_pyproject_template,
        generate_readme_template,
        generate_test_template,
    )

    app_name = typer.prompt(
        "Enter the app name",
        default="app_name",
        prompt_suffix=" (e.g., reddit, youtube): "
    ).strip()

    if not re.match(r"^[a-zA-Z0-9_]+$", app_name):
        typer.secho("\u274c Error: App name should only contain letters, numbers, and underscores (no spaces or special characters).", fg=typer.colors.RED)
        raise typer.Exit(1)

    path_input = typer.prompt(
        "Enter the path to create the project",
        default=".",
        prompt_suffix=" (e.g., /home/user/Desktop): "
    ).strip()
    path = Path(path_input)

    if not path.exists() or not path.is_dir():
        typer.secho(f"\u274c Error: Provided path '{path}' does not exist or is not a directory.", fg=typer.colors.RED)
        raise typer.Exit(1)

    base_dir = path / f"universal-mcp-{app_name}"
    src_dir = base_dir / "src" / app_name
    tests_dir = base_dir / "src" / "tests"

    try:
        typer.secho(f"\u2705 Project 'universal-mcp-{app_name}' initialized successfully at {path_input} !", fg=typer.colors.GREEN)

        has_openapi = typer.confirm("Do you have an openapi.json you want to use to populate the project?")

        if has_openapi:
            schema_input = typer.prompt("Enter the path to your openapi.json", prompt_suffix=" (e.g., /home/user/openapi.json): ").strip()
            schema_path = Path(schema_input)

            if not schema_path.exists() or not schema_path.is_file():
                typer.secho(f"\u274c Error: Provided schema path '{schema_path}' does not exist or is not a file.", fg=typer.colors.RED)
                raise typer.Exit(1)

            from universal_mcp.utils.api_generator import generate_api_from_schema
            src_base_dir = base_dir / "src"
            src_base_dir.mkdir(parents=True, exist_ok=False)
            try:
                asyncio.run(
                    generate_api_from_schema(
                        schema_path=schema_path,
                        output_folder_path=src_base_dir,
                        output_folder_name=app_name,
                        add_docstrings=False,
                    )
                )
                typer.secho(f"\u2705 API client successfully generated inside {src_base_dir}!", fg=typer.colors.GREEN)
            except Exception as e:
                typer.secho(f"\u274c Error generating API client: {e}", fg=typer.colors.RED)
                raise typer.Exit(1) from e
        else:
            src_dir.mkdir(parents=True, exist_ok=False)
            (src_dir / "__init__.py").write_text("")
            app_class_name = f"{app_name.capitalize()}App"
            (src_dir / "app.py").write_text(generate_app_py_template(app_class_name, app_name))

        try:
            app_class = extract_class_name(src_dir / "app.py")
        except Exception as e:
            typer.secho(f"\u26a0\ufe0f Warning: Could not extract class name from app.py: {e}", fg=typer.colors.YELLOW)
            app_class = f"{app_name.capitalize()}App"

        tests_dir.mkdir(parents=True, exist_ok=False)
        (tests_dir / f"test_{app_name}.py").write_text(generate_test_template(app_name, app_class))
        (base_dir / "pyproject.toml").write_text(generate_pyproject_template(app_name))
        (base_dir / "README.md").write_text(generate_readme_template(app_name))

        integration_type = typer.prompt(
            "Choose the integration type (api_key, agentr, oauth, none)",
            default="agentr"
        )

        integration_mapping = {
            "api_key": "ApiKeyIntegration",
            "agentr": "AgentRIntegration",
            "none": None,
        }

        integration_class = integration_mapping.get(integration_type)
        if integration_class is None and integration_type != "none":
            typer.secho(f"\u274c Error: Unsupported integration type '{integration_type}'.", fg=typer.colors.RED)
            raise typer.Exit(1)

        main_py_content = generate_main_py_template(
            app_name=app_name,
            app_class=app_class,
            integration_type=integration_type,
            integration_class=integration_class
        )

        (src_dir / "__main__.py").write_text(main_py_content)
        
        push_script_content = generate_push_script_template(app_name)
        push_script_path = base_dir / "push_on_agentr.sh"
        push_script_path.write_text(push_script_content)

        os.chmod(push_script_path, 0o755)
        typer.secho(f"\u2705 Created executable push script {push_script_path}.", fg=typer.colors.GREEN)
    
        typer.secho(f"\u2705 Project 'universal-mcp-{app_name}' initialization completed successfully at {path_input} !", fg=typer.colors.GREEN)

        should_push = typer.confirm("Do you want to push the project to AgentR GitHub now?")
        if should_push:
            try:
                subprocess.run(["./push_on_agentr.sh"], cwd=base_dir, check=True)
                typer.secho("\u2705 Project successfully pushed to AgentR GitHub!", fg=typer.colors.GREEN)
            except subprocess.CalledProcessError as e:
                typer.secho(f"\u274c Error while pushing project: {e}", fg=typer.colors.RED)
        else:
            typer.secho(f"\u2139\ufe0f You can push the project later by running: ./push_on_agentr.sh inside {base_dir}", fg=typer.colors.BLUE)

    except FileExistsError as e:
        typer.secho(f"\u274c Error: Directory '{base_dir}' already exists.", fg=typer.colors.RED)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.secho(f"\u274c Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1) from e

if __name__ == "__main__":
    app()
