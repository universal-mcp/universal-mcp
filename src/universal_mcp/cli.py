import re
from pathlib import Path
import yaml,json,sys,os

import typer
from rich.console import Console
from rich.panel import Panel

from universal_mcp.utils.installation import (
    get_supported_apps,
    install_claude,
    install_cursor,
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
        if app_name == "claude":
            console.print(f"[blue]Installing mcp server for: {app_name}[/blue]")
            install_claude(api_key)
            console.print("[green]App installed successfully[/green]")
        elif app_name == "cursor":
            console.print(f"[blue]Installing mcp server for: {app_name}[/blue]")
            install_cursor(api_key)
            console.print("[green]App installed successfully[/green]")
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
            console.print(
                f"[green]✅ Created output directory at '{output_dir}'[/green]"
            )
        except Exception as e:
            console.print(
                f"[red]❌ Failed to create output directory '{output_dir}': {e}[/red]"
            )
            raise typer.Exit(code=1) from e
    elif not output_dir.is_dir():
        console.print(
            f"[red]❌ Output path '{output_dir}' exists but is not a directory.[/red]"
        )
        raise typer.Exit(code=1)

    # Integration type
    if not integration_type:
        integration_type = typer.prompt(
            "Choose the integration type",
            default="agentr",
            prompt_suffix=" (api_key, oauth, agentr, none): ",
        ).lower()
    if integration_type not in ("api_key", "oauth", "agentr", "none"):
        console.print(
            "[red]❌ Integration type must be one of: api_key, oauth, agentr, none[/red]"
        )
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
    schema_path: Path | None = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to the OpenAPI schema file (JSON or YAML). Prompts if not provided.",
    ),
    output_path: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for the processed schema. Defaults to input file with _processed extension.",
    ),
    model: str = typer.Option(
        "perplexity/sonar",
        "--model",
        "-m",
        help="Model to use for generating descriptions/summaries.",
    ),
):
    """
    Preprocess an OpenAPI schema file to add missing summaries and descriptions using an LLM.
    First scans the schema and reports status, then prompts for action.
    """
    from universal_mcp.utils.openapi.preprocessor import (
        read_schema_file,
        write_schema_file,
        scan_schema_for_status,
        report_scan_results,
        preprocess_schema_with_llm,
        set_logging_level # Import the logging level setter if not already used
    )

    # Ensure logging level is set for this command's output
    # (You might have a global logger setup in cli.py, adjust if needed)
    set_logging_level("INFO")
    console.print("[bold blue]--- Starting OpenAPI Schema Preprocessor ---[/bold blue]")

    if schema_path is None:
        path_str = typer.prompt(
            "Please enter the path to the OpenAPI schema file (JSON or YAML)",
            prompt_suffix=": ",
        ).strip()
        if not path_str:
            console.print("[red]Error: Schema path is required.[/red]")
            raise typer.Exit(1)
        schema_path = Path(path_str)

    # --- Step 1: Read Schema ---
    try:
        schema_data = read_schema_file(str(schema_path))
    except (FileNotFoundError, yaml.YAMLError, json.JSONDecodeError, OSError) as e:
         # read_schema_file logs critical errors, just exit here
         raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]An unexpected error occurred while reading schema: {e}[/red]")
        raise typer.Exit(1) from e


    # --- Step 2: Scan and Report Status ---
    try:
        scan_report = scan_schema_for_status(schema_data)
        report_scan_results(scan_report)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during schema scanning: {e}[/red]")
        raise typer.Exit(1) from e

    # --- Step 3: Check for Critical Errors and Prompt User ---
    if scan_report.get("critical_errors"):
         console.print("[bold red]Cannot proceed with generation due to critical errors. Please fix the schema file manually.[/bold red]")
         raise typer.Exit(1)

    # Check if there's anything missing or fallback to justify prompting for generation
    total_missing_or_fallback = (
        scan_report["info_description"]["missing"] + scan_report["info_description"]["fallback"] +
        scan_report["operation_summary"]["missing"] + scan_report["operation_summary"]["fallback"] +
        scan_report["parameter_description"]["missing"] + scan_report["parameter_description"]["fallback"]
    )

    # Also consider parameters with missing name/in, as we can't generate for them
    # Even if other things are missing, report these separately as ungeneratable
    ungeneratable_params = len(scan_report.get("parameters_missing_name", [])) + len(scan_report.get("parameters_missing_in", []))

    if total_missing_or_fallback == 0:
        console.print("[bold green]No missing or fallback descriptions/summaries found that can be automatically generated.[/bold green]")
        if ungeneratable_params > 0:
             console.print(f"[yellow]Note: There are {ungeneratable_params} parameters with missing 'name' or 'in' fields that require manual fixing.[/yellow]")
        console.print("[bold blue]Preprocessor finished.[/bold blue]")
        raise typer.Exit(0) # Exit successfully if nothing needs generation


    # Prompt for action
    while True:
        console.print("\n[bold blue]Choose an action:[/bold blue]")
        console.print("  [1] Generate [bold]only missing[/bold] descriptions/summaries [green](default)[/green]")
        console.print("  [2] Generate/Enhance [bold]all[/bold] descriptions/summaries")
        console.print("  [3] [bold red]Quit[/bold red] (exit without changes)")

        choice = typer.prompt("Enter choice", default="1", show_default=False, type=str).strip()

        if choice == "3":
            console.print("[yellow]Exiting without making changes.[/yellow]")
            raise typer.Exit(0)
        elif choice == "1":
            enhance_all = False
            break
        elif choice == "2":
            enhance_all = True
            break
        else:
            console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")

    # --- Step 4: Perform LLM Generation based on Choice ---
    try:
        preprocess_schema_with_llm(schema_data, model, enhance_all)
        console.print("[green]LLM generation complete.[/green]")
    except Exception as e:
        console.print(f"[red]Error during LLM generation: {e}[/red]")
        # Log traceback for debugging
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise typer.Exit(1) from e

    # --- Step 5: Determine Output Path and Write ---
    if output_path is None:
        base, ext = os.path.splitext(schema_path)
        output_path = Path(f"{base}_processed{ext}")
        console.print(f"[blue]No output path specified. Defaulting to: {output_path}[/blue]")
    else:
         console.print(f"[blue]Saving processed schema to: {output_path}[/blue]")

    try:
        write_schema_file(schema_data, str(output_path))
    except (OSError, ValueError) as e:
         # write_schema_file logs critical errors, just exit here
         raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]An unexpected error occurred while writing the schema: {e}[/red]")
        raise typer.Exit(1) from e


    console.print("\n[bold green]--- Schema Processing and Saving Complete ---[/bold green]")
    console.print(f"Processed schema saved to: [blue]{output_path}[/blue]")
    console.print("[bold blue]Preprocessor finished successfully.[/bold blue]")

if __name__ == "__main__":
    app()
