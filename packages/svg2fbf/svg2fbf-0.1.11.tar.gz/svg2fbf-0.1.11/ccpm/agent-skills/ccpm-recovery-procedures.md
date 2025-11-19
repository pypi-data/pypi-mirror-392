# CCPM Recovery Procedures

**Skill**: Recover from common agent errors and mistakes
**Use when**: Something went wrong and you need to fix it

---

## Overview

Agents make mistakes. This skill provides recovery procedures for common failures. Git is a time machine - almost everything is recoverable if you act quickly.

**Philosophy**: Fail-fast, recover gracefully.

---

## Quick Reference Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Find lost commits
git reflog

# Revert a commit (safe for public branches)
git revert <commit-hash>

# Discard all uncommitted changes
git restore .

# Restore file from last commit
git restore <file>

# List all worktrees
git worktree list

# Remove worktree
git worktree remove <path>

# Check what's staged
git diff --cached --name-only
```

---

## Scenario 1: Broke Tests on dev Branch

### Detection
```bash
pytest tests/
# FAILED tests/test_something.py::test_feature - AssertionError
```

### Impact
- ⚠️ Low severity (dev allows broken tests)
- Blocks promotion to testing
- May affect other developers

### Recovery

**Option A: Fix immediately** (preferred)
```bash
# 1. Identify failing tests
pytest tests/ -v

# 2. Fix the code
# (Edit files)

# 3. Verify fix
pytest tests/

# 4. Commit fix
git add <fixed-files>
git commit -m "fix(tests): Resolve test failure in test_feature"
git push origin dev
```

**Option B: Revert breaking commit**
```bash
# 1. Identify breaking commit
git log --oneline -10

# 2. Revert it
git revert <commit-hash>
git push origin dev

# 3. Fix properly in new commit
```

**Option C: Reset** (only if not pushed yet)
```bash
# ONLY if commit wasn't pushed yet
git reset --hard HEAD~1

# Fix and commit correctly
```

---

## Scenario 2: Pushed to Wrong Branch

### Detection
```bash
# You pushed to master instead of dev!
git log master --oneline -1
# Shows your commit on master
```

### Impact
- 🔴 High severity
- Broke branch protection rules
- Contaminated stable branch

### Recovery

```bash
# 1. IMMEDIATELY notify human
gh issue comment <your-issue> --body "🚨 ERROR: Accidentally pushed to master instead of dev. Awaiting human intervention."

# 2. DO NOT try to fix yourself - you might make it worse!

# 3. Human will:
# - Reset master to previous state
# - Cherry-pick your commit to dev
# - Update branch protection rules to prevent this
```

**Prevention**: Use CCPM commands (`python ccpm/commands/issue_start.py`) which prevent this.

---

## Scenario 3: Modified Protected File

### Detection
```bash
# Pre-commit hook blocks you:
❌ BLOCKED: ccpm/plugin.yaml is protected
```

### Impact
- ⚠️ Medium severity
- Commit blocked (safety worked!)
- Need to unstage file

### Recovery

```bash
# 1. Unstage protected file
git restore --staged ccpm/plugin.yaml

# 2. Restore original version
git restore ccpm/plugin.yaml

# 3. Commit without protected file
git add <other-files>
git commit -m "fix: Your fix (without protected file changes)"

# 4. If you genuinely need to update protected file:
gh issue comment <issue> --body "$(cat <<'EOF'
@user - I need to modify protected file ccpm/plugin.yaml to fix this issue.

Reason: [explain why]
Changes needed: [explain what]

Please advise how to proceed.
EOF
)"
```

---

## Scenario 4: Lost Commits After Reset

### Detection
```bash
# Did git reset --hard, now commits are gone!
git log --oneline
# Doesn't show your commits
```

### Impact
- 🔴 High severity if pushed
- ⚠️ Low severity if not pushed (recoverable via reflog)

### Recovery

```bash
# 1. Find lost commits
git reflog
# Shows all HEAD movements, find your lost commit hash

# Output example:
# abc1234 HEAD@{0}: reset: moving to HEAD~1
# def5678 HEAD@{1}: commit: fix: My important fix  ← This is lost!
# ghi9012 HEAD@{2}: commit: Previous commit

# 2. Recover lost commit
git cherry-pick def5678  # Use the hash from reflog

# 3. Verify recovery
git log --oneline
# Should show your recovered commit

# 4. Push if needed
git push origin <branch>
```

---

## Scenario 5: Worktree Broken/Corrupted

### Detection
```bash
cd ~/.cache/ccpm-worktrees/owner-project/issue-123
# Error: fatal: not a git repository
```

### Impact
- ⚠️ Medium severity
- Can't continue work in that worktree
- Uncommitted changes may be lost

### Recovery

```bash
# 1. Check if commits were pushed
cd /path/to/main/repo
git log origin/issue-123 --oneline
# If commits are there, you're safe

# 2. Remove broken worktree
git worktree remove --force ~/.cache/ccpm-worktrees/owner-project/issue-123

# 3. Recreate worktree
git worktree add ~/.cache/ccpm-worktrees/owner-project/issue-123 issue-123

# 4. If commits weren't pushed:
# Try to recover from reflog (see Scenario 4)

# 5. If uncommitted changes lost:
# Notify user, may need to redo work
gh issue comment 123 --body "⚠️ Worktree corrupted, uncommitted changes lost. Will redo work."
```

**Prevention**: Commit and push frequently!

---

## Scenario 6: Merge Conflict

### Detection
```bash
git merge dev
# CONFLICT (content): Merge conflict in src/file.py
```

### Impact
- ⚠️ Medium severity
- Blocks merge/promotion
- Manual intervention needed

### Recovery

```bash
# 1. Identify conflicted files
git status
# Shows files with conflicts

# 2. View conflict
cat src/file.py
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> dev

# 3. Resolve manually or ask for help
gh issue comment <issue> --body "$(cat <<'EOF'
⚠️ Merge conflict detected in src/file.py

Conflict between my changes and dev branch.

Requesting human assistance to resolve.
EOF
)"

# 4. If you can resolve:
# Edit file to resolve conflict
git add src/file.py
git commit -m "merge: Resolve conflict in file.py"

# 5. If unsure:
# Abort merge and ask for help
git merge --abort
```

**Prevention**: Pull from dev frequently before making changes.

---

## Scenario 7: Accidentally Closed Issue

### Detection
```bash
# You closed issue but verification wasn't complete
gh issue view 123
# State: CLOSED (oops!)
```

### Impact
- ⚠️ Low-Medium severity
- Issue marked as resolved incorrectly
- Easy to fix

### Recovery

```bash
# 1. Reopen immediately
gh issue reopen 123

# 2. Add comment explaining
gh issue comment 123 --body "$(cat <<'EOF'
⚠️ Issue was closed prematurely before completing verification protocol.

Reopening to complete:
- [ ] Step 7.2: Reproduce original issue
- [ ] Step 7.3: Run all tests
- [ ] Step 7.4: Check for breaking changes
- [ ] Step 7.5: Check related issues

Will close again after completing all verification steps.
EOF
)"

# 3. Complete verification protocol
# (Use ccpm-verification-protocol skill)

# 4. Close properly after verification
```

---

## Scenario 8: Force-Pushed by Mistake

### Detection
```bash
# You ran: git push --force
# (You should NEVER do this!)
```

### Impact
- 🔴 Critical severity
- Destroyed other people's commits
- Human intervention required immediately

### Recovery

```bash
# 1. STOP! Do not make more changes!

# 2. Immediately notify human
gh issue comment <issue> --body "$(cat <<'EOF'
🚨 CRITICAL ERROR: Accidentally force-pushed to <branch>

This may have destroyed commits from other contributors.

Requesting immediate human intervention.
EOF
)"

# 3. Human will:
# - Check reflog on server
# - Restore lost commits
# - Add branch protection to prevent force-push
```

**Prevention**: NEVER use `git push --force`. If someone tells you to, refuse and ask human.

---

## Scenario 9: Can't Reproduce Issue Anymore

### Detection
```bash
# You reproduced issue yesterday
# Now following exact same steps, can't reproduce
```

### Impact
- ⚠️ Medium severity
- Can't verify fix works
- Might be environment issue

### Recovery

```bash
# 1. Double-check you're using same steps
# Review issue description and your reproduction notes

# 2. Check environment differences
# - Different Python version?
# - Different dependencies?
# - Different input data?
# - Different OS/platform?

# 3. Comment on issue
gh issue comment <issue> --body "$(cat <<'EOF'
⚠️ Unable to reproduce issue

**Original reproduction** (worked yesterday):
- Command: svg2fbf --input frames/ --output test.svg
- Result: Bug occurred

**Current attempt** (not reproducing):
- Command: Same command
- Result: No bug observed

**Environment**:
- Python: $(python --version)
- Dependencies: $(pip list | grep svg2fbf)

Possible causes:
1. Issue already fixed by another commit?
2. Environment changed?
3. Input data different?

Requesting user assistance.
EOF
)"

# 4. Ask user to reproduce and confirm
```

---

## Scenario 10: Ran Forbidden Command

### Detection
```bash
# You ran: just equalize
# (This is FORBIDDEN for agents!)

# Or: just publish
# (Also FORBIDDEN!)
```

### Impact
- 🔴 Critical severity
- `just equalize`: Destroyed branch divergence, force-synced all branches
- `just publish`: May have published to PyPI incorrectly

### Recovery

```bash
# 1. STOP IMMEDIATELY

# 2. Notify human with maximum urgency
gh issue comment <issue> --body "$(cat <<'EOF'
🚨🚨🚨 CRITICAL ERROR 🚨🚨🚨

I accidentally ran forbidden command: <command name>

This is a critical mistake that requires immediate human intervention.

**Do not make any more changes.**
EOF
)"

# 3. For `just equalize`:
# Human will restore branches from remote backup
# May need to re-do work

# 4. For `just publish`:
# Human will check PyPI, may need to yank release
# Severe consequences possible
```

**Prevention**: NEVER run `just equalize`, `just publish`, or other human-only commands. If unsure, ask first.

---

## Scenario 11: Stale Worktree Lock

### Detection
```bash
python ccpm/commands/issue_start.py 123 dev
# Error: Issue 123 is already being worked on by agent-xyz
# But agent-xyz crashed and isn't actually working on it
```

### Impact
- ⚠️ Low-Medium severity
- Blocks you from working
- Lock is stale from crashed agent

### Recovery

```bash
# 1. Verify lock is actually stale
python ccpm/commands/issue_status.py
# Check if agent-xyz is really inactive

# 2. If lock is stale (>24h old, agent crashed):
# Manually remove lock
rm ~/.cache/ccpm-worktrees/owner-project/issue-123/.agent-lock

# 3. Clean up stale worktree if needed
git worktree remove ~/.cache/ccpm-worktrees/owner-project/issue-123

# 4. Start fresh
python ccpm/commands/issue_start.py 123 dev

# 5. Document in issue
gh issue comment 123 --body "Removed stale lock from crashed agent-xyz, starting work."
```

---

## Emergency Escalation

If you encounter a situation not covered here:

```bash
# 1. STOP making changes

# 2. Create urgent comment
gh issue comment <issue> --body "$(cat <<'EOF'
🚨 EMERGENCY: Unknown Error Situation

**What happened**: [Describe]
**What I tried**: [Describe]
**Current state**: [Describe]

**Requesting immediate human intervention.**

I have stopped making changes to prevent further issues.
EOF
)"

# 3. Wait for human guidance

# 4. Document what happened for future recovery procedures
```

---

## Prevention Best Practices

### ALWAYS

- ✅ Commit frequently (every logical change)
- ✅ Push frequently (don't let commits pile up locally)
- ✅ Use CCPM commands instead of raw git
- ✅ Read error messages carefully
- ✅ Test before committing
- ✅ Ask if unsure

### NEVER

- ❌ Force-push
- ❌ Run `just equalize` or `just publish`
- ❌ Modify protected files
- ❌ Push to master/main directly
- ❌ Work outside of worktrees
- ❌ Ignore safety warnings

---

## When to Use This Skill

**Use this skill when**:
- Something went wrong
- Safety check blocked you
- Lost commits or work
- Unsure how to recover from error

**After recovery**:
- Use `ccpm-issue-workflow` to resume normal workflow
- Update issue with recovery actions taken

---

**For complete 11-scenario recovery guide, see**: `ccpm/skills/recovery-procedures.md`
