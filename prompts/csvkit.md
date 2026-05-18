# Task: Fix Bugs and Add Feature to a Python CSV Toolkit

You are working with csvkit, a suite of command-line tools for working
with CSV data. Familiarize yourself with the codebase and complete the
following three tasks in order.

## Task A: Fix Column Selection with Line Numbers (Small)

When using `csvcut` with both `-l` (add line numbers) and `-c 1`
(select first column), the line number column shifts the index so `-c 1`
selects the wrong column. The synthetic `line_number` column should not
be counted when resolving the `-c` column index.

1. Find where line numbers are inserted in csvcut
2. Fix the column selection logic so `-c` indices refer to the original
   columns, not the shifted ones
3. Add tests for `-l -c1`, `-l -c1,2`, and `-l` alone

## Task B: Fix --skip-lines with --names (Medium)

`csvstat --names --skip-lines N` ignores the `--skip-lines` option and
always reads column names from the first line. The `--names` code path
needs to apply `--skip-lines` before reading the header row.

1. Find the `--names` code path in csvstat (and potentially other tools)
2. Apply skip-lines before reading column names
3. Add tests verifying that `--names` respects `--skip-lines`

## Task C: Add Case-Insensitive Sort to csvsort (Medium)

Add a `--ignore-case` / `-I` flag to `csvsort` that performs
case-insensitive sorting, analogous to `sort -f` in Unix.

1. Add the `-I` / `--ignore-case` flag to the csvsort argument parser
2. Implement case-insensitive comparison in the sort logic
3. Add tests verifying case-insensitive sort order with mixed-case data

## Success Criterion

All existing tests continue to pass, and all new tests pass when running
`python -m pytest tests/`
