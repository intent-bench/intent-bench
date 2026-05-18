# REQ-TAG-001: Tag List Command

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

The `tag list` subcommand displays all tags that appear across the item library along with the count of items carrying each tag. The output provides an at-a-glance summary of how the library is organized.

## Acceptance Criteria

1. `tag list` outputs one row per distinct tag showing the tag name and the number of items that carry it.
2. Tags are displayed in their normalized (lowercase) form.
3. Tags with zero items (orphaned by deletion or rename) do not appear in the output.
4. Output is sorted alphabetically by tag name by default.
5. `tag list` with no tags in the library prints an empty result and exits with code 0.

## Dependencies

- REQ-CLI-001: Tags originate from items added via the `add` command.

## Test

Module: `test_cli` | Function: `TestTagList` | Method: Integration Test
