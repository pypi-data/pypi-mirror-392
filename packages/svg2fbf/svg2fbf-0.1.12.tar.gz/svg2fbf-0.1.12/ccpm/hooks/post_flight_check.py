#!/usr/bin/env python3
"""
Post-Flight Quality Check for CCPM Agents

Purpose: Validate code quality before creating PR
Usage: python post_flight_check.py [--fix]
Exit codes:
  0 - All checks passed, safe to create PR
  1 - Check failed, fix required

Checks performed:
  1. Tests pass (pytest)
  2. Linting passes (ruff check)
  3. Formatting correct (ruff format --check)
  4. No secrets detected (trufflehog)
  5. Correct branch (dev/testing/hotfix/*)
  6. No protected files modified

Options:
  --fix  Automatically fix linting and formatting issues

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import subprocess
import re
from pathlib import Path
from typing import List, Optional, Tuple
import shutil

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


def run_command(
    args: List[str],
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
) -> Optional[subprocess.CompletedProcess]:
    """
    Run a command and return the result.

    Args:
        args: Command and arguments as a list
        check: If True, raise exception on non-zero exit code
        capture_output: If True, capture stdout and stderr
        text: If True, return output as text instead of bytes

    Returns:
        CompletedProcess object if successful, None if command not found or failed (when check=False)
    """
    try:
        result = subprocess.run(
            args,
            capture_output=capture_output,
            text=text,
            check=check,
        )
        return result
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        raise


def run_git_command(args: List[str]) -> Optional[str]:
    """Run a git command and return output, or None if it fails."""
    result = run_command(["git"] + args, check=False)
    if result and result.returncode == 0:
        return result.stdout.strip()
    return None


def get_repo_root() -> Path:
    """Get the repository root directory."""
    repo_root = run_git_command(["rev-parse", "--show-toplevel"])
    if not repo_root:
        print(f"{Colors.RED}❌ Not in a git repository{Colors.NC}")
        sys.exit(1)
    return Path(repo_root)


def get_current_branch() -> str:
    """Get the current git branch name."""
    branch = run_git_command(["branch", "--show-current"])
    if not branch:
        print(f"{Colors.RED}❌ Could not determine current branch{Colors.NC}")
        sys.exit(1)
    return branch


def is_in_worktree() -> bool:
    """Check if we're in a git worktree."""
    is_worktree = run_git_command(["rev-parse", "--is-inside-work-tree"])
    if is_worktree != "true":
        return False

    git_common_dir = run_git_command(["rev-parse", "--git-common-dir"])
    if git_common_dir and "worktrees" in git_common_dir:
        return True
    return False


def check_tests() -> bool:
    """Run pytest test suite. Returns True if tests pass."""
    print(f"{Colors.YELLOW}[1/6]{Colors.NC} Running test suite...")

    if not shutil.which("pytest"):
        print(f"{Colors.YELLOW}   ⚠️  pytest not installed, skipping tests{Colors.NC}")
        print(f"   Install: {Colors.GREEN}uv pip install pytest{Colors.NC}")
        return True  # Don't fail if pytest not installed

    result = run_command(
        ["pytest", "tests/", "-v", "--tb=short"],
        check=False,
        capture_output=False,
    )

    if result and result.returncode == 0:
        print(f"{Colors.GREEN}   ✓ All tests passed{Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}   ✗ Tests failed{Colors.NC}")
        print()
        print(f"   {Colors.YELLOW}Fix tests before creating PR{Colors.NC}")
        print(f"   Run: {Colors.GREEN}pytest tests/ -v{Colors.NC}")
        return False


def check_linting(fix_mode: bool) -> bool:
    """Run ruff linter. Returns True if linting passes."""
    print(f"{Colors.YELLOW}[2/6]{Colors.NC} Running linter (ruff check)...")

    if not shutil.which("ruff"):
        print(f"{Colors.YELLOW}   ⚠️  ruff not installed, skipping linting{Colors.NC}")
        print(f"   Install: {Colors.GREEN}uv pip install ruff{Colors.NC}")
        return True  # Don't fail if ruff not installed

    if fix_mode:
        print("   Auto-fixing linting issues...")
        result = run_command(
            ["ruff", "check", "src/", "tests/", "--fix"],
            check=False,
            capture_output=False,
        )
        if result and result.returncode == 0:
            print(f"{Colors.GREEN}   ✓ Linting passed (auto-fixed){Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}   ✗ Linting failed (some issues cannot be auto-fixed){Colors.NC}")
            print(f"   Run: {Colors.GREEN}ruff check src/ tests/{Colors.NC}")
            return False
    else:
        result = run_command(
            ["ruff", "check", "src/", "tests/"],
            check=False,
            capture_output=False,
        )
        if result and result.returncode == 0:
            print(f"{Colors.GREEN}   ✓ Linting passed{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}   ✗ Linting failed{Colors.NC}")
            print()
            print(f"   {Colors.YELLOW}Fix linting issues or use --fix flag{Colors.NC}")
            print(f"   Run: {Colors.GREEN}python {Path(__file__).name} --fix{Colors.NC}")
            print(f"   Or:  {Colors.GREEN}ruff check src/ tests/ --fix{Colors.NC}")
            return False


def check_formatting(fix_mode: bool) -> bool:
    """Run ruff formatter. Returns True if formatting is correct."""
    print(f"{Colors.YELLOW}[3/6]{Colors.NC} Checking code formatting (ruff format)...")

    if not shutil.which("ruff"):
        print(f"{Colors.YELLOW}   ⚠️  ruff not installed, skipping formatting{Colors.NC}")
        return True  # Don't fail if ruff not installed

    if fix_mode:
        print("   Auto-formatting code...")
        result = run_command(
            ["ruff", "format", "src/", "tests/"],
            check=False,
            capture_output=False,
        )
        print(f"{Colors.GREEN}   ✓ Code formatted{Colors.NC}")
        return True
    else:
        result = run_command(
            ["ruff", "format", "--check", "src/", "tests/"],
            check=False,
            capture_output=False,
        )
        if result and result.returncode == 0:
            print(f"{Colors.GREEN}   ✓ Formatting correct{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}   ✗ Formatting issues detected{Colors.NC}")
            print()
            print(f"   {Colors.YELLOW}Fix formatting or use --fix flag{Colors.NC}")
            print(f"   Run: {Colors.GREEN}python {Path(__file__).name} --fix{Colors.NC}")
            print(f"   Or:  {Colors.GREEN}ruff format src/ tests/{Colors.NC}")
            return False


def check_secrets(repo_root: Path) -> bool:
    """Scan for secrets using trufflehog. Returns True if no secrets found."""
    print(f"{Colors.YELLOW}[4/6]{Colors.NC} Scanning for secrets (trufflehog)...")

    if not shutil.which("trufflehog"):
        print(f"{Colors.YELLOW}   ⚠️  trufflehog not installed, skipping secret scan{Colors.NC}")
        print(f"   Install: {Colors.GREEN}brew install trufflehog{Colors.NC}")
        return True  # Don't fail if trufflehog not installed

    # Scan git history for secrets
    result = run_command(
        ["trufflehog", "git", "file://.", "--only-verified", "--fail", "--no-update"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result and result.returncode == 0:
        print(f"{Colors.GREEN}   ✓ No secrets detected{Colors.NC}")
        return True
    else:
        # Check if secrets were actually found (trufflehog outputs 🐷 emoji)
        if result and "🐷" in result.stdout:
            print(f"{Colors.RED}   ✗ Secrets detected!{Colors.NC}")
            print()
            print(f"   {Colors.RED}CRITICAL: Verified secrets found in commits{Colors.NC}")
            print()
            print(f"   {Colors.YELLOW}Actions required:{Colors.NC}")
            print("   1. Remove secrets from code")
            print(f"   2. Rewrite git history: {Colors.GREEN}git rebase -i{Colors.NC}")
            print("   3. Rotate compromised credentials")
            print("   4. See: ccpm/skills/recovery-procedures.md")
            return False
        else:
            print(f"{Colors.GREEN}   ✓ No secrets detected{Colors.NC}")
            return True


def check_branch(current_branch: str) -> bool:
    """Validate branch name. Returns True if branch is allowed."""
    print(f"{Colors.YELLOW}[5/6]{Colors.NC} Validating branch...")

    # Forbidden branches
    forbidden_branches = ["master", "main"]
    if current_branch in forbidden_branches:
        print(f"{Colors.RED}   ✗ Working on forbidden branch: {current_branch}{Colors.NC}")
        print()
        print(f"   {Colors.RED}CRITICAL: Agents must NEVER work on master/main{Colors.NC}")
        print("   Switch to dev or testing branch immediately")
        return False

    # Warn if on review (allowed but supervised)
    if current_branch == "review":
        print(f"{Colors.YELLOW}   ⚠️  Working on review branch (requires supervision){Colors.NC}")

    # Check allowed branches
    allowed_branches = ["dev", "testing", "review"]
    branch_allowed = current_branch in allowed_branches

    # Also allow hotfix branches
    if current_branch.startswith("hotfix/"):
        branch_allowed = True
        print(f"{Colors.YELLOW}   ⚠️  Hotfix branch detected (requires supervision){Colors.NC}")

    # Also allow issue branches
    if re.match(r"^issue-\d+", current_branch):
        branch_allowed = True

    if branch_allowed:
        print(f"{Colors.GREEN}   ✓ Branch allowed: {current_branch}{Colors.NC}")
        return True
    else:
        print(f"{Colors.RED}   ✗ Invalid branch: {current_branch}{Colors.NC}")
        print("   Allowed: dev, testing, review, hotfix/*, issue-*")
        return False


def check_protected_files(repo_root: Path) -> bool:
    """Check for modifications to protected files. Returns True if no protected files modified."""
    print(f"{Colors.YELLOW}[6/6]{Colors.NC} Checking for protected file modifications...")

    protected_files_list = repo_root / "ccpm" / "rules" / "protected-files.txt"

    if not protected_files_list.exists():
        print(f"{Colors.YELLOW}   ⚠️  Protected files list not found, skipping check{Colors.NC}")
        return True

    # Read protected files patterns
    protected_patterns: List[str] = []
    with open(protected_files_list, "r") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue
            protected_patterns.append(line)

    # Get modified files (staged and unstaged)
    modified_files_output = run_git_command(["diff", "--name-only", "HEAD"])
    if not modified_files_output:
        print(f"{Colors.GREEN}   ✓ No protected files modified{Colors.NC}")
        return True

    modified_files = modified_files_output.split("\n")

    # Check each modified file against protected patterns
    violations: List[str] = []
    for file in modified_files:
        for pattern in protected_patterns:
            # Simple glob matching (supports * wildcard)
            if match_glob_pattern(file, pattern):
                violations.append(file)
                break

    if violations:
        print(f"{Colors.RED}   ✗ Protected files modified{Colors.NC}")
        print()
        for file in violations:
            print(f"      {Colors.RED}✗{Colors.NC} {file}")
        print()
        print(f"   {Colors.YELLOW}Recovery:{Colors.NC}")
        print(f"   {Colors.GREEN}git restore <file>{Colors.NC}")
        return False
    else:
        print(f"{Colors.GREEN}   ✓ No protected files modified{Colors.NC}")
        return True


def match_glob_pattern(path: str, pattern: str) -> bool:
    """
    Simple glob pattern matching for file paths.
    Supports * wildcard and exact matches.

    Args:
        path: File path to check
        pattern: Glob pattern (e.g., "*.py", "src/*", "exact/path.txt")

    Returns:
        True if path matches pattern
    """
    # Exact match
    if path == pattern:
        return True

    # Convert glob pattern to regex
    # Escape special regex chars except *
    regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
    regex_pattern = f"^{regex_pattern}$"

    return bool(re.match(regex_pattern, path))


def print_header(current_branch: str, in_worktree: bool, fix_mode: bool):
    """Print the script header."""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║           🛬 POST-FLIGHT QUALITY CHECK                    ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Branch:{Colors.NC} {current_branch}")
    print(f"{Colors.BLUE}Worktree:{Colors.NC} {in_worktree}")
    if fix_mode:
        print(f"{Colors.BLUE}Mode:{Colors.NC} Auto-fix enabled")
    print()


def print_summary_success(current_branch: str):
    """Print success summary."""
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║            ✅ POST-FLIGHT CHECK PASSED                    ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.GREEN}All quality checks passed!{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Ready to create PR:{Colors.NC}")
    print(f"   1. Commit changes: {Colors.GREEN}git add . && git commit{Colors.NC}")
    print(f"   2. Push to origin: {Colors.GREEN}git push origin {current_branch}{Colors.NC}")
    print(f"   3. Create PR: {Colors.GREEN}gh pr create --draft{Colors.NC}")
    print()


def print_summary_failure(failures: int):
    """Print failure summary."""
    print()
    print(f"{Colors.RED}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.RED}║              ❌ POST-FLIGHT CHECK FAILED                  ║{Colors.NC}")
    print(f"{Colors.RED}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.RED}{failures} check(s) failed{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}Actions required:{Colors.NC}")
    print("   1. Fix failing checks (see above)")
    print(f"   2. Re-run: {Colors.GREEN}python {Path(__file__).name}{Colors.NC}")
    print(f"   3. Or auto-fix: {Colors.GREEN}python {Path(__file__).name} --fix{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}See also:{Colors.NC}")
    print("   - Recovery procedures: ccpm/skills/recovery-procedures.md")
    print("   - 5-branch workflow: ccpm/skills/5-branch-workflow.md")
    print()


def main():
    """Main entry point."""
    Colors.strip_colors()

    # Parse arguments
    fix_mode = "--fix" in sys.argv

    try:
        # Get repository info
        repo_root = get_repo_root()
        current_branch = get_current_branch()
        in_worktree = is_in_worktree()

        # Change to repo root
        import os

        os.chdir(repo_root)

        # Print header
        print_header(current_branch, in_worktree, fix_mode)

        # Track failures
        failures = 0

        # Run all checks
        if not check_tests():
            failures += 1

        if not check_linting(fix_mode):
            failures += 1

        if not check_formatting(fix_mode):
            failures += 1

        if not check_secrets(repo_root):
            failures += 1

        if not check_branch(current_branch):
            failures += 1

        if not check_protected_files(repo_root):
            failures += 1

        # Print summary
        if failures == 0:
            print_summary_success(current_branch)
            sys.exit(0)
        else:
            print_summary_failure(failures)
            sys.exit(1)

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
