# REQ-ENC-001: Array Table Indentation

## Requirement
Apply table indentation to array tables when SetIndentTables is true.

## Acceptance Criteria
- `SetIndentTables(true)` indents keys within `[[array_table]]` sections
- Indentation depth matches regular `[table]` indentation
- Default behavior (no indentation) is unchanged

## Test
`TestArrayTableIndent` in `toml_test.go`
