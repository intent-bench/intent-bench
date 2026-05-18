# REQ-PARSE-001: Fix Parser Crash on Malformed Input

## Requirement
Fix nil pointer dereference on malformed YAML input.

## Acceptance Criteria
- Parsing `#\n-\n{` returns an error instead of panicking
- Other malformed inputs with comment/sequence combinations do not crash
- Valid YAML continues to parse correctly

## Test
`TestMalformedNoPanic` in `yaml_test.go`
