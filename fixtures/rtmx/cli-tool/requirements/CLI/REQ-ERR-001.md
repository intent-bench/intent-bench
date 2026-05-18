# REQ-ERR-001: Exit Codes

## Status: MISSING
## Priority: HIGH
## Phase: 1

## Requirement

All commands must use a consistent, documented set of exit codes so that callers and shell scripts can reliably detect success, runtime errors, and usage errors without parsing output text.

## Acceptance Criteria

1. Every command exits with code 0 when it completes successfully.
2. Every command exits with code 1 when it encounters a runtime error (item not found, I/O failure, data corruption).
3. Every command exits with code 2 when the invocation is invalid (missing required argument, unrecognized flag, wrong number of arguments).
4. Error details are written to stderr; normal output is written to stdout so callers can redirect them independently.
5. `--help` on any command or subcommand exits with code 0.

## Dependencies

None. This is a foundational CLI contract that applies to all commands.

## Test

Module: `test_cli` | Function: `TestExitCodes` | Method: Unit Test
