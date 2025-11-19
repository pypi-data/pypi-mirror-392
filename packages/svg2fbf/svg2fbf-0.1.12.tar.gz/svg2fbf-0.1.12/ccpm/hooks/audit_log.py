#!/usr/bin/env python3
"""
Audit Logging for CCPM Agents

Purpose: Log all agent actions to JSON for accountability and debugging
Usage: python audit_log.py <action> [details...]
Exit codes:
  0 - Log entry created successfully
  1 - Error creating log entry

Actions logged:
  - worktree_create
  - worktree_remove
  - commit
  - push
  - pr_create
  - pr_update
  - branch_switch
  - file_modify
  - error

Log format: JSON lines in {audit_log_dir}/YYYY-MM-DD.json

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import json
import subprocess
import socket
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.project_config import get_config


# ANSI color codes (work on Windows 10+ and Unix)
class Colors:
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color

    @staticmethod
    def strip_colors():
        """Disable colors if output is not a TTY."""
        if not sys.stdout.isatty():
            Colors.RED = ""
            Colors.YELLOW = ""
            Colors.GREEN = ""
            Colors.BLUE = ""
            Colors.CYAN = ""
            Colors.NC = ""


def run_git_command(args: List[str]) -> Optional[str]:
    """Run a git command and return output, or None if it fails."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_git_context() -> Dict[str, str]:
    """Get git repository context."""
    return {
        "repository": run_git_command(["rev-parse", "--show-toplevel"]) or "unknown",
        "branch": run_git_command(["branch", "--show-current"]) or "unknown",
        "commit": run_git_command(["rev-parse", "HEAD"]) or "unknown",
    }


def get_agent_context() -> Dict[str, str]:
    """Get agent execution context."""
    return {
        "agent_id": os.environ.get("CCPM_AGENT_ID", "unknown"),
        "session_id": os.environ.get("CCPM_SESSION_ID", str(os.getpid())),
        "hostname": socket.gethostname(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME", "unknown"),
    }


def build_log_entry(action: str, args: List[str]) -> Dict[str, Any]:
    """
    Build a log entry for the specified action.

    Args:
        action: Action type (worktree_create, commit, etc.)
        args: Additional arguments specific to the action

    Returns:
        Dictionary representing the log entry
    """
    # Base entry with timestamp and context
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **get_agent_context(),
        "action": action,
        **get_git_context(),
    }

    # Add action-specific fields
    if action == "worktree_create":
        if len(args) >= 1:
            entry["worktree_path"] = args[0]
        if len(args) >= 2:
            entry["issue_number"] = args[1]

    elif action == "worktree_remove":
        if len(args) >= 1:
            entry["worktree_path"] = args[0]

    elif action == "commit":
        if len(args) >= 1:
            entry["commit_hash"] = args[0]
        if len(args) >= 2:
            entry["commit_message"] = args[1]
        if len(args) >= 3:
            # Parse files_changed as integer if it's numeric
            try:
                entry["files_changed"] = int(args[2])
            except (ValueError, TypeError):
                entry["files_changed"] = args[2]

    elif action == "push":
        entry["remote"] = args[0] if len(args) >= 1 else "origin"
        entry["ref"] = args[1] if len(args) >= 2 else entry["branch"]
        # Parse force as boolean
        if len(args) >= 3:
            entry["force_push"] = args[2].lower() in ("true", "1", "yes")
        else:
            entry["force_push"] = False

    elif action == "pr_create":
        if len(args) >= 1:
            entry["pr_number"] = args[0]
        if len(args) >= 2:
            entry["pr_title"] = args[1]
        if len(args) >= 3:
            entry["draft"] = args[2].lower() in ("true", "1", "yes")
        else:
            entry["draft"] = True

    elif action == "pr_update":
        if len(args) >= 1:
            entry["pr_number"] = args[0]
        if len(args) >= 2:
            entry["update_type"] = args[1]

    elif action == "branch_switch":
        if len(args) >= 1:
            entry["from_branch"] = args[0]
        if len(args) >= 2:
            entry["to_branch"] = args[1]

    elif action == "file_modify":
        if len(args) >= 1:
            entry["file_path"] = args[0]
        if len(args) >= 2:
            entry["operation"] = args[1]
        else:
            entry["operation"] = "modify"

    elif action == "error":
        if len(args) >= 1:
            entry["error_type"] = args[0]
        if len(args) >= 2:
            entry["error_message"] = args[1]
        if len(args) >= 3:
            entry["recovery_action"] = args[2]

    else:
        # Generic action with details
        if args:
            entry["details"] = " ".join(args)

    return entry


def write_log_entry(entry: Dict[str, Any], log_file: Path) -> None:
    """
    Write log entry to JSON Lines file.

    Args:
        entry: Log entry dictionary
        log_file: Path to log file
    """
    # Ensure parent directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Append entry as JSON line
    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")


def log_to_syslog(action: str, agent_id: str, session_id: str) -> None:
    """
    Log to system logger if available (Unix-like systems).

    Args:
        action: Action type
        agent_id: Agent identifier
        session_id: Session identifier
    """
    # Try to use logger command on Unix-like systems
    try:
        subprocess.run(
            ["logger", "-t", "ccpm-agent", "-p", "user.info", f"action={action} agent={agent_id} session={session_id}"],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        # logger not available (e.g., on Windows)
        pass


def audit_log(action: str, args: List[str]) -> None:
    """
    Log an audit entry.

    Args:
        action: Action type
        args: Action-specific arguments
    """
    config = get_config()
    log_dir = Path(config["audit_log_dir"])
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    # Build and write log entry
    entry = build_log_entry(action, args)
    write_log_entry(entry, log_file)

    # Also log to syslog if available
    log_to_syslog(action, entry["agent_id"], entry["session_id"])

    # Success feedback (minimal, for scripting)
    if sys.stdout.isatty():
        print(f"{Colors.GREEN}✓ Logged: {action}{Colors.NC}")


def main():
    """Main entry point."""
    Colors.strip_colors()

    # Parse arguments
    if len(sys.argv) < 2:
        print(f"{Colors.RED}❌ Error: Action argument required{Colors.NC}", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} <action> [details...]", file=sys.stderr)
        print("\nActions: worktree_create, worktree_remove, commit, push,", file=sys.stderr)
        print("         pr_create, pr_update, branch_switch, file_modify, error", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    args = sys.argv[2:]

    try:
        audit_log(action, args)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.NC}", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
