import typer
from pathlib import Path

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_claude,
    install_cursor,
)

app = typer.Typer()


@app.command()
def generate(schema_path: Path = typer.Option(..., "--schema", "-s")):
    """Generate API client from OpenAPI schema"""
    if not schema_path.exists():
        typer.echo(f"Error: Schema file {schema_path} does not exist", err=True)
        raise typer.Exit(1)
    from .utils.openapi import generate_api_client, load_schema

    try:
        schema = load_schema(schema_path)
    except Exception as e:
        typer.echo(f"Error loading schema: {e}", err=True)
        raise typer.Exit(1)
    code = generate_api_client(schema)
    print(code)


@app.command()
def run(
    transport: str = typer.Option("stdio", "--transport", "-t"),
    server_type: str = typer.Option(
        "agentr", "--server-type", "-s", help="Server type: local or agentr"
    ),
    config_path: Path = typer.Option(
        "local_config.json", "--config", "-c", help="Path to the config file"
    ),
):
    """Run the MCP server"""
    from universal_mcp.servers.server import AgentRServer, LocalServer

    if server_type.lower() == "agentr":
        mcp = AgentRServer(name="AgentR Server", description="AgentR Server", port=8005)
    elif server_type.lower() == "local":
        mcp = LocalServer(
            name="Local Server",
            description="Local Server",
            port=8005,
            config_path=config_path,
        )
    else:
        typer.echo(
            f"Invalid server type: {server_type}. Must be 'local' or 'agentr'", err=True
        )
        raise typer.Exit(1)

    mcp.run(transport=transport)


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
    typer.echo(
        "╭─ Instruction ─────────────────────────────────────────────────────────────────╮"
    )
    typer.echo(
        "│ API key is required. Visit https://agentr.dev to create an API key.           │"
    )
    typer.echo(
        "╰───────────────────────────────────────────────────────────────────────────────╯"
    )

    # Prompt for API key
    api_key = typer.prompt("Enter your AgentR API key", hide_input=True)
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
        import traceback

        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
