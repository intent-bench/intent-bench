# REQ-CFG-002: Config Set and Show Commands

## Status: MISSING
## Priority: MEDIUM
## Phase: 2

## Requirement

The `config show` command displays the current configuration and the `config set <key> <value>` command updates a single configuration key. Changes made via `config set` are immediately persisted to the config file and take effect on the next invocation.

## Acceptance Criteria

1. `config show` prints all current configuration keys and their values in a human-readable format.
2. `config set format json` updates the `format` key and persists the change to the config file.
3. `config set color false` updates the `color` key; subsequent commands respect the new value.
4. `config set <unknown-key> <value>` prints an error to stderr and exits with code 1 without modifying the config file.
5. `config set` with missing key or value arguments prints a usage error and exits with code 2.

## Dependencies

- REQ-CFG-001: The config file must be initialized before values can be read or set.

## Test

Module: `test_cli` | Function: `TestConfigSetShow` | Method: Integration Test
