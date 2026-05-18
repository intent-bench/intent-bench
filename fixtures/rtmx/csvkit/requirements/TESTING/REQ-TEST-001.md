# REQ-TEST-001: Regression Safety

## Requirement
All existing tests continue to pass after changes.

## Acceptance Criteria
- `python -m pytest tests/` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing CSV processing

## Test
`python -m pytest tests/`
