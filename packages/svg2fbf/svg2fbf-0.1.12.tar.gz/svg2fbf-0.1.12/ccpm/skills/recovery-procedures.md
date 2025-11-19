# Recovery Procedures for svg2fbf Agent Errors

## Philosophy

**Fail-fast, recover gracefully**. Agents will make mistakes. This document provides recovery procedures for every identified failure scenario.

**Key Principle**: Git is a time machine. Almost everything is recoverable if you act quickly.

---

## Quick Reference: Common Recovery Commands

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
```

---

## Scenario 1: Agent Broke Tests on dev Branch

### Detection
```bash
$ pytest tests/
FAILED tests/test_svg2fbf.py::test_viewBox_detection - AssertionError
```

### Impact
- ⚠️ Low severity (dev branch allows broken tests)
- Tests fail, blocking promotion to testing
- Other developers may be affected

### Recovery Procedure

**Option A: Fix tests immediately** (preferred)
```bash
# 1. Identify failing tests
pytest tests/ -v

# 2. Fix the issue
# (Agent edits code)

# 3. Verify fix
pytest tests/

# 4. Commit fix
git add <fixed-files>
git commit -m "fix(tests): Correct test failure in test_viewBox_detection"

# 5. Push
git push origin dev
```

**Option B: Revert breaking commit**
```bash
# 1. Identify breaking commit
git log --oneline -10
# Find commit that broke tests

# 2. Revert it
git revert <commit-hash>

# 3. Push
git push origin dev

# 4. Fix issue properly in new commit
```

**Option C: Reset branch** (if very recent, no other commits)
```bash
# 1. ONLY if commit was just made and not pushed yet
git reset --hard HEAD~1

# 2. Fix issue

# 3. Commit correctly
git add <files>
git commit -m "fix: Correct implementation"

# 4. Push
git push origin dev
```

### Prevention
- ✅ Run `pytest tests/` before every commit
- ✅ Use pre-commit hooks (post_flight_check.py)
- ✅ Test in isolation before pushing

---

## Scenario 2: Agent Pushed to Wrong Branch

### Detection
```bash
$ git log origin/master --oneline -5
abc1234 feat(agent): Added experimental feature  # ❌ Should not be here!
```

### Impact
- 🔴 High severity if pushed to master/main
- 🟡 Medium severity if pushed to review
- 🟢 Low severity if pushed to testing

### Recovery Procedure

**If pushed to master/main** (CRITICAL):
```bash
# 1. IMMEDIATELY notify human
echo "🚨 CRITICAL: Pushed to master by mistake!"

# 2. Human decides recovery strategy:

# Option A: Revert commit (safe, preserves history)
git checkout master
git revert <commit-hash>
git push origin master

# Option B: Force reset (DANGEROUS, only if caught immediately)
# ONLY if no one else pulled yet
git checkout master
git reset --hard <commit-before-mistake>
git push --force origin master  # Requires admin privileges
```

**If pushed to review**:
```bash
# 1. Assess damage
git log origin/review --oneline -10

# 2. Revert unwanted commits
git checkout review
git revert <commit-hash>
git push origin review

# 3. CI will re-run, should pass
```

**If pushed to testing**:
```bash
# Similar to review, but less critical
git checkout testing
git revert <commit-hash>
git push origin testing
```

### Prevention
- ✅ Always work in dedicated worktrees
- ✅ Use pre-flight check to validate branch
- ✅ Never checkout master/main/review manually
- ✅ Use `git branch --show-current` before pushing

---

## Scenario 3: Agent Modified Protected File

### Detection
```bash
$ git status
modified:   justfile  # ❌ Protected file!
```

Or caught by pre-commit hook:
```bash
$ git commit
❌ ERROR: Attempting to commit protected file: justfile
```

### Impact
- 🔴 High severity if committed and pushed
- 🟢 Low severity if caught before commit

### Protected Files List
- `justfile`
- `scripts/release.sh`
- `cliff.toml`
- `.github/workflows/*`
- `CHANGELOG.md`
- `pyproject.toml` (except dependencies with approval)

### Recovery Procedure

**Before commit** (easy):
```bash
# 1. Restore file to original state
git restore justfile

# 2. Verify restoration
git status  # Should no longer show justfile as modified
```

**After commit, before push** (medium):
```bash
# 1. Remove file from last commit
git restore --staged justfile
git restore justfile

# 2. Amend commit
git commit --amend --no-edit

# 3. Verify
git show  # Should not include justfile
```

**After push** (hard):
```bash
# 1. Revert entire commit
git revert <commit-hash>
git push origin <branch>

# 2. Re-apply intended changes without protected file
git cherry-pick <commit-hash>
git restore justfile  # Remove unwanted change
git commit --amend -m "fix: Re-apply changes without modifying justfile"
git push origin <branch>
```

### Prevention
- ✅ Use pre-commit hook (pre_commit_safety.py)
- ✅ Check `protected-files.txt` before editing
- ✅ Run `git diff` before committing
- ✅ Review file list in `git status`

---

## Scenario 4: Multiple Agents on Same Issue

### Detection
```bash
$ ls ~/.cache/svg2fbf-worktrees/issue-123/.agent-lock
.agent-lock exists

$ cat ~/.cache/svg2fbf-worktrees/issue-123/.agent-lock
{"agent_id": "agent-42", "pid": 12345, "started": "2025-01-14T10:00:00Z"}
```

### Impact
- 🟡 Medium severity
- Potential for conflicting commits
- Wasted work if agents duplicate effort

### Recovery Procedure

**Detection at start** (pre-flight check catches):
```bash
# 1. Check lock file
if [ -f ~/.cache/svg2fbf-worktrees/issue-123/.agent-lock ]; then
    echo "⚠️ Another agent is working on this issue!"

    # 2. Check if process still alive
    lock_pid=$(jq -r .pid .agent-lock)
    if ps -p $lock_pid > /dev/null; then
        echo "❌ Agent still active, cannot proceed"
        exit 1
    else
        echo "🔧 Stale lock, removing"
        rm .agent-lock
    fi
fi
```

**If both agents already committed**:
```bash
# 1. List commits from both agents
git log --oneline --all

# 2. Human decides which commits to keep

# 3. Cherry-pick desired commits to clean branch
git checkout -b issue-123-merged dev
git cherry-pick <commit-1>
git cherry-pick <commit-2>

# 4. Test merged result
pytest tests/

# 5. Replace issue-123 branch
git branch -D issue-123
git branch -m issue-123

# 6. Force push (if necessary)
git push origin issue-123 --force
```

### Prevention
- ✅ Check for .agent-lock before starting (pre-flight check)
- ✅ Create lock immediately when starting work
- ✅ Remove lock when finishing (issue_finish.py)
- ✅ Include PID in lock to detect stale locks

---

## Scenario 5: Agent Corrupted CHANGELOG.md

### Detection
```bash
$ git diff CHANGELOG.md
- ## [0.1.8] - 2025-01-14
+ ## [0.1.8] - 2025-01-14 (Agent modified this)
```

### Impact
- 🔴 High severity (CHANGELOG.md is auto-generated)
- Breaks release process
- Confuses users about release history

### Recovery Procedure

**Before commit**:
```bash
# 1. Restore from last commit
git restore CHANGELOG.md

# 2. Verify
git diff CHANGELOG.md  # Should show no changes
```

**After commit**:
```bash
# 1. Restore from origin
git checkout origin/dev -- CHANGELOG.md

# 2. Commit restoration
git add CHANGELOG.md
git commit -m "fix: Restore auto-generated CHANGELOG.md"

# 3. Push
git push origin dev
```

**After release** (CRITICAL):
```bash
# 1. CHANGELOG.md was updated by git-cliff during release
# 2. Agent must NOT edit it afterward

# If edited after release:
git checkout v0.1.8 -- CHANGELOG.md  # Restore from release tag
git add CHANGELOG.md
git commit -m "fix: Restore CHANGELOG.md from v0.1.8 release"
git push origin <branch>
```

### Prevention
- ✅ CHANGELOG.md is in protected-files.txt
- ✅ Pre-commit hook blocks edits
- ✅ Agents should NEVER edit CHANGELOG.md
- ✅ git-cliff generates it automatically

---

## Scenario 6: Agent Lost Commits (Switched Branches in Worktree)

### Detection
```bash
$ git log --oneline
# Missing commits that were made earlier

$ git reflog
abc1234 HEAD@{0}: checkout: moving from issue-123 to dev
def5678 HEAD@{1}: commit: feat: Add feature (← Lost commit!)
```

### Impact
- 🟡 Medium severity
- Work appears lost but is recoverable
- May cause panic

### Recovery Procedure

**Using reflog** (safest):
```bash
# 1. View reflog to find lost commit
git reflog

# Output:
# abc1234 HEAD@{0}: checkout: moving from issue-123 to dev
# def5678 HEAD@{1}: commit: feat: Add feature
# ...

# 2. Identify lost commit hash: def5678

# 3. Cherry-pick lost commit to current branch
git cherry-pick def5678

# 4. Or create new branch from lost commit
git checkout -b issue-123-recovered def5678

# 5. Verify commit is back
git log --oneline
```

**Using fsck** (if reflog expired):
```bash
# 1. Find dangling commits
git fsck --lost-found

# 2. Examine dangling commits
git show <dangling-commit-hash>

# 3. Recover desired commit
git cherry-pick <dangling-commit-hash>
```

### Prevention
- ✅ Use dedicated worktrees (no branch switching)
- ✅ Always push commits before switching contexts
- ✅ Reflog keeps history for 90 days (default)

---

## Scenario 7: Merge Conflicts During Promotion

### Detection
```bash
$ just promote-to-testing
Auto-merging src/svg2fbf.py
CONFLICT (content): Merge conflict in src/svg2fbf.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Impact
- 🟢 Low severity (expected occasionally)
- Blocks promotion until resolved
- Requires human intervention

### Recovery Procedure

**Agent assists human**:
```bash
# 1. Identify conflicting files
git status

# Output:
# both modified:   src/svg2fbf.py

# 2. Show conflict
git diff src/svg2fbf.py

# 3. Agent explains conflict to human
echo "Conflict in svg2fbf.py:"
echo "- dev branch changed X"
echo "- testing branch changed Y"
echo "Suggested resolution: Keep X, discard Y (or merge both)"

# 4. Human resolves conflict manually

# 5. Mark resolved
git add src/svg2fbf.py

# 6. Complete merge
git commit -m "Merge dev into testing: resolve conflicts in svg2fbf.py"

# 7. Run tests
pytest tests/

# 8. Push
git push origin testing
```

**Abort merge if needed**:
```bash
# If resolution is too complex, abort and investigate
git merge --abort

# Then analyze conflict more carefully
git diff dev testing -- src/svg2fbf.py
```

### Prevention
- ✅ Keep branches in sync (promote frequently)
- ✅ Avoid working directly on testing/review
- ✅ Use feature branches for isolated work

---

## Scenario 8: CI Failed on review/master Branch

### Detection
```bash
$ gh pr checks
❌ test (ubuntu-latest, 3.12)    Failed
✅ test (ubuntu-latest, 3.11)    Passed
✅ lint                          Passed
```

### Impact
- 🔴 High severity (blocks promotion)
- Code cannot proceed to master
- Breaks release pipeline

### Recovery Procedure

**Investigation**:
```bash
# 1. View CI logs
gh run view <run-id>

# 2. Download logs
gh run download <run-id>

# 3. Reproduce locally
pytest tests/ --python=3.12

# 4. Identify root cause
```

**Fix on review branch** (supervised):
```bash
# 1. Create worktree from review
git worktree add ~/.cache/svg2fbf-worktrees/ci-fix review

# 2. Fix issue
cd ~/.cache/svg2fbf-worktrees/ci-fix
# Edit code

# 3. Test locally
pytest tests/

# 4. Commit fix
git add <fixed-files>
git commit -m "fix(ci): Resolve Python 3.12 compatibility issue"

# 5. Push
git push origin review

# 6. Monitor CI
gh run watch
```

**If unfixable** (revert):
```bash
# 1. Identify breaking commit
git log origin/review --oneline -10

# 2. Revert it
git checkout review
git revert <breaking-commit>
git push origin review

# 3. CI should pass now

# 4. Fix issue on dev, re-promote later
```

### Prevention
- ✅ Run tests locally before promoting
- ✅ Test on multiple Python versions (3.11, 3.12, 3.13)
- ✅ Use matrix testing in CI
- ✅ Monitor CI immediately after promotion

---

## Scenario 9: Catastrophic Git Corruption

### Detection
```bash
$ git status
error: object file .git/objects/a1/b2c3d4... is empty
fatal: loose object a1b2c3d4... is corrupt
```

### Impact
- 🔴 Critical severity
- Repository may be unusable
- Data loss possible

### Recovery Procedure

**Attempt fsck**:
```bash
# 1. Check corruption extent
git fsck --full

# 2. If recoverable, rebuild index
rm -f .git/index
git reset HEAD

# 3. Verify
git status
```

**Clone fresh from origin**:
```bash
# 1. Backup corrupted repo
mv svg2fbf svg2fbf-corrupted-backup

# 2. Clone fresh
git clone https://github.com/user/svg2fbf.git

# 3. Recover uncommitted work from backup
cp svg2fbf-corrupted-backup/src/new_feature.py svg2fbf/src/

# 4. Continue work
cd svg2fbf
```

**Use worktree from ~/.cache**:
```bash
# 1. Worktrees are independent
cd ~/.cache/svg2fbf-worktrees/issue-123

# 2. Push commits from worktree
git push origin dev

# 3. Clone fresh main repo
# (Commits are safe on origin)
```

### Prevention
- ✅ Push commits frequently
- ✅ Use worktrees (isolates corruption)
- ✅ GitHub is source of truth
- ✅ Never manually edit .git/ directory

---

## Scenario 10: Agent Accidentally Triggered Release

### Detection
```bash
$ just publish
🔍 Detecting version from pyproject.toml...
# OH NO! Didn't mean to run this!
```

### Impact
- 🔴 Critical severity if on master (publishes to PyPI)
- 🟡 Medium severity if on dev/testing/review

### Recovery Procedure

**During release** (interrupt):
```bash
# 1. Press Ctrl+C immediately
^C
Interrupted

# 2. Check what was done
git status
git log --oneline -1

# 3. If tag was created
git tag -d v0.1.8
git push origin :refs/tags/v0.1.8  # Delete remote tag

# 4. If commit was made (CHANGELOG.md)
git reset --hard HEAD~1
```

**After release to GitHub Releases** (not PyPI):
```bash
# 1. Delete GitHub Release
gh release delete v0.1.8

# 2. Delete tag
git tag -d v0.1.8
git push origin :refs/tags/v0.1.8

# 3. Revert CHANGELOG.md
git restore CHANGELOG.md
```

**After release to PyPI** (IRREVERSIBLE):
```bash
# ❌ CANNOT DELETE FROM PyPI

# Options:
# 1. Yank version (marks as not default)
pip install twine
twine yank svg2fbf 0.1.8

# 2. Publish fixed version immediately
# Edit pyproject.toml: version = "0.1.9"
just publish

# 3. Update PyPI description warning about issue
```

### Prevention
- ✅ **AGENTS MUST NEVER RUN `just publish`**
- ✅ Block command in agent scripts
- ✅ Require human confirmation
- ✅ Add `publish` to forbidden commands list

---

## Scenario 11: Stale Worktree After Crash

### Detection
```bash
$ git worktree list
/Users/user/svg2fbf        abc1234 [dev]
/home/.cache/.../issue-123 def5678 [HEAD detached]  # ← Stale

$ cd /home/.cache/svg2fbf-worktrees/issue-123
$ ls
# No .agent-lock, agent crashed
```

### Impact
- 🟢 Low severity
- Wastes disk space
- Clutters worktree list

### Recovery Procedure

```bash
# 1. Check for uncommitted changes
cd ~/.cache/svg2fbf-worktrees/issue-123
git status

# 2. If uncommitted changes exist, save them
git stash save "Recovered from stale worktree"
git stash show  # Review

# 3. Push stashed work to new branch (optional)
git checkout -b issue-123-recovered-work
git stash pop
git add .
git commit -m "Recovered work from crashed agent"
git push origin issue-123-recovered-work

# 4. Remove worktree
cd ~/svg2fbf
git worktree remove ~/.cache/svg2fbf-worktrees/issue-123

# 5. Prune worktree references
git worktree prune
```

### Prevention
- ✅ Use issue_abort.py for cleanup
- ✅ Trap signals to cleanup on crash
- ✅ Periodic cleanup script for stale worktrees

---

## Emergency Commands

### Nuclear Option: Reset Branch to Origin

**DESTRUCTIVE** - Only use if local branch is completely broken:

```bash
# 1. Fetch latest from origin
git fetch origin

# 2. DESTROY local branch and replace with origin
git checkout dev
git reset --hard origin/dev

# 3. Verify
git status  # Should show "nothing to commit"
```

### Save Work Before Destruction

```bash
# 1. Create backup branch
git branch backup-$(date +%Y%m%d-%H%M%S)

# 2. Now safe to reset
git reset --hard origin/dev
```

### Restore Deleted Branch

```bash
# 1. Find deleted branch in reflog
git reflog | grep "branch-name"

# 2. Recreate branch
git checkout -b branch-name <commit-hash>
```

---

## Recovery Decision Tree

```
Problem detected
    │
    ├─ Uncommitted changes?
    │  ├─ Yes → git restore <file> or git stash
    │  └─ No  → Continue
    │
    ├─ Commit not pushed?
    │  ├─ Yes → git reset --soft HEAD~1, fix, re-commit
    │  └─ No  → Continue
    │
    ├─ Commit pushed to dev/testing?
    │  ├─ Yes → git revert <commit>
    │  └─ No  → Continue
    │
    ├─ Commit pushed to review/master/main?
    │  ├─ Yes → 🚨 NOTIFY HUMAN IMMEDIATELY
    │  └─ No  → Continue
    │
    ├─ Protected file modified?
    │  ├─ Yes → git restore <file>, revert commit
    │  └─ No  → Continue
    │
    ├─ CI failing?
    │  ├─ Yes → Fix on same branch, push fix
    │  └─ No  → Continue
    │
    └─ Lost commits?
       ├─ Yes → git reflog, cherry-pick
       └─ No  → Resolved
```

---

## Audit Log Review

After recovery, check audit logs:

```bash
# 1. View recent agent actions
cat ~/.cache/svg2fbf-audit-logs/$(date +%Y-%m-%d).json | jq

# 2. Identify problematic action
# {
#   "timestamp": "2025-01-14T12:34:56Z",
#   "agent_id": "agent-42",
#   "action": "commit",
#   "files_changed": ["justfile"],  # ← Protected file!
#   "commit_hash": "abc1234"
# }

# 3. Use hash to investigate
git show abc1234

# 4. Add to incident report
```

---

## Human Escalation Criteria

**Immediately notify human if**:
- ❌ Pushed to master or main branch
- ❌ Modified CHANGELOG.md or justfile
- ❌ Triggered `just publish` or `just equalize`
- ❌ CI failing on review/master for >1 hour
- ❌ Git corruption detected
- ❌ Multiple agents on same issue with conflicts
- ❌ Released to PyPI by mistake

**Can self-recover if**:
- ✅ Broke tests on dev
- ✅ Uncommitted changes to wrong file
- ✅ Merge conflict on dev/testing
- ✅ Stale worktree
- ✅ Lost commits (recoverable via reflog)

---

## Post-Recovery Checklist

After recovering from any error:

```bash
# 1. Run full test suite
pytest tests/

# 2. Verify linting
ruff check src/ tests/

# 3. Verify formatting
ruff format --check src/ tests/

# 4. Check git status
git status  # Should be clean

# 5. Verify correct branch
git branch --show-current

# 6. Check audit log
cat ~/.cache/svg2fbf-audit-logs/$(date +%Y-%m-%d).json | jq

# 7. Update recovery documentation (if new scenario)
# Add to recovery-procedures.md

# 8. Commit recovery
git add .
git commit -m "fix: Recover from <error-type>"
git push origin <branch>
```

---

## Key Principles

1. **Git is a time machine** - Almost everything is recoverable
2. **Push frequently** - GitHub is source of truth
3. **Use worktrees** - Isolates corruption and mistakes
4. **Never panic** - Reflog keeps 90 days of history
5. **Escalate early** - When in doubt, notify human
6. **Learn from mistakes** - Update procedures for new scenarios
7. **Test recovery** - Practice procedures before needed

## Summary

**Most Common Recoveries**:
- `git restore <file>` - Discard uncommitted changes
- `git reset --soft HEAD~1` - Undo last commit, keep changes
- `git revert <commit>` - Undo commit on public branch
- `git reflog` - Find lost commits

**Emergency Contacts**:
- Human supervisor (always available)
- GitHub repository (source of truth)
- Audit logs (~/.cache/svg2fbf-audit-logs/)
- This document (recovery-procedures.md)
