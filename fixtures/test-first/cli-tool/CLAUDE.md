# Test-First Development

Pre-written tests are provided in `tests/bm_test.py`. Your task is to
make all tests pass by implementing the bookmark/snippet manager CLI.

## Contract

The tests invoke the CLI via subprocess. They look for entry points in
this order: `main.py`, `app.py`, `cli.py`, `bm.py`, or `python -m bm`.

Tests use `XDG_CONFIG_HOME` and `BM_DATA_DIR` environment variables for
isolation. Your implementation must respect these for config and data paths.

## Approach

1. Read all tests first to understand the full CLI contract
2. Implement the CLI to satisfy the test assertions
3. Run `pytest tests/` to verify
4. Do not modify the test files
