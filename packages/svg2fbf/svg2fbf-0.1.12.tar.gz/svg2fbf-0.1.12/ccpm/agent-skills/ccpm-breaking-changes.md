# CCPM Breaking Changes Detection and Handling

**Skill**: Identify, document, and get approval for backward-incompatible changes
**Use when**: Making changes that might affect existing user code or workflows

---

## Overview

Breaking changes are modifications that prevent existing user code from working without updates. They require **explicit user approval** with @mention before merging.

**Why This Matters**:
- Protects users from unexpected breakage
- Requires proper version bumping (major version)
- Forces creation of migration guides
- Gives users choice: accept breakage or find alternative solution

**Critical Rule**: NEVER merge breaking changes without user approval!

---

## What Constitutes a Breaking Change?

### 1. Function Signature Changes

❌ **BREAKING**:
```python
# Before
def process_file(filepath):
    pass

# After
def process_file(filepath, encoding):  # Added REQUIRED parameter
    pass
```

✅ **NOT BREAKING**:
```python
# Before
def process_file(filepath):
    pass

# After
def process_file(filepath, encoding='utf-8'):  # Added OPTIONAL parameter with default
    pass
```

---

### 2. Removed or Renamed Public APIs

❌ **BREAKING**:
```python
# Before
class SVGProcessor:
    def convert(self):
        pass

# After
class SVGProcessor:
    # convert() removed!
    def process(self):  # Renamed without keeping old name
        pass
```

✅ **NOT BREAKING** (Deprecation):
```python
# After
class SVGProcessor:
    def process(self):
        pass

    def convert(self):  # Keep old method
        warnings.warn("convert() is deprecated, use process()", DeprecationWarning)
        return self.process()  # Delegate to new method
```

---

### 3. Changed CLI Arguments

❌ **BREAKING**:
```bash
# Before
svg2fbf --input-folder ./frames

# After
svg2fbf --input ./frames  # Changed flag name without alias
```

✅ **NOT BREAKING**:
```bash
# After - both work
svg2fbf --input-folder ./frames  # Old flag still works
svg2fbf --input ./frames         # New flag also works
```

---

### 4. Changed Configuration Formats

❌ **BREAKING**:
```yaml
# Before - config.yaml
input: ./frames
output: ./output

# After - requires different format
settings:
  input: ./frames  # Nested under "settings"
  output: ./output
```

✅ **NOT BREAKING**:
```python
# Support BOTH old and new formats
if 'settings' in config:
    input_dir = config['settings']['input']  # New format
else:
    input_dir = config['input']  # Old format still works
```

---

### 5. Changed Output Formats

❌ **BREAKING**:
```python
# Before - returns list
def get_frames():
    return ['frame1.svg', 'frame2.svg']

# After - returns dict
def get_frames():
    return {'frames': ['frame1.svg', 'frame2.svg']}  # Different structure!
```

---

### 6. Changed Behavior

❌ **BREAKING**:
```python
# Before - returns None on error
def load_svg(path):
    try:
        return parse(path)
    except:
        return None

# After - raises exception on error
def load_svg(path):
    return parse(path)  # Now raises if invalid!
```

---

### 7. Removed Features

❌ **BREAKING**:
```python
# Before
svg2fbf --legacy-mode  # Flag existed

# After
# --legacy-mode removed entirely
```

---

## Detection Checklist

Before declaring issue resolved, check:

- [ ] Did I change function signatures (add/remove/reorder parameters)?
- [ ] Did I remove any public functions, methods, or classes?
- [ ] Did I rename any public APIs?
- [ ] Did I change CLI flags, arguments, or their behavior?
- [ ] Did I change configuration file format or keys?
- [ ] Did I change return types or output formats?
- [ ] Did I change error handling (returns → exceptions or vice versa)?
- [ ] Did I remove deprecated features?
- [ ] Did I change default behavior?
- [ ] Did I change data formats (JSON structure, CSV columns, etc.)?

**If YES to ANY → Breaking change detected!**

---

## Breaking Change Protocol

### Step 1: Document Breaking Changes

```bash
cat > /tmp/breaking_changes_issue_<N>.md <<'EOF'
## Breaking Changes in Issue #<N> Fix

### Summary
[One-sentence summary of what breaks]

### Changed Function Signatures
**Before**:
```python
def old_function(a, b):
    pass
```

**After**:
```python
def new_function(a, b, c):  # Added required parameter 'c'
    pass
```

**Impact**: All calls to `old_function()` will fail with TypeError

---

### Removed APIs
- Removed `legacy_method()` (deprecated since v1.2)
  - Use `new_method()` instead

**Impact**: Code calling `legacy_method()` will fail with AttributeError

---

### Changed CLI Arguments
**Before**: `--old-flag value`
**After**: `--new-flag value`

**Impact**: Scripts using `--old-flag` will fail with "unrecognized argument"

---

### Changed Output Format
**Before**: Returns list of strings
**After**: Returns dict with 'frames' key

**Impact**: Code expecting list will fail when trying to iterate dict

---

### Migration Guide

Users must update their code:

**1. Update function calls**:
```python
# Before
result = old_function(x, y)

# After
result = new_function(x, y, default_c_value)
```

**2. Replace removed APIs**:
```python
# Before
obj.legacy_method()

# After
obj.new_method()
```

**3. Update CLI scripts**:
```bash
# Before
svg2fbf --old-flag value

# After
svg2fbf --new-flag value
```

**4. Update code expecting old output**:
```python
# Before
for frame in get_frames():
    print(frame)

# After
for frame in get_frames()['frames']:
    print(frame)
```

---

### Estimated Migration Time
- Simple projects: 10-30 minutes
- Medium projects: 1-2 hours
- Large projects: 1 day

### Alternatives to Breaking Changes
[List backward-compatible alternatives if any exist]
EOF
```

---

### Step 2: Ask User Approval (MANDATORY)

```bash
gh issue comment <issue-number> --body "$(cat <<'EOF'
## ⚠️ Breaking Changes Detected - User Approval Required

This fix introduces **backward-incompatible changes** that will break existing user code.

[Paste breaking_changes_issue_<N>.md content here]

---

### Version Impact
**Current version**: 1.5.2
**Required new version**: 2.0.0 (major bump)

### Required Actions if Approved
- [ ] Bump major version in pyproject.toml (1.x.x → 2.0.0)
- [ ] Update CHANGELOG.md with breaking changes section
- [ ] Update README.md with new API examples
- [ ] Create MIGRATION_v2.md guide
- [ ] Update all documentation
- [ ] Add deprecation warnings in v1.x if possible

### Required Actions if Rejected
- [ ] Revert breaking changes
- [ ] Implement backward-compatible solution
- [ ] Add deprecation warnings for old API
- [ ] Keep old API working while adding new API

---

**⚠️ APPROVAL REQUIRED**: @<username>

Please choose one:
- [ ] **Yes, approve breaking changes** - Bump to v2.0.0 and create migration guide
- [ ] **No, find backward-compatible solution** - Revert and implement with deprecation

**I will wait for your response before proceeding.**
EOF
)"
```

**CRITICAL**: Include @mention of user to ensure they see this!

---

### Step 3: Wait for Response

```bash
# DO NOT:
# - Close the issue
# - Merge to higher branches
# - Create new PRs
# - Continue with other work on this issue

# DO:
# - Wait for user response
# - Monitor for comments
# - If no response in 24h, ping again:

gh issue comment <issue-number> --body "$(cat <<'EOF'
@<username> - Friendly reminder: This issue requires your approval decision for breaking changes. Please see comment above.

Without approval, I cannot proceed with closing this issue.
EOF
)"
```

---

### Step 4a: If User Approves

```bash
# 1. Update version (example for Python project)
# Edit pyproject.toml:
# version = "1.5.2" → version = "2.0.0"

# 2. Create migration guide
cat > MIGRATION_v2.md <<'EOF'
# Migration Guide: v1.x to v2.0

[Content from breaking_changes.md]
EOF

# 3. Update CHANGELOG.md
cat >> CHANGELOG.md <<'EOF'
## [2.0.0] - YYYY-MM-DD

### Breaking Changes
[List all breaking changes]

### Migration Guide
See MIGRATION_v2.md for complete migration instructions.
EOF

# 4. Update documentation
# Update README.md with new API examples
# Update any affected documentation

# 5. Commit
git add pyproject.toml MIGRATION_v2.md CHANGELOG.md README.md docs/
git commit -m "chore: Bump to v2.0.0 with breaking changes from #<issue>

BREAKING CHANGES:
- Changed function signature: old_function(a,b) → new_function(a,b,c)
- Removed legacy_method() (use new_method() instead)
- Changed CLI flag: --old-flag → --new-flag

See MIGRATION_v2.md for migration guide.

Approved by @<username> in issue #<issue>."

git push origin dev

# 6. Update issue
gh issue comment <issue-number> --body "$(cat <<'EOF'
## ✅ Breaking Changes Approved

Thank you for approving! I have:
- ✅ Bumped version to 2.0.0
- ✅ Created MIGRATION_v2.md
- ✅ Updated CHANGELOG.md
- ✅ Updated documentation

Proceeding with verification protocol.
EOF
)"

# 7. Proceed with Step 7 verification protocol
```

---

### Step 4b: If User Rejects

```bash
# 1. Revert breaking changes
git revert <breaking-commit-hash>
git push origin dev

# 2. Implement backward-compatible solution

# Example: Keep old API, add new API
# Before (breaking):
def new_function(a, b, c):  # Removed old_function
    pass

# After (non-breaking):
def new_function(a, b, c):
    pass

def old_function(a, b):  # Keep old function
    warnings.warn(
        "old_function() is deprecated and will be removed in v3.0. Use new_function(a, b, c) instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function(a, b, default_c_value)

# 3. Update issue
gh issue comment <issue-number> --body "$(cat <<'EOF'
## ✅ Backward-Compatible Solution Implemented

Breaking changes reverted. New approach:
- ✅ Old API still works (with deprecation warning)
- ✅ New API available for users who want to adopt it
- ✅ Deprecation will be removed in v3.0 (future major version)

This is now a minor version bump (v1.6.0) instead of major.
EOF
)"

# 4. Update version (minor bump instead)
# version = "1.5.2" → version = "1.6.0"

# 5. Proceed with verification
```

---

## Version Bumping Rules

Follow Semantic Versioning (semver.org):

**Major version bump (X.0.0)**: Breaking changes
- Example: 1.5.2 → 2.0.0

**Minor version bump (x.Y.0)**: New features (backward compatible)
- Example: 1.5.2 → 1.6.0

**Patch version bump (x.y.Z)**: Bug fixes (backward compatible)
- Example: 1.5.2 → 1.5.3

---

## Deprecation Strategy (Alternative to Breaking)

Instead of breaking immediately, deprecate:

```python
import warnings

def old_method(self):
    warnings.warn(
        "old_method() is deprecated and will be removed in v3.0. "
        "Use new_method() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()

def new_method(self):
    # New implementation
    pass
```

**Timeline**:
- v1.6: Add new_method(), deprecate old_method() (both work)
- v2.0: Keep both methods, louder warnings
- v3.0: Remove old_method() (breaking change but users had 2 major versions to migrate)

---

## Critical Rules

### ALWAYS

- ✅ Check for breaking changes in Step 7.4 of verification protocol
- ✅ Document ALL breaking changes completely
- ✅ Ask user approval with @mention
- ✅ WAIT for response before proceeding
- ✅ Bump major version if approved
- ✅ Create migration guide
- ✅ Update CHANGELOG.md

### NEVER

- ❌ Merge breaking changes without user approval
- ❌ Assume "small" breaking changes don't need approval
- ❌ Skip migration guide creation
- ❌ Forget to bump major version
- ❌ Close issue before getting approval

---

## When to Use This Skill

**Use this skill when**:
- Step 7.4 of verification protocol detects breaking changes
- Implementing new features that might break existing code
- Removing deprecated features
- Unsure if a change is breaking

**After using this skill**:
- Use `ccpm-verification-protocol` to complete verification
- Use `ccpm-label-management` to add `breaking-change` label if approved

---

## Quick Troubleshooting

**Issue**: "Not sure if this is breaking"
→ Check detection checklist above, when in doubt ASK USER

**Issue**: "User wants breaking change but later than v2.0"
→ Use deprecation strategy, plan breaking change for future major version

**Issue**: "Breaking change needed for security fix"
→ Still needs approval, but explain security urgency in request

---

**For complete verification protocol including breaking change detection, see**: `ccpm/skills/issue-management.md` (Step 7.4)
