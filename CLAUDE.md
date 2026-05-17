# CLAUDE.md

Agent guidance for working on the intent-bench codebase.

## Overview

intent-bench is an open-source benchmark measuring whether providing
structured intent (requirements, specifications, dependency ordering)
to coding agents improves implementation effectiveness. It uses a
controlled A/B design: agents receive identical prompts, but the
treatment condition additionally receives structured intent via a
pluggable treatment layer.

## Quick Commands

```bash
make setup        # Install Python dependencies
make validate     # Validate all experiment configs
make test         # Run harness and entropy tests
make gen-fixtures # Generate manual-spec fixtures from RTMX fixtures
make analyze      # Run statistical analysis on results
make charts       # Generate visualizations
```

## Architecture

```
bench.sh                 -- main harness (orchestrates runs)
agents/<name>.sh         -- agent wrappers (invoke coding agents)
treatments/<name>.sh     -- treatment plugins (seed intent artifacts)
lib/csv.sh               -- ledger schema and operations
lib/verify.sh            -- test outcome verification
lib/parse_transcript.py  -- token extraction from transcripts
entropy/agent_entropy.py -- knowledge entropy scorer
analysis/                -- statistical analysis and charts
experiments/             -- experiment YAML configs
prompts/                 -- task prompts (identical for both conditions)
fixtures/                -- treatment-specific fixture data
scripts/                 -- utility scripts (fixture generation)
```

## Key Design Decisions

1. Treatment plugins are shell scripts with a standard interface:
   `treatments/<name>.sh <setup|validate> <workdir> <experiment> <fixture_dir>`

2. Agent wrappers abstract the coding agent invocation:
   `agents/<name>.sh <workdir> <model> <prompt_file> <result_dir> <max_budget>`

3. The same prompt is used for both conditions. Treatment artifacts
   are seeded into the workdir, not injected into the prompt.

4. The ledger (results/summary.csv) is the single source of truth.
   It is append-only and schema-validated.

## Adding a Treatment

1. Create `treatments/<name>.sh` implementing setup and validate commands
2. Create fixture data in `fixtures/<name>/<experiment>/`
3. Reference it in experiment YAML: `treatment: <name>`

## Adding an Agent

1. Create `agents/<name>.sh` producing transcript.jsonl and stderr.log
2. Reference it in experiment YAML: `agent: <name>`

## Adding an Experiment

1. Create `experiments/<name>.yaml` with test_command, treatment, agent
2. Create `prompts/<name>.md` (must not reference any treatment tool)
3. Create fixture data for each treatment

## Impartiality Rules

- Prompts must never reference RTMX, MCP, RTM, or any treatment tool
- Manual-spec fixtures are generated programmatically from RTMX fixtures
  to ensure content parity (run `make gen-fixtures`)
- This repo does not use RTMX itself -- it evaluates RTMX as one treatment
