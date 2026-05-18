# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-GATE-001: Release gate subcommand shall be registered under release parent command

**Phase:** 1

*Cobra subcommand scaffolding*

### Acceptance Criteria

- `rtmx release gate --help` prints usage information
- Command accepts a positional `<version>` argument
- Command follows existing Cobra patterns in the codebase

---

## 2. REQ-GATE-003: Release gate shall exit 1 with warning when no requirements assigned to version

**Phase:** 1

**Depends on:** REQ-GATE-001

*Edge case: unplanned version*

### Acceptance Criteria

- When the sprint column has no rows matching the target version, print a warning
- Exit code is 1 (not 0 -- an unplanned version should not pass the gate)
- Warning message includes the version string

---

## 3. REQ-GATE-002: Release gate shall filter requirements by sprint column matching target version

**Phase:** 1

**Depends on:** REQ-GATE-001

*Database query against sprint field*

### Acceptance Criteria

- Reads the CSV database and selects rows where `sprint` equals the target version
- Handles version strings with and without `v` prefix (e.g., `v0.3.0` and `0.3.0`)
- Returns the filtered set for status checking

---

## 4. REQ-GATE-007: All existing tests shall continue to pass after adding release gate

**Phase:** 1

*Must not break existing commands*

### Acceptance Criteria

- `go test ./...` exits 0
- No existing test functions are removed or modified
- New command does not interfere with existing commands

---

## 5. REQ-GATE-004: Release gate shall exit 0 when all assigned requirements are COMPLETE

**Phase:** 2

**Depends on:** REQ-GATE-002

*Happy path*

### Acceptance Criteria

- All requirements with `sprint` matching the target version have status COMPLETE
- Print a success message including the version and count of requirements
- Exit code is 0

---

## 6. REQ-GATE-005: Release gate shall exit 1 with table of incomplete requirements when any are not COMPLETE

**Phase:** 2

**Depends on:** REQ-GATE-002

*Primary value: blocks bad releases*

### Acceptance Criteria

- If any assigned requirement has status other than COMPLETE, print a table
- Table columns: ID, Status, Description
- Table is sorted by requirement ID
- Exit code is 1
- Message includes count of incomplete vs total

---

## 7. REQ-GATE-006: Release gate shall accept --json flag for machine-readable output

**Phase:** 3

**Depends on:** REQ-GATE-004, REQ-GATE-005

*CI integration support*

### Acceptance Criteria

- `--json` flag produces valid JSON to stdout
- JSON includes: version, pass (boolean), total count, incomplete count, list of requirements with id/status/description
- Non-JSON output is suppressed when --json is used

---
