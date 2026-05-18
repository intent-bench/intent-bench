# REQ-IO-001: Export Command

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

The `export` command writes all items in the library to stdout or a specified file in the requested format. The output is suitable for archiving, migration, or ingestion by other tools. Supported formats are json and csv.

## Acceptance Criteria

1. `export --format json` writes a valid JSON array of all items to stdout.
2. `export --format csv` writes a valid CSV file with a header row and one row per item to stdout.
3. `export --format <fmt> --output <file>` writes output to the specified file path instead of stdout.
4. An export of an empty library produces a valid empty structure (empty JSON array `[]` or CSV header row only), not an error.
5. `export` with an unrecognized format value prints an error to stderr and exits with code 2.

## Dependencies

- REQ-FMT-001: Export reuses the shared format rendering logic.

## Test

Module: `test_cli` | Function: `TestExport` | Method: Integration Test
