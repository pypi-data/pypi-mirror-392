"""Edit commands for GORO."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from goro.config import Config, RepoConfig

console = Console()

def edit_repository(
    name: str,
    new_name: Optional[str] = None,
    path: Optional[str] = None,
    force: bool = False,
) -> None:
    """Edit a repository's name and/or path.
    
    Args:
        name: Current name of the repository to edit
        new_name: New name for the repository (optional)
        path: New path for the repository (optional)
        force: Skip confirmation prompts
    """
    config = Config.load()
    
    # Case-insensitive search for the repository
    repo_name = next((n for n in config.repos if n.lower() == name.lower()), None)
    
    if not repo_name:
        console.print(f"[red]Error: Repository '{name}' not found.[/]")
        console.print("Available repositories:")
        for repo in config.repos:
            console.print(f"- {repo}")
        raise typer.Exit(1)
    
    repo = config.repos[repo_name]
    
    # If no arguments provided, enter interactive mode
    if new_name is None and path is None:
        console.print(f"\nEditing repository: [bold]{repo_name}[/]")
        console.print(f"Current path: {repo.path}")
        
        new_name = Prompt.ask(
            "New name (press Enter to keep current)",
            default=repo_name,
            show_default=False
        )
        
        new_path = Prompt.ask(
            "New path (press Enter to keep current)",
            default=str(repo.path),
            show_default=False
        )
        
        if new_path != str(repo.path):
            new_path = Path(new_path).expanduser().resolve()
            if not new_path.exists():
                console.print(f"[yellow]Warning: Path '{new_path}' does not exist.[/]")
                if not force and not Confirm.ask("Continue anyway?", default=False):
                    console.print("Edit cancelled.")
                    raise typer.Exit(0)
    else:
        new_path = Path(path).expanduser().resolve() if path else repo.path
        new_name = new_name or repo_name
    
    # Check if new name conflicts with existing repositories
    if new_name.lower() != repo_name.lower() and new_name.lower() in (
        n.lower() for n in config.repos if n != repo_name
    ):
        console.print(f"[red]Error: A repository named '{new_name}' already exists.[/]")
        raise typer.Exit(1)
    
    # Check if new path is already tracked
    if str(new_path) != str(repo.path) and any(
        str(r.path) == str(new_path) for n, r in config.repos.items() if n != repo_name
    ):
        console.print(f"[red]Error: Path '{new_path}' is already tracked.[/]")
        raise typer.Exit(1)
    
    # Show changes and confirm
    changes = []
    if new_name != repo_name:
        changes.append(f"Rename: '{repo_name}' → '{new_name}'")
    if str(new_path) != str(repo.path):
        changes.append(f"Update path: '{repo.path}' → '{new_path}'")
    
    if not changes:
        console.print("No changes to make.")
        return
    
    console.print("\nChanges to be made:")
    for change in changes:
        console.print(f"- {change}")
    
    if not force and not Confirm.ask("\nApply these changes?"):
        console.print("Edit cancelled.")
        return
    
    # Apply changes
    if repo_name != new_name:
        config.repos[new_name] = RepoConfig(path=new_path)
        del config.repos[repo_name]
    else:
        config.repos[repo_name].path = new_path
    
    config.save()
    console.print(f"\n[green]✓ Successfully updated repository.[/]")
    console.print(f"Name: {new_name}")
    console.print(f"Path: {new_path}")
