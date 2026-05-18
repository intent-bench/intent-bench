# Task: Fix Bugs in a Python Structured Logging Library

You are working with structlog, a structured logging library for Python.
Familiarize yourself with the codebase and fix the following three bugs
in order.

## Task A: Fix ConsoleRenderer Mutating Caller's Style Dict (Small)

`ConsoleRenderer.__init__` mutates the caller's `level_styles` dict
in place by appending bold escape codes each time it is constructed.
If the same dict is reused, styles accumulate with each instantiation.

1. Find where `level_styles` is modified in `ConsoleRenderer.__init__`
2. Fix by deep-copying the dict before modifying it
3. Add tests: create two renderers sharing a style dict, verify the
   original dict is not modified

## Task B: Fix Filtered Log Interpolation Error (Medium)

`make_filtering_bound_logger` generates nop stubs for filtered log
levels. The nop function only accepts one positional argument (the
event string), so calls like `log.debug('hello %s', 'world')` raise
`TypeError` when debug is filtered out.

1. Find the nop stub generator in `make_filtering_bound_logger`
2. Fix the nop signature to accept `*args, **kwargs`
3. Add tests: create a logger with debug filtered, call
   `log.debug('msg %s', 'arg')` and verify no error is raised

## Task C: Fix KeyError in merge_contextvars (Medium)

`merge_contextvars` iterates over a context snapshot but can raise
`KeyError` when looking up context variables that were deleted between
the iteration start and the lookup. This is a race condition with
concurrent context modifications.

1. Find the iteration logic in `merge_contextvars`
2. Fix by using `.get()` with a sentinel or catching `KeyError`
3. Add tests simulating the race condition

## Success Criterion

All existing tests continue to pass, and all new tests pass when running
`python -m pytest tests/`
