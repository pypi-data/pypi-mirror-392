"""ReAlign auto-commit command - Automatically commit after each chat round."""

import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Set
import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from ..config import ReAlignConfig
from ..hooks import find_all_active_sessions
from ..commands.init import init_command
from ..commands.commit import commit_command as manual_commit

console = Console()


def is_realign_initialized() -> bool:
    """Check if ReAlign is initialized in the current repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip())

        # Check if .realign directory exists
        realign_dir = repo_root / ".realign"
        if not realign_dir.exists():
            return False

        # Check if hooks are installed
        result = subprocess.run(
            ["git", "config", "core.hooksPath"],
            capture_output=True,
            text=True,
        )
        hooks_path = result.stdout.strip()

        return ".realign/hooks" in hooks_path
    except subprocess.CalledProcessError:
        return False


def auto_initialize():
    """Automatically initialize ReAlign if not already initialized."""
    if not is_realign_initialized():
        console.print("[yellow]⚙️  ReAlign not initialized. Initializing...[/yellow]")
        try:
            # Call init command with auto-yes
            result = subprocess.run(
                ["realign", "init", "--yes"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                console.print("[green]✓[/green] ReAlign initialized successfully")
                return True
            else:
                console.print(f"[red]✗[/red] Failed to initialize ReAlign:\n{result.stderr}")
                return False
        except Exception as e:
            console.print(f"[red]✗[/red] Error initializing ReAlign: {e}")
            return False
    return True


def get_session_mtimes(repo_root: Path) -> dict:
    """Get modification times for all active session files."""
    config = ReAlignConfig.load()
    session_files = find_all_active_sessions(config, repo_root)

    mtimes = {}
    for session_file in session_files:
        if session_file.exists():
            mtimes[str(session_file)] = session_file.stat().st_mtime

    return mtimes


def generate_commit_message() -> str:
    """Generate an automatic commit message."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"chore: Auto-commit chat session ({timestamp})"


def auto_commit_once(repo_root: Path, message: Optional[str] = None, silent: bool = False) -> bool:
    """
    Perform a single auto-commit.

    Args:
        repo_root: Path to the repository root
        message: Custom commit message (auto-generated if not provided)
        silent: If True, suppress console output (for watcher mode)

    Returns:
        True if commit was successful, False otherwise
    """
    commit_message = message or generate_commit_message()

    try:
        # Stage all changes including sessions
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        )

        # Run realign commit
        result = subprocess.run(
            ["realign", "commit", "-m", commit_message],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            if not silent:
                console.print(f"[green]✓[/green] Auto-committed: {commit_message}")
            return True
        else:
            # Check if it's just "no changes" error
            if "No changes detected" in result.stdout or "No changes detected" in result.stderr:
                if not silent:
                    console.print("[dim]No changes to commit[/dim]")
                return True
            else:
                if not silent:
                    console.print(f"[red]✗[/red] Commit failed:\n{result.stderr}")
                return False
    except subprocess.CalledProcessError as e:
        if not silent:
            console.print(f"[red]✗[/red] Error during commit: {e}")
        return False


def auto_commit_command(
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Watch for changes and auto-commit continuously"
    ),
    interval: int = typer.Option(
        5,
        "--interval",
        "-i",
        help="Check interval in seconds (default: 5)"
    ),
    message: Optional[str] = typer.Option(
        None,
        "--message",
        "-m",
        help="Custom commit message (auto-generated if not provided)"
    ),
):
    """
    Automatically commit after each chat round.

    By default, performs a single commit. Use --watch to continuously monitor
    and commit changes as they happen.
    """
    # Check if in git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        console.print("[red]Error: Not in a git repository[/red]")
        raise typer.Exit(1)

    # Auto-initialize if needed
    if not auto_initialize():
        console.print("[red]Failed to initialize ReAlign[/red]")
        raise typer.Exit(1)

    if not watch:
        # Single commit mode
        console.print("[cyan]🔄 Performing auto-commit...[/cyan]")
        success = auto_commit_once(repo_root, message)
        if success:
            console.print("[green]✓[/green] Done")
        else:
            raise typer.Exit(1)
        return

    # Watch mode
    console.print("[cyan]👁️  Watching for session changes...[/cyan]")
    console.print(f"[dim]   Check interval: {interval} seconds[/dim]")
    console.print("[dim]   Press Ctrl+C to stop[/dim]\n")

    # Track last known modification times
    last_mtimes = get_session_mtimes(repo_root)
    commit_count = 0

    try:
        while True:
            time.sleep(interval)

            # Check for changes
            current_mtimes = get_session_mtimes(repo_root)

            # Detect if any session file was modified
            has_changes = False
            for session_path, mtime in current_mtimes.items():
                if session_path not in last_mtimes or last_mtimes[session_path] < mtime:
                    has_changes = True
                    console.print(f"[yellow]📝 Session change detected: {Path(session_path).name}[/yellow]")
                    break

            if has_changes:
                console.print("[cyan]🔄 Auto-committing...[/cyan]")
                if auto_commit_once(repo_root, message):
                    commit_count += 1
                    console.print(f"[green]✓[/green] Total commits: {commit_count}\n")
                last_mtimes = current_mtimes

    except KeyboardInterrupt:
        console.print(f"\n[cyan]👋 Stopped watching. Total commits: {commit_count}[/cyan]")
