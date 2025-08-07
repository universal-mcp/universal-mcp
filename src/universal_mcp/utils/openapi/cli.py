import os
import re
from pathlib import Path

import litellm
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.status import Status
from rich.syntax import Syntax

console = Console()
app = typer.Typer(name="codegen")


def _validate_filter_config(filter_config: Path | None) -> None:
    """
    Validate filter configuration file if provided.

    Args:
        filter_config: Path to filter config file or None

    Raises:
        typer.Exit: If validation fails
    """
    if filter_config is None:
        return

    # Handle edge case of empty string or invalid path
    if str(filter_config).strip() == "":
        console.print("[red]Error: Filter configuration path cannot be empty[/red]")
        raise typer.Exit(1)

    if not filter_config.exists():
        console.print(f"[red]Error: Filter configuration file '{filter_config}' does not exist[/red]")
        raise typer.Exit(1)

    if not filter_config.is_file():
        console.print(f"[red]Error: Filter configuration path '{filter_config}' is not a file[/red]")
        raise typer.Exit(1)


def _display_selective_mode_info(filter_config: Path | None, mode_name: str) -> None:
    """Display selective processing mode information if filter config is provided."""
    if filter_config:
        console.print(f"[bold cyan]Selective {mode_name} Mode Enabled[/bold cyan]")
        console.print(f"[cyan]Filter configuration: {filter_config}[/cyan]")
        console.print()


def _model_callback(model: str) -> str:
    """
    Validates the model and checks if the required API key is set.
    This callback is now silent on success.
    """
    if model is not None:
        api_key_env_var = None
        if "claude" in model:
            api_key_env_var = "ANTHROPIC_API_KEY"
        elif "gpt" in model:
            api_key_env_var = "OPENAI_API_KEY"
        elif "gemini" in model:
            api_key_env_var = "GEMINI_API_KEY"
        elif "perplexity" in model:
            api_key_env_var = "PERPLEXITYAI_API_KEY"

        if api_key_env_var and not os.getenv(api_key_env_var):
            error_message = (
                f"Environment variable '{api_key_env_var}' is not set. Please set it to use the '{model}' model."
            )
            raise typer.BadParameter(error_message)
        elif not api_key_env_var:
            pass

        return model


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
    filter_config: Path = typer.Option(
        None,
        "--filter-config",
        "-f",
        help="Path to JSON filter configuration file for selective API client generation.",
    ),
):
    """Generates Python client code from an OpenAPI (Swagger) schema.

    This command automates the creation of an API client class, including
    methods for each API operation defined in the schema. The generated
    code is designed to integrate with the Universal MCP application framework.

    It's recommended that the output filename (if specified via -o) matches
    the API's service name (e.g., 'twitter.py' for a Twitter API client)
    as this convention is used for organizing applications within U-MCP.
    If no output path is provided, the generated code will be printed to the console.

    Selective Generation:
    Use --filter-config to specify which API operations to generate methods for.
    The JSON configuration format is:
    {
        "/users/{user-id}/profile": "get",
        "/users/{user-id}/settings": "all",
        "/orders": ["get", "post"]
    }
    """
    # Import here to avoid circular imports
    from universal_mcp.utils.openapi.api_generator import generate_api_from_schema

    if not schema_path.exists():
        console.print(f"[red]Error: Schema file {schema_path} does not exist[/red]")
        raise typer.Exit(1)

    # Validate filter config and display info
    _validate_filter_config(filter_config)
    _display_selective_mode_info(filter_config, "API Client Generation")

    try:
        app_file_data = generate_api_from_schema(
            schema_path=schema_path,
            output_path=output_path,
            class_name=class_name,
            filter_config_path=str(filter_config) if filter_config else None,
        )
        if isinstance(app_file_data, dict) and "code" in app_file_data:
            console.print("[yellow]No output path specified, printing generated code to console:[/yellow]")
            console.print(app_file_data["code"])
            if "schemas_code" in app_file_data:
                console.print("[yellow]Generated schemas code:[/yellow]")
                console.print(app_file_data["schemas_code"])
        elif isinstance(app_file_data, tuple) and len(app_file_data) == 2:
            app_file, schemas_file = app_file_data
            console.print("[green]API client successfully generated and installed.[/green]")
            console.print(f"[blue]Application file: {app_file}[/blue]")
            console.print(f"[blue]Schemas file: {schemas_file}[/blue]")
        elif isinstance(app_file_data, Path):
            # Legacy support for single path return
            console.print("[green]API client successfully generated and installed.[/green]")
            console.print(f"[blue]Application file: {app_file_data}[/blue]")
        else:
            # Handle the error case from api_generator if validation fails
            if isinstance(app_file_data, dict) and "error" in app_file_data:
                console.print(f"[red]{app_file_data['error']}[/red]")
                raise typer.Exit(1)
            else:
                console.print("[red]Unexpected return value from API generator.[/red]")
                raise typer.Exit(1)

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
def generate_from_llm(
    output_dir: Path = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save 'app.py'. If omitted, you will be prompted.",
        resolve_path=True,
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="The LLM model to use for generation. If omitted, you will be prompted.",
        callback=_model_callback,
    ),
):
    """
    Generates an 'app.py' file from a natural language prompt using an LLM.
    """
    from universal_mcp.utils.prompts import APP_GENERATOR_SYSTEM_PROMPT

    console.print(
        Panel(
            "🚀 [bold]Welcome to the Universal App Generator[/bold] 🚀",
            title="[bold blue]MCP[/bold blue]",
            border_style="blue",
            expand=False,
        )
    )

    if output_dir is None:
        dir_str = Prompt.ask("[cyan]Enter the directory to save 'app.py'[/cyan]", default=str(Path.cwd()))
        output_dir = Path(dir_str).resolve()

    if model is None:
        model_str = Prompt.ask("[cyan]Enter the LLM model to use[/cyan]", default="perplexity/sonar")
        model = _model_callback(model_str)

    prompt_guidance = (
        "You can provide the application description (the prompt) in two ways:\n\n"
        "1. [bold green]From a Text File (Recommended)[/bold green]\n"
        "   - Ideal for longer, detailed, or multi-line prompts.\n"
        "   - Allows you to easily copy, paste, and edit your prompt in a text editor.\n\n"
        "2. [bold yellow]Directly in the Terminal[/bold yellow]\n"
        "   - Suitable for short, simple, single-line test prompts.\n"
        "   - Not recommended for complex applications as multi-line input is difficult."
    )
    console.print(
        Panel(prompt_guidance, title="[bold]How to Provide Your Prompt[/bold]", border_style="blue", padding=(1, 2))
    )

    use_file = Confirm.ask("\n[bold]Would you like to provide the prompt from a text file?[/bold]", default=True)

    prompt = ""
    if use_file:
        prompt_file = Prompt.ask("[cyan]Please enter the path to your prompt .txt file[/cyan]")
        try:
            prompt_path = Path(prompt_file).resolve()
            if not prompt_path.exists() or not prompt_path.is_file():
                console.print(f"[bold red]❌ File not found at: {prompt_path}[/bold red]")
                raise typer.Exit(code=1) from None
            prompt = prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[bold red]❌ Failed to read prompt file: {e}[/bold red]")
            raise typer.Exit(code=1) from e
    else:
        prompt = Prompt.ask("[cyan]Please describe the application you want to build[/cyan]")
        if not prompt.strip():
            console.print("[bold red]❌ Prompt cannot be empty. Aborting.[/bold red]")
            raise typer.Exit(code=1)

    PROMPT_DISPLAY_LIMIT = 400
    prompt_for_display = prompt

    if len(prompt) > PROMPT_DISPLAY_LIMIT:
        total_lines = len(prompt.splitlines())
        total_chars = len(prompt)

        prompt_for_display = (
            f"{prompt[:PROMPT_DISPLAY_LIMIT]}...\n\n"
            f"[italic grey50](Prompt truncated for display. "
            f"Full prompt is {total_lines} lines, {total_chars} characters)"
            f"[/italic]"
        )

    config_summary = (
        f"[bold blue]📝 Using Prompt:[/bold blue]\n[grey70]{prompt_for_display}[/grey70]\n\n"
        f"[bold blue]🤖 Using Model:[/bold blue] [cyan]{model}[/cyan]\n"
        f"[bold blue]💾 Output Directory:[/bold blue] [cyan]{output_dir}[/cyan]"
    )
    console.print(
        Panel(config_summary, title="[bold green]Configuration[/bold green]", border_style="green", padding=(1, 2))
    )

    try:
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f"[red]❌ Failed to create output directory '{output_dir}': {e}[/red]")
        raise typer.Exit(code=1) from e

    output_file_path = output_dir / "app.py"
    console.print(f"\n[green]Will save generated file to:[/green] [cyan]{output_file_path}[/cyan]\n")

    messages = [
        {"role": "system", "content": APP_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    response = None
    with Status("[bold green]Generating app code... (this may take a moment)[/bold green]", console=console) as status:
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0.1,
                timeout=120,
            )
        except Exception as e:
            status.update("[bold red]❌ An error occurred during LLM API call.[/bold red]")
            console.print(Panel(f"Error: {e}", title="[bold red]API Error[/bold red]", border_style="red"))
            raise typer.Exit(code=1) from e

    if not response or not response.choices:
        console.print("[bold red]❌ Failed to get a valid response from the LLM.[/bold red]")
        raise typer.Exit(code=1)

    generated_content = response.choices[0].message.content
    code_match = re.search(r"```python\n(.*?)\n```", generated_content, re.DOTALL)
    if code_match:
        final_code = code_match.group(1).strip()
    else:
        console.print(
            "[yellow]Warning: LLM response did not contain a markdown code block. Using the raw response.[/yellow]"
        )
        final_code = generated_content.strip()

    if not final_code:
        console.print("[bold red]❌ The LLM returned an empty code block. Aborting.[/bold red]")
        raise typer.Exit(code=1)

    CODE_DISPLAY_LINE_LIMIT = 200
    code_for_display = final_code
    is_truncated = False

    code_lines = final_code.splitlines()
    num_lines = len(code_lines)

    if num_lines > CODE_DISPLAY_LINE_LIMIT:
        is_truncated = True
        code_for_display = "\n".join(code_lines[:CODE_DISPLAY_LINE_LIMIT])

    console.print(
        Panel(
            Syntax(code_for_display, "python", theme="monokai", line_numbers=True),
            title="[bold magenta]Generated Code Preview: app.py[/bold magenta]",
            border_style="magenta",
            subtitle=f"Total lines: {num_lines}",
        )
    )

    if is_truncated:
        console.print(
            f"[italic yellow]... Output truncated. Showing the first {CODE_DISPLAY_LINE_LIMIT} of {num_lines} lines. "
            f"The full code has been saved to the {output_file_path}.[/italic yellow]\n"
        )

    try:
        output_file_path.write_text(final_code, encoding="utf-8")
        console.print(
            Panel(
                f"✅ [bold green]Success![/bold green]\nApplication code saved to [cyan]{output_file_path}[/cyan]",
                title="[bold green]Complete[/bold green]",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                f"Failed to write the generated code to file: {e}",
                title="[bold red]File Error[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from e


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
        help="App name (letters, numbers and hyphens only , underscores not allowed)",
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
    from typer import confirm, prompt

    from .cli import generate, generate_from_llm

    NAME_PATTERN = r"^[a-zA-Z0-9-]+$"

    def validate_app_name(value: str, field_name: str) -> None:
        if not re.match(NAME_PATTERN, value):
            console.print(f"[red]❌ Invalid {field_name}; only letters, numbers, hyphens allowed[/red]")
            raise typer.Exit(code=1)

    if not app_name:
        app_name = typer.prompt(
            "Enter the app name",
            default="app_name",
            prompt_suffix=" (e.g., reddit, youtube): ",
        ).strip()

    validate_app_name(app_name, "app name")

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
            console.print(f"[green]✅ Created output directory at '{output_dir}'[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to create output directory '{output_dir}': {e}[/red]")
            raise typer.Exit(code=1) from e
    elif not output_dir.is_dir():
        console.print(f"[red]❌ Output path '{output_dir}' exists but is not a directory.[/red]")
        raise typer.Exit(code=1)

    if not integration_type:
        integration_type = typer.prompt(
            "Choose the integration type",
            default="agentr",
            prompt_suffix=" (api_key, oauth, agentr, none): ",
        ).lower()
    if integration_type not in ("api_key", "oauth", "agentr", "none"):
        console.print("[red]❌ Integration type must be one of: api_key, oauth, agentr, none[/red]")
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

    generate_client = confirm("Do you want to also generate api_client ?")

    if not generate_client:
        console.print("[yellow]Skipping API client generation.[/yellow]")
        return

    has_openapi_spec = confirm("Do you have openapi spec for the application just created ?")

    app_dir = app_name.lower().replace("-", "_")
    target_app_dir = project_dir / "src" / f"universal_mcp_{app_dir}"

    try:
        target_app_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f"[red]❌ Failed to create target app directory '{target_app_dir}': {e}[/red]")
        raise typer.Exit(code=1) from e

    if has_openapi_spec:
        schema_path_str = prompt("Enter the path to the OpenAPI schema file (JSON or YAML)")
        schema_path = Path(schema_path_str)

        if not schema_path.exists():
            console.print(f"[red]Error: Schema file {schema_path} does not exist[/red]")
            raise typer.Exit(1)

        class_name = "".join([part.title() for part in app_name.split("-")]) + "App"

        try:
            console.print("\n[bold blue]Calling 'codegen generate' with provided schema...[/bold blue]")
            generate(schema_path=schema_path, output_path=target_app_dir, class_name=class_name)

        except typer.Exit as e:
            console.print(f"[red]API client generation from schema failed. Exit code: {e.exit_code}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]An unexpected error occurred during API client generation from schema: {e}[/red]")
            raise typer.Exit(code=1) from e

    else:
        try:
            llm_model = prompt("Enter the LLM model to use", default="perplexity/sonar")
            try:
                _model_callback(llm_model)
            except typer.BadParameter as e:
                console.print(f"[red]Validation Error: {e}[/red]")
                raise typer.Exit(code=1) from e

            llm_prompt_text = prompt("Describe the application and its tools (natural language)")

            console.print("\n[bold blue]Calling 'codegen generate-from-llm'...[/bold blue]")
            generate_from_llm(output_dir=target_app_dir, model=llm_model, prompt=llm_prompt_text)

        except typer.Exit as e:
            console.print(f"[red]API client generation from LLM failed. Exit code: {e.exit_code}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]An unexpected error occurred during API client generation from LLM: {e}[/red]")
            raise typer.Exit(code=1) from e


@app.command()
def preprocess(
    schema_path: Path = typer.Option(
        None, "--schema", "-s", help="Path to the input OpenAPI schema file (JSON or YAML)."
    ),
    output_path: Path = typer.Option(
        None, "--output", "-o", help="Path to save the processed (enhanced) OpenAPI schema file."
    ),
    filter_config: Path = typer.Option(
        None, "--filter-config", "-f", help="Path to JSON filter configuration file for selective processing."
    ),
):
    """Enhances an OpenAPI schema's descriptions using an LLM.

    This command takes an existing OpenAPI schema and uses a Large Language
    Model (LLM) to automatically generate or improve the descriptions for
    API paths, operations, parameters, and schemas. This is particularly
    helpful for schemas that are auto-generated or lack comprehensive
    human-written documentation, making the schema more understandable and
    usable for client generation or manual review.

    Use --filter-config to process only specific paths and methods defined
    in a JSON configuration file. Format:
    {
      "/users/{user-id}/profile": "get",
      "/users/{user-id}/settings": "all",
      "/orders/{order-id}": ["get", "put", "delete"]
    }
    """
    from universal_mcp.utils.openapi.preprocessor import run_preprocessing

    # Validate filter config and display info
    _validate_filter_config(filter_config)
    _display_selective_mode_info(filter_config, "Processing")

    run_preprocessing(
        schema_path=schema_path,
        output_path=output_path,
        filter_config_path=str(filter_config) if filter_config else None,
    )


@app.command()
def split_api(
    input_app_file: Path = typer.Argument(..., help="Path to the generated app.py file to split"),
    output_dir: Path = typer.Option(..., "--output-dir", "-o", help="Directory to save the split files"),
    package_name: str = typer.Option(
        None, "--package-name", "-p", help="Package name for absolute imports (e.g., 'hubspot')"
    ),
):
    """Splits a single generated API client file into multiple files based on path groups."""
    from universal_mcp.utils.openapi.api_splitter import split_generated_app_file

    if not input_app_file.exists() or not input_app_file.is_file():
        console.print(f"[red]Error: Input file {input_app_file} does not exist or is not a file.[/red]")
        raise typer.Exit(1)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]Created output directory: {output_dir}[/green]")
    elif not output_dir.is_dir():
        console.print(f"[red]Error: Output path {output_dir} is not a directory.[/red]")
        raise typer.Exit(1)

    try:
        split_generated_app_file(input_app_file, output_dir, package_name)
        console.print(f"[green]Successfully split {input_app_file} into {output_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Error splitting API client: {e}[/red]")

        raise typer.Exit(1) from e


@app.command()
def generate_tests(
    app_name: str = typer.Argument(..., help="Name of the app (e.g., 'outlook')"),
    class_name: str = typer.Argument(..., help="Name of the app class (e.g., 'OutlookApp')"),
    output_dir: str = typer.Option("tests", "--output", "-o", help="Output directory for the test file"),
):
    """Generate automated test cases for an app"""
    from universal_mcp.utils.openapi.test_generator import generate_test_cases

    console.print(f"[blue]Generating test cases for {app_name} ({class_name})...[/blue]")

    try:
        response = generate_test_cases(app_name, class_name, output_dir)
        console.print(f"[green]✅ Successfully generated {len(response.test_cases)} test cases![/green]")
    except ImportError as e:
        console.print(f"[red]Import Error: {e}[/red]")
        console.print(f"[yellow]Make sure the module 'universal_mcp_{app_name}' is installed and available.[/yellow]")
        raise typer.Exit(1) from e
    except AttributeError as e:
        console.print(f"[red]Attribute Error: {e}[/red]")
        console.print(f"[yellow]Make sure the class '{class_name}' exists in 'universal_mcp_{app_name}.app'.[/yellow]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error generating test cases: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def postprocess(
    input_file: Path = typer.Argument(..., help="Path to the input API client Python file"),
    output_file: Path = typer.Argument(..., help="Path to save the postprocessed API client Python file"),
):
    """Postprocess API client: add hint tags to docstrings based on HTTP method."""
    from universal_mcp.utils.openapi.postprocessor import add_hint_tags_to_docstrings

    if not input_file.exists() or not input_file.is_file():
        console.print(f"[red]Error: Input file {input_file} does not exist or is not a file.[/red]")
        raise typer.Exit(1)
    try:
        add_hint_tags_to_docstrings(str(input_file), str(output_file))
        console.print(f"[green]Successfully postprocessed {input_file} and saved to {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]Error during postprocessing: {e}[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
