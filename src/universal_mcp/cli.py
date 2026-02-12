"""Universal MCP CLI - Manage MCP applications from the command line."""

import asyncio

import typer
from rich import print as rprint

app = typer.Typer(
    name="unsw",
    help="Universal MCP - Find, install, authorize, and use MCP applications.",
    no_args_is_help=True,
)

# -- Subcommand groups --
app_cmd = typer.Typer(help="Manage MCP applications", no_args_is_help=True)
app.add_typer(app_cmd, name="app")

server_cmd = typer.Typer(help="MCP server management", no_args_is_help=True)
app.add_typer(server_cmd, name="server")

skills_app = typer.Typer(help="Manage Claude Code skills", no_args_is_help=True)
app.add_typer(skills_app, name="skills")

cron_app = typer.Typer(help="Manage scheduled AI tasks (crontabs)", no_args_is_help=True)
app.add_typer(cron_app, name="cron")


def _get_sdk():
    from universal_mcp.sdk import UniversalMCP

    return UniversalMCP()


async def _get_sdk_async():
    """Get SDK instance with async apps loaded."""
    from universal_mcp.sdk import UniversalMCP

    sdk = UniversalMCP()
    await sdk.load_manifest_async()
    return sdk


def _get_skills_registry():
    from universal_mcp.skills.registry import SkillsRegistry

    return SkillsRegistry()


def _get_crontab_registry():
    from universal_mcp.crontabs.registry import CrontabRegistry
    return CrontabRegistry()


# =============================================================================
# APP COMMANDS
# =============================================================================

@app_cmd.command("install")
def app_install(
    name_or_url: str = typer.Argument(help="App slug (e.g., 'github') or MCP server URL"),
    transport: str | None = typer.Option(None, "--transport", "-t", help="Transport type: http, sse, streamable-http (enables URL mode)"),
    type: str = typer.Option("api_key", "--type", help="Integration type: api_key or oauth2"),
    name: str | None = typer.Option(None, "--name", "-n", help="Override app name (for URL installs)"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="API key for auth"),
    header: list[str] | None = typer.Option(None, "--header", "-H", help="Headers as KEY=VALUE (repeatable)"),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tags to filter tools"),
):
    """Install an MCP application (local package or remote URL)."""
    sdk = _get_sdk()
    tag_list = tags.split(",") if tags else None

    # Determine if this is a URL install (has transport flag or looks like a URL)
    is_url = transport is not None or name_or_url.startswith(("http://", "https://", "mcp."))

    if is_url:
        # URL-based install
        headers: dict[str, str] = {}
        if not api_key and not header:
            rprint("[dim]Checking if authentication is required...[/dim]")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if header:
            for h in header:
                if "=" not in h:
                    rprint(f"[red]Invalid header format '{h}', expected KEY=VALUE[/red]")
                    raise typer.Exit(1) from None
                key, value = h.split("=", 1)
                headers[key.strip()] = value.strip()

        try:
            from universal_mcp.applications.mcp_app import _derive_app_name, normalize_mcp_url
            asyncio.run(sdk.add_from_url(name_or_url, name=name, headers=headers or None, tags=tag_list))
            app_name = name or _derive_app_name(normalize_mcp_url(name_or_url))
            tools = sdk.list_tools(app=app_name)
            rprint(f"[green]Installed remote MCP app from {name_or_url}[/green]")
            rprint(f"[dim]{len(tools)} tools registered[/dim]")
        except Exception as e:
            rprint(f"[red]Failed to install MCP app from '{name_or_url}': {e}[/red]")
            raise typer.Exit(1) from None
    else:
        # Package-based install
        try:
            sdk.add(name_or_url, integration_type=type, tags=tag_list)
            rprint(f"[green]Installed '{name_or_url}' with {type} authentication[/green]")
            tools = sdk.list_tools(app=name_or_url)
            rprint(f"[dim]{len(tools)} tools registered[/dim]")
        except Exception as e:
            rprint(f"[red]Failed to install '{name_or_url}': {e}[/red]")
            raise typer.Exit(1) from None


@app_cmd.command("remove")
def app_remove(
    slug: str = typer.Argument(help="Application slug to remove"),
):
    """Remove an MCP application."""
    async def _remove_app():
        sdk = await _get_sdk_async()
        if await sdk.remove(slug):
            rprint(f"[green]Removed '{slug}'[/green]")
        else:
            rprint(f"[yellow]App '{slug}' not found[/yellow]")

    asyncio.run(_remove_app())


@app_cmd.command("authorize")
def app_authorize(
    slug: str = typer.Argument(help="Application slug to authorize"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="API key"),
):
    """Authorize an MCP application with credentials."""
    sdk = _get_sdk()

    if not api_key:
        # Interactive prompt
        api_key = typer.prompt(f"Enter API key for '{slug}'", hide_input=True)

    result = asyncio.run(sdk.authorize(slug, api_key=api_key))
    rprint(f"[green]{result}[/green]")


@app_cmd.command("list")
def app_list():
    """List installed MCP applications."""
    sdk = _get_sdk()
    apps = sdk.list_apps()
    if not apps:
        rprint("[dim]No applications installed. Use 'unsw app install <slug>' to get started.[/dim]")
        return
    for name in apps:
        rprint(f"  {name}")


@app_cmd.command("list-tools")
def app_list_tools(
    app_name: str | None = typer.Option(None, "--app", "-a", help="Filter by app slug"),
):
    """List available tools."""
    async def _list_tools():
        sdk = await _get_sdk_async()
        tools = sdk.list_tools(app=app_name)
        if not tools:
            rprint("[dim]No tools available.[/dim]")
            return
        for tool in tools:
            name = tool["name"]
            desc = tool["description"]
            # Truncate long descriptions
            if len(desc) > 80:
                desc = desc[:77] + "..."
            rprint(f"  [bold]{name}[/bold]  {desc}")

    asyncio.run(_list_tools())


@app_cmd.command("search-tools")
def app_search_tools(
    query: str = typer.Argument(help="Search query"),
):
    """Search for tools by name, description, or tags."""
    async def _search_tools():
        sdk = await _get_sdk_async()
        tools = sdk.search_tools(query)
        if not tools:
            rprint(f"[dim]No tools matching '{query}'[/dim]")
            return
        for tool in tools:
            name = tool["name"]
            desc = tool["description"]
            if len(desc) > 80:
                desc = desc[:77] + "..."
            rprint(f"  [bold]{name}[/bold]  {desc}")

    asyncio.run(_search_tools())


# =============================================================================
# SERVER COMMANDS
# =============================================================================

@server_cmd.command("start")
def server_start(
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport: stdio, sse, streamable-http"),
    port: int = typer.Option(8005, "--port", "-p", help="Port for HTTP transports"),
):
    """Start the MCP server."""
    async def _start_server():
        sdk = await _get_sdk_async()
        apps = sdk.list_apps()
        if not apps:
            rprint("[yellow]No apps installed. Use 'unsw app install <slug>' first.[/yellow]")
            raise typer.Exit(1)

        rprint(f"[green]Starting MCP server with {len(apps)} app(s): {', '.join(apps)}[/green]")
        await sdk.run(transport=transport, port=port)

    asyncio.run(_start_server())


# =============================================================================
# SKILLS COMMANDS
# =============================================================================

@skills_app.command("list")
def skills_list(
    scope: str | None = typer.Option(None, "--scope", "-s", help="Filter by scope: global or project"),
):
    """List installed Claude Code skills."""
    registry = _get_skills_registry()
    skills = registry.list_skills(scope=scope)

    if not skills:
        scope_msg = f" in scope '{scope}'" if scope else ""
        rprint(f"[dim]No skills installed{scope_msg}.[/dim]")
        rprint("[dim]Use 'unsw skills install <source>' to get started.[/dim]")
        return

    for skill in skills:
        desc = skill.description
        if len(desc) > 80:
            desc = desc[:77] + "..."
        source = skill.source or "(manual)"
        rprint(f"  [bold]{skill.name}[/bold] ({skill.scope}, {source})")
        rprint(f"    {desc}")


@skills_app.command("search")
def skills_search(
    query: str = typer.Argument(help="Search query"),
):
    """Search installed skills by name or description."""
    registry = _get_skills_registry()
    skills = registry.search_skills(query)

    if not skills:
        rprint(f"[dim]No skills matching '{query}'[/dim]")
        return

    for skill in skills:
        desc = skill.description
        if len(desc) > 80:
            desc = desc[:77] + "..."
        rprint(f"  [bold]{skill.name}[/bold] ({skill.scope})")
        rprint(f"    {desc}")


@skills_app.command("install")
def skills_install(
    source: str = typer.Argument(help="Skill source: local path or GitHub URL"),
    scope: str = typer.Option("global", "--scope", "-s", help="Installation scope: global or project"),
):
    """Install a Claude Code skill from a local path or GitHub URL."""
    if scope not in ("global", "project"):
        rprint("[red]Scope must be 'global' or 'project'[/red]")
        raise typer.Exit(1)

    registry = _get_skills_registry()
    try:
        metadata = registry.install_skill(source, scope=scope)
        rprint(f"[green]Installed skill '{metadata.name}' (scope={scope})[/green]")
        rprint(f"[dim]Source: {source}[/dim]")
    except Exception as e:
        rprint(f"[red]Failed to install skill from '{source}': {e}[/red]")
        raise typer.Exit(1) from None


@skills_app.command("remove")
def skills_remove(
    name: str = typer.Argument(help="Skill name to remove"),
):
    """Remove an installed skill."""
    registry = _get_skills_registry()
    if registry.remove_skill(name):
        rprint(f"[green]Removed skill '{name}'[/green]")
    else:
        rprint(f"[yellow]Skill '{name}' not found[/yellow]")
        raise typer.Exit(1)


@skills_app.command("scan")
def skills_scan():
    """Scan skill directories and update the registry."""
    registry = _get_skills_registry()
    registry.scan_skills()
    skills = registry.list_skills()
    rprint("[green]Scanned skill directories[/green]")
    rprint(f"[dim]Found {len(skills)} skill(s)[/dim]")


@skills_app.command("info")
def skills_info(
    name: str = typer.Argument(help="Skill name"),
):
    """Show detailed information about a skill."""
    registry = _get_skills_registry()
    skill = registry.get_skill(name)

    if not skill:
        rprint(f"[red]Skill '{name}' not found[/red]")
        raise typer.Exit(1)

    rprint(f"[bold]{skill.name}[/bold]")
    rprint(f"  Description:  {skill.description}")
    rprint(f"  Version:      {skill.version}")
    rprint(f"  Scope:        {skill.scope}")
    rprint(f"  Source:       {skill.source or '(manual)'}")
    rprint(f"  Installed:    {skill.installed_at}")
    rprint(f"  Path:         {skill.path}")
    rprint("")

    # Display SKILL.md content
    skill_md = skill.path / "SKILL.md"
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding="utf-8")
            # Skip the frontmatter (between --- markers)
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            rprint("[bold]SKILL.md content:[/bold]")
            rprint(content)
        except Exception as e:
            rprint(f"[yellow]Could not read SKILL.md: {e}[/yellow]")
    else:
        rprint("[yellow]SKILL.md not found[/yellow]")


# =============================================================================
# CRON COMMANDS
# =============================================================================

@cron_app.command("list")
def cron_list(
    all_jobs: bool = typer.Option(False, "--all", "-a", help="Show disabled jobs too"),
):
    """List scheduled cron jobs."""
    registry = _get_crontab_registry()
    jobs = registry.list_jobs(enabled_only=not all_jobs)
    if not jobs:
        rprint("[dim]No cron jobs configured. Use 'unsw cron add' to create one.[/dim]")
        return
    for job in jobs:
        status = "[green]enabled[/green]" if job.enabled else "[red]disabled[/red]"
        desc = f"  [dim]{job.description}[/dim]" if job.description else ""
        rprint(f"  [bold]{job.name}[/bold]  {job.schedule}  {status}{desc}")


@cron_app.command("add")
def cron_add(
    name: str = typer.Argument(help="Unique job name"),
    schedule: str = typer.Option(..., "--schedule", "-s", help="Cron expression (e.g., '*/5 * * * *')"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="AI prompt to execute"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model override (sonnet, opus)"),
    description: str = typer.Option("", "--description", "-d", help="Job description"),
    timezone: str = typer.Option("UTC", "--timezone", help="Timezone for schedule"),
):
    """Add a new scheduled AI task."""
    from universal_mcp.crontabs.models import CrontabJob

    registry = _get_crontab_registry()
    try:
        job = CrontabJob(
            name=name,
            schedule=schedule,
            prompt=prompt,
            model=model,
            description=description,
            timezone=timezone,
        )
        registry.add_job(job)
        rprint(f"[green]Added cron job '{name}': {schedule}[/green]")
        rprint(f"[dim]Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}[/dim]")
    except Exception as e:
        rprint(f"[red]Failed to add cron job: {e}[/red]")
        raise typer.Exit(1) from None


@cron_app.command("remove")
def cron_remove(
    name: str = typer.Argument(help="Job name to remove"),
):
    """Remove a scheduled task."""
    registry = _get_crontab_registry()
    if registry.remove_job(name):
        rprint(f"[green]Removed cron job '{name}'[/green]")
    else:
        rprint(f"[yellow]Cron job '{name}' not found[/yellow]")
        raise typer.Exit(1)


@cron_app.command("enable")
def cron_enable(
    name: str = typer.Argument(help="Job name to enable"),
):
    """Enable a disabled cron job."""
    registry = _get_crontab_registry()
    try:
        registry.enable_job(name)
        rprint(f"[green]Enabled cron job '{name}'[/green]")
    except KeyError:
        rprint(f"[yellow]Cron job '{name}' not found[/yellow]")
        raise typer.Exit(1) from None


@cron_app.command("disable")
def cron_disable(
    name: str = typer.Argument(help="Job name to disable"),
):
    """Disable a cron job without removing it."""
    registry = _get_crontab_registry()
    try:
        registry.disable_job(name)
        rprint(f"[yellow]Disabled cron job '{name}'[/yellow]")
    except KeyError:
        rprint(f"[yellow]Cron job '{name}' not found[/yellow]")
        raise typer.Exit(1) from None


@cron_app.command("history")
def cron_history(
    name: str | None = typer.Argument(None, help="Job name (optional, shows all if omitted)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of records to show"),
):
    """Show execution history for cron jobs."""
    registry = _get_crontab_registry()
    history = registry.get_history(job_name=name, limit=limit)
    if not history:
        rprint("[dim]No execution history.[/dim]")
        return
    for record in history:
        status_color = {"success": "green", "error": "red", "running": "yellow"}.get(record.status, "white")
        error_msg = f"  [red]{record.error}[/red]" if record.error else ""
        rprint(
            f"  [{status_color}]{record.status}[/{status_color}]  "
            f"{record.job_name}  {record.started_at}{error_msg}"
        )


@cron_app.command("run")
def cron_run():
    """Start the cron scheduler daemon."""
    from universal_mcp.crontabs.scheduler import CrontabScheduler

    registry = _get_crontab_registry()
    jobs = registry.list_jobs(enabled_only=True)

    if not jobs:
        rprint("[yellow]No enabled cron jobs. Use 'unsw cron add' first.[/yellow]")
        raise typer.Exit(1)

    rprint(f"[green]Starting cron scheduler with {len(jobs)} job(s)...[/green]")
    for job in jobs:
        rprint(f"  [bold]{job.name}[/bold]  {job.schedule}")
    rprint("[dim]Press Ctrl+C to stop.[/dim]")

    scheduler = CrontabScheduler(registry=registry)
    asyncio.run(scheduler.run())


@cron_app.command("info")
def cron_info(
    name: str = typer.Argument(help="Job name"),
):
    """Show detailed information about a cron job."""
    registry = _get_crontab_registry()
    job = registry.get_job(name)
    if not job:
        rprint(f"[red]Cron job '{name}' not found[/red]")
        raise typer.Exit(1)

    status = "[green]enabled[/green]" if job.enabled else "[red]disabled[/red]"
    rprint(f"[bold]{job.name}[/bold]  {status}")
    rprint(f"  Schedule:     {job.schedule}")
    rprint(f"  Timezone:     {job.timezone}")
    rprint(f"  Prompt:       {job.prompt}")
    if job.model:
        rprint(f"  Model:        {job.model}")
    if job.description:
        rprint(f"  Description:  {job.description}")
    rprint(f"  Created:      {job.created_at}")
    rprint(f"  Updated:      {job.updated_at}")
    if job.tags:
        rprint(f"  Tags:         {', '.join(job.tags)}")
    rprint(f"  Max instances: {job.max_instances}")

    # Show recent history
    history = registry.get_history(job_name=name, limit=5)
    if history:
        rprint("")
        rprint("[bold]Recent executions:[/bold]")
        for record in history:
            status_color = {"success": "green", "error": "red", "running": "yellow"}.get(record.status, "white")
            rprint(f"    [{status_color}]{record.status}[/{status_color}]  {record.started_at}")


# =============================================================================
# TOP LEVEL COMMANDS
# =============================================================================

@app.command()
def status():
    """Show an overview of installed apps, tools, skills, and cron jobs."""
    async def _show_status():
        from rich.table import Table

        sdk = await _get_sdk_async()

        # -- Apps & Tools --
        apps = sdk.list_apps()
        tools = sdk.list_tools()

        rprint("[bold]Apps[/bold]")
        if apps:
            table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
            table.add_column("Name")
            table.add_column("Tools", justify="right")
            for name in apps:
                app_tools = sdk.list_tools(app=name)
                table.add_row(name, str(len(app_tools)))
            rprint(table)
        else:
            rprint("  [dim]No apps installed[/dim]")

        rprint(f"\n  [dim]Total tools: {len(tools)}[/dim]")

        return sdk

    sdk = asyncio.run(_show_status())

    # -- Skills --
    rprint("\n[bold]Skills[/bold]")
    try:
        skills_registry = _get_skills_registry()
        skills = skills_registry.list_skills()
        if skills:
            for skill in skills:
                rprint(f"  {skill.name} [dim]({skill.scope})[/dim]")
        else:
            rprint("  [dim]No skills installed[/dim]")
    except Exception:
        rprint("  [dim]No skills installed[/dim]")

    # -- Cron Jobs --
    rprint("\n[bold]Cron Jobs[/bold]")
    try:
        cron_registry = _get_crontab_registry()
        jobs = cron_registry.list_jobs()
        if jobs:
            for job in jobs:
                status_tag = "[green]enabled[/green]" if job.enabled else "[red]disabled[/red]"
                rprint(f"  {job.name}  {job.schedule}  {status_tag}")
        else:
            rprint("  [dim]No cron jobs configured[/dim]")
    except Exception:
        rprint("  [dim]No cron jobs configured[/dim]")

    # -- Manifest --
    rprint("\n[bold]Manifest[/bold]")
    rprint(f"  [dim]{sdk._manifest_path}[/dim]")


@app.command()
def agent(
    prompt: str | None = typer.Option(None, "--prompt", "-p", help="Initial prompt for the agent"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model to use (e.g., sonnet, opus)"),
):
    """Start a Claude Code agent with access to the Universal MCP CLI."""
    from universal_mcp.agent import start_agent

    rprint("[green]Starting Claude Code agent with Universal MCP CLI access...[/green]")
    rprint("[dim]The agent can manage MCP apps, tools, and skills using the 'unsw' command.[/dim]")

    exit_code = start_agent(prompt=prompt, model=model)
    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
