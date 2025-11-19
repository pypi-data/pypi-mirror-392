#!/usr/bin/env python3
"""
CCPM Issue Start Command

Purpose: Start work on a GitHub issue in isolated worktree
Usage: python issue_start.py <issue-number> [target-branch]
Exit codes:
  0 - Worktree created successfully
  1 - Error occurred

Steps:
  1. Run pre-flight checks
  2. Create worktree from target branch
  3. Create mutex lock file
  4. Create metadata file
  5. Install pre-commit hook
  6. Log action

Example:
  python issue_start.py 123 dev

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import json
import subprocess
import os
import socket
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict

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


def run_command(args: list[str], cwd: Optional[Path] = None, check: bool = True, capture_output: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print(f"{Colors.RED}❌ Command failed: {' '.join(args)}{Colors.NC}")
            if e.stderr:
                print(f"{Colors.RED}{e.stderr}{Colors.NC}")
            raise
        return None
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Command not found: {args[0]}{Colors.NC}")
        sys.exit(1)


def get_repo_root() -> Path:
    """Get the git repository root directory."""
    result = run_command(["git", "rev-parse", "--show-toplevel"])
    if result and result.stdout:
        return Path(result.stdout.strip())
    print(f"{Colors.RED}❌ Not in a git repository{Colors.NC}")
    sys.exit(1)


def get_issue_info(issue_number: int) -> Dict[str, str]:
    """Get issue information from GitHub using gh CLI."""
    try:
        result = run_command(["gh", "issue", "view", str(issue_number), "--json", "title,assignees"], check=False)
        if result and result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            title = data.get("title", "Unknown")
            assignees = data.get("assignees", [])
            assignee = assignees[0]["login"] if assignees else "Unassigned"
            return {"title": title, "assignee": assignee}
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    except FileNotFoundError:
        pass

    return {"title": "Unknown", "assignee": "Unknown"}


def run_preflight_check(ccpm_dir: Path, issue_number: int, target_branch: str) -> bool:
    """Run pre-flight safety checks."""
    preflight_script = ccpm_dir / "hooks" / "pre-flight-check.sh"

    if preflight_script.exists() and os.access(preflight_script, os.X_OK):
        try:
            result = run_command([str(preflight_script), str(issue_number), target_branch], check=False)
            if result and result.returncode == 0:
                return True
            else:
                print(f"{Colors.RED}❌ Pre-flight checks failed{Colors.NC}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Pre-flight check error: {e}{Colors.NC}")
            return False
    else:
        print(f"{Colors.YELLOW}⚠️  Pre-flight check script not found, skipping{Colors.NC}")
        return True


def create_worktree(repo_root: Path, worktree_dir: Path, target_branch: str) -> bool:
    """Create a git worktree."""
    # Check if worktree already exists
    if worktree_dir.exists():
        print(f"{Colors.RED}❌ Worktree already exists: {worktree_dir}{Colors.NC}")
        print("   Use issue-status.sh to check active worktrees")
        print("   Or use issue-abort.sh to remove stale worktree")
        return False

    # Create parent directory
    worktree_dir.parent.mkdir(parents=True, exist_ok=True)

    # Create worktree
    result = run_command(["git", "worktree", "add", str(worktree_dir), target_branch], cwd=repo_root, check=False)

    if result and result.returncode == 0:
        print(f"{Colors.GREEN}   ✓ Worktree created at: {worktree_dir}{Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}❌ Failed to create worktree{Colors.NC}")
        return False


def create_lock_file(lock_file: Path, agent_id: str, agent_session: str, issue_number: int, target_branch: str, started_at: str) -> None:
    """Create the mutex lock file."""
    lock_data = {"agent_id": agent_id, "session_id": agent_session, "pid": os.getpid(), "issue_number": issue_number, "target_branch": target_branch, "started": started_at, "hostname": socket.gethostname(), "user": os.getenv("USER", os.getenv("USERNAME", "unknown"))}

    with open(lock_file, "w") as f:
        json.dump(lock_data, f, indent=2)

    print(f"{Colors.GREEN}   ✓ Lock file created{Colors.NC}")


def create_metadata_file(metadata_file: Path, issue_number: int, target_branch: str, worktree_dir: Path, agent_id: str, agent_session: str, started_at: str) -> None:
    """Create the metadata file with issue information."""
    # Get issue info from GitHub
    issue_info = get_issue_info(issue_number)

    metadata = {"issue_number": issue_number, "issue_title": issue_info["title"], "issue_assignee": issue_info["assignee"], "target_branch": target_branch, "worktree_path": str(worktree_dir), "created_at": started_at, "agent_id": agent_id, "session_id": agent_session}

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"{Colors.GREEN}   ✓ Metadata file created{Colors.NC}")


def install_precommit_hook(worktree_dir: Path, ccpm_dir: Path) -> None:
    """Install pre-commit hook in the worktree."""
    worktree_hook_dir = worktree_dir / ".git" / "hooks"
    worktree_hook_dir.mkdir(parents=True, exist_ok=True)

    precommit_script = ccpm_dir / "hooks" / "pre-commit-safety.sh"

    if precommit_script.exists() and os.access(precommit_script, os.X_OK):
        # Create symlink (works on Windows 10+ with developer mode or admin privileges)
        hook_target = worktree_hook_dir / "pre-commit"
        try:
            # Remove existing hook if present
            if hook_target.exists() or hook_target.is_symlink():
                hook_target.unlink()

            # Create symlink
            hook_target.symlink_to(precommit_script)

            # Make it executable (Unix-like systems)
            if hasattr(os, "chmod"):
                hook_target.chmod(0o755)

            print(f"{Colors.GREEN}   ✓ Pre-commit hook installed{Colors.NC}")
        except (OSError, NotImplementedError) as e:
            # Symlink might fail on Windows without proper permissions
            # Fall back to copying the file
            import shutil

            shutil.copy2(precommit_script, hook_target)
            if hasattr(os, "chmod"):
                hook_target.chmod(0o755)
            print(f"{Colors.YELLOW}   ⚠️  Pre-commit hook copied (symlink failed){Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  Pre-commit hook not found, skipping{Colors.NC}")


def log_action(ccpm_dir: Path, agent_id: str, agent_session: str, worktree_dir: Path, issue_number: int) -> None:
    """Log the worktree creation action."""
    audit_script = ccpm_dir / "hooks" / "audit-log.sh"

    # Set environment variables for the audit script
    env = os.environ.copy()
    env["CCPM_AGENT_ID"] = agent_id
    env["CCPM_SESSION_ID"] = agent_session

    if audit_script.exists() and os.access(audit_script, os.X_OK):
        try:
            result = subprocess.run([str(audit_script), "worktree_create", str(worktree_dir), str(issue_number)], env=env, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"{Colors.GREEN}   ✓ Action logged{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}   ⚠️  Audit log warning{Colors.NC}")
        except Exception:
            print(f"{Colors.YELLOW}   ⚠️  Audit log failed{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  Audit log script not found, skipping{Colors.NC}")


def print_success_message(issue_number: int, worktree_dir: Path, ccpm_dir: Path) -> None:
    """Print success summary and next steps."""
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║              ✅ WORKTREE CREATED SUCCESSFULLY             ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.GREEN}Issue #{issue_number} workspace is ready!{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Worktree Location:{Colors.NC}")
    print(f"  {worktree_dir}")
    print()
    print(f"{Colors.BLUE}Next Steps:{Colors.NC}")
    print("  1. Change to worktree:")
    print(f"     {Colors.GREEN}cd {worktree_dir}{Colors.NC}")
    print()
    print("  2. Start working on the issue:")
    print(f"     {Colors.GREEN}# Edit files, make changes{Colors.NC}")
    print()
    print("  3. Commit your changes:")
    print(f"     {Colors.GREEN}git add .{Colors.NC}")
    print(f'     {Colors.GREEN}git commit -m "feat(scope): Description for issue #{issue_number}"{Colors.NC}')
    print()
    print("  4. Run quality checks:")
    print(f"     {Colors.GREEN}{ccpm_dir}/hooks/post-flight-check.sh{Colors.NC}")
    print()
    print("  5. Finish work and create PR:")
    print(f"     {Colors.GREEN}{ccpm_dir}/commands/issue-finish.sh {issue_number}{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}Remember:{Colors.NC}")
    print("  - Follow conventional commit format")
    print("  - Run tests before committing")
    print("  - Never modify protected files (see ccpm/rules/protected-files.txt)")
    print(f"  - Use {Colors.GREEN}issue-status.sh{Colors.NC} to check worktree status")
    print()


def start_issue(issue_number: int, target_branch: str = "dev") -> None:
    """Main function to start work on an issue."""
    config = get_config()
    repo_root = get_repo_root()
    ccpm_dir = repo_root / "ccpm"

    # Get worktree directory from config
    worktree_base = Path(config["worktree_base"])
    worktree_dir = worktree_base / f"issue-{issue_number}"

    # Agent info
    agent_id = os.getenv("CCPM_AGENT_ID", f"agent-{os.getpid()}")
    agent_session = str(os.getpid())
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Files
    lock_file = worktree_dir / ".agent-lock"
    metadata_file = worktree_dir / ".agent-metadata.json"

    # Print header
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║              🚀 STARTING WORK ON ISSUE                    ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Issue:{Colors.NC} #{issue_number}")
    print(f"{Colors.BLUE}Branch:{Colors.NC} {target_branch}")
    print(f"{Colors.BLUE}Agent:{Colors.NC} {agent_id}")
    print()

    # Step 1: Run pre-flight checks
    print(f"{Colors.YELLOW}Step 1/6:{Colors.NC} Running pre-flight safety checks...")
    print()

    if not run_preflight_check(ccpm_dir, issue_number, target_branch):
        sys.exit(1)

    print()

    # Step 2: Create worktree
    print(f"{Colors.YELLOW}Step 2/6:{Colors.NC} Creating worktree...")

    if not create_worktree(repo_root, worktree_dir, target_branch):
        sys.exit(1)

    # Step 3: Create mutex lock file
    print(f"{Colors.YELLOW}Step 3/6:{Colors.NC} Creating agent lock...")

    create_lock_file(lock_file, agent_id, agent_session, issue_number, target_branch, started_at)

    # Step 4: Create metadata file
    print(f"{Colors.YELLOW}Step 4/6:{Colors.NC} Creating metadata...")

    create_metadata_file(metadata_file, issue_number, target_branch, worktree_dir, agent_id, agent_session, started_at)

    # Step 5: Install pre-commit hook
    print(f"{Colors.YELLOW}Step 5/6:{Colors.NC} Installing pre-commit hook...")

    install_precommit_hook(worktree_dir, ccpm_dir)

    # Step 6: Log action
    print(f"{Colors.YELLOW}Step 6/6:{Colors.NC} Logging action...")

    log_action(ccpm_dir, agent_id, agent_session, worktree_dir, issue_number)

    # Success summary
    print_success_message(issue_number, worktree_dir, ccpm_dir)


def main():
    """Main entry point."""
    Colors.strip_colors()

    # Parse arguments
    if len(sys.argv) < 2:
        print(f"{Colors.RED}❌ ERROR: Issue number required{Colors.NC}")
        print(f"Usage: {sys.argv[0]} <issue-number> [target-branch]")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} 123 dev")
        sys.exit(1)

    try:
        issue_number = int(sys.argv[1])
    except ValueError:
        print(f"{Colors.RED}❌ ERROR: Issue number must be an integer{Colors.NC}")
        sys.exit(1)

    target_branch = sys.argv[2] if len(sys.argv) > 2 else "dev"

    try:
        start_issue(issue_number, target_branch)
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
