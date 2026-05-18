# REQ-GATE-002: Version Requirement Filtering

## Requirement
Release gate shall filter requirements by sprint column matching target version.

## Acceptance Criteria
- Reads the CSV database and selects rows where `sprint` equals the target version
- Handles version strings with and without `v` prefix (e.g., `v0.3.0` and `0.3.0`)
- Returns the filtered set for status checking

## Dependencies
- REQ-GATE-001

## Test
`TestReleaseGateFilter` in `internal/cmd/release_test.go`
