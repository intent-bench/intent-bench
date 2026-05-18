#!/usr/bin/env bash
# test-first.sh -- Test-first treatment plugin
# Provides pre-written test files as the intent layer.
# The agent sees failing tests and must implement code to pass them.
set -euo pipefail

cmd="${1:?usage: test-first.sh <setup|validate> [args...]}"

case "$cmd" in
    validate)
        echo "test-first treatment: OK (no external dependencies)"
        exit 0
        ;;
    setup)
        workdir="${2:?workdir required}"
        experiment="${3:?experiment required}"
        fixture_dir="${4:?fixture_dir required}"

        if [[ ! -d "$fixture_dir" ]]; then
            echo "ERROR: Fixture directory not found: $fixture_dir" >&2
            exit 1
        fi

        # Copy test files into the workdir
        if [[ -d "$fixture_dir/tests" ]]; then
            cp -r "$fixture_dir/tests/"* "$workdir/" 2>/dev/null || true
        fi

        # Copy optional CLAUDE.md
        if [[ -f "$fixture_dir/CLAUDE.md" ]]; then
            cp "$fixture_dir/CLAUDE.md" "$workdir/CLAUDE.md"
        fi

        echo "test-first treatment: seeded test files into $workdir"
        ;;
    *)
        echo "Unknown command: $cmd" >&2
        exit 1
        ;;
esac
