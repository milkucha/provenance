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

A brief with ONE entry under `characters` is a REFLECTION scene (2026-10-17: the pursuit stage
arrived_empty, a character alone at a place): the same reply shape, with that character as the only
speaker, the only entry under `participants`, and `claims` free to be empty. validate_reply() enforces the
one-speaker and one-participant parts; the schema itself is unchanged, and `criterion_move` stays
available exactly as before (only when a director's note flags the anchor as live; nothing widened).

THE CONTEXT WINDOW (a correctness matter, 2026-10-17): Ollama gives a model whatever `num_ctx` it defaults
to (a few thousand tokens) unless the request names one, and a prompt that does not fit is TRUNCATED
SILENTLY FROM THE START, which is where the rules and the legend are. A pair-scene prompt is the
preamble (about 4k tokens) plus the brief (about 4k, both characters' whole knowledge samples), 7 to 9k.
So every call now sends `options.num_ctx` (tuning.json `enacter.num_ctx`, `--num-ctx` overrides), and two
checks fail LOUDLY instead of letting a clipped prompt through: a pre-flight estimate (characters /
`chars_per_token`, plus `reply_reserve_tokens` for the answer) that refuses to send what cannot fit, and a
look at the response's own `prompt_eval_count` (and `eval_count`): at or above num_ctx less a small margin
the prompt was cut or the reply ran the window out, and the reply is refused, not accepted.

Usage:
    py scripts/lore/enact_via_ollama.py --brief-file .simulate_pass_brief_combined.json
    py scripts/lore/enact_via_ollama.py --brief-file brief.json --director-note "..." --out reply.json
    py scripts/lore/pass_prep.py --p1 a --pass-number 1 | py scripts/lore/enact_via_ollama.py
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PREAMBLE_PATH = SCRIPTS_DIR / "enact_preamble.md"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402

# Used only if _lore/tuning.json has no `enacter` block (an old root); the numbers live there.
ENACTER_DEFAULTS = {"num_ctx": 12288, "reply_reserve_tokens": 1536, "chars_per_token": 3.5, "truncation_margin": 16}


def enacter_cfg() -> dict:
    cfg = dict(ENACTER_DEFAULTS)
    cfg.update({k: v for k, v in (tuning.load().get("enacter") or {}).items() if not k.startswith("_")})
    return cfg

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


def estimate_tokens(*texts: str, chars_per_token: float = 3.5) -> int:
    """A cheap estimate of the tokens in the texts (characters / chars_per_token, rounded up). Measured on
    the preamble and a real brief it errs a little high for English with JSON punctuation, which is the
    safe side for a pre-flight."""
    return int(-(-sum(len(t) for t in texts) // chars_per_token))


def check_fits(system: str, user: str, num_ctx: int, reply_reserve: int, chars_per_token: float = 3.5) -> int:
    """The pre-flight: refuse (SystemExit, loud) a prompt that, by the estimate, plus the room kept for the
    reply, would not fit in `num_ctx`. Returns the estimated prompt tokens when it fits."""
    est = estimate_tokens(system, user, chars_per_token=chars_per_token)
    if est + reply_reserve > num_ctx:
        raise SystemExit(
            f"the prompt will not fit the context window: about {est} tokens "
            f"({len(system) + len(user)} characters / {chars_per_token}) plus {reply_reserve} kept for the reply "
            f"is more than num_ctx {num_ctx}. Ollama would drop the START of the prompt (the rules and the legend) "
            f"without a word. Raise `enacter.num_ctx` in _lore/tuning.json (or --num-ctx) if the GPU's memory "
            f"allows it, or trim the brief (tuning.json `enacter_knowledge` caps)."
        )
    return est


def check_not_truncated(body: dict, num_ctx: int, margin: int) -> None:
    """Ollama reports the tokens it actually evaluated for the prompt (`prompt_eval_count`) and generated
    (`eval_count`). A prompt that came back at or above num_ctx less `margin` was cut to fit (from the
    start); a prompt plus reply that reached the window means the reply was cut or the context shifted.
    Either way the reply is not to be trusted: raise (SystemExit), never accept it."""
    pec = body.get("prompt_eval_count")
    if pec is not None and pec >= num_ctx - margin:
        raise SystemExit(
            f"the prompt was TRUNCATED by Ollama: it evaluated {pec} prompt tokens against num_ctx {num_ctx} "
            f"(margin {margin}); what did not fit was dropped from the start of the prompt, the rules and the "
            f"legend. The reply is refused. Raise `enacter.num_ctx` in _lore/tuning.json (or --num-ctx), or trim the brief."
        )
    ec = body.get("eval_count")
    if pec is not None and ec is not None and pec + ec >= num_ctx - margin:
        raise SystemExit(
            f"the context window ran out while the reply was being written: {pec} prompt + {ec} reply tokens "
            f"against num_ctx {num_ctx}. The reply is refused. Raise `enacter.num_ctx` in _lore/tuning.json (or --num-ctx)."
        )


def parse_chat_body(body: dict, num_ctx: int, margin: int) -> dict:
    """The model's reply from a /api/chat response body, after the truncation check. Pure, so it can be
    tested with a stubbed body."""
    check_not_truncated(body, num_ctx, margin)
    content = body.get("message", {}).get("content", "")
    if not content:
        raise SystemExit(f"empty reply from Ollama: {json.dumps(body)[:500]}")
    return json.loads(content)  # model was constrained to REPLY_SCHEMA; a parse failure here is real


def call_ollama(host: str, model: str, system: str, user: str, temperature: float,
                num_ctx: int | None = None, cfg: dict | None = None) -> dict:
    cfg = cfg or enacter_cfg()
    num_ctx = int(num_ctx or cfg["num_ctx"])
    check_fits(system, user, num_ctx, int(cfg["reply_reserve_tokens"]), float(cfg["chars_per_token"]))
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "format": REPLY_SCHEMA,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": num_ctx},
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
    return parse_chat_body(body, num_ctx, int(cfg["truncation_margin"]))


def known_tags(brief: dict) -> set:
    """Every string the brief itself offers as a legitimate `about` tag - a claim/grounded_experience
    tag has to copy one of these exactly (see enact_preamble.md's "copy character-for-character"
    rule). Built once per call so validate_reply can check without re-deriving this each time."""
    tags = set()
    for char in brief.get("characters", {}).values():
        anchor = (char.get("criterion") or {}).get("anchor")
        if anchor:
            tags.add(anchor)
        for ref in (char.get("knowledge") or {}).get("education") or {}:
            tags.add(ref)  # a knowledge ref ("tale: x", "location: y") is a legitimate tag, copied exactly
        arc_premise = char.get("arc_premise") or {}
        for key in ("about", "needs"):
            for t in arc_premise.get(key) or []:
                tags.add(t)
    matched_about = (brief.get("brief", {}).get("arc") or {}).get("matched_about")
    for t in matched_about or []:
        tags.add(t)
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
            if (g.get("text") or "").strip() and (g.get("about") or "").strip()
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
    if len(expected_slugs) == 1:
        # A reflection: every line is the one character's. The speaker label is their name (or slug).
        only = expected_slugs[0]
        allowed = {only.lower(), str(((brief.get("characters") or {}).get(only) or {}).get("name", only)).lower()}
        for turn in reply.get("scene", []):
            if str(turn.get("speaker", "")).strip().lower() not in allowed:
                problems.append(f"a reflection has one speaker, {sorted(allowed)}; got {turn.get('speaker')!r}")
                break
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


def enacter_view(brief: dict) -> dict:
    """The last gate before the model: `horizon_pre` is reduced to the band, whatever the caller
    handed in. The lifespan is meant to be secret (`ending`, `lived` are orchestrator bookkeeping);
    pass_prep.py already sends the band only, this keeps a hand-built or older brief from leaking."""
    view = dict(brief)
    view["horizon_pre"] = {s: {"band": (h or {}).get("band")} for s, h in (brief.get("horizon_pre") or {}).items()}
    return view


def build_user_message(brief: dict, director_note: str) -> str:
    parts = ["## This pass's brief (JSON)", "```json", json.dumps(enacter_view(brief), indent=2, ensure_ascii=False), "```"]
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
    parser.add_argument("--num-ctx", type=int, default=None, help="the context window sent to Ollama, in tokens (default: _lore/tuning.json enacter.num_ctx)")
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
            reply = call_ollama(args.host, args.model, system, user, args.temperature, num_ctx=args.num_ctx)
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
