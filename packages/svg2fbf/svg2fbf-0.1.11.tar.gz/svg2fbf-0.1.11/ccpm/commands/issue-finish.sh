#!/usr/bin/env bash
#
# CCPM Issue Finish Command
#
# Purpose: Complete work on issue, push changes, create PR
# Usage: ./issue-finish.sh <issue-number> [--keep-worktree]
# Exit codes:
#   0 - Work completed successfully
#   1 - Error occurred
#
# Steps:
#   1. Validate worktree exists
#   2. Run post-flight quality checks
#   3. Push commits to origin
#   4. Create Draft PR
#   5. Remove agent lock
#   6. Optionally remove worktree
#   7. Log action
#
# Example:
#   ./issue-finish.sh 123
#   ./issue-finish.sh 123 --keep-worktree
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
KEEP_WORKTREE=false

if [[ "${2:-}" == "--keep-worktree" ]]; then
    KEEP_WORKTREE=true
fi

# Validation
if [[ -z "$ISSUE_NUMBER" ]]; then
    echo -e "${RED}❌ ERROR: Issue number required${NC}"
    echo "Usage: $0 <issue-number> [--keep-worktree]"
    echo ""
    echo "Example:"
    echo "  $0 123"
    echo "  $0 123 --keep-worktree  # Keep worktree after finishing"
    exit 1
fi

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CCPM_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="${HOME}/.cache/svg2fbf-worktrees/issue-${ISSUE_NUMBER}"
LOCK_FILE="${WORKTREE_DIR}/.agent-lock"
METADATA_FILE="${WORKTREE_DIR}/.agent-metadata.json"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            🏁 FINISHING WORK ON ISSUE                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Issue:${NC} #${ISSUE_NUMBER}"
echo ""

# ============================================================================
# Step 1: Validate worktree exists
# ============================================================================
echo -e "${YELLOW}Step 1/7:${NC} Validating worktree..."

if [[ ! -d "$WORKTREE_DIR" ]]; then
    echo -e "${RED}❌ Worktree not found: ${WORKTREE_DIR}${NC}"
    echo "   Use issue-status.sh to check active worktrees"
    exit 1
fi

# Read metadata
if [[ -f "$METADATA_FILE" ]]; then
    TARGET_BRANCH=$(jq -r '.target_branch' "$METADATA_FILE")
    AGENT_ID=$(jq -r '.agent_id' "$METADATA_FILE")
    echo -e "${GREEN}   ✓ Worktree found${NC}"
    echo "     Branch: $TARGET_BRANCH"
    echo "     Agent: $AGENT_ID"
else
    echo -e "${YELLOW}   ⚠️  Metadata file not found, continuing anyway${NC}"
    TARGET_BRANCH="unknown"
    AGENT_ID="unknown"
fi

# ============================================================================
# Step 2: Run post-flight quality checks
# ============================================================================
echo -e "${YELLOW}Step 2/7:${NC} Running quality checks..."
echo ""

cd "$WORKTREE_DIR"

if [[ -x "${CCPM_DIR}/hooks/post-flight-check.sh" ]]; then
    if ! "${CCPM_DIR}/hooks/post-flight-check.sh"; then
        echo ""
        echo -e "${RED}❌ Quality checks failed${NC}"
        echo ""
        echo "   ${YELLOW}Options:${NC}"
        echo "   1. Fix issues and re-run: ${GREEN}$0 ${ISSUE_NUMBER}${NC}"
        echo "   2. Auto-fix: ${GREEN}${CCPM_DIR}/hooks/post-flight-check.sh --fix${NC}"
        echo "   3. Abort work: ${GREEN}${CCPM_DIR}/commands/issue-abort.sh ${ISSUE_NUMBER}${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}   ⚠️  Post-flight check script not found, skipping${NC}"
fi

echo ""

# ============================================================================
# Step 3: Push commits to origin
# ============================================================================
echo -e "${YELLOW}Step 3/7:${NC} Pushing commits..."

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${RED}❌ Uncommitted changes detected${NC}"
    echo ""
    git status --short
    echo ""
    echo "   ${YELLOW}Commit changes first:${NC}"
    echo "   ${GREEN}git add .${NC}"
    echo "   ${GREEN}git commit -m \"type(scope): Description\"${NC}"
    exit 1
fi

# Check if there are commits to push
if git rev-parse "@{u}" &> /dev/null; then
    # Upstream exists, check if ahead
    commits_ahead=$(git rev-list --count "@{u}..HEAD")
    if [[ "$commits_ahead" -eq 0 ]]; then
        echo -e "${YELLOW}   ⚠️  No new commits to push${NC}"
    else
        echo "   Pushing $commits_ahead commit(s)..."
        if git push origin "$CURRENT_BRANCH"; then
            echo -e "${GREEN}   ✓ Pushed successfully${NC}"
        else
            echo -e "${RED}❌ Push failed${NC}"
            exit 1
        fi
    fi
else
    # No upstream, set it and push
    echo "   Setting upstream and pushing..."
    if git push -u origin "$CURRENT_BRANCH"; then
        echo -e "${GREEN}   ✓ Pushed successfully${NC}"
    else
        echo -e "${RED}❌ Push failed${NC}"
        exit 1
    fi
fi

# ============================================================================
# Step 4: Create Draft PR
# ============================================================================
echo -e "${YELLOW}Step 4/7:${NC} Creating Pull Request..."

if command -v gh &> /dev/null; then
    # Check if PR already exists
    existing_pr=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number // ""')

    if [[ -n "$existing_pr" ]]; then
        echo -e "${YELLOW}   ⚠️  PR already exists: #${existing_pr}${NC}"
        echo "     ${GREEN}https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pull/${existing_pr}${NC}"
    else
        # Get issue info for PR title/body
        issue_title=""
        if issue_info=$(gh issue view "$ISSUE_NUMBER" --json title 2>/dev/null); then
            issue_title=$(echo "$issue_info" | jq -r '.title')
        fi

        # Create PR title
        pr_title="Fix #${ISSUE_NUMBER}: ${issue_title}"

        # Create PR body
        pr_body="Fixes #${ISSUE_NUMBER}

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
- Agent ID: ${AGENT_ID}
- Branch: ${CURRENT_BRANCH}
- Target: ${TARGET_BRANCH}
"

        # Create draft PR
        if pr_url=$(gh pr create \
            --draft \
            --title "$pr_title" \
            --body "$pr_body" \
            --base "$TARGET_BRANCH" \
            2>&1); then

            pr_number=$(echo "$pr_url" | grep -oE '[0-9]+$')
            echo -e "${GREEN}   ✓ Draft PR created: #${pr_number}${NC}"
            echo "     ${GREEN}${pr_url}${NC}"
        else
            echo -e "${RED}❌ Failed to create PR${NC}"
            echo "   Error: $pr_url"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}   ⚠️  GitHub CLI not installed, skipping PR creation${NC}"
    echo "   Install: ${GREEN}brew install gh${NC}"
fi

# ============================================================================
# Step 5: Remove agent lock
# ============================================================================
echo -e "${YELLOW}Step 5/7:${NC} Removing agent lock..."

if [[ -f "$LOCK_FILE" ]]; then
    rm -f "$LOCK_FILE"
    echo -e "${GREEN}   ✓ Lock removed${NC}"
else
    echo -e "${YELLOW}   ⚠️  Lock file not found${NC}"
fi

# ============================================================================
# Step 6: Optionally remove worktree
# ============================================================================
echo -e "${YELLOW}Step 6/7:${NC} Cleaning up worktree..."

if [[ "$KEEP_WORKTREE" == true ]]; then
    echo -e "${YELLOW}   ⚠️  Keeping worktree (--keep-worktree flag)${NC}"
    echo "     Worktree: ${WORKTREE_DIR}"
    echo "     Remove later with: ${GREEN}git worktree remove ${WORKTREE_DIR}${NC}"
else
    cd "$REPO_ROOT"
    if git worktree remove "$WORKTREE_DIR" --force; then
        echo -e "${GREEN}   ✓ Worktree removed${NC}"
    else
        echo -e "${RED}❌ Failed to remove worktree${NC}"
        echo "   Remove manually: ${GREEN}git worktree remove ${WORKTREE_DIR}${NC}"
    fi
fi

# ============================================================================
# Step 7: Log action
# ============================================================================
echo -e "${YELLOW}Step 7/7:${NC} Logging action..."

export CCPM_AGENT_ID="${AGENT_ID}"
export CCPM_SESSION_ID="$$"

if [[ -x "${CCPM_DIR}/hooks/audit-log.sh" ]]; then
    "${CCPM_DIR}/hooks/audit-log.sh" pr_create "$pr_number" "$pr_title" "true"
    echo -e "${GREEN}   ✓ Action logged${NC}"
else
    echo -e "${YELLOW}   ⚠️  Audit log script not found, skipping${NC}"
fi

# ============================================================================
# Success Summary
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ WORK COMPLETED SUCCESSFULLY               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Issue #${ISSUE_NUMBER} work is complete!${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  - Commits pushed to: ${CURRENT_BRANCH}"
echo "  - Draft PR created: #${pr_number:-N/A}"
echo "  - Agent lock removed"
if [[ "$KEEP_WORKTREE" == true ]]; then
    echo "  - Worktree preserved: ${WORKTREE_DIR}"
else
    echo "  - Worktree removed"
fi
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review the PR on GitHub"
echo "  2. Request review from maintainer"
echo "  3. Wait for CI checks to pass"
echo "  4. Address any feedback"
echo "  5. Convert to Ready for Review when ready"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  - DO NOT merge your own PR"
echo "  - Wait for human review and approval"
echo "  - Monitor CI checks for failures"
echo ""

exit 0
