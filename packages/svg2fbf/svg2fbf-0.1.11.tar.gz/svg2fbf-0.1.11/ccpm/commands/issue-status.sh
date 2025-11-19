#!/usr/bin/env bash
#
# CCPM Issue Status Command
#
# Purpose: Show status of all active issue worktrees
# Usage: ./issue-status.sh [--verbose]
# Exit codes:
#   0 - Success
#   1 - Error occurred
#
# Shows:
#   - List of all active worktrees
#   - Issue numbers and titles
#   - Agent IDs and lock status
#   - Branches and commit status
#   - Uncommitted changes
#   - Stale lock detection
#
# Example:
#   ./issue-status.sh
#   ./issue-status.sh --verbose
#
# Author: CCPM Plugin
# Last updated: 2025-01-14

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Arguments
VERBOSE=false
if [[ "${1:-}" == "--verbose" ]]; then
    VERBOSE=true
fi

# Paths
WORKTREE_BASE="${HOME}/.cache/svg2fbf-worktrees"
REPO_ROOT="$(git rev-parse --show-toplevel)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            📊 ACTIVE ISSUE WORKTREES STATUS               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if worktree directory exists
if [[ ! -d "$WORKTREE_BASE" ]]; then
    echo -e "${YELLOW}No worktrees found${NC}"
    echo "   Directory does not exist: ${WORKTREE_BASE}"
    echo ""
    echo "   Start new work with:"
    echo "   ${GREEN}ccpm/commands/issue-start.sh <issue-number>${NC}"
    exit 0
fi

# Find all worktrees
worktrees=()
for dir in "$WORKTREE_BASE"/issue-*; do
    if [[ -d "$dir" ]]; then
        worktrees+=("$dir")
    fi
done

# Check if any worktrees found
if [[ ${#worktrees[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No active worktrees${NC}"
    echo ""
    echo "   Start new work with:"
    echo "   ${GREEN}ccpm/commands/issue-start.sh <issue-number>${NC}"
    exit 0
fi

echo -e "${CYAN}Found ${#worktrees[@]} active worktree(s)${NC}"
echo ""

# Process each worktree
for worktree_dir in "${worktrees[@]}"; do
    issue_number=$(basename "$worktree_dir" | sed 's/issue-//')

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Issue #${issue_number}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Read metadata
    metadata_file="${worktree_dir}/.agent-metadata.json"
    lock_file="${worktree_dir}/.agent-lock"

    if [[ -f "$metadata_file" ]]; then
        issue_title=$(jq -r '.issue_title // "Unknown"' "$metadata_file")
        target_branch=$(jq -r '.target_branch // "unknown"' "$metadata_file")
        agent_id=$(jq -r '.agent_id // "unknown"' "$metadata_file")
        created_at=$(jq -r '.created_at // "unknown"' "$metadata_file")

        echo -e "${YELLOW}Title:${NC} ${issue_title}"
        echo -e "${YELLOW}Branch:${NC} ${target_branch}"
        echo -e "${YELLOW}Agent:${NC} ${agent_id}"
        echo -e "${YELLOW}Created:${NC} ${created_at}"
    else
        echo -e "${YELLOW}⚠️  Metadata file not found${NC}"
    fi

    # Check lock status
    echo ""
    if [[ -f "$lock_file" ]]; then
        lock_pid=$(jq -r '.pid // 0' "$lock_file")
        lock_agent=$(jq -r '.agent_id // "unknown"' "$lock_file")
        lock_started=$(jq -r '.started // "unknown"' "$lock_file")

        if ps -p "$lock_pid" > /dev/null 2>&1; then
            echo -e "${GREEN}🔒 Lock Status:${NC} Active"
            echo -e "   Agent: ${lock_agent}"
            echo -e "   PID: ${lock_pid}"
            echo -e "   Started: ${lock_started}"
        else
            echo -e "${RED}🔒 Lock Status:${NC} Stale (process not running)"
            echo -e "   Agent: ${lock_agent}"
            echo -e "   PID: ${lock_pid} (dead)"
            echo -e "   Started: ${lock_started}"
            echo ""
            echo -e "${YELLOW}   Remove stale lock:${NC}"
            echo -e "   ${GREEN}rm ${lock_file}${NC}"
        fi
    else
        echo -e "${YELLOW}🔒 Lock Status:${NC} No lock (possibly finished or aborted)"
    fi

    # Git status
    echo ""
    if [[ -d "${worktree_dir}/.git" ]]; then
        cd "$worktree_dir"

        current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        echo -e "${YELLOW}Current Branch:${NC} ${current_branch}"

        # Check for uncommitted changes
        if ! git diff --quiet || ! git diff --cached --quiet; then
            echo -e "${YELLOW}Uncommitted Changes:${NC} Yes"
            if [[ "$VERBOSE" == true ]]; then
                echo ""
                git status --short
            fi
        else
            echo -e "${GREEN}Uncommitted Changes:${NC} No"
        fi

        # Check for unpushed commits
        if git rev-parse "@{u}" &> /dev/null 2>&1; then
            commits_ahead=$(git rev-list --count "@{u}..HEAD" 2>/dev/null || echo "0")
            if [[ "$commits_ahead" -gt 0 ]]; then
                echo -e "${YELLOW}Unpushed Commits:${NC} ${commits_ahead}"
                if [[ "$VERBOSE" == true ]]; then
                    echo ""
                    git log --oneline "@{u}..HEAD"
                fi
            else
                echo -e "${GREEN}Unpushed Commits:${NC} 0"
            fi
        else
            echo -e "${YELLOW}Upstream:${NC} Not set"
        fi

        # Last commit
        last_commit=$(git log -1 --oneline 2>/dev/null || echo "No commits")
        echo -e "${YELLOW}Last Commit:${NC} ${last_commit}"

    else
        echo -e "${RED}⚠️  Not a valid git worktree${NC}"
    fi

    # Check for associated PRs
    echo ""
    if command -v gh &> /dev/null; then
        pr_list=$(gh pr list --search "in:title,body #${issue_number}" --json number,title,state --jq '.[] | "\(.number): \(.title) (\(.state))"' 2>/dev/null || echo "")

        if [[ -n "$pr_list" ]]; then
            echo -e "${YELLOW}Associated PRs:${NC}"
            while IFS= read -r pr; do
                echo "   $pr"
            done <<< "$pr_list"
        else
            echo -e "${YELLOW}Associated PRs:${NC} None"
        fi
    fi

    # Worktree path
    echo ""
    echo -e "${YELLOW}Path:${NC} ${worktree_dir}"

    echo ""
done

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo "   Total worktrees: ${#worktrees[@]}"

# Count active locks
active_locks=0
stale_locks=0
for worktree_dir in "${worktrees[@]}"; do
    lock_file="${worktree_dir}/.agent-lock"
    if [[ -f "$lock_file" ]]; then
        lock_pid=$(jq -r '.pid // 0' "$lock_file")
        if ps -p "$lock_pid" > /dev/null 2>&1; then
            ((active_locks++))
        else
            ((stale_locks++))
        fi
    fi
done

echo "   Active locks: ${active_locks}"
if [[ "$stale_locks" -gt 0 ]]; then
    echo -e "   ${RED}Stale locks: ${stale_locks}${NC}"
fi

echo ""
echo -e "${BLUE}Available Commands:${NC}"
echo "   View detailed status: ${GREEN}$0 --verbose${NC}"
echo "   Start new work: ${GREEN}ccpm/commands/issue-start.sh <issue-number>${NC}"
echo "   Finish work: ${GREEN}ccpm/commands/issue-finish.sh <issue-number>${NC}"
echo "   Abort work: ${GREEN}ccpm/commands/issue-abort.sh <issue-number>${NC}"
echo ""

# Audit log info
LOG_DIR="${HOME}/.cache/svg2fbf-audit-logs"
if [[ -d "$LOG_DIR" ]]; then
    log_count=$(find "$LOG_DIR" -name "*.json" | wc -l | tr -d ' ')
    echo -e "${CYAN}Audit Logs:${NC}"
    echo "   Location: ${LOG_DIR}"
    echo "   Files: ${log_count}"
    echo "   View today's log: ${GREEN}cat ${LOG_DIR}/$(date +%Y-%m-%d).json | jq${NC}"
    echo ""
fi

exit 0
