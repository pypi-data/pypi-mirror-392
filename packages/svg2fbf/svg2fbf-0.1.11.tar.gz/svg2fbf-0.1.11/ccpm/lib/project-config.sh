#!/usr/bin/env bash
#
# CCPM Project Configuration
#
# Purpose: Auto-detect project information for generic CCPM plugin usage
# Usage: source ccpm/lib/project-config.sh
#
# This library detects:
# - Project name from git repository
# - Repository owner
# - Worktree and audit log locations
#
# Author: CCPM Plugin
# Last updated: 2025-01-17

# Detect project name from git remote URL
get_project_name() {
    local remote_url
    remote_url=$(git remote get-url origin 2>/dev/null || echo "")

    if [[ -z "$remote_url" ]]; then
        # Fallback: use directory name
        basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    else
        # Extract repo name from URL (works for both HTTPS and SSH)
        # github.com/user/repo.git → repo
        # github.com/user/repo → repo
        echo "$remote_url" | sed -E 's|.*/||; s|\.git$||'
    fi
}

# Detect repository owner from git remote URL
get_repo_owner() {
    local remote_url
    remote_url=$(git remote get-url origin 2>/dev/null || echo "")

    if [[ -z "$remote_url" ]]; then
        echo "unknown"
    else
        # Extract owner from URL
        # github.com/user/repo.git → user
        # github.com:user/repo.git → user
        echo "$remote_url" | sed -E 's|.*[:/]([^/]+)/[^/]+(.git)?$|\1|'
    fi
}

# Export project configuration variables
export PROJECT_NAME
export REPO_OWNER
export WORKTREE_BASE
export AUDIT_LOG_DIR
export PROJECT_SLUG

PROJECT_NAME=$(get_project_name)
REPO_OWNER=$(get_repo_owner)
PROJECT_SLUG="${REPO_OWNER}-${PROJECT_NAME}"

# Worktree and audit log locations (project-specific)
WORKTREE_BASE="${HOME}/.cache/ccpm-worktrees/${PROJECT_SLUG}"
AUDIT_LOG_DIR="${HOME}/.cache/ccpm-audit-logs/${PROJECT_SLUG}"

# Create directories if they don't exist
mkdir -p "${WORKTREE_BASE}" 2>/dev/null || true
mkdir -p "${AUDIT_LOG_DIR}" 2>/dev/null || true
