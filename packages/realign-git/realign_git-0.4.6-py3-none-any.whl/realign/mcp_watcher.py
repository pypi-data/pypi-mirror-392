"""Session file watcher for MCP auto-commit per user request completion."""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from .config import ReAlignConfig
from .hooks import find_all_active_sessions


class DialogueWatcher:
    """Watch session files and auto-commit immediately after each user request completes."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.config = ReAlignConfig.load()
        self.last_commit_time: Optional[float] = None
        self.last_session_sizes: Dict[str, int] = {}  # Track file sizes
        self.last_stop_reason_counts: Dict[str, int] = {}  # Track stop_reason counts per session
        self.min_commit_interval = 5.0  # Minimum 5 seconds between commits (cooldown)
        self.debounce_delay = 2.0  # Wait 2 seconds after file change to ensure turn is complete
        self.running = False
        self.pending_commit_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start watching session files."""
        if not self.config.mcp_auto_commit:
            print("[MCP Watcher] Auto-commit disabled in config", file=sys.stderr)
            return

        self.running = True
        print("[MCP Watcher] Started watching for dialogue completion", file=sys.stderr)
        print(f"[MCP Watcher] Mode: Per-dialogue-turn (requires 2 new end_turn stop_reasons)", file=sys.stderr)
        print(f"[MCP Watcher] Debounce: {self.debounce_delay}s, Cooldown: {self.min_commit_interval}s", file=sys.stderr)

        # Initialize baseline sizes and stop_reason counts
        self.last_session_sizes = self._get_session_sizes()
        self.last_stop_reason_counts = self._get_stop_reason_counts()

        # Poll for file changes more frequently
        while self.running:
            try:
                await self.check_for_changes()
                await asyncio.sleep(0.5)  # Check every 0.5 seconds for responsiveness
            except Exception as e:
                print(f"[MCP Watcher] Error: {e}", file=sys.stderr)
                await asyncio.sleep(1.0)

    async def stop(self):
        """Stop watching."""
        self.running = False
        if self.pending_commit_task:
            self.pending_commit_task.cancel()
        print("[MCP Watcher] Stopped", file=sys.stderr)

    def _get_session_sizes(self) -> Dict[str, int]:
        """Get current sizes of all active session files."""
        sizes = {}
        try:
            session_files = find_all_active_sessions(self.config, self.repo_path)
            for session_file in session_files:
                if session_file.exists():
                    sizes[str(session_file)] = session_file.stat().st_size
        except Exception as e:
            print(f"[MCP Watcher] Error getting session sizes: {e}", file=sys.stderr)
        return sizes

    def _get_stop_reason_counts(self) -> Dict[str, int]:
        """Get current count of stop_reason:end_turn occurrences in all active session files."""
        counts = {}
        try:
            session_files = find_all_active_sessions(self.config, self.repo_path)
            for session_file in session_files:
                if session_file.exists():
                    counts[str(session_file)] = self._count_stop_reasons(session_file)
        except Exception as e:
            print(f"[MCP Watcher] Error getting stop_reason counts: {e}", file=sys.stderr)
        return counts

    def _count_stop_reasons(self, session_file: Path) -> int:
        """Count the number of stop_reason:end_turn occurrences in a session file."""
        count = 0
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        message = data.get("message", {})
                        if message.get("stop_reason") == "end_turn":
                            count += 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[MCP Watcher] Error counting stop_reasons in {session_file.name}: {e}", file=sys.stderr)
        return count

    async def check_for_changes(self):
        """Check if any session file has been modified."""
        try:
            current_sizes = self._get_session_sizes()

            # Detect changed files
            changed_files = []
            for path, size in current_sizes.items():
                old_size = self.last_session_sizes.get(path, 0)
                if size > old_size:
                    changed_files.append(Path(path))

            if changed_files:
                # File changed - cancel any pending commit and schedule a new one
                if self.pending_commit_task:
                    self.pending_commit_task.cancel()

                # Wait for debounce period to ensure the turn is complete
                self.pending_commit_task = asyncio.create_task(
                    self._debounced_commit(changed_files)
                )

            # Update tracked sizes
            self.last_session_sizes = current_sizes

        except Exception as e:
            print(f"[MCP Watcher] Error checking for changes: {e}", file=sys.stderr)

    async def _debounced_commit(self, changed_files: list):
        """Wait for debounce period, then check if dialogue is complete and commit."""
        try:
            # Wait for debounce period
            await asyncio.sleep(self.debounce_delay)

            # Check cooldown period
            current_time = time.time()
            if self.last_commit_time:
                time_since_last = current_time - self.last_commit_time
                if time_since_last < self.min_commit_interval:
                    print(f"[MCP Watcher] Skipping commit (cooldown: {time_since_last:.1f}s < {self.min_commit_interval}s)", file=sys.stderr)
                    return

            # Check if any of the changed files contains a complete dialogue turn
            has_complete_turn = False
            for session_file in changed_files:
                if await self._check_if_turn_complete(session_file):
                    has_complete_turn = True
                    print(f"[MCP Watcher] Complete turn detected in {session_file.name}", file=sys.stderr)
                    break

            if has_complete_turn:
                await self._do_commit()

        except asyncio.CancelledError:
            # Task was cancelled because a newer change was detected
            pass
        except Exception as e:
            print(f"[MCP Watcher] Error in debounced commit: {e}", file=sys.stderr)

    async def _check_if_turn_complete(self, session_file: Path) -> bool:
        """
        Check if the session file contains a complete dialogue turn.

        A complete turn is defined as having 2 NEW stop_reason:end_turn occurrences
        since the last commit. This represents:
        1. User message -> Assistant response with end_turn (first turn)
        2. User message -> Assistant response with end_turn (second turn)

        This ensures we only commit after a full back-and-forth dialogue turn.
        """
        try:
            # Count current stop_reason:end_turn occurrences
            current_count = self._count_stop_reasons(session_file)

            # Get the last known count for this session
            session_path = str(session_file)
            last_count = self.last_stop_reason_counts.get(session_path, 0)

            # Calculate how many new stop_reasons have been added
            new_stop_reasons = current_count - last_count

            # Debug logging
            if new_stop_reasons > 0:
                print(f"[MCP Watcher] {session_file.name}: {new_stop_reasons} new end_turn(s) detected (was {last_count}, now {current_count})", file=sys.stderr)

            # A complete dialogue turn requires at least 2 new stop_reasons
            return new_stop_reasons >= 2

        except Exception as e:
            print(f"[MCP Watcher] Error checking turn completion: {e}", file=sys.stderr)
            return False

    async def _do_commit(self):
        """Perform the actual commit."""
        try:
            # Generate commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"chore: Auto-commit MCP session ({timestamp})"

            # Use realign commit command
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_realign_commit,
                message
            )

            if result:
                print(f"[MCP Watcher] ✓ Committed: {message}", file=sys.stderr)
                self.last_commit_time = time.time()

                # Update baseline stop_reason counts after successful commit
                self.last_stop_reason_counts = self._get_stop_reason_counts()
                print(f"[MCP Watcher] Updated baseline stop_reason counts", file=sys.stderr)

        except Exception as e:
            print(f"[MCP Watcher] Error during commit: {e}", file=sys.stderr)

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
