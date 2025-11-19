#!/usr/bin/env python3
"""
Pre-Commit Safety Hook for CCPM Agents

Purpose: Block commits that modify protected infrastructure files
Usage: Called automatically by git pre-commit hook
Exit codes:
  0 - Safe to commit
  1 - Blocked (protected file modified)

Installation:
  ln -sf ../../ccpm/hooks/pre_commit_safety.py .git/hooks/pre-commit

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Optional
from fnmatch import fnmatch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.project_config import run_git_command


# ANSI color codes (work on Windows 10+ and Unix)
class Colors:
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[0;32m"
    NC = "\033[0m"  # No Color

    @staticmethod
    def strip_colors():
        """Disable colors if output is not a TTY."""
        if not sys.stdout.isatty():
            Colors.RED = ""
            Colors.YELLOW = ""
            Colors.GREEN = ""
            Colors.NC = ""


def get_main_repo_root() -> Path:
    """
    Get the main repository root (handles worktrees correctly).

    For worktrees, ccpm/ exists in main repo, not worktree (it's gitignored).
    Use --git-common-dir to find main .git, then navigate up to repo root.

    Returns:
        Path to the main repository root
    """
    git_common_dir = run_git_command(["rev-parse", "--git-common-dir"])
    if not git_common_dir:
        # Fallback to current repo root
        git_common_dir = run_git_command(["rev-parse", "--git-dir"])
        if not git_common_dir:
            print(f"{Colors.RED}❌ ERROR: Not in a git repository{Colors.NC}")
            sys.exit(1)

    # Navigate up from .git directory to repo root
    main_repo_root = Path(git_common_dir).parent.resolve()
    return main_repo_root


def load_protected_patterns(protected_files_list: Path) -> List[str]:
    """
    Load protected file patterns from the configuration file.

    Args:
        protected_files_list: Path to protected-files.txt

    Returns:
        List of patterns (excluding comments and empty lines)
    """
    try:
        with protected_files_list.open("r", encoding="utf-8") as f:
            patterns = []
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith("#") or not line:
                    continue
                patterns.append(line)
            return patterns
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"{Colors.RED}❌ ERROR: Failed to read protected files list: {e}{Colors.NC}")
        sys.exit(1)


def get_staged_files() -> List[str]:
    """
    Get list of staged files from git.

    Returns:
        List of staged file paths
    """
    output = run_git_command(["diff", "--cached", "--name-only"])
    if not output:
        return []
    return [f for f in output.split("\n") if f.strip()]


def check_protected_files(staged_files: List[str], protected_patterns: List[str]) -> List[str]:
    """
    Check if any staged files match protected patterns.

    Args:
        staged_files: List of staged file paths
        protected_patterns: List of patterns to match against

    Returns:
        List of violations (files that match protected patterns)
    """
    violations = []

    for file in staged_files:
        for pattern in protected_patterns:
            # Support both exact match and glob patterns
            # fnmatch handles *, ?, [seq], etc.
            if fnmatch(file, pattern) or file == pattern:
                violations.append(file)
                break  # Don't add same file multiple times

    return violations


def print_blocked_message(violations: List[str]) -> None:
    """
    Print the error message when protected files are modified.

    Args:
        violations: List of protected files that were modified
    """
    print(f"{Colors.RED}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.RED}║                 ⛔ COMMIT BLOCKED                         ║{Colors.NC}")
    print(f"{Colors.RED}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.RED}❌ ERROR: Attempting to modify protected infrastructure files{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}Protected files detected in this commit:{Colors.NC}")
    for file in violations:
        print(f"   {Colors.RED}✗{Colors.NC} {file}")
    print()
    print(f"{Colors.YELLOW}Why this is blocked:{Colors.NC}")
    print("   These files are critical infrastructure managed by humans only.")
    print("   Agents must NOT modify:")
    print("   - justfile (build commands)")
    print("   - scripts/release.sh (release automation)")
    print("   - .github/workflows/* (CI/CD pipelines)")
    print("   - CHANGELOG.md (auto-generated by git-cliff)")
    print("   - pyproject.toml (project configuration)")
    print()
    print(f"{Colors.GREEN}Recovery options:{Colors.NC}")
    print()
    print("   1. Unstage protected files:")
    print(f"      {Colors.GREEN}git restore --staged <file>{Colors.NC}")
    print()
    print("   2. Restore protected files to original state:")
    print(f"      {Colors.GREEN}git restore <file>{Colors.NC}")
    print()
    print("   3. Commit only non-protected files:")
    print(f"      {Colors.GREEN}git add <safe-files>{Colors.NC}")
    print(f"      {Colors.GREEN}git commit{Colors.NC}")
    print()
    print("   4. If you need to modify these files:")
    print(f"      {Colors.YELLOW}Contact a human maintainer for approval{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}See also:{Colors.NC}")
    print("   - Protected files list: ccpm/rules/protected-files.txt")
    print("   - Recovery procedures: ccpm/skills/recovery-procedures.md")
    print()


def main() -> None:
    """Main entry point for pre-commit safety check."""
    Colors.strip_colors()

    try:
        # Get main repository root (handles worktrees)
        main_repo_root = get_main_repo_root()
        protected_files_list = main_repo_root / "ccpm" / "rules" / "protected-files.txt"

        # Check if protected files list exists
        if not protected_files_list.exists():
            print(f"{Colors.YELLOW}⚠️  Warning: Protected files list not found at:{Colors.NC}")
            print(f"   {protected_files_list}")
            print("   Skipping protected file check.")
            sys.exit(0)

        # Load protected patterns
        protected_patterns = load_protected_patterns(protected_files_list)

        if not protected_patterns:
            print(f"{Colors.YELLOW}⚠️  Warning: No protected patterns found{Colors.NC}")
            print("   Skipping protected file check.")
            sys.exit(0)

        # Get staged files
        staged_files = get_staged_files()

        if not staged_files:
            # No files staged - this is OK, just exit silently
            sys.exit(0)

        # Check for violations
        violations = check_protected_files(staged_files, protected_patterns)

        # If violations found, block commit
        if violations:
            print_blocked_message(violations)
            sys.exit(1)

        # All clear
        print(f"{Colors.GREEN}✅ Pre-commit safety check passed{Colors.NC}")
        print("   No protected files modified")
        sys.exit(0)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}❌ ERROR: {e}{Colors.NC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
