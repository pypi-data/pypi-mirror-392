"""Command-line interface for GORO."""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from GitOps_Repo_Orchestrator.commands.status import status_repo, status_all
from GitOps_Repo_Orchestrator.commands.sync import sync_repository, sync_all_repositories
from GitOps_Repo_Orchestrator.commands.edit import edit_repository
from GitOps_Repo_Orchestrator.config import Config, RepoConfig

app = typer.Typer(name="goro", help="GORO - A Git Repository Manager")
console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        from GitOps_Repo_Orchestrator import __version__

        console.print(f"goro v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
    ctx: typer.Context = typer.Context,
):
    """GORO - A TUI-based tool for managing multiple Git repositories.
    
    When no command is provided, launches the interactive TUI interface.
    """
    if ctx.invoked_subcommand is None:
        from GitOps_Repo_Orchestrator.tui.app import GRMApp
        app = GRMApp()
        app.run()


@app.command()
def init():
    """Initialize the GORO configuration."""
    config_path = Config.get_config_path()
    if config_path.exists():
        console.print("[yellow]Configuration already exists at:[/]")
        console.print(f"  {config_path}")
        return

    config = Config()
    config.save()
    console.print("[green]✓ Configuration initialized at:[/]")
    console.print(f"  {config_path}")


@app.command("list")
def list_repos():
    """List all tracked repositories."""
    config = Config.load()
    if not config.repos:
        console.print("[yellow]No repositories tracked.[/]")
        return

    table = Table(title="Tracked Repositories")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Plugins", style="magenta")

    for name, repo in config.repos.items():
        plugins = ", ".join(repo.plugins or [])
        table.add_row(name, str(repo.path), plugins)

    console.print(table)


@app.command()
def status(name: Optional[str] = typer.Argument(None, help="Name of the repository")):
    """Show status of repositories.
    
    Args:
        name: Optional repository name. If not provided, shows status of all repositories.
    """
    if name:
        # Handle case where name might be split into multiple arguments
        if name not in Config.load().repos and len(sys.argv) > 3:
            # Reconstruct the full name from remaining arguments
            name = " ".join([name] + sys.argv[3:])
        status_repo(name)
    else:
        status_all()


@app.command("status-all")
def status_all_cmd():
    """Show status of all tracked repositories."""
    status_all()


@app.command()
def sync(name: Optional[str] = typer.Argument(None, help="Name of the repository to sync")):
    """Synchronize repositories.
    
    Args:
        name: Optional repository name. If not provided, syncs all repositories.
    """
    if name:
        # Handle case where name might be split into multiple arguments
        if name not in Config.load().repos and len(sys.argv) > 3:
            # Reconstruct the full name from remaining arguments
            name = " ".join([name] + sys.argv[3:])
        asyncio.run(sync_repository(name))
    else:
        asyncio.run(sync_all_repositories())


@app.command("sync-all")
def sync_all():
    """Synchronize all tracked repositories."""
    asyncio.run(sync_all_repositories())


@app.command()
def edit(
    name: str,
    new_name: Optional[str] = typer.Option(
        None, "--name", "-n", help="New name for the repository"
    ),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="New path for the repository"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompts"
    ),
):
    """Edit a repository's name and/or path.
    
    If no options are provided, enters interactive mode.
    
    Examples:
        goro edit my-repo --name new-repo-name
        goro edit my-repo --path /new/path
        goro edit my-repo --name new-name --path /new/path
        goro edit my-repo  # Interactive mode
    """
    # Handle case where name might be split into multiple arguments
    if name not in Config.load().repos and len(sys.argv) > 3:
        # Find where the name ends and options begin
        name_parts = []
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg.startswith('--'):
                break
            name_parts.append(arg)
        if name_parts:
            name = ' '.join(name_parts)
    
    edit_repository(name=name, new_name=new_name, path=path, force=force)


@app.command()
def add(name: str, path: str):
    """Add a new repository to track.

    Args:
        name: A short name for the repository
        path: Path to the repository (can be relative or absolute)
    """
    config = Config.load()
    repo_path = Path(path).expanduser().resolve()

    # Check if the path exists and is a directory
    if not repo_path.exists():
        console.print(f"[red]Error: Path '{repo_path}' does not exist.[/]")
        raise typer.Exit(1)

    if not repo_path.is_dir():
        console.print(f"[red]Error: '{repo_path}' is not a directory.[/]")
        raise typer.Exit(1)

    # Check if the path is already tracked
    for repo in config.repos.values():
        if repo.path == repo_path:
            console.print(f"[yellow]This path is already tracked as '{repo.name}'.[/]")
            return

    # Add the repository
    config.repos[name] = RepoConfig(name=name, path=repo_path)
    config.save()
    console.print(f"[green]✓ Added repository '{name}' at {repo_path}[/]")


@app.command()
def remove(name: str):
    """Remove a tracked repository.

    Args:
        name: Name of the repository to remove
    """
    config = Config.load()
    if name not in config.repos:
        console.print(f"[red]Error: No repository named '{name}' found.[/]")
        raise typer.Exit(1)

    del config.repos[name]
    config.save()
    console.print(f"[green]✓ Removed repository '{name}'[/]")


@app.command()
def ui():
    """Launch the Textual TUI interface."""
    from GitOps_Repo_Orchestrator.tui.app import GRMApp

    app = GRMApp()
    app.run()


if __name__ == "__main__":
    app()
