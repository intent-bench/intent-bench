# REQ-GATE-006: JSON Output

## Requirement
Release gate shall accept --json flag for machine-readable output.

## Acceptance Criteria
- `--json` flag produces valid JSON to stdout
- JSON includes: version, pass (boolean), total count, incomplete count, list of requirements with id/status/description
- Non-JSON output is suppressed when --json is used

## Dependencies
- REQ-GATE-004, REQ-GATE-005

## Test
`TestReleaseGateJSON` in `internal/cmd/release_test.go`
