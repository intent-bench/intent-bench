# REQ-CLI-005: Delete Command

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

The `delete <id>` command permanently removes an item from the data store. Deletion requires explicit confirmation to prevent accidental data loss. In non-interactive mode the `--confirm` flag must be supplied; in interactive mode the user may confirm via a prompt.

## Acceptance Criteria

1. `delete <id> --confirm` removes the item and exits with code 0.
2. `delete <id>` without `--confirm` in a non-interactive context prints an error and exits with code 1 without modifying the store.
3. `delete <id>` for an unknown ID prints an error to stderr and exits with code 1.
4. After successful deletion the item no longer appears in `list` or `show` output.
5. The deleted item's ID is not reused for subsequently added items.

## Dependencies

- REQ-CLI-001: Items must exist before they can be deleted.

## Test

Module: `test_cli` | Function: `TestDelete` | Method: Integration Test
