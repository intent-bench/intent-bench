# Test-First Development

Pre-written tests are provided in `tests/`. Your task is to make all
tests pass by fixing bugs in the go-toml library.

## Contract

The tests verify three bug fixes in the TOML decoder and encoder.
They import the library's public API and check behavior against
expected outputs.

## Approach

1. Read all tests first to understand the expected behavior
2. Study the existing decoder and encoder code paths
3. Implement fixes to satisfy the test assertions
4. Run `go test ./...` to verify all tests pass
5. Do not modify the test files
