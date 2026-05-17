# Methodology

## Hypothesis

Providing structured intent (requirements with dependency ordering,
acceptance criteria, and verification hooks) to coding agents reduces
knowledge entropy and increases task completion rate on complex
greenfield implementations.

## Design

### A/B with Blinding

- **Control:** Empty working directory + task prompt
- **Treatment:** Empty working directory + task prompt + intent artifacts

The prompt is identical in both conditions. The agent in the treatment
condition discovers intent artifacts (e.g., `.rtmx/` directory, MCP
server, or `REQUIREMENTS.md`) through its normal exploration behavior.
The prompt never mentions the treatment.

### Why Greenfield

Greenfield experiments isolate the effect of structured intent from
confounding factors present in brownfield tasks (existing code quality,
documentation coverage, test suite completeness). The agent must make
all architectural decisions from scratch, making planning overhead
and exploration waste maximally visible.

### Why Multiple Requirements

Single-requirement tasks (like HumanEval or SWE-bench bug fixes) are
too simple to exhibit the planning failures that structured intent
prevents. The threshold is approximately 8 requirements with 3+ levels
of dependency depth before agents begin to thrash.

## Metrics

### Primary

1. **Completion rate:** Fraction of runs where all tests pass (PASS outcome)
2. **Token efficiency:** Total tokens consumed (input + output) for PASS runs

### Secondary

3. **Knowledge entropy:** 0-10 composite score measuring agent process quality
4. **Variance (CV):** Coefficient of variation in tokens across runs
5. **Backtrack rate:** Fraction of turns re-reading previously read files

### Derived

6. **Token efficiency ratio:** mean(control_tokens) / mean(treatment_tokens)
7. **Variance reduction:** 1 - (treatment_CV / control_CV)
8. **Sustained productive turns:** Fraction of turns producing lasting output

## Statistical Methods

- **Token comparison:** Mann-Whitney U test (non-parametric, appropriate
  for small N and non-normal distributions)
- **Completion rate:** Fisher exact test (appropriate for 2x2 contingency
  tables with small counts)
- **Confidence intervals:** Bootstrap (10,000 iterations, seed=42)
- **Correlation:** Spearman rank correlation (entropy vs tokens)
- **Effect size:** Report ratio of means with 95% CI
- **Significance threshold:** p < 0.05

## Controls

1. **Prompt identity:** SHA-256 of prompt file recorded in ledger
2. **Model identity:** Exact model ID recorded per run
3. **No RTMX in prompt:** Automated validation rejects prompts with
   treatment references
4. **Budget cap:** Prevents runaway consumption from confounding results
5. **Language freedom:** Agent chooses implementation language freely
6. **Deterministic verification:** Test suite auto-detects language and
   framework

## Threats to Validity

### Internal

- **Agent non-determinism:** Token sampling introduces variance. Mitigated
  by N >= 5 per condition and reporting confidence intervals.
- **Model updates:** API models may change behavior between runs. Mitigated
  by recording exact model ID and running control/treatment in parallel.
- **Test quality:** Agent-written tests may be trivial. Mitigated by the
  test_command in experiment YAML running actual verification.

### External

- **Single agent:** Results with Claude Code may not generalize to other
  agents. Mitigated by agent abstraction allowing community reproduction.
- **Greenfield bias:** Results may not transfer to brownfield tasks.
  Advanced experiments test brownfield separately.
- **Treatment confounding:** RTMX provides both requirements structure
  AND an MCP server (tool calling overhead). The manual-spec treatment
  isolates the requirements-only effect.

## Interpretation Guidelines

- Baseline experiments (< 8 requirements): RTMX is expected to add
  overhead. A neutral or positive result here would be surprising.
- Standard experiments (8-20 requirements): This is the target
  complexity for efficacy claims.
- Report both positive and negative findings. Do not cherry-pick.
