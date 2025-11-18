#!/usr/bin/env python3
"""Aline MCP Server - AI Agent Chat Session Tracker via Model Context Protocol."""

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
app = Server("aline")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Aline tools."""
    return [
        Tool(
            name="aline_init",
            description=(
                "Initialize Aline in a directory to enable AI conversation tracking. "
                "This command automatically sets up the workspace and configures session tracking. "
                "Use this to start tracking AI conversations in your project."
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
            name="aline_search",
            description=(
                "Search through AI agent chat sessions. "
                "Finds sessions with matching keywords in session content. "
                "Returns session information and optionally full content. "
                "Can search in sessions only or include metadata."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for in sessions",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to workspace (default: current directory)",
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
                        "description": "Search only in session files. Useful for finding topics discussed in historical conversations.",
                        "default": False,
                    },
                    "commits_only": {
                        "type": "boolean",
                        "description": "Search only in metadata, not session files.",
                        "default": False,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="aline_show",
            description=(
                "Display an AI agent chat session. "
                "Supports navigation through the session with line ranges. "
                "Use aline_search first to find matching lines, then use this tool to view context around those lines."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "commit_hash": {
                        "type": "string",
                        "description": "Session identifier (full or short)",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to workspace (default: current directory)",
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
            name="aline_get_latest_session",
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
                        "description": "Path to workspace (for Claude auto-detection)",
                    },
                },
            },
        ),
        Tool(
            name="aline_version",
            description=(
                f"Get the current version of Aline ({__version__}). "
                "Aline is a tool that tracks and preserves AI agent chat sessions."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""

    try:
        # Execute the tool
        if name == "aline_init":
            result = await handle_init(arguments)
        elif name == "aline_search":
            result = await handle_search(arguments)
        elif name == "aline_show":
            result = await handle_show(arguments)
        elif name == "aline_get_latest_session":
            result = await handle_get_latest_session(arguments)
        elif name == "aline_version":
            result = await handle_version(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return result

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_init(args: dict) -> list[TextContent]:
    """Handle aline_init tool."""
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
            "✅ Aline initialized successfully\n",
            "Parameters:",
            f"  • Workspace Path: {result.get('repo_path', 'N/A')}",
            f"  • Workspace Root: {result.get('repo_root', 'N/A')}",
            f"  • Aline Directory: {result.get('realign_dir', 'N/A')}",
            f"  • Config Path: {result.get('config_path', 'N/A')}",
            f"  • History Directory: {result.get('history_dir', 'N/A')}",
            f"  • Initialized: {result.get('git_initialized', False)}",
            f"  • Hooks Created: {', '.join(result.get('hooks_created', [])) or 'None'}",
            f"  • Auto-committed: {result.get('committed', False)}",
            "",
            "Aline is now tracking your AI conversations automatically.",
            "Use aline_search to find past discussions.",
        ]
        return [TextContent(type="text", text="\n".join(output_lines))]
    else:
        error_lines = [
            "❌ Failed to initialize Aline\n",
            f"Error: {result['message']}",
        ]
        if result.get("errors"):
            error_lines.append("\nDetails:")
            for error in result["errors"]:
                error_lines.append(f"  • {error}")
        return [TextContent(type="text", text="\n".join(error_lines))]


async def handle_search(args: dict) -> list[TextContent]:
    """Handle aline_search tool."""
    keyword = args["keyword"]
    repo_path = args.get("repo_path", ".")
    show_session = args.get("show_session", False)
    max_results = args.get("max_results", 20)
    session_only = args.get("session_only", False)
    commits_only = args.get("commits_only", False)

    # Build command
    cmd = ["aline", "search", keyword, "--max", str(max_results)]
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
    """Handle aline_show tool."""
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
    cmd = ["aline", "show"]
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
    """Handle aline_get_latest_session tool."""
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


async def handle_version(args: dict) -> list[TextContent]:
    """Handle aline_version tool."""
    return [TextContent(
        type="text",
        text=f"Aline version {__version__}"
    )]


async def async_main():
    """Run the MCP server (async)."""
    print("[MCP Server] Starting Aline MCP server...", file=sys.stderr)
    print(f"[MCP Server] Current working directory: {Path.cwd()}", file=sys.stderr)

    # Detect workspace path and start the watcher
    # Try multiple methods since MCP server may run in different context
    repo_path = None

    try:
        # Method 1: Try git rev-parse from current directory
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            repo_path = Path(result.stdout.strip())
            print(f"[MCP Server] Detected workspace from git: {repo_path}", file=sys.stderr)
        else:
            print(f"[MCP Server] Not in git repo (cwd: {Path.cwd()})", file=sys.stderr)

        # Method 2: If not in git repo, try to find from Claude session files
        if not repo_path:
            claude_projects = Path.home() / ".claude" / "projects"
            print(f"[MCP Server] Checking Claude projects at: {claude_projects}", file=sys.stderr)
            if claude_projects.exists():
                # Find most recently modified session file
                session_files = list(claude_projects.glob("*/*.jsonl"))
                print(f"[MCP Server] Found {len(session_files)} Claude session files", file=sys.stderr)
                if session_files:
                    # Sort by modification time, newest first
                    session_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    print(f"[MCP Server] Most recent session: {session_files[0]}", file=sys.stderr)
                    # Extract project path from directory name
                    # Format: -Users-jundewu-Downloads-code-noclue -> /Users/jundewu/Downloads/code/noclue
                    project_dir_name = session_files[0].parent.name
                    print(f"[MCP Server] Project dir name: {project_dir_name}", file=sys.stderr)
                    if project_dir_name.startswith('-'):
                        # Convert back to path: -Users-foo-bar -> /Users/foo/bar
                        # Note: underscores were also replaced with dashes, but we can't distinguish
                        # So we just replace dashes with slashes
                        path_str = '/' + project_dir_name[1:].replace('-', '/')
                        candidate_path = Path(path_str)
                        print(f"[MCP Server] Candidate path: {candidate_path}, exists: {candidate_path.exists()}", file=sys.stderr)
                        if candidate_path.exists():
                            repo_path = candidate_path
                            print(f"[MCP Server] Detected workspace from Claude session: {repo_path}", file=sys.stderr)

        # Method 3: Fallback to current directory
        if not repo_path:
            repo_path = Path.cwd()
            print(f"[MCP Server] Using current directory: {repo_path}", file=sys.stderr)

        # Start the watcher
        print(f"[MCP Server] Starting watcher for: {repo_path}", file=sys.stderr)
        await start_watcher(repo_path)

    except Exception as e:
        print(f"[MCP Server] Warning: Could not start watcher: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

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
