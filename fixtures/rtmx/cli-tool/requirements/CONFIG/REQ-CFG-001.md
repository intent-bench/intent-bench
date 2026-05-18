# REQ-CFG-001: Config File Initialization

## Status: MISSING
## Priority: HIGH
## Phase: 1

## Requirement

On the first run, if no configuration file is present, the tool creates one at the XDG-compliant location (`$XDG_CONFIG_HOME/bm/config.yaml`, defaulting to `~/.config/bm/config.yaml`) populated with default values. Subsequent runs read from this file without recreating it.

## Acceptance Criteria

1. If `~/.config/bm/config.yaml` (or the XDG override path) does not exist, running any command creates it with default values before proceeding.
2. The default config contains at minimum: `format: table`, `color: true`, and `data_file` pointing to the default data store path.
3. If `XDG_CONFIG_HOME` is set, the config file is created under that directory rather than `~/.config`.
4. The config file is valid YAML and can be opened and edited by hand.
5. If the config directory does not exist, it is created with appropriate permissions (0700 or 0755).

## Dependencies

None. This is the foundational configuration layer required by REQ-CFG-002.

## Test

Module: `test_cli` | Function: `TestConfigInit` | Method: Unit Test
