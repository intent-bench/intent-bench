# REQ-VALID-001: Front Matter Validation

## Requirement
Report error for invalid YAML front matter with filename and line number.

## Acceptance Criteria
- When a markdown file contains malformed YAML between `---` delimiters, the generator reports a clear error
- Error message includes the filename and approximate line number
- Processing stops for that file but continues for others
- Exit code is non-zero when errors are encountered

## Test
`TestInvalidFrontMatter` in `zs_test.go`
