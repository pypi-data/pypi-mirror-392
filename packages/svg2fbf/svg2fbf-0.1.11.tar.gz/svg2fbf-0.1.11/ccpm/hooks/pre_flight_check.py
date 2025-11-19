#!/usr/bin/env python3
"""
Pre-Flight Safety Check for CCPM Agents

Purpose: Validate preconditions before agent starts work on an issue
Usage: python pre_flight_check.py <issue-number> [target-branch]
Exit codes:
  0 - All checks passed, safe to proceed
  1 - Check failed, cannot proceed

Checks performed:
  1. Issue exists and is assigned
  2. No conflicting agent lock exists
  3. Target branch is allowed (not master/main/review)
  4. No conflicting PRs for same issue
  5. Repository state is clean
  6. Target branch exists and is up-to-date

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

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
    """
    Run a git command and return output.

    Args:
        args: List of git command arguments (without 'git')
        cwd: Working directory for the command
        check: Whether to raise exception on error

    Returns:
        Command output as string, or None if command failed and check=False
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=check,
            cwd=str(cwd) if cwd else None,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if not check:
            return None
        print(f"{Colors.RED}❌ git command failed: {' '.join(args)}{Colors.NC}")
        print(f"{Colors.RED}   {e.stderr.strip()}{Colors.NC}")
        return None
    except FileNotFoundError:
        print(f"{Colors.RED}❌ git is not installed{Colors.NC}")
        sys.exit(1)


def run_gh_command(args: List[str], check: bool = True) -> Optional[str]:
    """
    Run a GitHub CLI command and return output.

    Args:
        args: List of gh command arguments (without 'gh')
        check: Whether to raise exception on error

    Returns:
        Command output as string, or None if command failed
    """
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=check,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return None  # gh not installed
    except subprocess.CalledProcessError:
        if not check:
            return None
        return None


def check_gh_available() -> bool:
    """Check if GitHub CLI is available."""
    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def get_repo_root() -> Path:
    """Get the repository root directory."""
    repo_root = run_git_command(["rev-parse", "--show-toplevel"])
    if not repo_root:
        print(f"{Colors.RED}❌ Not in a git repository{Colors.NC}")
        sys.exit(1)
    return Path(repo_root)


def check_issue_exists_and_assigned(issue_number: str) -> bool:
    """
    Check 1: Issue exists and is assigned.

    Args:
        issue_number: GitHub issue number

    Returns:
        True if check passed (warning only if not assigned)
    """
    print(f"{Colors.YELLOW}[1/6]{Colors.NC} Checking issue exists and is assigned...")

    if not check_gh_available():
        print(f"{Colors.YELLOW}   ⚠️  GitHub CLI not installed, skipping issue check{Colors.NC}")
        return True

    # Get issue info
    issue_info_str = run_gh_command(["issue", "view", issue_number, "--json", "number,title,state,assignees"], check=False)

    if not issue_info_str:
        print(f"{Colors.RED}   ✗ Issue #{issue_number} not found{Colors.NC}")
        print(f"   Run: gh issue view {issue_number}")
        return False

    try:
        issue_info = json.loads(issue_info_str)
    except json.JSONDecodeError:
        print(f"{Colors.RED}   ✗ Failed to parse issue information{Colors.NC}")
        return False

    # Check issue state
    issue_state = issue_info.get("state", "")
    if issue_state == "CLOSED":
        print(f"{Colors.RED}   ✗ Issue #{issue_number} is already closed{Colors.NC}")
        print("   Cannot work on closed issues")
        return False

    # Check if assigned
    assignees = issue_info.get("assignees", [])
    if len(assignees) == 0:
        print(f"{Colors.YELLOW}   ⚠️  Issue #{issue_number} is not assigned{Colors.NC}")
        print("   Consider assigning to yourself first:")
        print(f"   {Colors.GREEN}gh issue edit {issue_number} --add-assignee @me{Colors.NC}")
        # Warning only, not blocking
    else:
        assignee = assignees[0].get("login", "unknown")
        print(f"{Colors.GREEN}   ✓ Issue assigned to: {assignee}{Colors.NC}")

    return True


def check_no_conflicting_locks(lock_file: Path) -> bool:
    """
    Check 2: No conflicting agent lock exists.

    Args:
        lock_file: Path to the agent lock file

    Returns:
        True if no conflicting locks exist
    """
    print(f"{Colors.YELLOW}[2/6]{Colors.NC} Checking for conflicting agent locks...")

    if not lock_file.exists():
        print(f"{Colors.GREEN}   ✓ No conflicting locks{Colors.NC}")
        return True

    # Read lock info
    try:
        with open(lock_file, "r") as f:
            lock_data = json.load(f)

        agent_id = lock_data.get("agent_id", "unknown")
        lock_pid = lock_data.get("pid", 0)
        started = lock_data.get("started", "unknown")

        # Check if process still alive
        if is_process_running(lock_pid):
            print(f"{Colors.RED}   ✗ Another agent is currently working on this issue{Colors.NC}")
            print(f"   Agent ID: {agent_id}")
            print(f"   PID: {lock_pid}")
            print(f"   Started: {started}")
            print()
            print(f"   {Colors.YELLOW}Cannot proceed while another agent holds the lock{Colors.NC}")
            print()
            print("   If this is a stale lock (agent crashed):")
            print(f"   {Colors.GREEN}rm {lock_file}{Colors.NC}")
            return False
        else:
            print(f"{Colors.YELLOW}   ⚠️  Stale lock detected (process {lock_pid} not running){Colors.NC}")
            print("   Removing stale lock...")
            lock_file.unlink(missing_ok=True)
            print(f"{Colors.GREEN}   ✓ Stale lock removed{Colors.NC}")
            return True

    except (json.JSONDecodeError, IOError) as e:
        print(f"{Colors.YELLOW}   ⚠️  Invalid lock file, removing...{Colors.NC}")
        lock_file.unlink(missing_ok=True)
        print(f"{Colors.GREEN}   ✓ Invalid lock removed{Colors.NC}")
        return True


def is_process_running(pid: int) -> bool:
    """
    Check if a process is running.

    Args:
        pid: Process ID

    Returns:
        True if process is running
    """
    if pid == 0:
        return False

    import platform

    system = platform.system()

    try:
        if system == "Windows":
            # Windows: use tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
        else:
            # Unix-like: use ps
            result = subprocess.run(
                ["ps", "-p", str(pid)],
                capture_output=True,
            )
            return result.returncode == 0
    except Exception:
        return False


def check_target_branch_allowed(target_branch: str) -> bool:
    """
    Check 3: Target branch is allowed.

    Args:
        target_branch: Branch name to check

    Returns:
        True if branch is allowed
    """
    print(f"{Colors.YELLOW}[3/6]{Colors.NC} Validating target branch...")

    FORBIDDEN_BRANCHES = ["master", "main", "review"]
    if target_branch in FORBIDDEN_BRANCHES:
        print(f"{Colors.RED}   ✗ Cannot start work on protected branch: {target_branch}{Colors.NC}")
        print()
        print("   Agents are NOT allowed to work directly on:")
        print("   - master (stable releases)")
        print("   - main (protected default branch)")
        print("   - review (release candidates)")
        print()
        print(f"   {Colors.GREEN}Use dev or testing instead{Colors.NC}")
        return False

    ALLOWED_BRANCHES = ["dev", "testing"]
    branch_allowed = target_branch in ALLOWED_BRANCHES

    # Also allow hotfix branches
    if target_branch.startswith("hotfix/"):
        branch_allowed = True
        print(f"{Colors.YELLOW}   ⚠️  Working on hotfix branch (requires supervision){Colors.NC}")

    if not branch_allowed:
        print(f"{Colors.RED}   ✗ Invalid target branch: {target_branch}{Colors.NC}")
        print("   Allowed branches: dev, testing, hotfix/*")
        return False

    print(f"{Colors.GREEN}   ✓ Target branch allowed: {target_branch}{Colors.NC}")
    return True


def check_no_conflicting_prs(issue_number: str) -> bool:
    """
    Check 4: No conflicting PRs for same issue.

    Args:
        issue_number: GitHub issue number

    Returns:
        True (warning only, not blocking)
    """
    print(f"{Colors.YELLOW}[4/6]{Colors.NC} Checking for conflicting pull requests...")

    if not check_gh_available():
        print(f"{Colors.YELLOW}   ⚠️  GitHub CLI not installed, skipping PR check{Colors.NC}")
        return True

    # Search for PRs mentioning this issue
    pr_list_str = run_gh_command(["pr", "list", "--search", f"in:title,body #{issue_number}", "--json", "number"], check=False)

    if not pr_list_str:
        print(f"{Colors.GREEN}   ✓ No conflicting PRs found{Colors.NC}")
        return True

    try:
        pr_list = json.loads(pr_list_str)
        pr_count = len(pr_list)

        if pr_count > 0:
            print(f"{Colors.YELLOW}   ⚠️  Found {pr_count} existing PR(s) for issue #{issue_number}{Colors.NC}")

            # List PRs
            run_gh_command(["pr", "list", "--search", f"in:title,body #{issue_number}", "--json", "number,title,state,headRefName"], check=False)

            print()
            print(f"   {Colors.YELLOW}Proceed with caution:{Colors.NC}")
            print("   - You may be duplicating work")
            print("   - Consider coordinating with PR author")
            print("   - Or continue if you're updating an existing PR")
            # Warning only, not blocking
        else:
            print(f"{Colors.GREEN}   ✓ No conflicting PRs found{Colors.NC}")

    except json.JSONDecodeError:
        print(f"{Colors.YELLOW}   ⚠️  Failed to parse PR list{Colors.NC}")

    return True


def check_repository_state(repo_root: Path) -> bool:
    """
    Check 5: Repository state is clean.

    Args:
        repo_root: Repository root directory

    Returns:
        True (warning only, not blocking)
    """
    print(f"{Colors.YELLOW}[5/6]{Colors.NC} Checking repository state...")

    # Check for uncommitted changes
    diff_output = run_git_command(["diff", "--quiet"], cwd=repo_root, check=False)
    diff_cached_output = run_git_command(["diff", "--cached", "--quiet"], cwd=repo_root, check=False)

    # If either command returns non-zero (via check=False), there are changes
    has_changes = diff_output is None or diff_cached_output is None

    if has_changes:
        print(f"{Colors.YELLOW}   ⚠️  Main repository has uncommitted changes{Colors.NC}")
        print()
        status_output = run_git_command(["status", "--short"], cwd=repo_root)
        if status_output:
            print(status_output)
        print()
        print(f"   {Colors.YELLOW}This won't block worktree creation, but consider:{Colors.NC}")
        print(f"   - Committing changes: {Colors.GREEN}git add . && git commit{Colors.NC}")
        print(f"   - Stashing changes: {Colors.GREEN}git stash{Colors.NC}")
        # Warning only, not blocking
    else:
        print(f"{Colors.GREEN}   ✓ Repository state is clean{Colors.NC}")

    return True


def check_target_branch_status(target_branch: str, repo_root: Path) -> bool:
    """
    Check 6: Target branch exists and is up-to-date.

    Args:
        target_branch: Branch name to check
        repo_root: Repository root directory

    Returns:
        True if branch exists and is ready
    """
    print(f"{Colors.YELLOW}[6/6]{Colors.NC} Checking target branch status...")

    # Fetch latest
    print("   Fetching latest from origin...")
    run_git_command(["fetch", "origin", "--quiet"], cwd=repo_root, check=False)

    # Check if branch exists on origin
    branch_exists = run_git_command(["rev-parse", "--verify", f"origin/{target_branch}"], cwd=repo_root, check=False)

    if not branch_exists:
        print(f"{Colors.RED}   ✗ Branch {target_branch} does not exist on origin{Colors.NC}")
        print("   Available branches:")
        branches = run_git_command(["branch", "-r"], cwd=repo_root)
        if branches:
            for branch in branches.split("\n"):
                if "HEAD" not in branch:
                    print(f"     {branch.strip()}")
        return False

    # Check if local branch exists and is in sync
    local_exists = run_git_command(["rev-parse", "--verify", target_branch], cwd=repo_root, check=False)

    if local_exists:
        local_hash = run_git_command(["rev-parse", target_branch], cwd=repo_root)
        remote_hash = run_git_command(["rev-parse", f"origin/{target_branch}"], cwd=repo_root)

        if local_hash != remote_hash:
            print(f"{Colors.YELLOW}   ⚠️  Local {target_branch} branch is out of sync with origin{Colors.NC}")
            print("   Updating local branch...")
            run_git_command(["checkout", target_branch, "--quiet"], cwd=repo_root)
            run_git_command(["pull", "origin", target_branch, "--quiet"], cwd=repo_root)
            print(f"{Colors.GREEN}   ✓ Branch updated{Colors.NC}")
        else:
            print(f"{Colors.GREEN}   ✓ Branch is up-to-date{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  Local {target_branch} branch doesn't exist, will be created{Colors.NC}")

    return True


def print_header(issue_number: str, target_branch: str):
    """Print check header."""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║           🛫 PRE-FLIGHT SAFETY CHECK                      ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Issue:{Colors.NC} #{issue_number}")
    print(f"{Colors.BLUE}Target Branch:{Colors.NC} {target_branch}")
    print()


def print_success_summary(issue_number: str, target_branch: str, worktree_dir: Path):
    """Print success summary."""
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║              ✅ PRE-FLIGHT CHECK PASSED                   ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.GREEN}Safe to proceed with:{Colors.NC}")
    print(f"   Issue: #{issue_number}")
    print(f"   Branch: {target_branch}")
    print(f"   Worktree: {worktree_dir}")
    print()
    print(f"{Colors.BLUE}Next steps:{Colors.NC}")
    print(f"   1. Create worktree: {Colors.GREEN}git worktree add {worktree_dir} {target_branch}{Colors.NC}")
    print(f'   2. Create lock file: {Colors.GREEN}echo \'{{"agent_id":"..."}}\' > {worktree_dir / ".agent-lock"}{Colors.NC}')
    print("   3. Start work on issue")
    print()


def main():
    """Main entry point."""
    Colors.strip_colors()

    # Parse arguments
    if len(sys.argv) < 2:
        print(f"{Colors.RED}❌ ERROR: Issue number required{Colors.NC}")
        print(f"Usage: {sys.argv[0]} <issue-number> [target-branch]")
        sys.exit(1)

    issue_number = sys.argv[1]
    target_branch = sys.argv[2] if len(sys.argv) > 2 else "dev"

    # Get repository root
    repo_root = get_repo_root()

    # Get project configuration
    config = get_config()

    # Calculate paths
    worktree_dir = Path(config["worktree_base"]) / f"issue-{issue_number}"
    lock_file = worktree_dir / ".agent-lock"

    # Print header
    print_header(issue_number, target_branch)

    # Run all checks
    all_checks_passed = True

    try:
        # Check 1: Issue exists and is assigned
        if not check_issue_exists_and_assigned(issue_number):
            all_checks_passed = False

        # Check 2: No conflicting agent locks
        if not check_no_conflicting_locks(lock_file):
            all_checks_passed = False

        # Check 3: Target branch is allowed
        if not check_target_branch_allowed(target_branch):
            all_checks_passed = False

        # Check 4: No conflicting PRs (warning only)
        check_no_conflicting_prs(issue_number)

        # Check 5: Repository state is clean (warning only)
        check_repository_state(repo_root)

        # Check 6: Target branch exists and is up-to-date
        if not check_target_branch_status(target_branch, repo_root):
            all_checks_passed = False

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.NC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Print result
    if all_checks_passed:
        print_success_summary(issue_number, target_branch, worktree_dir)
        sys.exit(0)
    else:
        print()
        print(f"{Colors.RED}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.RED}║              ❌ PRE-FLIGHT CHECK FAILED                   ║{Colors.NC}")
        print(f"{Colors.RED}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
        print()
        print(f"{Colors.RED}Cannot proceed with issue #{issue_number}{Colors.NC}")
        print("Fix the issues above and try again")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
