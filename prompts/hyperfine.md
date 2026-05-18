# Task: Fix Bugs and Add Feature to a Rust Benchmarking Tool

You are working with hyperfine, a command-line benchmarking tool written
in Rust. Familiarize yourself with the codebase and complete the following
three tasks in order.

## Task A: Fix Divide-by-Zero in Outlier Detection (Small)

The outlier detection code in `src/outlier_detection.rs` has two bugs:

1. Division by zero when the MAD (Median Absolute Deviation) is zero,
   which happens when all timing samples are identical
2. A missing `abs()` call that causes roughly 50% of outliers to be
   missed (values below the median are never flagged)

Fix both issues and add tests for edge cases: identical samples,
outliers above and below the median.

## Task B: Fix Time Unit Consistency in User/System Display (Medium)

The `[User: X ms, System: Y ms]` display always uses milliseconds
regardless of the `--time-unit` flag. When the user specifies
`--time-unit second`, the mean/stddev/min/max use seconds but user
and system time still show milliseconds.

1. Find the display formatting for user and system time
2. Apply the same time unit conversion used for other statistics
3. Add tests verifying unit consistency

## Task C: Add Geometric Mean to Analysis Output (Medium)

Add a geometric mean calculation to the benchmark results:

1. Compute the geometric mean of all timing samples for each command
2. Display it alongside mean, median, min, max in the summary output
3. Include it in JSON export output under a `geometric_mean` field
4. Add tests verifying correct geometric mean calculation

## Success Criterion

All existing tests continue to pass, and all new tests pass when running
`cargo test`
