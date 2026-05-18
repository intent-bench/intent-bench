# REQ-FMT-001: Output Formats

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

The `list` and `export` commands support three output formats: table (default), json, and csv. Each format must be well-formed and machine-parseable. No external table or serialization library is required; the implementation must produce correct output using the standard library.

## Acceptance Criteria

1. Table format renders column headers and rows with consistent alignment; columns are separated by at least one space and headers are visually distinct.
2. JSON format produces a valid JSON array where each element is an object with all item fields; the output passes a JSON schema validator.
3. CSV format produces a header row followed by one data row per item; all fields are correctly quoted when they contain commas, newlines, or quote characters.
4. `--format` is case-insensitive; `--format JSON` and `--format json` are equivalent.
5. An unrecognized format value prints an error to stderr and exits with code 2.

## Dependencies

- REQ-CLI-002: List command consumes this format logic.
- REQ-IO-001: Export command also consumes this format logic.

## Test

Module: `test_cli` | Function: `TestOutputFormats` | Method: Unit Test
