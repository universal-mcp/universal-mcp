import typer
from pathlib import Path
import sys

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
def run():
    """Run the MCP server"""
    from universal_mcp.servers.server import AgentRServer
    mcp = AgentRServer(name="AgentR Server", description="AgentR Server")
    mcp.run()

@app.command()
def install(app_name: str = typer.Argument(..., help="Name of app to install")):
    """Install an app"""
    # List of supported apps
    supported_apps = ["claude", "cursor"]
    
    if app_name not in supported_apps:
        typer.echo("Available apps:")
        for app in supported_apps:
            typer.echo(f"  - {app}")
        typer.echo(f"\nApp '{app_name}' not supported")
        raise typer.Exit(1)

    import json

    # Print instructions before asking for API key
    typer.echo("╭─ Instruction ─────────────────────────────────────────────────────────────────╮")
    typer.echo("│ API key is required. Visit https://agentr.dev to create an API key.           │")
    typer.echo("╰───────────────────────────────────────────────────────────────────────────────╯")
    
    # Prompt for API key
    api_key = typer.prompt("Enter your AgentR API key", hide_input=True)

    if app_name == "claude":
        typer.echo(f"Installing mcp server for: {app_name}")

        # Determine platform-specific config path
        if sys.platform == "darwin":  # macOS
            config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        elif sys.platform == "win32":  # Windows
            config_path = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
        else:
            typer.echo("Unsupported platform. Only macOS and Windows are currently supported.", err=True)
            raise typer.Exit(1)
        
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        config['mcpServers']['agentr'] = {
            "command": "uvx",
            "args": ["agentr@latest", "run"],
            "env": {
                "AGENTR_API_KEY": api_key
            }
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        typer.echo("App installed successfully")
    elif app_name == "cursor":
        typer.echo(f"Installing mcp server for: {app_name}")
        
        # Set up Cursor config path
        config_path = Path.home() / ".cursor/mcp.json"
        
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create or load existing config
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}

        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        config['mcpServers']['agentr'] = {
            "command": "uvx",
            "args": ["agentr@latest", "run"],
            "env": {
                "AGENTR_API_KEY": api_key
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        typer.echo("App installed successfully")

if __name__ == "__main__":
    app()
