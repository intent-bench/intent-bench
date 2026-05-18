# REQ-CLI-006: Search Command

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

The `search <query>` command performs a case-insensitive full-text search across item titles, descriptions, and content (URL or snippet text). All items whose stored text contains the query as a substring are returned.

## Acceptance Criteria

1. `search <query>` returns all items where the query string appears (case-insensitively) in the title, description, or content field.
2. Matches are partial: searching for "py" matches items containing "python" or "py script".
3. Results are displayed in the same table format as `list` by default; `--format json|csv` overrides the format.
4. `search <query>` with no matching items prints an empty result (not an error) and exits with code 0.
5. `search` with no query argument prints a usage error and exits with code 2.

## Dependencies

- REQ-CLI-001: Items must exist in the store before they can be searched.

## Test

Module: `test_cli` | Function: `TestSearch` | Method: Integration Test
