# REQ-CLI-004: Edit Command

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

The `edit <id>` command updates one or more mutable fields of an existing item. Accepted flags are `--title`, `--tags`, and `--description`. At least one flag must be provided. Changes are persisted to the data store.

## Acceptance Criteria

1. `edit <id> --title "New title"` updates only the title and leaves all other fields unchanged.
2. `edit <id> --tags "go,cli"` replaces the item's tags with the normalized, deduplicated set.
3. `edit <id> --description "New desc"` updates only the description.
4. Multiple flags may be combined in a single invocation to update several fields at once.
5. `edit <id>` with no flags prints a usage error to stderr and exits with code 2.
6. `edit <id>` for an unknown ID prints an error message to stderr and exits with code 1.

## Dependencies

- REQ-CLI-001: Items must exist before they can be edited.

## Test

Module: `test_cli` | Function: `TestEdit` | Method: Integration Test
