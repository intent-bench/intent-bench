# Reproducing Results

## Prerequisites

- macOS or Linux (bash 4+)
- Python 3.10+
- Claude Code CLI (`claude`) installed and authenticated
- For RTMX treatment: `rtmx` binary on PATH

## Cost Estimates

Per experiment, per condition, for N=5 runs:

| Experiment | Model | Estimated Cost |
|------------|-------|---------------|
| url-shortener | claude-sonnet-4 | ~$15-25 |
| task-manager | claude-sonnet-4 | ~$30-50 |

Total for a full run (2 experiments x 2 conditions x 5 runs): ~$90-150

## Setup

```bash
git clone https://github.com/intent-bench/intent-bench.git
cd intent-bench
make setup
make validate
```

## Running Experiments

### Full benchmark (all experiments, both conditions)

```bash
make run-all
```

### Individual experiment

```bash
# Control condition (no intent layer)
bash bench.sh run task-manager --condition control --runs 5

# Treatment condition (RTMX)
bash bench.sh run task-manager --condition treatment --runs 5 --treatment rtmx

# Treatment condition (manual spec)
bash bench.sh run task-manager --condition treatment --runs 5 --treatment manual-spec
```

### Options

```bash
--model <id>           # Model ID (default: claude-sonnet-4-20250514)
--runs <N>             # Number of runs (default: 5, minimum 5 for claims)
--treatment <name>     # Treatment plugin (default: from experiment yaml)
--agent <name>         # Agent wrapper (default: claude-code)
--dry-run              # Validate without running
```

## Analysis

```bash
make analyze    # Statistical comparison (results/analysis.json)
make charts     # Generate visualizations (results/charts/)
```

## Submitting Community Results

We welcome reproduction attempts. To submit results:

1. Run the benchmark with the exact commands above
2. Include your `results/summary.csv` and `results/analysis.json`
3. Report: model ID, date of runs, N per condition, any deviations
4. Open a discussion on this repo with your findings

## Verification

```bash
# Validate ledger schema
bash lib/csv.sh validate results/summary.csv

# Re-generate manual-spec fixtures (verify impartiality)
make gen-fixtures
git diff fixtures/manual-spec/  # should show no changes
```
