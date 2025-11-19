# CCPM Label Management

**Skill**: Complete GitHub label taxonomy and usage rules
**Use when**: Adding, removing, or understanding issue labels

---

## Overview

CCPM uses 46 labels across 8 categories to track issue lifecycle. Understanding when to add/remove labels and which can coexist is critical for proper issue management.

**Why Labels Matter**:
- Track issue progress through state machine
- Filter and search issues efficiently
- Identify work appropriate for agents vs. humans
- Prioritize work

---

## 46 Labels Across 8 Categories

### Status Labels (10) - **MUTUALLY EXCLUSIVE**

**Critical Rule**: Only ONE status label at a time!

```
needs-triage → examining → reproduced → verified → in-progress → needs-review → fixed
              └→ needs-reproduction → examining (after info provided)
              └→ cannot-reproduce (after 3 attempts)
              └→ wontfix (rejected)
```

**Labels**:
- `needs-triage` - New issue, not yet examined
- `examining` - Agent/human is investigating
- `reproduced` - Issue successfully reproduced
- `needs-reproduction` - Can't reproduce, need more info (attempt 1-2/3)
- `cannot-reproduce` - Failed to reproduce after 3 attempts
- `verified` - Issue understood, root cause identified, ready to work
- `in-progress` - Active work happening
- `needs-review` - PR created, awaiting review
- `fixed` - Completed and verified
- `wontfix` - Won't be fixed (intentional behavior, out of scope)

---

### Type Labels (7) - **CAN COEXIST** (with exceptions)

**Labels**:
- `bug` - Something is broken
- `enhancement` - New feature or improvement
- `documentation` - Docs need updating
- `question` - User question
- `duplicate` - Duplicate of another issue
- `invalid` - Not a real issue
- `regression` - Previously working feature broke

**Can coexist**:
- `bug` + `regression` (bug that broke working feature)
- `bug` + `security` (critical security bug)
- `enhancement` + `documentation` (new feature needs docs)

**Mutually exclusive**:
- `bug` vs. `enhancement` (can't be both)
- `duplicate` vs. any other (if duplicate, type doesn't matter)
- `invalid` vs. any other (if invalid, type doesn't matter)

---

### Priority Labels (4) - **MUTUALLY EXCLUSIVE**

Only ONE priority at a time!

- `priority:critical` - System broken, data loss, security issue
- `priority:high` - Major feature broken, affects many users
- `priority:medium` - Normal bugs, most issues
- `priority:low` - Nice to have, minor issues

---

### Component Labels (8) - **CAN COEXIST**

Multiple components can be affected!

- `component:cli` - Command-line interface
- `component:core` - Core logic
- `component:api` - Public API
- `component:validation` - Input validation
- `component:ui/ux` - User interface
- `component:tests` - Test suite
- `component:ci/cd` - Build/deployment
- `component:docs` - Documentation

**Example**: `component:cli` + `component:validation` (CLI argument validation bug)

---

### Effort Labels (5) - **MUTUALLY EXCLUSIVE**

Only ONE effort estimate!

- `effort:trivial` - < 30 minutes
- `effort:small` - 1-2 hours
- `effort:medium` - 1 day
- `effort:large` - 2-5 days
- `effort:epic` - > 1 week

---

### Contribution Labels (4) - **CAN COEXIST**

- `good first issue` - Simple, well-defined, good for newcomers
- `help wanted` - Community help appreciated
- `agent-friendly` - Safe for AI agents to work on
- `needs-human` - Requires human judgment/expertise

**Example**: `good first issue` + `agent-friendly` (perfect for new agents)

---

### Platform Labels (4) - **CAN COEXIST**

- `platform:windows` - Windows-specific issue
- `platform:macos` - macOS-specific issue
- `platform:linux` - Linux-specific issue
- `platform:all` - Affects all platforms

**Example**: `platform:windows` + `platform:linux` (but not macOS)

---

### Standard Labels (4) - **CAN COEXIST**

- `dependencies` - Dependency update/issue
- `security` - Security vulnerability
- `performance` - Performance problem
- `breaking-change` - Breaks backward compatibility

---

## Label Workflow - Status State Machine

### Normal Flow

```bash
# 1. New issue created
gh issue edit N --add-label "needs-triage"

# 2. Start examining
gh issue edit N --remove-label "needs-triage" --add-label "examining"

# 3a. Successfully reproduced (for bugs)
gh issue edit N --remove-label "examining" --add-label "reproduced"

# 3b. Can't reproduce yet (need more info)
gh issue edit N --remove-label "examining" --add-label "needs-reproduction"
# User provides info...
gh issue edit N --remove-label "needs-reproduction" --add-label "examining"

# 3c. Can't reproduce after 3 attempts
gh issue edit N --remove-label "examining" --add-label "cannot-reproduce"
gh issue close N --reason "not planned"

# 4. Root cause identified, ready to work
gh issue edit N --remove-label "reproduced" --add-label "verified"

# 5. Start work
gh issue edit N --remove-label "verified" --add-label "in-progress"

# 6. Create PR
gh issue edit N --remove-label "in-progress" --add-label "needs-review"

# 7. After PR merged AND verification complete
gh issue edit N --remove-label "needs-review" --add-label "fixed"
gh issue close N --reason "completed"
```

### **CRITICAL RULE**: Remove old status label when adding new one!

❌ **WRONG**:
```bash
gh issue edit 7 --add-label "in-progress"
# Result: "examining" + "in-progress" (TWO status labels - INVALID!)
```

✅ **CORRECT**:
```bash
gh issue edit 7 --remove-label "examining" --add-label "in-progress"
# Result: Only "in-progress" (ONE status label)
```

---

## Valid Label Combinations

### Example 1: Critical Security Bug in CLI
```bash
gh issue edit N --add-label "bug,security,priority:critical,component:cli,effort:small,needs-human"
```
**Explanation**:
- `bug` - Type
- `security` - Standard (coexists with bug)
- `priority:critical` - Priority (exclusive)
- `component:cli` - Component
- `effort:small` - Effort (exclusive)
- `needs-human` - Contribution (security needs human review)

### Example 2: Medium-Priority Documentation Enhancement
```bash
gh issue edit N --add-label "enhancement,documentation,priority:medium,component:docs,effort:trivial,good first issue,agent-friendly"
```

### Example 3: Cross-Platform Performance Regression
```bash
gh issue edit N --add-label "bug,regression,performance,priority:high,component:core,platform:all,effort:large"
```

---

## Invalid Label Combinations

### ❌ Multiple Status Labels
```bash
gh issue edit N --add-label "examining,in-progress"
# WRONG! Only ONE status label allowed!
```
**Fix**: Remove old status before adding new

### ❌ Bug + Enhancement
```bash
gh issue edit N --add-label "bug,enhancement"
# WRONG! Can't be both bug and feature
```
**Fix**: Choose one. If fixing bug AND adding feature, split into 2 issues.

### ❌ Multiple Priorities
```bash
gh issue edit N --add-label "priority:high,priority:critical"
# WRONG! Only ONE priority allowed
```
**Fix**: Choose highest priority

### ❌ Multiple Efforts
```bash
gh issue edit N --add-label "effort:small,effort:large"
# WRONG! Only ONE effort estimate
```
**Fix**: Re-evaluate and pick one

---

## When to Add/Remove Labels

### When Issue Created
**ADD**:
- `needs-triage` (status)
- Type label if obvious (`bug`, `enhancement`, etc.)
- `platform:*` if platform-specific

### When Starting Examination
**REMOVE**: `needs-triage`
**ADD**: `examining`

### When Reproduced
**REMOVE**: `examining`
**ADD**: `reproduced`
**ALSO ADD**:
- Priority label
- Component labels
- Effort estimate

### When Can't Reproduce
**REMOVE**: `examining`
**ADD**: `needs-reproduction`
**COMMENT**: Ask user for more details

### When Starting Work
**REMOVE**: `verified`
**ADD**: `in-progress`
**ALSO ADD**:
- `agent-friendly` or `needs-human` if not already set

### When Creating PR
**REMOVE**: `in-progress`
**ADD**: `needs-review`

### When Closing Issue
**REMOVE**: `needs-review`
**ADD**: `fixed` (if resolved) or `wontfix` (if rejected) or `duplicate` (if duplicate)

---

## Label Cleanup Guidelines

### Remove Obsolete Labels

When issue status changes, old labels may become obsolete:

```bash
# Issue was initially thought to be CLI bug but was actually core logic
gh issue edit N --remove-label "component:cli" --add-label "component:core"

# Issue was high priority but user said it's actually low
gh issue edit N --remove-label "priority:high" --add-label "priority:low"

# Feature completed, remove in-progress labels
gh issue edit N --remove-label "needs-human,help wanted"
```

### Don't Accumulate Status Labels

❌ **BAD** - Issue with 5 status labels accumulated over time:
```
needs-triage, examining, reproduced, in-progress, needs-review
```

✅ **GOOD** - Issue with only current status:
```
needs-review
```

**Fix**:
```bash
gh issue edit N --remove-label "needs-triage,examining,reproduced,in-progress"
# Keep only current status
```

---

## Quick Reference Commands

```bash
# List all labels
gh label list

# View issue labels
gh issue view <number>

# Add labels
gh issue edit <number> --add-label "label1,label2,label3"

# Remove labels
gh issue edit <number> --remove-label "label1,label2"

# Transition status (remove old, add new)
gh issue edit <number> --remove-label "examining" --add-label "reproduced"

# Search by labels
gh issue list --label "bug,priority:high"
gh issue list --label "agent-friendly,good first issue"
```

---

## Common Mistakes to Avoid

### Mistake 1: Not Removing Old Status
❌ Add `in-progress` without removing `examining`
✅ Always remove old status when transitioning

### Mistake 2: Multiple Priorities
❌ Issue has both `priority:high` and `priority:critical`
✅ Only ONE priority label

### Mistake 3: Conflicting Types
❌ Issue labeled `bug` + `enhancement`
✅ Split into 2 issues or choose primary type

### Mistake 4: Forgetting Component
❌ Issue has status/type but no component
✅ Always add component during reproduction/verification

### Mistake 5: Wrong Platform Label
❌ `platform:windows` on cross-platform issue
✅ Use `platform:all` or multiple platform labels

---

## When to Use This Skill

**Use this skill when**:
- Creating new issues
- Updating issue status
- Unsure which labels to add
- Seeing invalid label combinations
- Cleaning up old issues

**After using this skill**:
- Use `ccpm-issue-workflow` for complete workflow
- Use `ccpm-verification-protocol` before closing
- Use `ccpm-breaking-changes` if `breaking-change` label needed

---

**For complete 200-line label usage rules, see**: `ccpm/skills/issue-management.md` (Label Usage Rules section)
