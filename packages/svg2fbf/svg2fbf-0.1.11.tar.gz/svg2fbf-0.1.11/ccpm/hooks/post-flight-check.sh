#!/usr/bin/env bash
#
# Post-Flight Quality Check for CCPM Agents
#
# Purpose: Validate code quality before creating PR
# Usage: ./post-flight-check.sh [--fix]
# Exit codes:
#   0 - All checks passed, safe to create PR
#   1 - Check failed, fix required
#
# Checks performed:
#   1. Tests pass (pytest)
#   2. Linting passes (ruff check)
#   3. Formatting correct (ruff format --check)
#   4. No secrets detected (trufflehog)
#   5. Correct branch (dev/testing/hotfix/*)
#   6. No protected files modified
#
# Options:
#   --fix  Automatically fix linting and formatting issues
#
# Author: CCPM Plugin
# Last updated: 2025-01-14

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arguments
FIX_MODE=false
if [[ "${1:-}" == "--fix" ]]; then
    FIX_MODE=true
fi

# Paths
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Check if we're in a worktree
CURRENT_BRANCH=$(git branch --show-current)
IN_WORKTREE=false
if [[ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" == "true" ]]; then
    if git rev-parse --git-common-dir | grep -q "worktrees"; then
        IN_WORKTREE=true
    fi
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🛬 POST-FLIGHT QUALITY CHECK                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Branch:${NC} ${CURRENT_BRANCH}"
echo -e "${BLUE}Worktree:${NC} ${IN_WORKTREE}"
if [[ "$FIX_MODE" == true ]]; then
    echo -e "${BLUE}Mode:${NC} Auto-fix enabled"
fi
echo ""

# Track failures
FAILURES=0

# ============================================================================
# Check 1: Tests pass
# ============================================================================
echo -e "${YELLOW}[1/6]${NC} Running test suite..."

if command -v pytest &> /dev/null; then
    if pytest tests/ -v --tb=short; then
        echo -e "${GREEN}   ✓ All tests passed${NC}"
    else
        echo -e "${RED}   ✗ Tests failed${NC}"
        echo ""
        echo "   ${YELLOW}Fix tests before creating PR${NC}"
        echo "   Run: ${GREEN}pytest tests/ -v${NC}"
        ((FAILURES++))
    fi
else
    echo -e "${YELLOW}   ⚠️  pytest not installed, skipping tests${NC}"
    echo "   Install: ${GREEN}uv pip install pytest${NC}"
fi

# ============================================================================
# Check 2: Linting passes
# ============================================================================
echo -e "${YELLOW}[2/6]${NC} Running linter (ruff check)..."

if command -v ruff &> /dev/null; then
    if [[ "$FIX_MODE" == true ]]; then
        echo "   Auto-fixing linting issues..."
        if ruff check src/ tests/ --fix; then
            echo -e "${GREEN}   ✓ Linting passed (auto-fixed)${NC}"
        else
            echo -e "${RED}   ✗ Linting failed (some issues cannot be auto-fixed)${NC}"
            echo "   Run: ${GREEN}ruff check src/ tests/${NC}"
            ((FAILURES++))
        fi
    else
        if ruff check src/ tests/; then
            echo -e "${GREEN}   ✓ Linting passed${NC}"
        else
            echo -e "${RED}   ✗ Linting failed${NC}"
            echo ""
            echo "   ${YELLOW}Fix linting issues or use --fix flag${NC}"
            echo "   Run: ${GREEN}$0 --fix${NC}"
            echo "   Or:  ${GREEN}ruff check src/ tests/ --fix${NC}"
            ((FAILURES++))
        fi
    fi
else
    echo -e "${YELLOW}   ⚠️  ruff not installed, skipping linting${NC}"
    echo "   Install: ${GREEN}uv pip install ruff${NC}"
fi

# ============================================================================
# Check 3: Formatting correct
# ============================================================================
echo -e "${YELLOW}[3/6]${NC} Checking code formatting (ruff format)..."

if command -v ruff &> /dev/null; then
    if [[ "$FIX_MODE" == true ]]; then
        echo "   Auto-formatting code..."
        ruff format src/ tests/
        echo -e "${GREEN}   ✓ Code formatted${NC}"
    else
        if ruff format --check src/ tests/; then
            echo -e "${GREEN}   ✓ Formatting correct${NC}"
        else
            echo -e "${RED}   ✗ Formatting issues detected${NC}"
            echo ""
            echo "   ${YELLOW}Fix formatting or use --fix flag${NC}"
            echo "   Run: ${GREEN}$0 --fix${NC}"
            echo "   Or:  ${GREEN}ruff format src/ tests/${NC}"
            ((FAILURES++))
        fi
    fi
else
    echo -e "${YELLOW}   ⚠️  ruff not installed, skipping formatting${NC}"
fi

# ============================================================================
# Check 4: No secrets detected
# ============================================================================
echo -e "${YELLOW}[4/6]${NC} Scanning for secrets (trufflehog)..."

if command -v trufflehog &> /dev/null; then
    # Scan git history for secrets
    if trufflehog git file://. --only-verified --fail --no-update 2>&1 | grep -q "🐷"; then
        echo -e "${RED}   ✗ Secrets detected!${NC}"
        echo ""
        echo "   ${RED}CRITICAL: Verified secrets found in commits${NC}"
        echo ""
        echo "   ${YELLOW}Actions required:${NC}"
        echo "   1. Remove secrets from code"
        echo "   2. Rewrite git history: ${GREEN}git rebase -i${NC}"
        echo "   3. Rotate compromised credentials"
        echo "   4. See: ccpm/skills/recovery-procedures.md"
        ((FAILURES++))
    else
        echo -e "${GREEN}   ✓ No secrets detected${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  trufflehog not installed, skipping secret scan${NC}"
    echo "   Install: ${GREEN}brew install trufflehog${NC}"
fi

# ============================================================================
# Check 5: Correct branch validation
# ============================================================================
echo -e "${YELLOW}[5/6]${NC} Validating branch..."

FORBIDDEN_BRANCHES=("master" "main")
for forbidden in "${FORBIDDEN_BRANCHES[@]}"; do
    if [[ "$CURRENT_BRANCH" == "$forbidden" ]]; then
        echo -e "${RED}   ✗ Working on forbidden branch: ${forbidden}${NC}"
        echo ""
        echo "   ${RED}CRITICAL: Agents must NEVER work on master/main${NC}"
        echo "   Switch to dev or testing branch immediately"
        ((FAILURES++))
    fi
done

# Warn if on review (allowed but supervised)
if [[ "$CURRENT_BRANCH" == "review" ]]; then
    echo -e "${YELLOW}   ⚠️  Working on review branch (requires supervision)${NC}"
fi

# Check allowed branches
ALLOWED_BRANCHES=("dev" "testing" "review")
branch_allowed=false
for allowed in "${ALLOWED_BRANCHES[@]}"; do
    if [[ "$CURRENT_BRANCH" == "$allowed" ]]; then
        branch_allowed=true
        break
    fi
done

# Also allow hotfix branches
if [[ "$CURRENT_BRANCH" =~ ^hotfix/ ]]; then
    branch_allowed=true
    echo -e "${YELLOW}   ⚠️  Hotfix branch detected (requires supervision)${NC}"
fi

# Also allow issue branches
if [[ "$CURRENT_BRANCH" =~ ^issue-[0-9]+ ]]; then
    branch_allowed=true
fi

if [[ "$branch_allowed" == true ]]; then
    echo -e "${GREEN}   ✓ Branch allowed: ${CURRENT_BRANCH}${NC}"
else
    echo -e "${RED}   ✗ Invalid branch: ${CURRENT_BRANCH}${NC}"
    echo "   Allowed: dev, testing, review, hotfix/*, issue-*"
    ((FAILURES++))
fi

# ============================================================================
# Check 6: No protected files modified
# ============================================================================
echo -e "${YELLOW}[6/6]${NC} Checking for protected file modifications..."

PROTECTED_FILES_LIST="${REPO_ROOT}/ccpm/rules/protected-files.txt"

if [[ -f "$PROTECTED_FILES_LIST" ]]; then
    # Read protected files
    protected_patterns=()
    while IFS= read -r line; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue
        protected_patterns+=("$line")
    done < "$PROTECTED_FILES_LIST"

    # Get modified files (staged and unstaged)
    modified_files=$(git diff --name-only HEAD)

    # Check each modified file
    violations=()
    for file in $modified_files; do
        for pattern in "${protected_patterns[@]}"; do
            if [[ "$file" == $pattern ]]; then
                violations+=("$file")
                break
            fi
        done
    done

    if [[ ${#violations[@]} -gt 0 ]]; then
        echo -e "${RED}   ✗ Protected files modified${NC}"
        echo ""
        for file in "${violations[@]}"; do
            echo -e "      ${RED}✗${NC} $file"
        done
        echo ""
        echo "   ${YELLOW}Recovery:${NC}"
        echo "   ${GREEN}git restore <file>${NC}"
        ((FAILURES++))
    else
        echo -e "${GREEN}   ✓ No protected files modified${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Protected files list not found, skipping check${NC}"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""

if [[ $FAILURES -eq 0 ]]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            ✅ POST-FLIGHT CHECK PASSED                    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}All quality checks passed!${NC}"
    echo ""
    echo -e "${BLUE}Ready to create PR:${NC}"
    echo "   1. Commit changes: ${GREEN}git add . && git commit${NC}"
    echo "   2. Push to origin: ${GREEN}git push origin ${CURRENT_BRANCH}${NC}"
    echo "   3. Create PR: ${GREEN}gh pr create --draft${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ❌ POST-FLIGHT CHECK FAILED                  ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}${FAILURES} check(s) failed${NC}"
    echo ""
    echo -e "${YELLOW}Actions required:${NC}"
    echo "   1. Fix failing checks (see above)"
    echo "   2. Re-run: ${GREEN}$0${NC}"
    echo "   3. Or auto-fix: ${GREEN}$0 --fix${NC}"
    echo ""
    echo -e "${YELLOW}See also:${NC}"
    echo "   - Recovery procedures: ccpm/skills/recovery-procedures.md"
    echo "   - 5-branch workflow: ccpm/skills/5-branch-workflow.md"
    echo ""
    exit 1
fi
