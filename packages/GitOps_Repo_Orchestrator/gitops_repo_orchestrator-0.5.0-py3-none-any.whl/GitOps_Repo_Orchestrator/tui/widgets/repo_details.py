"""Repository details widget for the GORO TUI."""
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Label, Static

from GitOps_Repo_Orchestrator.config import RepoConfig


class RepoDetails(Static):
    """Widget that displays details of the selected repository."""

    repo: Optional[RepoConfig] = reactive(None)

    def compose(self) -> ComposeResult:
        """Create child widgets for the repository details."""
        with Container(id="repo-details-container"):
            yield Label("Repository Details", classes="header")
            with Container(id="repo-details"):
                yield Label("Select a repository to view details")

    def update_repo(self, repo: Optional[RepoConfig] = None) -> None:
        """Update the displayed repository details.

        Args:
            repo: The repository configuration to display, or None to show no selection
        """
        self.repo = repo
        details = self.query_one("#repo-details", Container)
        details.remove_children()

        if repo is None:
            details.mount(Label("Select a repository to view details"))
            return

        # Create a Static widget with rich content
        from rich.panel import Panel as RichPanel
        from rich.table import Table as RichTable
        
        table = RichTable(show_header=False, box=None, show_edge=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Name:", repo.name)
        table.add_row("Path:", str(repo.path))
        table.add_row("Plugins:", ", ".join(repo.plugins) if repo.plugins else "None")

        panel = RichPanel(
            table,
            title=f"{repo.name}",
            border_style="blue",
            expand=True
        )
        
        # Create a Static widget to display the rich content
        static = Static()
        static.update(panel)
        details.mount(static)
