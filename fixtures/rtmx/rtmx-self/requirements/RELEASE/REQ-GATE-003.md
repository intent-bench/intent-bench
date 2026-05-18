# REQ-GATE-003: Empty Version Warning

## Requirement
Release gate shall exit 1 with warning when no requirements are assigned to the version.

## Acceptance Criteria
- When the sprint column has no rows matching the target version, print a warning
- Exit code is 1 (not 0 -- an unplanned version should not pass the gate)
- Warning message includes the version string

## Dependencies
- REQ-GATE-001

## Test
`TestReleaseGateEmpty` in `internal/cmd/release_test.go`
