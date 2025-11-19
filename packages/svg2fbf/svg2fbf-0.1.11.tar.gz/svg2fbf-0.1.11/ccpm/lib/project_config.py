"""
CCPM Project Configuration

Purpose: Auto-detect project information for generic CCPM plugin usage
Usage: from ccpm.lib.project_config import get_config

This library detects:
- Project name from git repository
- Repository owner
- Worktree and audit log locations

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Dict


def run_git_command(args: list[str]) -> Optional[str]:
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


def get_project_name() -> str:
    """Detect project name from git remote URL or directory name."""
    remote_url = run_git_command(["remote", "get-url", "origin"])

    if not remote_url:
        # Fallback: use directory name
        repo_root = run_git_command(["rev-parse", "--show-toplevel"])
        if repo_root:
            return Path(repo_root).name
        return Path.cwd().name

    # Extract repo name from URL (works for both HTTPS and SSH)
    # github.com/user/repo.git → repo
    # github.com/user/repo → repo
    match = re.search(r"/([^/]+?)(\.git)?$", remote_url)
    if match:
        return match.group(1)

    # Fallback
    return Path.cwd().name


def get_repo_owner() -> str:
    """Detect repository owner from git remote URL."""
    remote_url = run_git_command(["remote", "get-url", "origin"])

    if not remote_url:
        return "unknown"

    # Extract owner from URL
    # github.com/user/repo.git → user
    # github.com:user/repo.git → user
    match = re.search(r"[:/]([^/]+)/[^/]+(\.git)?$", remote_url)
    if match:
        return match.group(1)

    return "unknown"


def get_config() -> Dict[str, str]:
    """
    Get complete project configuration.

    Returns:
        Dict with keys:
        - project_name: Name of the project
        - repo_owner: Owner/organization of the repository
        - project_slug: Combined owner-project identifier
        - worktree_base: Base directory for worktrees
        - audit_log_dir: Directory for audit logs
    """
    project_name = get_project_name()
    repo_owner = get_repo_owner()
    project_slug = f"{repo_owner}-{project_name}"

    # Worktree and audit log locations (project-specific)
    cache_dir = Path.home() / ".cache"
    worktree_base = cache_dir / "ccpm-worktrees" / project_slug
    audit_log_dir = cache_dir / "ccpm-audit-logs" / project_slug

    # Create directories if they don't exist
    worktree_base.mkdir(parents=True, exist_ok=True)
    audit_log_dir.mkdir(parents=True, exist_ok=True)

    return {
        "project_name": project_name,
        "repo_owner": repo_owner,
        "project_slug": project_slug,
        "worktree_base": str(worktree_base),
        "audit_log_dir": str(audit_log_dir),
    }


# For direct execution or import
if __name__ == "__main__":
    config = get_config()
    print(f"Project: {config['project_name']}")
    print(f"Owner: {config['repo_owner']}")
    print(f"Slug: {config['project_slug']}")
    print(f"Worktrees: {config['worktree_base']}")
    print(f"Audit logs: {config['audit_log_dir']}")
