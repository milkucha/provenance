"""
Shared plumbing for /simulate's mechanical pass pipeline - originally lived only inside
simulate_generate_population.py (the `-generate` mode driver), extracted 2026-08-13 so the
interactive/showcase-trail mode's own pre-scene and post-scene drivers (simulate_pass_brief.py,
simulate_pass_resolve.py) can reuse the exact same tested sibling-script wrappers instead of a
second, subtly-different reimplementation. Not a standalone script - import from a sibling driver.

Step 5's archetype lookup is folded directly into `resolve_location()` here (design debrief
2026-08-13): a plain dict lookup in _lore/archetypes.json never needed its own pipeline step, only a
caller who already has both the resolved location and the home-frame character's routines - which
this function has by construction, since it's the one that just resolved them.

Usage (from a sibling script in this same directory):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import simulate_pass_lib as lib
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402

T = tuning.load()
PARTNER_THRESHOLD = T["partner_threshold"]
PARENT_COOLDOWN_PASSES = T["parent_cooldown_passes"]
CHILD_COOLDOWN_PASSES = T["child_cooldown_passes"]
LEAD_EXPIRY_PASSES = T["lead_expiry_passes"]
ARC_RESOLUTION_THRESHOLD = T["arc_resolution_threshold"]

ARCHETYPES = json.loads((ROOT / "_lore" / "archetypes.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------
# Plumbing: character file I/O, sibling-script invocation, stdout parsing
# --------------------------------------------------------------------------------------------

def load_char(key: str) -> dict:
    path = CHAR_DIR / f"{key}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_char(key: str, character: dict) -> None:
    path = CHAR_DIR / f"{key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def call(script_name: str, argv: list) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *argv],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} {argv} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def kv(stdout: str) -> dict:
    """Parses top-level (non-indented) 'key: value' lines into a dict. Indented lines (e.g. a
    script's per-item '  notified: x' listing) are deliberately excluded - use a dedicated
    line-scraper (see notified_keys()) for those instead."""
    out = {}
    for line in stdout.splitlines():
        if not line or line[0] in " \t":
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def notified_keys(stdout: str) -> list:
    return re.findall(r"^\s+notified:\s+(\S+)", stdout, re.MULTILINE)


# --------------------------------------------------------------------------------------------
# Sibling-script wrappers (one per scripts/lore/*.py this pipeline calls)
# --------------------------------------------------------------------------------------------

def pick_pair(pool: list) -> tuple:
    d = kv(call("pick_pair.py", pool))
    return d["participant_1"], d["participant_2"]


def roll_lead_followup(leads: list) -> dict:
    return kv(call("roll_lead_followup.py", ["--leads", *leads]))


def roll_routine(routines: list) -> str:
    args = [f"{r['location']}:{r['weight']}" for r in routines]
    return kv(call("roll_routine.py", args))["routine"]


def resolve_archetype_for_location(character: dict, location: str) -> str:
    for r in character.get("routines", []):
        if r["location"] == location:
            return r["archetype"]
    raise RuntimeError(f"'{character.get('name')}' has no routine at location '{location}'.")


def resolve_location(p1: str, p1_routine: str, p1_char: dict, p2: str, p2_routine: str, p2_char: dict) -> dict:
    """Folds the old separate steps 3/4/5 (routine resolution -> location resolution -> archetype
    lookup) into one call: resolves mode/location/home_frame/traveler via resolve_location.py, then
    looks up whichever routine matched that location on the home-frame character's own file for its
    archetype, texture, and provides tags - a plain dict fetch, never worth a script of its own."""
    out = kv(call("resolve_location.py", [
        "--p1", p1, "--p1-routine", p1_routine, "--p2", p2, "--p2-routine", p2_routine,
    ]))
    home_frame_char = p1_char if out["home_frame"] == p1 else p2_char
    archetype = resolve_archetype_for_location(home_frame_char, out["location"])
    out["archetype"] = archetype
    out["texture"] = ARCHETYPES[archetype]["texture"]
    out["provides"] = ARCHETYPES[archetype]["provides"]
    return out


def check_needs_provides(needs: list, provides: list) -> dict:
    args = []
    for n in needs:
        args += ["--needs", n]
    for p in provides:
        args += ["--provides", p]
    return kv(call("check_needs_provides.py", args))


def roll_arc_primacy(p1: str, p2: str) -> str:
    return kv(call("roll_arc_primacy.py", ["--p1", p1, "--p2", p2]))["primary"]


def peer_knowledge_items(character: dict, cap: int = 15) -> list:
    items = []
    for entry in character.get("knowledge", {}).get("experience", []):
        if isinstance(entry, dict) and entry.get("about"):
            about = entry["about"]
            tags = about if isinstance(about, list) else [about]
            items.append(f"{entry.get('text', '')}::{','.join(tags)}")
    return items[-cap:]


def check_arc_alignment(arc_about: list, arc_needs: list, peer: dict) -> dict:
    args = []
    for tag in arc_about:
        args += ["--arc-about", tag]
    for tag in arc_needs:
        args += ["--arc-needs", tag]
    criterion = peer.get("criterion", {})
    args += ["--peer-standard", criterion.get("standard", "")]
    args += ["--peer-wasted-life", criterion.get("wasted_life", "")]
    for item in peer_knowledge_items(peer):
        args += ["--peer-knowledge-item", item]
    out = kv(call("check_arc_alignment.py", args))
    out["matched_about"] = [t for t in out.get("matched_about", "").split(",") if t]
    return out


def roll_contested() -> bool:
    return kv(call("roll_contested.py", []))["contested"] == "true"


def roll_arc_outcome(inclined: str) -> str:
    return kv(call("roll_arc_outcome.py", ["--inclined", inclined]))["outcome"]


def record_partner(key: str, other: str) -> None:
    call("record_partner.py", [key, "--with", other])


def roll_reproduction(p1: str, p2: str) -> dict:
    return kv(call("roll_reproduction.py", ["--p1", p1, "--p2", p2]))


def generate_offspring(parent_a: str, parent_b: str, name: str, pass_number: int) -> dict:
    stdout = call("generate_offspring.py", [
        "--parent-a", parent_a, "--parent-b", parent_b, "--name", name, "--pass-number", str(pass_number),
    ])
    born_match = re.search(r"^born: (\S+) \(", stdout, re.MULTILINE)
    eligible_match = re.search(r">=\s*(\d+)", stdout)
    return {
        "slug": born_match.group(1),
        "eligible_pass": int(eligible_match.group(1)),
        "stdout": stdout,
    }


def horizon(key: str) -> dict:
    return kv(call("horizon.py", [key]))


def record_death(key: str) -> dict:
    stdout = call("record_death.py", [key])
    return {"notified": notified_keys(stdout), "stdout": stdout}


def roll_death_legacy(candidates: list) -> dict:
    return kv(call("roll_death_legacy.py", ["--candidates", *candidates]))


def update_character_lived(key: str, delta: int = 1) -> None:
    call("update_character.py", [key, "--lived-delta", str(delta)])


def register_arc_concept(key: str) -> str:
    return call("register_arc_concept.py", [key])


def tally(history: list) -> int:
    last_transform = -1
    for i, h in enumerate(history):
        if h.get("outcome") == "transform":
            last_transform = i
    relevant = history[last_transform + 1:]
    score = {"advance": 1, "stall": 0, "reverse": -1}
    return sum(score.get(h.get("outcome"), 0) for h in relevant)
