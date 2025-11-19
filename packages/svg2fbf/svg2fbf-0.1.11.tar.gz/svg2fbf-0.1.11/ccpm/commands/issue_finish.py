#!/usr/bin/env python3
"""
CCPM Issue Finish Command

Purpose: Complete work on issue, push changes, create PR
Usage: python issue_finish.py <issue-number> [--keep-worktree]
Exit codes:
  0 - Work completed successfully
  1 - Error occurred

Steps:
  1. Validate worktree exists
  2. Run post-flight quality checks
  3. Push commits to origin
  4. Create Draft PR
  5. Remove agent lock
  6. Optionally remove worktree
  7. Log action

Example:
  python issue_finish.py 123
  python issue_finish.py 123 --keep-worktree

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


def run_git_command(args: list[str], cwd: Optional[Path] = None, check: bool = True) -> Optional[str]:
    """Run a git command and return output."""
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
        if check:
            print(f"{Colors.RED}❌ Git command failed: {e}{Colors.NC}")
            if e.stderr:
                print(f"   Error: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Git is not installed{Colors.NC}")
        sys.exit(1)


def run_gh_command(args: list[str], check: bool = True) -> Optional[str]:
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
        print(f"{Colors.RED}❌ GitHub CLI (gh) is not installed{Colors.NC}")
        print("Install: https://cli.github.com/")
        return None
    except subprocess.CalledProcessError as e:
        if check:
            print(f"{Colors.RED}❌ gh command failed: {e}{Colors.NC}")
            if e.stderr:
                print(f"   Error: {e.stderr.strip()}")
        return None


def run_hook_script(script_name: str, args: list[str] = None, cwd: Optional[Path] = None) -> bool:
    """Run a CCPM hook script and return success status."""
    ccpm_dir = Path(__file__).parent.parent
    script_path = ccpm_dir / "hooks" / script_name

    if not script_path.exists():
        print(f"{Colors.YELLOW}   ⚠️  Hook script not found: {script_path}{Colors.NC}")
        return True  # Not finding a hook is not a failure

    if not os.access(script_path, os.X_OK):
        print(f"{Colors.YELLOW}   ⚠️  Hook script not executable: {script_path}{Colors.NC}")
        return True

    try:
        cmd = [str(script_path)]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=False,  # Let output flow to console
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to run hook script: {e}{Colors.NC}")
        return False


def get_repo_root() -> Path:
    """Get the git repository root directory."""
    root = run_git_command(["rev-parse", "--show-toplevel"])
    if not root:
        print(f"{Colors.RED}❌ Not in a git repository{Colors.NC}")
        sys.exit(1)
    return Path(root)


def validate_worktree(worktree_dir: Path) -> Tuple[str, str]:
    """
    Validate that worktree exists and read metadata.

    Returns:
        Tuple of (target_branch, agent_id)
    """
    metadata_file = worktree_dir / ".agent-metadata.json"

    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            target_branch = metadata.get("target_branch", "unknown")
            agent_id = metadata.get("agent_id", "unknown")

            print(f"{Colors.GREEN}   ✓ Worktree found{Colors.NC}")
            print(f"     Branch: {target_branch}")
            print(f"     Agent: {agent_id}")

            return target_branch, agent_id
        except Exception as e:
            print(f"{Colors.YELLOW}   ⚠️  Failed to read metadata: {e}{Colors.NC}")
            print(f"{Colors.YELLOW}   ⚠️  Continuing anyway{Colors.NC}")
            return "unknown", "unknown"
    else:
        print(f"{Colors.YELLOW}   ⚠️  Metadata file not found, continuing anyway{Colors.NC}")
        return "unknown", "unknown"


def check_uncommitted_changes(worktree_dir: Path) -> bool:
    """Check if there are uncommitted changes in the worktree."""
    # Check unstaged changes
    diff_result = subprocess.run(
        ["git", "diff", "--quiet"],
        cwd=str(worktree_dir),
        capture_output=True,
    )
    has_unstaged = diff_result.returncode != 0

    # Check staged changes
    diff_cached_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(worktree_dir),
        capture_output=True,
    )
    has_staged = diff_cached_result.returncode != 0

    return has_unstaged or has_staged


def get_commits_ahead(worktree_dir: Path) -> Optional[int]:
    """Get number of commits ahead of upstream."""
    # Check if upstream exists
    upstream_check = subprocess.run(
        ["git", "rev-parse", "@{u}"],
        cwd=str(worktree_dir),
        capture_output=True,
    )

    if upstream_check.returncode != 0:
        return None  # No upstream set

    # Get commits ahead
    result = run_git_command(["rev-list", "--count", "@{u}..HEAD"], cwd=worktree_dir)
    if result:
        return int(result)
    return 0


def push_commits(worktree_dir: Path) -> bool:
    """Push commits to origin."""
    current_branch = run_git_command(["branch", "--show-current"], cwd=worktree_dir)
    if not current_branch:
        print(f"{Colors.RED}❌ Failed to get current branch{Colors.NC}")
        return False

    # Check for uncommitted changes
    if check_uncommitted_changes(worktree_dir):
        print(f"{Colors.RED}❌ Uncommitted changes detected{Colors.NC}")
        print()

        # Show status
        subprocess.run(["git", "status", "--short"], cwd=str(worktree_dir))

        print()
        print(f"   {Colors.YELLOW}Commit changes first:{Colors.NC}")
        print(f"   {Colors.GREEN}git add .{Colors.NC}")
        print(f'   {Colors.GREEN}git commit -m "type(scope): Description"{Colors.NC}')
        return False

    # Check commits ahead
    commits_ahead = get_commits_ahead(worktree_dir)

    if commits_ahead is None:
        # No upstream, set it and push
        print("   Setting upstream and pushing...")
        result = subprocess.run(
            ["git", "push", "-u", "origin", current_branch],
            cwd=str(worktree_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}   ✓ Pushed successfully{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}❌ Push failed{Colors.NC}")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
            return False
    elif commits_ahead == 0:
        print(f"{Colors.YELLOW}   ⚠️  No new commits to push{Colors.NC}")
        return True
    else:
        print(f"   Pushing {commits_ahead} commit(s)...")
        result = subprocess.run(
            ["git", "push", "origin", current_branch],
            cwd=str(worktree_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}   ✓ Pushed successfully{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}❌ Push failed{Colors.NC}")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
            return False


def create_pull_request(issue_number: str, target_branch: str, agent_id: str, worktree_dir: Path) -> Optional[str]:
    """
    Create a draft pull request.

    Returns:
        PR number if successful, None otherwise
    """
    current_branch = run_git_command(["branch", "--show-current"], cwd=worktree_dir)
    if not current_branch:
        print(f"{Colors.RED}❌ Failed to get current branch{Colors.NC}")
        return None

    # Check if gh is available
    if not run_gh_command(["--version"], check=False):
        print(f"{Colors.YELLOW}   ⚠️  GitHub CLI not installed, skipping PR creation{Colors.NC}")
        print(f"   Install: {Colors.GREEN}brew install gh{Colors.NC}")
        return None

    # Check if PR already exists
    existing_pr = run_gh_command(["pr", "list", "--head", current_branch, "--json", "number", "--jq", '.[0].number // ""'], check=False)

    if existing_pr:
        print(f"{Colors.YELLOW}   ⚠️  PR already exists: #{existing_pr}{Colors.NC}")

        # Get repo info for URL
        repo_info = run_gh_command(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
        if repo_info:
            print(f"     {Colors.GREEN}https://github.com/{repo_info}/pull/{existing_pr}{Colors.NC}")

        return existing_pr

    # Get issue info for PR title
    issue_title = ""
    issue_info = run_gh_command(["issue", "view", issue_number, "--json", "title"], check=False)
    if issue_info:
        try:
            issue_data = json.loads(issue_info)
            issue_title = issue_data.get("title", "")
        except:
            pass

    # Create PR title
    pr_title = f"Fix #{issue_number}: {issue_title}"

    # Create PR body
    pr_body = f"""Fixes #{issue_number}

## Summary
<!-- Brief description of changes -->

## Changes
<!-- List of key changes made -->

## Testing
- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Formatting correct
- [ ] No secrets detected

## Agent Info
- Agent ID: {agent_id}
- Branch: {current_branch}
- Target: {target_branch}
"""

    # Create draft PR
    result = subprocess.run(
        ["gh", "pr", "create", "--draft", "--title", pr_title, "--body", pr_body, "--base", target_branch],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        pr_url = result.stdout.strip()
        # Extract PR number from URL (last segment)
        pr_number = pr_url.split("/")[-1]

        print(f"{Colors.GREEN}   ✓ Draft PR created: #{pr_number}{Colors.NC}")
        print(f"     {Colors.GREEN}{pr_url}{Colors.NC}")

        return pr_number
    else:
        print(f"{Colors.RED}❌ Failed to create PR{Colors.NC}")
        if result.stderr:
            print(f"   Error: {result.stderr.strip()}")
        return None


def remove_worktree(worktree_dir: Path, repo_root: Path) -> bool:
    """Remove the worktree."""
    result = subprocess.run(
        ["git", "worktree", "remove", str(worktree_dir), "--force"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"{Colors.GREEN}   ✓ Worktree removed{Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}❌ Failed to remove worktree{Colors.NC}")
        print(f"   Remove manually: {Colors.GREEN}git worktree remove {worktree_dir}{Colors.NC}")
        return False


def finish_issue(issue_number: str, keep_worktree: bool = False) -> None:
    """Main function to finish work on an issue."""
    config = get_config()
    repo_root = get_repo_root()

    # Build worktree path
    worktree_base = Path(config["worktree_base"])
    worktree_dir = worktree_base / f"issue-{issue_number}"
    lock_file = worktree_dir / ".agent-lock"

    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║            🏁 FINISHING WORK ON ISSUE                     ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Issue:{Colors.NC} #{issue_number}")
    print()

    # ========================================================================
    # Step 1: Validate worktree exists
    # ========================================================================
    print(f"{Colors.YELLOW}Step 1/7:{Colors.NC} Validating worktree...")

    if not worktree_dir.exists():
        print(f"{Colors.RED}❌ Worktree not found: {worktree_dir}{Colors.NC}")
        print("   Use issue-status.sh to check active worktrees")
        sys.exit(1)

    target_branch, agent_id = validate_worktree(worktree_dir)

    # ========================================================================
    # Step 2: Run post-flight quality checks
    # ========================================================================
    print(f"{Colors.YELLOW}Step 2/7:{Colors.NC} Running quality checks...")
    print()

    if not run_hook_script("post-flight-check.sh", cwd=worktree_dir):
        print()
        print(f"{Colors.RED}❌ Quality checks failed{Colors.NC}")
        print()
        print(f"   {Colors.YELLOW}Options:{Colors.NC}")
        print(f"   1. Fix issues and re-run: {Colors.GREEN}python {__file__} {issue_number}{Colors.NC}")

        ccpm_dir = Path(__file__).parent.parent
        print(f"   2. Auto-fix: {Colors.GREEN}{ccpm_dir}/hooks/post-flight-check.sh --fix{Colors.NC}")
        print(f"   3. Abort work: {Colors.GREEN}{ccpm_dir}/commands/issue-abort.sh {issue_number}{Colors.NC}")
        sys.exit(1)

    print()

    # ========================================================================
    # Step 3: Push commits to origin
    # ========================================================================
    print(f"{Colors.YELLOW}Step 3/7:{Colors.NC} Pushing commits...")

    if not push_commits(worktree_dir):
        sys.exit(1)

    # Get current branch for later use
    current_branch = run_git_command(["branch", "--show-current"], cwd=worktree_dir)

    # ========================================================================
    # Step 4: Create Draft PR
    # ========================================================================
    print(f"{Colors.YELLOW}Step 4/7:{Colors.NC} Creating Pull Request...")

    pr_number = create_pull_request(issue_number, target_branch, agent_id, worktree_dir)

    # ========================================================================
    # Step 5: Remove agent lock
    # ========================================================================
    print(f"{Colors.YELLOW}Step 5/7:{Colors.NC} Removing agent lock...")

    if lock_file.exists():
        try:
            lock_file.unlink()
            print(f"{Colors.GREEN}   ✓ Lock removed{Colors.NC}")
        except Exception as e:
            print(f"{Colors.YELLOW}   ⚠️  Failed to remove lock: {e}{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  Lock file not found{Colors.NC}")

    # ========================================================================
    # Step 6: Optionally remove worktree
    # ========================================================================
    print(f"{Colors.YELLOW}Step 6/7:{Colors.NC} Cleaning up worktree...")

    if keep_worktree:
        print(f"{Colors.YELLOW}   ⚠️  Keeping worktree (--keep-worktree flag){Colors.NC}")
        print(f"     Worktree: {worktree_dir}")
        print(f"     Remove later with: {Colors.GREEN}git worktree remove {worktree_dir}{Colors.NC}")
    else:
        remove_worktree(worktree_dir, repo_root)

    # ========================================================================
    # Step 7: Log action
    # ========================================================================
    print(f"{Colors.YELLOW}Step 7/7:{Colors.NC} Logging action...")

    # Set environment variables for audit logging
    os.environ["CCPM_AGENT_ID"] = agent_id
    os.environ["CCPM_SESSION_ID"] = str(os.getpid())

    # Only log if we successfully created a PR
    if pr_number:
        pr_title = f"Fix #{issue_number}"
        if run_hook_script("audit-log.sh", args=["pr_create", pr_number, pr_title, "true"]):
            print(f"{Colors.GREEN}   ✓ Action logged{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}   ⚠️  Failed to log action{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}   ⚠️  No PR created, skipping audit log{Colors.NC}")

    # ========================================================================
    # Success Summary
    # ========================================================================
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║              ✅ WORK COMPLETED SUCCESSFULLY               ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.GREEN}Issue #{issue_number} work is complete!{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Summary:{Colors.NC}")
    print(f"  - Commits pushed to: {current_branch}")
    print(f"  - Draft PR created: #{pr_number if pr_number else 'N/A'}")
    print("  - Agent lock removed")
    if keep_worktree:
        print(f"  - Worktree preserved: {worktree_dir}")
    else:
        print("  - Worktree removed")
    print()
    print(f"{Colors.BLUE}Next Steps:{Colors.NC}")
    print("  1. Review the PR on GitHub")
    print("  2. Request review from maintainer")
    print("  3. Wait for CI checks to pass")
    print("  4. Address any feedback")
    print("  5. Convert to Ready for Review when ready")
    print()
    print(f"{Colors.YELLOW}Important:{Colors.NC}")
    print("  - DO NOT merge your own PR")
    print("  - Wait for human review and approval")
    print("  - Monitor CI checks for failures")
    print()


def main():
    """Main entry point."""
    Colors.strip_colors()

    # Parse arguments
    if len(sys.argv) < 2:
        print(f"{Colors.RED}❌ ERROR: Issue number required{Colors.NC}")
        print(f"Usage: {sys.argv[0]} <issue-number> [--keep-worktree]")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} 123")
        print(f"  {sys.argv[0]} 123 --keep-worktree  # Keep worktree after finishing")
        sys.exit(1)

    issue_number = sys.argv[1]
    keep_worktree = "--keep-worktree" in sys.argv

    try:
        finish_issue(issue_number, keep_worktree)
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
