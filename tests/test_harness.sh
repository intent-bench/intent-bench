#!/usr/bin/env bash
# test_harness.sh -- Tests for the intent-bench harness
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PASS=0
FAIL=0

assert_eq() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  [PASS] $desc"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $desc: expected '$expected', got '$actual'"
        FAIL=$((FAIL + 1))
    fi
}

assert_exit() {
    local desc="$1" expected="$2"
    shift 2
    local actual=0
    "$@" >/dev/null 2>&1 || actual=$?
    assert_eq "$desc" "$expected" "$actual"
}

echo "=== Harness Tests ==="

# Test: csv.sh ledger operations
echo "--- csv.sh ---"
tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT

# Init ledger
bash "$REPO_DIR/lib/csv.sh" init "$tmpdir/test.csv"
header=$(head -1 "$tmpdir/test.csv")
col_count=$(echo "$header" | awk -F, '{print NF}')
assert_eq "ledger init creates 26-column header" "26" "$col_count"

# Validate empty ledger
assert_exit "empty ledger validates" 0 bash "$REPO_DIR/lib/csv.sh" validate "$tmpdir/test.csv"

# Validate column names
first_col=$(echo "$header" | cut -d, -f1)
assert_eq "first column is session_id" "session_id" "$first_col"
fifth_col=$(echo "$header" | cut -d, -f5)
assert_eq "fifth column is treatment" "treatment" "$fifth_col"
sixth_col=$(echo "$header" | cut -d, -f6)
assert_eq "sixth column is agent" "agent" "$sixth_col"

echo ""

# Test: experiment validation
echo "--- experiment validation ---"
assert_exit "url-shortener validates" 0 bash "$REPO_DIR/bench.sh" validate url-shortener
assert_exit "task-manager validates" 0 bash "$REPO_DIR/bench.sh" validate task-manager
assert_exit "nonexistent experiment fails" 1 bash "$REPO_DIR/bench.sh" validate nonexistent

echo ""

# Test: prompt blinding
echo "--- prompt blinding ---"
for prompt in "$REPO_DIR"/prompts/*.md; do
    name=$(basename "$prompt" .md)
    if grep -qi -E '\b(rtmx|rtm|mcp|requirements.traceability)\b' "$prompt" 2>/dev/null; then
        echo "  [FAIL] $name prompt contains treatment references"
        FAIL=$((FAIL + 1))
    else
        echo "  [PASS] $name prompt has no treatment references"
        PASS=$((PASS + 1))
    fi
done

echo ""

# Test: treatment plugins
echo "--- treatment plugins ---"
for plugin in "$REPO_DIR"/treatments/*.sh; do
    name=$(basename "$plugin" .sh)
    # Validate command should work (rtmx may not be installed)
    if [[ "$name" == "manual-spec" ]]; then
        assert_exit "$name validate succeeds" 0 bash "$plugin" validate
    fi
done

echo ""

# Test: manual-spec fixture generation
echo "--- fixture generation ---"
tmpfixtures=$(mktemp -d)
python3 "$REPO_DIR/scripts/gen_requirements_md.py" \
    "$REPO_DIR/fixtures/rtmx/url-shortener/rtm.csv" \
    "$REPO_DIR/fixtures/rtmx/url-shortener/requirements" \
    "$tmpfixtures/requirements.md" 2>/dev/null
if [[ -f "$tmpfixtures/requirements.md" ]]; then
    # Verify it contains all requirement IDs from the CSV
    req_count=$(grep -c "^## [0-9]" "$tmpfixtures/requirements.md" || true)
    assert_eq "generated requirements.md has 10 requirements" "10" "$req_count"
else
    echo "  [FAIL] fixture generation did not produce output"
    FAIL=$((FAIL + 1))
fi
rm -rf "$tmpfixtures"

echo ""

# Test: dry run
echo "--- dry run ---"
output=$(bash "$REPO_DIR/bench.sh" run url-shortener --condition control --dry-run 2>&1)
if echo "$output" | grep -q "Would run"; then
    echo "  [PASS] dry run produces expected output"
    PASS=$((PASS + 1))
else
    echo "  [FAIL] dry run output unexpected"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] || exit 1
