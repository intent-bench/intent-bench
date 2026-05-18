# REQ-TAG-002: Tag Rename Command

## Status: MISSING
## Priority: MEDIUM
## Phase: 3

## Requirement

The `tag rename <old> <new>` subcommand replaces every occurrence of a tag across all items in the library. The rename is atomic from the user's perspective: after the command completes, no item carries the old tag name.

## Acceptance Criteria

1. `tag rename <old> <new>` replaces the old tag with the new tag on every item that carries it.
2. The new tag name is normalized to lowercase and deduplicated against existing tags on each item.
3. If an item already carries both the old and the new tag, the rename results in a single normalized tag (no duplicates).
4. `tag rename <old> <new>` where `<old>` does not exist prints an error to stderr and exits with code 1.
5. After a successful rename `tag list` no longer shows the old tag.

## Dependencies

- REQ-TAG-001: The tag must exist (visible in `tag list`) before it can be renamed.

## Test

Module: `test_cli` | Function: `TestTagRename` | Method: Integration Test
