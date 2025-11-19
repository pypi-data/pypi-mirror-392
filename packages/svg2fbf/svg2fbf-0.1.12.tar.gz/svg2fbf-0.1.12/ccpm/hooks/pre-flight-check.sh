#!/usr/bin/env bash
#
# Pre-Flight Safety Check for CCPM Agents
#
# Purpose: Validate preconditions before agent starts work on an issue
# Usage: ./pre-flight-check.sh <issue-number> <target-branch>
# Exit codes:
#   0 - All checks passed, safe to proceed
#   1 - Check failed, cannot proceed
#
# Checks performed:
#   1. Issue exists and is assigned
#   2. No conflicting agent lock exists
#   3. Target branch is allowed (not master/main/review)
#   4. No conflicting PRs for same issue
#   5. Repository state is clean
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
TARGET_BRANCH="${2:-dev}"

# Paths
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="${HOME}/.cache/svg2fbf-worktrees/issue-${ISSUE_NUMBER}"
LOCK_FILE="${WORKTREE_DIR}/.agent-lock"

# Validation
if [[ -z "$ISSUE_NUMBER" ]]; then
    echo -e "${RED}❌ ERROR: Issue number required${NC}"
    echo "Usage: $0 <issue-number> [target-branch]"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🛫 PRE-FLIGHT SAFETY CHECK                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Issue:${NC} #${ISSUE_NUMBER}"
echo -e "${BLUE}Target Branch:${NC} ${TARGET_BRANCH}"
echo ""

# ============================================================================
# Check 1: Issue exists and is assigned
# ============================================================================
echo -e "${YELLOW}[1/6]${NC} Checking issue exists and is assigned..."

if command -v gh &> /dev/null; then
    # Get issue info
    if ! issue_info=$(gh issue view "$ISSUE_NUMBER" --json number,title,state,assignees 2>&1); then
        echo -e "${RED}   ✗ Issue #${ISSUE_NUMBER} not found${NC}"
        echo "   Run: gh issue view ${ISSUE_NUMBER}"
        exit 1
    fi

    # Parse issue state
    issue_state=$(echo "$issue_info" | jq -r '.state')
    if [[ "$issue_state" == "CLOSED" ]]; then
        echo -e "${RED}   ✗ Issue #${ISSUE_NUMBER} is already closed${NC}"
        echo "   Cannot work on closed issues"
        exit 1
    fi

    # Check if assigned
    assignee_count=$(echo "$issue_info" | jq '.assignees | length')
    if [[ "$assignee_count" -eq 0 ]]; then
        echo -e "${YELLOW}   ⚠️  Issue #${ISSUE_NUMBER} is not assigned${NC}"
        echo "   Consider assigning to yourself first:"
        echo "   ${GREEN}gh issue edit ${ISSUE_NUMBER} --add-assignee @me${NC}"
        # Warning only, not blocking
    else
        assignee=$(echo "$issue_info" | jq -r '.assignees[0].login')
        echo -e "${GREEN}   ✓ Issue assigned to: ${assignee}${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  GitHub CLI not installed, skipping issue check${NC}"
fi

# ============================================================================
# Check 2: No conflicting agent lock exists
# ============================================================================
echo -e "${YELLOW}[2/6]${NC} Checking for conflicting agent locks..."

if [[ -f "$LOCK_FILE" ]]; then
    # Read lock info
    agent_id=$(jq -r '.agent_id // "unknown"' "$LOCK_FILE")
    lock_pid=$(jq -r '.pid // 0' "$LOCK_FILE")
    started=$(jq -r '.started // "unknown"' "$LOCK_FILE")

    # Check if process still alive
    if ps -p "$lock_pid" > /dev/null 2>&1; then
        echo -e "${RED}   ✗ Another agent is currently working on this issue${NC}"
        echo "   Agent ID: $agent_id"
        echo "   PID: $lock_pid"
        echo "   Started: $started"
        echo ""
        echo "   ${YELLOW}Cannot proceed while another agent holds the lock${NC}"
        echo ""
        echo "   If this is a stale lock (agent crashed):"
        echo "   ${GREEN}rm ${LOCK_FILE}${NC}"
        exit 1
    else
        echo -e "${YELLOW}   ⚠️  Stale lock detected (process ${lock_pid} not running)${NC}"
        echo "   Removing stale lock..."
        rm -f "$LOCK_FILE"
        echo -e "${GREEN}   ✓ Stale lock removed${NC}"
    fi
else
    echo -e "${GREEN}   ✓ No conflicting locks${NC}"
fi

# ============================================================================
# Check 3: Target branch is allowed
# ============================================================================
echo -e "${YELLOW}[3/6]${NC} Validating target branch..."

FORBIDDEN_BRANCHES=("master" "main" "review")
for forbidden in "${FORBIDDEN_BRANCHES[@]}"; do
    if [[ "$TARGET_BRANCH" == "$forbidden" ]]; then
        echo -e "${RED}   ✗ Cannot start work on protected branch: ${forbidden}${NC}"
        echo ""
        echo "   Agents are NOT allowed to work directly on:"
        echo "   - master (stable releases)"
        echo "   - main (protected default branch)"
        echo "   - review (release candidates)"
        echo ""
        echo "   ${GREEN}Use dev or testing instead:${NC}"
        echo "   $0 ${ISSUE_NUMBER} dev"
        exit 1
    fi
done

ALLOWED_BRANCHES=("dev" "testing")
branch_allowed=false
for allowed in "${ALLOWED_BRANCHES[@]}"; do
    if [[ "$TARGET_BRANCH" == "$allowed" ]]; then
        branch_allowed=true
        break
    fi
done

# Also allow hotfix branches
if [[ "$TARGET_BRANCH" =~ ^hotfix/ ]]; then
    branch_allowed=true
    echo -e "${YELLOW}   ⚠️  Working on hotfix branch (requires supervision)${NC}"
fi

if [[ "$branch_allowed" == false ]]; then
    echo -e "${RED}   ✗ Invalid target branch: ${TARGET_BRANCH}${NC}"
    echo "   Allowed branches: dev, testing, hotfix/*"
    exit 1
fi

echo -e "${GREEN}   ✓ Target branch allowed: ${TARGET_BRANCH}${NC}"

# ============================================================================
# Check 4: No conflicting PRs for same issue
# ============================================================================
echo -e "${YELLOW}[4/6]${NC} Checking for conflicting pull requests..."

if command -v gh &> /dev/null; then
    # Search for PRs mentioning this issue
    pr_count=$(gh pr list --search "in:title,body #${ISSUE_NUMBER}" --json number --jq 'length')

    if [[ "$pr_count" -gt 0 ]]; then
        echo -e "${YELLOW}   ⚠️  Found ${pr_count} existing PR(s) for issue #${ISSUE_NUMBER}${NC}"

        # List PRs
        gh pr list --search "in:title,body #${ISSUE_NUMBER}" --json number,title,state,headRefName

        echo ""
        echo "   ${YELLOW}Proceed with caution:${NC}"
        echo "   - You may be duplicating work"
        echo "   - Consider coordinating with PR author"
        echo "   - Or continue if you're updating an existing PR"
        # Warning only, not blocking
    else
        echo -e "${GREEN}   ✓ No conflicting PRs found${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  GitHub CLI not installed, skipping PR check${NC}"
fi

# ============================================================================
# Check 5: Repository state is clean
# ============================================================================
echo -e "${YELLOW}[5/6]${NC} Checking repository state..."

cd "$REPO_ROOT"

# Check for uncommitted changes in main repo
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${YELLOW}   ⚠️  Main repository has uncommitted changes${NC}"
    echo ""
    git status --short
    echo ""
    echo "   ${YELLOW}This won't block worktree creation, but consider:${NC}"
    echo "   - Committing changes: ${GREEN}git add . && git commit${NC}"
    echo "   - Stashing changes: ${GREEN}git stash${NC}"
    # Warning only, not blocking
else
    echo -e "${GREEN}   ✓ Repository state is clean${NC}"
fi

# ============================================================================
# Check 6: Target branch exists and is up-to-date
# ============================================================================
echo -e "${YELLOW}[6/6]${NC} Checking target branch status..."

# Fetch latest
git fetch origin --quiet

# Check if branch exists
if ! git rev-parse --verify "origin/${TARGET_BRANCH}" &> /dev/null; then
    echo -e "${RED}   ✗ Branch ${TARGET_BRANCH} does not exist on origin${NC}"
    echo "   Available branches:"
    git branch -r | grep -v HEAD
    exit 1
fi

# Check if local branch is behind origin
if git rev-parse --verify "${TARGET_BRANCH}" &> /dev/null; then
    local_hash=$(git rev-parse "${TARGET_BRANCH}")
    remote_hash=$(git rev-parse "origin/${TARGET_BRANCH}")

    if [[ "$local_hash" != "$remote_hash" ]]; then
        echo -e "${YELLOW}   ⚠️  Local ${TARGET_BRANCH} branch is out of sync with origin${NC}"
        echo "   Updating local branch..."
        git checkout "${TARGET_BRANCH}" --quiet
        git pull origin "${TARGET_BRANCH}" --quiet
        echo -e "${GREEN}   ✓ Branch updated${NC}"
    else
        echo -e "${GREEN}   ✓ Branch is up-to-date${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Local ${TARGET_BRANCH} branch doesn't exist, will be created${NC}"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ PRE-FLIGHT CHECK PASSED                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Safe to proceed with:${NC}"
echo "   Issue: #${ISSUE_NUMBER}"
echo "   Branch: ${TARGET_BRANCH}"
echo "   Worktree: ${WORKTREE_DIR}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "   1. Create worktree: ${GREEN}git worktree add ${WORKTREE_DIR} ${TARGET_BRANCH}${NC}"
echo "   2. Create lock file: ${GREEN}echo '{\"agent_id\":\"...\"}' > ${LOCK_FILE}${NC}"
echo "   3. Start work on issue"
echo ""

exit 0
