# intent-bench

An open-source benchmark measuring whether providing structured intent
to coding agents improves implementation effectiveness.

## What This Measures

Existing agent benchmarks (SWE-bench, HumanEval, Aider Polyglot) test
single-requirement tasks or bug fixes. Real engineering involves
multi-requirement features with dependency ordering, cross-cutting
concerns, and state machines. intent-bench fills this gap.

**Research question:** Does providing structured requirements (with
dependency ordering, acceptance criteria, and verification hooks) to
a coding agent reduce token waste and increase task completion rate
on complex greenfield implementations?

## Design

intent-bench uses a controlled A/B design:

- **Control:** Agent receives only a task prompt in an empty directory
- **Treatment:** Agent receives the same prompt, plus structured intent
  artifacts seeded into the working directory

Both conditions use identical prompts. The treatment condition
additionally receives intent via a pluggable treatment layer (e.g.,
RTMX with MCP server, or a plain markdown specification file).

### Treatments

| Treatment | Description | Delivery |
|-----------|-------------|----------|
| `rtmx` | RTMX requirements database + MCP server | `.rtmx/` dir + MCP config |
| `manual-spec` | Plain markdown requirements file | `REQUIREMENTS.md` in workdir |

### Experiments

| Experiment | Complexity | Requirements | Depth |
|------------|-----------|--------------|-------|
| url-shortener | Baseline | 10 | 2 |
| task-manager | Standard | 13 | 5 |

## Quick Start

```bash
# Prerequisites: bash 4+, python3, Claude Code CLI
make setup

# Validate configuration
make validate

# Run a single experiment
bash bench.sh run url-shortener --condition control --runs 5
bash bench.sh run url-shortener --condition treatment --runs 5

# Analyze results
make analyze
make charts
```

## Results

Results are recorded in `results/summary.csv` (the data ledger).
Each row captures a complete session: token counts, outcome,
wall clock time, and knowledge entropy score.

Statistical analysis uses Mann-Whitney U for token comparison and
Fisher exact test for completion rate comparison, with bootstrap
confidence intervals.

## Metrics

| Metric | Description |
|--------|-------------|
| Completion rate | Fraction of runs where all tests pass |
| Total tokens | Input + output tokens consumed |
| Token efficiency ratio | Control tokens / Treatment tokens |
| Knowledge entropy | 0-10 score measuring agent process quality |
| Variance (CV) | Coefficient of variation across runs |
| Backtrack rate | Fraction of turns re-reading previously read files |

## Adding Treatments

Create `treatments/<name>.sh` with this interface:

```bash
# treatments/<name>.sh validate
#   Exit 0 if dependencies are met
# treatments/<name>.sh setup <workdir> <experiment> <fixture_dir>
#   Seed intent artifacts into workdir. Exit 0 = ready.
```

## Adding Agents

Create `agents/<name>.sh` with this interface:

```bash
# agents/<name>.sh <workdir> <model> <prompt_file> <result_dir> <max_budget>
#   Must produce: $result_dir/transcript.jsonl, $result_dir/stderr.log
#   Exit 0 = completed, non-zero = crashed
```

## Subject Selection Criteria

See [docs/subject-criteria.md](docs/subject-criteria.md) for what
qualifies as a valid experiment, complexity classifications, and
minimum sample size requirements.

## Reproducing Results

See [REPRODUCING.md](REPRODUCING.md) for exact commands, cost
estimates, and how to submit community results.

## Related Work

- SWE-bench: Single bug fixes in existing repos
- HumanEval: Single-function code generation
- Aider Polyglot: Multi-language refactoring
- ProjDevBench: Multi-file project development
- FeatureBench: Feature implementation
- SWE-EVO: Evolving complexity

intent-bench uniquely combines: greenfield multi-requirement tasks,
explicit dependency ordering, causal A/B design with blinding, and
pluggable intent delivery mechanisms.

## License

Apache 2.0
