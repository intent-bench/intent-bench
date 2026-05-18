# REQ-CLI-003: Show Command

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

The `show <id>` command displays the full details of a single item identified by its stable ID. It must distinguish between a valid item and an unknown ID.

## Acceptance Criteria

1. `show <id>` for a known ID displays all fields: id, type, title, url or content, tags, description, and creation timestamp.
2. `show <id>` for an unknown ID prints an error message to stderr and exits with code 1.
3. Output is human-readable and clearly labels each field.
4. The command accepts the same `--format` flag as `list` for machine-readable output.
5. Tags are displayed as a comma-separated list in the same normalized form they were stored.

## Dependencies

- REQ-CLI-001: Items must be added before they can be shown.

## Test

Module: `test_cli` | Function: `TestShow` | Method: Integration Test
