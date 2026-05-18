# REQ-CUT-001: Fix Column Selection with Line Numbers

## Requirement
Fix column selection when -l line numbers shifts column indices.

## Acceptance Criteria
- `csvcut -l -c 1` selects the first original column, not the line_number column
- `csvcut -l -c 1,2` selects the first two original columns
- `csvcut -l` alone still prepends the line_number column correctly
- Column names in `-c` also work correctly with `-l`

## Test
`test_line_number_column_select` in `test_csvcut.py`
