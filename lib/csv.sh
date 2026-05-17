#!/usr/bin/env bash
# csv.sh -- Ledger row construction and validation for intent-bench
# Schema: 26-column CSV recording all experiment run data
set -euo pipefail

LEDGER_COLUMNS=(
    session_id
    timestamp
    experiment
    condition
    treatment
    agent
    run_number
    model
    prompt_sha256
    input_tokens
    output_tokens
    total_tokens
    tool_tokens
    planning_tokens
    execution_tokens
    turns
    backtracks
    tool_calls_intent
    tool_calls_other
    outcome
    tests_total
    tests_passed
    tests_failed
    wall_clock_seconds
    knowledge_entropy
    transcript_path
)

LEDGER_HEADER=$(IFS=,; echo "${LEDGER_COLUMNS[*]}")
EXPECTED_COLUMN_COUNT=${#LEDGER_COLUMNS[@]}

# Initialize an empty ledger with the header row
ledger_init() {
    local path="${1:?Usage: ledger_init <path>}"
    if [[ -f "$path" ]]; then
        echo "ERROR: Ledger already exists: $path" >&2
        return 1
    fi
    mkdir -p "$(dirname "$path")"
    echo "$LEDGER_HEADER" > "$path"
    echo "Initialized ledger: $path ($EXPECTED_COLUMN_COUNT columns)" >&2
}

# Append a row to the ledger atomically
ledger_append() {
    local path="${1:?Usage: ledger_append <path> <field1> ... <fieldN>}"
    shift

    if [[ ! -f "$path" ]]; then
        echo "ERROR: Ledger does not exist: $path (run ledger_init first)" >&2
        return 1
    fi

    if [[ $# -ne $EXPECTED_COLUMN_COUNT ]]; then
        echo "ERROR: Expected $EXPECTED_COLUMN_COUNT fields, got $#" >&2
        return 1
    fi

    local row
    row=$(IFS=,; echo "$*")

    # Atomic append: write to temp file, then move
    local tmpfile
    tmpfile=$(mktemp "${path}.XXXXXX")
    cat "$path" > "$tmpfile"
    echo "$row" >> "$tmpfile"
    mv "$tmpfile" "$path"
}

# Validate ledger schema and data integrity
ledger_validate() {
    local path="${1:?Usage: ledger_validate <path>}"
    local errors=0

    if [[ ! -f "$path" ]]; then
        echo "ERROR: Ledger not found: $path" >&2
        return 1
    fi

    # Check header
    local header
    header=$(head -1 "$path")
    if [[ "$header" != "$LEDGER_HEADER" ]]; then
        echo "ERROR: Header mismatch" >&2
        echo "  Expected: $LEDGER_HEADER" >&2
        echo "  Got:      $header" >&2
        errors=$((errors + 1))
    fi

    # Check each data row
    local line_num=0
    while IFS= read -r line; do
        line_num=$((line_num + 1))
        [[ $line_num -eq 1 ]] && continue

        local col_count
        col_count=$(echo "$line" | awk -F, '{print NF}')
        if [[ "$col_count" -ne "$EXPECTED_COLUMN_COUNT" ]]; then
            echo "ERROR: Line $line_num: expected $EXPECTED_COLUMN_COUNT columns, got $col_count" >&2
            errors=$((errors + 1))
            continue
        fi

        # Validate condition field (column 4)
        local condition
        condition=$(echo "$line" | cut -d, -f4)
        if [[ "$condition" != "control" && "$condition" != "treatment" ]]; then
            echo "ERROR: Line $line_num: invalid condition '$condition'" >&2
            errors=$((errors + 1))
        fi

        # Validate outcome field (column 20)
        local outcome
        outcome=$(echo "$line" | cut -d, -f20)
        if [[ "$outcome" != "PASS" && "$outcome" != "PARTIAL" && "$outcome" != "FAIL" && "$outcome" != "ERROR" && "$outcome" != "TIMEOUT" ]]; then
            echo "ERROR: Line $line_num: invalid outcome '$outcome'" >&2
            errors=$((errors + 1))
        fi

        # Validate total_tokens = input_tokens + output_tokens
        local input_tokens output_tokens total_tokens
        input_tokens=$(echo "$line" | cut -d, -f10)
        output_tokens=$(echo "$line" | cut -d, -f11)
        total_tokens=$(echo "$line" | cut -d, -f12)
        if [[ $((input_tokens + output_tokens)) -ne "$total_tokens" ]]; then
            echo "ERROR: Line $line_num: total_tokens mismatch" >&2
            errors=$((errors + 1))
        fi

        # Validate control condition has zero tool tokens
        if [[ "$condition" == "control" ]]; then
            local tool_tokens tool_calls_intent
            tool_tokens=$(echo "$line" | cut -d, -f13)
            tool_calls_intent=$(echo "$line" | cut -d, -f18)
            if [[ "$tool_tokens" -ne 0 ]]; then
                echo "ERROR: Line $line_num: control has non-zero tool_tokens ($tool_tokens)" >&2
                errors=$((errors + 1))
            fi
            if [[ "$tool_calls_intent" -ne 0 ]]; then
                echo "ERROR: Line $line_num: control has non-zero tool_calls_intent ($tool_calls_intent)" >&2
                errors=$((errors + 1))
            fi
        fi
    done < "$path"

    local data_rows=$((line_num > 0 ? line_num - 1 : 0))
    if [[ $errors -eq 0 ]]; then
        echo "VALID: $path ($data_rows data rows, $EXPECTED_COLUMN_COUNT columns)" >&2
        return 0
    else
        echo "INVALID: $path ($errors errors in $data_rows data rows)" >&2
        return 1
    fi
}

# Subcommand dispatch when run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cmd="${1:-help}"
    shift || true
    case "$cmd" in
        init)     ledger_init "$@" ;;
        append)   ledger_append "$@" ;;
        validate) ledger_validate "$@" ;;
        help)
            echo "Usage: csv.sh <command> [args]"
            echo "Commands:"
            echo "  init <path>           Initialize empty ledger"
            echo "  append <path> <vals>  Append a row"
            echo "  validate <path>       Validate ledger schema"
            ;;
        *)
            echo "Unknown command: $cmd" >&2
            exit 1
            ;;
    esac
fi
