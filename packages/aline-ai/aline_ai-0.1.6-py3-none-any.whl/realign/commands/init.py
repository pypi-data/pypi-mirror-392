"""ReAlign init command - Initialize ReAlign in a git repository."""

import os
import subprocess
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import typer
from rich.console import Console
from rich.prompt import Confirm

from ..config import ReAlignConfig, get_default_config_content

console = Console()


def init_repository(
    repo_path: str = ".",
    auto_init_git: bool = True,
    skip_commit: bool = False,
) -> Dict[str, Any]:
    """
    Core initialization logic (non-interactive).

    Args:
        repo_path: Path to the repository to initialize
        auto_init_git: Automatically initialize git repo if not exists
        skip_commit: Skip auto-commit of hooks

    Returns:
        Dictionary with initialization results and metadata
    """
    result = {
        "success": False,
        "repo_path": None,
        "repo_root": None,
        "realign_dir": None,
        "hooks_created": [],
        "config_path": None,
        "history_dir": None,
        "git_initialized": False,
        "message": "",
        "errors": [],
    }

    # Change to target directory
    original_dir = os.getcwd()
    try:
        os.chdir(repo_path)
        result["repo_path"] = os.getcwd()
    except Exception as e:
        result["errors"].append(f"Failed to change to directory {repo_path}: {e}")
        result["message"] = "Failed to access target directory"
        return result
    try:
        # Check if we're in a git repository
        is_git_repo = True
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            is_git_repo = False

        # If not a git repo, auto-initialize if allowed
        if not is_git_repo:
            if auto_init_git:
                try:
                    subprocess.run(["git", "init"], check=True, capture_output=True)
                    result["git_initialized"] = True
                except subprocess.CalledProcessError as e:
                    result["errors"].append(f"Failed to initialize git repository: {e}")
                    result["message"] = "Git initialization failed"
                    return result
            else:
                result["errors"].append("Not in a git repository and auto_init_git=False")
                result["message"] = "Not a git repository"
                return result

        repo_root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        result["repo_root"] = str(repo_root)

        # Create directory structure
        realign_dir = repo_root / ".realign"
        hooks_dir = realign_dir / "hooks"
        sessions_dir = realign_dir / "sessions"
        result["realign_dir"] = str(realign_dir)

        for directory in [realign_dir, hooks_dir, sessions_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Install pre-commit hook
        pre_commit_path = hooks_dir / "pre-commit"
        if not pre_commit_path.exists():
            pre_commit_content = get_pre_commit_hook()
            pre_commit_path.write_text(pre_commit_content, encoding="utf-8")
            pre_commit_path.chmod(0o755)
            result["hooks_created"].append("pre-commit")

        # Install prepare-commit-msg hook
        hook_path = hooks_dir / "prepare-commit-msg"
        if not hook_path.exists():
            hook_content = get_prepare_commit_msg_hook()
            hook_path.write_text(hook_content, encoding="utf-8")
            hook_path.chmod(0o755)
            result["hooks_created"].append("prepare-commit-msg")

        # Create .gitignore for sessions (optional - commented out for MVP)
        gitignore_path = realign_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("# Uncomment to ignore session files\n# sessions/\n", encoding="utf-8")

        # Backup and set core.hooksPath
        backup_file = realign_dir / "backup_hook_config.yaml"
        current_hooks_path = subprocess.run(
            ["git", "config", "--local", "core.hooksPath"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

        if current_hooks_path and current_hooks_path != ".realign/hooks":
            # Backup old configuration
            backup_data = {
                "original_hooks_path": current_hooks_path,
                "backup_timestamp": subprocess.run(
                    ["date", "+%Y-%m-%d %H:%M:%S"],
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.strip(),
            }
            with open(backup_file, "w", encoding="utf-8") as f:
                yaml.dump(backup_data, f)

        # Set new hooks path
        subprocess.run(
            ["git", "config", "--local", "core.hooksPath", ".realign/hooks"],
            check=True,
        )

        # Initialize global config if not exists
        global_config_path = Path.home() / ".config" / "realign" / "config.yaml"
        if not global_config_path.exists():
            global_config_path.parent.mkdir(parents=True, exist_ok=True)
            global_config_path.write_text(get_default_config_content(), encoding="utf-8")
        result["config_path"] = str(global_config_path)

        # Create local history directory
        config = ReAlignConfig.load()
        history_dir = config.expanded_local_history_path
        history_dir.mkdir(parents=True, exist_ok=True)
        result["history_dir"] = str(history_dir)

        # Add hooks to git (optional commit)
        if not skip_commit:
            try:
                subprocess.run(["git", "add", ".realign/hooks/prepare-commit-msg"], check=True)
                # Try to commit (may fail if no changes, which is fine)
                commit_result = subprocess.run(
                    ["git", "commit", "-m", "chore(realign): add prepare-commit-msg hook", "--no-verify"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                result["committed"] = commit_result.returncode == 0
            except subprocess.CalledProcessError:
                result["committed"] = False

        result["success"] = True
        result["message"] = "ReAlign initialized successfully"

    except Exception as e:
        result["errors"].append(f"Initialization failed: {e}")
        result["message"] = f"Failed to initialize: {e}"
    finally:
        # Restore original directory
        os.chdir(original_dir)

    return result


def init_command(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts (deprecated, now default)"),
    skip_commit: bool = typer.Option(False, "--skip-commit", help="Skip auto-commit of hooks"),
):
    """Initialize ReAlign in the current git repository."""
    # Call the core function
    result = init_repository(
        repo_path=".",
        auto_init_git=True,
        skip_commit=skip_commit,
    )

    # Print detailed results
    console.print("\n[bold blue]═══ ReAlign Initialization ═══[/bold blue]\n")

    if result["success"]:
        console.print("[bold green]✓ Status: SUCCESS[/bold green]\n")
    else:
        console.print("[bold red]✗ Status: FAILED[/bold red]\n")

    # Print all parameters and results
    console.print("[bold]Parameters:[/bold]")
    console.print(f"  Repository Path: [cyan]{result.get('repo_path', 'N/A')}[/cyan]")
    console.print(f"  Repository Root: [cyan]{result.get('repo_root', 'N/A')}[/cyan]")
    console.print(f"  ReAlign Directory: [cyan]{result.get('realign_dir', 'N/A')}[/cyan]")
    console.print(f"  Config Path: [cyan]{result.get('config_path', 'N/A')}[/cyan]")
    console.print(f"  History Directory: [cyan]{result.get('history_dir', 'N/A')}[/cyan]")
    console.print(f"  Git Initialized: [cyan]{result.get('git_initialized', False)}[/cyan]")
    console.print(f"  Skip Commit: [cyan]{skip_commit}[/cyan]")
    console.print(f"  Hooks Created: [cyan]{', '.join(result.get('hooks_created', [])) or 'None'}[/cyan]")
    console.print(f"  Auto-committed: [cyan]{result.get('committed', False)}[/cyan]")

    if result.get("errors"):
        console.print("\n[bold red]Errors:[/bold red]")
        for error in result["errors"]:
            console.print(f"  • {error}", style="red")

    console.print(f"\n[bold]Result:[/bold] {result['message']}\n")

    if result["success"]:
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Ensure your agent saves chat histories to:", style="dim")
        console.print(f"     {result['history_dir']}", style="cyan")
        console.print("  2. Make commits as usual - ReAlign will automatically track sessions", style="dim")
        console.print("  3. Search sessions with: [cyan]realign search <keyword>[/cyan]", style="dim")
        console.print("  4. View sessions with: [cyan]realign show <commit>[/cyan]", style="dim")
    else:
        raise typer.Exit(1)


def get_pre_commit_hook() -> str:
    """Get the pre-commit hook script content."""
    return '''#!/bin/bash
# ReAlign pre-commit hook
# Finds and stages agent session files before commit

# 1. Try to find realign-hook-pre-commit in PATH first (pipx/pip installations)
if command -v realign-hook-pre-commit >/dev/null 2>&1; then
    VERSION=$(realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign pre-commit hook (dev-$VERSION)" >&2
    exec realign-hook-pre-commit "$@"
fi

# 2. Try using uvx (for MCP installations where command is in uvx cache)
if command -v uvx >/dev/null 2>&1; then
    VERSION=$(uvx --from realign-git realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign pre-commit hook (release-$VERSION)" >&2
    exec uvx --from realign-git realign-hook-pre-commit "$@"
fi

# If all else fails, print an error
echo "Error: Cannot find realign. Please ensure it's installed:" >&2
echo "  - For CLI: pipx install realign-git" >&2
echo "  - For MCP: Ensure uvx is available" >&2
exit 1
'''


def get_prepare_commit_msg_hook() -> str:
    """Get the prepare-commit-msg hook script content."""
    return '''#!/bin/bash
# ReAlign prepare-commit-msg hook
# Adds agent session metadata to commit messages

COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Skip for merge, squash, and commit --amend (but allow message and template)
if [ "$COMMIT_SOURCE" = "merge" ] || [ "$COMMIT_SOURCE" = "squash" ] || [ "$COMMIT_SOURCE" = "commit" ]; then
    exit 0
fi

# 1. Try to find realign-hook-prepare-commit-msg in PATH first (pipx/pip installations)
if command -v realign-hook-prepare-commit-msg >/dev/null 2>&1; then
    VERSION=$(realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign prepare-commit-msg hook (dev-$VERSION)" >&2
    exec realign-hook-prepare-commit-msg "$@"
fi

# 2. Try using uvx (for MCP installations where command is in uvx cache)
if command -v uvx >/dev/null 2>&1; then
    VERSION=$(uvx --from realign-git realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign prepare-commit-msg hook (release-$VERSION)" >&2
    exec uvx --from realign-git realign-hook-prepare-commit-msg "$@"
fi

# If all else fails, print an error
echo "Error: Cannot find realign. Please ensure it's installed:" >&2
echo "  - For CLI: pipx install realign-git" >&2
echo "  - For MCP: Ensure uvx is available" >&2
exit 1
'''


if __name__ == "__main__":
    typer.run(init_command)
