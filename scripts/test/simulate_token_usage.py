"""
Sum the orchestrating session's own token usage over a time window, read from Claude Code's own
session transcript - built 2026-08-30 on request, to compare a /simulate run's real cost across
dispatch models (Local/Ollama vs. a Claude subagent per pass) without adding any new instrumentation
to the skill itself. Never touches lore state; purely a read of the harness's own JSONL log.

Claude Code writes one JSON object per line to
    ~/.claude/projects/<project-slug>/<session-id>.jsonl
and each assistant turn carries a `message.usage` block (input_tokens, output_tokens,
cache_creation_input_tokens, cache_read_input_tokens) plus a timestamp. `isSidechain: true` marks a
subagent's own turn (an Agent-tool dispatch) rather than the orchestrator's - summed separately here,
though a run using the Local/Ollama path has none of these, since it never dispatches a subagent.

This is a coarse instrument, not a billing reconciliation: `input_tokens` is usually tiny once
prompt caching kicks in (most of a turn's context is `cache_read_input_tokens`, heavily discounted
vs. a fresh token, cache_creation less so) - the script reports all four separately plus a naive sum
so the reader can weigh them, rather than picking one "true cost" number for them.

Usage:
    py scripts/test/simulate_token_usage.py --transcript <path to session .jsonl> \
        --since 2026-08-30T21:22:50Z --until 2026-08-30T21:27:56Z --label "passes 3-5 + Step 4"
"""

import argparse
import json
from pathlib import Path


def in_window(ts: str, since: str | None, until: str | None) -> bool:
    if since and ts < since:
        return False
    if until and ts > until:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--transcript", required=True, help="Path to the session's own .jsonl transcript")
    parser.add_argument("--since", default=None, help="ISO8601 timestamp, inclusive lower bound")
    parser.add_argument("--until", default=None, help="ISO8601 timestamp, inclusive upper bound")
    parser.add_argument("--label", default=None, help="Optional label for this window, echoed in the output")
    args = parser.parse_args()

    path = Path(args.transcript)
    if not path.exists():
        raise SystemExit(f"transcript not found: {path}")

    totals = {
        "orchestrator": {"turns": 0, "input": 0, "output": 0, "cache_creation": 0, "cache_read": 0},
        "subagent": {"turns": 0, "input": 0, "output": 0, "cache_creation": 0, "cache_read": 0},
    }

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "assistant":
                continue
            ts = d.get("timestamp")
            if not ts or not in_window(ts, args.since, args.until):
                continue
            usage = (d.get("message") or {}).get("usage")
            if not usage:
                continue
            bucket = totals["subagent"] if d.get("isSidechain") else totals["orchestrator"]
            bucket["turns"] += 1
            bucket["input"] += usage.get("input_tokens", 0)
            bucket["output"] += usage.get("output_tokens", 0)
            bucket["cache_creation"] += usage.get("cache_creation_input_tokens", 0)
            bucket["cache_read"] += usage.get("cache_read_input_tokens", 0)

    for bucket in totals.values():
        bucket["total"] = bucket["input"] + bucket["output"] + bucket["cache_creation"] + bucket["cache_read"]

    if args.label:
        print(f"Window: {args.label}")
    print(f"Since: {args.since or '(start of file)'}   Until: {args.until or '(end of file)'}")
    for name, bucket in totals.items():
        if bucket["turns"] == 0:
            continue
        print(
            f"{name}: {bucket['turns']} turns | input {bucket['input']:,} | output {bucket['output']:,} | "
            f"cache_creation {bucket['cache_creation']:,} | cache_read {bucket['cache_read']:,} | "
            f"total {bucket['total']:,}"
        )


if __name__ == "__main__":
    main()
