"""Sync commands for GORO."""

import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from goro.config import Config

console = Console()

async def run_git_command(cmd: List[str], cwd: Path) -> Tuple[bool, List[str]]:
    """Run a git command and capture its output.
    
    Args:
        cmd: List of command arguments
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success, output_lines)
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        output = []
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line = line.decode().strip()
            if line:  # Only log non-empty lines
                output.append(line)
        
        await process.wait()
        return process.returncode == 0, output
        
    except Exception as e:
        return False, [f"Error: {str(e)}"]

async def sync_repository(name: str, show_header: bool = False) -> bool:
    """Synchronize a single repository.
    
    Args:
        name: Name of the repository to sync
        show_header: Whether to show the repository header
        
    Returns:
        bool: True if sync was successful, False otherwise
    """
    config = Config.load()
    
    # Case-insensitive search for the repository
    repo_name = next((n for n in config.repos if n.lower() == name.lower()), None)
    
    if not repo_name:
        console.print(f"[red]Error: Repository '{name}' not found.[/]")
        return False
    
    if show_header:
        console.print(f"\n[bold]=== Syncing {repo_name} ===[/]")
    
    repo = config.repos[repo_name]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Syncing {repo_name}...", total=100)
        
        # Fetch changes
        success, output = await run_git_command(["git", "fetch"], repo.path)
        if not success:
            progress.print(f"[red]Error fetching changes for {repo_name}:[/]")
            for line in output:
                progress.print(f"  {line}")
            return False
        
        # Pull changes
        success, output = await run_git_command(["git", "pull"], repo.path)
        progress.update(task, completed=100)
        
        if success:
            if output and any(not line.startswith('Already up to date') for line in output):
                console.print(f"[green]✓ Successfully synced {repo_name}[/]")
                for line in output:
                    if line.strip() and not line.startswith('Already up to date'):
                        console.print(f"  {line}")
            else:
                console.print(f"[green]✓ {repo_name} is already up to date[/]")
            return True
        else:
            console.print(f"[red]✗ Error syncing {repo_name}:[/]")
            for line in output:
                console.print(f"  {line}")
            return False

async def sync_all_repositories() -> None:
    """Synchronize all tracked repositories."""
    config = Config.load()
    
    if not config.repos:
        console.print("[yellow]No repositories to sync.[/]")
        return
    
    console.print("\n[bold]Starting sync for all repositories:[/]")
    
    # Run syncs sequentially for better output readability
    for name in config.repos:
        console.print(f"\n[bold]=== Syncing {name} ===[/]")
        await sync_repository(name)
    
    console.print("\n[bold]All repositories synced.[/]")
