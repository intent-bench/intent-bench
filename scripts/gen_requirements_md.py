#!/usr/bin/env python3
"""Generate a plain-markdown requirements.md from an RTMX rtm.csv and requirement files.

This script ensures impartiality in the manual-spec treatment: the same
requirement content is delivered as a structured markdown document, without
any RTMX tooling, MCP server, or binary dependency.

Usage:
    python3 gen_requirements_md.py <rtm.csv> <requirements_dir> <output.md>

The output preserves:
- Requirement IDs and text
- Dependency ordering (topological sort)
- Acceptance criteria from requirement files (if available)
- Phase grouping
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path


def parse_rtm(csv_path: str) -> list[dict]:
    """Parse the RTM database CSV."""
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def topological_sort(rows: list[dict]) -> list[dict]:
    """Sort requirements by dependency order (Kahn's algorithm)."""
    # Build adjacency: dep -> [dependents]
    id_to_row = {r["req_id"]: r for r in rows}
    in_degree = {r["req_id"]: 0 for r in rows}
    graph = defaultdict(list)

    for row in rows:
        deps = row.get("dependencies", "")
        if deps:
            for dep in deps.split("|"):
                dep = dep.strip()
                if dep and dep in id_to_row:
                    graph[dep].append(row["req_id"])
                    in_degree[row["req_id"]] += 1

    # Kahn's algorithm with priority tie-breaking
    queue = []
    for rid, deg in in_degree.items():
        if deg == 0:
            queue.append(rid)
    queue.sort(
        key=lambda rid: (
            int(id_to_row[rid].get("phase", "0") or "0"),
            id_to_row[rid].get("priority", "Z"),
            rid,
        )
    )

    result = []
    while queue:
        node = queue.pop(0)
        result.append(id_to_row[node])
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
        queue.sort(
            key=lambda rid: (
                int(id_to_row[rid].get("phase", "0") or "0"),
                id_to_row[rid].get("priority", "Z"),
                rid,
            )
        )

    # Append any remaining (cycles or disconnected)
    seen = {r["req_id"] for r in result}
    for row in rows:
        if row["req_id"] not in seen:
            result.append(row)

    return result


def load_requirement_file(req_dir: Path, row: dict) -> str | None:
    """Load the detailed requirement markdown file if it exists."""
    req_file = row.get("requirement_file", "")
    if req_file:
        path = req_dir / req_file
        if path.exists():
            return path.read_text()

    # Fallback: search by req_id
    for md in req_dir.rglob(f"{row['req_id']}.md"):
        return md.read_text()

    return None


def extract_acceptance_criteria(content: str) -> str | None:
    """Extract acceptance criteria section from a requirement file."""
    lines = content.split("\n")
    in_section = False
    criteria_lines = []

    for line in lines:
        if line.strip().lower().startswith("## acceptance criteria"):
            in_section = True
            continue
        elif in_section and line.strip().startswith("## "):
            break
        elif in_section:
            criteria_lines.append(line)

    text = "\n".join(criteria_lines).strip()
    return text if text else None


def extract_api_endpoints(content: str) -> str | None:
    """Extract API endpoints section from a requirement file."""
    lines = content.split("\n")
    in_section = False
    endpoint_lines = []

    for line in lines:
        if line.strip().lower().startswith("## api endpoints"):
            in_section = True
            continue
        elif in_section and line.strip().startswith("## "):
            break
        elif in_section:
            endpoint_lines.append(line)

    text = "\n".join(endpoint_lines).strip()
    if text and text.lower() != "not applicable. this is an internal infrastructure requirement.":
        return text
    return None


def generate_markdown(rows: list[dict], req_dir: Path) -> str:
    """Generate the requirements.md content."""
    sorted_rows = topological_sort(rows)

    lines = []
    lines.append("# Requirements Specification")
    lines.append("")
    lines.append("## Implementation Order")
    lines.append("")
    lines.append("Requirements are listed in dependency order. Implement each")
    lines.append("requirement fully before moving to the next. Later requirements")
    lines.append("depend on earlier ones being complete.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, row in enumerate(sorted_rows, 1):
        req_id = row["req_id"]
        req_text = row.get("requirement_text", "")
        deps = row.get("dependencies", "")
        phase = row.get("phase", "")
        notes = row.get("notes", "")

        lines.append(f"## {i}. {req_id}: {req_text}")
        lines.append("")

        if phase:
            lines.append(f"**Phase:** {phase}")
            lines.append("")

        if deps:
            dep_list = [d.strip() for d in deps.split("|") if d.strip()]
            lines.append(f"**Depends on:** {', '.join(dep_list)}")
            lines.append("")

        if notes:
            lines.append(f"*{notes}*")
            lines.append("")

        # Load detailed content from requirement file
        if req_dir.exists():
            content = load_requirement_file(req_dir, row)
            if content:
                criteria = extract_acceptance_criteria(content)
                if criteria:
                    lines.append("### Acceptance Criteria")
                    lines.append("")
                    lines.append(criteria)
                    lines.append("")

                endpoints = extract_api_endpoints(content)
                if endpoints:
                    lines.append("### API")
                    lines.append("")
                    lines.append(endpoints)
                    lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: gen_requirements_md.py <rtm.csv> <requirements_dir> <output.md>",
            file=sys.stderr,
        )
        sys.exit(1)

    csv_path = sys.argv[1]
    req_dir = Path(sys.argv[2])
    output_path = sys.argv[3]

    rows = parse_rtm(csv_path)
    if not rows:
        print(f"ERROR: No requirements found in {csv_path}", file=sys.stderr)
        sys.exit(1)

    markdown = generate_markdown(rows, req_dir)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(markdown)
    print(f"  Generated {output_path} ({len(rows)} requirements)")


if __name__ == "__main__":
    main()
