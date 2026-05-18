# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-CUT-001: Fix column selection when -l line numbers shifts column indices

**Phase:** 1

*Issue #1145: -l -c1 picks wrong column*

### Acceptance Criteria

- `csvcut -l -c 1` selects the first original column, not the line_number column
- `csvcut -l -c 1,2` selects the first two original columns
- `csvcut -l` alone still prepends the line_number column correctly
- Column names in `-c` also work correctly with `-l`

---

## 2. REQ-STAT-001: Fix --names to respect --skip-lines option

**Phase:** 1

**Depends on:** REQ-CUT-001

*Issue #951: --skip-lines ignored with --names*

### Acceptance Criteria

- `csvstat --names --skip-lines 2` reads column names from line 3 (after skipping 2)
- Other tools with --names also respect --skip-lines
- Without --skip-lines, behavior is unchanged

---

## 3. REQ-TEST-001: All existing tests continue to pass after changes

**Phase:** 1

*Must not break existing functionality*

### Acceptance Criteria

- `python -m pytest tests/` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing CSV processing

---

## 4. REQ-SORT-001: Add --ignore-case / -I flag for case-insensitive sorting

**Phase:** 2

**Depends on:** REQ-CUT-001

*Issue #1175: feature request analogous to sort -f*

### Acceptance Criteria

- `csvsort -c 1 -I` sorts data case-insensitively
- `csvsort -c 1 --ignore-case` is the long form
- Without the flag, default case-sensitive behavior is unchanged
- Mixed-case values like "Apple", "banana", "Cherry" sort correctly

---
