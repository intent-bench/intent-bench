# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-RENDER-001: Fix ConsoleRenderer mutating caller's level_styles dict

**Phase:** 1

*Issue #643: bold codes accumulate on reuse*

### Acceptance Criteria

- Constructing a ConsoleRenderer does not modify the passed-in level_styles dict
- Creating multiple renderers with the same dict does not cause style accumulation
- Default styles continue to work when no dict is passed

---

## 2. REQ-TEST-001: All existing tests continue to pass after changes

**Phase:** 1

*Must not break existing functionality*

### Acceptance Criteria

- `python -m pytest tests/` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing logging behavior

---

## 3. REQ-FILTER-001: Fix nop stub to accept *args and **kwargs for filtered levels

**Phase:** 2

**Depends on:** REQ-RENDER-001

*Issue #476: nop only accepts one positional arg*

### Acceptance Criteria

- `log.debug('hello %s', 'world')` does not raise TypeError when debug is filtered
- `log.debug('msg', key='value')` also works when filtered
- Filtered calls are still no-ops (no output produced)
- Non-filtered levels continue to work with interpolation

---

## 4. REQ-CTX-001: Fix KeyError in merge_contextvars on concurrent context deletion

**Phase:** 2

**Depends on:** REQ-FILTER-001

*Issue #591: race between iteration and lookup*

### Acceptance Criteria

- No KeyError when context variables are deleted during iteration
- merge_contextvars handles missing variables gracefully
- Existing context variables are still merged correctly

---
