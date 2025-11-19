"""Dialog for syncing all repositories."""
import asyncio
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label
from textual import work

class SyncDialog(ModalScreen[None]):
    """A dialog showing sync progress for all repositories."""

    BINDINGS = [("escape", "dismiss")]
    
    DEFAULT_CSS = """
    SyncDialog {
        align: center middle;
    }
    
    SyncDialog > Container {
        width: 90%;
        height: 90%;
        max-width: 80;
        background: $surface;
        padding: 2 3;
        border: panel $primary;
        border-title-color: $text;
    }
    
    .sync-header {
        width: 100%;
        text-style: bold;
        margin-bottom: 1;
        padding-bottom: 1;
        border-bottom: solid $accent;
    }
    
    .sync-output {
        width: 100%;
        height: 1fr;
        overflow: auto;
        margin: 0 0;
        padding: 1;
        background: $panel;
        border: panel $panel-lighten-2;
    }
    
    .dialog-buttons {
        width: 100%;
        height: auto;
        min-height: 3;
        align: right middle;
        margin-top: 1;
        margin-bottom: 1;
    }
    
    .dialog-buttons > Button {
        min-width: 10;
        margin-left: 1;
        opacity: 0.5;
    }
    
    .dialog-buttons > Button.enabled {
        opacity: 1;
    }
    
    .command {
        color: $text-muted;
        margin: 0 0 0 0;  /* top right bottom left - using integers only */
    }
    
    .command-output {
        margin: 0 0 0 2;
        color: $text;
    }
    
    .error {
        color: $error;
    }
    
    .success {
        color: $success;
    }
    
    .repo-header {
        text-style: bold underline;
        color: $accent;
        margin: 1 0 0 0;
        padding: 1 0;
        border-bottom: solid $accent 30%;
    }
    """

    def __init__(self, config: Dict, *args, **kwargs) -> None:
        """Initialize the sync dialog.
        
        Args:
            config: The application configuration containing repository paths.
        """
        super().__init__(*args, **kwargs)
        self.config = config
        self.results: List[Tuple[str, str, bool]] = []  # (repo_name, output, success)
        self.close_button: Optional[Button] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the dialog."""
        with Container():
            yield Label("Syncing Repositories", classes="sync-header")
            with ScrollableContainer(classes="sync-output"):
                self.output_container = Static()
                yield self.output_container
            with Container(classes="dialog-buttons"):
                self.close_button = Button("Close", variant="primary", id="close", disabled=True)
                yield self.close_button

    def on_mount(self) -> None:
        """Start the sync process when the dialog is mounted."""
        self.start_sync()

    @work(exclusive=True)
    async def start_sync(self) -> None:
        """Run git sync commands for all repositories."""
        for repo_name, repo_data in self.config.repos.items():
            repo_path = Path(repo_data.path)
            await self.run_sync_commands(repo_name, repo_path)
        
        # Enable close button after all repos are synced
        if self.close_button:
            self.close_button.disabled = False
            self.close_button.add_class("enabled")

    async def run_sync_commands(self, repo_name: str, repo_path: Path) -> None:
        """Run git commands for a single repository.
        
        Args:
            repo_name: Name of the repository
            repo_path: Path to the repository
        """
        # Display repository name prominently
        await self.append_output(f"{repo_name}", "repo-header")
        
        commands = [
            ("git add .", "Adding changes"),
            ('git commit -m "goro Sync: Auto-commit by GORO" --allow-empty-message', "Committing changes"),
            ("git pull", "Pulling latest changes"),
            ("git push", "Pushing changes")
        ]
        
        for cmd, description in commands:
            success, output = await self.run_command(cmd, repo_path)
            self.results.append((repo_name, f"{description}: {output}", success))
            
            if not success:
                break  # Stop if any command fails

    async def run_command(self, command: str, cwd: Path) -> Tuple[bool, str]:
        """Run a shell command and return its output.
        
        Args:
            command: The command to run
            cwd: Working directory for the command
            
        Returns:
            Tuple of (success, output)
        """
        # Update UI with the command being run
        await self.append_output(f"$ {command}", "command")
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                shell=True
            )
            
            # Read output in real-time
            output = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line = line.decode().strip()
                output.append(line)
                await self.append_output(line, "command-output")
            
            # Wait for process to complete
            await process.wait()
                
            return True, output
            
        except Exception as e:
            error_msg = f"Error running command: {str(e)}"
            await self.append_output(error_msg, "error")
            return False, error_msg

    async def append_output(self, text: str, class_name: str = "") -> None:
        """Append text to the output container."""
        output = self.query_one(".sync-output", ScrollableContainer)
        output.mount(Static(text, classes=class_name))
        output.scroll_end(animate=False)
        # Force a refresh to show the output immediately
        self.refresh()

    def action_dismiss(self) -> None:
        """Dismiss the dialog."""
        if self.close_button and not self.close_button.disabled:
            self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "close" and not event.button.disabled:
            self.dismiss()
