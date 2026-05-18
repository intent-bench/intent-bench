# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-DEC-001: Reset slice fields before unmarshaling array of tables

**Phase:** 1

*Issue #931: slices appended instead of reset*

### Acceptance Criteria

- When unmarshaling `[[array_of_tables]]` into a struct with a pre-populated slice, existing elements are cleared
- The slice contains only elements from the TOML input after unmarshal
- Non-slice fields are unaffected by this change

---

## 2. REQ-TEST-001: All existing tests continue to pass after changes

**Phase:** 1

*Must not break existing functionality*

### Acceptance Criteria

- `go test ./...` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing TOML parsing or encoding

---

## 3. REQ-DEC-002: Return error when TOML array type does not match Go target type

**Phase:** 2

**Depends on:** REQ-DEC-001

*Issue #799: silent success on incompatible types*

### Acceptance Criteria

- Decoding a TOML string array into a Go `[]int` field returns a descriptive error
- Decoding a TOML int array into a Go `[]string` field returns a descriptive error
- Error message includes the expected and actual types
- Nested type mismatches are also caught

---

## 4. REQ-ENC-001: Apply table indentation to array tables when SetIndentTables is true

**Phase:** 2

*Issue #888: indent ignored for [[array]]*

### Acceptance Criteria

- `SetIndentTables(true)` indents keys within `[[array_table]]` sections
- Indentation depth matches regular `[table]` indentation
- Default behavior (no indentation) is unchanged

---
