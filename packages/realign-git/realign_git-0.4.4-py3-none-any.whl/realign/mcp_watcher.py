"""Session file watcher for MCP auto-commit per user request completion."""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import ReAlignConfig


class DialogueWatcher:
    """Watch session files and auto-commit after each user request completes."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.config = ReAlignConfig.load()
        self.last_commit_time: Optional[float] = None
        self.check_interval = 10.0  # Check every 10 seconds
        self.min_commit_interval = 30.0  # Minimum 30 seconds between commits
        self.running = False

    async def start(self):
        """Start watching session files."""
        if not self.config.mcp_auto_commit:
            print("[MCP Watcher] Auto-commit disabled in config", file=sys.stderr)
            return

        self.running = True
        print("[MCP Watcher] Started watching for session changes", file=sys.stderr)
        print(f"[MCP Watcher] Check interval: {self.check_interval}s, Min commit interval: {self.min_commit_interval}s", file=sys.stderr)

        while self.running:
            try:
                await self.check_and_commit()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"[MCP Watcher] Error: {e}", file=sys.stderr)
                await asyncio.sleep(self.check_interval)

    async def stop(self):
        """Stop watching."""
        self.running = False
        print("[MCP Watcher] Stopped", file=sys.stderr)

    async def check_and_commit(self):
        """
        Check for session changes and commit if found.

        Uses the existing realign commit logic which already knows how to:
        - Find all active sessions using find_all_active_sessions()
        - Check if they've been modified recently (within 5 minutes)
        - Create empty commits with --allow-empty if only sessions changed
        """
        try:
            # Rate limiting
            current_time = time.time()
            if self.last_commit_time:
                time_since_last = current_time - self.last_commit_time
                if time_since_last < self.min_commit_interval:
                    return

            # Generate commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"chore: Auto-commit MCP session ({timestamp})"

            # Use realign commit command which already handles session detection
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_realign_commit,
                message
            )

            if result:
                print(f"[MCP Watcher] ✓ Committed: {message}", file=sys.stderr)
                self.last_commit_time = current_time

        except Exception as e:
            print(f"[MCP Watcher] Error during commit check: {e}", file=sys.stderr)

    def _run_realign_commit(self, message: str) -> bool:
        """
        Run realign commit command.

        The command will:
        - Auto-initialize git and ReAlign if needed
        - Check for session changes (modified within last 5 minutes)
        - Create empty commit if only sessions changed
        - Return True if commit was created, False otherwise
        """
        try:
            # Check if ReAlign is initialized
            realign_dir = self.repo_path / ".realign"

            if not realign_dir.exists():
                print("[MCP Watcher] ReAlign not initialized, initializing...", file=sys.stderr)

                # Auto-initialize ReAlign (which also inits git if needed)
                init_result = subprocess.run(
                    ["realign", "init", "--yes"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if init_result.returncode != 0:
                    print(f"[MCP Watcher] Failed to initialize ReAlign: {init_result.stderr}", file=sys.stderr)
                    return False

                print("[MCP Watcher] ✓ ReAlign initialized successfully", file=sys.stderr)

            # Now run the commit
            result = subprocess.run(
                ["realign", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Check if commit was successful
            # realign commit returns 0 on success, 1 if no changes
            if result.returncode == 0:
                return True
            elif "No changes detected" in result.stdout or "No changes detected" in result.stderr:
                # No changes - this is expected, not an error
                return False
            else:
                # Log the error for debugging
                error_msg = result.stderr or result.stdout
                if "Not in a git repository" in error_msg:
                    print("[MCP Watcher] Not in a git repository - this shouldn't happen after init!", file=sys.stderr)
                else:
                    print(f"[MCP Watcher] Commit failed: {error_msg}", file=sys.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("[MCP Watcher] Commit command timed out", file=sys.stderr)
            return False
        except FileNotFoundError:
            print("[MCP Watcher] realign command not found in PATH", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[MCP Watcher] Commit error: {e}", file=sys.stderr)
            return False


# Global watcher instance
_watcher: Optional[DialogueWatcher] = None


async def start_watcher(repo_path: Path):
    """Start the global session watcher for auto-commit on user request completion."""
    global _watcher

    if _watcher and _watcher.running:
        print("[MCP Watcher] Already running", file=sys.stderr)
        return

    _watcher = DialogueWatcher(repo_path)
    asyncio.create_task(_watcher.start())


async def stop_watcher():
    """Stop the global session watcher."""
    global _watcher

    if _watcher:
        await _watcher.stop()
        _watcher = None
