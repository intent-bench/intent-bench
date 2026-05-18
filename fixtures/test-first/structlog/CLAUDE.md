# Test-First Development

Pre-written tests are provided in `tests/`. Your task is to make all
tests pass by fixing bugs in structlog.

## Contract

The tests verify a style dict mutation fix, a filtered log interpolation
error fix, and a race condition fix in contextvars.

## Approach

1. Read all tests first to understand the expected behavior
2. Study the existing ConsoleRenderer, filtering, and contextvars code
3. Implement fixes to satisfy the test assertions
4. Run `python -m pytest tests/` to verify all tests pass
5. Do not modify the test files
