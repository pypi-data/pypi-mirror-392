#!/usr/bin/env bash
#
# Audit Logging for CCPM Agents
#
# Purpose: Log all agent actions to JSON for accountability and debugging
# Usage: ./audit-log.sh <action> <details...>
# Exit codes:
#   0 - Log entry created successfully
#   1 - Error creating log entry
#
# Actions logged:
#   - worktree_create
#   - worktree_remove
#   - commit
#   - push
#   - pr_create
#   - pr_update
#   - branch_switch
#   - file_modify
#   - error
#
# Log format: JSON lines in ~/.cache/svg2fbf-audit-logs/YYYY-MM-DD.json
#
# Author: CCPM Plugin
# Last updated: 2025-01-14

set -euo pipefail

# Arguments
ACTION="${1:-unknown}"
shift  # Remove first argument, rest are details

# Paths
LOG_DIR="${HOME}/.cache/svg2fbf-audit-logs"
LOG_FILE="${LOG_DIR}/$(date +%Y-%m-%d).json"

# Create log directory if needed
mkdir -p "$LOG_DIR"

# Get context
AGENT_ID="${CCPM_AGENT_ID:-unknown}"
AGENT_SESSION="${CCPM_SESSION_ID:-$$}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo 'unknown')"
CURRENT_BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
CURRENT_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"

# Build log entry
log_entry() {
    local action="$1"
    shift

    # Base entry
    cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "agent_id": "$AGENT_ID",
  "session_id": "$AGENT_SESSION",
  "action": "$action",
  "repository": "$REPO_ROOT",
  "branch": "$CURRENT_BRANCH",
  "commit": "$CURRENT_COMMIT",
EOF

    # Add action-specific fields
    case "$action" in
        worktree_create)
            local worktree_path="${1:-}"
            local issue_number="${2:-}"
            cat <<EOF
  "worktree_path": "$worktree_path",
  "issue_number": "$issue_number",
EOF
            ;;

        worktree_remove)
            local worktree_path="${1:-}"
            cat <<EOF
  "worktree_path": "$worktree_path",
EOF
            ;;

        commit)
            local commit_hash="${1:-}"
            local commit_message="${2:-}"
            local files_changed="${3:-}"
            cat <<EOF
  "commit_hash": "$commit_hash",
  "commit_message": "$commit_message",
  "files_changed": $files_changed,
EOF
            ;;

        push)
            local remote="${1:-origin}"
            local ref="${2:-$CURRENT_BRANCH}"
            local force="${3:-false}"
            cat <<EOF
  "remote": "$remote",
  "ref": "$ref",
  "force_push": $force,
EOF
            ;;

        pr_create)
            local pr_number="${1:-}"
            local pr_title="${2:-}"
            local draft="${3:-true}"
            cat <<EOF
  "pr_number": "$pr_number",
  "pr_title": "$pr_title",
  "draft": $draft,
EOF
            ;;

        pr_update)
            local pr_number="${1:-}"
            local update_type="${2:-}"
            cat <<EOF
  "pr_number": "$pr_number",
  "update_type": "$update_type",
EOF
            ;;

        branch_switch)
            local from_branch="${1:-}"
            local to_branch="${2:-}"
            cat <<EOF
  "from_branch": "$from_branch",
  "to_branch": "$to_branch",
EOF
            ;;

        file_modify)
            local file_path="${1:-}"
            local operation="${2:-modify}"
            cat <<EOF
  "file_path": "$file_path",
  "operation": "$operation",
EOF
            ;;

        error)
            local error_type="${1:-}"
            local error_message="${2:-}"
            local recovery_action="${3:-}"
            cat <<EOF
  "error_type": "$error_type",
  "error_message": "$error_message",
  "recovery_action": "$recovery_action",
EOF
            ;;

        *)
            # Generic details
            local details="$*"
            cat <<EOF
  "details": "$details",
EOF
            ;;
    esac

    # Close entry
    cat <<EOF
  "hostname": "$(hostname)",
  "user": "$(whoami)"
}
EOF
}

# Write log entry
log_entry "$ACTION" "$@" >> "$LOG_FILE"

# Also log to syslog if available
if command -v logger &> /dev/null; then
    logger -t "ccpm-agent" -p user.info "action=$ACTION agent=$AGENT_ID session=$AGENT_SESSION"
fi

exit 0
