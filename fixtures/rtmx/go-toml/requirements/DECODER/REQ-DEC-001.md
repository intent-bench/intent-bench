# REQ-DEC-001: Slice Reset on Unmarshal

## Requirement
Reset slice fields before unmarshaling array of tables.

## Acceptance Criteria
- When unmarshaling `[[array_of_tables]]` into a struct with a pre-populated slice, existing elements are cleared
- The slice contains only elements from the TOML input after unmarshal
- Non-slice fields are unaffected by this change

## Test
`TestSliceReset` in `toml_test.go`
