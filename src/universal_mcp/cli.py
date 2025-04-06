import typer
from pathlib import Path
import os

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_claude,
    install_cursor,
)

app = typer.Typer()


@app.command()
def generate(
    schema_path: Path = typer.Option(..., "--schema", "-s"),
    output_path: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    add_docstrings: bool = typer.Option(True, "--docstrings/--no-docstrings", help="Add docstrings to generated code"),
):
    """Generate API client from OpenAPI schema with optional docstring generation"""
    import asyncio
    
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
    
    if output_path:
        # Save to file if output path is provided
        with open(output_path, "w") as f:
            f.write(code)
        typer.echo(f"Generated API client at: {output_path}")
        
        # Verify the file was written correctly
        try:
            with open(output_path, "r") as f:
                file_content = f.read()
                typer.echo(f"Successfully wrote {len(file_content)} bytes to {output_path}")
                
                # Basic syntax check
                import ast
                try:
                    ast.parse(file_content)
                    typer.echo("Python syntax check passed")
                except SyntaxError as e:
                    typer.echo(f"Warning: Generated file has syntax error: {e}", err=True)
        except Exception as e:
            typer.echo(f"Error verifying output file: {e}", err=True)
        
        # Add docstrings if requested
        if add_docstrings:
            from universal_mcp.react_agent.graph import graph
            
            async def run_docstring():
                # Convert output_path to string if it's a Path object
                script_path = str(output_path)
                typer.echo(f"Adding docstrings to {script_path}...")
                
                # Debug: Check if the file exists
                if not os.path.exists(script_path):
                    typer.echo(f"Warning: File {script_path} does not exist", err=True)
                    return None
                
                # Debug: Try reading the file
                try:
                    with open(script_path, "r") as f:
                        content = f.read()
                        typer.echo(f"Successfully read {len(content)} bytes from {script_path}")
                except Exception as e:
                    typer.echo(f"Error reading file for docstring generation: {e}", err=True)
                    return None
                
                # Create input state with target_script_path
                input_state = {"target_script_path": script_path}
                typer.echo(f"Passing input state: {input_state}")
                
                try:
                    result = await graph.ainvoke(
                        input_state, 
                        {"recursion_limit": 100}
                    )
                    return result
                except Exception as e:
                    typer.echo(f"Error running docstring generation: {e}", err=True)
                    import traceback
                    traceback.print_exc()
                    return None
            
            result = asyncio.run(run_docstring())
            
            if result:
                # Get the path to the file with docstrings (the _new file)
                output_dir = output_path.parent
                file_name = output_path.name
                file_name_without_ext, ext = os.path.splitext(file_name)
                new_file_path = output_dir / f"{file_name_without_ext}_new{ext}"
                
                if "functions_processed" in result:
                    typer.echo(f"Processed {result['functions_processed']} functions")
                
                if os.path.exists(new_file_path):
                    typer.echo(f"API client with docstrings generated at: {new_file_path}")
                else:
                    typer.echo(f"Error: Expected output file {new_file_path} not found", err=True)
            else:
                typer.echo("Docstring generation failed", err=True)
    else:
        # Print to stdout if no output path
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
