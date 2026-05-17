#!/usr/bin/env python3
"""State-agnostic knowledge entropy scorer for agent output.

Part of intent-bench. Measures agent process quality -- how much of
the agent's work was productive vs wasted. All dimensions are derivable
from transcript + workdir without assumptions about project age, git
history, or documentation artifacts.

Dimensions:
  - productivity:     Fraction of tool calls that produced lasting output
  - rework:           Fraction of edits targeting already-edited files
  - conventionality:  Does the workdir follow standard project layout?
  - test_coherence:   Do the tests the agent wrote actually pass?

Output: JSON with entropy_score and per-dimension breakdown.
Scale: 0.0 (perfectly efficient) to 10.0 (maximum waste/entropy).
"""

import json
import os
import sys
from pathlib import Path


# Dimension weights (sum to 1.0)
WEIGHTS = {
    "productivity": 0.35,
    "rework": 0.25,
    "conventionality": 0.20,
    "test_coherence": 0.20,
}

# Normalization baselines
BASELINES = {
    "productivity": {"min": 0.4, "max": 1.0},
    "rework": {"min": 0.0, "max": 0.6},
    "conventionality": {"min": 0, "max": 4},
    "test_coherence": {"min": 0.0, "max": 1.0},
}

# Intent tool prefix: configurable via env var
INTENT_TOOL_PREFIX = os.environ.get("INTENT_TOOL_PREFIX", "mcp__rtmx__")


def load_transcript(path: str) -> list[dict]:
    """Load NDJSON transcript."""
    messages = []
    text = Path(path).read_text().strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("messages", [data])
        return []
    except json.JSONDecodeError:
        pass

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return messages


def extract_tool_calls(messages: list[dict]) -> list[dict]:
    """Extract all tool calls from transcript messages."""
    calls = []
    for raw in messages:
        if not isinstance(raw, dict):
            continue

        msg_type = raw.get("type", "")
        if msg_type in ("assistant", "user") and "message" in raw:
            msg = raw["message"]
        elif "role" in raw:
            msg = raw
        else:
            continue

        if msg.get("role") != "assistant":
            continue

        content = msg.get("content", [])
        if isinstance(content, str):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                tool_input = block.get("input", {})
                calls.append({
                    "name": block.get("name", ""),
                    "input": tool_input if isinstance(tool_input, dict) else {},
                })

    return calls


def score_productivity(tool_calls: list[dict], workdir: str) -> tuple[float, dict]:
    """Score productivity: fraction of tool calls producing lasting output."""
    productive = 0
    wasted = 0
    total = 0

    existing_files = set()
    if workdir and os.path.isdir(workdir):
        skip_dirs = {"node_modules", ".venv", "venv", "vendor", "target",
                     "__pycache__", ".git", ".pytest_cache"}
        for root, _, files in os.walk(workdir):
            rel_root = os.path.relpath(root, workdir)
            if any(part in skip_dirs for part in Path(rel_root).parts):
                continue
            for f in files:
                existing_files.add(os.path.join(root, f))
                existing_files.add(os.path.relpath(os.path.join(root, f), workdir))

    prefixes = tuple(p.strip() for p in INTENT_TOOL_PREFIX.split(",") if p.strip())

    for call in tool_calls:
        name = call["name"]
        inp = call["input"]

        if name in ("Write", "Edit"):
            total += 1
            file_path = inp.get("file_path", "")
            basename = os.path.basename(file_path)
            if any(basename in ef for ef in existing_files):
                productive += 1
            else:
                wasted += 1

        elif name == "Bash":
            total += 1
            productive += 1

        elif name == "Read":
            total += 1
            productive += 1

        elif any(name.startswith(p) for p in prefixes):
            total += 1
            productive += 1  # Intent tool calls are planning, always productive

    ratio = productive / total if total > 0 else 1.0
    return ratio, {"productive": productive, "wasted": wasted, "total": total}


def score_rework(tool_calls: list[dict]) -> tuple[float, dict]:
    """Score rework: fraction of edits targeting already-edited files."""
    files_edited = {}
    files_read = {}

    for call in tool_calls:
        name = call["name"]
        inp = call["input"]

        if name in ("Write", "Edit"):
            fp = inp.get("file_path", "")
            if fp:
                files_edited[fp] = files_edited.get(fp, 0) + 1

        elif name == "Read":
            fp = inp.get("file_path", "")
            if fp:
                files_read[fp] = files_read.get(fp, 0) + 1

    total_edits = sum(files_edited.values())
    unique_files = len(files_edited)
    rework_edits = total_edits - unique_files if total_edits > unique_files else 0

    total_reads = sum(files_read.values())
    unique_reads = len(files_read)
    rework_reads = total_reads - unique_reads if total_reads > unique_reads else 0

    total_ops = total_edits + total_reads
    total_rework = rework_edits + rework_reads
    rate = total_rework / total_ops if total_ops > 0 else 0.0

    return rate, {
        "total_edits": total_edits,
        "unique_files_edited": unique_files,
        "rework_edits": rework_edits,
        "rework_reads": rework_reads,
        "rate": round(rate, 3),
    }


def score_conventionality(workdir: str) -> tuple[int, dict]:
    """Score structural conventionality: how many project conventions are met."""
    if not workdir or not os.path.isdir(workdir):
        return 0, {"checks": {}, "met": 0, "total": 4}

    checks = {}

    manifests = ["package.json", "go.mod", "Cargo.toml", "pyproject.toml",
                 "requirements.txt", "Gemfile", "pom.xml", "build.gradle"]
    has_manifest = any(os.path.isfile(os.path.join(workdir, m)) for m in manifests)
    checks["project_manifest"] = has_manifest

    has_src = os.path.isdir(os.path.join(workdir, "src")) or \
              os.path.isdir(os.path.join(workdir, "lib")) or \
              os.path.isdir(os.path.join(workdir, "app")) or \
              os.path.isdir(os.path.join(workdir, "internal"))
    has_test = os.path.isdir(os.path.join(workdir, "tests")) or \
               os.path.isdir(os.path.join(workdir, "test")) or \
               os.path.isdir(os.path.join(workdir, "__tests__")) or \
               os.path.isdir(os.path.join(workdir, "spec"))
    checks["separated_dirs"] = has_src and has_test

    entry_points = ["main.go", "main.py", "index.js", "index.ts", "app.py",
                    "server.js", "server.ts", "Makefile", "Dockerfile"]
    has_entry = any(os.path.isfile(os.path.join(workdir, e)) for e in entry_points)
    if not has_entry and has_src:
        for src_dir in ["src", "lib", "app"]:
            src_path = os.path.join(workdir, src_dir)
            if os.path.isdir(src_path):
                has_entry = any(
                    os.path.isfile(os.path.join(src_path, e))
                    for e in ["index.js", "index.ts", "main.go", "main.py",
                              "app.py", "server.js", "server.ts"]
                )
                if has_entry:
                    break
    checks["entry_point"] = has_entry

    docs = ["README.md", "README", "README.txt", "CLAUDE.md", "docs"]
    has_docs = any(
        os.path.isfile(os.path.join(workdir, d)) or os.path.isdir(os.path.join(workdir, d))
        for d in docs
    )
    checks["documentation"] = has_docs

    met = sum(1 for v in checks.values() if v)
    return met, {"checks": checks, "met": met, "total": 4}


def score_test_coherence(tests_passed: int, tests_failed: int,
                         tests_total: int, outcome: str) -> tuple[float, dict]:
    """Score test coherence: do the tests the agent wrote actually pass?"""
    if tests_total == 0:
        if outcome == "PASS":
            pass_rate = 0.5
        else:
            pass_rate = 0.0
    else:
        pass_rate = tests_passed / tests_total

    return pass_rate, {
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "tests_total": tests_total,
        "outcome": outcome,
        "pass_rate": round(pass_rate, 3),
    }


def normalize(value: float, dim: str) -> float:
    """Normalize a dimension value to [0, 1] where 1 = maximum entropy."""
    baseline = BASELINES[dim]
    lo, hi = baseline["min"], baseline["max"]

    if dim in ("productivity", "test_coherence", "conventionality"):
        if dim == "conventionality":
            return max(0.0, min(1.0, 1.0 - (value / hi)))
        else:
            if value >= hi:
                return 0.0
            if value <= lo:
                return 1.0
            return 1.0 - (value - lo) / (hi - lo)
    else:
        if value <= lo:
            return 0.0
        if value >= hi:
            return 1.0
        return (value - lo) / (hi - lo)


def compute_agent_entropy(transcript_path: str, workdir: str,
                          tests_passed: int = 0, tests_failed: int = 0,
                          tests_total: int = 0, outcome: str = "ERROR") -> dict:
    """Compute composite agent entropy score."""
    messages = load_transcript(transcript_path) if transcript_path else []
    tool_calls = extract_tool_calls(messages)

    prod_raw, prod_detail = score_productivity(tool_calls, workdir)
    rework_raw, rework_detail = score_rework(tool_calls)
    conv_raw, conv_detail = score_conventionality(workdir)
    test_raw, test_detail = score_test_coherence(
        tests_passed, tests_failed, tests_total, outcome
    )

    dimensions = []
    weighted_sum = 0.0

    for dim_name, raw_value in [
        ("productivity", prod_raw),
        ("rework", rework_raw),
        ("conventionality", float(conv_raw)),
        ("test_coherence", test_raw),
    ]:
        norm = normalize(raw_value, dim_name)
        weight = WEIGHTS[dim_name]
        weighted_sum += norm * weight

        dimensions.append({
            "name": dim_name,
            "raw": round(raw_value, 3) if isinstance(raw_value, float) else raw_value,
            "normalized": round(norm, 3),
            "weight": weight,
            "included": True,
        })

    entropy_score = round(weighted_sum * 10, 1)

    return {
        "entropy_score": entropy_score,
        "dimensions": dimensions,
        "dimensions_included": 4,
        "dimensions_excluded": [],
        "detail": {
            "productivity": prod_detail,
            "rework": rework_detail,
            "conventionality": conv_detail,
            "test_coherence": test_detail,
        },
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Compute agent output entropy from transcript + workdir"
    )
    parser.add_argument("transcript", help="Path to transcript.jsonl")
    parser.add_argument("workdir", help="Path to agent working directory")
    parser.add_argument("--tests-passed", type=int, default=0)
    parser.add_argument("--tests-failed", type=int, default=0)
    parser.add_argument("--tests-total", type=int, default=0)
    parser.add_argument("--outcome", default="ERROR")
    args = parser.parse_args()

    result = compute_agent_entropy(
        args.transcript, args.workdir,
        args.tests_passed, args.tests_failed, args.tests_total,
        args.outcome,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
