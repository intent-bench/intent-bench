# Test-First Development

Pre-written tests are provided in `tests/bookstore_test.py`. Your task is to
make all tests pass by implementing the bookstore REST API.

## Contract

The tests expect `from app import create_app` or `from main import create_app`
returning a Flask or FastAPI application with `create_app(testing=True)`.

## Approach

1. Read all tests first to understand the full API contract
2. Implement the application to satisfy the test assertions
3. Run `pytest tests/` to verify
4. Do not modify the test files
