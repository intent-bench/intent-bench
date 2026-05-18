# REQ-FILTER-001: Fix Filtered Log Interpolation

## Requirement
Fix nop stub to accept *args and **kwargs for filtered levels.

## Acceptance Criteria
- `log.debug('hello %s', 'world')` does not raise TypeError when debug is filtered
- `log.debug('msg', key='value')` also works when filtered
- Filtered calls are still no-ops (no output produced)
- Non-filtered levels continue to work with interpolation

## Test
`test_filtered_interpolation` in `test_filtering.py`
