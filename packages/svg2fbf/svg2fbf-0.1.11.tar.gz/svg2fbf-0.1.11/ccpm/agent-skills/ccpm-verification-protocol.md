# CCPM Critical Verification Protocol

**Skill**: Complete 8-step verification process before closing ANY issue
**Use when**: After PR is merged and before closing issue

---

## Overview

This is the **MANDATORY** verification protocol that MUST be completed before declaring any issue resolved. Never skip this step!

**Why This Matters**:
- Prevents false "resolved" status
- Detects regressions early
- Ensures backward compatibility
- Finds related issues that are also fixed
- Protects users from breaking changes

---

## The 8-Step Verification Protocol

### Step 7.1: Pull Latest Changes

```bash
# Sync with latest dev branch
git checkout dev
git pull origin dev
```

**Why**: Ensure you're testing the actual merged code, not old code.

---

### Step 7.2: Reproduce Original Issue Again (MANDATORY)

**⚠️ CRITICAL**: You MUST verify the issue is actually fixed by reproducing it again.

#### For Bug Fixes:
```bash
# Use EXACT same steps as when you reproduced during Step 2
# Example from issue #7 (duplicate header bug):
svg2fbf --input_folder ./test_frames --output_path /tmp/test.fbf.svg

# Expected: Header appears ONCE (not twice)
# If still appears twice → Bug NOT fixed, reopen issue!
```

#### For New Features/Changes:
```bash
# Create temporary test script
cat > /tmp/test_issue_<number>.sh <<'EOF'
#!/bin/bash
# Test the new feature/change
<your test code here>

# Example:
output=$(svg2fbf --new-feature-flag --input test/)
if echo "$output" | grep -q "expected behavior"; then
    echo "✅ PASS: Feature works as expected"
    exit 0
else
    echo "❌ FAIL: Feature not working"
    exit 1
fi
EOF

chmod +x /tmp/test_issue_<number>.sh
/tmp/test_issue_<number>.sh

# Clean up after verification
rm /tmp/test_issue_<number>.sh
```

**If issue persists or feature doesn't work**:
- ❌ Fix FAILED
- Reopen issue immediately
- Do NOT close

---

### Step 7.3: Run ALL Tests for Regressions (MANDATORY)

```bash
# Run complete test suite
pytest tests/ -v

# ALL tests MUST pass!
# If ANY test fails that previously passed:
```

**If regressions detected**:
```bash
# Option A: Fix the code to be backward compatible
# Edit code to not break existing functionality
git add <fixed-files>
git commit -m "fix: Resolve regression in <component> from issue #X"
git push origin dev

# Option B: Update tests if expectations legitimately changed
# But ONLY if the change was intentional and documented!
# Never ignore failing tests!

# DO NOT close issue until regressions are fixed!
```

**Why This Matters**: Your fix might have broken other parts of the codebase.

---

### Step 7.4: Check for Breaking Changes (MANDATORY)

**Ask yourself these questions**:
- ❓ Did you change any function signatures?
- ❓ Did you remove or rename any public APIs?
- ❓ Did you change CLI arguments or flags?
- ❓ Did you change configuration file formats?
- ❓ Did you change output formats?
- ❓ Did you change the behavior of existing functions?

**If YES to ANY → Breaking changes detected!**

#### Breaking Changes Protocol:

```bash
# 1. Document ALL breaking changes
cat > /tmp/breaking_changes.md <<'EOF'
## Breaking Changes in Issue #X Fix

### Changed Function Signatures
- `old_function(a, b)` → `new_function(a, b, c)` (added required parameter c)

### Removed APIs
- Removed deprecated `legacy_method()` (use `new_method()` instead)

### Changed CLI Arguments
- `--old-flag` removed (use `--new-flag` instead)

### Changed Output Format
- JSON output now uses camelCase instead of snake_case

### Migration Guide for Users
Users need to:
1. Update calls to `old_function()` to include new parameter `c`
2. Replace `legacy_method()` with `new_method()`
3. Replace `--old-flag` with `--new-flag` in scripts
4. Update JSON parsers to handle camelCase
EOF

# 2. Ask user for explicit approval (WITH @MENTION!)
gh issue comment <issue-number> --body "$(cat <<'EOF'
## ⚠️ Breaking Changes Detected

This fix introduces **backward-incompatible changes** that will break existing user code:

[Paste breaking_changes.md content here]

**Version Bump Required**: Major version (e.g., 1.x.x → 2.0.0)

**Documentation Updates Required**:
- CHANGELOG.md (breaking changes section)
- README.md (updated API examples)
- Migration guide for users

**⚠️ User Approval Required**: @<username> - Do you approve these breaking changes?
- [ ] Yes, approve and bump major version
- [ ] No, find backward-compatible solution

Please respond before I proceed.
EOF
)"

# 3. WAIT for user approval
# ⚠️ DO NOT PROCEED WITHOUT USER APPROVAL!
# ⚠️ DO NOT CLOSE THE ISSUE!
# ⚠️ DO NOT MERGE TO HIGHER BRANCHES!

# 4. If user APPROVES:
# - Bump major version in pyproject.toml (or equivalent)
# - Update CHANGELOG.md with breaking changes section
# - Update all documentation
# - Create migration guide
# - Only then can you close the issue

# 5. If user REJECTS:
# - Revert breaking changes
# - Find backward-compatible solution
# - Implement with deprecation warnings instead
# - Add shims for old API while introducing new API
```

**Critical Rule**: NEVER merge breaking changes without explicit user approval with @mention!

---

### Step 7.5: Check for Related Issues (MANDATORY)

**Your fix might have solved other issues too!**

```bash
# 1. Search for related open issues with keywords
gh issue list --state open --search "in:title,body <keywords from your fix>"

# Example: If you fixed header duplication
gh issue list --state open --search "in:title,body header duplicate output"
gh issue list --state open --search "in:title,body print twice"
gh issue list --state open --search "in:title,body console output header"

# 2. For EACH potentially related issue:

# a) Read the issue description
gh issue view <related-issue-number>

# b) Reproduce using THEIR steps (not yours!)

# c) Run steps 7.2, 7.3, 7.4 for that issue too!

# 3. If another issue IS also fixed:
gh issue comment <related-issue-number> --body "$(cat <<'EOF'
## ✅ Resolved as Side Effect of #<original-issue>

This issue appears to be resolved by the fix for #<original-issue>.

**Root Cause**: Same underlying issue (duplicate header printing)

**Verification Completed**:
- ✅ Reproduced original issue
- ✅ Verified fix resolves it
- ✅ No regressions detected (all tests pass)
- ✅ No breaking changes detected

**Fixed in**: PR #<pr-number>

Closing as completed.
EOF
)"

gh issue close <related-issue-number> --reason "completed"
gh issue edit <related-issue-number> --add-label "duplicate,fixed"

# 4. Update original issue with cross-reference
gh issue comment <original-issue> --body "Note: This fix also resolved #<related-1>, #<related-2>"
```

**Why This Matters**: Fixes often solve multiple related issues. Finding and closing them saves time!

---

### Step 7.6: Final Verification Checklist

Before closing, verify **ALL** checkboxes:

- [ ] Original issue reproduced and verified fixed (or new feature tested with temp script)
- [ ] All tests pass (no regressions)
- [ ] Backward compatibility maintained OR user approved breaking changes
- [ ] Related issues checked and closed if also fixed
- [ ] Documentation updated if needed
- [ ] Migration guide created if breaking changes
- [ ] Version bumped appropriately (major if breaking, minor if feature, patch if bugfix)

**If ANY checkbox is unchecked → DO NOT CLOSE ISSUE!**

---

### Step 7.7: Close Issue (ONLY After ALL Checks Pass)

```bash
gh issue close <issue-number> --reason "completed" --comment "$(cat <<'EOF'
## ✅ Verified Fixed - Complete Verification Report

### 1. Original Issue Verification
- ✅ Reproduced original issue
- ✅ Verified fix resolves issue
- **Test method**: [Exact reproduction steps OR temp test script used]

### 2. Regression Testing
- ✅ All tests pass
- **Test results**: X/X tests passed, 0 failed

### 3. Backward Compatibility
- ✅ No breaking changes
  OR
- ✅ Breaking changes approved by user (see comment #N)
- ✅ Major version bumped to X.0.0
- ✅ Migration guide created: [link]

### 4. Related Issues
- ✅ Checked for related issues
- ✅ Also fixed: #<issue-1>, #<issue-2>
  OR
- ✅ No related issues found

### 5. Documentation
- ✅ CHANGELOG.md updated
- ✅ README.md updated (if needed)
- ✅ Migration guide added (if breaking changes)

**Fixed in**: PR #<pr-number>
**Available in**: dev branch (will be in next release)

Closing as completed after full verification protocol.
EOF
)"

# Update label
gh issue edit <issue-number> --remove-label "needs-review" --add-label "fixed"
```

---

### Step 7.8: If ANY Verification Fails

```bash
# Reopen immediately!
gh issue reopen <issue-number>

gh issue comment <issue-number> --body "$(cat <<'EOF'
## ⚠️ Verification Failed - Issue Reopened

**Failure details**:
- [ ] Original issue still reproducible (bug not actually fixed)
- [ ] Regression detected in: [specific component/test]
- [ ] Breaking changes detected - awaiting user approval
- [ ] Related issue check incomplete

**Next steps**:
1. [Specific action needed to address failure]
2. [Specific action needed]

Reopening for further investigation.
EOF
)"

# Update labels
gh issue edit <issue-number> --add-label "regression" --remove-label "fixed"
```

---

## Critical Rules

### ALWAYS

- ✅ Complete ALL 8 steps before closing
- ✅ Reproduce original issue again (or test feature with temp script)
- ✅ Run full test suite
- ✅ Check for breaking changes
- ✅ Get user approval for ANY breaking changes (with @mention)
- ✅ Search for and test related issues
- ✅ Create temp test scripts for features (delete after)

### NEVER

- ❌ Skip verification to "save time"
- ❌ Ignore failing tests ("I'll fix later")
- ❌ Merge breaking changes without user approval
- ❌ Close without checking related issues
- ❌ Assume feature works without testing it

---

## When to Use This Skill

**Use this skill**:
- After PR is merged
- Before closing ANY issue
- When user asks "is issue X fixed?"
- When you need to verify a fix

**After using this skill**:
- Use `ccpm-breaking-changes` if Step 7.4 detected breaking changes
- Use `ccpm-label-management` to update issue labels correctly
- Use `ccpm-recovery-procedures` if verification fails

---

## Quick Troubleshooting

**Issue**: "Tests were passing in PR but failing now"
→ Pull latest dev, re-run tests, fix conflicts or regressions

**Issue**: "Don't know if this is a breaking change"
→ Use `ccpm-breaking-changes` skill for detection criteria

**Issue**: "User hasn't responded to approval request"
→ DO NOT close issue, wait for response, ping again if >24h

**Issue**: "Found 10+ related issues"
→ Test top 3 most similar, ask user if you should verify all

---

**Remember**: Verification is NOT optional. Agents who skip verification create technical debt and frustrated users!

For complete 280-line detailed guide, see: `ccpm/skills/issue-management.md` (Step 7)
