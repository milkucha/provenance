#!/bin/bash
# Stop hook: nudge (once per session) to consider a CHRONICLE.md landmark entry.
# See CHRONICLE.md's own header for what counts. Soft nudge, not a hard block:
# fires at most once per session, and only when the session looks substantive
# and CHRONICLE.md doesn't already have uncommitted changes.

input=$(cat)

# Claude Code sets stop_hook_active=true on the retry after this hook already
# blocked once, to prevent an infinite loop. Never block twice in a row.
stop_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [ "$stop_active" = "true" ]; then
  exit 0
fi

session_id=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)
transcript=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)

marker_dir="${TMPDIR:-/tmp}/claude-chronicle-nudge"
mkdir -p "$marker_dir" 2>/dev/null
marker="$marker_dir/$session_id"

# Already nudged this session — don't nag again.
if [ -f "$marker" ]; then
  exit 0
fi

# Resolve repo root relative to this script, regardless of the hook's cwd.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 0

# Heuristic: "substantive session" — rough proxy via transcript line count.
# Each turn/tool-call/tool-result is at least one JSONL line, so a short
# back-and-forth won't cross this; adjust the threshold if it misfires.
lines=0
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  lines=$(wc -l < "$transcript" 2>/dev/null || echo 0)
fi
if [ "$lines" -lt 30 ]; then
  exit 0
fi

# If CHRONICLE.md already has uncommitted changes, assume it was already
# handled this session — mark as nudged and stay quiet.
if ! git diff --quiet -- CHRONICLE.md 2>/dev/null || ! git diff --cached --quiet -- CHRONICLE.md 2>/dev/null; then
  touch "$marker" 2>/dev/null
  exit 0
fi

touch "$marker" 2>/dev/null

cat <<'JSON'
{"decision":"block","reason":"This session looks substantive (session-end nudge, fires once). Before stopping: check CHRONICLE.md's own header at the repo root for what counts as a landmark entry, and if something from this session qualifies (a decision, an argument that shifted, a learning, a new open question), append a short dated entry there. If nothing rises to that bar, say so briefly and stop again — this is a soft check, not a requirement."}
JSON
