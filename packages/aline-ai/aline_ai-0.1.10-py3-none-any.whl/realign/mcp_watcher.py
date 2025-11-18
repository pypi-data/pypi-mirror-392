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


# File-based logger for debugging when stderr is not visible
_log_file = None

def _log(msg: str):
    """Log to both stderr and a debug file."""
    global _log_file
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(f"[MCP Watcher] {msg}", file=sys.stderr)

    # Also write to file for debugging
    if _log_file is None:
        log_path = Path.home() / ".aline_watcher.log"
        try:
            _log_file = open(log_path, "a", buffering=1)  # Line buffered
            _log_file.write(f"\n{'='*60}\n")
            _log_file.write(f"[{timestamp}] MCP Watcher Started\n")
            _log_file.write(f"{'='*60}\n")
        except Exception:
            _log_file = False  # Mark as failed so we don't retry

    if _log_file and _log_file is not False:
        try:
            _log_file.write(full_msg + "\n")
            _log_file.flush()
        except Exception:
            pass


class DialogueWatcher:
    """Watch session files and auto-commit immediately after each user request completes."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path  # Default repo path (may be overridden per-session)
        self.config = ReAlignConfig.load()
        self.last_commit_time: Dict[str, float] = {}  # Track commit time per project
        self.last_session_sizes: Dict[str, int] = {}  # Track file sizes
        self.last_stop_reason_counts: Dict[str, int] = {}  # Track stop_reason counts per session
        self.min_commit_interval = 5.0  # Minimum 5 seconds between commits (cooldown)
        self.debounce_delay = 2.0  # Wait 2 seconds after file change to ensure turn is complete
        self.running = False
        self.pending_commit_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start watching session files."""
        if not self.config.mcp_auto_commit:
            _log("Auto-commit disabled in config")
            return

        self.running = True
        _log("Started watching for dialogue completion")
        _log(f"Mode: Per-request (triggers at end of each Claude response)")
        _log(f"Debounce: {self.debounce_delay}s, Cooldown: {self.min_commit_interval}s")
        _log(f"Home directory: {Path.home()}")
        _log(f"Current working directory: {Path.cwd()}")

        # Initialize baseline sizes and stop_reason counts
        self.last_session_sizes = self._get_session_sizes()
        self.last_stop_reason_counts = self._get_stop_reason_counts()

        # Log initial session files being monitored
        if self.last_session_sizes:
            _log(f"Monitoring {len(self.last_session_sizes)} session file(s):")
            for session_path in list(self.last_session_sizes.keys())[:5]:  # Show first 5
                _log(f"  - {session_path}")
            if len(self.last_session_sizes) > 5:
                _log(f"  ... and {len(self.last_session_sizes) - 5} more")
        else:
            claude_projects = Path.home() / ".claude" / "projects"
            _log(f"WARNING: No session files found in {claude_projects}")

        # Poll for file changes more frequently
        while self.running:
            try:
                await self.check_for_changes()
                await asyncio.sleep(0.5)  # Check every 0.5 seconds for responsiveness
            except Exception as e:
                _log(f"Error: {e}")
                await asyncio.sleep(1.0)

    async def stop(self):
        """Stop watching."""
        self.running = False
        if self.pending_commit_task:
            self.pending_commit_task.cancel()
        _log("Stopped")

    def _get_session_sizes(self) -> Dict[str, int]:
        """Get current sizes of all active session files (from all Claude projects)."""
        sizes = {}
        try:
            # Watch ALL Claude session files, not just one project
            claude_projects = Path.home() / ".claude" / "projects"
            if claude_projects.exists():
                for session_file in claude_projects.glob("*/*.jsonl"):
                    if session_file.exists():
                        sizes[str(session_file)] = session_file.stat().st_size
        except Exception as e:
            _log(f"Error getting session sizes: {e}")
        return sizes

    def _get_stop_reason_counts(self) -> Dict[str, int]:
        """Get current count of stop_reason entries in all active session files."""
        counts = {}
        try:
            # Watch ALL Claude session files
            claude_projects = Path.home() / ".claude" / "projects"
            if claude_projects.exists():
                for session_file in claude_projects.glob("*/*.jsonl"):
                    if session_file.exists():
                        counts[str(session_file)] = self._count_stop_reasons(session_file)
        except Exception as e:
            _log(f"Error getting stop_reason counts: {e}")
        return counts

    def _count_stop_reasons(self, session_file: Path) -> int:
        """
        Count the number of unique stop_reason='end_turn' entries in a session file.

        Deduplicates by message ID since Claude Code writes the same message multiple times
        (first with thinking, then with full content).
        """
        unique_message_ids = set()
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        message = data.get("message", {})
                        # Only count end_turn stop reasons (ignore tool_use, etc.)
                        if message.get("stop_reason") == "end_turn":
                            # Deduplicate by message ID to handle incremental writes
                            msg_id = message.get("id")
                            if msg_id:
                                unique_message_ids.add(msg_id)
                            else:
                                # If no message ID, count it anyway (shouldn't happen normally)
                                unique_message_ids.add(f"no_id_{len(unique_message_ids)}")
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            _log(f"Error counting stop_reasons in {session_file}: {e}")
        return len(unique_message_ids)

    async def check_for_changes(self):
        """Check if any session file has been modified."""
        try:
            current_sizes = self._get_session_sizes()

            # Debug: log if no sessions found (only once)
            if not current_sizes and not hasattr(self, '_no_session_warned'):
                print(f"[MCP Watcher] Warning: No active sessions found for repo: {self.repo_path}", file=sys.stderr)
                self._no_session_warned = True

            # Detect changed files
            changed_files = []
            for path, size in current_sizes.items():
                old_size = self.last_session_sizes.get(path, 0)
                if size > old_size:
                    changed_files.append(Path(path))
                    _log(f"Session file changed: {Path(path).name} ({old_size} -> {size} bytes)")

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
            _log(f"Error checking for changes: {e}")

    async def _debounced_commit(self, changed_files: list):
        """Wait for debounce period, then check if dialogue is complete and commit."""
        try:
            # Wait for debounce period
            await asyncio.sleep(self.debounce_delay)

            # Check if any of the changed files contains a complete dialogue turn
            for session_file in changed_files:
                if await self._check_if_turn_complete(session_file):
                    _log(f"Complete turn detected in {session_file.name}")

                    # Extract project path from session file's parent directory
                    project_path = self._get_project_path_from_session(session_file)
                    if project_path:
                        # Check cooldown for this specific project
                        current_time = time.time()
                        last_time = self.last_commit_time.get(str(project_path), 0)
                        if current_time - last_time < self.min_commit_interval:
                            _log(f"Skipping commit for {project_path} (cooldown)")
                            continue

                        await self._do_commit(project_path)
                    else:
                        _log(f"WARNING: Could not extract project path from {session_file}, skipping commit")

        except asyncio.CancelledError:
            # Task was cancelled because a newer change was detected
            pass
        except Exception as e:
            _log(f"Error in debounced commit: {e}")

    async def _check_if_turn_complete(self, session_file: Path) -> bool:
        """
        Check if the session file has at least 1 new stop_reason='end_turn' entry since last check.

        Each complete dialogue round in Claude Code has:
        1. User message (no stop_reason field)
        2. Assistant response with stop_reason: "end_turn"

        We deduplicate by message ID to handle incremental writes of the same message.
        Therefore, each request-response cycle produces 1 unique end_turn entry.
        """
        try:
            session_path = str(session_file)
            current_count = self._count_stop_reasons(session_file)
            last_count = self.last_stop_reason_counts.get(session_path, 0)

            new_stop_reasons = current_count - last_count

            # Commit after each complete assistant response (1 new end_turn)
            if new_stop_reasons >= 1:
                _log(f"Detected {new_stop_reasons} new end_turn entry(ies) in {session_file.name}")
                # Update baseline immediately to avoid double-counting
                self.last_stop_reason_counts[session_path] = current_count
                return True

            return False

        except Exception as e:
            _log(f"Error checking turn completion: {e}")
            return False

    def _get_project_path_from_session(self, session_file: Path) -> Optional[Path]:
        """
        Extract the actual project path from a Claude session file's location.

        Claude Code stores sessions in: ~/.claude/projects/-Users-username-path/session.jsonl
        The directory name encodes the project path with dashes replacing both slashes and underscores.
        This means we need to intelligently reconstruct the path by testing which separators work.
        """
        try:
            project_dir_name = session_file.parent.name
            _log(f"Extracting project path from: {project_dir_name}")

            if project_dir_name.startswith('-'):
                # Split into segments
                segments = project_dir_name[1:].split('-')
                _log(f"Path segments: {segments}")

                # Try to reconstruct the path by checking which combinations exist
                candidate_path = self._reconstruct_path_from_segments(segments)

                if candidate_path and candidate_path.exists():
                    _log(f"Project path exists: {candidate_path}")
                    return candidate_path
                else:
                    # Fallback: try simple replacement (for backward compatibility)
                    simple_path = Path('/' + project_dir_name[1:].replace('-', '/'))
                    if simple_path.exists():
                        _log(f"Project path exists (simple method): {simple_path}")
                        return simple_path
                    _log(f"WARNING: Could not find valid project path for: {project_dir_name}")
            else:
                _log(f"WARNING: Directory name doesn't start with '-': {project_dir_name}")
        except Exception as e:
            _log(f"Error extracting project path: {e}")
        return None

    def _reconstruct_path_from_segments(self, segments: list) -> Optional[Path]:
        """
        Reconstruct a file path from encoded segments.

        Claude Code encodes paths by replacing both '/' and '_' with '-'.
        This method tries to find the correct path by testing which separators
        produce valid paths.

        Strategy:
        1. Start from root '/'
        2. Build path incrementally, checking if each partial path exists
        3. When a segment doesn't match, try combining with next segment using '_' or '-'
        """
        if not segments:
            return None

        current_path = Path('/')
        i = 0

        while i < len(segments):
            segment = segments[i]

            # Try direct match first (segment is a directory/file name)
            test_path = current_path / segment
            if test_path.exists():
                current_path = test_path
                i += 1
                continue

            # If direct match fails, try combining with next segments using '_' or '-'
            found_match = False
            for lookahead in range(1, min(10, len(segments) - i)):  # Try up to 10 segments ahead
                # Try combining segments with underscores
                combined_underscore = '_'.join(segments[i:i+lookahead+1])
                test_path_underscore = current_path / combined_underscore

                # Try combining segments with hyphens
                combined_hyphen = '-'.join(segments[i:i+lookahead+1])
                test_path_hyphen = current_path / combined_hyphen

                # Try mixed combinations for longer paths
                if test_path_underscore.exists():
                    current_path = test_path_underscore
                    i += lookahead + 1
                    found_match = True
                    _log(f"Found match with underscores: {combined_underscore}")
                    break
                elif test_path_hyphen.exists():
                    current_path = test_path_hyphen
                    i += lookahead + 1
                    found_match = True
                    _log(f"Found match with hyphens: {combined_hyphen}")
                    break

            if not found_match:
                # If no match found, this might be the final segment (file or non-existent dir)
                # Just append remaining segments with '/' and check
                remaining = '/'.join(segments[i:])
                final_path = current_path / remaining
                if final_path.exists():
                    return final_path

                # Try treating remaining as underscore-joined
                remaining_underscore = '_'.join(segments[i:])
                final_path_underscore = current_path / remaining_underscore
                if final_path_underscore.exists():
                    return final_path_underscore

                # Nothing worked, return what we have
                _log(f"Could not match segment '{segment}' at path {current_path}")
                return None

        return current_path if current_path != Path('/') else None

    async def _do_commit(self, project_path: Path):
        """Perform the actual commit for a specific project."""
        try:
            # Generate commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"chore: Auto-commit MCP session ({timestamp})"

            _log(f"Attempting commit in {project_path} with message: {message}")

            # Use realign commit command with the specific project path
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_realign_commit,
                message,
                project_path
            )

            if result:
                _log(f"✓ Committed in {project_path}: {message}")
                self.last_commit_time[str(project_path)] = time.time()
                # Baseline counts already updated in _check_if_turn_complete()

        except Exception as e:
            _log(f"Error during commit: {e}")

    def _run_realign_commit(self, message: str, project_path: Path) -> bool:
        """
        Run aline commit command using Python functions directly.

        The command will:
        - Auto-initialize git and Aline if needed
        - Check for session changes (modified within last 5 minutes)
        - Create empty commit if only sessions changed
        - Return True if commit was created, False otherwise
        """
        try:
            from .commands.init import init_repository
            from .commands.commit import smart_commit

            # Check if Aline is initialized
            realign_dir = project_path / ".realign"

            if not realign_dir.exists():
                _log(f"Aline not initialized in {project_path}, initializing...")

                # Auto-initialize Aline (which also inits git if needed)
                init_result = init_repository(
                    repo_path=str(project_path),
                    auto_init_git=True,
                    skip_commit=False,
                )

                if not init_result.get("success"):
                    _log(f"Failed to initialize Aline: {init_result.get('message', 'Unknown error')}")
                    return False

                _log("✓ Aline initialized successfully")

            # Now run the commit with stage_all=True
            result = smart_commit(
                message=message,
                repo_path=str(project_path),
                stage_all=True,
                amend=False,
                no_edit=False,
            )

            # Check if commit was successful
            if result.get("success"):
                return True
            elif result.get("no_changes"):
                # No changes - this is expected, not an error
                return False
            else:
                # Log the error for debugging
                error_msg = result.get("message", "Unknown error")
                _log(f"Commit failed: {error_msg}")
                return False

        except Exception as e:
            _log(f"Commit error: {e}")
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
