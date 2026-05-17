#!/usr/bin/env bash
# test_entropy.sh -- Tests for the agent entropy scorer
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

echo "=== Entropy Tests ==="

# Create minimal transcript and workdir for testing
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# Create a minimal transcript (NDJSON)
cat > "$tmpdir/transcript.jsonl" <<'EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Write","input":{"file_path":"/tmp/test/main.go","content":"package main"}}],"usage":{"input_tokens":100,"output_tokens":50}}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Write","input":{"file_path":"/tmp/test/main_test.go","content":"package main"}}],"usage":{"input_tokens":200,"output_tokens":80}}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Bash","input":{"command":"go test ./..."}}],"usage":{"input_tokens":150,"output_tokens":30}}}
EOF

# Create workdir with conventional structure
mkdir -p "$tmpdir/workdir"
echo "module test" > "$tmpdir/workdir/go.mod"
echo "package main" > "$tmpdir/workdir/main.go"
echo "package main" > "$tmpdir/workdir/main_test.go"

# Test: basic scoring produces valid JSON
echo "--- basic scoring ---"
output=$(python3 "$REPO_DIR/entropy/agent_entropy.py" \
    "$tmpdir/transcript.jsonl" "$tmpdir/workdir" \
    --tests-passed 5 --tests-failed 0 --tests-total 5 --outcome PASS 2>/dev/null)

if echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'entropy_score' in d" 2>/dev/null; then
    echo "  [PASS] produces valid JSON with entropy_score"
    PASS=$((PASS + 1))
else
    echo "  [FAIL] did not produce valid JSON"
    FAIL=$((FAIL + 1))
fi

# Test: score is in valid range
score=$(echo "$output" | python3 -c "import sys,json; print(json.load(sys.stdin)['entropy_score'])")
if python3 -c "assert 0.0 <= float('$score') <= 10.0" 2>/dev/null; then
    echo "  [PASS] entropy_score in [0, 10]: $score"
    PASS=$((PASS + 1))
else
    echo "  [FAIL] entropy_score out of range: $score"
    FAIL=$((FAIL + 1))
fi

# Test: 4 dimensions included
dims=$(echo "$output" | python3 -c "import sys,json; print(json.load(sys.stdin)['dimensions_included'])")
assert_eq "4 dimensions included" "4" "$dims"

# Test: perfect PASS with conventional structure should have low entropy
if python3 -c "assert float('$score') < 5.0" 2>/dev/null; then
    echo "  [PASS] good run has low entropy (< 5.0): $score"
    PASS=$((PASS + 1))
else
    echo "  [FAIL] good run should have low entropy, got $score"
    FAIL=$((FAIL + 1))
fi

echo ""

# Test: FAIL outcome with no tests should have high entropy
echo "--- high entropy case ---"
fail_output=$(python3 "$REPO_DIR/entropy/agent_entropy.py" \
    "$tmpdir/transcript.jsonl" "$tmpdir/workdir" \
    --tests-passed 0 --tests-failed 5 --tests-total 5 --outcome FAIL 2>/dev/null)
fail_score=$(echo "$fail_output" | python3 -c "import sys,json; print(json.load(sys.stdin)['entropy_score'])")

if python3 -c "assert float('$fail_score') > float('$score')" 2>/dev/null; then
    echo "  [PASS] FAIL has higher entropy ($fail_score) than PASS ($score)"
    PASS=$((PASS + 1))
else
    echo "  [FAIL] expected FAIL entropy > PASS entropy"
    FAIL=$((FAIL + 1))
fi

echo ""

# Test: parse_transcript.py
echo "--- parse_transcript ---"
token_output=$(python3 "$REPO_DIR/lib/parse_transcript.py" "$tmpdir/transcript.jsonl" 2>/dev/null)
token_count=$(echo "$token_output" | awk '{print $3}')
if [[ "$token_count" -gt 0 ]]; then
    echo "  [PASS] parse_transcript extracts tokens: $token_count"
    PASS=$((PASS + 1))
else
    echo "  [FAIL] parse_transcript returned 0 tokens"
    FAIL=$((FAIL + 1))
fi

# Test: configurable prefix via env var
echo "--- configurable prefix ---"
cat > "$tmpdir/transcript_mcp.jsonl" <<'EOF'
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"mcp__rtmx__status","input":{}}],"usage":{"input_tokens":100,"output_tokens":50}}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Write","input":{"file_path":"/tmp/x","content":"x"}}],"usage":{"input_tokens":200,"output_tokens":80}}}
EOF

intent_calls=$(INTENT_TOOL_PREFIX="mcp__rtmx__" python3 "$REPO_DIR/lib/parse_transcript.py" \
    "$tmpdir/transcript_mcp.jsonl" 2>/dev/null | awk '{print $9}')
assert_eq "detects 1 intent tool call" "1" "$intent_calls"

# Different prefix should find 0
intent_calls2=$(INTENT_TOOL_PREFIX="mcp__other__" python3 "$REPO_DIR/lib/parse_transcript.py" \
    "$tmpdir/transcript_mcp.jsonl" 2>/dev/null | awk '{print $9}')
assert_eq "different prefix finds 0 intent calls" "0" "$intent_calls2"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] || exit 1
