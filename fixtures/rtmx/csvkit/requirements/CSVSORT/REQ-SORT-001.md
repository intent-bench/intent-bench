# REQ-SORT-001: Case-Insensitive Sort

## Requirement
Add --ignore-case / -I flag for case-insensitive sorting.

## Acceptance Criteria
- `csvsort -c 1 -I` sorts data case-insensitively
- `csvsort -c 1 --ignore-case` is the long form
- Without the flag, default case-sensitive behavior is unchanged
- Mixed-case values like "Apple", "banana", "Cherry" sort correctly

## Test
`test_ignore_case` in `test_csvsort.py`
