# REQ-STAT-002: Fix Outlier Detection Direction

## Requirement
Fix missing abs() causing 50% of outliers to be missed.

## Acceptance Criteria
- Outliers below the median are detected (not just above)
- The modified z-score uses absolute deviation from median
- Tests verify outlier detection in both directions

## Test
`test_outlier_both_sides` in `outlier_detection.rs`
