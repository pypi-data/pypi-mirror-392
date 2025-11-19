# CCPM Branch Workflow Guide

## ⚠️ Important: Project-Specific Branch Workflow

**This documentation shows the svg2fbf project's 5-branch workflow** as an example.

**Your project may be different!** CCPM adapts to ANY branch configuration:
- Single branch (main only)
- Simple workflow (dev → main)
- Feature branches (feature/* → main)
- Complex multi-environment setups
- Custom workflows with hundreds of branches

**Always check your project's `DEVELOPMENT.md` or `CONTRIBUTING.md`** to understand:
- Which branches exist in YOUR project
- How code flows between branches
- When to use each branch
- Hotfix/emergency procedures specific to your project

**CCPM provides the framework**, your project defines the specific workflow.

---

## svg2fbf Project's 5-Branch Workflow

### Branch Hierarchy (NEVER skip stages)

```
dev → testing → review → master → main
 ↓       ↓        ↓        ↓       ↓
alpha   beta     rc     stable  (mirror)
```

**Critical Rule**: Code MUST flow sequentially through all stages. No skipping allowed (except hotfixes).

## Branch Rules

### dev (Alpha Channel)
- **Purpose**: Active development, rapid iteration, experimental features
- **CI**: ❌ Disabled (tests may fail during development)
- **Agent Permission**: ✅ **YES** - Primary work branch for agents
- **Quality Expectation**: Work in progress, breakage acceptable
- **Merge to**: `testing` (via `just promote-to-testing`)
- **Agent Actions Allowed**:
  - ✅ Create feature branches
  - ✅ Commit experimental code
  - ✅ Break tests temporarily (fix before promoting)
  - ✅ Add dependencies
  - ✅ Refactor code

### testing (Beta Channel)
- **Purpose**: QA testing, bug hunting, integration testing
- **CI**: ❌ Disabled (allows testing of potentially broken code)
- **Agent Permission**: ✅ **YES** - Bug fixes and testing improvements only
- **Quality Expectation**: Should mostly work, but bugs expected
- **Merge to**: `review` (via `just promote-to-review`)
- **Agent Actions Allowed**:
  - ✅ Fix bugs discovered in testing
  - ✅ Improve test coverage
  - ✅ Add test documentation
  - ⚠️ NO new features (only bug fixes)

### review (RC Channel)
- **Purpose**: Final approval gate, release candidate validation
- **CI**: ✅ **ENABLED** - Tests MUST pass, no exceptions
- **Agent Permission**: ⚠️ **SUPERVISED ONLY** - Human must review before promotion
- **Quality Expectation**: Production-ready, zero known bugs
- **Merge to**: `master` (via `just promote-to-stable`)
- **Agent Actions Allowed**:
  - ⚠️ Critical bug fixes ONLY (with human supervision)
  - ⚠️ Documentation fixes (with human approval)
  - ❌ NO features
  - ❌ NO refactoring
  - ❌ NO dependency changes

### master (Stable Channel)
- **Purpose**: Production releases, PyPI publication
- **CI**: ✅ **ENABLED** - Strict validation
- **Agent Permission**: ⚠️ **CRITICAL HOTFIXES ONLY** (priority:critical OR priority:blocker)
- **Quality Expectation**: Battle-tested, stable, production-grade
- **Merge to**: `main` (auto-synced via `just sync-main`)
- **Agent Actions Allowed**:
  - ⚠️ Work directly on master for **critical hotfixes** (security, data loss, crashes)
  - ⚠️ Must verify issue has `priority:critical` or `priority:blocker` label
  - ⚠️ Must explain in commit why normal pipeline was bypassed
  - ⚠️ Must check if dev needs backport using `just backport-hotfix`
- **Agent Actions FORBIDDEN**:
  - ❌ Add new features (ALWAYS dev first)
  - ❌ Refactoring (ALWAYS dev first)
  - ❌ Non-critical bugs (use dev → testing → review → master)
  - ❌ Any changes without critical/blocker label

### main
- **Purpose**: Mirror of master, protected default branch
- **CI**: ✅ **ENABLED**
- **Agent Permission**: ❌ **ABSOLUTELY NO** - Read-only mirror
- **Quality Expectation**: Identical to master
- **Agent Actions Allowed**:
  - ❌ NO actions whatsoever
  - ❌ Auto-synced from master only

## Agent Work Rules (READ THIS CAREFULLY)

### ✅ ALWAYS DO:
1. **Work in dedicated worktree** - Never work directly in main repo
2. **Start from dev or testing** - Never start from review/master/main
3. **Create Draft PR immediately** - As soon as work begins
4. **Run tests before promoting** - Use `just test` or `pytest`
5. **Run linting before promoting** - Use `just lint` or `ruff check`
6. **Follow conventional commits** - Format: `type(scope): description`
7. **Document changes** - Update relevant .md files
8. **Request human review** - Before promoting past testing

### ❌ NEVER DO:
1. **NEVER merge your own PR** - Always wait for human approval
2. **NEVER skip promotion stages** - Must go dev→testing→review→master sequentially
3. **NEVER use `just equalize`** - This is DANGEROUS, human-only command
4. **NEVER run `just publish`** - Release process is human-supervised
5. **NEVER push to review/master/main directly** - Use promotion commands only
6. **NEVER modify protected files** - See `protected-files.txt` for blacklist
7. **NEVER force-push** - Respect git history
8. **NEVER work on multiple issues in same worktree** - One issue = one worktree

## Promotion Commands (Human-Supervised)

### From dev to testing:
```bash
just promote-to-testing
```
**Agent Role**: Request promotion after tests pass, human executes

### From testing to review:
```bash
just promote-to-review
```
**Agent Role**: Notify human when ready, human executes

### From review to master:
```bash
just promote-to-stable
```
**Agent Role**: NO involvement, human decision only

### From master to main:
```bash
just sync-main
```
**Agent Role**: NO involvement, automatic or human-triggered

### Emergency Override (DANGEROUS):
```bash
just equalize
```
**Agent Role**: ❌ **NEVER USE** - This force-syncs all branches to current branch, destroying divergence

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

1. **Verify issue is critical**:
   ```bash
   gh issue view <number> --json labels
   # Must have: priority:critical OR priority:blocker
   ```

2. **Work directly on master** (EXCEPTION):
   ```bash
   git checkout master
   git pull origin master
   # Fix ONLY the critical bug
   # NO new features, NO refactoring, minimal changes only
   git commit -m "fix(critical): Description #<number>

   HOTFIX for production release.
   Bypasses normal dev pipeline because:
   - [Explain why critical]
   - [Explain dev status]

   Fixes #<number>"
   git push origin master
   ```

3. **Check if dev needs the fix**:
   ```bash
   git checkout dev
   grep -r "vulnerable_pattern" src/
   ```

4. **Backport to dev if needed**:
   ```bash
   # If dev has same bug:
   git checkout dev
   just backport-hotfix  # Select the commit
   just test
   git push origin dev

   # If dev doesn't have bug:
   gh issue comment <number> --body "✅ Hotfix applied to master.
   Dev not affected (code refactored)."
   ```

5. **Release patch version**:
   ```bash
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

**Remember**: 99% of issues go through dev → testing → review → master!

## Quality Expectations by Branch

| Branch   | Tests  | Linting | Formatting | Docs | CI     |
|----------|--------|---------|------------|------|--------|
| dev      | 🟡 OK  | 🟡 OK   | 🟡 OK      | 🟡 OK| ❌     |
| testing  | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES| ❌    |
| review   | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES| ✅ YES |
| master   | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES| ✅ YES |
| main     | 🟢 YES | 🟢 YES  | 🟢 YES     | 🟢 YES| ✅ YES |

Legend:
- 🟢 YES = Required, must pass
- 🟡 OK = Best effort, can fail temporarily
- ❌ = CI disabled
- ✅ YES = CI enabled

## Common Mistakes (DON'T DO THESE)

❌ **Mistake**: "I'll just push this small fix directly to master"
✅ **Correct**: Work in dev, promote through pipeline

❌ **Mistake**: "Tests are failing on dev, I'll skip to review"
✅ **Correct**: Fix tests on dev, then promote to testing

❌ **Mistake**: "I'll use `just equalize` to sync branches quickly"
✅ **Correct**: NEVER use equalize - it destroys git history

❌ **Mistake**: "I'll merge my own PR to speed things up"
✅ **Correct**: Wait for human review, ALWAYS

❌ **Mistake**: "I'll work on issue-123 and issue-456 in same worktree"
✅ **Correct**: One issue = one worktree, no exceptions

## Recovery from Mistakes

If you accidentally:
- **Pushed to wrong branch**: Notify human immediately, see `recovery-procedures.md`
- **Broke tests on dev**: Fix them before promoting, it's OK on dev
- **Modified protected file**: Revert immediately, check `protected-files.txt`
- **Lost commits**: Check worktree, run `git reflog`, notify human

## Summary

**Agent-Safe Branches**: dev, testing, hotfix/*
**Human-Only Branches**: review, master, main
**Never Use**: `just equalize`, `just publish`, force-push
**Always Use**: Worktrees, Draft PRs, conventional commits, human review
