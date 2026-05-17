#!/usr/bin/env bash
# claude-code.sh -- Claude Code agent wrapper for intent-bench
# Invokes Claude Code in headless mode with a prompt file.
#
# Usage: claude-code.sh <workdir> <model> <prompt_file> <result_dir> <max_budget>
#
# Contract:
#   - Produces $result_dir/transcript.jsonl
#   - Produces $result_dir/stderr.log
#   - Exit 0 = agent completed, non-zero = agent crashed
#   - Runs in the caller's process group (harness handles setsid)
set -euo pipefail

workdir="${1:?Usage: claude-code.sh <workdir> <model> <prompt_file> <result_dir> <max_budget>}"
model="${2:?model required}"
prompt_file="${3:?prompt_file required}"
result_dir="${4:?result_dir required}"
max_budget="${5:?max_budget required}"

cd "$workdir"

claude --model "$model" \
    -p "$(cat "$prompt_file")" \
    --output-format stream-json --verbose \
    --max-budget-usd "$max_budget" \
    --dangerously-skip-permissions \
    > "$result_dir/transcript.jsonl" 2>"$result_dir/stderr.log"
