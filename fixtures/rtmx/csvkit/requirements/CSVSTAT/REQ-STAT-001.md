# REQ-STAT-001: Fix --names with --skip-lines

## Requirement
Fix --names to respect --skip-lines option.

## Acceptance Criteria
- `csvstat --names --skip-lines 2` reads column names from line 3 (after skipping 2)
- Other tools with --names also respect --skip-lines
- Without --skip-lines, behavior is unchanged

## Test
`test_names_skip_lines` in `test_csvstat.py`
