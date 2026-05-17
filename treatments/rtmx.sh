#!/usr/bin/env bash
# rtmx.sh -- RTMX treatment plugin for intent-bench
# Seeds a working directory with RTMX requirements traceability artifacts
# and MCP server configuration.
#
# Usage: rtmx.sh setup <workdir> <experiment> <fixture_dir>
#
# Contract:
#   - Exit 0 = treatment ready
#   - Exit 1 = fatal setup error
#   - Must not modify anything outside $workdir
#   - Requires rtmx binary on $PATH
set -euo pipefail

cmd="${1:?Usage: rtmx.sh <setup|validate> <workdir> <experiment> <fixture_dir>}"

case "$cmd" in
    validate)
        if ! command -v rtmx >/dev/null 2>&1; then
            echo "ERROR: rtmx binary not found on PATH" >&2
            exit 1
        fi
        echo "rtmx treatment: OK ($(rtmx --version 2>/dev/null || echo 'unknown version'))"
        exit 0
        ;;
    setup)
        ;;
    *)
        echo "ERROR: Unknown subcommand: $cmd" >&2
        exit 1
        ;;
esac

workdir="${2:?workdir required}"
experiment="${3:?experiment name required}"
fixture_dir="${4:?fixture_dir required}"

# Validate binary
if ! command -v rtmx >/dev/null 2>&1; then
    echo "ERROR: rtmx binary not found (required for RTMX treatment)" >&2
    exit 1
fi

# Validate fixture
if [[ ! -d "$fixture_dir" ]]; then
    echo "ERROR: Fixture directory not found: $fixture_dir" >&2
    exit 1
fi
if [[ ! -f "$fixture_dir/rtm.csv" ]]; then
    echo "ERROR: Fixture missing rtm.csv: $fixture_dir/rtm.csv" >&2
    exit 1
fi

# Seed RTMX artifacts
mkdir -p "$workdir/.rtmx"
cp "$fixture_dir/rtm.csv" "$workdir/.rtmx/database.csv"
if [[ -d "$fixture_dir/requirements" ]]; then
    cp -r "$fixture_dir/requirements" "$workdir/.rtmx/requirements"
fi

# Write minimal config
cat > "$workdir/.rtmx/config.yaml" <<YAML
project:
  name: $experiment
rtm:
  database: .rtmx/database.csv
  requirements_dir: .rtmx/requirements
  schema: core
YAML

# Write MCP server config
local_rtmx=$(command -v rtmx)
cat > "$workdir/.mcp.json" <<MCPJSON
{
  "mcpServers": {
    "rtmx": {
      "command": "$local_rtmx",
      "args": ["mcp-server", "--stdio"],
      "cwd": "$workdir"
    }
  }
}
MCPJSON

# Generate agent prompt (CLAUDE.md) from rtmx's own template
(cd "$workdir" && rtmx install --agents claude --force --yes 2>/dev/null)
