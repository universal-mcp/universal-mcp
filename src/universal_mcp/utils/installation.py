import json
import shutil
import sys
from pathlib import Path

from loguru import logger
from rich import print


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
    return ["claude", "cursor", "cline", "continue", "goose", "windsurf", "zed"]


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
        "args": ["universal_mcp[all]@latest", "run"],
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
        "args": ["universal_mcp[all]@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Cursor configuration installed successfully")


def install_cline(api_key: str) -> None:
    """Install Cline"""
    print("[bold blue]Installing Cline configuration...[/bold blue]")
    # Set up Cline config path
    config_path = Path.home() / ".config/cline/mcp.json"

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
        "args": ["universal_mcp[all]@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Cline configuration installed successfully")


def install_continue(api_key: str) -> None:
    """Install Continue"""
    print("[bold blue]Installing Continue configuration...[/bold blue]")

    # Determine platform-specific config path
    if sys.platform == "darwin":  # macOS
        config_path = Path.home() / "Library/Application Support/Continue/mcp.json"
    elif sys.platform == "win32":  # Windows
        config_path = Path.home() / "AppData/Roaming/Continue/mcp.json"
    else:  # Linux and others
        config_path = Path.home() / ".config/continue/mcp.json"

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
        "args": ["universal_mcp[all]@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Continue configuration installed successfully")


def install_goose(api_key: str) -> None:
    """Install Goose"""
    print("[bold blue]Installing Goose configuration...[/bold blue]")

    # Determine platform-specific config path
    if sys.platform == "darwin":  # macOS
        config_path = Path.home() / "Library/Application Support/Goose/mcp-config.json"
    elif sys.platform == "win32":  # Windows
        config_path = Path.home() / "AppData/Roaming/Goose/mcp-config.json"
    else:  # Linux and others
        config_path = Path.home() / ".config/goose/mcp-config.json"

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
        "args": ["universal_mcp[all]@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Goose configuration installed successfully")


def install_windsurf(api_key: str) -> None:
    """Install Windsurf"""
    print("[bold blue]Installing Windsurf configuration...[/bold blue]")

    # Determine platform-specific config path
    if sys.platform == "darwin":  # macOS
        config_path = Path.home() / "Library/Application Support/Windsurf/mcp.json"
    elif sys.platform == "win32":  # Windows
        config_path = Path.home() / "AppData/Roaming/Windsurf/mcp.json"
    else:  # Linux and others
        config_path = Path.home() / ".config/windsurf/mcp.json"

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
        "args": ["universal_mcp[all]@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Windsurf configuration installed successfully")


def install_zed(api_key: str) -> None:
    """Install Zed"""
    print("[bold blue]Installing Zed configuration...[/bold blue]")

    # Set up Zed config path
    config_dir = Path.home() / ".config/zed"
    config_path = config_dir / "mcp_servers.json"

    # Create config directory if it doesn't exist
    create_file_if_not_exists(config_path)

    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        print(
            "[yellow]Config file was empty or invalid, creating new configuration[/yellow]"
        )
        config = {}

    if not isinstance(config, list):
        config = []

    # Check if universal_mcp is already in the config
    existing_config = False
    for server in config:
        if server.get("name") == "universal_mcp":
            existing_config = True
            server.update(
                {
                    "command": get_uvx_path(),
                    "args": ["universal_mcp[all]@latest", "run"],
                    "env": {"AGENTR_API_KEY": api_key},
                }
            )
            break

    if not existing_config:
        config.append(
            {
                "name": "universal_mcp",
                "command": get_uvx_path(),
                "args": ["universal_mcp[all]@latest", "run"],
                "env": {"AGENTR_API_KEY": api_key},
            }
        )

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("[green]✓[/green] Zed configuration installed successfully")


def install_app(app_name: str, api_key: str) -> None:
    """Install an app"""
    print(f"[bold]Installing {app_name}...[/bold]")
    if app_name == "claude":
        install_claude(api_key)
    elif app_name == "cursor":
        install_cursor(api_key)
    elif app_name == "cline":
        install_cline(api_key)
    elif app_name == "continue":
        install_continue(api_key)
    elif app_name == "goose":
        install_goose(api_key)
    elif app_name == "windsurf":
        install_windsurf(api_key)
    elif app_name == "zed":
        install_zed(api_key)
    else:
        print(f"[red]Error: App '{app_name}' not supported[/red]")
        raise ValueError(f"App '{app_name}' not supported")
