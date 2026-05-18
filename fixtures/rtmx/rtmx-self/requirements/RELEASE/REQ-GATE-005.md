# REQ-GATE-005: Gate Fail

## Requirement
Release gate shall exit 1 with table of incomplete requirements when any are not COMPLETE.

## Acceptance Criteria
- If any assigned requirement has status other than COMPLETE, print a table
- Table columns: ID, Status, Description
- Table is sorted by requirement ID
- Exit code is 1
- Message includes count of incomplete vs total

## Dependencies
- REQ-GATE-002

## Test
`TestReleaseGateFail` in `internal/cmd/release_test.go`
