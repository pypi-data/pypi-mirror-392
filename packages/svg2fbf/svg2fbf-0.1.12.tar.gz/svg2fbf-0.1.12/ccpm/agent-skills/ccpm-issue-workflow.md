# CCPM Issue Workflow Management

**Skill**: Complete GitHub issue lifecycle management with CCPM plugin
**Use when**: Working on ANY GitHub issue in a project with CCPM plugin

---

## Overview

This skill teaches you the complete 8-step issue lifecycle using the CCPM (Controlled Concurrent Project Management) plugin for safe, isolated, and verified issue resolution.

**CRITICAL**: This is NOT optional workflow guidance - these are MANDATORY steps with safety mechanisms.

---

## Prerequisites Check

Before starting ANY issue:

```bash
# 1. Check if CCPM plugin is available
ls ccpm/commands/issue_start.py
# If found → CCPM is installed
# If not found → Ask user if they want to install CCPM

# 2. Check if labels are set up (first time only)
gh label list | grep -c "needs-triage"
# If 0 → Run: python ccpm/commands/setup_labels.py
# If >0 → Labels already configured

# 3. Read the complete guide (MANDATORY first time)
# File: ccpm/skills/issue-management.md (1,124 lines)
```

---

## The 8-Step Workflow

### Step 1: Check for Duplicates (MANDATORY)

**Never skip this step!**

```bash
# Search existing issues (open AND closed)
gh issue list --search "in:title,body <keywords>" --state all

# Example searches:
gh issue list --search "in:title,body header duplicate" --state all
gh issue list --search "in:title,body import error" --state all

# If duplicate found:
gh issue comment <new-issue> --body "Duplicate of #<original>"
gh issue close <new-issue> --reason "not planned"
# Then work on the ORIGINAL issue instead
```

### Step 2: Reproduce Issue (MANDATORY - 3-Attempt Policy)

**For Bugs**:
```bash
# 1. Read issue description carefully
# 2. Gather exact reproduction steps
# 3. Attempt reproduction

# If reproduced:
gh issue edit <number> --add-label "reproduced"

# If NOT reproduced (attempt 1/3):
gh issue edit <number> --add-label "needs-reproduction"
gh issue comment <number> --body "Unable to reproduce. Please provide:
1. Exact command you ran
2. Sample input files
3. Expected vs actual behavior
4. Environment (OS, Python version, tool version)"

# If still can't reproduce after attempt 3:
gh issue edit <number> --add-label "cannot-reproduce"
gh issue close <number> --reason "not planned" --comment "Closing after 3 failed reproduction attempts. Please reopen with complete reproduction steps."
```

**For New Features**:
```bash
# Understand the feature request
# Verify it's not already implemented
# Confirm scope with user if ambiguous
```

### Step 3: Label the Issue

```bash
# Assign to yourself
gh issue edit <number> --add-assignee @me

# Add type and component labels
gh issue edit <number> --add-label "bug,component:cli,priority:medium"

# Transition status labels (ONE at a time!)
gh issue edit <number> --remove-label "needs-triage" --add-label "examining"
# After reproducing:
gh issue edit <number> --remove-label "examining" --add-label "reproduced"
# After understanding root cause:
gh issue edit <number> --remove-label "reproduced" --add-label "verified"
# Add effort estimate:
gh issue edit <number> --add-label "effort:small"
```

**Status Label State Machine** (ONLY ONE status label at a time):
```
needs-triage → examining → reproduced → verified → in-progress → needs-review → fixed
              └→ needs-reproduction → examining (after user provides info)
              └→ cannot-reproduce (after 3 attempts)
```

### Step 4: Start Work in Isolated Worktree

#### Normal Workflow (99% of cases):

```bash
# Transition to in-progress
gh issue edit <number> --remove-label "verified" --add-label "in-progress"

# Start work in dev branch (creates isolated worktree)
python ccpm/commands/issue_start.py <issue-number> dev

# This runs pre-flight checks:
# - Issue exists and assigned
# - No conflicting locks
# - Target branch allowed
# - No conflicting PRs
# - Repository clean

# Work in isolated worktree
cd ~/.cache/ccpm-worktrees/{owner}-{project}/issue-<number>
```

#### ⚠️ EXCEPTION: Critical Hotfix Workflow (1% of cases)

**When to use**: Issue is `priority:critical` OR `priority:blocker` AND affects production/stable

**Decision checklist**:
- ✅ Security vulnerability affecting stable release?
- ✅ Critical bug causing data loss in production?
- ✅ Crash bug affecting all stable users?
- ✅ Code in dev has diverged (bug no longer exists there)?

**If YES to any above → Work on master directly:**

```bash
# Verify labels
gh issue view <number> --json labels
# Must have: priority:critical OR priority:blocker

# Work directly on master (EXCEPTION)
git checkout master
git pull origin master

# Make the fix
# ... edit files ...

# Commit with explanation
git commit -m "fix(critical): Description #<number>

HOTFIX for production release.
Bypasses normal dev pipeline because:
- [Explain why this is critical]
- [Explain why dev doesn't need it OR will be backported]

Fixes #<number>"

# Push to master
git push origin master

# Check if dev needs the fix
git checkout dev
# Search for vulnerable code
grep -r "pattern" src/

# If found → backport to dev
git checkout dev
just backport-hotfix  # Select the commit
just test
git push origin dev

# If not found → document
gh issue comment <number> --body "✅ Hotfix applied to master.
Dev is not affected (code was refactored)."

# Release patch
git checkout master
just release patch

# Skip to Step 8 (close issue)
```

**If NO to all → Use normal dev workflow** (continue below)

### Step 5: Make Changes

```bash
# Work normally in the worktree
# Make changes, commit, test
git add <files>
git commit -m "fix(component): Description

- Detail 1
- Detail 2

Fixes #<issue-number>"

# Pre-commit hook automatically blocks protected files
```

### Step 6: Finish and Create PR

```bash
# Finish work (runs quality checks)
python ccpm/commands/issue_finish.py <issue-number>

# This runs post-flight checks:
# - Tests pass
# - Linting passes
# - Formatting correct
# - No secrets
# - Correct branch
# - No protected files modified

# Then automatically:
# - Pushes commits
# - Creates Draft PR
# - Removes lock
# - Optionally removes worktree

# Update label
gh issue edit <number> --remove-label "in-progress" --add-label "needs-review"
```

### Step 7: CRITICAL VERIFICATION PROTOCOL (After PR Merged)

**⚠️ MANDATORY - See ccpm-verification-protocol skill for complete details**

Quick summary (8 sub-steps):
1. Pull latest changes
2. Reproduce original issue again (or test feature with temp script)
3. Run ALL tests for regressions
4. Check for breaking changes → Ask user approval if found
5. Check if fix solved related issues → Test and close them too
6. Complete final checklist
7. Close ONLY after all checks pass
8. Reopen immediately if any check fails

**Use the ccpm-verification-protocol skill for complete step-by-step guide.**

### Step 8: Close Issue

```bash
# ONLY after completing Step 7 verification!
gh issue edit <number> --remove-label "needs-review" --add-label "fixed"
gh issue close <number> --reason "completed" --comment "$(cat <<'EOF'
## ✅ Verified Fixed - Complete Verification Report

[See Step 7.7 template in issue-management.md]
EOF
)"
```

---

## Common Commands Reference

```bash
# Check status of all active issues
python ccpm/commands/issue_status.py

# Abort work on an issue
python ccpm/commands/issue_abort.py <issue-number>

# List all labels
gh label list

# View issue details
gh issue view <number>

# Comment on issue
gh issue comment <number> --body "message"
```

---

## Critical Rules

### ALWAYS

- ✅ Check for duplicates before starting
- ✅ Reproduce issue before working (3-attempt policy)
- ✅ Use isolated worktrees (via issue_start.py)
- ✅ Complete Step 7 verification before closing
- ✅ Only ONE status label at a time
- ✅ Transition labels properly (state machine)

### NEVER

- ❌ Skip duplicate check
- ❌ Work without reproducing issue first
- ❌ Skip Step 7 verification protocol
- ❌ Add multiple status labels
- ❌ Close without verification
- ❌ Work on duplicates

---

## When to Use This Skill

**Use this skill when**:
- User asks you to work on a GitHub issue
- You see an issue that needs fixing
- You need to understand the CCPM workflow
- You're unsure about issue lifecycle steps

**After reading this skill**:
- Use `ccpm-verification-protocol` skill before closing issues
- Use `ccpm-label-management` skill for label questions
- Use `ccpm-breaking-changes` skill if you detect API changes
- Read `ccpm/skills/issue-management.md` for complete 1,124-line guide

---

## Quick Troubleshooting

**Issue**: Can't start work (issue_start.py fails)
→ Check pre-flight errors, fix them, retry

**Issue**: Tests failing in post-flight check
→ Fix tests before creating PR (never skip!)

**Issue**: Don't know which label to use
→ Use `ccpm-label-management` skill

**Issue**: Made a mistake
→ Use `ccpm-recovery-procedures` skill

---

**Remember**: This workflow has safety mechanisms (pre-flight, post-flight, verification protocol) to prevent mistakes. Don't bypass them!
