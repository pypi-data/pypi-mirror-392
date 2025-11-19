#!/usr/bin/env bash
#
# CCPM Issue Abort Command
#
# Purpose: Abort work on issue and cleanup worktree
# Usage: ./issue-abort.sh <issue-number> [--force]
# Exit codes:
#   0 - Work aborted successfully
#   1 - Error occurred
#
# Steps:
#   1. Validate worktree exists
#   2. Show uncommitted changes (if any)
#   3. Confirm abort (unless --force)
#   4. Remove agent lock
#   5. Remove worktree
#   6. Log action
#
# Example:
#   ./issue-abort.sh 123
#   ./issue-abort.sh 123 --force  # Skip confirmation
#
# Author: CCPM Plugin
# Last updated: 2025-01-14

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arguments
ISSUE_NUMBER="${1:-}"
FORCE=false

if [[ "${2:-}" == "--force" ]]; then
    FORCE=true
fi

# Validation
if [[ -z "$ISSUE_NUMBER" ]]; then
    echo -e "${RED}❌ ERROR: Issue number required${NC}"
    echo "Usage: $0 <issue-number> [--force]"
    echo ""
    echo "Example:"
    echo "  $0 123"
    echo "  $0 123 --force  # Skip confirmation"
    exit 1
fi

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CCPM_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="${HOME}/.cache/svg2fbf-worktrees/issue-${ISSUE_NUMBER}"
LOCK_FILE="${WORKTREE_DIR}/.agent-lock"
METADATA_FILE="${WORKTREE_DIR}/.agent-metadata.json"

echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║              ⚠️  ABORTING WORK ON ISSUE                   ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Issue:${NC} #${ISSUE_NUMBER}"
echo ""

# ============================================================================
# Step 1: Validate worktree exists
# ============================================================================
echo -e "${YELLOW}Step 1/5:${NC} Validating worktree..."

if [[ ! -d "$WORKTREE_DIR" ]]; then
    echo -e "${RED}❌ Worktree not found: ${WORKTREE_DIR}${NC}"
    echo "   Use issue-status.sh to check active worktrees"
    exit 1
fi

# Read metadata
AGENT_ID="unknown"
TARGET_BRANCH="unknown"
if [[ -f "$METADATA_FILE" ]]; then
    AGENT_ID=$(jq -r '.agent_id' "$METADATA_FILE")
    TARGET_BRANCH=$(jq -r '.target_branch' "$METADATA_FILE")
fi

echo -e "${GREEN}   ✓ Worktree found${NC}"
echo "     Path: ${WORKTREE_DIR}"
echo "     Branch: ${TARGET_BRANCH}"
echo "     Agent: ${AGENT_ID}"

# ============================================================================
# Step 2: Check for uncommitted changes
# ============================================================================
echo -e "${YELLOW}Step 2/5:${NC} Checking for uncommitted changes..."

cd "$WORKTREE_DIR"

HAS_CHANGES=false
if ! git diff --quiet || ! git diff --cached --quiet; then
    HAS_CHANGES=true
    echo -e "${YELLOW}   ⚠️  Uncommitted changes detected:${NC}"
    echo ""
    git status --short
    echo ""
fi

# Check for unpushed commits
UNPUSHED_COMMITS=0
if git rev-parse "@{u}" &> /dev/null; then
    UNPUSHED_COMMITS=$(git rev-list --count "@{u}..HEAD")
    if [[ "$UNPUSHED_COMMITS" -gt 0 ]]; then
        echo -e "${YELLOW}   ⚠️  ${UNPUSHED_COMMITS} unpushed commit(s):${NC}"
        echo ""
        git log --oneline "@{u}..HEAD"
        echo ""
    fi
fi

if [[ "$HAS_CHANGES" == false ]] && [[ "$UNPUSHED_COMMITS" -eq 0 ]]; then
    echo -e "${GREEN}   ✓ No uncommitted changes or unpushed commits${NC}"
fi

# ============================================================================
# Step 3: Confirm abort (unless --force)
# ============================================================================
if [[ "$FORCE" == false ]]; then
    echo -e "${YELLOW}Step 3/5:${NC} Confirmation required..."
    echo ""
    echo -e "${RED}⚠️  WARNING: This will:${NC}"
    echo "   - Discard all uncommitted changes"
    if [[ "$UNPUSHED_COMMITS" -gt 0 ]]; then
        echo "   - Lose $UNPUSHED_COMMITS unpushed commit(s)"
    fi
    echo "   - Remove the worktree"
    echo "   - Cannot be undone"
    echo ""
    read -p "Are you sure you want to abort? (yes/no): " -r
    echo ""

    if [[ ! "$REPLY" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Abort cancelled${NC}"
        echo ""
        echo "To proceed with abort:"
        echo "  ${GREEN}$0 ${ISSUE_NUMBER} --force${NC}"
        exit 0
    fi
else
    echo -e "${YELLOW}Step 3/5:${NC} Skipping confirmation (--force flag)"
fi

# ============================================================================
# Step 4: Remove agent lock
# ============================================================================
echo -e "${YELLOW}Step 4/5:${NC} Removing agent lock..."

if [[ -f "$LOCK_FILE" ]]; then
    rm -f "$LOCK_FILE"
    echo -e "${GREEN}   ✓ Lock removed${NC}"
else
    echo -e "${YELLOW}   ⚠️  Lock file not found (may have been already removed)${NC}"
fi

# ============================================================================
# Step 5: Remove worktree
# ============================================================================
echo -e "${YELLOW}Step 5/5:${NC} Removing worktree..."

cd "$REPO_ROOT"

if git worktree remove "$WORKTREE_DIR" --force; then
    echo -e "${GREEN}   ✓ Worktree removed${NC}"
else
    echo -e "${RED}❌ Failed to remove worktree${NC}"
    echo "   Try manually: ${GREEN}git worktree remove ${WORKTREE_DIR} --force${NC}"
    exit 1
fi

# ============================================================================
# Step 6: Log action
# ============================================================================
echo -e "${YELLOW}Step 6/5:${NC} Logging abort action..."

export CCPM_AGENT_ID="${AGENT_ID}"
export CCPM_SESSION_ID="$$"

if [[ -x "${CCPM_DIR}/hooks/audit-log.sh" ]]; then
    "${CCPM_DIR}/hooks/audit-log.sh" worktree_remove "$WORKTREE_DIR"
    echo -e "${GREEN}   ✓ Action logged${NC}"
else
    echo -e "${YELLOW}   ⚠️  Audit log script not found, skipping${NC}"
fi

# ============================================================================
# Success Summary
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ WORK ABORTED SUCCESSFULLY                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Issue #${ISSUE_NUMBER} work has been aborted${NC}"
echo ""
echo -e "${BLUE}What was removed:${NC}"
if [[ "$HAS_CHANGES" == true ]]; then
    echo "  - Uncommitted changes (discarded)"
fi
if [[ "$UNPUSHED_COMMITS" -gt 0 ]]; then
    echo "  - $UNPUSHED_COMMITS unpushed commit(s) (lost)"
fi
echo "  - Agent lock file"
echo "  - Worktree: ${WORKTREE_DIR}"
echo ""

if [[ "$UNPUSHED_COMMITS" -gt 0 ]]; then
    echo -e "${YELLOW}Recovery:${NC}"
    echo "  If you need to recover lost commits:"
    echo "  1. Use git reflog in main repository:"
    echo "     ${GREEN}cd ${REPO_ROOT}${NC}"
    echo "     ${GREEN}git reflog${NC}"
    echo "  2. Find commit hash and cherry-pick:"
    echo "     ${GREEN}git cherry-pick <commit-hash>${NC}"
    echo "  3. See: ccpm/skills/recovery-procedures.md"
    echo ""
fi

echo -e "${BLUE}Next Steps:${NC}"
echo "  - Start new work: ${GREEN}${CCPM_DIR}/commands/issue-start.sh <issue-number>${NC}"
echo "  - Check active worktrees: ${GREEN}${CCPM_DIR}/commands/issue-status.sh${NC}"
echo ""

exit 0
