# REQ-GATE-001: Release Gate Command Registration

## Requirement
Release gate subcommand shall be registered under the release parent command.

## Acceptance Criteria
- `rtmx release gate --help` prints usage information
- Command accepts a positional `<version>` argument
- Command follows existing Cobra patterns in the codebase

## Test
`TestReleaseGateHelp` in `internal/cmd/release_test.go`
