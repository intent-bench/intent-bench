# Test-First Development

Pre-written tests are provided in `tests/`. Your task is to make all
tests pass by fixing bugs in the go-yaml v3 library.

## Contract

The tests verify a parser crash fix, an omitempty bug with time.Time,
and a spurious quoting bug on boolean-like field names.

## Approach

1. Read all tests first to understand the expected behavior
2. Study the existing parser and encoder code paths
3. Implement fixes to satisfy the test assertions
4. Run `go test ./...` to verify all tests pass
5. Do not modify the test files
