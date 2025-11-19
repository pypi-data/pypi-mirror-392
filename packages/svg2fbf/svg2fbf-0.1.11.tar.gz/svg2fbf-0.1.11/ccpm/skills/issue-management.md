# Issue Management for AI Agents

## Critical Rule for Agents

**BEFORE working on ANY issue**, you MUST follow the complete issue lifecycle documented below. Jumping straight to code is forbidden.

---

## Step 0: Ensure Labels Are Set Up (First Time Only)

**Before working on your first issue**, verify that GitHub labels are configured:

```bash
# Check if labels exist
gh label list

# If empty or missing key labels, run setup
python ccpm/commands/setup_labels.py
```

**This creates 46 standard labels** across 8 categories:
- **Status**: `needs-triage`, `examining`, `reproduced`, `in-progress`, etc.
- **Type**: `bug`, `enhancement`, `documentation`, `question`, etc.
- **Priority**: `priority:critical`, `priority:high`, `priority:medium`, `priority:low`
- **Component**: `component:cli`, `component:svg-import`, `component:ui/ux`, etc.
- **Effort**: `effort:trivial`, `effort:small`, `effort:medium`, `effort:large`, `effort:epic`
- **Contribution**: `good first issue`, `help wanted`, `agent-friendly`, `needs-human`
- **Platform**: `platform:windows`, `platform:macos`, `platform:linux`, `platform:all`
- **Standard**: `dependencies`, `security`, `performance`, `breaking-change`

**Auto-setup**: The setup script checks for existing labels and only creates missing ones. Safe to run multiple times.

**When to run**:
- ✅ First time working on svg2fbf issues
- ✅ After repository label cleanup
- ✅ If you get "label not found" errors

**DO NOT run with `--force`** unless specifically instructed by a human (it deletes and recreates all labels).

---

## Issue Lifecycle Workflow

```
New Issue → Triage → Reproduce → Verify → Work → Verify Fix → Close
    ↓          ↓         ↓          ↓       ↓         ↓          ↓
  Label:   examining  repro-    verified  in-prog  fixed      closed
                      needed                       (PR)
```

---

## Step 1: Check for Duplicates (MANDATORY)

**Before creating OR working on an issue**, search for duplicates:

```bash
# Search existing issues
gh issue list --search "in:title,body <keywords>" --state all

# Examples:
gh issue list --search "in:title,body header duplicate" --state all
gh issue list --search "in:title,body viewBox error" --state all
gh issue list --search "in:title,body import frames" --state all
```

### If Duplicate Found:

1. **DO NOT create new issue** - Comment on existing issue instead
2. **DO NOT work on new issue** - Link to existing issue
3. Add comment to new issue:
   ```bash
   gh issue comment <new-issue> --body "Duplicate of #<original-issue>"
   ```
4. Close new issue as duplicate:
   ```bash
   gh issue close <new-issue> --reason "not planned" --comment "Closing as duplicate of #<original-issue>"
   ```
5. Work on the original issue instead

### If NOT Duplicate:

Proceed to Step 2 (Reproduction).

---

## Step 2: Reproduce the Issue (MANDATORY)

**Never start working without reproducing the issue first.**

### Reproduction Checklist:

1. **Read issue description carefully**
   - What is the expected behavior?
   - What is the actual behavior?
   - What are the steps to reproduce?

2. **Gather reproduction information**:
   - Command line arguments used
   - Input files (SVG frames)
   - Environment (Python version, OS, dependencies)
   - Error messages or screenshots

3. **Attempt reproduction**:
   ```bash
   # Example: Try to reproduce the duplicate header issue
   cd tests/sessions/test_session_001_2frames/input_frames/
   svg2fbf --input_folder . --output_path /tmp/test.fbf.svg
   # Observe console output for duplicate headers
   ```

4. **Document reproduction**:
   - ✅ If reproduced: Add comment with steps
   - ❌ If NOT reproduced: Request more information

---

## Step 3: Handle Non-Reproducible Issues

### If You CANNOT Reproduce (Attempt 1):

1. **Label as `needs-reproduction`**:
   ```bash
   gh issue edit <issue-number> --add-label "needs-reproduction"
   ```

2. **Ask for clarification** (be specific):
   ```bash
   gh issue comment <issue-number> --body "$(cat <<'EOF'
   ## Unable to Reproduce

   I attempted to reproduce this issue but was unsuccessful.

   **What I tried**:
   - Command: `svg2fbf --input_folder ./frames --output_path test.fbf.svg`
   - Input: 10 SVG frames (1920x1080)
   - Environment: Python 3.12, svg2fbf v0.1.8

   **What I observed**:
   - [Describe what you saw]

   **Questions to help reproduce**:
   1. What exact command did you run?
   2. Can you share a sample SVG frame?
   3. What version of svg2fbf are you using? (`svg2fbf --version`)
   4. What is your Python version? (`python --version`)
   5. What operating system?

   Please provide these details so I can reproduce and fix the issue.
   EOF
   )"
   ```

3. **Wait for response** - Do not proceed until more information provided

### If You CANNOT Reproduce (Attempt 2):

Same as Attempt 1, but add:
```bash
gh issue comment <issue-number> --body "**Reproduction Attempt 2/3**: Still unable to reproduce with provided information. Please provide the details requested above."
```

### If You CANNOT Reproduce (Attempt 3 - FINAL):

1. **Label as `cannot-reproduce`**:
   ```bash
   gh issue edit <issue-number> --add-label "cannot-reproduce"
   ```

2. **Close the issue**:
   ```bash
   gh issue close <issue-number> --reason "not planned" --comment "$(cat <<'EOF'
   ## Closing as Cannot Reproduce

   After 3 attempts, I was unable to reproduce this issue with the information provided.

   **Attempts made**:
   1. [Date] - Initial attempt, requested clarification
   2. [Date] - Second attempt with additional details
   3. [Date] - Final attempt, still cannot reproduce

   **Closing criteria**: Per project policy, issues that cannot be reproduced after 3 attempts are closed to keep the issue tracker clean.

   **If you can still reproduce**:
   - Please open a new issue with complete reproduction steps
   - Include exact commands, input files, environment details
   - Screenshots or error logs if applicable

   Feel free to reopen if you can provide reproduction steps.
   EOF
   )"
   ```

---

## Step 4: Label Taxonomy (Use These Labels)

### Status Labels (Issue Lifecycle)

| Label | Meaning | When to Use |
|-------|---------|-------------|
| `needs-triage` | New issue, not yet examined | Auto-applied to new issues |
| `examining` | Agent is investigating | When you start looking at an issue |
| `needs-reproduction` | Waiting for repro info | When you can't reproduce (attempts 1-2) |
| `cannot-reproduce` | Closed after 3 failed attempts | After 3rd failed reproduction |
| `reproduced` | Successfully reproduced | When you confirm the bug exists |
| `verified` | Issue confirmed valid | After reproducing and understanding root cause |
| `in-progress` | Agent is working on fix | When you run `issue_start.py` |
| `needs-review` | Fix ready, awaiting human | When PR created |
| `fixed` | Fix merged and released | After PR merged |

### Type Labels

| Label | Meaning |
|-------|---------|
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |
| `documentation` | Docs need update |
| `question` | User question, not a bug |
| `duplicate` | Duplicate of existing issue |

### Priority Labels

| Label | Meaning |
|-------|---------|
| `priority:critical` | Blocks users, needs immediate fix |
| `priority:high` | Important, fix soon |
| `priority:medium` | Normal priority |
| `priority:low` | Nice to have |

### Component Labels

| Label | Meaning |
|-------|---------|
| `component:cli` | Command-line interface |
| `component:svg-import` | SVG frame import logic |
| `component:fbf-generation` | FBF.SVG generation |
| `component:validation` | Validation and error checking |
| `component:ui/ux` | User interface/experience |
| `component:tests` | Test suite |
| `component:ci/cd` | Build and release automation |

---

## Label Usage Rules (CRITICAL - Read This!)

### Status Label Workflow (Mutually Exclusive)

**IMPORTANT**: Only ONE status label should be active at a time. Status labels represent the current state of the issue.

**Status Transitions** (Normal Flow):
```
needs-triage → examining → reproduced → verified → in-progress → needs-review → fixed
              └─→ needs-reproduction (if can't reproduce)
                  └─→ examining (when user provides info)
                  └─→ cannot-reproduce (after 3 attempts)
```

**When to ADD status labels**:
- `examining`: When you start investigating an issue
- `needs-reproduction`: When you can't reproduce (attempts 1-2)
- `cannot-reproduce`: After 3rd failed reproduction attempt
- `reproduced`: When you successfully reproduce the bug
- `verified`: After reproducing AND understanding root cause
- `in-progress`: When running `issue_start.py`
- `needs-review`: When creating a PR
- `fixed`: After PR merged

**When to REMOVE status labels**:
- Remove `needs-triage` when adding `examining`
- Remove `examining` when adding `reproduced` or `needs-reproduction`
- Remove `needs-reproduction` when adding `reproduced` or `cannot-reproduce`
- Remove `reproduced` when adding `verified`
- Remove `verified` when adding `in-progress`
- Remove `in-progress` when adding `needs-review`
- Remove `needs-review` when adding `fixed`

**Example workflow**:
```bash
# Start examining
gh issue edit 7 --remove-label "needs-triage" --add-label "examining"

# Successfully reproduced
gh issue edit 7 --remove-label "examining" --add-label "reproduced"

# Verified root cause
gh issue edit 7 --remove-label "reproduced" --add-label "verified"

# Start working
gh issue edit 7 --remove-label "verified" --add-label "in-progress"

# Created PR
gh issue edit 7 --remove-label "in-progress" --add-label "needs-review"

# PR merged
gh issue edit 7 --remove-label "needs-review" --add-label "fixed"
```

### Type Labels (Can Have Multiple)

**Can coexist**:
- `bug` + `regression` (a bug that previously worked)
- `bug` + `security` (security vulnerability)
- `enhancement` + `breaking-change` (new feature that breaks compatibility)
- `documentation` + `good first issue` (docs improvement for newcomers)

**Mutually exclusive**:
- `bug` vs `enhancement` (it's either broken or a new feature)
- `bug` vs `question` (questions aren't bugs)
- `duplicate` (should be the ONLY type label if issue is duplicate)

**When to use**:
- `bug`: Something is broken or behaves incorrectly
- `enhancement`: New feature or improvement to existing feature
- `documentation`: Only documentation needs update (not code)
- `question`: User asking how to use something (not a bug)
- `duplicate`: Issue already exists (close this one)
- `invalid`: Issue doesn't seem right or is spam
- `regression`: Previously working feature now broken

### Priority Labels (Mutually Exclusive)

**Only ONE priority label at a time**:
- `priority:critical` - Blocks users, production down, data loss risk
- `priority:high` - Impacts many users, needs fix in next release
- `priority:medium` - Normal bugs and features (default)
- `priority:low` - Nice to have, cosmetic issues

**When to change priority**:
```bash
# Upgrade priority if issue is worse than initially thought
gh issue edit 7 --remove-label "priority:medium" --add-label "priority:high"

# Downgrade if workaround found
gh issue edit 7 --remove-label "priority:critical" --add-label "priority:high"
```

### Component Labels (Can Have Multiple)

**Can coexist** (issue affects multiple components):
- `component:cli` + `component:validation` (CLI needs better validation)
- `component:svg-import` + `component:tests` (import bug found in tests)
- `component:ui/ux` + `component:cli` (CLI output is confusing)

**When to use multiple**:
- If fix requires changes in multiple components
- If bug spans multiple areas

**Example**:
```bash
# Issue affects both CLI and validation
gh issue edit 7 --add-label "component:cli,component:validation"
```

### Effort Labels (Mutually Exclusive)

**Only ONE effort label at a time**:
- `effort:trivial` - Less than 1 hour (typo fix, simple output change)
- `effort:small` - 1-4 hours (small bug fix, minor feature)
- `effort:medium` - 1-2 days (typical bug fix with tests)
- `effort:large` - 3-5 days (complex feature, architectural change)
- `effort:epic` - More than 1 week (major feature, redesign)

**When to add**:
- After reproducing and understanding the fix scope
- Helps prioritize work

**Example**:
```bash
# After examining issue 7, it's a small fix
gh issue edit 7 --add-label "effort:small"
```

### Contribution Labels (Can Have Multiple)

**Can coexist**:
- `good first issue` + `agent-friendly` (great for AI agents new to codebase)
- `help wanted` + `good first issue` (community contribution welcome)

**Mutually exclusive**:
- `agent-friendly` vs `needs-human` (one or the other, not both)

**When to use**:
- `good first issue`: Simple, well-defined, good for newcomers
- `help wanted`: Community help appreciated
- `agent-friendly`: Suitable for AI agent (clear requirements, testable)
- `needs-human`: Requires human expertise (UX design, security review, etc.)

### Platform Labels (Can Have Multiple)

**Can coexist** (issue affects multiple platforms):
- `platform:windows` + `platform:linux` (bug on both)
- `platform:all` (REPLACES individual platform labels)

**When to use**:
- Add specific platform labels if issue only affects certain OS
- Use `platform:all` if affects all platforms (don't add individual labels)

### Standard Labels (Can Have Multiple)

**Can coexist**:
- `security` + `priority:critical` (security issues are often critical)
- `breaking-change` + `enhancement` (new feature that breaks API)
- `performance` + `bug` (performance regression is a bug)

### Common Label Combinations

**Valid combinations**:
```bash
# Critical security bug in CLI
gh issue edit N --add-label "bug,security,priority:critical,component:cli"

# Small UX enhancement, good for newcomers
gh issue edit N --add-label "enhancement,component:ui/ux,effort:small,good first issue,agent-friendly"

# Performance regression affecting all platforms
gh issue edit N --add-label "bug,regression,performance,priority:high,platform:all"

# Breaking change in validation logic
gh issue edit N --add-label "enhancement,breaking-change,component:validation,needs-human"
```

**Invalid combinations** (don't do this):
```bash
# ❌ Multiple status labels
gh issue edit N --add-label "examining,in-progress"  # WRONG!

# ❌ Multiple priorities
gh issue edit N --add-label "priority:high,priority:critical"  # WRONG!

# ❌ Conflicting types
gh issue edit N --add-label "bug,enhancement"  # WRONG!

# ❌ platform:all + individual platforms
gh issue edit N --add-label "platform:all,platform:windows"  # WRONG!

# ❌ agent-friendly + needs-human
gh issue edit N --add-label "agent-friendly,needs-human"  # WRONG!
```

### Label Cleanup

**When to remove labels**:
- Remove `needs-reproduction` when issue is reproduced
- Remove `good first issue` if issue becomes complex during investigation
- Remove `agent-friendly` if human expertise needed
- Remove specific platform labels if changing to `platform:all`

**Example cleanup**:
```bash
# Issue was thought to be Windows-only, but affects all platforms
gh issue edit 7 --remove-label "platform:windows" --add-label "platform:all"

# Issue was thought to be simple, but root cause is complex
gh issue edit 7 --remove-label "effort:small,good first issue" --add-label "effort:large,needs-human"
```

---

## Step 5: Issue Workflow Commands

### Assign Issue to Yourself

```bash
gh issue edit <issue-number> --add-assignee @me
```

### Add Labels

```bash
# Single label
gh issue edit 7 --add-label "examining"

# Multiple labels
gh issue edit 7 --add-label "bug,component:ui/ux,priority:medium"
```

### Remove Labels

```bash
gh issue edit 7 --remove-label "needs-reproduction"
```

### Comment on Issue

```bash
gh issue comment 7 --body "I can reproduce this issue. Starting work now."
```

### Link to Related Issues

```bash
gh issue comment 7 --body "Related to #5 and #12"
```

### Close Issue

```bash
# Close as completed (fixed)
gh issue close 7 --reason "completed" --comment "Fixed in PR #42"

# Close as not planned (won't fix, duplicate, cannot reproduce)
gh issue close 7 --reason "not planned" --comment "Closing as duplicate of #3"
```

---

## Step 6: Working on the Issue (After Reproduction)

### Before Starting Work:

1. ✅ Issue reproduced successfully
2. ✅ No duplicates found
3. ✅ Issue assigned to you
4. ✅ Labels applied (`examining`, `reproduced`, `verified`)

### Normal Workflow (99% of cases):

```bash
# Add label before starting
gh issue edit <issue-number> --add-label "in-progress"

# Start worktree on dev branch
python ccpm/commands/issue_start.py <issue-number> dev

# Work on fix
cd ~/.cache/svg2fbf-worktrees/issue-<number>
# Make changes, commit, test

# Finish and create PR
python ccpm/commands/issue_finish.py <issue-number>

# Update label
gh issue edit <issue-number> --remove-label "in-progress" --add-label "needs-review"
```

### ⚠️ EXCEPTION: Critical Hotfix Workflow (1% of cases)

**When to use**: Issue labeled `priority:critical` OR `priority:blocker` AND affects production/stable

**Decision checklist** - If YES to any:
- ✅ Security vulnerability affecting stable release?
- ✅ Critical bug causing data loss in production?
- ✅ Crash bug affecting all stable users?
- ✅ Code in dev has diverged (bug no longer exists there)?

**Critical Hotfix Process:**

```bash
# 1. Verify labels
gh issue view <number> --json labels
# Must have: priority:critical OR priority:blocker

# 2. Work directly on master (EXCEPTION)
git checkout master
git pull origin master

# 3. Make the fix (minimal changes only!)
# ... edit files ...

# 4. Commit with explanation
git commit -m "fix(critical): Description #<number>

HOTFIX for production release.
Bypasses normal dev pipeline because:
- [Explain why critical]
- [Explain dev status]

Fixes #<number>"

# 5. Push to master
git push origin master

# 6. Check if dev needs the fix
git checkout dev
grep -r "vulnerable_pattern" src/

# 7a. If dev needs fix → backport
git checkout dev
just backport-hotfix  # Select the commit
just test
git push origin dev

# 7b. If dev doesn't need fix → document
gh issue comment <number> --body "✅ Hotfix applied to master (v0.1.X).
Dev not affected (code was refactored)."

# 8. Release patch version
git checkout master
just release patch

# 9. Close issue
gh issue close <number> --reason "completed"
```

**When NOT to use hotfix workflow:**
- ❌ Non-critical bugs → use dev pipeline
- ❌ New features → ALWAYS dev first
- ❌ Refactoring → ALWAYS dev first
- ❌ Anything that can wait → use normal pipeline

**Remember**: 99% of issues go through dev → testing → review → master!

---

## Step 7: Verify Fix (After PR Merged) - CRITICAL VERIFICATION PROTOCOL

**⚠️ MANDATORY**: Never declare an issue resolved without completing ALL verification steps below.

### Verification Protocol (ALL steps required):

#### 7.1. Pull Latest Changes

```bash
git checkout dev
git pull origin dev
```

#### 7.2. Reproduce Original Issue Again (MANDATORY)

**For Bug Fixes**:
- Use **EXACT** same steps as initial reproduction
- Expected: Issue should NO LONGER occur
- If issue still occurs → Fix failed, reopen issue

**For New Features/Changes**:
- Write a temporary test script to verify the feature works
- Execute the test script
- Verify all expected behaviors work correctly
- Delete the temp test script after verification

Example:
```bash
# Create temp test script
cat > /tmp/test_issue_7.sh <<'EOF'
#!/bin/bash
# Test for issue #7 - duplicate header fix

# Run svg2fbf and capture output
output=$(svg2fbf --input_folder ./test_frames --output_path /tmp/test.fbf.svg 2>&1)

# Count header occurrences (should be exactly 1)
header_count=$(echo "$output" | grep -c "SVG2FBF")

if [ "$header_count" -eq 1 ]; then
    echo "✅ PASS: Header appears exactly once"
    exit 0
else
    echo "❌ FAIL: Header appears $header_count times (expected 1)"
    exit 1
fi
EOF

chmod +x /tmp/test_issue_7.sh
/tmp/test_issue_7.sh

# Clean up
rm /tmp/test_issue_7.sh
```

#### 7.3. Check for Regressions and Test Failures (MANDATORY)

```bash
# Run ALL tests to detect regressions
pytest tests/ -v

# Check for newly failing tests
# If ANY tests fail that previously passed:
# 1. Determine if failure is caused by your changes
# 2. Either:
#    a) Fix the code to not break existing functionality
#    b) Update the tests if expectations legitimately changed
# 3. Never ignore failing tests!
```

**If regressions detected**:
```bash
# Create new commit fixing the regression
git add .
git commit -m "fix: Resolve regression in <component> caused by issue #X fix"

# Push and update PR
git push origin issue-<number>

# DO NOT close the issue until regressions are fixed!
```

#### 7.4. Check for Backward Compatibility / API Breaking Changes (MANDATORY)

**Questions to ask**:
- Did you change any function signatures?
- Did you remove or rename any public APIs?
- Did you change the behavior of existing functions?
- Did you change CLI arguments or flags?
- Did you change configuration file formats?
- Did you change output formats?

**If YES to any above**:

```bash
# 1. Document all breaking changes
cat > /tmp/breaking_changes.md <<'EOF'
## Breaking Changes in Issue #X Fix

### Changed Function Signatures
- `old_function(a, b)` → `new_function(a, b, c)` (added required parameter c)

### Removed APIs
- Removed deprecated `legacy_method()` (use `new_method()` instead)

### Changed Behavior
- `process()` now returns dict instead of list

### Migration Guide
Users need to:
1. Update calls to `old_function()` to include new parameter
2. Replace `legacy_method()` with `new_method()`
3. Update code expecting list from `process()` to handle dict
EOF

# 2. Ask user for explicit approval
gh issue comment <issue-number> --body "$(cat <<'EOF'
## ⚠️ Breaking Changes Detected

This fix introduces backward-incompatible changes:

[Paste breaking_changes.md content here]

**Version Bump Required**: Major version (e.g., 1.x.x → 2.0.0)

**Documentation Updates Required**:
- CHANGELOG.md (breaking changes section)
- README.md (updated API examples)
- Migration guide

**User Approval Required**: @user - Do you approve these breaking changes?
- [ ] Yes, approve and bump major version
- [ ] No, find backward-compatible solution
EOF
)"

# 3. WAIT for user approval - DO NOT PROCEED without it!

# 4. If approved:
#    - Bump major version in pyproject.toml
#    - Update CHANGELOG.md with breaking changes section
#    - Update all documentation
#    - Add migration guide

# 5. If NOT approved:
#    - Revert breaking changes
#    - Find backward-compatible solution
#    - Implement with deprecation warnings instead
```

#### 7.5. Check for Related Issues Also Fixed (MANDATORY)

**Your fix might have solved other issues too!**

```bash
# 1. Search for related open issues
gh issue list --state open --search "in:title,body <keywords from your fix>"

# Example: If you fixed header duplication, search for:
gh issue list --state open --search "in:title,body header duplicate output"
gh issue list --state open --search "in:title,body print twice"
gh issue list --state open --search "in:title,body console output"

# 2. For each potentially related issue:
#    a) Read the issue description
#    b) Reproduce the issue using their steps
#    c) Verify if your fix also resolved it

# 3. If another issue IS also fixed:

# Test it using same verification protocol (steps 7.2, 7.3, 7.4)
# If all checks pass:
gh issue comment <related-issue-number> --body "$(cat <<'EOF'
## ✅ Resolved as Side Effect

This issue appears to be resolved by the fix for #<original-issue>.

**Root Cause**: Same underlying issue (duplicate header printing)

**Verification**:
- Reproduced original issue: ✅
- Verified fix resolves it: ✅
- No regressions detected: ✅
- No breaking changes: ✅

Closing as duplicate/fixed.
EOF
)"

gh issue close <related-issue-number> --reason "completed"
gh issue edit <related-issue-number> --add-label "duplicate,fixed"

# 4. Update original issue with cross-references
gh issue comment <original-issue> --body "Note: This fix also resolved #<related-issue-1>, #<related-issue-2>"
```

#### 7.6. Final Verification Checklist

Before closing ANY issue, verify:

- [ ] Original issue reproduced and verified fixed (or new feature tested with temp script)
- [ ] All tests pass (no regressions)
- [ ] Backward compatibility maintained OR user approved breaking changes
- [ ] Related issues checked and closed if also fixed
- [ ] Documentation updated if needed
- [ ] Migration guide created if breaking changes
- [ ] Version bumped appropriately (major if breaking, minor if feature, patch if bugfix)

#### 7.7. Close Issue (Only After ALL Checks Pass)

```bash
# Only execute this if ALL verification steps passed!

gh issue close <issue-number> --reason "completed" --comment "$(cat <<'EOF'
## ✅ Verified Fixed - Complete Verification Report

### 1. Original Issue Verification
- ✅ Reproduced original issue
- ✅ Verified fix resolves issue
- **Test method**: [Describe exact reproduction steps or temp test script]

### 2. Regression Testing
- ✅ All tests pass
- **Test results**: X/X tests passed, 0 failed

### 3. Backward Compatibility
- ✅ No breaking changes
  OR
- ✅ Breaking changes approved by user (see comment #N)
- ✅ Major version bumped to X.0.0
- ✅ Migration guide created

### 4. Related Issues
- ✅ Checked for related issues
- ✅ Also fixed: #<issue-1>, #<issue-2> (if any)
  OR
- ✅ No related issues found

### 5. Documentation
- ✅ CHANGELOG.md updated
- ✅ README.md updated (if needed)
- ✅ Migration guide added (if breaking changes)

**Fixed in**: PR #<pr-number>
**Available in**: dev branch (will be in next release)

Closing as completed after full verification.
EOF
)"
```

#### 7.8. If Verification Fails

```bash
# If ANY verification step fails:

gh issue reopen <issue-number>
gh issue comment <issue-number> --body "$(cat <<'EOF'
## ⚠️ Verification Failed - Issue Reopened

**Failure details**:
- [ ] Original issue still reproducible
- [ ] Regression detected in: [component]
- [ ] Breaking changes need approval
- [ ] Related issue check incomplete

**Next steps**:
1. [Specific action needed]
2. [Specific action needed]

Reopening for further investigation.
EOF
)"

gh issue edit <issue-number> --add-label "regression" --remove-label "fixed"
```

---

### Summary: Verification is NOT Optional

**NEVER** declare an issue resolved without:
1. ✅ Reproducing the original issue again (or testing new feature with temp script)
2. ✅ Running all tests for regressions
3. ✅ Checking for breaking changes (and getting approval if needed)
4. ✅ Checking if fix also solved related issues

**Agents who skip verification steps will create technical debt and user frustration!**

---

---

## Step 8: Communication Best Practices

### Always Be Specific:

❌ **Bad**: "I can't reproduce this"
✅ **Good**: "I attempted reproduction with `svg2fbf --input_folder ./test --output_path out.svg` using 5 frames, but did not observe the duplicate header. Can you provide your exact command?"

❌ **Bad**: "Fixed"
✅ **Good**: "Fixed by removing the second `print_header()` call on line 342 of svg2fbf.py. Verified with test case."

### Use Clear Formatting:

```markdown
## Reproduction Confirmed ✅

**Steps**:
1. Run `svg2fbf --input_folder frames/ --output_path test.fbf.svg`
2. Observe console output

**Expected**: Single header at start
**Actual**: Header printed twice (line 87 and line 342)

**Root Cause**: Duplicate call to `print_header()` after import phase

**Proposed Fix**: Replace second header with import summary
```

### Update Regularly:

Comment on the issue:
- When you start examining
- When you reproduce (or can't)
- When you start working
- When you create PR
- When you verify fix

---

## Complete Example Workflow

### Issue #7: Duplicate Header Bug

#### Day 1: Triage and Reproduction

```bash
# Step 1: Check for duplicates
gh issue list --search "in:title,body header duplicate" --state all
# Result: No duplicates found

# Step 2: Assign to self and add initial labels
gh issue edit 7 --add-assignee @me

# Step 3: Add type and component labels (can coexist)
gh issue edit 7 --add-label "bug,component:ui/ux"

# Step 4: Start examining (status transition: needs-triage → examining)
gh issue edit 7 --remove-label "needs-triage" --add-label "examining"

# Step 5: Attempt reproduction
cd tests/sessions/test_session_001_2frames/input_frames/
svg2fbf --input_folder . --output_path /tmp/test.fbf.svg
# Observe: Header printed twice ✅ REPRODUCED

# Step 6: Comment with reproduction details
gh issue comment 7 --body "$(cat <<'EOF'
## Reproduction Confirmed ✅

**Steps**:
1. `svg2fbf --input_folder test_frames/ --output_path test.fbf.svg`
2. Observe console output

**Result**: Header printed at line 87 (after arg parsing) and line 342 (after import)

**Root Cause**: Second `print_header()` call should be replaced with import summary

Starting work now.
EOF
)"

# Step 7: Update status (examining → reproduced)
gh issue edit 7 --remove-label "examining" --add-label "reproduced"

# Step 8: Verify root cause and add effort estimate
gh issue edit 7 --remove-label "reproduced" --add-label "verified"
gh issue edit 7 --add-label "effort:small,priority:medium,agent-friendly"

# Step 9: Start work (verified → in-progress)
gh issue edit 7 --remove-label "verified" --add-label "in-progress"
python ccpm/commands/issue_start.py 7 dev
```

#### Day 1: Fix Implementation

```bash
cd ~/.cache/svg2fbf-worktrees/issue-7

# Make changes to src/svg2fbf.py
# - Remove second print_header() call
# - Add print_import_summary() function
# - Test changes

# Commit
git add src/svg2fbf.py
git commit -m "fix(ui): Replace duplicate header with import summary

- Remove second print_header() call on line 342
- Add new print_import_summary() function
- Shows frame count, validation status, and next action
- Improves user experience and information value

Fixes #7"

# Finish and create PR
python ccpm/commands/issue_finish.py 7

# Update status (in-progress → needs-review)
gh issue edit 7 --remove-label "in-progress" --add-label "needs-review"
```

#### Day 2: After PR Merged

```bash
# Pull latest
git checkout dev
git pull origin dev

# Verify fix
svg2fbf --input_folder test_frames/ --output_path test.fbf.svg
# Observe: Only one header, then import summary ✅ FIXED

# Update status (needs-review → fixed)
gh issue edit 7 --remove-label "needs-review" --add-label "fixed"

# Close issue with verification comment
gh issue close 7 --reason "completed" --comment "$(cat <<'EOF'
## ✅ Verified Fixed in dev

**Fix details**:
- Removed duplicate header call
- Added import summary with frame count and status
- Improved UX as requested

**Merged in**: PR #8
**Available in**: dev branch (will be in next alpha release)

Thank you for reporting this issue!
EOF
)"
```

---

## Common Mistakes to Avoid

### ❌ Don't Skip Reproduction

**Wrong**:
```bash
gh issue view 7
# Reads description
python ccpm/commands/issue_start.py 7 dev  # ← WRONG! Skipped reproduction
```

**Right**:
```bash
gh issue view 7
# Reads description
# Attempts reproduction
# Confirms bug exists
# THEN starts work
python ccpm/commands/issue_start.py 7 dev
```

### ❌ Don't Work on Duplicates

**Wrong**:
```bash
gh issue view 42
# Issue looks interesting
python ccpm/commands/issue_start.py 42 dev  # ← WRONG! Didn't check for duplicates
```

**Right**:
```bash
gh issue view 42
gh issue list --search "in:title,body <keywords>" --state all
# Found duplicate: #38
gh issue comment 42 --body "Duplicate of #38"
gh issue close 42 --reason "not planned"
# Work on #38 instead
```

### ❌ Don't Close Without Verification

**Wrong**:
```bash
# PR merged
gh issue close 7 --reason "completed"  # ← WRONG! Didn't verify fix
```

**Right**:
```bash
# PR merged
git pull origin dev

# 1. Reproduce original issue again (MANDATORY)
svg2fbf --input_folder test/ --output_path test.fbf.svg
# Confirm bug is gone OR run temp test script

# 2. Run all tests for regressions (MANDATORY)
pytest tests/ -v
# All must pass!

# 3. Check for breaking changes (MANDATORY)
# Review all function signature changes, API changes, CLI changes
# If breaking changes: Get user approval FIRST!

# 4. Check for related issues (MANDATORY)
gh issue list --state open --search "in:title,body header duplicate"
# Test if those are also fixed

# 5. ONLY THEN close the issue
gh issue close 7 --reason "completed" --comment "Verified fixed (see Step 7 verification protocol)"
```

### ❌ Don't Add Multiple Status Labels

**Wrong**:
```bash
# Adding multiple status labels at once
gh issue edit 7 --add-label "reproduced,verified,in-progress"  # ← WRONG! 3 status labels!
gh issue edit 7 --add-label "examining,in-progress"  # ← WRONG! 2 status labels!
```

**Right**:
```bash
# Transition one status at a time
gh issue edit 7 --remove-label "examining" --add-label "reproduced"
# Later...
gh issue edit 7 --remove-label "reproduced" --add-label "verified"
# Later...
gh issue edit 7 --remove-label "verified" --add-label "in-progress"
```

**Why**: Status labels represent the current state. An issue can only be in ONE state at a time (examining OR reproduced OR verified OR in-progress, not multiple).

---

## Summary: Issue Management Checklist

Before working on ANY issue:

- [ ] **Check for duplicates** (`gh issue list --search`)
- [ ] **Assign to yourself** (`gh issue edit --add-assignee @me`)
- [ ] **Add type/component labels** (bug, enhancement, component:*, etc.)
- [ ] **Start examining**: Remove `needs-triage`, add `examining`
- [ ] **Attempt reproduction** with exact steps
- [ ] **If reproduced**:
  - [ ] Remove `examining`, add `reproduced`
  - [ ] Remove `reproduced`, add `verified`
  - [ ] Add effort/priority labels (`effort:small`, `priority:medium`)
  - [ ] Remove `verified`, add `in-progress`
  - [ ] Start work with `issue_start.py`
- [ ] **If NOT reproduced**:
  - [ ] Remove `examining`, add `needs-reproduction`
  - [ ] Request clarification (attempt 1/3)
  - [ ] If still can't reproduce after attempt 3:
    - [ ] Remove `needs-reproduction`, add `cannot-reproduce`
    - [ ] Close issue
- [ ] **During work**: Status should be `in-progress` (only one status label!)
- [ ] **After PR created**: Remove `in-progress`, add `needs-review`
- [ ] **After PR merged - COMPLETE VERIFICATION PROTOCOL (Step 7)**:
  - [ ] **7.1** Pull latest changes
  - [ ] **7.2** Reproduce original issue again (EXACT same steps OR temp test script for features)
  - [ ] **7.3** Run ALL tests to check for regressions (`pytest tests/ -v`)
  - [ ] **7.4** Check for backward compatibility / API breaking changes
    - [ ] If breaking changes → Ask user approval FIRST
    - [ ] If approved → Bump major version, update docs, create migration guide
  - [ ] **7.5** Check for related issues also fixed
    - [ ] Search for related open issues
    - [ ] Test if they're also resolved
    - [ ] Close them with verification
  - [ ] **7.6** Complete final verification checklist (see Step 7.6)
  - [ ] **7.7** ONLY AFTER ALL CHECKS PASS:
    - [ ] Remove `needs-review`, add `fixed`
    - [ ] Close issue with complete verification report (see Step 7.7)

**Remember**:
- Issue quality > Issue quantity. Better to properly handle 5 issues than rush through 20.
- Only ONE status label at a time (examining, reproduced, verified, in-progress, needs-review, fixed)
- Can have multiple type, component, platform labels simultaneously
- **CRITICAL**: Never close an issue without completing the full Step 7 verification protocol!
- **Breaking changes ALWAYS require user approval** - do not merge without it!
