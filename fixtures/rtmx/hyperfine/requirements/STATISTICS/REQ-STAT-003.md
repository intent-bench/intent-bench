# REQ-STAT-003: Geometric Mean Calculation

## Requirement
Add geometric mean calculation to benchmark results.

## Acceptance Criteria
- Geometric mean is computed for all timing samples per command
- Displayed in the summary alongside mean, median, min, max
- Included in JSON export as `geometric_mean` field
- Handles edge cases: single sample, very small/large values

## Test
`test_geometric_mean` in `benchmark_result.rs`
