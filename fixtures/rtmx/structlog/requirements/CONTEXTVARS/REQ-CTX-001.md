# REQ-CTX-001: Fix KeyError in merge_contextvars

## Requirement
Fix KeyError in merge_contextvars on concurrent context deletion.

## Acceptance Criteria
- No KeyError when context variables are deleted during iteration
- merge_contextvars handles missing variables gracefully
- Existing context variables are still merged correctly

## Test
`test_merge_concurrent_delete` in `test_contextvars.py`
