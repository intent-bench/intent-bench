# REQ-DISP-001: Time Unit Consistency

## Requirement
Use consistent time unit for user/system time display.

## Acceptance Criteria
- When `--time-unit second` is specified, user and system times display in seconds
- When `--time-unit millisecond` is specified, user and system times display in milliseconds
- Default behavior (auto-detect) continues to work

## Test
`test_time_unit_consistency` in `benchmark_result.rs`
