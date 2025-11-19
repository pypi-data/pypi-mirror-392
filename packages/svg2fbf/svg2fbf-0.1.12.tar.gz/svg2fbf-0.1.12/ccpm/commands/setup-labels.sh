#!/usr/bin/env bash
#
# GitHub Label Setup (CCPM Plugin)
#
# Purpose: Create standard labels for issue management in ANY GitHub repository
# Usage: ./setup-labels.sh [--force]
# Exit codes:
#   0 - Labels created/verified successfully
#   1 - Error occurred
#
# Options:
#   --force  Delete existing labels and recreate (DANGEROUS)
#
# Author: CCPM Plugin
# Last updated: 2025-01-17
# Project-Agnostic: Works with any GitHub repository

set -euo pipefail

# Load project configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/project-config.sh
source "${SCRIPT_DIR}/../lib/project-config.sh"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Arguments
FORCE=false
if [[ "${1:-}" == "--force" ]]; then
    FORCE=true
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
printf "${BLUE}║    🏷️  GitHub Label Setup for %-26s ║${NC}\n" "${PROJECT_NAME}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Project: ${PROJECT_NAME}${NC}"
echo -e "${CYAN}Owner: ${REPO_OWNER}${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub${NC}"
    echo "Run: ${GREEN}gh auth login${NC}"
    exit 1
fi

echo -e "${CYAN}Setting up labels...${NC}"
echo ""

# Function to create or update label
create_label() {
    local name="$1"
    local color="$2"
    local description="$3"

    # Check if label exists
    if gh label list --json name --jq '.[].name' | grep -q "^${name}$"; then
        if [[ "$FORCE" == true ]]; then
            echo -e "${YELLOW}   ⟳ Updating: ${name}${NC}"
            gh label edit "$name" --color "$color" --description "$description" 2>/dev/null || true
        else
            echo -e "${GREEN}   ✓ Exists: ${name}${NC}"
        fi
    else
        echo -e "${CYAN}   + Creating: ${name}${NC}"
        if ! gh label create "$name" --color "$color" --description "$description" 2>/dev/null; then
            # Label might have been created between check and create (race condition)
            # or might exist with different case - just note it exists
            echo -e "${YELLOW}   ⚠ Label may already exist: ${name}${NC}"
        fi
    fi
}

# ============================================================================
# Status Labels (Issue Lifecycle)
# ============================================================================
echo -e "${BLUE}[1/8]${NC} Status labels..."

create_label "needs-triage" "d4c5f9" "New issue, not yet examined by maintainers"
create_label "examining" "d4c5f9" "Agent/maintainer is investigating this issue"
create_label "needs-reproduction" "fbca04" "Waiting for reproduction steps or more information"
create_label "cannot-reproduce" "cccccc" "Closed after 3 failed reproduction attempts"
create_label "reproduced" "0e8a16" "Successfully reproduced, issue confirmed"
create_label "verified" "0e8a16" "Issue confirmed valid and ready for work"
create_label "in-progress" "1d76db" "Agent/maintainer is actively working on this"
create_label "needs-review" "fbca04" "Fix ready, awaiting human review"
create_label "fixed" "0e8a16" "Fix merged and released"
create_label "wontfix" "ffffff" "This will not be worked on"

echo ""

# ============================================================================
# Type Labels
# ============================================================================
echo -e "${BLUE}[2/8]${NC} Type labels..."

create_label "bug" "d73a4a" "Something isn't working"
create_label "enhancement" "a2eeef" "New feature or request"
create_label "documentation" "0075ca" "Improvements or additions to documentation"
create_label "question" "d876e3" "Further information is requested"
create_label "duplicate" "cfd3d7" "This issue or pull request already exists"
create_label "invalid" "e4e669" "This doesn't seem right"
create_label "regression" "d93f0b" "Previously working feature is now broken"

echo ""

# ============================================================================
# Priority Labels
# ============================================================================
echo -e "${BLUE}[3/8]${NC} Priority labels..."

create_label "priority:critical" "b60205" "Blocks users, needs immediate fix"
create_label "priority:high" "d93f0b" "Important, fix soon"
create_label "priority:medium" "fbca04" "Normal priority"
create_label "priority:low" "0e8a16" "Nice to have"

echo ""

# ============================================================================
# Component Labels
# ============================================================================
echo -e "${BLUE}[4/8]${NC} Component labels..."

create_label "component:cli" "c5def5" "Command-line interface"
create_label "component:svg-import" "c5def5" "SVG frame import and parsing"
create_label "component:fbf-generation" "c5def5" "FBF.SVG generation and output"
create_label "component:validation" "c5def5" "Validation and error checking"
create_label "component:ui/ux" "c5def5" "User interface and experience"
create_label "component:tests" "c5def5" "Test suite and testing infrastructure"
create_label "component:ci/cd" "c5def5" "Build and release automation"
create_label "component:docs" "c5def5" "Documentation and guides"

echo ""

# ============================================================================
# Effort Labels
# ============================================================================
echo -e "${BLUE}[5/8]${NC} Effort labels..."

create_label "effort:trivial" "bfdadc" "Less than 1 hour of work"
create_label "effort:small" "bfdadc" "1-4 hours of work"
create_label "effort:medium" "bfdadc" "1-2 days of work"
create_label "effort:large" "bfdadc" "3-5 days of work"
create_label "effort:epic" "bfdadc" "More than 1 week of work"

echo ""

# ============================================================================
# Good First Issue / Help Wanted
# ============================================================================
echo -e "${BLUE}[6/8]${NC} Contribution labels..."

create_label "good first issue" "7057ff" "Good for newcomers"
create_label "help wanted" "008672" "Extra attention is needed"
create_label "agent-friendly" "7057ff" "Suitable for AI agent contribution"
create_label "needs-human" "d93f0b" "Requires human expertise, not agent-friendly"

echo ""

# ============================================================================
# Platform Labels
# ============================================================================
echo -e "${BLUE}[7/8]${NC} Platform labels..."

create_label "platform:windows" "e99695" "Windows-specific issue"
create_label "platform:macos" "e99695" "macOS-specific issue"
create_label "platform:linux" "e99695" "Linux-specific issue"
create_label "platform:all" "e99695" "Affects all platforms"

echo ""

# ============================================================================
# Standard GitHub Labels (Preserve)
# ============================================================================
echo -e "${BLUE}[8/8]${NC} Standard GitHub labels..."

# These are default GitHub labels, update if they exist
create_label "dependencies" "0366d6" "Pull requests that update a dependency file"
create_label "security" "d93f0b" "Security vulnerability or security-related issue"
create_label "performance" "d4c5f9" "Performance improvement"
create_label "breaking-change" "d93f0b" "Breaking change that requires major version bump"

echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ LABEL SETUP COMPLETE                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Count labels
label_count=$(gh label list --json name --jq 'length')
echo -e "${CYAN}Total labels in repository:${NC} ${label_count}"
echo ""

echo -e "${BLUE}Label categories:${NC}"
echo "  • Status: 10 labels (needs-triage, examining, reproduced, etc.)"
echo "  • Type: 7 labels (bug, enhancement, documentation, etc.)"
echo "  • Priority: 4 labels (critical, high, medium, low)"
echo "  • Component: 8 labels (cli, svg-import, fbf-generation, etc.)"
echo "  • Effort: 5 labels (trivial, small, medium, large, epic)"
echo "  • Contribution: 4 labels (good first issue, help wanted, etc.)"
echo "  • Platform: 4 labels (windows, macos, linux, all)"
echo "  • Standard: 4 labels (dependencies, security, performance, etc.)"
echo ""

echo -e "${YELLOW}View all labels:${NC}"
echo "  ${GREEN}gh label list${NC}"
echo ""

echo -e "${YELLOW}Usage in issues:${NC}"
echo "  ${GREEN}gh issue edit <number> --add-label \"bug,priority:high,component:cli\"${NC}"
echo ""

exit 0
