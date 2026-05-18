# REQ-STAT-001: Fix Zero MAD Division

## Requirement
Fix divide-by-zero when MAD is zero in outlier detection.

## Acceptance Criteria
- No panic or division by zero when all timing samples are identical
- When MAD is zero, outlier detection returns no outliers (all values are the same)
- Function handles single-sample input gracefully

## Test
`test_zero_mad` in `outlier_detection.rs`
