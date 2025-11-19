"""A unified dialog for adding and editing repositories."""
from pathlib import Path
from typing import Optional, Literal, Union, Tuple

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from ..utils import is_valid_repo_name, resolve_path


class RepoDialog(ModalScreen[Union[Tuple[str, Path], Tuple[str, str, Path], None]]):
    """A dialog for adding or editing a repository.
    
    Args:
        mode: Either "add" or "edit"
        repo_name: The name of the repository (for edit mode)
        repo_path: The path of the repository (for edit mode)
    """
    
    CSS_PATH = "../css/dialogs.tcss"
    
    def __init__(
        self, 
        mode: Literal["add", "edit"], 
        repo_name: str = "", 
        repo_path: str = "",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.original_name = repo_name if mode == "edit" else ""
        self.original_path = repo_path if mode == "edit" else ""
        
        # Set title based on mode
        if mode == "add":
            self.title = "Add Repository"
            self.button_text = "Add"
        else:
            self.title = f"Edit Repository: {repo_name}"
            self.button_text = "Save"
    
    def compose(self) -> ComposeResult:
        """Create the dialog content."""
        with Container(classes="dialog-screen"):
            with Container():
                yield Label(self.title, classes="dialog-header")
                with Vertical(classes="dialog-content"):
                    yield Input(
                        value=self.original_name,
                        placeholder="Repository name", 
                        id="repo-name"
                    )
                    yield Input(
                        value=str(self.original_path),
                        placeholder="Repository path", 
                        id="repo-path"
                    )
                with Horizontal(classes="dialog-buttons"):
                    yield Button("Cancel", variant="error", id="cancel-btn")
                    yield Button(self.button_text, variant="primary", id="save-btn")
    
    def on_mount(self) -> None:
        """Focus the name input when dialog is mounted."""
        self.query_one("#repo-name", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the dialog."""
        if event.button.id == "save-btn":
            self.save_repository()
        else:
            self.dismiss(None)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields."""
        if event.input.id == "repo-path":
            self.save_repository()
        else:
            # Move focus to path input
            self.query_one("#repo-path", Input).focus()
    
    def save_repository(self) -> None:
        """Validate and save the repository."""
        name_input = self.query_one("#repo-name", Input)
        path_input = self.query_one("#repo-path", Input)
        
        name = name_input.value.strip()
        path_str = path_input.value.strip()
        
        if not name:
            self.notify("Repository name cannot be empty", severity="error")
            return
            
        if not path_str:
            self.notify("Repository path cannot be empty", severity="error")
            return
            
        try:
            path = resolve_path(path_str)
            if not path.exists():
                self.notify(f"Path does not exist: {path}", severity="error")
                return
                
            if not is_valid_repo_name(name):
                self.notify(
                    "Invalid repository name. Please avoid these characters: \\ / : * ? \" < > |\n"
                    "Names must be 1-100 characters long and contain at least one non-space character.",
                    severity="error"
                )
                return
            
            # Return appropriate result based on mode
            if self.mode == "add":
                self.dismiss((name, path))
            else:
                self.dismiss((self.original_name, name, path))
                
        except Exception as e:
            self.notify(f"Error: {str(e)}", severity="error")
