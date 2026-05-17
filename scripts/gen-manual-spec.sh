#!/usr/bin/env bash
# gen-manual-spec.sh -- Generate manual-spec fixtures from RTMX fixtures
# Ensures impartiality: same requirement content, different delivery mechanism.
#
# Usage: gen-manual-spec.sh [experiment...]
#        gen-manual-spec.sh             # generates all
#        gen-manual-spec.sh url-shortener task-manager
#
# Reads: fixtures/rtmx/<experiment>/rtm.csv
#         fixtures/rtmx/<experiment>/requirements/**/*.md (if present)
# Writes: fixtures/manual-spec/<experiment>/requirements.md
#          fixtures/manual-spec/<experiment>/CLAUDE.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

generate_experiment() {
    local experiment="$1"
    local rtmx_dir="$REPO_DIR/fixtures/rtmx/$experiment"
    local out_dir="$REPO_DIR/fixtures/manual-spec/$experiment"

    if [[ ! -f "$rtmx_dir/rtm.csv" ]]; then
        echo "ERROR: No rtm.csv found for experiment: $experiment" >&2
        return 1
    fi

    mkdir -p "$out_dir"

    # Parse CSV and generate markdown
    python3 "$SCRIPT_DIR/gen_requirements_md.py" \
        "$rtmx_dir/rtm.csv" \
        "$rtmx_dir/requirements" \
        "$out_dir/requirements.md"

    # Generate agent guidance file
    cat > "$out_dir/CLAUDE.md" <<'EOF'
# Project Guidance

Read REQUIREMENTS.md before starting implementation. It contains a structured
list of requirements with dependency ordering and acceptance criteria.
Implement them in the specified dependency order to avoid rework.

Write a comprehensive test suite covering all requirements. Tests should be
self-contained and runnable with a single command.
EOF

    echo "  [OK] $experiment -> $out_dir/requirements.md"
}

# Determine which experiments to generate
if [[ $# -gt 0 ]]; then
    experiments=("$@")
else
    experiments=()
    for dir in "$REPO_DIR/fixtures/rtmx"/*/; do
        if [[ -d "$dir" ]]; then
            experiments+=("$(basename "$dir")")
        fi
    done
fi

echo "Generating manual-spec fixtures..."
for exp in "${experiments[@]}"; do
    generate_experiment "$exp"
done
echo "Done."
