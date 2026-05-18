# Task: Fix Bugs in a Go TOML Library

You are working with go-toml v2, a widely-used Go TOML parser and encoder.
Familiarize yourself with the codebase and fix the following three bugs
in order.

## Task A: Fix Slice Reset on Unmarshal (Small)

When unmarshaling an array of tables (`[[Slice]]`) into a Go struct that
already has a pre-populated slice field, the existing elements are not
cleared. Instead, new elements are appended to the existing slice.

1. The decoder should reset slice fields before populating them from TOML
2. This applies to `[[array_of_tables]]` syntax
3. Add tests demonstrating the fix: unmarshal into a pre-populated struct
   and verify old elements are gone

## Task B: Fix Encoder Indentation for Array Tables (Medium)

`SetIndentTables(true)` correctly indents regular `[table]` entries but
has no effect on array tables (`[[array_table]]`). The encoder's array
table emission path does not apply the configured indentation.

1. Find the encoder's array table emit path
2. Apply the same indentation logic used for regular tables
3. Add tests comparing output with and without `SetIndentTables(true)`
   for array tables

## Task C: Report Error on Array Type Mismatches (Medium)

When a TOML array is decoded into an incompatible Go type (e.g., a TOML
array of strings into an `int` field), the library silently succeeds
instead of returning a descriptive error.

1. Find the type-checking path in the decoder
2. Return a clear error when the TOML value type does not match the
   target Go type
3. Add tests for several mismatch scenarios: string array into int,
   int into string, nested type mismatches

## Success Criterion

All existing tests continue to pass, and all new tests pass when running
`go test ./...`
