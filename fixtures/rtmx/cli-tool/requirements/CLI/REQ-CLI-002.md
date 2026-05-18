# REQ-CLI-002: List Command

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

The `list` command displays all stored items and supports filtering by type and tag. Output format is controlled by the `--format` flag (table, json, csv), defaulting to table. Filters may be combined.

## Acceptance Criteria

1. `list` with no flags displays all items in table format with aligned columns and headers.
2. `--type bookmark` or `--type snippet` restricts output to items of that type.
3. `--tag <tag>` restricts output to items that carry the specified tag.
4. `--format json` produces valid JSON; `--format csv` produces valid CSV with a header row.
5. `--type` and `--tag` may be combined to filter by both type and tag simultaneously.

## Dependencies

- REQ-CLI-001: Items must exist in the store before listing.
- REQ-FMT-001: Output format logic is shared with the export command.

## Test

Module: `test_cli` | Function: `TestList` | Method: Integration Test
