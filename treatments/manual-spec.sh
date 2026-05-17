#!/usr/bin/env bash
# manual-spec.sh -- Manual specification treatment plugin for intent-bench
# Seeds a working directory with a plain markdown requirements file.
# Demonstrates that intent-bench is tool-agnostic: no MCP server, no binary.
#
# Usage: manual-spec.sh setup <workdir> <experiment> <fixture_dir>
#
# Contract:
#   - Exit 0 = treatment ready
#   - Exit 1 = fatal setup error
#   - Must not modify anything outside $workdir
set -euo pipefail

cmd="${1:?Usage: manual-spec.sh <setup|validate> <workdir> <experiment> <fixture_dir>}"

case "$cmd" in
    validate)
        echo "manual-spec treatment: OK (no external dependencies)"
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

# Validate fixture
if [[ ! -d "$fixture_dir" ]]; then
    echo "ERROR: Fixture directory not found: $fixture_dir" >&2
    exit 1
fi
if [[ ! -f "$fixture_dir/requirements.md" ]]; then
    echo "ERROR: Fixture missing requirements.md: $fixture_dir/requirements.md" >&2
    exit 1
fi

# Copy requirements spec into workdir
cp "$fixture_dir/requirements.md" "$workdir/REQUIREMENTS.md"

# Copy agent guidance if provided
if [[ -f "$fixture_dir/CLAUDE.md" ]]; then
    cp "$fixture_dir/CLAUDE.md" "$workdir/CLAUDE.md"
fi
