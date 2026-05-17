# Subject Selection Criteria

This document defines what qualifies as a valid rtmx-bench experiment.
All experiments must meet these criteria to produce credible, reproducible
results. The criteria exist to prevent cherry-picking and ensure that
positive or negative findings reflect genuine signal.

## Complexity Classification

Each experiment is classified by the complexity of its requirement graph.
This classification determines how results are interpreted.

### Baseline (overhead measurement)

- Fewer than 8 requirements
- Dependency depth less than 3 levels
- Purpose: measure the cost of RTMX tool interaction overhead
- Example: url-shortener (5 requirements, depth 1)
- Interpretation: RTMX is expected to add overhead here. If it does not,
  that is a surprising positive result. If it does, that is the expected
  cost of structured planning on a trivially-sized task.

### Standard (primary efficacy measurement)

- 8 to 20 requirements
- Dependency depth 3 to 5 levels
- At least 2 cross-cutting concerns (e.g., auth + validation + logging)
- Purpose: measure whether RTMX improves completion rate and reduces
  outcome variability on tasks complex enough to cause agent thrashing
- Example: task-manager (15 requirements, depth 5, 6 entities)
- Interpretation: this is the target complexity for RTMX value claims.

### Advanced (stress test)

- More than 20 requirements, or brownfield against an existing codebase
- Purpose: test scaling limits and amortization of planning overhead
- Example: brownfield (3 incremental tasks against an existing Go repo),
  rtmx-self (implement a real feature in the RTMX CLI itself)
- Interpretation: results here are exploratory, not used for primary claims.

## Required Properties

Every experiment must satisfy all of the following:

1. **Language-agnostic prompt**: The prompt must not specify an
   implementation language. The agent chooses freely. This prevents
   confounding language skill with RTMX efficacy.

2. **No RTMX references in prompt**: The prompt must not mention RTMX,
   RTM, MCP, or requirements traceability. The treatment condition
   receives RTMX via the seeded `.rtmx/` directory and MCP server, not
   via the prompt. This maintains blinding between conditions.

3. **Deterministic test verification**: The experiment must define a
   `test_command` that auto-detects the language and framework, runs
   tests, and produces parseable pass/fail output. The harness supports:
   Go, Rust, Python (pytest), Node.js (Jest, Mocha, Vitest, Bun), TAP,
   and generic checkmark/summary formats.

4. **Budget cap**: The experiment YAML must include `max_budget_usd`.
   This prevents runaway token consumption and ensures comparable cost
   across runs. Recommended: $5 for baseline, $10 for standard, $20
   for advanced.

5. **Prompt SHA-256 in ledger**: The ledger records the SHA-256 of the
   prompt file for each run. If the prompt changes, old and new results
   are not directly comparable.

6. **Reproducible starting state**: Greenfield experiments start from an
   empty directory. Brownfield experiments must pin a specific commit SHA
   in the experiment YAML. No moving targets.

7. **Self-contained tests**: Tests must set up and tear down their own
   state (databases, files, servers). No external service dependencies.

## Disqualifying Factors

An experiment is invalid if any of the following apply:

- Prompt contains RTMX, RTM, MCP, or requirements traceability references
- Requires external services that cannot be bootstrapped locally
  (cloud databases, third-party APIs requiring credentials)
- Test suite is non-deterministic (flaky tests that sometimes pass,
  sometimes fail on identical code)
- Single run exceeds 30 minutes wall clock (impractical for N >= 5)
- Treatment fixture (RTM database) does not match the prompt requirements
  (requirement IDs must map to actual prompt specifications)

## Minimum Sample Size

- N >= 5 per condition (control and treatment) for any published claim
- N >= 10 per condition recommended for statistical significance
- Mann-Whitney U test for token comparison; Fisher exact test for
  completion rate comparison
- Report p-values, confidence intervals, and effect sizes alongside
  point estimates

## Result Reporting Standards

When publishing results from rtmx-bench:

1. **Report both positive and negative findings.** If RTMX adds overhead
   on baseline experiments, report that alongside efficacy on standard
   experiments.

2. **State the exact scope.** Agent name, model ID, N per condition,
   date of runs. Do not generalize beyond the tested configuration.

3. **Link to raw data.** Point to the ledger CSV and methodology docs
   so others can verify the analysis.

4. **Invite reproduction.** Include a link to the reproduction guide
   and encourage others to run the benchmark with different agents
   and models.
