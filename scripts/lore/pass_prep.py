"""
Driver script for /simulate's unattended batch mode - collapses every mechanical, pre-scene call a
pass needs into one: `p1`'s pre-scene horizon band (/enact Step 1's "Horizon" bullet) plus the whole
of simulate_pass_brief.py (/enact Step 4). Chains the real scripts via subprocess, exactly like
write_arc.py already chains to register_arc_concept.py - this never reimplements their logic, it only
collapses how many separate tool-call round-trips a subagent pays for reaching it.

**Updated for the asymmetric per-pass model (design session 2026-09-13):** only `--p1` is required
now - there is no pre-fixed `--p2`/`--forced-visit` any more, since whether a second participant even
exists this pass (and who) is discovered inside simulate_pass_brief.py itself. This script reads
`participant_2` back out of the brief JSON after that call returns and only fetches its own
horizon/`characters` block for them if the brief actually names one.

Why this exists: a /simulate subagent dispatched fresh per pass shares no context or cache with any
other pass, so every separate Bash call re-pays that pass's entire growing context. See the repo's own
memory note "simulate-token-efficiency" (2026-08-10 pilot) - batching mechanical calls into driver
scripts cut tool calls per pass from ~15-20 to ~5.4 and kept a 115-pass run inside one usage window.
This script (plus pass_record.py and pass_apply.py) is that same pattern rebuilt for the current
mechanism, which has grown since (survival/energy, death-legacy, reproduction moved post-scene,
resonance/synthesis) - the 2026-08-10 versions never covered any of that.

Prints one combined JSON block (never write it to a file yourself - the model reads this call's own
stdout) with both participants' pre-scene band (the band only: `ending` and `lived` are not the
enacter's to see, and nothing downstream reads them from here - pass_apply.py and the driver's
apply_solo() re-read horizon.py) plus the full brief simulate_pass_brief.py already wrote to
.simulate_pass_brief.json. Nothing here makes a judgment call; everything decidable by a
script already was, by the scripts this only sequences.

Also includes a `characters` block (added 2026-08-29, round-3 debrief) - each participant's
criterion (standard/wasted_life/trusts/distrusts/anchor) and, if they have one, their arc's own
premise/about/needs. This was the one piece of the design principle "script everything that can be
scripted" this driver hadn't actually reached yet: the orchestrator was re-deriving this every pass
with an ad-hoc `py -c` one-liner and then hand-composing it into prose for the enacter dispatch -
both steps mechanical, neither one needing a judgment call, so both belong here instead. The enacter
should now receive this script's raw JSON output directly (plus the fixed instruction preamble and,
when a gate hit needs one, a short one-sentence director's note) - never a hand-paraphrased retelling
of it. See `.claude/PRINCIPLES.md`'s "script everything that can be scripted" principle.

Knowledge and place (added 2026-10-17, the author's call on "what the enacter is given"): each
participant's `characters` entry also carries their `name` and their WHOLE knowledge sample resolved
from refs to text (education keyed by its ref, so a claim can be tagged with it; experience as text,
which is where the hearsay they carry lives), and the combined block carries the scene's `place`
(from encodings `locations`) and the universal `facts`. `_lore/tuning.json` `enacter_knowledge` can cap
the two lists; the default is no cap.

Usage:
    py scripts/lore/pass_prep.py --p1 khaoe --pass-number 12
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
import travel_graph  # noqa: E402
import temperament  # noqa: E402
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
TUNING_PATH = ROOT / "_lore" / "tuning.json"
FACTS_PATH = ROOT / "_lore" / "facts" / "facts.json"


def run(args: list) -> str:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"{' '.join(args)} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def parse_horizon(output: str) -> dict:
    fields = {}
    for line in output.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return {"band": fields.get("band"), "lived": int(fields.get("lived", 0)), "ending": fields.get("ending") == "true"}


def enacter_horizon(parsed: dict) -> dict:
    """What the enacter may see of a horizon reading: the band and nothing else. `ending` and `lived`
    stay with the orchestrator and the driver (pass_apply.py/apply_solo() re-read horizon.py for their
    own bookkeeping); the lifespan is meant to be secret, and the preamble tells the model it cannot
    know whether a scene is a last one (author's call 2026-10-17)."""
    return {"band": parsed.get("band")}


def _tuning() -> dict:
    return json.loads(TUNING_PATH.read_text(encoding="utf-8")).get("enacter_knowledge") or {}


def _index_encodings(enc: dict) -> dict:
    """{ref: text} for every thing a knowledge ref can point at, built once per call. A ref is
    "<category>: <id>" (education items) as sample_lore_knowledge.py writes them."""
    out = {}
    for c in enc.get("concepts", []) or []:
        name = (c.get("names") or [c.get("id")])[0]
        out[f"concept: {c['id']}"] = f"{name}: {c.get('description', '')}".strip()
    for c in enc.get("conflicts", []) or []:
        out[f"conflict: {c['id']}"] = f"{c.get('topic', '')}: {c.get('detail', '')}".strip()
    for c in enc.get("locations", []) or []:
        out[f"location: {c['id']}"] = _place_text(c)
    for c in enc.get("characters", []) or []:
        out[f"character: {c['id']}"] = (c.get("description") or c.get("summary") or c.get("notes") or "").strip()
    for c in enc.get("routes", []) or []:
        out[f"route: {c['id']}"] = (c.get("description") or c.get("notes") or "").strip()
    for t in (enc.get("tales") or {}).get("entries", []) or []:
        out[f"tale: {t['id']}"] = t.get("summary", "")
    for h in (enc.get("hearsay") or {}).get("entries", []) or []:
        for i, claim in enumerate(h.get("claims", []), 1):
            out[f"hearsay: {h['id']}#{i}"] = claim.get("text", "")
    return out


def _place_body(loc: dict) -> str:
    return " ".join(str(loc.get(k)).strip() for k in ("description", "composition", "notes") if loc.get(k))


def _place_text(loc: dict) -> str:
    name = (loc.get("names") or [loc.get("id")])[0]
    body = _place_body(loc)
    return f"{name}: {body}" if body else name


def place_block(location: str | None, enc: dict | None = None) -> dict | None:
    """The scene's place, from encodings `locations` (description/composition, or the notes field
    this corpus' locations use), matched by id or by any of its names. None if the pass has no
    resolvable place (a made-up string). A road node (`road:<a>--<b>`, derived from the connections
    between places) is described from a template on its endpoints' names, no authoring needed
    (travel_graph.describe_road)."""
    if not location:
        return None
    enc = enc or json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))
    if travel_graph.is_road(location):
        return travel_graph.describe_road(location, enc)
    norm = lambda x: "".join(ch for ch in str(x).lower() if ch.isalnum())
    want = norm(location)
    for loc in enc.get("locations", []) or []:
        if want in {norm(loc.get("id", ""))} | {norm(n) for n in loc.get("names") or []}:
            return {"name": (loc.get("names") or [loc["id"]])[0], "description": _place_body(loc)}
    return None


def knowledge_block(char: dict, index: dict) -> dict:
    """A participant's whole knowledge sample as text: education refs resolved through the index
    ({ref: text}; an unresolved ref stays as the bare ref), experience entries as their text (this is
    where the hearsay they carry lives, "Grew up hearing: ..."). Education is keyed by its ref so a
    claim can be tagged with it, copied exactly. `_lore/tuning.json` `enacter_knowledge` can cap each
    list; null (the default) means everything."""
    cfg = _tuning()
    know = char.get("knowledge") or {}
    items = list((know.get("education") or {}).get("items") or [])
    if cfg.get("max_education_items") is not None:
        items = items[: cfg["max_education_items"]]
    exp = [e.get("text", "") if isinstance(e, dict) else str(e) for e in (know.get("experience") or [])]
    exp = [e for e in exp if e.strip()]
    if cfg.get("max_experience_items") is not None:
        exp = exp[-cfg["max_experience_items"]:] if cfg["max_experience_items"] else []
    return {"education": {ref: index.get(ref) or ref for ref in items}, "experience": exp}


def universal_facts() -> list:
    """Facts every character knows in full (never sampled): title and text only. The `withheld`
    notes in facts.json are for the orchestrator, not the enacter."""
    if not FACTS_PATH.exists():
        return []
    facts = json.loads(FACTS_PATH.read_text(encoding="utf-8")).get("facts", [])
    return [f"{f.get('title', '')}: {f.get('text', '')}".strip(": ") for f in facts]


def load_character_brief(slug: str, context: str, index: dict | None = None) -> dict:
    """Everything a scene needs about a character that isn't already in the mechanical brief: their
    criterion (the thing their whole standard is judged against), their routine for THIS pass's own
    `context` if one exists (added 2026-08-29, same debrief as the criterion/arc_premise fields below
    - a routine's own `routine_actions` text is exactly what grounds a character's ordinary behavior
    in a given setting, and picking the one matching the pass's context is itself mechanical, not a
    judgment call), and, if they have one, their arc's own premise text - never the character's full
    file, which is far more than an enacter needs and would just cost tokens re-sending it."""
    path = CHAR_DIR / f"{slug}.json"
    if not path.exists():
        return {}
    char = json.loads(path.read_text(encoding="utf-8"))
    criterion = char.get("criterion") or {}
    result = {
        "name": char.get("name", slug),
        "criterion": {
            "standard": criterion.get("standard"),
            "wasted_life": criterion.get("wasted_life"),
            "trusts": criterion.get("trusts"),
            "distrusts": criterion.get("distrusts"),
            "anchor": criterion.get("anchor"),
        }
    }
    # A few words for how they tend to act, from the four traits (temperament.words); nothing at all for
    # a neutral character, so the brief only grows for those who have something to say.
    tw = temperament.words(char, (json.loads(TUNING_PATH.read_text(encoding="utf-8")).get("temperament") or {}).get("word_threshold", 0.4))
    if tw:
        result["temperament"] = tw
    routine = next((r for r in char.get("routines", []) if r.get("context") == context), None)
    if routine:
        result["routine"] = {"location": routine.get("location"), "routine_actions": routine.get("routine_actions")}
    arc = char.get("arc")
    if arc and arc.get("resolution") == "ongoing":
        result["arc_premise"] = {
            "about": arc.get("about"),
            "needs": arc.get("needs"),
            "premise": arc.get("premise"),
        }
    result["knowledge"] = knowledge_block(char, index if index is not None else _index_encodings(json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))))
    return result


def enacter_input(brief: dict, horizon_parsed: dict) -> dict:
    """The combined JSON the enacter receives (and the driver/orchestrator pass straight through):
    `horizon_pre` (band only), the mechanical `brief`, a `characters` block with each participant's
    criterion, routine, arc premise AND knowledge, the `place`, and the universal `facts`. Built in one
    place so the Claude-subagent path, the Ollama path and the driver's resume path cannot drift."""
    enc = json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))
    index = _index_encodings(enc)
    context = brief.get("context")
    slugs = [brief["participant_1"]] + ([brief["participant_2"]] if brief.get("participant_2") else [])
    return {
        "horizon_pre": {s: enacter_horizon(horizon_parsed[s]) for s in slugs},
        "brief": brief,
        "characters": {s: load_character_brief(s, context, index) for s in slugs},
        "place": place_block(brief.get("location"), enc),
        "facts": universal_facts(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    p1 = args.p1.lower()

    horizon = {p1: parse_horizon(run([str(SCRIPTS_DIR / "horizon.py"), p1]))}

    brief_cmd = [str(SCRIPTS_DIR / "simulate_pass_brief.py"), "--p1", p1, "--pass-number", str(args.pass_number)]
    run(brief_cmd)

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))

    p2 = brief.get("participant_2")
    if p2:
        horizon[p2] = parse_horizon(run([str(SCRIPTS_DIR / "horizon.py"), p2]))

    print(json.dumps(enacter_input(brief, horizon), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
