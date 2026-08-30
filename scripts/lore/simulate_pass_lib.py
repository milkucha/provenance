"""
Shared plumbing for /enact's mechanical grounding block - originally lived only inside
simulate_generate_population.py (the `/generate` driver), extracted 2026-08-13 so
simulate_pass_brief.py (`/enact`'s own Step 4) and apply_death_legacy.py/roll_death_legacy.py
(`/enact`'s own Step 8) can reuse the exact same tested sibling-script wrappers instead of a
second, subtly-different reimplementation. Not a standalone script - import from a sibling driver.

Step 5's context lookup is folded directly into `resolve_location()` here (design debrief
2026-08-13): a plain dict lookup in _lore/contexts.json never needed its own pipeline step, only a
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
import rng_context  # noqa: E402

T = tuning.load()
PARTNER_THRESHOLD = T["partner_threshold"]
PARENT_COOLDOWN_PASSES = T["parent_cooldown_passes"]
CHILD_COOLDOWN_PASSES = T["child_cooldown_passes"]
LEAD_EXPIRY_PASSES = T["lead_expiry_passes"]
ARC_RESOLUTION_THRESHOLD = T["arc_resolution_threshold"]
SURVIVAL = T["survival"]

CONTEXTS = json.loads((ROOT / "_lore" / "contexts.json").read_text(encoding="utf-8"))


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
    stochastic = script_name in rng_context.STOCHASTIC_SCRIPTS and "--seed" not in argv
    seed = draw_index = None
    if stochastic:
        seed, draw_index = rng_context.reserve_seed(ROOT)
        if seed is not None:
            argv = [*argv, "--seed", str(seed)]

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *argv],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} {argv} failed (exit {result.returncode}):\n{result.stderr}")

    if stochastic:
        rng_context.log_draw(ROOT, script_name, argv, kv(result.stdout), seed, draw_index)

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


def resolve_context_for_location(character: dict, location: str) -> str:
    for r in character.get("routines", []):
        if r["location"] == location:
            return r["context"]
    raise RuntimeError(f"'{character.get('name')}' has no routine at location '{location}'.")


def roll_home_visit(p1: str, p2: str, p1_choice: str = "none", p2_choice: str = "none") -> tuple:
    """Design debrief 2026-08-28: decides who's home BEFORE any routine gets rolled, replacing the
    old order (roll both routines independently, then compare to resolve home-turf-vs-visit).
    `p1_choice`/`p2_choice` are each participant's own roll_survival() result for this pass (see
    below) - a "survive" lean skews the coin toward that participant staying home."""
    d = kv(call("roll_home_visit.py", [
        "--p1", p1, "--p2", p2, "--p1-choice", p1_choice, "--p2-choice", p2_choice,
    ]))
    return d["home"], d["visiting"]


# --------------------------------------------------------------------------------------------
# Survival mechanism (design session 2026-08-28) - roll_survival() BEFORE roll_home_visit() (it
# reads a character's own home location, not the pass's eventual one); apply_survival() and
# apply_upkeep() AFTER, once the pass's actual location is resolved. See TODO.md's "Survival
# mechanism" entry for the full math.
# --------------------------------------------------------------------------------------------

def roll_survival(key: str, home_location: str) -> dict:
    out = kv(call("roll_survival.py", ["--key", key, "--location", home_location]))
    return out


def apply_survival(key: str, location: str, choice: str) -> dict:
    out = kv(call("apply_survival.py", ["--key", key, "--location", location, "--choice", choice]))
    out["died"] = out["died"] == "true"
    out["energy"] = int(out["energy"])
    return out


def apply_upkeep(location: str) -> dict:
    return kv(call("apply_upkeep.py", ["--location", location]))


def assemble_location(home: str, home_routine: str, visiting: str, home_char: dict) -> dict:
    """No script call - a plain assembly, same discipline as the context/texture lookup this always
    folded in. With only the home participant ever rolling a routine (roll_home_visit.py already
    decided home; roll_routine.py only ever runs for them now), there's nothing left to resolve by
    comparison: location IS the home participant's own rolled routine, home_frame IS them, traveler
    IS whoever else. Replaces the old resolve_location.py + its "coincidence" mode outright - that
    mode depended on two independently-rolled routines, and only one is ever rolled per pass now."""
    context = resolve_context_for_location(home_char, home_routine)
    return {
        "location": home_routine, "home_frame": home, "traveler": visiting,
        "context": context, "texture": CONTEXTS[context]["texture"], "provides": CONTEXTS[context]["provides"],
    }


def check_needs_provides(needs: list, provides: list) -> dict:
    args = []
    for n in needs:
        args += ["--needs", n]
    for p in provides:
        args += ["--provides", p]
    return kv(call("check_needs_provides.py", args))


def roll_arc_primacy(p1: str, p2: str) -> str:
    return kv(call("roll_arc_primacy.py", ["--p1", p1, "--p2", p2]))["primary"]


def ancestors_of(key: str, cache: dict | None = None) -> set:
    """Every ancestor of `key`, walking `parents` all the way up (parents, grandparents,
    great-grandparents, ...) - not just the immediate one. A founder (no `parents` field) returns an
    empty set. `cache`, if given, memoizes per-key results across many calls in one long-running
    process (2026-08-17 fix, see LAB_REPORT.md Run 4/5: `/generate` calls this every pass for
    up to thousands of passes, and a lineage 20+ generations deep would otherwise re-walk and re-load
    the same ancestor chain from disk repeatedly)."""
    if cache is not None and key in cache:
        return cache[key]
    direct = load_char(key).get("parents", [])
    result = set(direct)
    for p in direct:
        result |= ancestors_of(p, cache)
    if cache is not None:
        cache[key] = result
    return result


def already_related(key1: str, char1: dict, key2: str, char2: dict, cache: dict | None = None) -> bool:
    """True if key1/key2 must not reproduce together: either is an ancestor of the other (any number
    of generations - parent, grandparent, great-grandparent, ...), or they share at least one parent
    (full or half sibling). Cousins (share only a grandparent, not a parent) are deliberately
    allowed - excluding them too would exhaust a small closed founding population's eligible pairs
    even faster, and `/generate`'s own intent is a starting population that stays somewhat
    homogeneous (a town/dynasty), not one engineered for maximum diversity. See LAB_REPORT.md Run 4's
    entry on population convergence for why this replaced the old direct-parent-only check (2026-08-17)."""
    if key2 in ancestors_of(key1, cache) or key1 in ancestors_of(key2, cache):
        return True
    return bool(set(char1.get("parents", [])) & set(char2.get("parents", [])))


def peer_knowledge_items(character: dict, cap: int = 15) -> list:
    """Candidate items fed to check_arc_alignment.py's gate. Experience entries with an explicit
    `about` tag come first (richest, narrated text - what /enact's interactive mode actually
    produces). Any remaining cap budget is filled with a random sample of the character's own
    `knowledge.education.items` (2026-08-17 fix, see LAB_REPORT.md Run 4: the gate previously only
    ever saw `about`-tagged experience entries, which nothing in `/generate`'s own data pipeline
    produces - `generate_offspring.py` only ever appends bare, untagged strings - so the gate silently
    missed every single time across a whole 2000-pass run, for every character, founders included. A
    bare education item doubles as both its own searchable text and its own tag, since that's exactly
    the vocabulary an arc's own about/needs tags are already written in - no format conversion needed)."""
    exp_items = []
    for entry in character.get("knowledge", {}).get("experience", []):
        if isinstance(entry, dict) and entry.get("about"):
            about = entry["about"]
            tags = about if isinstance(about, list) else [about]
            exp_items.append(f"{entry.get('text', '')}::{','.join(tags)}")
    exp_items = exp_items[-cap:]

    remaining = cap - len(exp_items)
    edu_items = []
    if remaining > 0:
        pool = character.get("knowledge", {}).get("education", {}).get("items", [])
        rng = rng_context.local_random("peer_knowledge_items", ROOT)
        sample = rng.sample(pool, min(remaining, len(pool))) if pool else []
        edu_items = [f"{item}::{item}" for item in sample]

    return exp_items + edu_items


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


def roll_contested(strength: int = 0, quality: int = 0) -> bool:
    args = ["--strength", str(strength), "--quality", str(quality)]
    return kv(call("roll_contested.py", args))["contested"] == "true"


def roll_arc_outcome(inclined: str, contested: bool = False) -> str:
    args = ["--inclined", inclined]
    if contested:
        args.append("--contested")
    return kv(call("roll_arc_outcome.py", args))["outcome"]


def record_partner(key: str, other: str) -> None:
    call("record_partner.py", [key, "--with", other])


BOND_QUALITY_DELTA = {"help": 1, "hinder": -1, "mixed": 0, "neutral": 0}


def record_bond_quality(key: str, other: str, delta: int) -> None:
    call("record_bond_quality.py", [key, "--with", other, "--delta", str(delta)])


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


def record_death(key: str, cause: str | None = None) -> dict:
    argv = [key] + (["--cause", cause] if cause else [])
    stdout = call("record_death.py", argv)
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
