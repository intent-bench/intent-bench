# REQ-DEC-002: Array Type Mismatch Error

## Requirement
Return error when TOML array type does not match Go target type.

## Acceptance Criteria
- Decoding a TOML string array into a Go `[]int` field returns a descriptive error
- Decoding a TOML int array into a Go `[]string` field returns a descriptive error
- Error message includes the expected and actual types
- Nested type mismatches are also caught

## Test
`TestArrayTypeMismatch` in `toml_test.go`
