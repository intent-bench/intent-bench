#!/usr/bin/env bash
# bench.sh -- Experiment runner for intent-bench
# Measures whether providing structured intent to coding agents
# improves implementation effectiveness.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/csv.sh"

# Defaults
DEFAULT_MODEL="claude-sonnet-4-20250514"
DEFAULT_RUNS=5
DEFAULT_AGENT="claude-code"
RESULTS_DIR="$SCRIPT_DIR/results"
LEDGER="$RESULTS_DIR/summary.csv"

# Process isolation globals
CURRENT_WORKDIR=""
CURRENT_PGID=""

# Portable setsid: macOS lacks setsid, use perl POSIX::setsid()
run_in_new_pgroup() {
    if command -v setsid >/dev/null 2>&1; then
        setsid "$@"
    else
        perl -e 'use POSIX qw(setsid); setsid(); exec @ARGV' -- "$@"
    fi
}

cleanup_run() {
    local exit_code=$?
    if [[ -n "$CURRENT_PGID" ]]; then
        kill -TERM -"$CURRENT_PGID" 2>/dev/null || true
        sleep 1
        kill -KILL -"$CURRENT_PGID" 2>/dev/null || true
        CURRENT_PGID=""
    fi
    if [[ -n "$CURRENT_WORKDIR" && -d "$CURRENT_WORKDIR" ]]; then
        rm -rf "$CURRENT_WORKDIR"
        CURRENT_WORKDIR=""
    fi
    return $exit_code
}

cleanup_orphans() {
    for port in 8080 3000 5000; do
        local pid
        pid=$(lsof -ti :"$port" 2>/dev/null || true)
        if [[ -n "$pid" ]]; then
            echo "  [WARN] Port $port occupied by pid $pid, killing orphan"
            kill "$pid" 2>/dev/null || true
        fi
    done
}

usage() {
    cat <<EOF
Usage: bench.sh <command> [options]

Commands:
  run <experiment>       Run an experiment
  validate <experiment>  Validate experiment configuration
  init-ledger            Initialize the results ledger

Run options:
  --condition <control|treatment>  Condition to run (required)
  --treatment <name>               Treatment plugin (default: from experiment yaml)
  --agent <name>                   Agent wrapper (default: $DEFAULT_AGENT)
  --runs <N>                       Number of runs (default: $DEFAULT_RUNS)
  --model <model>                  Model ID (default: $DEFAULT_MODEL)
  --dry-run                        Validate setup without invoking model

Examples:
  bench.sh run url-shortener --condition control --runs 5
  bench.sh run url-shortener --condition treatment --treatment rtmx --runs 5
  bench.sh run task-manager --condition treatment --treatment manual-spec --runs 5
  bench.sh validate url-shortener
  bench.sh init-ledger
EOF
}

# Load experiment configuration
load_experiment() {
    local name="${1:?experiment name required}"
    local config="$SCRIPT_DIR/experiments/${name}.yaml"

    if [[ ! -f "$config" ]]; then
        echo "ERROR: Experiment config not found: $config" >&2
        return 1
    fi

    EXP_NAME="$name"
    EXP_REPO=$(python3 -c "import yaml; print(yaml.safe_load(open('$config'))['repo'])" 2>/dev/null || echo "")
    EXP_TEST_CMD=$(python3 -c "import yaml; print(yaml.safe_load(open('$config'))['test_command'])" 2>/dev/null || echo "")
    EXP_SETUP_CMD=$(python3 -c "import yaml; print(yaml.safe_load(open('$config')).get('setup_command', ''))" 2>/dev/null || echo "")
    EXP_BUDGET=$(python3 -c "import yaml; print(yaml.safe_load(open('$config')).get('max_budget_usd', '5.00'))" 2>/dev/null || echo "5.00")
    EXP_TREATMENT=$(python3 -c "import yaml; print(yaml.safe_load(open('$config')).get('treatment', 'rtmx'))" 2>/dev/null || echo "rtmx")
    EXP_AGENT=$(python3 -c "import yaml; print(yaml.safe_load(open('$config')).get('agent', 'claude-code'))" 2>/dev/null || echo "claude-code")

    if [[ -z "$EXP_TEST_CMD" ]]; then
        echo "ERROR: Experiment '$name' has no test_command defined" >&2
        return 1
    fi
}

# Validate experiment configuration
validate_experiment() {
    local name="${1:?experiment name required}"
    local errors=0

    echo "Validating experiment: $name"

    if ! load_experiment "$name" 2>/dev/null; then
        echo "  [FAIL] Config file missing or invalid" >&2
        return 1
    fi
    echo "  [PASS] Config loads"

    # Prompt exists and has no treatment references
    local prompt="$SCRIPT_DIR/prompts/${name}.md"
    if [[ ! -f "$prompt" ]]; then
        echo "  [FAIL] Prompt file missing: $prompt" >&2
        errors=$((errors + 1))
    else
        if grep -qi -E '\b(rtmx|rtm|mcp|requirements.traceability)\b' "$prompt" 2>/dev/null; then
            echo "  [FAIL] Prompt contains treatment references (violates blinding)" >&2
            errors=$((errors + 1))
        else
            echo "  [PASS] Prompt exists, no treatment references"
        fi
    fi

    # Treatment plugin exists
    local treatment_script="$SCRIPT_DIR/treatments/${EXP_TREATMENT}.sh"
    if [[ ! -f "$treatment_script" ]]; then
        echo "  [FAIL] Treatment plugin missing: $treatment_script" >&2
        errors=$((errors + 1))
    else
        # Validate treatment plugin (runtime deps may be missing in CI)
        local validate_output
        if validate_output=$(bash "$treatment_script" validate 2>&1); then
            echo "  [PASS] Treatment plugin valid: $EXP_TREATMENT"
        else
            echo "  [WARN] Treatment runtime deps unavailable: $EXP_TREATMENT ($validate_output)"
        fi
    fi

    # Agent wrapper exists
    local agent_script="$SCRIPT_DIR/agents/${EXP_AGENT}.sh"
    if [[ ! -f "$agent_script" ]]; then
        echo "  [FAIL] Agent wrapper missing: $agent_script" >&2
        errors=$((errors + 1))
    else
        echo "  [PASS] Agent wrapper exists: $EXP_AGENT"
    fi

    # Fixture exists for treatment
    local fixture_dir="$SCRIPT_DIR/fixtures/${EXP_TREATMENT}/$name"
    if [[ ! -d "$fixture_dir" ]]; then
        echo "  [WARN] No fixture directory: $fixture_dir (treatment condition unavailable)"
    else
        echo "  [PASS] Fixture directory exists"
    fi

    if [[ $errors -eq 0 ]]; then
        echo "  Result: VALID"
        return 0
    else
        echo "  Result: INVALID ($errors errors)"
        return 1
    fi
}

# Set up working directory
# Control: empty dir (or cloned repo) only
# Treatment: delegates to treatment plugin
setup_workdir() {
    local name="$1" condition="$2" treatment="$3" workdir="$4"

    # Create base workdir
    if [[ -z "$EXP_REPO" || "$EXP_REPO" == "none" ]]; then
        mkdir -p "$workdir"
    else
        git clone --quiet "$EXP_REPO" "$workdir"
    fi

    # Run experiment-specific setup
    if [[ -n "$EXP_SETUP_CMD" ]]; then
        (cd "$workdir" && eval "$EXP_SETUP_CMD")
    fi

    # Treatment condition: delegate to plugin
    if [[ "$condition" == "treatment" ]]; then
        local fixture_dir="$SCRIPT_DIR/fixtures/${treatment}/$name"
        local treatment_script="$SCRIPT_DIR/treatments/${treatment}.sh"

        if [[ ! -f "$treatment_script" ]]; then
            echo "ERROR: Treatment plugin not found: $treatment_script" >&2
            return 1
        fi

        bash "$treatment_script" setup "$workdir" "$name" "$fixture_dir"
    fi
}

# Execute a single run
execute_run() {
    local experiment="$1" condition="$2" treatment="$3" agent="$4"
    local run_number="$5" model="$6" workdir="$7"

    local prompt="$SCRIPT_DIR/prompts/${experiment}.md"
    local prompt_sha
    prompt_sha=$(shasum -a 256 "$prompt" | cut -d' ' -f1)

    local session_id
    session_id=$(python3 -c "import uuid; print(uuid.uuid4())")
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local result_dir="$RESULTS_DIR/raw/$experiment/$condition/$session_id"
    mkdir -p "$result_dir"

    echo "[$condition/$treatment] Run $run_number -- session $session_id"

    local start_time
    start_time=$(date +%s)

    # Delegate to agent wrapper
    local agent_script="$SCRIPT_DIR/agents/${agent}.sh"
    local exit_code=0
    export BENCH_TEST_CMD="$EXP_TEST_CMD"
    run_in_new_pgroup bash "$agent_script" \
        "$workdir" "$model" "$prompt" "$result_dir" "$EXP_BUDGET" &
    local agent_pid=$!
    CURRENT_PGID=$agent_pid
    wait "$agent_pid" || exit_code=$?
    CURRENT_PGID=""

    local end_time
    end_time=$(date +%s)
    local wall_clock=$((end_time - start_time))

    # Extract token counts from transcript
    local input_tokens=0 output_tokens=0 total_tokens=0
    local tool_tokens=0 planning_tokens=0 execution_tokens=0
    local turns=0 backtracks=0 tool_calls_intent=0 tool_calls_other=0
    if [[ -f "$result_dir/transcript.jsonl" ]]; then
        local token_output
        token_output=$(python3 "$SCRIPT_DIR/lib/parse_transcript.py" \
            "$result_dir/transcript.jsonl" 2>"$result_dir/token_detail.json" || echo "0 0 0 0 0 0 0 0 0 0")
        read -r input_tokens output_tokens total_tokens tool_tokens planning_tokens \
            execution_tokens turns backtracks tool_calls_intent tool_calls_other <<< "$token_output"
    fi

    # Outcome verification (wrapped to prevent abort before ledger write)
    local outcome="ERROR" tests_total=0 tests_passed=0 tests_failed=0
    if [[ $exit_code -ne 0 && ! -f "$result_dir/transcript.jsonl" ]]; then
        outcome="ERROR"
    else
        if source "$SCRIPT_DIR/lib/verify.sh" && \
           verify_outcome "$workdir" "$EXP_TEST_CMD" "$result_dir/test_output.txt" 2>"$result_dir/verify_stderr.log"; then
            outcome="$VERIFY_OUTCOME"
            tests_total="$VERIFY_TOTAL"
            tests_passed="$VERIFY_PASSED"
            tests_failed="$VERIFY_FAILED"
        else
            echo "  [WARN] Outcome verification failed, recording as ERROR" >&2
            outcome="ERROR"
        fi
    fi

    # Compute knowledge entropy
    local knowledge_entropy=""
    if [[ -f "$result_dir/transcript.jsonl" && -d "$workdir" ]]; then
        knowledge_entropy=$(python3 "$SCRIPT_DIR/entropy/agent_entropy.py" \
            "$result_dir/transcript.jsonl" "$workdir" \
            --tests-passed "$tests_passed" --tests-failed "$tests_failed" \
            --tests-total "$tests_total" --outcome "$outcome" 2>/dev/null \
            | python3 -c "import sys,json; print(json.load(sys.stdin).get('entropy_score',''))" 2>/dev/null || echo "")
    fi

    # Append to ledger (new schema with treatment, agent columns)
    ledger_append "$LEDGER" \
        "$session_id" "$timestamp" "$experiment" "$condition" "$treatment" "$agent" \
        "$run_number" "$model" "$prompt_sha" \
        "$input_tokens" "$output_tokens" "$total_tokens" \
        "$tool_tokens" "$planning_tokens" "$execution_tokens" \
        "$turns" "$backtracks" "$tool_calls_intent" "$tool_calls_other" \
        "$outcome" "$tests_total" "$tests_passed" "$tests_failed" \
        "$wall_clock" "$knowledge_entropy" \
        "results/raw/$experiment/$condition/$session_id" \
        "$SCORE_VERSION"

    # Preserve workdir for inspection
    rsync -a --exclude='node_modules' --exclude='.venv' --exclude='venv' \
        --exclude='__pycache__' --exclude='target' \
        "$workdir/" "$result_dir/workdir/"

    echo "  Outcome: $outcome | Tokens: $total_tokens | Time: ${wall_clock}s"
}

# Main run command
cmd_run() {
    local experiment="" condition="" runs=$DEFAULT_RUNS model=$DEFAULT_MODEL
    local treatment="" agent="" dry_run=0

    # Parse first positional arg as experiment name
    if [[ $# -gt 0 && ! "$1" =~ ^-- ]]; then
        experiment="$1"
        shift
    fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --condition)   condition="$2"; shift 2 ;;
            --treatment)   treatment="$2"; shift 2 ;;
            --agent)       agent="$2"; shift 2 ;;
            --runs)        runs="$2"; shift 2 ;;
            --model)       model="$2"; shift 2 ;;
            --dry-run)     dry_run=1; shift ;;
            *)             echo "Unknown option: $1" >&2; return 1 ;;
        esac
    done

    if [[ -z "$experiment" ]]; then
        echo "ERROR: Experiment name required" >&2
        usage
        return 1
    fi
    if [[ -z "$condition" ]]; then
        echo "ERROR: --condition required (control|treatment)" >&2
        return 1
    fi
    if [[ "$condition" != "control" && "$condition" != "treatment" ]]; then
        echo "ERROR: condition must be 'control' or 'treatment'" >&2
        return 1
    fi

    load_experiment "$experiment"

    # Override treatment/agent from CLI if specified
    treatment="${treatment:-$EXP_TREATMENT}"
    agent="${agent:-$EXP_AGENT}"

    if [[ $dry_run -eq 1 ]]; then
        echo "=== Dry Run ==="
        validate_experiment "$experiment"
        echo ""
        echo "Would run $runs sessions:"
        echo "  Condition: $condition"
        echo "  Treatment: $treatment"
        echo "  Agent: $agent"
        echo "  Model: $model"
        return 0
    fi

    # Ensure ledger exists
    if [[ ! -f "$LEDGER" ]]; then
        ledger_init "$LEDGER"
    fi

    trap cleanup_run EXIT INT TERM

    echo "=== intent-bench: $experiment ($condition, $treatment, $runs runs) ==="
    echo "Agent: $agent | Model: $model"
    echo ""

    for i in $(seq 1 "$runs"); do
        cleanup_orphans

        local workdir
        workdir=$(mktemp -d "/tmp/intent-bench-${experiment}-${condition}-XXXXXX")
        CURRENT_WORKDIR="$workdir"

        setup_workdir "$experiment" "$condition" "$treatment" "$workdir"
        execute_run "$experiment" "$condition" "$treatment" "$agent" "$i" "$model" "$workdir"

        rm -rf "$workdir"
        CURRENT_WORKDIR=""
    done

    trap - EXIT INT TERM

    echo ""
    echo "=== Complete: $runs runs recorded to $LEDGER ==="
}

# Dispatch
case "${1:-help}" in
    run)          shift; cmd_run "$@" ;;
    validate)     shift; validate_experiment "$@" ;;
    init-ledger)  ledger_init "$LEDGER" ;;
    help|--help)  usage ;;
    *)            echo "Unknown command: $1" >&2; usage; exit 1 ;;
esac
