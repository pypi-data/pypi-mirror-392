# CCPM - Controlled Concurrent Project Management for AI Agents

**Version:** 2.0.0 (Phase 1 - Cross-Platform Python Edition)
**Status:** Development (Local Only)
**License:** MIT (planned)

---

## What is CCPM?

CCPM is a **cross-platform plugin** for AI agents that provides safe, isolated issue management on GitHub repositories using git worktrees and comprehensive verification protocols.

### Key Features

✅ **Cross-Platform** - Python 3.6+ (Windows, macOS, Linux) - NO Bash required
✅ **Project-Agnostic** - Auto-detects project from git remote, works with ANY repository
✅ **Branch-Flexible** - Adapts to any branch workflow (single branch to hundreds of branches)
✅ **Issue Isolation** - Each issue gets its own worktree with mutex locks
✅ **46 GitHub Labels** - Complete taxonomy with state machine workflows
✅ **Critical Verification Protocol** - 8-step mandatory verification before closing issues
✅ **Zero Dependencies** - Uses only Python standard library
✅ **Complete Audit Trail** - JSON logs of all agent actions

### Branch Workflow Adaptability

**IMPORTANT**: The CCPM plugin adapts to YOUR project's branch workflow:

- The documentation examples use a **5-branch workflow** (dev → testing → review → master → main)
- This is **specific to the svg2fbf project**, NOT a CCPM requirement
- **Your project may use**:
  - Single branch (main only)
  - Simple workflow (dev → main)
  - Feature branches (feature/* → main)
  - Complex workflows (multiple environments, hundreds of branches)
  - **ANY other branch configuration**

**Agents must**:
- ✅ Read the project's `DEVELOPMENT.md` or `CONTRIBUTING.md` to understand the branch workflow
- ✅ Adapt CCPM workflows to match the project's specific branch structure
- ✅ Use the branch names and promotion commands defined by the project
- ✅ Follow the project's hotfix/emergency procedures if documented

**CCPM provides the framework** (isolated worktrees, verification protocol, label taxonomy)
**Your project defines the workflow** (which branches, how code flows, promotion rules)

---

## Installation

```bash
# Clone or copy the ccpm/ directory to your project
cp -r ccpm/ /path/to/your/project/

# The plugin auto-configures based on git remote URL
# No configuration needed!
```

---

## Quick Start for Agents

### 1. Set Up Labels (First Time Only)

```bash
python ccpm/commands/setup_labels.py
```

This creates 46 standard GitHub labels for issue management.

### 2. Read the Skills

**MANDATORY reading before working on ANY issue:**

- `ccpm/skills/issue-management.md` (1,124 lines) - **READ THIS FIRST**
  - Complete issue lifecycle (8 steps)
  - Label taxonomy and usage rules
  - **CRITICAL: Step 7 Verification Protocol (280 lines)**
- `ccpm/skills/5-branch-workflow.md` - Branch hierarchy and permissions
- `ccpm/skills/promotion-rules.md` - How code moves through branches
- `ccpm/skills/recovery-procedures.md` - Error recovery procedures

### 3. Work on an Issue

```bash
# Start work (creates isolated worktree)
python ccpm/commands/issue_start.py 123 dev

# Work in isolated worktree
cd ~/.cache/ccpm-worktrees/{owner}-{project}/issue-123
# Make changes, commit, test

# Finish and create PR (runs quality checks)
python ccpm/commands/issue_finish.py 123

# Check status of all active issues
python ccpm/commands/issue_status.py
```

### 4. After PR is Merged - CRITICAL VERIFICATION PROTOCOL

**⚠️ MANDATORY** - Never close an issue without completing ALL 8 steps:

```bash
# Step 7.1 - Pull latest changes
git checkout dev && git pull origin dev

# Step 7.2 - Reproduce original issue again
# For bugs: Use EXACT same reproduction steps
# For features: Create temp test script, execute, verify, delete

# Step 7.3 - Run ALL tests for regressions
pytest tests/ -v
# ALL tests MUST pass!

# Step 7.4 - Check for breaking changes
# Review: function signatures, APIs, CLI args, configs, output formats
# If breaking changes → Ask user approval with @mention
# If approved → Bump major version, update docs, create migration guide

# Step 7.5 - Check if fix also solved related issues
gh issue list --state open --search "in:title,body <keywords>"
# Test each related issue with full verification protocol

# Step 7.6 - Complete final checklist
# See ccpm/skills/issue-management.md Step 7.6

# Step 7.7 - Close issue with complete verification report
gh issue close <number> --reason "completed" --comment "$(cat <<'EOF'
## ✅ Verified Fixed - Complete Verification Report
[See Step 7.7 template in issue-management.md]
EOF
)"

# Step 7.8 - If ANY verification fails, reopen immediately
```

---

## Critical Rules for Agents

### ALWAYS

- ✅ Read `ccpm/skills/issue-management.md` before working on issues
- ✅ Check for duplicates before working on any issue
- ✅ Reproduce issues before starting work (3-attempt policy)
- ✅ Use isolated worktrees for each issue
- ✅ Complete the 8-step verification protocol before closing
- ✅ Reproduce original issue again to verify fix
- ✅ Run ALL tests to detect regressions
- ✅ Check for backward compatibility breaking changes
- ✅ Ask user approval for ANY breaking changes (with @mention)
- ✅ Check if fix also solved related issues
- ✅ Use correct label workflow (state machine transitions)

### NEVER

- ❌ Close issue without completing Step 7 verification protocol
- ❌ Ignore failing tests or regressions
- ❌ Merge breaking changes without user approval
- ❌ Skip related issue checks
- ❌ Work on multiple issues in same worktree
- ❌ Modify protected files (see `ccpm/rules/protected-files.txt`)
- ❌ Merge your own PRs
- ❌ Push to master/main branches
- ❌ Skip reproduction step

---

## Available Commands

### Issue Management

```bash
# Set up GitHub labels (run once per repository)
python ccpm/commands/setup_labels.py [--force]

# Start work on issue in isolated worktree
python ccpm/commands/issue_start.py <issue-number> [target-branch]

# Finish work, create PR (runs quality checks)
python ccpm/commands/issue_finish.py <issue-number> [--keep-worktree]

# Abort work, cleanup worktree
python ccpm/commands/issue_abort.py <issue-number> [--force]

# Show status of all active worktrees
python ccpm/commands/issue_status.py [--verbose]
```

### Hooks (Automatic)

```bash
# Pre-flight checks (run by issue_start.py)
python ccpm/hooks/pre_flight_check.py <issue-number> <target-branch>

# Pre-commit safety (blocks protected file modifications)
python ccpm/hooks/pre_commit_safety.py

# Post-flight checks (run by issue_finish.py)
python ccpm/hooks/post_flight_check.py [--fix]

# Audit logging (JSON logs of all actions)
python ccpm/hooks/audit_log.py <action> [metadata]
```

---

## Label System

### 46 Labels Across 8 Categories

**Status** (10) - Lifecycle states (mutually exclusive):
- `needs-triage` → `examining` → `reproduced` → `verified` → `in-progress` → `needs-review` → `fixed`
- Alternative paths: `needs-reproduction`, `cannot-reproduce`, `wontfix`

**Type** (7) - Issue type:
- `bug`, `enhancement`, `documentation`, `question`, `duplicate`, `invalid`, `regression`

**Priority** (4) - Urgency (mutually exclusive):
- `priority:critical`, `priority:high`, `priority:medium`, `priority:low`

**Component** (8) - Affected area (can have multiple):
- `component:cli`, `component:core`, `component:api`, `component:validation`, `component:ui/ux`, `component:tests`, `component:ci/cd`, `component:docs`

**Effort** (5) - Time estimate (mutually exclusive):
- `effort:trivial`, `effort:small`, `effort:medium`, `effort:large`, `effort:epic`

**Contribution** (4) - Contributor guidance:
- `good first issue`, `help wanted`, `agent-friendly`, `needs-human`

**Platform** (4) - OS affected:
- `platform:windows`, `platform:macos`, `platform:linux`, `platform:all`

**Standard** (4) - Special categories:
- `dependencies`, `security`, `performance`, `breaking-change`

See `ccpm/skills/issue-management.md` for complete label usage rules.

---

## Architecture

```
ccpm/
├── README.md                    # This file
├── plugin.yaml                  # Plugin metadata and configuration
├── requirements.txt             # Python dependencies (none required!)
├── __init__.py                  # Package initialization
│
├── lib/                         # Core library
│   ├── __init__.py
│   ├── project_config.py        # Auto-detect project name/owner
│   └── project-config.sh        # Legacy Bash version
│
├── commands/                    # Agent workflow commands
│   ├── __init__.py
│   ├── setup_labels.py          # Set up 46 GitHub labels
│   ├── issue_start.py           # Start work on issue
│   ├── issue_finish.py          # Complete work, create PR
│   ├── issue_abort.py           # Abort work, cleanup
│   └── issue_status.py          # Show status of all worktrees
│
├── hooks/                       # Safety and validation hooks
│   ├── __init__.py
│   ├── pre_flight_check.py      # Pre-work validation
│   ├── pre_commit_safety.py     # Block protected file modifications
│   ├── post_flight_check.py     # Quality checks before PR
│   └── audit_log.py             # JSON audit logging
│
├── skills/                      # Agent education documents
│   ├── issue-management.md      # COMPLETE GUIDE (1,124 lines)
│   ├── 5-branch-workflow.md     # Branch hierarchy
│   ├── promotion-rules.md       # Code promotion process
│   ├── release-process.md       # Release system (observe only)
│   └── recovery-procedures.md   # Error recovery
│
└── rules/
    └── protected-files.txt      # Files agents cannot modify
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Read issue-management.md (MANDATORY)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Check for duplicates (gh issue list --search)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Reproduce issue (3-attempt policy)                           │
│    - Can't reproduce → needs-reproduction → close after 3 tries │
│    - Can reproduce → reproduced → verified                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Start work (issue_start.py)                                  │
│    - Pre-flight checks                                          │
│    - Create isolated worktree                                   │
│    - Create mutex lock                                          │
│    - Install pre-commit hook                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Make changes in worktree                                     │
│    - Commit often                                               │
│    - Pre-commit hook blocks protected files                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Finish work (issue_finish.py)                                │
│    - Post-flight quality checks (tests, lint, format, secrets)  │
│    - Push commits                                               │
│    - Create Draft PR                                            │
│    - Remove lock                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. CRITICAL VERIFICATION PROTOCOL (After PR merged)             │
│    7.1 Pull latest changes                                      │
│    7.2 Reproduce original issue again (MANDATORY)               │
│    7.3 Run ALL tests for regressions (MANDATORY)                │
│    7.4 Check for breaking changes (MANDATORY)                   │
│        → If breaking: Ask user approval, bump major version     │
│    7.5 Check if fix solved related issues (MANDATORY)           │
│    7.6 Complete final checklist                                 │
│    7.7 Close ONLY after ALL checks pass                         │
│    7.8 Reopen immediately if ANY check fails                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Examples

### Example 1: Bug Fix Workflow

```bash
# 1. Check for duplicates
gh issue list --search "in:title,body header duplicate" --state all

# 2. Assign and label
gh issue edit 7 --add-assignee @me
gh issue edit 7 --add-label "bug,component:ui/ux,priority:medium"
gh issue edit 7 --remove-label "needs-triage" --add-label "examining"

# 3. Reproduce
svg2fbf --input_folder test/ --output_path test.fbf.svg
# Observe: Header printed twice ✅ REPRODUCED

# 4. Update labels
gh issue edit 7 --remove-label "examining" --add-label "reproduced"
gh issue edit 7 --remove-label "reproduced" --add-label "verified"
gh issue edit 7 --add-label "effort:small,agent-friendly"

# 5. Start work
gh issue edit 7 --remove-label "verified" --add-label "in-progress"
python ccpm/commands/issue_start.py 7 dev

# 6. Make fix
cd ~/.cache/ccpm-worktrees/Emasoft-svg2fbf/issue-7
# Edit code, commit, test

# 7. Finish and create PR
python ccpm/commands/issue_finish.py 7
gh issue edit 7 --remove-label "in-progress" --add-label "needs-review"

# 8. After PR merged - CRITICAL VERIFICATION
git checkout dev && git pull origin dev

# Reproduce original issue again
svg2fbf --input_folder test/ --output_path test.fbf.svg
# ✅ Header now appears only once!

# Run all tests
pytest tests/ -v
# ✅ All tests pass

# Check for breaking changes
# ✅ No API changes, backward compatible

# Check for related issues
gh issue list --state open --search "in:title,body header print"
# ✅ No related issues found

# Close with verification report
gh issue edit 7 --remove-label "needs-review" --add-label "fixed"
gh issue close 7 --reason "completed" --comment "[Complete verification report]"
```

---

## FAQ

**Q: Why Python instead of Bash?**
A: Cross-platform compatibility. The plugin now works on Windows, macOS, and Linux without requiring Bash.

**Q: Will this work with my project?**
A: Yes! The plugin auto-detects your project name and owner from the git remote URL. It works with ANY GitHub repository.

**Q: Can I skip the verification protocol to save time?**
A: **NO.** The verification protocol is MANDATORY. Skipping it creates technical debt and can lead to:
- Regressions going unnoticed
- Breaking changes being merged without user approval
- Related issues not being fixed
- False "resolved" status on issues

**Q: What if I make breaking changes?**
A: You MUST:
1. Document all breaking changes
2. Ask user approval with @mention
3. WAIT for approval
4. If approved: Bump major version, update docs, create migration guide
5. If NOT approved: Revert and find backward-compatible solution

**Q: Do I need to install any dependencies?**
A: No! The plugin uses only Python standard library. Optional: `psutil` for better process detection.

**Q: Where are the audit logs stored?**
A: `~/.cache/ccpm-audit-logs/{owner}-{project}/YYYY-MM-DD.json` (JSON Lines format)

---

## Support

**Documentation:**
- `ccpm/skills/issue-management.md` - Complete guide (READ THIS FIRST)
- `ccpm/skills/5-branch-workflow.md` - Branch hierarchy
- `ccpm/skills/recovery-procedures.md` - Error recovery

**Commands:**
- `python ccpm/commands/issue_status.py` - Check status
- `python ccpm/commands/issue_abort.py <number>` - Abort work

**Audit Logs:**
- `~/.cache/ccpm-audit-logs/{owner}-{project}/` - JSON logs

---

## License

MIT (planned) - Currently local development only

---

## Version History

**v2.0.0** (2025-01-17)
- Converted all scripts to Python for cross-platform compatibility
- Made project-agnostic (auto-detects project from git remote)
- Added 8-step Critical Verification Protocol (280 lines)
- Added comprehensive label usage rules (200 lines)
- Added proper Python package structure
- Zero mandatory dependencies

**v1.1.0** (2025-01-17)
- Added label system (46 labels)
- Added issue-management.md skill

**v1.0.0** (2025-01-14)
- Initial Bash version for svg2fbf project only

---

**The CCPM plugin ensures safe, isolated, and verified agent workflows on ANY GitHub repository!**
