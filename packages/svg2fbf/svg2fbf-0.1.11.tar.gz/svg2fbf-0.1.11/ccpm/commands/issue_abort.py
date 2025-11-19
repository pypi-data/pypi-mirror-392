#!/usr/bin/env python3
"""
CCPM Issue Abort Command

Purpose: Abort work on issue and cleanup worktree
Usage: python issue_abort.py <issue-number> [--force]
Exit codes:
  0 - Work aborted successfully
  1 - Error occurred

Steps:
  1. Validate worktree exists
  2. Show uncommitted changes (if any)
  3. Confirm abort (unless --force)
  4. Remove agent lock
  5. Remove worktree
  6. Log action

Example:
  python issue_abort.py 123
  python issue_abort.py 123 --force  # Skip confirmation

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import json
import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.project_config import get_config


# ANSI color codes (work on Windows 10+ and Unix)
class Colors:
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color

    @staticmethod
    def strip_colors():
        """Disable colors if output is not a TTY."""
        if not sys.stdout.isatty():
            Colors.RED = ""
            Colors.YELLOW = ""
            Colors.GREEN = ""
            Colors.BLUE = ""
            Colors.NC = ""


def run_command(args: list[str], cwd: Optional[Path] = None, check: bool = True, capture: bool = True) -> Tuple[int, str, str]:
    """
    Run a command and return (returncode, stdout, stderr).

    Args:
        args: Command and arguments as list
        cwd: Working directory for command
        check: If True, raise exception on non-zero exit
        capture: If True, capture output; otherwise print to console

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    try:
        if capture:
            result = subprocess.run(
                args,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(
                args,
                cwd=cwd,
                check=check,
            )
            return result.returncode, "", ""
    except subprocess.CalledProcessError as e:
        if not check:
            return e.returncode, e.stdout if e.stdout else "", e.stderr if e.stderr else ""
        raise
    except FileNotFoundError as e:
        print(f"{Colors.RED}❌ Command not found: {args[0]}{Colors.NC}")
        print(f"Error: {e}")
        sys.exit(1)


def get_repo_root() -> Path:
    """Get the git repository root directory."""
    returncode, stdout, stderr = run_command(["git", "rev-parse", "--show-toplevel"])
    if returncode != 0:
        print(f"{Colors.RED}❌ Not in a git repository{Colors.NC}")
        sys.exit(1)
    return Path(stdout.strip())


def check_uncommitted_changes(worktree_dir: Path) -> bool:
    """
    Check for uncommitted changes in the worktree.

    Returns:
        True if there are uncommitted changes, False otherwise
    """
    # Check unstaged changes
    returncode1, _, _ = run_command(["git", "diff", "--quiet"], cwd=worktree_dir, check=False)
    # Check staged changes
    returncode2, _, _ = run_command(["git", "diff", "--cached", "--quiet"], cwd=worktree_dir, check=False)

    return returncode1 != 0 or returncode2 != 0


def get_unpushed_commits(worktree_dir: Path) -> int:
    """
    Get the count of unpushed commits.

    Returns:
        Number of unpushed commits, or 0 if no upstream or error
    """
    # Check if upstream exists
    returncode, _, _ = run_command(["git", "rev-parse", "@{u}"], cwd=worktree_dir, check=False)

    if returncode != 0:
        return 0

    # Count unpushed commits
    returncode, stdout, _ = run_command(["git", "rev-list", "--count", "@{u}..HEAD"], cwd=worktree_dir, check=False)

    if returncode != 0:
        return 0

    try:
        return int(stdout.strip())
    except ValueError:
        return 0


def read_metadata(metadata_file: Path) -> Tuple[str, str]:
    """
    Read agent metadata from JSON file.

    Returns:
        Tuple of (agent_id, target_branch)
    """
    if not metadata_file.exists():
        return "unknown", "unknown"

    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            return metadata.get("agent_id", "unknown"), metadata.get("target_branch", "unknown")
    except (json.JSONDecodeError, IOError):
        return "unknown", "unknown"


def confirm_abort() -> bool:
    """
    Ask user to confirm abort action.

    Returns:
        True if user confirms, False otherwise
    """
    try:
        response = input("Are you sure you want to abort? (yes/no): ").strip().lower()
        print()
        return response == "yes"
    except EOFError:
        # Handle non-interactive terminals
        print("no")
        print()
        return False


def abort_issue(issue_number: str, force: bool = False) -> None:
    """
    Abort work on an issue and cleanup worktree.

    Args:
        issue_number: The issue number to abort
        force: If True, skip confirmation prompt
    """
    config = get_config()

    # Paths
    repo_root = get_repo_root()
    worktree_base = Path.home() / ".cache" / "svg2fbf-worktrees"
    worktree_dir = worktree_base / f"issue-{issue_number}"
    lock_file = worktree_dir / ".agent-lock"
    metadata_file = worktree_dir / ".agent-metadata.json"
    ccpm_dir = Path(__file__).parent.parent

    # Header
    print(f"{Colors.YELLOW}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.YELLOW}║              ⚠️  ABORTING WORK ON ISSUE                   ║{Colors.NC}")
    print(f"{Colors.YELLOW}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}Issue:{Colors.NC} #{issue_number}")
    print()

    # ============================================================================
    # Step 1: Validate worktree exists
    # ============================================================================
    print(f"{Colors.YELLOW}Step 1/6:{Colors.NC} Validating worktree...")

    if not worktree_dir.exists() or not worktree_dir.is_dir():
        print(f"{Colors.RED}❌ Worktree not found: {worktree_dir}{Colors.NC}")
        print("   Use issue-status.sh to check active worktrees")
        sys.exit(1)

    # Read metadata
    agent_id, target_branch = read_metadata(metadata_file)

    print(f"{Colors.GREEN}   ✓ Worktree found{Colors.NC}")
    print(f"     Path: {worktree_dir}")
    print(f"     Branch: {target_branch}")
    print(f"     Agent: {agent_id}")

    # ============================================================================
    # Step 2: Check for uncommitted changes
    # ============================================================================
    print(f"{Colors.YELLOW}Step 2/6:{Colors.NC} Checking for uncommitted changes...")

    has_changes = check_uncommitted_changes(worktree_dir)

    if has_changes:
        print(f"{Colors.YELLOW}   ⚠️  Uncommitted changes detected:{Colors.NC}")
        print()
        run_command(["git", "status", "--short"], cwd=worktree_dir, capture=False)
        print()

    # Check for unpushed commits
    unpushed_commits = get_unpushed_commits(worktree_dir)

    if unpushed_commits > 0:
        print(f"{Colors.YELLOW}   ⚠️  {unpushed_commits} unpushed commit(s):{Colors.NC}")
        print()
        run_command(["git", "log", "--oneline", "@{u}..HEAD"], cwd=worktree_dir, capture=False)
        print()

    if not has_changes and unpushed_commits == 0:
        print(f"{Colors.GREEN}   ✓ No uncommitted changes or unpushed commits{Colors.NC}")

    # ============================================================================
    # Step 3: Confirm abort (unless --force)
    # ============================================================================
    if not force:
        print(f"{Colors.YELLOW}Step 3/6:{Colors.NC} Confirmation required...")
        print()
        print(f"{Colors.RED}⚠️  WARNING: This will:{Colors.NC}")
        print("   - Discard all uncommitted changes")
        if unpushed_commits > 0:
            print(f"   - Lose {unpushed_commits} unpushed commit(s)")
        print("   - Remove the worktree")
        print("   - Cannot be undone")
        print()

        if not confirm_abort():
            print(f"{Colors.YELLOW}Abort cancelled{Colors.NC}")
            print()
            print("To proceed with abort:")
            print(f"  {Colors.GREEN}python {Path(__file__).name} {issue_number} --force{Colors.NC}")
            sys.exit(0)
    else:
        print(f"{Colors.YELLOW}Step 3/6:{Colors.NC} Skipping confirmation (--force flag)")

    # ============================================================================
    # Step 4: Remove agent lock
    # ============================================================================
    print(f"{Colors.YELLOW}Step 4/6:{Colors.NC} Removing agent lock...")

    if lock_file.exists():
        try:
            lock_file.unlink()
            print(f"{Colors.GREEN}   ✓ Lock removed{Colors.NC}")
        except OSError as e:
            print(f"{Colors.YELLOW}   ⚠️  Failed to remove lock: {e}{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  Lock file not found (may have been already removed){Colors.NC}")

    # ============================================================================
    # Step 5: Remove worktree
    # ============================================================================
    print(f"{Colors.YELLOW}Step 5/6:{Colors.NC} Removing worktree...")

    returncode, stdout, stderr = run_command(["git", "worktree", "remove", str(worktree_dir), "--force"], cwd=repo_root, check=False)

    if returncode == 0:
        print(f"{Colors.GREEN}   ✓ Worktree removed{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ Failed to remove worktree{Colors.NC}")
        print(f"   Try manually: {Colors.GREEN}git worktree remove {worktree_dir} --force{Colors.NC}")
        if stderr:
            print(f"   Error: {stderr}")
        sys.exit(1)

    # ============================================================================
    # Step 6: Log action
    # ============================================================================
    print(f"{Colors.YELLOW}Step 6/6:{Colors.NC} Logging abort action...")

    audit_log_script = ccpm_dir / "hooks" / "audit-log.sh"

    if audit_log_script.exists() and os.access(audit_log_script, os.X_OK):
        env = os.environ.copy()
        env["CCPM_AGENT_ID"] = agent_id
        env["CCPM_SESSION_ID"] = str(os.getpid())

        returncode, _, _ = run_command([str(audit_log_script), "worktree_remove", str(worktree_dir)], check=False)

        if returncode == 0:
            print(f"{Colors.GREEN}   ✓ Action logged{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}   ⚠️  Failed to log action{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  Audit log script not found, skipping{Colors.NC}")

    # ============================================================================
    # Success Summary
    # ============================================================================
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║              ✅ WORK ABORTED SUCCESSFULLY                 ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.GREEN}Issue #{issue_number} work has been aborted{Colors.NC}")
    print()
    print(f"{Colors.BLUE}What was removed:{Colors.NC}")
    if has_changes:
        print("  - Uncommitted changes (discarded)")
    if unpushed_commits > 0:
        print(f"  - {unpushed_commits} unpushed commit(s) (lost)")
    print("  - Agent lock file")
    print(f"  - Worktree: {worktree_dir}")
    print()

    if unpushed_commits > 0:
        print(f"{Colors.YELLOW}Recovery:{Colors.NC}")
        print("  If you need to recover lost commits:")
        print("  1. Use git reflog in main repository:")
        print(f"     {Colors.GREEN}cd {repo_root}{Colors.NC}")
        print(f"     {Colors.GREEN}git reflog{Colors.NC}")
        print("  2. Find commit hash and cherry-pick:")
        print(f"     {Colors.GREEN}git cherry-pick <commit-hash>{Colors.NC}")
        print("  3. See: ccpm/skills/recovery-procedures.md")
        print()

    print(f"{Colors.BLUE}Next Steps:{Colors.NC}")
    print(f"  - Start new work: {Colors.GREEN}python {ccpm_dir}/commands/issue_start.py <issue-number>{Colors.NC}")
    print(f"  - Check active worktrees: {Colors.GREEN}python {ccpm_dir}/commands/issue_status.py{Colors.NC}")
    print()


def main():
    """Main entry point."""
    Colors.strip_colors()

    # Parse arguments
    args = sys.argv[1:]

    if not args or args[0] in ["-h", "--help"]:
        print(f"{Colors.BLUE}CCPM Issue Abort Command{Colors.NC}")
        print()
        print("Usage: python issue_abort.py <issue-number> [--force]")
        print()
        print("Arguments:")
        print("  <issue-number>  The GitHub issue number to abort work on")
        print()
        print("Options:")
        print("  --force         Skip confirmation prompt")
        print()
        print("Example:")
        print("  python issue_abort.py 123")
        print("  python issue_abort.py 123 --force")
        print()
        sys.exit(0 if not args else 1)

    issue_number = args[0]
    force = "--force" in args

    # Validate issue number
    if not issue_number.isdigit():
        print(f"{Colors.RED}❌ ERROR: Issue number must be a positive integer{Colors.NC}")
        print(f"Got: {issue_number}")
        sys.exit(1)

    try:
        abort_issue(issue_number, force)
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
