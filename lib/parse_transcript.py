#!/usr/bin/env python3
"""Parse Claude Code session transcripts for token accounting.

Part of intent-bench. Extracts token counts, intent tool attribution,
planning vs execution phases, and backtrack detection from Claude Code
JSON transcripts.

The tool prefix is configurable via INTENT_TOOL_PREFIX env var
(default: "mcp__rtmx__"). This allows different treatment plugins
to be recognized without code changes.
"""

import json
import os
import sys
from pathlib import Path

# Intent tool prefixes: configurable via env var
_env_prefix = os.environ.get("INTENT_TOOL_PREFIX", "mcp__rtmx__")
INTENT_TOOL_PREFIXES = tuple(p.strip() for p in _env_prefix.split(",") if p.strip())


def is_intent_tool(tool_name: str) -> bool:
    """Check if a tool call is an intent layer tool."""
    return any(tool_name.startswith(prefix) for prefix in INTENT_TOOL_PREFIXES)


def is_code_edit_tool(tool_name: str) -> bool:
    """Check if a tool call is a code editing operation."""
    return tool_name in ("Edit", "Write", "NotebookEdit")


def load_transcript(path: str):
    """Load transcript from JSON array, single JSON object, or NDJSON."""
    text = Path(path).read_text().strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "messages" in data:
                return data["messages"]
            return [data]
        return []
    except json.JSONDecodeError:
        pass

    # NDJSON
    messages = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not messages:
        raise json.JSONDecodeError("No valid JSON found", text, 0)
    return messages


def parse_transcript(path: str) -> dict:
    """Parse a Claude Code transcript and extract token metrics."""
    messages = load_transcript(path)

    result = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "tool_tokens": 0,
        "planning_tokens": 0,
        "execution_tokens": 0,
        "turns": 0,
        "backtracks": 0,
        "tool_calls_intent": 0,
        "tool_calls_other": 0,
        "tool_breakdown": {},
    }

    first_edit_seen = False
    files_read = set()
    has_result_summary = False
    cumulative_input = 0
    cumulative_output = 0
    cumulative_tokens_at_first_edit = 0
    turn_count = 0

    for raw in messages:
        if not isinstance(raw, dict):
            continue

        msg_type = raw.get("type", "")
        if msg_type in ("assistant", "user") and "message" in raw:
            msg = raw["message"]
        elif msg_type == "result" and "usage" in raw:
            if has_result_summary:
                continue
            has_result_summary = True
            usage = raw.get("usage", {})
            cache_input = usage.get("cache_creation_input_tokens", 0) + \
                usage.get("cache_read_input_tokens", 0)
            result["input_tokens"] = usage.get("input_tokens", 0) + cache_input
            result["output_tokens"] = usage.get("output_tokens", 0)
            result["turns"] = raw.get("num_turns", turn_count)
            continue
        elif "role" in raw:
            msg = raw
        elif "usage" in raw and not msg_type:
            usage = raw["usage"]
            cumulative_input += usage.get("input_tokens", 0)
            cumulative_output += usage.get("output_tokens", 0)
            continue
        else:
            continue

        role = msg.get("role", "")
        if role == "assistant":
            turn_count += 1

        usage = msg.get("usage", {})
        msg_input = usage.get("input_tokens", 0)
        msg_output = usage.get("output_tokens", 0)
        cumulative_input += msg_input
        cumulative_output += msg_output

        content = msg.get("content", [])
        if isinstance(content, str):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue

            if block.get("type") == "tool_use":
                tool_name = block.get("name", "")

                if is_intent_tool(tool_name):
                    result["tool_calls_intent"] += 1
                    result["tool_tokens"] += msg_input + msg_output
                    short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
                    result["tool_breakdown"][short_name] = (
                        result["tool_breakdown"].get(short_name, 0) + 1
                    )
                else:
                    result["tool_calls_other"] += 1

                if not first_edit_seen and is_code_edit_tool(tool_name):
                    first_edit_seen = True
                    cumulative_tokens_at_first_edit = (
                        cumulative_input + cumulative_output
                    )

                if tool_name == "Read":
                    file_path = ""
                    tool_input = block.get("input", {})
                    if isinstance(tool_input, dict):
                        file_path = tool_input.get("file_path", "")
                    if file_path in files_read:
                        result["backtracks"] += 1
                    else:
                        files_read.add(file_path)

    if not has_result_summary:
        result["input_tokens"] = cumulative_input
        result["output_tokens"] = cumulative_output
        result["turns"] = turn_count

    result["total_tokens"] = result["input_tokens"] + result["output_tokens"]

    if first_edit_seen:
        result["planning_tokens"] = cumulative_tokens_at_first_edit
        result["execution_tokens"] = result["total_tokens"] - cumulative_tokens_at_first_edit
    else:
        result["planning_tokens"] = result["total_tokens"]
        result["execution_tokens"] = 0

    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: parse_transcript.py <transcript.jsonl>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        result = parse_transcript(path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Failed to parse transcript: {e}", file=sys.stderr)
        print("0 0 0 0 0 0 0 0 0 0")
        sys.exit(1)

    # Output space-separated for shell consumption
    print(
        f"{result['input_tokens']} "
        f"{result['output_tokens']} "
        f"{result['total_tokens']} "
        f"{result['tool_tokens']} "
        f"{result['planning_tokens']} "
        f"{result['execution_tokens']} "
        f"{result['turns']} "
        f"{result['backtracks']} "
        f"{result['tool_calls_intent']} "
        f"{result['tool_calls_other']}"
    )

    # Detailed JSON to stderr for logging
    print(json.dumps(result, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
