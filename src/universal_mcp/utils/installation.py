import json
import shutil
import sys
from pathlib import Path
from rich import print
from loguru import logger


def get_uvx_path() -> str:
    """Get the full path to the uv executable."""
    uvx_path = shutil.which("uvx")
    if not uvx_path:
        logger.error(
            "uvx executable not found in PATH, falling back to 'uvx'. "
            "Please ensure uvx is installed and in your PATH"
        )
        return "uvx"  # Fall back to just "uvx" if not found
    return uvx_path


def create_file_if_not_exists(path: Path) -> None:
    """Create a file if it doesn't exist"""
    if not path.exists():
        print(f"[yellow]Creating config file at {path}[/yellow]")
        with open(path, "w") as f:
            json.dump({}, f)


def get_supported_apps() -> list[str]:
    """Get list of supported apps"""
    return ["claude", "cursor", "windsurf"]


def install_claude(api_key: str) -> None:
    """Install Claude"""
    print("[bold blue]Installing Claude configuration...[/bold blue]")
    # Determine platform-specific config path
    if sys.platform == "darwin":  # macOS
        config_path = (
            Path.home()
            / "Library/Application Support/Claude/claude_desktop_config.json"
        )
    elif sys.platform == "win32":  # Windows
        config_path = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
    else:
        raise ValueError(
            "Unsupported platform. Only macOS and Windows are currently supported.",
        )

    # Create config directory if it doesn't exist
    create_file_if_not_exists(config_path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        print(
            "[yellow]Config file was empty or invalid, creating new configuration[/yellow]"
        )
        config = {}
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["universal_mcp"] = {
        "command": get_uvx_path(),
        "args": ["universal_mcp@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Claude configuration installed successfully")


def install_cursor(api_key: str) -> None:
    """Install Cursor"""
    print("[bold blue]Installing Cursor configuration...[/bold blue]")
    # Set up Cursor config path
    config_path = Path.home() / ".cursor/mcp.json"

    # Create config directory if it doesn't exist
    create_file_if_not_exists(config_path)

    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        print(
            "[yellow]Config file was empty or invalid, creating new configuration[/yellow]"
        )
        config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["universal_mcp"] = {
        "command": get_uvx_path(),
        "args": ["universal_mcp@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Cursor configuration installed successfully")


def install_windsurf() -> None:
    """Install Windsurf"""
    print("[yellow]Windsurf installation not yet implemented[/yellow]")
    pass


def install_app(app_name: str) -> None:
    """Install an app"""
    print(f"[bold]Installing {app_name}...[/bold]")
    if app_name == "claude":
        install_claude()
    elif app_name == "cursor":
        install_cursor()
    elif app_name == "windsurf":
        install_windsurf()
    else:
        print(f"[red]Error: App '{app_name}' not supported[/red]")
        raise ValueError(f"App '{app_name}' not supported")
