#!/usr/bin/env bash
#
# CCPM Issue Start Command
#
# Purpose: Start work on a GitHub issue in isolated worktree
# Usage: ./issue-start.sh <issue-number> [target-branch]
# Exit codes:
#   0 - Worktree created successfully
#   1 - Error occurred
#
# Steps:
#   1. Run pre-flight checks
#   2. Create worktree from target branch
#   3. Create mutex lock file
#   4. Create metadata file
#   5. Log action
#   6. Install pre-commit hook
#
# Example:
#   ./issue-start.sh 123 dev
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

# Validation
if [[ -z "$ISSUE_NUMBER" ]]; then
    echo -e "${RED}❌ ERROR: Issue number required${NC}"
    echo "Usage: $0 <issue-number> [target-branch]"
    echo ""
    echo "Example:"
    echo "  $0 123 dev"
    exit 1
fi

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CCPM_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="${HOME}/.cache/svg2fbf-worktrees/issue-${ISSUE_NUMBER}"
LOCK_FILE="${WORKTREE_DIR}/.agent-lock"
METADATA_FILE="${WORKTREE_DIR}/.agent-metadata.json"

# Agent info
AGENT_ID="${CCPM_AGENT_ID:-agent-$$}"
AGENT_SESSION="$$"
STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              🚀 STARTING WORK ON ISSUE                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Issue:${NC} #${ISSUE_NUMBER}"
echo -e "${BLUE}Branch:${NC} ${TARGET_BRANCH}"
echo -e "${BLUE}Agent:${NC} ${AGENT_ID}"
echo ""

# ============================================================================
# Step 1: Run pre-flight checks
# ============================================================================
echo -e "${YELLOW}Step 1/6:${NC} Running pre-flight safety checks..."
echo ""

if [[ -x "${CCPM_DIR}/hooks/pre-flight-check.sh" ]]; then
    if ! "${CCPM_DIR}/hooks/pre-flight-check.sh" "$ISSUE_NUMBER" "$TARGET_BRANCH"; then
        echo -e "${RED}❌ Pre-flight checks failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Pre-flight check script not found, skipping${NC}"
fi

echo ""

# ============================================================================
# Step 2: Create worktree
# ============================================================================
echo -e "${YELLOW}Step 2/6:${NC} Creating worktree..."

# Check if worktree already exists
if [[ -d "$WORKTREE_DIR" ]]; then
    echo -e "${RED}❌ Worktree already exists: ${WORKTREE_DIR}${NC}"
    echo "   Use issue-status.sh to check active worktrees"
    echo "   Or use issue-abort.sh to remove stale worktree"
    exit 1
fi

# Create parent directory
mkdir -p "$(dirname "$WORKTREE_DIR")"

# Create worktree
cd "$REPO_ROOT"
if git worktree add "$WORKTREE_DIR" "$TARGET_BRANCH"; then
    echo -e "${GREEN}   ✓ Worktree created at: ${WORKTREE_DIR}${NC}"
else
    echo -e "${RED}❌ Failed to create worktree${NC}"
    exit 1
fi

# ============================================================================
# Step 3: Create mutex lock file
# ============================================================================
echo -e "${YELLOW}Step 3/6:${NC} Creating agent lock..."

cat > "$LOCK_FILE" <<EOF
{
  "agent_id": "$AGENT_ID",
  "session_id": "$AGENT_SESSION",
  "pid": $$,
  "issue_number": $ISSUE_NUMBER,
  "target_branch": "$TARGET_BRANCH",
  "started": "$STARTED_AT",
  "hostname": "$(hostname)",
  "user": "$(whoami)"
}
EOF

echo -e "${GREEN}   ✓ Lock file created${NC}"

# ============================================================================
# Step 4: Create metadata file
# ============================================================================
echo -e "${YELLOW}Step 4/6:${NC} Creating metadata..."

# Get issue info from GitHub (if gh available)
ISSUE_TITLE="Unknown"
ISSUE_ASSIGNEE="Unknown"
if command -v gh &> /dev/null; then
    if issue_info=$(gh issue view "$ISSUE_NUMBER" --json title,assignees 2>/dev/null); then
        ISSUE_TITLE=$(echo "$issue_info" | jq -r '.title')
        ISSUE_ASSIGNEE=$(echo "$issue_info" | jq -r '.assignees[0].login // "Unassigned"')
    fi
fi

cat > "$METADATA_FILE" <<EOF
{
  "issue_number": $ISSUE_NUMBER,
  "issue_title": "$ISSUE_TITLE",
  "issue_assignee": "$ISSUE_ASSIGNEE",
  "target_branch": "$TARGET_BRANCH",
  "worktree_path": "$WORKTREE_DIR",
  "created_at": "$STARTED_AT",
  "agent_id": "$AGENT_ID",
  "session_id": "$AGENT_SESSION"
}
EOF

echo -e "${GREEN}   ✓ Metadata file created${NC}"

# ============================================================================
# Step 5: Install pre-commit hook
# ============================================================================
echo -e "${YELLOW}Step 5/6:${NC} Installing pre-commit hook..."

# Create symlink to pre-commit-safety.sh in worktree
WORKTREE_HOOK_DIR="${WORKTREE_DIR}/.git/hooks"
mkdir -p "$WORKTREE_HOOK_DIR"

if [[ -x "${CCPM_DIR}/hooks/pre-commit-safety.sh" ]]; then
    ln -sf "${CCPM_DIR}/hooks/pre-commit-safety.sh" "${WORKTREE_HOOK_DIR}/pre-commit"
    chmod +x "${WORKTREE_HOOK_DIR}/pre-commit"
    echo -e "${GREEN}   ✓ Pre-commit hook installed${NC}"
else
    echo -e "${YELLOW}   ⚠️  Pre-commit hook not found, skipping${NC}"
fi

# ============================================================================
# Step 6: Log action
# ============================================================================
echo -e "${YELLOW}Step 6/6:${NC} Logging action..."

export CCPM_AGENT_ID="$AGENT_ID"
export CCPM_SESSION_ID="$AGENT_SESSION"

if [[ -x "${CCPM_DIR}/hooks/audit-log.sh" ]]; then
    "${CCPM_DIR}/hooks/audit-log.sh" worktree_create "$WORKTREE_DIR" "$ISSUE_NUMBER"
    echo -e "${GREEN}   ✓ Action logged${NC}"
else
    echo -e "${YELLOW}   ⚠️  Audit log script not found, skipping${NC}"
fi

# ============================================================================
# Success Summary
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ WORKTREE CREATED SUCCESSFULLY             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Issue #${ISSUE_NUMBER} workspace is ready!${NC}"
echo ""
echo -e "${BLUE}Worktree Location:${NC}"
echo "  ${WORKTREE_DIR}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Change to worktree:"
echo "     ${GREEN}cd ${WORKTREE_DIR}${NC}"
echo ""
echo "  2. Start working on the issue:"
echo "     ${GREEN}# Edit files, make changes${NC}"
echo ""
echo "  3. Commit your changes:"
echo "     ${GREEN}git add .${NC}"
echo "     ${GREEN}git commit -m \"feat(scope): Description for issue #${ISSUE_NUMBER}\"${NC}"
echo ""
echo "  4. Run quality checks:"
echo "     ${GREEN}${CCPM_DIR}/hooks/post-flight-check.sh${NC}"
echo ""
echo "  5. Finish work and create PR:"
echo "     ${GREEN}${CCPM_DIR}/commands/issue-finish.sh ${ISSUE_NUMBER}${NC}"
echo ""
echo -e "${YELLOW}Remember:${NC}"
echo "  - Follow conventional commit format"
echo "  - Run tests before committing"
echo "  - Never modify protected files (see ccpm/rules/protected-files.txt)"
echo "  - Use ${GREEN}issue-status.sh${NC} to check worktree status"
echo ""

exit 0
