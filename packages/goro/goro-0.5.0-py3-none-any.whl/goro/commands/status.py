"""Status commands for GORO."""

import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

from rich.console import Console
from rich.table import Table

from goro.config import Config

console = Console()

def get_git_status(repo_path: Path) -> Tuple[bool, str]:
    """Get the git status of a repository.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        Tuple of (is_clean, status_output)
    """
    try:
        # Check if the directory is a git repository
        result = subprocess.run(
            ["git", "status"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return False, result.stderr or "Unknown error"
            
        status_output = result.stdout.strip()
        is_clean = "nothing to commit, working tree clean" in status_output
        return is_clean, status_output
        
    except Exception as e:
        return False, f"Error checking status: {str(e)}"

def status_repo(name: str) -> None:
    """Show status of a single repository.
    
    Args:
        name: Name of the repository to check (case-insensitive)
    """
    config = Config.load()
    
    # Case-insensitive search for the repository
    repo_name = next((n for n in config.repos if n.lower() == name.lower()), None)
    
    if not repo_name:
        console.print(f"[red]Error: Repository '{name}' not found.[/]")
        console.print("Available repositories:")
        for repo in config.repos:
            console.print(f"- {repo}")
        return
        
    repo = config.repos[repo_name]
    is_clean, status = get_git_status(repo.path)
    
    console.print(f"\n[bold]Repository:[/] {name}")
    console.print(f"[bold]Path:[/] {repo.path}\n")
    
    if is_clean:
        console.print("[green]✓ Working directory clean[/]")
    else:
        console.print("[yellow]! Uncommitted changes:[/]")
        console.print(status)

def status_all() -> None:
    """Show status of all tracked repositories."""
    config = Config.load()
    
    if not config.repos:
        console.print("[yellow]No repositories tracked.[/]")
        return
        
    table = Table(title="Repository Status")
    table.add_column("Repository", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Path", style="magenta")
    
    for name, repo in config.repos.items():
        is_clean, _ = get_git_status(repo.path)
        status = "[green]Clean" if is_clean else "[yellow]Dirty"
        table.add_row(name, status, str(repo.path))
    
    console.print(table)
