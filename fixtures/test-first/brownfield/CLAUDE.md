# Test-First Development

Pre-written tests are provided in `tests/brownfield_test.go`. Your task is to
make all tests pass by implementing the three features in the existing codebase.

## Contract

The tests call `buildSite(srcDir, outDir)` which must be wired to the
actual site generator's build function. You may need to adapt the test
helper to match the existing codebase's API.

## Approach

1. Read all tests to understand the three features (validation, RSS, tags)
2. Study the existing codebase to understand its architecture
3. Wire the `buildSite` function to the actual build entry point
4. Implement each feature, running `go test ./...` after each
5. Do not modify the test assertions, only the contract wiring
