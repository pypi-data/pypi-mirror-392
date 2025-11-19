"""Main Textual application for GORO."""

from pathlib import Path
from typing import Optional, Dict, Any, List

from rich.panel import Panel
from rich.table import Table
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    TabbedContent,
    TabPane,
    Tabs,
)

from GitOps_Repo_Orchestrator.config import Config, RepoConfig

# Import widgets and dialogs
from .widgets import RepoList, RepoDetails, StatusBar
from .dialogs.repo_dialog import RepoDialog
from .dialogs.confirm_dialog import ConfirmDialog
from .dialogs.status_dialog import StatusDialog
from .dialogs.sync_dialog import SyncDialog
from .utils import safe_id, is_valid_repo_name, resolve_path
import asyncio
from pathlib import Path

class GRMApp(App):
    """GORO Textual Application."""

    CSS_PATH = "css/global.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_repo", "Add Repository"),
        ("r", "remove_repo", "Remove Repository"),
        ("s", "sync_repo", "Sync Repository"),
        ("S", "sync_all", "Sync All Repositories"),
        ("f2", "edit_repo", "Edit Repository"),
        ("t", "show_status", "Show Status"),
        ("c", "clear_logs", "Clear Logs"),
    ]

    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self.selected_repo = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the goro."""
        # Main app container with grid layout
        with Container(classes="main-app"):
            yield Header(show_clock=True, id="header")
            
            # Main content area
            with Horizontal():
                # Left side - Repository list with header
                with Container(id="repo-container"):
                    yield Label("Repositories", classes="section-header")
                    yield RepoList(self.config.repos, id="repo-list")
                    
                # Right side - Repository details
                yield RepoDetails(id="repo-details")
            
            # Status bar and footer
            status_bar = StatusBar(id="status-bar")
            status_bar.status = "Ready"
            yield status_bar
            yield Footer()

    def on_mount(self) -> None:
        """Handle app mount event."""
        self.title = "GORO"
        self.sub_title = f"Managing {len(self.config.repos)} repositories"
        
        # Initialize the repository list with all repositories
        if self.config.repos:
            repo_list = self.query_one("#repo-list", RepoList)
            repo_list.repos = self.config.repos
            
            # Select the first repository
            first_repo = next(iter(self.config.repos))
            self.selected_repo = first_repo
            details = self.query_one(RepoDetails)
            details.update_repo(self.config.repos[first_repo])

    def on_repo_list_selected(self, event: RepoList.Selected) -> None:
        """Handle repository selection."""
        self.selected_repo = event.repo_name
        repo = self.config.repos.get(self.selected_repo)
        details = self.query_one(RepoDetails)
        details.update_repo(repo)
        self.query_one(StatusBar).status = f"Selected: {self.selected_repo}"

    async def action_add_repo(self) -> None:
        """Add a new repository."""
        async def handle_dialog_result(result: tuple[str, Path] | None) -> None:
            if not result:
                return  # User cancelled
                
            name, path = result
            
            # Check for duplicate name
            if name in self.config.repos:
                self.notify(
                    f"A repository with name '{name}' already exists",
                    severity="error"
                )
                return
                
            try:
                # Add the new repository
                self.config.add_repo(name, str(path))
                self.config.save()
                
                # Update the UI
                self.query_one(StatusBar).status = f"Added repository: {name}"
                
                # Update the repository list
                repo_list = self.query_one("#repo-list", RepoList)
                repo_list.repos = self.config.repos
                
                # Select the new repository
                self.selected_repo = name
                
                # Update the details view
                details = self.query_one(RepoDetails)
                details.update_repo(self.config.repos[name])
                
            except ValueError as e:
                self.notify(str(e), severity="error")
        
        # Show the dialog
        self.push_screen(RepoDialog(mode="add"), handle_dialog_result)

    async def action_remove_repo(self) -> None:
        """Remove the selected repository."""
        if not self.selected_repo:
            self.notify("No repository selected", severity="warning")
            return
        
        async def remove_repo(confirmed: bool) -> None:
            if confirmed:
                try:
                    # Remove the repository
                    repo_name = self.selected_repo
                    self.config.remove_repo(repo_name)
                    self.config.save()
                    
                    # Update UI
                    self.query_one(StatusBar).status = f"Removed repository: {repo_name}"
                    self.selected_repo = None
                    
                    # Refresh the repository list
                    repo_list = self.query_one("#repo-list", RepoList)
                    repo_list.repos = self.config.repos
                    
                    # Clear details
                    details = self.query_one(RepoDetails)
                    details.update_repo(None)
                    
                except Exception as e:
                    self.notify(f"Error removing repository: {str(e)}", severity="error")
        
        # Create and show the dialog
        dialog = ConfirmDialog(
            f"Are you sure you want to remove '{self.selected_repo}'?",
            confirm_text="Remove",
            cancel_text="Cancel"
        )
        
        # Show the dialog and wait for result
        self.push_screen(dialog, remove_repo)

    async def action_edit_repo(self) -> None:
        """Edit the selected repository."""
        if not self.selected_repo:
            self.notify("No repository selected", severity="warning")
            return
            
        repo = self.config.repos[self.selected_repo]
        
        async def handle_dialog_result(result: tuple[str, str, Path] | None) -> None:
            if not result:
                return  # User cancelled
                
            old_name, new_name, new_path = result
            
            try:
                # If name changed, check for duplicates
                if old_name != new_name and new_name in self.config.repos:
                    self.notify(
                        f"A repository with name '{new_name}' already exists",
                        severity="error"
                    )
                    return
                
                # Check for duplicate path
                for repo_name, repo in self.config.repos.items():
                    if repo_name != old_name and Path(repo.path).resolve() == new_path:
                        self.notify(
                            f"A repository at this path already exists with name '{repo_name}'",
                            severity="error"
                        )
                        return
                
                # Remove the old repository if name changed
                if old_name != new_name:
                    self.config.remove_repo(old_name)
                
                # Add/update the repository
                self.config.add_repo(new_name, str(new_path))
                self.config.save()
                
                # Update UI
                self.selected_repo = new_name
                self.query_one(StatusBar).status = f"Updated repository: {new_name}"
                
                # Refresh the repository list
                repo_list = self.query_one("#repo-list", RepoList)
                repo_list.repos = self.config.repos
                
                # Select the updated repository
                for i, item in enumerate(repo_list.children):
                    if item.id == safe_id(new_name):
                        repo_list.index = i
                        break
                
                # Update the details view
                details = self.query_one(RepoDetails)
                details.update_repo(self.config.repos[new_name])
                
            except Exception as e:
                self.notify(f"Error updating repository: {str(e)}", severity="error")
        
        # Show the dialog
        self.push_screen(
            RepoDialog(mode="edit", repo_name=self.selected_repo, repo_path=repo.path),
            handle_dialog_result
        )

    async def action_sync_repo(self) -> None:
        """Sync the selected repository with detailed logging."""
        if not self.selected_repo:
            self.notify("No repository selected", severity="warning")
            return
        
        repo_name = self.selected_repo
        repo_path = Path(self.config.repos[repo_name].path)
        
        # Get the status bar instance
        status_bar = self.query_one("StatusBar")
        status_bar.log(f"Starting sync for {repo_name}...", "info")
        
        # Define git commands to run
        commands = [
            ("git add .", "Adding changes"),
            ('git commit -m "goro Sync: Auto-commit by GORO" --allow-empty-message', "Committing changes"),
            ("git pull", "Pulling latest changes"),
            ("git push", "Pushing changes")
        ]
        
        for cmd, description in commands:
            status_bar.log(f"{description}...", "info")
            try:
                # Run the command
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    cwd=repo_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    shell=True
                )
                
                # Capture and log output
                output = []
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    line = line.decode().strip()
                    if line:  # Only log non-empty lines
                        output.append(line)
                        status_bar.log(f"  {line}", "debug")
                
                # Wait for process to complete
                await process.wait()
                
            except Exception as e:
                error_msg = f"Error running '{cmd}': {str(e)}"
                status_bar.log(error_msg, "error")
                self.notify(error_msg, severity="error")
                return
        
        # Success
        status_bar.log(f"Successfully synced {repo_name}", "success")
        self.notify(f"Successfully synced {repo_name}", title="Sync Complete")

    def action_clear_logs(self) -> None:
        """Clear the status bar logs."""
        status_bar = self.query_one("StatusBar")
        status_bar.rich_log.clear()
        status_bar.log("Logs cleared", "info")
        
    async def action_show_status(self) -> None:
        """Show git status for the selected repository."""
        if not self.selected_repo:
            self.notify("No repository selected", severity="warning")
            return
            
        repo_name = self.selected_repo
        repo_path = Path(self.config.repos[repo_name].path)
        
        # Get the status bar instance for logging
        status_bar = self.query_one("StatusBar")
        status_bar.log(f"Checking status for {repo_name}...", "info")
        
        try:
            # Run git status command
            process = await asyncio.create_subprocess_shell(
                "git status",
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                shell=True
            )
            
            # Capture output
            output = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                output.append(line.decode().strip())
                
            # Wait for process to complete
            await process.wait()
            
            # Show status in a dialog
            status_output = "\n".join(output)
            self.push_screen(StatusDialog(status_output, repo_name))
            
        except Exception as e:
            error_msg = f"Error checking status: {str(e)}"
            status_bar.log(error_msg, "error")
            self.notify(error_msg, severity="error")

    def action_sync_all(self) -> None:
        """Sync all repositories."""
        if not self.config.repos:
            self.notify("No repositories configured", severity="warning")
            return
            
        self.push_screen(SyncDialog(self.config))
