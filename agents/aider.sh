#!/usr/bin/env bash
# aider.sh -- Aider agent wrapper for intent-bench
# Uses aider (https://aider.chat) for multi-model support.
# Supports OpenAI, Anthropic, Ollama, and other providers.
#
# Usage: aider.sh <workdir> <model> <prompt_file> <result_dir> <max_budget>
#
# Model examples:
#   openai/gpt-4o           -- OpenAI GPT-4o (requires OPENAI_API_KEY)
#   anthropic/claude-sonnet-4-20250514 -- Anthropic (requires ANTHROPIC_API_KEY)
#   ollama/llama3           -- Local Ollama model
#   deepseek/deepseek-chat  -- DeepSeek (requires DEEPSEEK_API_KEY)
#
# Contract:
#   - Produces $result_dir/transcript.jsonl (from chat history)
#   - Produces $result_dir/stderr.log
#   - Exit 0 = agent completed, non-zero = agent crashed
set -euo pipefail

workdir="${1:?Usage: aider.sh <workdir> <model> <prompt_file> <result_dir> <max_budget>}"
model="${2:?model required}"
prompt_file="${3:?prompt_file required}"
result_dir="${4:?result_dir required}"
max_budget="${5:?max_budget required}"

if ! command -v aider &>/dev/null; then
    echo "ERROR: aider not found. Install with: brew install aider" >&2
    exit 1
fi

cd "$workdir"

# Aider uses model names directly; strip provider prefix for ollama
aider_model="$model"

# Determine test command from experiment config if available
test_cmd_args=()
if [[ -n "${BENCH_TEST_CMD:-}" ]]; then
    test_cmd_args=(--test-cmd "$BENCH_TEST_CMD" --auto-test)
fi

# If treatment placed a REQUIREMENTS.md, add it as read-only context
read_args=()
if [[ -f "$workdir/REQUIREMENTS.md" ]]; then
    read_args=(--read "$workdir/REQUIREMENTS.md")
fi

# Chat history captures the full conversation for transcript parsing.
# LLM history captures raw API calls for token accounting.
chat_history="$result_dir/chat_history.md"
llm_history="$result_dir/llm_history.jsonl"

aider \
    --model "$aider_model" \
    --message-file "$prompt_file" \
    --yes-always \
    --no-auto-commits \
    --no-show-model-warnings \
    --no-analytics \
    --chat-history-file "$chat_history" \
    --llm-history-file "$llm_history" \
    "${test_cmd_args[@]}" \
    "${read_args[@]}" \
    2>"$result_dir/stderr.log" || true

# Convert aider's LLM history to our transcript format.
# aider writes NDJSON to llm_history with request/response pairs.
# We pass it through as-is since parse_transcript.py handles NDJSON.
if [[ -f "$llm_history" ]]; then
    cp "$llm_history" "$result_dir/transcript.jsonl"
elif [[ -f "$chat_history" ]]; then
    # Fallback: wrap chat history as a single JSON record
    python3 -c "
import json, sys
content = open('$chat_history').read()
record = {
    'type': 'chat_history',
    'agent': 'aider',
    'model': '$model',
    'content': content
}
json.dump(record, sys.stdout)
print()
" > "$result_dir/transcript.jsonl"
else
    echo '{"type":"error","message":"no transcript produced"}' \
        > "$result_dir/transcript.jsonl"
fi
