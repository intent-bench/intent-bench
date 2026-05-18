# REQ-ENC-001: Fix omitempty with time.Time

## Requirement
Fix omitempty check to use IsZero() for time.Time and similar types.

## Acceptance Criteria
- Non-zero `time.Time` fields tagged `omitempty` are included in marshal output
- Zero `time.Time` fields tagged `omitempty` are correctly omitted
- Other types implementing `IsZero() bool` also work correctly
- Types without `IsZero()` continue to use the existing check

## Test
`TestOmitemptyTimeTime` in `yaml_test.go`
