# Test-First Development

Pre-written tests are provided in `tests/`. Your task is to make all
tests pass by fixing bugs and adding features to hyperfine.

## Contract

The tests verify two bug fixes in outlier detection, a time unit
consistency fix, and a geometric mean feature addition.

## Approach

1. Read all tests first to understand the expected behavior
2. Study the existing statistical and display code paths
3. Implement fixes and features to satisfy the test assertions
4. Run `cargo test` to verify all tests pass
5. Do not modify the test files
