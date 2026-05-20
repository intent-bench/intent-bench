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
#   - Must not overwrite existing repo files (non-destructive)
#   - Requires rtmx binary on $PATH
#
# Design: Fixtures are placed in .intent-bench/ (not .rtmx/) to avoid
# colliding with repos that already use RTMX or other intent systems.
# This keeps both conditions seeing the same baseline repo state --
# the treatment only adds experiment-specific decomposition via MCP.
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

# Treatment namespace: .intent-bench/ (never .rtmx/)
# This prevents collisions with repos that already have .rtmx/
intent_dir="$workdir/.intent-bench"
mkdir -p "$intent_dir"
cp "$fixture_dir/rtm.csv" "$intent_dir/database.csv"
if [[ -d "$fixture_dir/requirements" ]]; then
    cp -r "$fixture_dir/requirements" "$intent_dir/requirements"
fi

# Write config in treatment namespace using paths relative to workdir
# The .rtmx/ directory within .intent-bench/ makes rtmx's config
# discovery find this config when cwd is .intent-bench/
mkdir -p "$intent_dir/.rtmx"
cat > "$intent_dir/.rtmx/config.yaml" <<YAML
project:
  name: $experiment
rtm:
  database: database.csv
  requirements_dir: requirements
  schema: core
YAML

# Symlink database and requirements into .rtmx/ for config discovery
ln -sf ../database.csv "$intent_dir/.rtmx/database.csv"
if [[ -d "$intent_dir/requirements" ]]; then
    ln -sf ../requirements "$intent_dir/.rtmx/requirements"
fi

# Write MCP server config -- cwd points at .intent-bench/ so the
# server finds .rtmx/config.yaml there (not the repo's own .rtmx/).
# This leaves any existing repo .rtmx/ untouched: both conditions
# see identical repo state.
local_rtmx=$(command -v rtmx)
cat > "$workdir/.mcp.json" <<MCPJSON
{
  "mcpServers": {
    "rtmx": {
      "command": "$local_rtmx",
      "args": ["mcp-server", "--stdio"],
      "cwd": "$workdir/.intent-bench"
    }
  }
}
MCPJSON

# Generate agent guidance
# Run rtmx install from the treatment namespace so it reads fixture
# requirements, not the repo's own (if any)
(cd "$intent_dir" && rtmx install --agents claude --force --yes 2>/dev/null) || true
# Move generated CLAUDE.md to workdir root where the agent expects it
if [[ -f "$intent_dir/CLAUDE.md" ]]; then
    if [[ -f "$workdir/CLAUDE.md" ]]; then
        # Repo already has CLAUDE.md -- append treatment guidance
        printf '\n\n' >> "$workdir/CLAUDE.md"
        cat "$intent_dir/CLAUDE.md" >> "$workdir/CLAUDE.md"
    else
        mv "$intent_dir/CLAUDE.md" "$workdir/CLAUDE.md"
    fi
fi
