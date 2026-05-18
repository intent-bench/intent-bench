# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-STAT-001: Fix divide-by-zero when MAD is zero in outlier detection

**Phase:** 1

*Issue #329: division by zero when all samples equal*

### Acceptance Criteria

- No panic or division by zero when all timing samples are identical
- When MAD is zero, outlier detection returns no outliers (all values are the same)
- Function handles single-sample input gracefully

---

## 2. REQ-STAT-002: Fix missing abs() causing 50% of outliers to be missed

**Phase:** 1

**Depends on:** REQ-STAT-001

*Issue #329: only upper outliers detected*

### Acceptance Criteria

- Outliers below the median are detected (not just above)
- The modified z-score uses absolute deviation from median
- Tests verify outlier detection in both directions

---

## 3. REQ-TEST-001: All existing tests continue to pass after changes

**Phase:** 1

*Must not break existing functionality*

### Acceptance Criteria

- `cargo test` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing benchmarking behavior

---

## 4. REQ-DISP-001: Use consistent time unit for user/system time display

**Phase:** 2

**Depends on:** REQ-STAT-002

*Issue #408: always shows milliseconds*

### Acceptance Criteria

- When `--time-unit second` is specified, user and system times display in seconds
- When `--time-unit millisecond` is specified, user and system times display in milliseconds
- Default behavior (auto-detect) continues to work

---

## 5. REQ-STAT-003: Add geometric mean calculation to benchmark results

**Phase:** 2

**Depends on:** REQ-STAT-002

*Issue #759: feature request*

### Acceptance Criteria

- Geometric mean is computed for all timing samples per command
- Displayed in the summary alongside mean, median, min, max
- Included in JSON export as `geometric_mean` field
- Handles edge cases: single sample, very small/large values

---
