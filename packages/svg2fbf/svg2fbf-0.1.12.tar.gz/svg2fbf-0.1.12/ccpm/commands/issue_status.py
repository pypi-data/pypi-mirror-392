#!/usr/bin/env python3
"""
CCPM Issue Status Command

Purpose: Show status of all active issue worktrees
Usage: python issue_status.py [--verbose]
Exit codes:
  0 - Success
  1 - Error occurred

Shows:
  - List of all active worktrees
  - Issue numbers and titles
  - Agent IDs and lock status
  - Branches and commit status
  - Uncommitted changes
  - Associated PRs
  - Stale lock detection

Example:
  python issue_status.py
  python issue_status.py --verbose

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import json
import subprocess
import os
import errno
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Try to import psutil, but make it optional
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

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


def run_git_command(args: List[str], cwd: Optional[Path] = None, check: bool = True) -> Optional[str]:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=check,
            cwd=cwd,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        if not check:
            return None
        raise
    except FileNotFoundError:
        print(f"{Colors.RED}❌ git is not installed{Colors.NC}")
        sys.exit(1)


def run_gh_command(args: List[str], check: bool = True) -> Optional[str]:
    """Run a GitHub CLI command and return output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=check,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return None  # gh not installed, skip gh features
    except subprocess.CalledProcessError:
        if not check:
            return None
        raise


def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is running (cross-platform)."""
    if HAS_PSUTIL:
        try:
            return psutil.pid_exists(pid)
        except Exception:
            pass  # Fall through to manual check

    # Manual cross-platform check
    try:
        # On Unix, sending signal 0 checks if process exists
        if hasattr(os, "kill"):
            try:
                os.kill(pid, 0)
                return True
            except OSError as e:
                return e.errno == errno.EPERM  # Process exists but no permission
        else:
            # Windows: use tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
    except Exception:
        return False


def read_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Read and parse a JSON file, return None on error."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return None


def get_worktrees(worktree_base: Path) -> List[Path]:
    """Find all issue worktrees."""
    if not worktree_base.exists():
        return []

    worktrees = []
    for item in worktree_base.iterdir():
        if item.is_dir() and item.name.startswith("issue-"):
            worktrees.append(item)

    return sorted(worktrees)


def check_git_status(worktree_dir: Path, verbose: bool) -> None:
    """Check and display git status for a worktree."""
    if not (worktree_dir / ".git").exists():
        print(f"{Colors.RED}⚠️  Not a valid git worktree{Colors.NC}")
        return

    # Current branch
    current_branch = run_git_command(["branch", "--show-current"], cwd=worktree_dir, check=False) or "unknown"
    print(f"{Colors.YELLOW}Current Branch:{Colors.NC} {current_branch}")

    # Check for uncommitted changes
    diff_result = subprocess.run(
        ["git", "diff", "--quiet"],
        cwd=worktree_dir,
        capture_output=True,
    )
    diff_cached_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=worktree_dir,
        capture_output=True,
    )

    has_changes = diff_result.returncode != 0 or diff_cached_result.returncode != 0

    if has_changes:
        print(f"{Colors.YELLOW}Uncommitted Changes:{Colors.NC} Yes")
        if verbose:
            print()
            status_output = run_git_command(["status", "--short"], cwd=worktree_dir)
            if status_output:
                print(status_output)
    else:
        print(f"{Colors.GREEN}Uncommitted Changes:{Colors.NC} No")

    # Check for unpushed commits
    has_upstream = (
        subprocess.run(
            ["git", "rev-parse", "@{u}"],
            cwd=worktree_dir,
            capture_output=True,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )

    if has_upstream:
        commits_ahead = run_git_command(["rev-list", "--count", "@{u}..HEAD"], cwd=worktree_dir, check=False) or "0"

        commits_ahead_int = int(commits_ahead)
        if commits_ahead_int > 0:
            print(f"{Colors.YELLOW}Unpushed Commits:{Colors.NC} {commits_ahead}")
            if verbose:
                print()
                log_output = run_git_command(["log", "--oneline", "@{u}..HEAD"], cwd=worktree_dir)
                if log_output:
                    print(log_output)
        else:
            print(f"{Colors.GREEN}Unpushed Commits:{Colors.NC} 0")
    else:
        print(f"{Colors.YELLOW}Upstream:{Colors.NC} Not set")

    # Last commit
    last_commit = run_git_command(["log", "-1", "--oneline"], cwd=worktree_dir, check=False) or "No commits"
    print(f"{Colors.YELLOW}Last Commit:{Colors.NC} {last_commit}")


def check_associated_prs(issue_number: str) -> None:
    """Check for PRs associated with an issue."""
    pr_output = run_gh_command(["pr", "list", "--search", f"in:title,body #{issue_number}", "--json", "number,title,state", "--jq", '.[] | "\\(.number): \\(.title) (\\(.state))"'], check=False)

    if pr_output is None:
        return  # gh not available

    if pr_output:
        print(f"{Colors.YELLOW}Associated PRs:{Colors.NC}")
        for pr_line in pr_output.split("\n"):
            if pr_line.strip():
                print(f"   {pr_line}")
    else:
        print(f"{Colors.YELLOW}Associated PRs:{Colors.NC} None")


def display_worktree_status(worktree_dir: Path, verbose: bool) -> Dict[str, int]:
    """Display status for a single worktree and return lock statistics."""
    issue_number = worktree_dir.name.replace("issue-", "")

    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}Issue #{issue_number}{Colors.NC}")
    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}")
    print()

    # Read metadata
    metadata_file = worktree_dir / ".agent-metadata.json"
    lock_file = worktree_dir / ".agent-lock"

    metadata = read_json_file(metadata_file)
    if metadata:
        issue_title = metadata.get("issue_title", "Unknown")
        target_branch = metadata.get("target_branch", "unknown")
        agent_id = metadata.get("agent_id", "unknown")
        created_at = metadata.get("created_at", "unknown")

        print(f"{Colors.YELLOW}Title:{Colors.NC} {issue_title}")
        print(f"{Colors.YELLOW}Branch:{Colors.NC} {target_branch}")
        print(f"{Colors.YELLOW}Agent:{Colors.NC} {agent_id}")
        print(f"{Colors.YELLOW}Created:{Colors.NC} {created_at}")
    else:
        print(f"{Colors.YELLOW}⚠️  Metadata file not found{Colors.NC}")

    # Check lock status
    print()
    lock_stats = {"active": 0, "stale": 0}

    lock_data = read_json_file(lock_file)
    if lock_data:
        lock_pid = lock_data.get("pid", 0)
        lock_agent = lock_data.get("agent_id", "unknown")
        lock_started = lock_data.get("started", "unknown")

        if is_process_running(lock_pid):
            print(f"{Colors.GREEN}🔒 Lock Status:{Colors.NC} Active")
            print(f"   Agent: {lock_agent}")
            print(f"   PID: {lock_pid}")
            print(f"   Started: {lock_started}")
            lock_stats["active"] = 1
        else:
            print(f"{Colors.RED}🔒 Lock Status:{Colors.NC} Stale (process not running)")
            print(f"   Agent: {lock_agent}")
            print(f"   PID: {lock_pid} (dead)")
            print(f"   Started: {lock_started}")
            print()
            print(f"{Colors.YELLOW}   Remove stale lock:{Colors.NC}")
            print(f"   {Colors.GREEN}rm {lock_file}{Colors.NC}")
            lock_stats["stale"] = 1
    else:
        print(f"{Colors.YELLOW}🔒 Lock Status:{Colors.NC} No lock (possibly finished or aborted)")

    # Git status
    print()
    check_git_status(worktree_dir, verbose)

    # Check for associated PRs
    print()
    check_associated_prs(issue_number)

    # Worktree path
    print()
    print(f"{Colors.YELLOW}Path:{Colors.NC} {worktree_dir}")
    print()

    return lock_stats


def display_summary(worktrees: List[Path], total_active_locks: int, total_stale_locks: int, config: Dict[str, str]) -> None:
    """Display summary information."""
    print(f"{Colors.BLUE}{'━' * 60}{Colors.NC}")
    print()
    print(f"{Colors.CYAN}Summary:{Colors.NC}")
    print(f"   Total worktrees: {len(worktrees)}")
    print(f"   Active locks: {total_active_locks}")

    if total_stale_locks > 0:
        print(f"   {Colors.RED}Stale locks: {total_stale_locks}{Colors.NC}")

    print()
    print(f"{Colors.BLUE}Available Commands:{Colors.NC}")
    print(f"   View detailed status: {Colors.GREEN}python ccpm/commands/issue_status.py --verbose{Colors.NC}")
    print(f"   Start new work: {Colors.GREEN}ccpm/commands/issue-start.sh <issue-number>{Colors.NC}")
    print(f"   Finish work: {Colors.GREEN}ccpm/commands/issue-finish.sh <issue-number>{Colors.NC}")
    print(f"   Abort work: {Colors.GREEN}ccpm/commands/issue-abort.sh <issue-number>{Colors.NC}")
    print()

    # Audit log info
    audit_log_dir = Path(config["audit_log_dir"])
    if audit_log_dir.exists():
        log_files = list(audit_log_dir.glob("*.json"))
        log_count = len(log_files)

        print(f"{Colors.CYAN}Audit Logs:{Colors.NC}")
        print(f"   Location: {audit_log_dir}")
        print(f"   Files: {log_count}")

        today = datetime.now().strftime("%Y-%m-%d")
        today_log = audit_log_dir / f"{today}.json"
        if today_log.exists():
            print(f"   View today's log: {Colors.GREEN}cat {today_log} | jq{Colors.NC}")
        print()


def show_issue_status(verbose: bool = False) -> None:
    """Main function to show issue status."""
    config = get_config()
    worktree_base = Path(config["worktree_base"])

    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║            📊 ACTIVE ISSUE WORKTREES STATUS               ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()

    # Check if worktree directory exists
    if not worktree_base.exists():
        print(f"{Colors.YELLOW}No worktrees found{Colors.NC}")
        print(f"   Directory does not exist: {worktree_base}")
        print()
        print("   Start new work with:")
        print(f"   {Colors.GREEN}ccpm/commands/issue-start.sh <issue-number>{Colors.NC}")
        return

    # Find all worktrees
    worktrees = get_worktrees(worktree_base)

    # Check if any worktrees found
    if not worktrees:
        print(f"{Colors.YELLOW}No active worktrees{Colors.NC}")
        print()
        print("   Start new work with:")
        print(f"   {Colors.GREEN}ccpm/commands/issue-start.sh <issue-number>{Colors.NC}")
        return

    print(f"{Colors.CYAN}Found {len(worktrees)} active worktree(s){Colors.NC}")
    print()

    # Process each worktree
    total_active_locks = 0
    total_stale_locks = 0

    for worktree_dir in worktrees:
        lock_stats = display_worktree_status(worktree_dir, verbose)
        total_active_locks += lock_stats["active"]
        total_stale_locks += lock_stats["stale"]

    # Display summary
    display_summary(worktrees, total_active_locks, total_stale_locks, config)


def main():
    """Main entry point."""
    Colors.strip_colors()

    verbose = "--verbose" in sys.argv

    try:
        show_issue_status(verbose)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
