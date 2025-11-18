#!/usr/bin/env python3
"""ReAlign MCP Server - Expose ReAlign functionality via Model Context Protocol."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import ReAlignConfig
from .commands import init, search, show, commit
from .mcp_watcher import start_watcher

from . import __version__

# Initialize MCP server
app = Server("realign")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ReAlign tools."""
    return [
        Tool(
            name="realign_init",
            description=(
                "Initialize ReAlign in a directory to enable AI conversation tracking with git commits. "
                "This command AUTOMATICALLY initializes a git repository if one doesn't exist yet, "
                "then sets up git hooks and configures session tracking. "
                "IMPORTANT: Use this instead of 'git init' when you want to track AI conversations. "
                "It will handle both git initialization AND ReAlign setup in one step."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to directory to initialize (default: current directory)",
                    },
                },
            },
        ),
        Tool(
            name="realign_search",
            description=(
                "Search through git commits and AI agent chat sessions. "
                "Finds commits with matching keywords in commit messages or session content. "
                "Returns commit hashes, messages, dates, and optionally session content. "
                "Can search in commits only, sessions only, or both (default)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for in commits and sessions",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)",
                    },
                    "show_session": {
                        "type": "boolean",
                        "description": "Include full session content in results",
                        "default": False,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20,
                    },
                    "session_only": {
                        "type": "boolean",
                        "description": "Search only in session files, not commits. Useful for finding topics discussed in historical conversations.",
                        "default": False,
                    },
                    "commits_only": {
                        "type": "boolean",
                        "description": "Search only in commits, not session files. Useful for quick commit message searches.",
                        "default": False,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="realign_show",
            description=(
                "Display the AI agent chat session associated with a specific git commit or session file. "
                "Supports navigation through the session with line ranges. "
                "Use realign_search first to find matching lines, then use this tool to view context around those lines."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "commit_hash": {
                        "type": "string",
                        "description": "Git commit hash (full or short)",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)",
                    },
                    "session_path": {
                        "type": "string",
                        "description": "Direct path to session file (alternative to commit_hash)",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pretty", "json", "raw"],
                        "description": "Output format",
                        "default": "pretty",
                    },
                    "from_line": {
                        "type": "integer",
                        "description": "Start from line number (inclusive, 1-indexed)",
                    },
                    "to_line": {
                        "type": "integer",
                        "description": "End at line number (inclusive, 1-indexed)",
                    },
                    "around_line": {
                        "type": "integer",
                        "description": "Show lines around this line number (use with context)",
                    },
                    "context": {
                        "type": "integer",
                        "description": "Number of lines before/after when using around_line (default: 5)",
                        "default": 5,
                    },
                    "first": {
                        "type": "integer",
                        "description": "Show only first N lines",
                    },
                    "last": {
                        "type": "integer",
                        "description": "Show only last N lines",
                    },
                },
            },
        ),
        Tool(
            name="realign_get_latest_session",
            description=(
                "Get the path to the most recent AI agent chat session. "
                "Automatically detects Claude Code sessions or uses configured history path. "
                "Useful for retrieving the current conversation context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (for Claude auto-detection)",
                    },
                },
            },
        ),
        Tool(
            name="realign_commit",
            description=(
                "Smart commit command with AI session tracking. "
                "**IMPORTANT: AI agents MUST call this tool after completing each user request to preserve the conversation history.** "
                "Automatically handles four scenarios: "
                "1) Workspace not initialized: Auto-runs 'realign init' to set up ReAlign, then commits "
                "2) Has file changes: Acts like 'git commit' with automatic session tracking "
                "3) Only AI session changes: Creates an empty commit with --allow-empty to preserve the discussion "
                "4) No changes at all: Shows an error and helpful message. "
                "Use this instead of 'git commit' to ensure AI conversations are tracked. "
                "**REQUIRED**: Call this at the end of every turn after completing the user's request. "
                "No need to call realign_init first - this tool handles initialization automatically."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Commit message",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)",
                    },
                    "all": {
                        "type": "boolean",
                        "description": "Stage all changes before committing (equivalent to -a flag)",
                        "default": False,
                    },
                    "amend": {
                        "type": "boolean",
                        "description": "Amend the previous commit",
                        "default": False,
                    },
                    "no_edit": {
                        "type": "boolean",
                        "description": "Use previous commit message (with --amend)",
                        "default": False,
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="realign_version",
            description=(
                f"Get the current version of ReAlign ({__version__}). "
                "ReAlign is a tool that tracks and versions AI agent chat sessions with git commits."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="realign_auto_commit",
            description=(
                "Automatically commit the current chat session. "
                "If ReAlign is not initialized, it will automatically initialize first. "
                "This is useful for committing after each chat round without manual intervention. "
                "Use this at the end of each AI response to ensure conversations are tracked."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Optional custom commit message. If not provided, an automatic message will be generated.",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""

    try:
        # Execute the tool
        if name == "realign_init":
            result = await handle_init(arguments)
        elif name == "realign_search":
            result = await handle_search(arguments)
        elif name == "realign_show":
            result = await handle_show(arguments)
        elif name == "realign_get_latest_session":
            result = await handle_get_latest_session(arguments)
        elif name == "realign_commit":
            result = await handle_commit(arguments)
        elif name == "realign_version":
            result = await handle_version(arguments)
        elif name == "realign_auto_commit":
            result = await handle_auto_commit(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return result

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_init(args: dict) -> list[TextContent]:
    """Handle realign_init tool."""
    from .commands.init import init_repository

    repo_path = args.get("repo_path", ".")

    # Call Python function directly instead of subprocess
    # This avoids PATH issues completely
    result = init_repository(
        repo_path=repo_path,
        auto_init_git=True,
        skip_commit=False,
    )

    # Format output with detailed parameters
    if result["success"]:
        output_lines = [
            "✅ ReAlign initialized successfully\n",
            "Parameters:",
            f"  • Repository Path: {result.get('repo_path', 'N/A')}",
            f"  • Repository Root: {result.get('repo_root', 'N/A')}",
            f"  • ReAlign Directory: {result.get('realign_dir', 'N/A')}",
            f"  • Config Path: {result.get('config_path', 'N/A')}",
            f"  • History Directory: {result.get('history_dir', 'N/A')}",
            f"  • Git Initialized: {result.get('git_initialized', False)}",
            f"  • Hooks Created: {', '.join(result.get('hooks_created', [])) or 'None'}",
            f"  • Auto-committed: {result.get('committed', False)}",
            "",
            "Next steps:",
            f"  1. Ensure your agent saves chat histories to: {result['history_dir']}",
            "  2. Make commits as usual - ReAlign will automatically track sessions",
            "  3. Search sessions with: realign search <keyword>",
            "  4. View sessions with: realign show <commit>",
        ]
        return [TextContent(type="text", text="\n".join(output_lines))]
    else:
        error_lines = [
            "❌ Failed to initialize ReAlign\n",
            f"Error: {result['message']}",
        ]
        if result.get("errors"):
            error_lines.append("\nDetails:")
            for error in result["errors"]:
                error_lines.append(f"  • {error}")
        return [TextContent(type="text", text="\n".join(error_lines))]


async def handle_search(args: dict) -> list[TextContent]:
    """Handle realign_search tool."""
    keyword = args["keyword"]
    repo_path = args.get("repo_path", ".")
    show_session = args.get("show_session", False)
    max_results = args.get("max_results", 20)
    session_only = args.get("session_only", False)
    commits_only = args.get("commits_only", False)

    # Build command
    cmd = ["realign", "search", keyword, "--max", str(max_results)]
    if show_session:
        cmd.append("--show-session")
    if session_only:
        cmd.append("--session-only")
    if commits_only:
        cmd.append("--commits-only")

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    output = result.stdout
    if result.returncode == 0:
        return [TextContent(type="text", text=output or "No results found")]
    else:
        return [TextContent(
            type="text",
            text=f"Error searching: {result.stderr}"
        )]


async def handle_show(args: dict) -> list[TextContent]:
    """Handle realign_show tool."""
    commit_hash = args.get("commit_hash")
    repo_path = args.get("repo_path", ".")
    session_path = args.get("session_path")
    format_type = args.get("format", "pretty")
    from_line = args.get("from_line")
    to_line = args.get("to_line")
    around_line = args.get("around_line")
    context = args.get("context", 5)
    first = args.get("first")
    last = args.get("last")

    # Build command
    cmd = ["realign", "show"]
    if session_path:
        cmd.extend(["--session", session_path])
    elif commit_hash:
        cmd.append(commit_hash)
    else:
        return [TextContent(
            type="text",
            text="Error: Must provide either commit_hash or session_path"
        )]

    cmd.extend(["--format", format_type])

    # Add range parameters
    if from_line is not None:
        cmd.extend(["--from", str(from_line)])
    if to_line is not None:
        cmd.extend(["--to", str(to_line)])
    if around_line is not None:
        cmd.extend(["--around", str(around_line)])
        if context != 5:  # Only add if not default
            cmd.extend(["--context", str(context)])
    if first is not None:
        cmd.extend(["--first", str(first)])
    if last is not None:
        cmd.extend(["--last", str(last)])

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return [TextContent(type="text", text=result.stdout)]
    else:
        return [TextContent(
            type="text",
            text=f"Error showing session: {result.stderr}"
        )]


async def handle_get_latest_session(args: dict) -> list[TextContent]:
    """Handle realign_get_latest_session tool."""
    from .claude_detector import find_claude_sessions_dir

    repo_path = args.get("repo_path", ".")
    config = ReAlignConfig.load()

    # Try Claude auto-detection first
    if config.auto_detect_claude:
        claude_dir = find_claude_sessions_dir(Path(repo_path))
        if claude_dir:
            # Find latest session in Claude directory
            session_files = sorted(
                claude_dir.glob("*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if session_files:
                return [TextContent(
                    type="text",
                    text=f"Latest Claude Code session: {session_files[0]}"
                )]

    # Fallback to configured history path
    history_path = config.expanded_local_history_path

    if not history_path.exists():
        return [TextContent(
            type="text",
            text=f"No sessions found. History path does not exist: {history_path}"
        )]

    # Find latest session file
    session_files = sorted(
        history_path.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if session_files:
        return [TextContent(
            type="text",
            text=f"Latest session: {session_files[0]}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"No session files found in {history_path}"
        )]


async def handle_commit(args: dict) -> list[TextContent]:
    """Handle realign_commit tool."""
    message = args["message"]
    repo_path = args.get("repo_path", ".")
    stage_all = args.get("all", False)
    amend = args.get("amend", False)
    no_edit = args.get("no_edit", False)

    # Check if ReAlign is initialized
    repo_path_obj = Path(repo_path).resolve()
    realign_dir = repo_path_obj / ".realign"

    if not realign_dir.exists():
        # Auto-initialize ReAlign before committing
        init_cmd = ["realign", "init", "--yes"]
        init_result = subprocess.run(
            init_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if init_result.returncode != 0:
            return [TextContent(
                type="text",
                text=f"❌ Failed to auto-initialize ReAlign\n\n{init_result.stdout + init_result.stderr}"
            )]

        # Inform user that auto-init happened
        init_output = f"🔧 Auto-initialized ReAlign in repository\n\n{init_result.stdout}\n"
    else:
        init_output = ""

    # Build command
    cmd = ["realign", "commit", "-m", message]

    if stage_all:
        cmd.append("-a")
    if amend:
        cmd.append("--amend")
    if no_edit:
        cmd.append("--no-edit")

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    if result.returncode == 0:
        return [TextContent(
            type="text",
            text=f"{init_output}✅ Commit created successfully\n\n{output}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"{init_output}❌ Failed to create commit\n\n{output}"
        )]


async def handle_version(args: dict) -> list[TextContent]:
    """Handle realign_version tool."""
    return [TextContent(
        type="text",
        text=f"ReAlign version {__version__}"
    )]


async def handle_auto_commit(args: dict) -> list[TextContent]:
    """Handle realign_auto_commit tool."""
    message = args.get("message")
    repo_path = args.get("repo_path", ".")

    # Build command
    cmd = ["realign", "auto-commit"]

    if message:
        cmd.extend(["-m", message])

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    if result.returncode == 0:
        return [TextContent(
            type="text",
            text=f"✅ Auto-commit successful\n\n{output}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"⚠️ Auto-commit completed with warnings\n\n{output}"
        )]


async def async_main():
    """Run the MCP server (async)."""
    print("[MCP Server] Starting ReAlign MCP server...", file=sys.stderr)

    # Detect repository path and start the watcher
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            repo_path = Path(result.stdout.strip())
            print(f"[MCP Server] Detected git repository: {repo_path}", file=sys.stderr)
            # Start the dialogue watcher in the background
            await start_watcher(repo_path)
        else:
            # Not in a git repo - use current directory
            # The watcher will auto-initialize git when needed
            repo_path = Path.cwd()
            print(f"[MCP Server] Not in git repo, using current directory: {repo_path}", file=sys.stderr)
            print(f"[MCP Server] Watcher will auto-initialize git when session changes detected", file=sys.stderr)
            await start_watcher(repo_path)
    except Exception as e:
        print(f"[MCP Server] Warning: Could not start watcher: {e}", file=sys.stderr)

    print("[MCP Server] MCP server ready", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server command."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
