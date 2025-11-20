#!/usr/bin/env python3
import signal
import sys
from importlib.metadata import version

import typer
from rich.console import Console
from rich.table import Table

from .config import CONFIG
from .mcp import app as mcp_app
from .mcp import get_steps as mcp_get_steps
from .mcp import save_step as mcp_save_step
from .mcp import task_create as mcp_create_task
from .mcp import task_list as mcp_list_tasks
from .mcp import task_show as mcp_show_task
from .services import Timeline
from .utils0 import L as logger  # noqa: N811


def version_callback(value: bool) -> None:
    if value:
        console = Console()
        console.print(f"tliner version {version('tliner')}")
        raise typer.Exit


cli_app = typer.Typer()
console = Console()


@cli_app.callback(invoke_without_command=True)
def main(version_flag: bool = typer.Option(False, "--version", "-v", help="Show version and exit", callback=version_callback, is_eager=True)) -> None:
    """🌟 Timeliner CLI - AI's diary. Tracking AI's work with markdown log"""


@cli_app.command(name="version")
def version_cmd() -> None:
    """Show version information"""
    console.print(f"tliner version {version('tliner')}")


@cli_app.command()
def serve(  # noqa: PLR0913
    mkdocs: bool = typer.Option(False, "--mkdocs/--no-mkdocs", help="Enable MkDocs documentation server"),
    mkdocs_auto_open: bool = typer.Option(True, "--mkdocs-auto-open/--no-mkdocs-auto-open", help="Auto-open browser on MkDocs start"),
    mkdocs_port: int | None = typer.Option(None, "--mkdocs-port", help="MkDocs server port (default: hash-based stable port)"),
    mkdocs_idle_timeout: int = typer.Option(300, "--mkdocs-idle-timeout", help="Idle timeout in seconds before MkDocs server shuts down"),
    mkdocs_regenerate_settings: bool = typer.Option(True, "--mkdocs-regenerate-settings/--no-mkdocs-regenerate-settings", help="Force regenerate MkDocs config files"),
    mkdocs_site_name: str | None = typer.Option(None, "--mkdocs-site-name", help="Custom site name for MkDocs"),
    mkdocs_reverse_navigation: bool = typer.Option(False, "--mkdocs-reverse-navigation/--no-mkdocs-reverse-navigation", help="Show newest tasks first in navigation"),
) -> None:
    """Run Timeliner as MCP server"""
    console.print("[green]Starting Timeliner MCP server...[/green]")

    CONFIG.mkdocs = mkdocs
    CONFIG.mkdocs_auto_open = mkdocs_auto_open
    CONFIG.mkdocs_port = mkdocs_port
    CONFIG.mkdocs_idle_timeout = mkdocs_idle_timeout
    CONFIG.mkdocs_regenerate_settings = mkdocs_regenerate_settings
    CONFIG.mkdocs_site_name = mkdocs_site_name
    CONFIG.mkdocs_reverse_navigation = mkdocs_reverse_navigation

    def signal_handler(signum: int, _frame: object) -> None:
        logger.info("Received signal %d, shutting down...", signum)
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    mcp_app.run()


@cli_app.command()
def task_create(title: str, user_prompt: str | None = typer.Option(None, "--prompt", "-p", help="Initial user prompt to save as first step")) -> None:
    """Create a new task with auto-generated ID"""
    result = mcp_create_task.fn(task_title=title, user_prompt=user_prompt or "")
    task_id = result.get("task_id")
    console.print(f"[green]✓[/green] Created task: [cyan]{task_id}[/cyan]")
    if user_prompt:
        console.print("  Initial prompt saved as step")


@cli_app.command()
def task_list() -> None:
    """List all tasks in the system"""
    result = mcp_list_tasks.fn()
    tasks = result.get("tasks", [])
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("Task ID", style="cyan")
    table.add_column("Description")
    table.add_column("Steps", justify="right", style="green")

    for task in tasks:
        task_id = task["task_id"]
        title = task.get("title") or "[dim]No title[/dim]"
        steps = Timeline().get_steps_by_task_id(task_id)
        step_count = str(len(steps))

        table.add_row(task_id, title, step_count)

    console.print(table)


@cli_app.command()
def task_show(task_id: str) -> None:
    """Show all steps for a task"""
    result = mcp_show_task.fn(task_id)
    steps = result.get("steps", [])

    console.print(f"\n[bold cyan]Task: {task_id}[/bold cyan]")
    for step in steps:
        console.print(f"\n[green]{step['timestamp']}[/green]")
        console.print(f"  {step['outcomes']}", markup=False)
        if step.get("tags"):
            console.print(f"  Tags: {', '.join(step['tags'])}")


@cli_app.command()
def create(task_id: str, title: str, outcomes: str, tags: list[str] | None = typer.Option(None, "--tag", "-t", help="Tags for the step")) -> None:  # noqa: B008
    """Create a step for a task"""
    result = mcp_save_step.fn(task_id=task_id, title=title, outcomes=outcomes, tags=tags or [], metadata=None)
    step_id = result.get("step_id", "N/A")
    console.print(f"[green]✓[/green] Saved step {step_id} for task {task_id}")


@cli_app.command(name="list")
def list_steps(
    since: str | None = typer.Option(None, "--since", "-s", help="Filter steps since timestamp (include) (ISO format, e.g., 2025-01-01T00:00:00Z). Couple of --until"),
    until: str | None = typer.Option(None, "--until", "-u", help="Filter steps until timestamp (exclude) (ISO format, e.g., 2025-01-01T00:00:00Z). Couple of --since"),
    tasks: list[str] | None = typer.Option(None, "--task", "-t", help="Filter steps by task ID(s)"),  # noqa: B008
) -> None:
    """List all steps across all tasks with optional time and task filters"""
    result = mcp_get_steps.fn(since=since or "", until=until or "", task_ids=tasks or [])
    steps = result.get("steps", [])

    if not steps:
        console.print("[yellow]No steps found[/yellow]")
        return

    title_parts = ["All Steps"]
    if since and until:
        title_parts.append(f"since {since} until {until}")
    elif since:
        title_parts.append(f"since {since}")
    elif until:
        title_parts.append(f"until {until}")
    if tasks:
        title_parts.append(f"tasks: {', '.join(tasks)}")
    title = title_parts[0] + (f" ({', '.join(title_parts[1:])})" if len(title_parts) > 1 else "")
    table = Table(title=title)
    table.add_column("Timestamp", style="green")
    table.add_column("Task ID", style="cyan")
    table.add_column("Outcomes")
    table.add_column("Tags", style="dim")

    for step in steps:
        timestamp = step["timestamp"]
        task_id = step["task_id"]
        outcomes = step["outcomes"][:80] + "..." if len(step["outcomes"]) > 80 else step["outcomes"]  # noqa: PLR2004
        tags = ", ".join(step.get("tags", []))

        table.add_row(timestamp, task_id, outcomes, tags)

    console.print(table)
    console.print(f"\n[dim]Total: {len(steps)} steps[/dim]")


@cli_app.command()
def task_generate_id() -> None:
    """Generate a new task ID"""
    task_id = Timeline().generate_task_id()
    console.print(f"Generated task ID: [cyan]{task_id}[/cyan]")


app = cli_app

if __name__ == "__main__":
    cli_app()
