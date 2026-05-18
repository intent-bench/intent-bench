# REQ-CLI-001: Add Command

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

The `add` command accepts a URL or free-text snippet as its positional argument and auto-detects the item type. It stores the item with correct type metadata and supports optional `--title`, `--tags`, and `--description` flags.

## Acceptance Criteria

1. `add <url>` where the argument starts with `http://` or `https://` stores the item as type `bookmark`.
2. `add <text>` where the argument is not a URL stores the item as type `snippet`.
3. `--title`, `--tags`, and `--description` flags are accepted and stored with the item.
4. Tags are comma-separated, normalized to lowercase, and deduplicated before storage.
5. Each stored item receives a stable, unique ID (incrementing integer or UUID) that does not change on subsequent runs.

## Dependencies

None. This is the foundational write operation required by REQ-CLI-002, REQ-CLI-003, REQ-CLI-005, and REQ-TAG-001.

## Test

Module: `test_cli` | Function: `TestAdd` | Method: Integration Test
