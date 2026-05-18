# Test-First Development

Pre-written tests are provided in `tests/`. Your task is to make all
tests pass by fixing bugs and adding features to csvkit.

## Contract

The tests verify a column selection bug fix, a skip-lines interaction
fix, and a case-insensitive sort feature addition.

## Approach

1. Read all tests first to understand the expected behavior
2. Study the existing csvcut, csvstat, and csvsort implementations
3. Implement fixes and features to satisfy the test assertions
4. Run `python -m pytest tests/` to verify all tests pass
5. Do not modify the test files
