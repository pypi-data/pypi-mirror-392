#!/usr/bin/env python3
"""
GitHub Label Setup (CCPM Plugin)

Purpose: Create standard labels for issue management in ANY GitHub repository
Usage: python setup_labels.py [--force]
Exit codes:
  0 - Labels created/verified successfully
  1 - Error occurred

Options:
  --force  Delete existing labels and recreate (DANGEROUS)

Author: CCPM Plugin
Last updated: 2025-01-17
Cross-platform: Works on Windows, macOS, Linux
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

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
        print(f"{Colors.RED}❌ GitHub CLI (gh) is not installed{Colors.NC}")
        print("Install: https://cli.github.com/")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        if not check:
            return None
        print(f"{Colors.RED}❌ gh command failed: {e}{Colors.NC}")
        return None


def check_gh_auth() -> bool:
    """Check if authenticated with GitHub."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"{Colors.RED}❌ Not authenticated with GitHub{Colors.NC}")
        print(f"Run: {Colors.GREEN}gh auth login{Colors.NC}")
        return False
    return True


def get_existing_labels() -> List[str]:
    """Get list of existing label names."""
    output = run_gh_command(["label", "list", "--json", "name", "--jq", ".[].name"])
    if not output:
        return []
    return output.split("\n")


def create_label(name: str, color: str, description: str, force: bool = False) -> None:
    """Create or update a GitHub label."""
    existing_labels = get_existing_labels()

    if name in existing_labels:
        if force:
            print(f"{Colors.YELLOW}   ⟳ Updating: {name}{Colors.NC}")
            run_gh_command(["label", "edit", name, "--color", color, "--description", description], check=False)
        else:
            print(f"{Colors.GREEN}   ✓ Exists: {name}{Colors.NC}")
    else:
        print(f"{Colors.CYAN}   + Creating: {name}{Colors.NC}")
        result = subprocess.run(
            ["gh", "label", "create", name, "--color", color, "--description", description],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Label might have been created between check and create
            print(f"{Colors.YELLOW}   ⚠ Label may already exist: {name}{Colors.NC}")


def setup_labels(force: bool = False) -> None:
    """Set up all standard labels."""
    config = get_config()

    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║    🏷️  GitHub Label Setup for {config['project_name']:<26} ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.CYAN}Project: {config['project_name']}{Colors.NC}")
    print(f"{Colors.CYAN}Owner: {config['repo_owner']}{Colors.NC}")
    print()

    if not check_gh_auth():
        sys.exit(1)

    print(f"{Colors.CYAN}Setting up labels...{Colors.NC}")
    print()

    # Status Labels (Issue Lifecycle)
    print(f"{Colors.BLUE}[1/8]{Colors.NC} Status labels...")
    status_labels = [
        ("needs-triage", "d4c5f9", "New issue, not yet examined by maintainers"),
        ("examining", "d4c5f9", "Agent/maintainer is investigating this issue"),
        ("needs-reproduction", "fbca04", "Waiting for reproduction steps or more information"),
        ("cannot-reproduce", "cccccc", "Closed after 3 failed reproduction attempts"),
        ("reproduced", "0e8a16", "Successfully reproduced, issue confirmed"),
        ("verified", "0e8a16", "Issue confirmed valid and ready for work"),
        ("in-progress", "1d76db", "Agent/maintainer is actively working on this"),
        ("needs-review", "fbca04", "Fix ready, awaiting human review"),
        ("fixed", "0e8a16", "Fix merged and released"),
        ("wontfix", "ffffff", "This will not be worked on"),
    ]
    for name, color, description in status_labels:
        create_label(name, color, description, force)
    print()

    # Type Labels
    print(f"{Colors.BLUE}[2/8]{Colors.NC} Type labels...")
    type_labels = [
        ("bug", "d73a4a", "Something isn't working"),
        ("enhancement", "a2eeef", "New feature or request"),
        ("documentation", "0075ca", "Improvements or additions to documentation"),
        ("question", "d876e3", "Further information is requested"),
        ("duplicate", "cfd3d7", "This issue or pull request already exists"),
        ("invalid", "e4e669", "This doesn't seem right"),
        ("regression", "d93f0b", "Previously working feature is now broken"),
    ]
    for name, color, description in type_labels:
        create_label(name, color, description, force)
    print()

    # Priority Labels
    print(f"{Colors.BLUE}[3/8]{Colors.NC} Priority labels...")
    priority_labels = [
        ("priority:critical", "b60205", "Blocks users, needs immediate fix"),
        ("priority:high", "d93f0b", "Important, fix soon"),
        ("priority:medium", "fbca04", "Normal priority"),
        ("priority:low", "0e8a16", "Nice to have"),
    ]
    for name, color, description in priority_labels:
        create_label(name, color, description, force)
    print()

    # Component Labels
    print(f"{Colors.BLUE}[4/8]{Colors.NC} Component labels...")
    component_labels = [
        ("component:cli", "c5def5", "Command-line interface"),
        ("component:core", "c5def5", "Core logic and functionality"),
        ("component:api", "c5def5", "API and external interfaces"),
        ("component:validation", "c5def5", "Validation and error checking"),
        ("component:ui/ux", "c5def5", "User interface and experience"),
        ("component:tests", "c5def5", "Test suite and testing infrastructure"),
        ("component:ci/cd", "c5def5", "Build and release automation"),
        ("component:docs", "c5def5", "Documentation and guides"),
    ]
    for name, color, description in component_labels:
        create_label(name, color, description, force)
    print()

    # Effort Labels
    print(f"{Colors.BLUE}[5/8]{Colors.NC} Effort labels...")
    effort_labels = [
        ("effort:trivial", "bfdadc", "Less than 1 hour of work"),
        ("effort:small", "bfdadc", "1-4 hours of work"),
        ("effort:medium", "bfdadc", "1-2 days of work"),
        ("effort:large", "bfdadc", "3-5 days of work"),
        ("effort:epic", "bfdadc", "More than 1 week of work"),
    ]
    for name, color, description in effort_labels:
        create_label(name, color, description, force)
    print()

    # Contribution Labels
    print(f"{Colors.BLUE}[6/8]{Colors.NC} Contribution labels...")
    contribution_labels = [
        ("good first issue", "7057ff", "Good for newcomers"),
        ("help wanted", "008672", "Extra attention is needed"),
        ("agent-friendly", "7057ff", "Suitable for AI agent contribution"),
        ("needs-human", "d93f0b", "Requires human expertise, not agent-friendly"),
    ]
    for name, color, description in contribution_labels:
        create_label(name, color, description, force)
    print()

    # Platform Labels
    print(f"{Colors.BLUE}[7/8]{Colors.NC} Platform labels...")
    platform_labels = [
        ("platform:windows", "e99695", "Windows-specific issue"),
        ("platform:macos", "e99695", "macOS-specific issue"),
        ("platform:linux", "e99695", "Linux-specific issue"),
        ("platform:all", "e99695", "Affects all platforms"),
    ]
    for name, color, description in platform_labels:
        create_label(name, color, description, force)
    print()

    # Standard GitHub Labels
    print(f"{Colors.BLUE}[8/8]{Colors.NC} Standard GitHub labels...")
    standard_labels = [
        ("dependencies", "0366d6", "Pull requests that update a dependency file"),
        ("security", "d93f0b", "Security vulnerability or security-related issue"),
        ("performance", "d4c5f9", "Performance improvement"),
        ("breaking-change", "d93f0b", "Breaking change that requires major version bump"),
    ]
    for name, color, description in standard_labels:
        create_label(name, color, description, force)
    print()

    # Summary
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║              ✅ LABEL SETUP COMPLETE                      ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()

    # Count labels
    label_count = len(get_existing_labels())
    print(f"{Colors.CYAN}Total labels in repository:{Colors.NC} {label_count}")
    print()

    print(f"{Colors.BLUE}Label categories:{Colors.NC}")
    print("  • Status: 10 labels (needs-triage, examining, reproduced, etc.)")
    print("  • Type: 7 labels (bug, enhancement, documentation, etc.)")
    print("  • Priority: 4 labels (critical, high, medium, low)")
    print("  • Component: 8 labels (cli, core, api, validation, etc.)")
    print("  • Effort: 5 labels (trivial, small, medium, large, epic)")
    print("  • Contribution: 4 labels (good first issue, help wanted, etc.)")
    print("  • Platform: 4 labels (windows, macos, linux, all)")
    print("  • Standard: 4 labels (dependencies, security, performance, etc.)")
    print()

    print(f"{Colors.YELLOW}View all labels:{Colors.NC}")
    print(f"  {Colors.GREEN}gh label list{Colors.NC}")
    print()

    print(f"{Colors.YELLOW}Usage in issues:{Colors.NC}")
    print(f'  {Colors.GREEN}gh issue edit <number> --add-label "bug,priority:high,component:cli"{Colors.NC}')
    print()


def main():
    """Main entry point."""
    Colors.strip_colors()

    force = "--force" in sys.argv

    try:
        setup_labels(force)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
