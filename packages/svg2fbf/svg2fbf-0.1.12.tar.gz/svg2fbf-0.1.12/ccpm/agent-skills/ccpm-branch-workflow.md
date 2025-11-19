# CCPM Branch Workflow

**Skill**: Understanding branch hierarchy and permissions
**Use when**: Starting work, choosing target branch, or promoting code

---

## ⚠️ Important: Project-Specific Branch Workflow

**This documentation shows the svg2fbf project's 5-branch workflow** as an example.

**Your project may be different!** Always check the project's `DEVELOPMENT.md` or `CONTRIBUTING.md` to understand:
- Which branches exist
- How code flows between branches
- When to use each branch
- Hotfix/emergency procedures

**CCPM adapts to ANY branch workflow**: single branch, dev → main, feature branches, or complex multi-environment setups.

---

## Overview (svg2fbf Project Example)

This project uses a 5-branch workflow to ensure code quality through staged promotion. Code MUST flow sequentially through all branches.

**Branch Hierarchy**:
```
dev → testing → review → master → main
 ↓       ↓        ↓        ↓       ↓
alpha   beta     rc     stable  (mirror)
```

**Critical Rule**: Never skip stages! (Except hotfixes)

---

## The 5 Branches

### 1. dev (Alpha Channel)

**Purpose**: Active development, experimentation, rapid iteration

**Agent Permission**: ✅ **YES - Primary work branch**

**CI**: ❌ Disabled (tests may fail during development)

**Quality**: Work in progress, breakage acceptable

**What Agents CAN Do**:
- ✅ Create feature branches from dev
- ✅ Commit experimental code
- ✅ Break tests temporarily (fix before promoting)
- ✅ Add dependencies
- ✅ Refactor code
- ✅ Make breaking changes (with plan to fix)

**What Agents CANNOT Do**:
- ❌ Push without committing first
- ❌ Work on multiple issues in same worktree
- ❌ Modify protected files

**Next Step**: Promote to `testing` via `just promote-to-testing` (human-supervised)

---

### 2. testing (Beta Channel)

**Purpose**: QA testing, bug hunting, integration testing

**Agent Permission**: ✅ **YES - Bug fixes only**

**CI**: ❌ Disabled (allows testing of potentially broken code)

**Quality**: Should mostly work, but bugs expected

**What Agents CAN Do**:
- ✅ Fix bugs discovered in testing
- ✅ Improve test coverage
- ✅ Add test documentation
- ✅ Fix failing tests

**What Agents CANNOT Do**:
- ❌ Add new features (only bug fixes!)
- ❌ Make breaking changes
- ❌ Add dependencies (unless fixing bug)

**Next Step**: Promote to `review` via `just promote-to-review` (human-supervised)

---

### 3. review (RC Channel)

**Purpose**: Final approval gate, release candidate validation

**Agent Permission**: ⚠️ **SUPERVISED ONLY - Critical fixes with human approval**

**CI**: ✅ **ENABLED - Tests MUST pass, no exceptions**

**Quality**: Production-ready, zero known bugs

**What Agents CAN Do**:
- ⚠️ Critical bug fixes ONLY (with human supervision)
- ⚠️ Documentation fixes (with human approval)

**What Agents CANNOT Do**:
- ❌ Add features
- ❌ Refactor code
- ❌ Add dependencies
- ❌ Make any changes without human approval

**Next Step**: Promote to `master` via `just promote-to-stable` (human-only decision)

---

### 4. master (Stable Channel)

**Purpose**: Production releases, PyPI publication

**Agent Permission**: ⚠️ **CRITICAL HOTFIXES ONLY** (priority:critical OR priority:blocker)

**CI**: ✅ **ENABLED - Strict validation**

**Quality**: Battle-tested, stable, production-grade

**What Agents CAN Do**:
- ⚠️ Work directly on master for **critical hotfixes** (security, data loss, crashes)
- ⚠️ Must verify issue has `priority:critical` or `priority:blocker` label
- ⚠️ Must explain in commit why normal pipeline was bypassed
- ⚠️ Must check if dev needs backport using `just backport-hotfix`

**What Agents CANNOT Do**:
- ❌ Add new features (ALWAYS dev first)
- ❌ Refactoring (ALWAYS dev first)
- ❌ Non-critical bugs (use dev → testing → review → master)
- ❌ Any changes without critical/blocker label

**Next Step**: Sync to `main` via `just sync-main` (automatic or human-triggered)

---

### 5. main

**Purpose**: Protected default branch, mirror of master

**Agent Permission**: ❌ **ABSOLUTELY NO - Read-only mirror**

**CI**: ✅ **ENABLED**

**Quality**: Identical to master

**What Agents CAN Do**:
- ❌ NOTHING - This is a read-only mirror

**What Agents CANNOT Do**:
- ❌ Any actions whatsoever
- ❌ Auto-synced from master only

---

## Quality Expectations by Branch

| Branch   | Tests  | Linting | Formatting | Docs   | CI     |
|----------|--------|---------|------------|--------|--------|
| dev      | 🟡 OK  | 🟡 OK   | 🟡 OK      | 🟡 OK  | ❌     |
| testing  | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES | ❌     |
| review   | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES | ✅ YES |
| master   | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES | ✅ YES |
| main     | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES | ✅ YES |

**Legend**:
- 🟢 YES = Required, must pass
- 🟡 OK = Best effort, can fail temporarily
- ❌ = CI disabled
- ✅ YES = CI enabled

---

## Choosing Your Target Branch

### For New Issues:

**Start from dev** (99% of cases):
```bash
python ccpm/commands/issue_start.py 123 dev
```

**Start from testing** (rare - only for bugs found in testing):
```bash
# Only if bug was found IN testing branch and doesn't exist in dev
python ccpm/commands/issue_start.py 456 testing
```

**Never start from review/master/main** - Always escalate to human.

---

## Agent Work Rules

### ✅ ALWAYS DO

1. **Work in dedicated worktree** - Never work directly in main repo
2. **Start from dev or testing** - Never from review/master/main
3. **Create Draft PR immediately** - As soon as work begins
4. **Run tests before promoting** - Use `pytest tests/`
5. **Run linting before promoting** - Use `ruff check`
6. **Follow conventional commits** - Format: `type(scope): description`
7. **Request human review** - Before promoting past testing

### ❌ NEVER DO

1. **NEVER merge your own PR** - Wait for human approval
2. **NEVER skip promotion stages** - Must go dev→testing→review→master sequentially
3. **NEVER use `just equalize`** - DANGEROUS human-only command
4. **NEVER run `just publish`** - Release process is human-supervised
5. **NEVER push to review/master/main directly** - Use promotion commands
6. **NEVER modify protected files** - See `ccpm/rules/protected-files.txt`
7. **NEVER force-push** - Respect git history
8. **NEVER work on multiple issues in same worktree** - One issue = one worktree

---

## Common Workflows

### Normal Feature/Bug Fix (dev → testing → review → master):

```bash
# 1. Start work on dev
python ccpm/commands/issue_start.py 123 dev

# 2. Make changes, commit, test
cd ~/.cache/ccpm-worktrees/owner-project/issue-123
# Work...
git add .
git commit -m "fix(cli): Fix issue #123"

# 3. Finish and create PR
python ccpm/commands/issue_finish.py 123
# This creates PR to dev

# 4. After PR merged to dev, request promotion
gh issue comment 123 --body "@user - Ready for promotion to testing. All tests pass."

# 5. Human runs: just promote-to-testing
# Code is now in testing branch

# 6. After testing validates, request promotion to review
gh issue comment 123 --body "@user - Testing complete, ready for review branch."

# 7. Human runs: just promote-to-review
# Code is now in review branch (RC)

# 8. Human reviews and decides to promote to stable
# Human runs: just promote-to-stable
# Code is now in master (stable)

# 9. Automatic or human-triggered sync to main
# just sync-main
# Code is now in main (protected mirror)
```

---

## Hotfix Workflow (EXCEPTION to "Never Skip Stages")

When critical bugs are found in production (master/main), agents CAN work directly on master.

### When Agents Can Work on Master

**Only for truly critical issues:**
- ✅ Security vulnerabilities affecting stable
- ✅ Data loss bugs in production
- ✅ Crash bugs affecting all users
- ✅ Code in dev has diverged (bug no longer there)
- ✅ Issue labeled `priority:critical` or `priority:blocker`

### Hotfix Process

```bash
# 1. Verify this is critical
gh issue view <number> --json labels
# Must have: priority:critical OR priority:blocker

# 2. Work directly on master (EXCEPTION)
git checkout master
git pull origin master

# Make the fix (minimal changes only!)
# - Fix ONLY the critical bug
# - NO new features
# - NO refactoring
# - Minimal changes only

# 3. Commit with explanation
git commit -m "fix(critical): Description #<number>

HOTFIX for production release.
Bypasses normal dev pipeline because:
- [Critical security/data loss/crash]
- [Dev already fixed/removed this code]

Fixes #<number>"

# 4. Push to master
git push origin master

# 5. Check if dev needs the fix
git checkout dev
grep -r "vulnerable_code" src/

# 6a. If dev needs fix → backport
git checkout dev
just backport-hotfix  # Select the commit
just test
git push origin dev

# 6b. If dev doesn't need fix → document
gh issue comment <number> --body "✅ Hotfix applied to master.
Dev not affected (code refactored)."

# 7. Release patch version
git checkout master
just release patch
```

### When NOT to Use Hotfix Workflow

**DO NOT use hotfix for:**
- ❌ Non-critical bugs → use dev pipeline
- ❌ New features → ALWAYS dev first
- ❌ Refactoring → ALWAYS dev first
- ❌ "Nice to have" fixes → use normal pipeline
- ❌ Anything that can wait → use normal pipeline

**Remember**: 99% of issues should go through dev → testing → review → master!

---

## Common Mistakes

### ❌ Mistake 1: "I'll push this small fix directly to master"

**Why Wrong**: Bypasses quality gates, breaks workflow

**Correct**: Work in dev, promote through pipeline

---

### ❌ Mistake 2: "Tests failing on dev, I'll skip to review"

**Why Wrong**: Skipping stages breaks the workflow

**Correct**: Fix tests on dev, then promote to testing

---

### ❌ Mistake 3: "I'll use `just equalize` to sync branches quickly"

**Why Wrong**: `just equalize` force-syncs ALL branches to current branch, destroying divergence and history

**Correct**: NEVER use `just equalize` - let humans handle branch syncing

---

### ❌ Mistake 4: "I'll merge my own PR to speed things up"

**Why Wrong**: No human review, might merge broken code

**Correct**: Wait for human review ALWAYS

---

### ❌ Mistake 5: "I'll work on issue-123 and issue-456 in same worktree"

**Why Wrong**: Issues get mixed, hard to track, conflicts likely

**Correct**: One issue = one worktree, no exceptions

---

## Branch Protection (Phase 4+)

In later phases, GitHub branch protection will be enabled:

**Protected Branches**: review, master, main
- Require PR reviews
- Require status checks to pass
- Prevent force-push
- Prevent deletion

**Agent Impact**:
- Must work through PRs (already doing this)
- Can't bypass reviews (already can't)
- Enhanced safety

---

## When to Use This Skill

**Use this skill when**:
- Starting new work (which branch?)
- Unsure if you can work on a branch
- Need to understand promotion workflow
- Made a mistake with branches

**After using this skill**:
- Use `ccpm-issue-workflow` for complete issue lifecycle
- Use `ccpm-promotion-rules` for promotion commands
- Use `ccpm-recovery-procedures` if you pushed to wrong branch

---

## Quick Reference

**Agent-Safe Branches**: dev, testing, hotfix/*

**Human-Only Branches**: review, master, main

**Never Use**: `just equalize`, `just publish`, force-push

**Always Use**: Worktrees, Draft PRs, conventional commits, human review

---

**For complete branch workflow guide, see**: `ccpm/skills/5-branch-workflow.md`
