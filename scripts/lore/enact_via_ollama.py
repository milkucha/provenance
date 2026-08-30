"""
Standalone-tested local-model enacter for /simulate's per-pass dispatch (Step 3 point 4) - calls a
locally-hosted Ollama model instead of the Agent tool's Claude subagent, forcing strict JSON output
via Ollama's structured-output mode rather than the free-text reply a Claude subagent produces (a
14B local model is far less reliable at producing parseable prose than a hosted frontier model, so
this path skips that risk entirely instead of trying to parse around it).

Not wired into simulate/SKILL.md yet - this is the infrastructure being proven first. It takes the
exact combined JSON pass_prep.py already produces (--brief-file, or stdin) plus an optional one-line
director's note (same "only when the gate hit needs a concrete nudge" rule the Claude-subagent path
follows), and returns one JSON object shaped so it plugs directly into record_hearsay.py's claims
payload and pass_apply.py's decisions payload with no further reshaping - see enact_preamble.md for
the exact reply schema and the writing rules sent alongside it.

The fixed instruction preamble (scripts/lore/enact_preamble.md) is read fresh each call, never
inlined here - so editing the writing rules never means editing this script.

Usage:
    py scripts/lore/enact_via_ollama.py --brief-file .simulate_pass_brief_combined.json
    py scripts/lore/enact_via_ollama.py --brief-file brief.json --director-note "..." --out reply.json
    py scripts/lore/pass_prep.py --p1 a --p2 b --pass-number 1 | py scripts/lore/enact_via_ollama.py
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PREAMBLE_PATH = SCRIPTS_DIR / "enact_preamble.md"

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:14b"

REPLY_SCHEMA = {
    "type": "object",
    "properties": {
        "scene": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "speaker": {"type": "string"},
                    "line": {"type": "string"},
                },
                "required": ["speaker", "line"],
            },
        },
        "hearsay": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "summary": {"type": "string"},
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "about": {"type": "string"},
                            "note": {"type": "string"},
                            "oral_lore": {"type": "boolean"},
                        },
                        "required": ["text", "about"],
                    },
                },
            },
            "required": ["location", "summary", "claims"],
        },
        "participants": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "experience": {"type": "array", "items": {"type": "string"}},
                    "grounded_experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "about": {"type": "string"},
                                "text": {"type": "string"},
                            },
                            "required": ["about", "text"],
                        },
                    },
                    "cost_ledger": {"type": "array", "items": {"type": "string"}},
                    "criterion_move": {
                        "type": ["object", "null"],
                        "properties": {
                            "move": {"type": "string", "enum": ["reject", "reinterpret", "break"]},
                            "dialog": {"type": "string"},
                            "cause": {"type": "string"},
                            "note": {"type": "string"},
                            "trusts": {"type": "string"},
                            "distrusts": {"type": "string"},
                        },
                        "required": ["move", "dialog", "cause"],
                    },
                },
                "required": ["experience", "grounded_experience", "cost_ledger", "criterion_move"],
            },
        },
    },
    "required": ["scene", "hearsay", "participants"],
}


def load_preamble() -> str:
    if not PREAMBLE_PATH.exists():
        raise SystemExit(f"missing preamble: {PREAMBLE_PATH}")
    return PREAMBLE_PATH.read_text(encoding="utf-8")


def call_ollama(host: str, model: str, system: str, user: str, temperature: float) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "format": REPLY_SCHEMA,
        "stream": False,
        "options": {"temperature": temperature},
    }
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise SystemExit(
            f"could not reach Ollama at {host} (is `ollama serve` running / the app open?): {e}"
        )
    content = body.get("message", {}).get("content", "")
    if not content:
        raise SystemExit(f"empty reply from Ollama: {json.dumps(body)[:500]}")
    return json.loads(content)  # model was constrained to REPLY_SCHEMA; a parse failure here is real


def known_tags(brief: dict) -> set:
    """Every string the brief itself offers as a legitimate `about` tag - a claim/grounded_experience
    tag has to copy one of these exactly (see enact_preamble.md's "copy character-for-character"
    rule). Built once per call so validate_reply can check without re-deriving this each time."""
    tags = set()
    for char in brief.get("characters", {}).values():
        anchor = (char.get("criterion") or {}).get("anchor")
        if anchor:
            tags.add(anchor)
        arc_premise = char.get("arc_premise") or {}
        for key in ("about", "needs"):
            for t in arc_premise.get(key) or []:
                tags.add(t)
    matched_about = (brief.get("brief", {}).get("arc") or {}).get("matched_about")
    if matched_about:
        tags.add(matched_about)
    return tags


def clean_reply(reply: dict) -> dict:
    """Mechanical cleanup only - never a judgment call. Drops junk placeholder entries (an array
    slot whose text is empty) that a small model sometimes pads a required array with instead of
    leaving it genuinely empty, and normalizes `about: ""` to `about: None` to match
    record_hearsay.py's own null contract (see its docstring: `about` is a required key, but its
    value may be null)."""
    hearsay = reply.get("hearsay", {})
    hearsay["claims"] = [
        {**c, "about": c.get("about") or None}
        for c in hearsay.get("claims", [])
        if (c.get("text") or "").strip()
    ]
    for entry in hearsay["claims"]:
        if not entry.get("note"):
            entry.pop("note", None)
    reply["hearsay"] = hearsay

    for data in reply.get("participants", {}).values():
        data["experience"] = [e for e in data.get("experience", []) if e.strip()]
        data["cost_ledger"] = [e for e in data.get("cost_ledger", []) if e.strip()]
        data["grounded_experience"] = [
            {**g, "about": g.get("about") or None}
            for g in data.get("grounded_experience", [])
            if (g.get("text") or "").strip()
        ]
    return reply


def validate_reply(reply: dict, expected_slugs: list, brief: dict) -> list:
    """Structural checks beyond what the JSON schema constraint already guarantees - a model can
    satisfy the schema and still, say, name a participant slug from thin air, or paraphrase an
    `about` tag instead of copying it. Returns a list of problems (empty = clean). Call after
    clean_reply(), so empty-placeholder noise is already gone and doesn't trigger a wasted retry."""
    problems = []
    if not reply.get("scene"):
        problems.append("scene is empty")
    for turn in reply.get("scene", []):
        if not turn.get("line", "").strip():
            problems.append("a scene turn has an empty line")
        if "*" in turn.get("line", ""):
            problems.append(f"possible stage direction (asterisk) in a line: {turn['line'][:60]!r}")
    participants = reply.get("participants", {})
    missing = [s for s in expected_slugs if s not in participants]
    extra = [s for s in participants if s not in expected_slugs]
    if missing:
        problems.append(f"missing participant slug(s) in reply: {missing}")
    if extra:
        problems.append(f"unexpected participant slug(s) in reply: {extra}")

    tags = known_tags(brief)
    for c in reply.get("hearsay", {}).get("claims", []):
        about = c.get("about")
        if about and about not in tags:
            problems.append(f"claim `about` tag doesn't exactly match a brief tag, copy it verbatim: {about!r}")
    for slug, data in participants.items():
        for g in data.get("grounded_experience", []):
            about = g.get("about")
            if about and about not in tags:
                problems.append(
                    f"{slug}'s grounded_experience `about` tag doesn't exactly match a brief tag: {about!r}"
                )
    return problems


def build_user_message(brief: dict, director_note: str) -> str:
    parts = ["## This pass's brief (JSON)", "```json", json.dumps(brief, indent=2, ensure_ascii=False), "```"]
    if director_note:
        parts += ["", f"## Director's note\n{director_note}"]
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brief-file", default=None, help="pass_prep.py's combined JSON output; omit to read stdin")
    parser.add_argument("--director-note", default="", help="one-sentence nudge, only when a gate hit needs one")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--temperature", type=float, default=0.85)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--out", default=None, help="also write the validated reply to this path")
    args = parser.parse_args()

    raw = Path(args.brief_file).read_text(encoding="utf-8") if args.brief_file else sys.stdin.read()
    brief = json.loads(raw)
    expected_slugs = sorted(brief.get("characters", {}).keys())
    if not expected_slugs:
        raise SystemExit("brief has no `characters` block - is this pass_prep.py's actual output?")

    system = load_preamble()
    user = build_user_message(brief, args.director_note)

    attempt = 0
    problems = ["not yet attempted"]
    reply = None
    while attempt <= args.max_retries and problems:
        attempt += 1
        try:
            reply = call_ollama(args.host, args.model, system, user, args.temperature)
        except json.JSONDecodeError as e:
            problems = [f"reply was not valid JSON: {e}"]
            reply = None
            continue
        reply = clean_reply(reply)
        problems = validate_reply(reply, expected_slugs, brief)
        if problems:
            user = (
                build_user_message(brief, args.director_note)
                + "\n\n## Your previous reply had problems - fix them and answer again\n"
                + "\n".join(f"- {p}" for p in problems)
            )

    result = {
        "attempts": attempt,
        "problems": problems,
        "model": args.model,
        "reply": reply,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
