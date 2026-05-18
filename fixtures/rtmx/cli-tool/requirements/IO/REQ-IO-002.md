# REQ-IO-002: Import Command

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

The `import <file>` command reads items from a JSON or CSV file and adds them to the library. The file format is auto-detected from the file extension or content. Imported items receive new stable IDs; original IDs in the import file are not preserved.

## Acceptance Criteria

1. `import <file.json>` reads a JSON array of item objects and adds each as a new item with a freshly assigned ID.
2. `import <file.csv>` reads a CSV file with a header row and adds each data row as a new item.
3. Items imported from a valid export file (produced by REQ-IO-001) round-trip correctly: all fields are preserved.
4. `import <file>` where the file does not exist prints an error to stderr and exits with code 1.
5. `import <file>` where the file is malformed (invalid JSON or CSV) prints a descriptive error to stderr and exits with code 1 without adding partial data.

## Dependencies

- REQ-IO-001: The import format mirrors the export format; a round-trip export then import must be lossless.

## Test

Module: `test_cli` | Function: `TestImport` | Method: Integration Test
