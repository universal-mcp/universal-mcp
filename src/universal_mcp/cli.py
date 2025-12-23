# from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_app,
)
from universal_mcp.utils.openapi.cli import app as codegen_app

# Setup rich console and logging
console = Console()

app = typer.Typer(name="mcp")
app.add_typer(codegen_app, name="codegen", help="Code generation and manipulation commands")


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


if __name__ == "__main__":
    app()
