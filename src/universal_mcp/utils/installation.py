import json
import sys
from pathlib import Path


def create_file_if_not_exists(path: Path) -> None:
    """Create a file if it doesn't exist"""
    if not path.exists():
        with open(path, "w") as f:
            json.dump({}, f)


def get_supported_apps() -> list[str]:
    """Get list of supported apps"""
    return ["claude", "cursor", "windsurf"]


def install_claude(api_key: str) -> None:
    """Install Claude"""
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
        config = {}
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["universal_mcp"] = {
        "command": "uvx",
        "args": ["universal_mcp@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def install_cursor(api_key: str) -> None:
    """Install Cursor"""
    # Set up Cursor config path
    config_path = Path.home() / ".cursor/mcp.json"

    # Create config directory if it doesn't exist
    create_file_if_not_exists(config_path)

    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["universal_mcp"] = {
        "command": "uvx",
        "args": ["universal_mcp@latest", "run"],
        "env": {"AGENTR_API_KEY": api_key},
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def install_windsurf() -> None:
    """Install Windsurf"""
    pass


def install_app(app_name: str) -> None:
    """Install an app"""
    if app_name == "claude":
        install_claude()
    elif app_name == "cursor":
        install_cursor()
    elif app_name == "windsurf":
        install_windsurf()
    else:
        raise ValueError(f"App '{app_name}' not supported")
