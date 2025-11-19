# Release Process for svg2fbf

## Critical Rule for Agents

❌ **AGENTS MUST NEVER TRIGGER RELEASES**

You should:
- ✅ Understand the release process (read this document)
- ✅ Prepare code for releases (tests, docs, commits)
- ✅ Observe releases when they happen (learn from them)
- ❌ NEVER run `just publish`
- ❌ NEVER manually edit version numbers
- ❌ NEVER trigger PyPI uploads
- ❌ NEVER edit CHANGELOG.md

**Why**: Releases are permanent, public, and irreversible. Only humans make release decisions.

---

## Release Overview

The svg2fbf project uses a **multi-channel release system** where each branch publishes to a different release channel:

```
Branch    → Channel → Audience           → Installation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
dev       → alpha   → Developers         → pip install svg2fbf --pre
testing   → beta    → QA Testers         → pip install svg2fbf --pre
review    → rc      → Release Candidates → pip install svg2fbf --pre
master    → stable  → Production Users   → pip install svg2fbf
```

**Key Insight**: Each branch can publish independently. A bug fix on testing can be released as a new beta without affecting stable releases.

---

## Release Command: `just publish`

**Human executes** from any branch (dev, testing, review, master):

```bash
just publish
```

This triggers `scripts/release.sh`, which performs:

1. **Safety Checks** (Lines 484-499 of release.sh)
   - Clean working tree (no uncommitted changes)
   - Branch in sync with origin
   - Valid branch (dev/testing/review/master only)
   - PyPI token configured (for stable channel)

2. **Version Detection** (Lines 596-625)
   - Reads current version from `pyproject.toml`
   - Determines channel from branch:
     - dev → alpha (e.g., 0.1.8a0)
     - testing → beta (e.g., 0.1.8b0)
     - review → rc (e.g., 0.1.8rc0)
     - master → stable (e.g., 0.1.8)

3. **Changelog Generation** (Lines 758-821)
   - Uses `git-cliff` to generate release notes
   - Reads conventional commits since last release
   - Updates CHANGELOG.md automatically
   - Creates .release-notes-<version>.md temporarily

4. **Pre-Release Safety Check** (Lines 823-831) ⚠️ **CRITICAL**
   - For stable channel (master) ONLY:
   - Verifies version has NO alpha/beta/rc markers
   - **PREVENTS ACCIDENTAL PRE-RELEASE TO PyPI**
   - Example: Blocks `0.1.8rc0` from reaching production

5. **Build Process** (Lines 850-880)
   - Runs `uv build` to create wheel and sdist
   - Generates .whl and .tar.gz in dist/
   - Validates package integrity

6. **Git Tagging** (Lines 882-895)
   - Creates annotated tag: `v0.1.8` or `v0.1.8rc0`
   - Pushes tag to origin
   - Tag triggers GitHub Release creation (via Actions)

7. **Publication** (Lines 897-912)
   - For stable (master): Publishes to PyPI
   - For pre-release (dev/testing/review): GitHub Releases only
   - Uses `uv publish --token <PYPI_TOKEN>`

8. **Cleanup** (Lines 918-945)
   - Deletes temporary .release-notes-*.md files
   - Preserves dist/ directory (contains wheels)
   - Restores original branch if changed during process

---

## What Happens During a Release (Step-by-Step)

### Example: Releasing v0.1.8 (Stable) from master

```bash
$ just publish

🔍 Detecting version from pyproject.toml...
   Current version: 0.1.8

🔍 Determining release channel...
   Branch: master → Channel: stable

✅ Safety checks passed:
   - Working tree clean
   - Branch in sync with origin/master
   - PyPI token configured

📝 Generating changelog with git-cliff...
   Reading commits since v0.1.7...
   Found 15 commits:
     - 8 features
     - 5 bug fixes
     - 2 documentation updates
   Updated CHANGELOG.md

✅ Pre-release safety check: No alpha/beta/rc markers found

🔨 Building package...
   Running: uv build
   Created: dist/svg2fbf-0.1.8-py3-none-any.whl
   Created: dist/svg2fbf-0.1.8.tar.gz

🏷️  Tagging release...
   Created: v0.1.8
   Pushed to origin

📦 Publishing to PyPI...
   Uploading svg2fbf-0.1.8-py3-none-any.whl
   Uploading svg2fbf-0.1.8.tar.gz
   ✅ Published successfully

🧹 Cleaning up...
   Deleted: .release-notes-0.1.8.md

🎉 Release complete: v0.1.8 (stable)
   PyPI: https://pypi.org/project/svg2fbf/0.1.8/
   GitHub: https://github.com/user/svg2fbf/releases/tag/v0.1.8
```

---

## Changelog Generation (git-cliff)

### How It Works

The `git-cliff` tool reads conventional commits and generates structured release notes:

**Input** (Git commits since last release):
```
feat(svg2fbf): Add support for nested <g> elements
fix(validator): Correct viewBox validation regex
docs(README): Update installation instructions
chore(deps): Bump ruff to 0.8.5
```

**Output** (CHANGELOG.md):
```markdown
## [0.1.8] - 2025-01-14

### Features
- Add support for nested <g> elements

### Bug Fixes
- Correct viewBox validation regex

### Documentation
- Update installation instructions

### Miscellaneous
- Bump ruff to 0.8.5
```

### Agent Responsibilities

✅ **Write good conventional commits**:
```bash
# Good examples
feat(core): Add frame interpolation algorithm
fix(cli): Handle missing --input_folder argument
docs(CONTRIBUTING): Add section on pre-commit hooks
test(svg2fbf): Add test for empty viewBox attribute

# Bad examples (avoid)
Update stuff
Fix bug
Changes
WIP
```

✅ **Commit message format**:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, test, chore, refactor, perf, style, build, ci

**Scopes**: svg2fbf, validator, cli, core, docs, tests, deps

---

## Version Bumping

### Semantic Versioning

svg2fbf follows **semver**: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.2.0): New features, backward-compatible
- **PATCH** (0.1.9): Bug fixes, backward-compatible

**Pre-release markers**:
- `a0` = alpha (dev)
- `b0` = beta (testing)
- `rc0` = release candidate (review)

**Examples**:
- `0.1.8a0` → Alpha release from dev
- `0.1.8b0` → Beta release from testing
- `0.1.8rc0` → Release candidate from review
- `0.1.8` → Stable release from master

### How Versions Change

Versions are **manually specified** in `pyproject.toml`:

```toml
[project]
name = "svg2fbf"
version = "0.1.8"  # Human edits this
```

**Agent Role**:
- ❌ DO NOT edit version in pyproject.toml
- ✅ Suggest appropriate version bump (patch/minor/major)
- ✅ Understand version semantics
- ✅ Check if changes warrant version bump

**Human decides**:
- When to bump version
- Which part to bump (major/minor/patch)
- Edits `pyproject.toml` directly

---

## Pre-Release Safety Mechanism

### The Critical Safety Check (Lines 823-831 of release.sh)

```bash
# CRITICAL SAFETY CHECK: Verify version string contains NO pre-release markers
if [[ "$new_version" == *a[0-9]* || "$new_version" == *b[0-9]* || "$new_version" == *rc[0-9]* ]]; then
    echo "❌ SAFETY ABORT: Version ${new_version} contains pre-release marker!" >&2
    echo "❌ Pre-release versions (alpha/beta/rc) must NEVER be published to PyPI!" >&2
    exit 1
fi
```

**What this prevents**:
- Accidentally publishing `0.1.8rc0` to PyPI production
- Users installing pre-release as stable
- Confusion about which version is production-ready

**How it works**:
- Only runs when publishing from **master** branch (stable channel)
- Checks version string for `a`, `b`, or `rc` markers
- **Aborts immediately** if markers found
- Forces human to fix version before retrying

**Example failure**:
```bash
$ git checkout master
$ # Forgot to remove 'rc0' from pyproject.toml
$ just publish

❌ SAFETY ABORT: Version 0.1.8rc0 contains pre-release marker!
❌ Pre-release versions (alpha/beta/rc) must NEVER be published to PyPI!
```

---

## Multi-Channel Publishing

### Channel-Specific Behavior

#### Alpha (dev branch)
```bash
$ git checkout dev
$ just publish

Version: 0.1.9a0
Channel: alpha
Target: GitHub Releases only (no PyPI)
Audience: Developers testing bleeding-edge features
```

#### Beta (testing branch)
```bash
$ git checkout testing
$ just publish

Version: 0.1.9b0
Channel: beta
Target: GitHub Releases only (no PyPI)
Audience: QA testers, early adopters
```

#### RC (review branch)
```bash
$ git checkout review
$ just publish

Version: 0.1.9rc0
Channel: rc
Target: GitHub Releases only (no PyPI)
Audience: Release validators, final testing
```

#### Stable (master branch)
```bash
$ git checkout master
$ just publish

Version: 0.1.9
Channel: stable
Target: PyPI + GitHub Releases
Audience: Production users
```

---

## Release Artifacts

Each release creates:

1. **Git Tag**: `v0.1.8` or `v0.1.8rc0`
   - Permanent marker in git history
   - Triggers GitHub Actions
   - Allows version checkout: `git checkout v0.1.8`

2. **GitHub Release**: https://github.com/user/svg2fbf/releases/tag/v0.1.8
   - Contains release notes from CHANGELOG.md
   - Includes .whl and .tar.gz as downloadable assets
   - Visible to all users on GitHub

3. **PyPI Package** (stable only): https://pypi.org/project/svg2fbf/0.1.8/
   - Installable via `pip install svg2fbf`
   - **Permanent and irreversible** (cannot delete from PyPI)
   - Indexed by search engines

4. **Wheel File**: `dist/svg2fbf-0.1.8-py3-none-any.whl`
   - Binary distribution format
   - Fast installation
   - Platform-independent

5. **Source Distribution**: `dist/svg2fbf-0.1.8.tar.gz`
   - Source code archive
   - Includes all files from `pyproject.toml` manifest
   - Can be built locally

---

## Agent Observation During Releases

When a human runs `just publish`, agents should:

### ✅ DO Observe:
1. **Watch the build process**
   - Note any warnings from `uv build`
   - Learn package structure

2. **Review the changelog**
   - See how your commits appear in CHANGELOG.md
   - Learn conventional commit best practices

3. **Check release artifacts**
   - Verify files in dist/ directory
   - Understand wheel vs sdist

4. **Monitor PyPI** (for stable releases)
   - Visit PyPI URL after publication
   - Confirm package metadata is correct

5. **Test installation**
   - Install published version: `pip install svg2fbf==0.1.8`
   - Verify it works as expected

### ❌ DO NOT:
1. Interrupt the release process
2. Modify files during release
3. Push commits during release
4. Suggest emergency fixes mid-release
5. Trigger another release immediately

---

## Release Checklist (For Human Reference)

Before running `just publish`:

```bash
# 1. Verify branch
git branch --show-current  # Should be dev/testing/review/master

# 2. Verify version in pyproject.toml
cat pyproject.toml | grep version

# 3. Verify all commits follow conventional format
git log --oneline -10

# 4. Verify working tree is clean
git status

# 5. Verify in sync with origin
git fetch origin
git status  # Should not show "behind"

# 6. Run tests
pytest tests/

# 7. For stable (master) only: Verify no pre-release markers
# Version should be: 0.1.8 (not 0.1.8rc0)

# 8. Execute release
just publish
```

---

## Common Release Scenarios

### Scenario 1: First Alpha Release of v0.2.0

```bash
# On dev branch
# pyproject.toml: version = "0.2.0a0"

$ just publish

Result:
- Tag: v0.2.0a0
- GitHub Release: svg2fbf-0.2.0a0
- PyPI: Not published (alpha channel)
- dist/: svg2fbf-0.2.0a0-py3-none-any.whl
```

### Scenario 2: Beta Release After QA

```bash
# Promoted dev → testing
# pyproject.toml: version = "0.2.0b0"

$ git checkout testing
$ just publish

Result:
- Tag: v0.2.0b0
- GitHub Release: svg2fbf-0.2.0b0
- PyPI: Not published (beta channel)
- dist/: svg2fbf-0.2.0b0-py3-none-any.whl
```

### Scenario 3: Release Candidate

```bash
# Promoted testing → review
# pyproject.toml: version = "0.2.0rc0"

$ git checkout review
$ just publish

Result:
- Tag: v0.2.0rc0
- GitHub Release: svg2fbf-0.2.0rc0
- PyPI: Not published (rc channel)
- dist/: svg2fbf-0.2.0rc0-py3-none-any.whl
```

### Scenario 4: Stable Production Release

```bash
# Promoted review → master
# pyproject.toml: version = "0.2.0" (NO pre-release marker!)

$ git checkout master
$ just publish

Result:
- Tag: v0.2.0
- GitHub Release: svg2fbf-0.2.0
- PyPI: https://pypi.org/project/svg2fbf/0.2.0/
- dist/: svg2fbf-0.2.0-py3-none-any.whl
- **PERMANENT ON PyPI** (cannot be deleted)
```

### Scenario 5: Hotfix Release v0.1.9

```bash
# Critical bug found in v0.1.8
# Created hotfix/v0.1.9-security from master
# Fixed bug, merged to master
# pyproject.toml: version = "0.1.9"

$ git checkout master
$ just publish

Result:
- Tag: v0.1.9
- Changelog includes only hotfix commits
- Published to PyPI immediately
- Users can upgrade: pip install --upgrade svg2fbf
```

---

## Rollback and Recovery

### If Release Fails Mid-Process

**git-cliff fails**:
```bash
Error: Failed to parse git log
```
→ Fix: Check conventional commit format, re-run

**uv build fails**:
```bash
Error: Missing dependency in pyproject.toml
```
→ Fix: Add dependency, commit, re-run

**PyPI upload fails**:
```bash
Error: Authentication failed
```
→ Fix: Check PYPI_API_TOKEN, re-run

**Safety check fails**:
```bash
Error: Version 0.1.8rc0 contains pre-release marker
```
→ Fix: Edit pyproject.toml, remove marker, re-run

### If Bad Release Published to PyPI

❌ **CANNOT DELETE FROM PyPI** - Releases are permanent

✅ **Can do**:
1. Publish fixed version immediately (e.g., v0.1.9)
2. Yank broken version (marks as not installable by default)
3. Update release notes warning about issue

**Human executes**:
```bash
# Yank broken version
pip install twine
twine yank svg2fbf 0.1.8

# Users can still install if they explicitly request it:
pip install svg2fbf==0.1.8  # Still works

# But default install gets latest working version:
pip install svg2fbf  # Gets 0.1.9 instead
```

---

## Key Principles

1. **Only Humans Trigger Releases**: Agents prepare, humans execute
2. **Releases Are Permanent**: Especially on PyPI, cannot delete
3. **Multi-Channel System**: Each branch publishes to different audience
4. **Safety First**: Pre-release markers blocked from stable channel
5. **Conventional Commits**: Drive automatic changelog generation
6. **Version Semantics**: Follow semver strictly

## Summary for Agents

**Your Role**:
- ✅ Write conventional commits
- ✅ Prepare code for releases (tests, docs, quality)
- ✅ Suggest version bumps when appropriate
- ✅ Observe and learn from releases

**Not Your Role**:
- ❌ Running `just publish`
- ❌ Editing pyproject.toml version
- ❌ Editing CHANGELOG.md
- ❌ Uploading to PyPI

**Remember**: Releases are permanent and public. Let humans make those decisions.
