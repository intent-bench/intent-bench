# Task: Fix Bugs in a Go YAML Library

You are working with go-yaml v3, the standard YAML library for Go.
Familiarize yourself with the codebase and fix the following three bugs
in order.

## Task A: Fix Parser Crash on Malformed Input (Small)

Parsing certain malformed YAML sequences causes a nil pointer
dereference panic. For example, the input `#\n-\n{` crashes the parser
in the comment-splitting logic.

1. Find the nil pointer dereference in the parser
2. Add a nil guard to prevent the crash
3. Add tests with several malformed inputs that should return errors
   instead of panicking

## Task B: Fix omitempty with time.Time (Medium)

Fields of type `time.Time` tagged with `omitempty` are always omitted
from the output, even when the time value is non-zero. The isEmpty
check uses `reflect.DeepEqual` against the zero value, but `time.Time`
has an `IsZero()` method that should be used instead.

1. Find the omitempty check in the encoder
2. Add support for types that implement an `IsZero() bool` method
3. Add tests verifying that non-zero `time.Time` values are marshaled
   and zero values are omitted

## Task C: Fix Spurious Quoting of Boolean-like Field Names (Medium)

When marshaling a Go struct, field names that happen to be legacy YAML
boolean strings (`y`, `n`, `Y`, `N`, `yes`, `no`, etc.) are emitted
with unnecessary quotes. For example, `image.Point{X: 4, Y: 5}`
produces `x: 4` but `"y": 5` with quotes around `y`.

1. Find the string-quoting logic in the emitter
2. Fix it so that map keys / field names that are boolean-like strings
   are not quoted (they are unambiguous as keys)
3. Add tests for several boolean-like field names

## Success Criterion

All existing tests continue to pass, and all new tests pass when running
`go test ./...`
