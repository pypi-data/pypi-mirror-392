# CCPM Promotion Rules

**Skill**: How code moves through the 5-branch pipeline
**Use when**: Ready to promote code to next stage

---

## Overview

Code promotion is the process of moving validated code from one branch to the next in the 5-branch workflow. Promotions are **merge-based** and **human-supervised**.

**Promotion Pipeline**:
```
dev → testing → review → master → main
```

**Critical Rule**: Agents request promotions, humans execute them.

---

## The 4 Promotion Commands

### 1. Promote to Testing (dev → testing)

**Command** (human-only):
```bash
just promote-to-testing
```

**What it does**:
- Merges dev into testing
- Runs merge-based workflow (not fast-forward)
- Preserves branch history
- No CI checks (testing branch has CI disabled)

**Agent Role**:
```bash
# After PR merged to dev and verification complete:
gh issue comment <issue> --body "$(cat <<'EOF'
## Ready for Promotion to Testing

**Checklist**:
- ✅ PR merged to dev
- ✅ All tests pass
- ✅ Linting passes
- ✅ Verification protocol completed

**Requesting promotion to testing branch.**

@user - Please run `just promote-to-testing` when ready.
EOF
)"
```

**Preconditions**:
- Work completed on dev
- Tests pass on dev
- No known bugs

---

### 2. Promote to Review (testing → review)

**Command** (human-only):
```bash
just promote-to-review
```

**What it does**:
- Merges testing into review
- Triggers CI checks (review has CI enabled!)
- Creates release candidate (RC)
- Runs full test suite on CI

**Agent Role**:
```bash
# After QA testing validates the code:
gh issue comment <issue> --body "$(cat <<'EOF'
## Ready for Promotion to Review

**Testing Results**:
- ✅ Functionality tested and verified
- ✅ No regressions found
- ✅ Integration tests pass
- ✅ Ready for release candidate

**Requesting promotion to review branch (RC).**

@user - Please run `just promote-to-review` when ready.
EOF
)"
```

**Preconditions**:
- Testing complete on testing branch
- All bugs found in testing are fixed
- Code is production-ready

---

### 3. Promote to Stable (review → master)

**Command** (human-only):
```bash
just promote-to-stable
```

**What it does**:
- Merges review into master
- Tags release (e.g., v1.2.3)
- Updates CHANGELOG.md
- Triggers PyPI publication (if configured)
- Marks code as stable

**Agent Role**:
```bash
# Agents do NOT request this promotion
# This is a human decision based on:
# - Business requirements
# - Release schedule
# - User feedback on RC

# If asked about it:
gh issue comment <issue> --body "$(cat <<'EOF'
This issue's fix is now in review branch (RC).

Promotion to master (stable release) is a human decision.

I cannot request or influence this promotion.
EOF
)"
```

**Preconditions**:
- CI passes on review
- Release criteria met
- Human approval

**Agent Involvement**: ❌ NONE - Human decision only

---

### 4. Sync to Main (master → main)

**Command** (human-only or automatic):
```bash
just sync-main
```

**What it does**:
- Fast-forward merges master into main
- Ensures main is identical to master
- Updates protected default branch

**Agent Role**: ❌ NONE - Automatic or human-triggered only

**Preconditions**:
- Master has new commits
- Ready to update public-facing default branch

---

## Promotion vs. Direct Push

### ✅ Promotion (Correct):
```bash
# Work on dev
git checkout dev
# Make changes, commit, push

# Human merges dev → testing
just promote-to-testing

# Human merges testing → review
just promote-to-review
```

**Benefits**:
- Preserves history
- Allows testing at each stage
- Enables rollback
- Clear audit trail

---

### ❌ Direct Push (Wrong):
```bash
# WRONG! Don't do this:
git checkout testing
git push origin testing  # Pushed directly without merging dev

# WRONG! Even worse:
git checkout master
git push origin master  # Pushed directly to stable!
```

**Problems**:
- Bypasses quality gates
- Breaks branch divergence
- No testing validation
- History is unclear

---

## Version Bumping During Promotion

### dev → testing: No version bump

Code is still in alpha/beta, version stays same.

---

### testing → review: Optional version bump

May bump to RC version (e.g., v1.2.3-rc1) but not required.

---

### review → master: Required version bump

**Version bumping rules** (Semantic Versioning):

```bash
# Bug fix (backward compatible)
# 1.2.3 → 1.2.4 (patch bump)

# New feature (backward compatible)
# 1.2.3 → 1.3.0 (minor bump)

# Breaking changes (user-approved)
# 1.2.3 → 2.0.0 (major bump)
```

**Process**:
```bash
# Human updates version in pyproject.toml (or equivalent)
# Then runs:
just promote-to-stable
# This tags the release with new version
```

---

## CI Integration

### Branches with CI Disabled:
- dev (allows broken code during development)
- testing (allows testing of potentially broken code)

**Agent impact**: Tests may fail, it's OK on these branches (fix before promoting)

---

### Branches with CI Enabled:
- review (must pass before promotion to master)
- master (must pass before publication)
- main (must pass, identical to master)

**Agent impact**: Code MUST pass all CI checks on review before promotion to master

---

## Rollback Procedures

If promoted code breaks:

### Rollback from testing:
```bash
# Human reverts merge commit
git checkout testing
git revert <merge-commit-hash>
git push origin testing
```

---

### Rollback from review:
```bash
# Human reverts merge commit
git checkout review
git revert <merge-commit-hash>
git push origin review

# CI re-runs, should pass
```

---

### Rollback from master:
```bash
# Human creates hotfix branch
git checkout master
git checkout -b hotfix/v1.2.4-revert-breaking-change

# Human reverts problematic commit
git revert <commit-hash>

# Agent can help with hotfix under supervision
python ccpm/commands/issue_start.py <issue> hotfix/v1.2.4-revert-breaking-change

# Human merges hotfix to master
# Publishes new patch version
```

---

## Forbidden Operations

### ❌ NEVER use `just equalize`

**What it does** (DANGEROUS!):
```bash
# Forces ALL branches to match current branch
# Destroys all divergence
# Irreversible without reflog magic
```

**Why forbidden**:
- Destroys development work on other branches
- Breaks the entire workflow
- Requires extensive recovery
- Human intervention to fix

**If you accidentally run this**: See `ccpm-recovery-procedures` skill, Scenario 10.

---

### ❌ NEVER use `just publish`

**What it does**:
- Publishes package to PyPI
- Creates public release
- Irreversible (can't delete PyPI releases easily)

**Why forbidden**:
- Only humans decide when to publish
- Requires version validation
- Legal/business implications
- Publishing broken code is disaster

**If you accidentally run this**: Immediately notify human, see `ccpm-recovery-procedures` skill.

---

## Agent Promotion Checklist

Before requesting promotion, verify:

### For dev → testing promotion:

- [ ] PR merged to dev
- [ ] All tests pass locally (`pytest tests/`)
- [ ] Linting passes (`ruff check`)
- [ ] Formatting correct (`ruff format --check`)
- [ ] Verification protocol completed (Step 7)
- [ ] No known bugs
- [ ] Documentation updated

### For testing → review promotion:

- [ ] QA testing completed
- [ ] Integration tests pass
- [ ] No regressions found
- [ ] User-facing changes documented
- [ ] Ready for release candidate

**Agents do NOT request review → master promotions** (human decision)

---

## Promotion Timeline

**Typical timeline** (varies by project):

1. **Work completed on dev**: Immediately after PR merged
2. **Promote dev → testing**: Within 1-2 days
3. **Testing validation**: 1-7 days
4. **Promote testing → review**: After testing validates
5. **Review (RC) validation**: 1-7 days
6. **Promote review → master**: Human decision (release schedule)

**Agents**: Focus on getting code into dev and testing. Human handles review → master.

---

## When to Use This Skill

**Use this skill when**:
- Ready to request promotion
- Understanding promotion workflow
- Unsure about version bumping
- Need to understand CI integration

**After using this skill**:
- Use `ccpm-branch-workflow` for branch permissions
- Use `ccpm-verification-protocol` before requesting promotion
- Use `ccpm-issue-workflow` for complete lifecycle

---

## Quick Reference

**Agent Can Request**:
- ✅ dev → testing promotion
- ✅ testing → review promotion

**Agent CANNOT Request**:
- ❌ review → master promotion (human decision)
- ❌ master → main sync (automatic/human)

**Forbidden Commands**:
- ❌ `just equalize` (destroys branches)
- ❌ `just publish` (publishes to PyPI)

**Promotion Method**:
- ✅ Merge-based (preserves history)
- ❌ Fast-forward (loses merge commits)

---

**For complete promotion workflow guide, see**: `ccpm/skills/promotion-rules.md`
