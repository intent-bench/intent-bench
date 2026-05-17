# Ledger Schema

The data ledger (`results/summary.csv`) is the single source of truth
for all experiment results. It is append-only and schema-validated.

## Columns (26 total)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | session_id | UUID | Unique run identifier |
| 2 | timestamp | ISO 8601 | Run start time (UTC) |
| 3 | experiment | string | Experiment name (e.g., "task-manager") |
| 4 | condition | enum | "control" or "treatment" |
| 5 | treatment | string | Treatment plugin name (e.g., "rtmx", "manual-spec") |
| 6 | agent | string | Agent wrapper name (e.g., "claude-code") |
| 7 | run_number | int | Sequential run number within a batch |
| 8 | model | string | Model ID (e.g., "claude-sonnet-4-20250514") |
| 9 | prompt_sha256 | hex | SHA-256 of the prompt file |
| 10 | input_tokens | int | Total input tokens (including cache) |
| 11 | output_tokens | int | Total output tokens |
| 12 | total_tokens | int | input_tokens + output_tokens |
| 13 | tool_tokens | int | Tokens attributed to intent tool calls |
| 14 | planning_tokens | int | Tokens before first code edit |
| 15 | execution_tokens | int | Tokens after first code edit |
| 16 | turns | int | Number of assistant turns |
| 17 | backtracks | int | Re-reads of previously read files |
| 18 | tool_calls_intent | int | Number of intent tool invocations |
| 19 | tool_calls_other | int | Number of non-intent tool calls |
| 20 | outcome | enum | PASS, PARTIAL, FAIL, ERROR, TIMEOUT |
| 21 | tests_total | int | Total tests detected |
| 22 | tests_passed | int | Tests that passed |
| 23 | tests_failed | int | Tests that failed |
| 24 | wall_clock_seconds | int | Wall clock duration |
| 25 | knowledge_entropy | float | Agent entropy score (0-10) |
| 26 | transcript_path | path | Relative path to raw session data |

## Outcome Definitions

- **PASS:** All tests pass (tests_failed == 0, tests_passed > 0)
- **PARTIAL:** Some tests pass but some fail, or test runner has issues
- **FAIL:** Tests run but most/all fail
- **ERROR:** Agent crashed or produced no usable output
- **TIMEOUT:** Agent exceeded budget or wall clock limit

## Validation Rules

1. total_tokens == input_tokens + output_tokens
2. condition must be "control" or "treatment"
3. outcome must be one of the five defined values
4. control runs must have tool_tokens == 0 and tool_calls_intent == 0
5. Column count must be exactly 26

Run validation: `bash lib/csv.sh validate results/summary.csv`

## Token Attribution

- **tool_tokens:** Tokens in turns that contain intent tool calls
  (configurable prefix via INTENT_TOOL_PREFIX env var)
- **planning_tokens:** All tokens before the first Write/Edit tool call
- **execution_tokens:** All tokens after the first Write/Edit tool call
- planning_tokens + execution_tokens == total_tokens (approximately;
  tool_tokens is a subset of planning_tokens)
