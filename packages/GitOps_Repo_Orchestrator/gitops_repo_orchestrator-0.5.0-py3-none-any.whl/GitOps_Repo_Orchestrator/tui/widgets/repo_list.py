"""Repository list widget for the GORO TUI."""
from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from textual.widgets import Label, ListItem, ListView
    from textual.message import Message

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, ListItem, ListView, Static

from ..utils import safe_id


class RepoList(ListView):
    """Widget that displays a list of repositories."""

    repos = reactive(dict)
    selected_repo = reactive(str)

    def __init__(self, repos: Dict, **kwargs):
        # Initialize with empty list - we'll populate it in on_mount
        super().__init__(*[], **kwargs)
        self._repos = dict(repos)  # Internal storage
        self.selected_repo = next(iter(repos), "")
        
    @property
    def repos(self) -> Dict:
        return self._repos
        
    @repos.setter
    def repos(self, new_repos: Dict) -> None:
        # Update the internal state
        self._repos = dict(new_repos)
        
        # Store current selection if it still exists
        current_selection = self.selected_repo if self.selected_repo in self._repos else (
            next(iter(self._repos)) if self._repos else None
        )
        
        # Clear and repopulate the list
        self.clear()
        
        # Add all repositories to the list view
        for name in sorted(self._repos.keys()):
            item = ListItem(Label(name), id=safe_id(name))
            self.append(item)
        
        # Update selection if needed
        if current_selection and current_selection in self._repos:
            self.selected_repo = current_selection
            # Find and select the item in the list by name
            for i, item in enumerate(self.children):
                if item.children and isinstance(item.children[0], Label):
                    try:
                        # Try to get text using render() method
                        rendered = item.children[0].render()
                        if hasattr(rendered, 'plain'):
                            label_text = rendered.plain
                        else:
                            # Fallback to string representation
                            label_text = str(rendered)
                        
                        if label_text == current_selection:
                            self.index = i
                            return
                    except Exception:
                        continue
            # The selection will be handled by the ListView.Selected event

    def on_list_view_selected(self, event: 'RepoList.Selected') -> None:
        """Handle repository selection."""
        if hasattr(event, 'repo_name') and event.repo_name in self._repos:
            self.selected_repo = event.repo_name

    class Selected(ListView.Selected):
        """Message sent when a repository is selected."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Get the repository name from the selected item
            if hasattr(self, 'item') and hasattr(self.item, 'children'):
                for child in self.item.children:
                    if isinstance(child, Label):
                        try:
                            rendered = child.render()
                            self.repo_name = rendered.plain if hasattr(rendered, 'plain') else str(rendered)
                            break
                        except Exception:
                            continue
            else:
                self.repo_name = ''
