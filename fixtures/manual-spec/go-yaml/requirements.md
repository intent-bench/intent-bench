# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-PARSE-001: Fix nil pointer dereference on malformed YAML input

**Phase:** 1

*Issue #855: panic on certain comment/sequence combos*

### Acceptance Criteria

- Parsing `#\n-\n{` returns an error instead of panicking
- Other malformed inputs with comment/sequence combinations do not crash
- Valid YAML continues to parse correctly

---

## 2. REQ-TEST-001: All existing tests continue to pass after changes

**Phase:** 1

*Must not break existing functionality*

### Acceptance Criteria

- `go test ./...` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing YAML parsing or encoding

---

## 3. REQ-ENC-001: Fix omitempty check to use IsZero() for time.Time and similar types

**Phase:** 2

**Depends on:** REQ-PARSE-001

*Issue #244: time.Time always omitted*

### Acceptance Criteria

- Non-zero `time.Time` fields tagged `omitempty` are included in marshal output
- Zero `time.Time` fields tagged `omitempty` are correctly omitted
- Other types implementing `IsZero() bool` also work correctly
- Types without `IsZero()` continue to use the existing check

---

## 4. REQ-ENC-002: Remove spurious quotes on boolean-like field names in struct marshal

**Phase:** 2

**Depends on:** REQ-PARSE-001

*Issue #1020: y and n quoted but x is not*

### Acceptance Criteria

- Field names `y`, `n`, `Y`, `N`, `yes`, `no` are not quoted when used as map keys
- Marshaling `image.Point{X: 4, Y: 5}` produces `x: 4\ny: 5` without quotes
- Boolean values (not keys) are still handled correctly
- YAML 1.1 boolean-like strings in value position continue to be quoted where needed

---
