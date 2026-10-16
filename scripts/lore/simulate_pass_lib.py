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
from random import Random

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402
import rng_context  # noqa: E402
import location_context  # noqa: E402
import travel_graph  # noqa: E402

T = tuning.load()
PARTNER_THRESHOLD = T["partner_threshold"]
PARENT_COOLDOWN_PASSES = T["parent_cooldown_passes"]
CHILD_COOLDOWN_PASSES = T["child_cooldown_passes"]
LEAD_EXPIRY_PASSES = T["lead_expiry_passes"]
ARC_RESOLUTION_THRESHOLD = T["arc_resolution_threshold"]
SURVIVAL = T["survival"]
ARC_MATCH_BOOST_FACTOR = T["arc_match_boost_factor"]
ARC_PAYMENT = T["arc_payment"]

CONTEXTS = json.loads((ROOT / "_lore" / "contexts.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------
# Plumbing: character file I/O, sibling-script invocation, stdout parsing
# --------------------------------------------------------------------------------------------

def load_char(key: str) -> dict:
    path = CHAR_DIR / f"{key}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all_characters() -> dict:
    """Every real character file in _lore/characters/, keyed by slug - excludes `_template.json` and
    `lifespans.json`, same convention `notify_death.py`/`location_context.py --live` already use.
    Fresh off disk every call (no caching) - the pass mechanics run at most a handful of times a
    process, and staleness would be a much worse bug than the extra reads."""
    out = {}
    for path in CHAR_DIR.glob("*.json"):
        if path.stem in ("_template", "lifespans"):
            continue
        with open(path, encoding="utf-8") as f:
            try:
                out[path.stem] = json.load(f)
            except json.JSONDecodeError:
                continue
    return out


def load_encodings() -> dict:
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
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

def draw_participant(pool: list) -> str:
    """Replaces the old pick_pair()'s draw-two behavior (design session 2026-09-13, asymmetric
    per-pass rewrite) - draws exactly one `p1`, uniform, unweighted. There is no second participant
    to fix up front any more; see run_pass_mechanics()'s own docstring for how one gets discovered
    (or doesn't) over the rest of the pass."""
    return kv(call("pick_pair.py", pool))["participant"]


def roll_lead_followup(leads: list) -> dict:
    return kv(call("roll_lead_followup.py", ["--leads", *leads]))


def roll_routine(routines: list) -> str:
    args = [f"{r['location']}:{r['weight']}" for r in routines]
    return kv(call("roll_routine.py", args))["routine"]


def roll_routine_boosted(routines: list, boost_locations: set) -> str:
    """Step 4's own-routine preference (design session 2026-09-13): any of `routines` whose
    `location` is in `boost_locations` (the caller has already worked out which of this character's
    own routines have a context that provides their arc's matched need) gets its weight multiplied by
    `ARC_MATCH_BOOST_FACTOR` before the ordinary weighted pick - favored, not forced, same "skew,
    never decide" discipline as everywhere else in this pipeline."""
    args = []
    for r in routines:
        weight = r["weight"] * ARC_MATCH_BOOST_FACTOR if r.get("location") in boost_locations else r["weight"]
        args.append(f"{r['location']}:{weight}")
    return kv(call("roll_routine.py", args))["routine"]


def resolve_context_for_location(character: dict, location: str) -> str:
    for r in character.get("routines", []):
        if r["location"] == location:
            return r["context"]
    raise RuntimeError(f"'{character.get('name')}' has no routine at location '{location}'.")


def roll_meetable(candidates: list, favor: str | None = None) -> dict:
    """Step 6's "missed connection" roll (design session 2026-09-13) - see roll_meetable.py's own
    docstring. Caller must not call this with an empty `candidates` list; an empty pool is an
    automatic miss per the design conversation, with nothing to roll."""
    args = ["--candidates", *candidates]
    if favor:
        args += ["--favor", favor]
    out = kv(call("roll_meetable.py", args))
    out["met"] = out["met"] == "true"
    return out


def candidates_at(location: str, all_characters: dict, exclude: str) -> list:
    """Every LIVING character key (excluding `exclude`) in `all_characters` (load_all_characters()'s
    own shape - key -> character dict) with a routines[] entry at exactly `location` - Step 6's
    candidate pool for the meetable roll. Sorted, so a seeded draw over it is reproducible. The dead
    are filtered out (audit F3: 13 of 35 candidates at one corpus city were dead)."""
    out = []
    for key, char in sorted(all_characters.items()):
        if key == exclude or (char.get("life") or {}).get("deceased"):
            continue
        if any(r.get("location") == location for r in (char.get("routines") or [])):
            out.append(key)
    return out


def _logged_rng(context_name: str, argv: list) -> tuple:
    """A `Random` seeded through rng_context like every scripted roll (so a seeded run replays it),
    plus the (seed, draw_index) the caller hands to `rng_context.log_draw` once it knows the result.
    For rolls that live in this module instead of a sibling script (the payment gate does the same)."""
    seed, draw_index = rng_context.reserve_seed(ROOT)
    return Random(seed), seed, draw_index


def draw_destination(p1_key: str, need: str, options: list) -> dict:
    """Pursuit redesign (2026-10-17): the weighted draw over `location_context.destination_options()`.
    Logged to the draw audit as `pursuit_destination` with the weights it drew from."""
    rng, seed, draw_index = _logged_rng("pursuit_destination", [p1_key, need])
    chosen = location_context.pick_destination(options, rng)
    rng_context.log_draw(
        ROOT, "pursuit_destination", [p1_key, need],
        {"chosen": chosen["location"], "weights": {o["location"]: o["weight"] for o in options}}, seed, draw_index,
    )
    return chosen


def draw_bystander(p1_key: str, pool: list) -> str:
    """Pursuit redesign: with nobody useful at the place, the scene goes to someone else who is
    there. Uniform over the living residents present; logged as `pursuit_bystander`."""
    rng, seed, draw_index = _logged_rng("pursuit_bystander", [p1_key])
    chosen = rng.choice(sorted(pool))
    rng_context.log_draw(ROOT, "pursuit_bystander", [p1_key, *sorted(pool)], {"chosen": chosen}, seed, draw_index)
    return chosen


def roll_routine_at(character: dict, location: str) -> dict:
    """A character's routine roll restricted to the routines they have AT `location` (weights
    kept). For a bystander the draw already says they are there; this only decides what they are
    doing, which gives the scene its context."""
    here = [r for r in (character.get("routines") or []) if r.get("location") == location]
    # roll_routine.py draws by name; the names here are the contexts, so two routines at one place
    # stay distinguishable
    chosen = roll_routine([{"location": r["context"], "weight": r["weight"]} for r in here])
    return next(r for r in here if r["context"] == chosen)


# --------------------------------------------------------------------------------------------
# Energy/eating mechanism (design session 2026-08-28; economy rewrite 2026-10-17) - roll_survival()
# (work vs. arc) against a character's own home `location` field; apply_survival()/apply_upkeep()
# AFTER, once the pass's actual location is resolved. See TODO.md's "Economy rewrite" entry.
# --------------------------------------------------------------------------------------------

def roll_survival(key: str, home_location: str) -> dict:
    out = kv(call("roll_survival.py", ["--key", key, "--location", home_location]))
    return out


def apply_survival(key: str, location: str, choice: str) -> dict:
    out = kv(call("apply_survival.py", ["--key", key, "--location", location, "--choice", choice]))
    out["died"] = out["died"] == "true"
    out["energy"] = int(out["energy"])
    out["provisions"] = float(out["provisions"])
    return out


def apply_upkeep(location: str) -> dict:
    return kv(call("apply_upkeep.py", ["--location", location]))


def arc_payment_gate(p1_key: str, p2_key: str, arc: dict) -> dict:
    """Step 8's payment gate (design session 2026-09-13, asymmetric per-pass rewrite) - the single,
    clear owner of "is this pass economically motivated," replacing check_needs_provides.py's old
    word-overlap role in that spot (check_needs_provides.py itself is untouched and still used
    elsewhere - see needs_candidates()'s own import of its significant_words()).

    Hard gate: p1's own `provisions` must already cover `arc_payment.arc_need_cost`
    (_lore/tuning.json) or this is an automatic failure, no roll at all. Otherwise rolls a graded
    probability: `odds_percent.base` plus `surplus_weight` scaled by p1's surplus above the cost
    (normalized against `survival.provides_provisions_threshold`, same normalization style
    roll_survival.py's own personal_cushion/pool_surplus terms use) and damped by `(1 - ratio)`,
    where `ratio` is the arc's current tally-to-ARC_RESOLUTION_THRESHOLD ratio (0 at arc start,
    approaching 1 near completion) - a near-complete arc leans less on raw economics to advance
    further. On success, transfers `arc_need_cost` in `provisions` from p1 to p2 (both files
    written) - this success is what makes the pass "motivated," gating the unchanged
    contested/alignment/outcome chain below it."""
    cost = ARC_PAYMENT["arc_need_cost"]
    p1_char = load_char(p1_key)
    provisions = p1_char.get("provisions", SURVIVAL["starting_provisions_per_capita"])
    if provisions < cost:
        return {"motivated": False, "reason": "cannot_afford", "odds_used": None, "cost": cost}

    surplus = provisions - cost
    threshold = SURVIVAL["provides_provisions_threshold"]
    surplus_norm = min(1.0, surplus / threshold) if threshold else 0.0
    ratio = min(1.0, abs(tally(arc.get("history", []))) / ARC_RESOLUTION_THRESHOLD) if ARC_RESOLUTION_THRESHOLD else 0.0

    odds = ARC_PAYMENT["odds_percent"]
    pct = odds["base"] + ARC_PAYMENT["surplus_weight"] * surplus_norm * (1 - ratio)
    pct = max(odds["min"], min(odds["max"], pct))

    seed, draw_index = rng_context.reserve_seed(ROOT)
    rng = Random(seed)
    success = rng.random() < (pct / 100.0)
    rng_context.log_draw(
        ROOT, "arc_payment_gate.py", [p1_key, p2_key],
        {"success": success, "odds_used": round(pct, 1)}, seed, draw_index,
    )

    if not success:
        return {"motivated": False, "reason": "payment_failed", "odds_used": round(pct, 1), "cost": cost}

    p1_char["provisions"] = max(0, provisions - cost)  # floored at 0, same as provisions_lib.set_provisions
    save_char(p1_key, p1_char)
    p2_char = load_char(p2_key)
    p2_char["provisions"] = max(0, p2_char.get("provisions", SURVIVAL["starting_provisions_per_capita"]) + cost)
    save_char(p2_key, p2_char)

    return {"motivated": True, "reason": None, "odds_used": round(pct, 1), "cost": cost}


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


# --------------------------------------------------------------------------------------------
# The asymmetric per-pass algorithm (design session 2026-09-13) - shared between simulate_pass_brief.py
# (`/enact`'s own mechanical block, one pair-or-solo pass at a time, brief written to
# .simulate_pass_brief.json) and simulate_generate_population.py (`/generate`'s fast-forward loop, no
# scene, no subagent). Consolidated here rather than duplicated in both callers a second time (the two
# scripts already shared everything above this point) - the two callers differ only in how they
# ENRICH/report `arc_authoring_needed` (full authoring context + tale-writing vs. a queued pending-arc
# entry) and in what they do afterward with `participant_2`/`contested_hinder_slot` (a real subagent
# scene + apply_contested_lead.py vs. always leaving a contested hinder ambient, per
# simulate_generate_population.py's own documented scope limits).
#
# Only `p1` is ever fixed before this runs (draw_participant()). Everything else - whether a second
# participant even exists this pass, and who - is discovered over the course of the algorithm itself:
#   Step 2  roll_survival(p1)                                   - work vs. arc
#   Step 3  work -> p1's own routine roll, apply, DONE        - no second participant, ever. Mid-journey
#           (a kept destination) they work where they stand and the journey survives (audit F7)
#   Step 4  arc, locally satisfiable (and standing at a place of their own routines) -> boosted
#           own-routine roll, apply, DONE                        - pursuit stage local_satisfied
#   Step 5  arc, not locally satisfiable -> destination: the one kept from an earlier pass, or a
#           weighted dice draw over location_context.destination_options() (known suppliers skewed,
#           general places by hops). No option -> DONE (no_target); not there yet -> a mechanical
#           "route" hop, the destination kept in p1's `pursuit` field, DONE (en_route / died_en_route);
#           arrived -> Step 6
#   Step 6  who's about at the arrival place: living residents with a routine there. None -> solo
#           scene (arrived_empty). roll_meetable, favoring a known supplier - miss -> a scene with
#           someone else who is there (arrived_nobody), no purchase, no arc outcome
#   Step 7  p2's own routine roll - routine elsewhere -> as a miss; context doesn't supply the need ->
#           a scene with p2, no purchase (met_mismatch); match -> Step 8
#   Step 8  arc_payment_gate() - fail -> a scene with p2, NO arc outcome rolled (met_cannot_pay);
#           success -> the UNCHANGED contested/alignment/outcome/tally chain, keyed to p1's arc vs.
#           p2 as peer (met_paid)
#
# Every exit of Steps 4-8 sets `result["pursuit"]` {stage, reason, need, place, supplier, present,
# could_afford} (PURSUIT_STAGES, below), and `result["scene"]` ("pair" / "solo" / None) says whether
# the pass is something to dramatize. `motivated` stays what it was: the payment went through.
#
# Partner tracking (record_partner, both directions) fires exactly once, at the point p1 and p2 are
# BOTH confirmed present (Step 7, or a bystander scene) - the earliest point in the new algorithm
# where two characters have actually, verifiably shared a pass, matching the old algorithm's own
# "the moment the pair is fixed" timing as closely as the new asymmetric model allows.
# This is a judgment call, not dictated by the spec - see this rewrite's own report for the reasoning
# and the open question it leaves (whether a payment-gate failure should still count as a "meeting"
# for partner-tracking purposes; it does, here, since the two characters still verifiably crossed
# paths this pass regardless of whether the transaction went through).
#
# `leads`/roll_lead_followup.py/apply_contested_lead.py's OWN follow-up half (the "does p1 chase down
# a named rival" question) has no call site left in this algorithm - see the rewrite's report. Nothing
# here deletes `leads` entries or roll_lead_followup.py itself (out of scope, not asked for), but
# nothing in this pipeline drains them any more either.
# --------------------------------------------------------------------------------------------

# Pursuit stages (brief["pursuit"]["stage"]). Every exit of the pursuit branch of run_pass_mechanics
# sets exactly one. The legend the enacter reads is in enact_preamble.md; keep the two in step.
PURSUIT_STAGES = (
    "local_satisfied",  # the need is met where they live; routine roll, nothing to travel for
    "no_target",        # nowhere reachable supplies the need, so the arc cannot move
    "en_route",         # chose or kept a destination; this pass is a step toward it, no scene
    "arrived_nobody",   # at the destination, the person/place's supplier is not there; scene with someone else present
    "arrived_empty",    # at the destination, nobody else is there at all; solo scene
    "met_mismatch",     # met someone present, but what they are doing this pass does not supply the need; scene
    "met_cannot_pay",   # found the supplier, the purchase did not go through (reason: cannot_afford | payment_failed); scene, no arc outcome rolled
    "met_paid",         # found the supplier and paid; the arc outcome is rolled and the scene dramatizes it
    "died_en_route",    # energy ran out on the road
)

_KEEP = object()


def run_pass_mechanics(p1: str, pass_number: int) -> dict:
    """Runs the full Step 2-8 algorithm for one already-picked `p1`. Returns a result dict shared by
    both callers - see this module's own section docstring above for the field-by-field shape used
    by each step. `arc_authoring_needed`, when present, is a minimal `{"character_slug", "reason"}`
    signal only - each caller enriches it with the full authoring context (band/criterion/routines/
    needs_candidates/prior_arc) and, on `reauthor_complete`, writes the completion tale itself, the
    same division of labor the pre-rewrite simulate_pass_brief.py already used for this exact slot.

    Pursuit redesign (2026-10-17, TODO.md): the pursuit branch (arc chosen, need not met at home)
    now draws its destination with dice (location_context.destination_options), keeps it across
    passes (the character's `pursuit` field) until they arrive, turns a failed arrival into a scene
    instead of a dead pass, and names every exit in `result["pursuit"]` (see PURSUIT_STAGES).
    `result["scene"]` says what the driver should do with the pass: "pair" (a two-character scene,
    `participant_2` set), "solo" (a scene-worthy situation with nobody else in it) or None (no
    scene)."""
    notes: list = []
    p1_char = load_char(p1)
    location_now = p1_char.get("location", "")

    result = {
        "pass": pass_number,
        "participant_1": p1,
        "participant_2": None,
        "location": None,
        "context": None,
        "travel": None,
        "scene": None,
        "pursuit": None,
        "motivated": False,
        "matched_need": None,
        "matched_provide": None,
        "contested": False,
        "arc": {"gate": "miss", "inclined": None, "outcome": None, "tally_result": None, "matched_about": []},
        "arc_authoring_needed": None,
        "contested_hinder_slot": None,
        "survival": {},
        "notes": notes,
    }

    def _own_routine_roll(character: dict) -> str:
        return roll_routine(character.get("routines", []))

    def _write_back(location: str, last_scene: str, pursuit=None) -> None:
        """Task fix (2026-09-13 smoke test): the automated `/simulate` pipeline (pass_apply.py,
        simulate_driver.py's apply_solo()) never wrote `location`/`places_visited`/`last_scene` back
        to a character's file - only /enact's own interactive Step 10 did. That silently broke the
        new multi-hop travel mechanism: a traveling character's `location` never advanced, so every
        subsequent pass re-pathfound from the exact same starting point forever. Fixed here, in the
        one place both automated callers (simulate_pass_brief.py -> pass_prep.py -> simulate_driver.py,
        and simulate_generate_population.py) and the interactive path funnel through, rather than in
        either pass_apply.py or simulate_driver.py's apply_solo() individually - a solo pass (which
        covers every en-route travel hop) never reaches either of those, so fixing only one of them
        would have left this exact bug in place. Read fresh and saved immediately, same
        read-modify-save discipline apply_survival.py and every other sibling script in this pass
        already use, so this can't race or clobber a write made earlier in the same pass.

        Interactive /enact's own Step 10 still runs afterward and is unaffected: it overwrites
        `last_scene` with the actual dramatized summary (per its own docs, `last_scene` is
        "overwritten every run, never accumulated") and re-sets `location`/`places_visited` to the
        same values this already wrote, a harmless no-op.

        Also owns the character's `pursuit` field (the destination they are walking toward): a dict
        while a journey is in progress, cleared (None) by every other exit, so the default is to end
        the journey. `_KEEP` leaves it as it is."""
        character = load_char(p1)
        character["location"] = location
        visited = character.setdefault("places_visited", [])
        if location not in visited:
            visited.append(location)
        character["last_scene"] = last_scene
        if pursuit is not _KEEP:
            if pursuit:
                character["pursuit"] = pursuit
            else:
                character.pop("pursuit", None)
        save_char(p1, character)

    afford = {"v": None}  # set by _apply_p1 (after eating) and read by _pursuit; see could_afford below

    def _apply_p1(location: str, choice: str, context: str | None) -> dict:
        """Applies apply_upkeep/apply_survival for p1 at `location` and writes the common result
        fields every branch below needs - `context` is always the caller's own explicit call (a
        routine roll's resolved context, "route" for a mechanical travel override, or None when no
        routine was rolled at all this pass), never guessed here."""
        apply_upkeep(location)
        effect = apply_survival(p1, location, choice)
        # Means as of now, after this pass's eating: what the payment gate will see (see `afford` below).
        afford["v"] = effect["provisions"] >= ARC_PAYMENT["arc_need_cost"]
        result["location"] = location
        result["context"] = context
        result["survival"][p1] = {"choice": choice, "energy": effect["energy"], "died": effect["died"]}
        if effect["died"]:
            notes.append(f"{p1}'s energy hit 0 - exhaustion/starvation, not yet recorded (post-scene step)")
        return effect

    # A journey in progress (the `pursuit` field) is dropped if the arc it was for is gone or no
    # longer wants that need - a finished, failed or re-authored arc does not keep walking.
    arc = p1_char.get("arc") or {}
    journey = p1_char.get("pursuit") or None
    if journey and (arc.get("resolution") != "ongoing" or journey.get("need") not in (arc.get("needs") or [])):
        journey = None
        p1_char.pop("pursuit", None)
        save_char(p1, p1_char)

    # Mid-journey, "home" for the work-or-arc roll is where they set out from, not the hop they are
    # standing on (audit F7, second half).
    home_location = (journey or {}).get("origin") or location_now
    p1_survival = roll_survival(p1, home_location)

    # Step 3 - work: p1's own routine roll, unweighted, apply at that location, done. No second
    # participant, matching how a "no ongoing arc" work-only pass already works today.
    if p1_survival["choice"] == "work":
        if journey:
            # Audit F7: a work roll mid-journey used to snap the traveler back to a routine
            # location and lose the trip. Now they work where they stand and the journey is kept.
            _apply_p1(location_now, "work", "route")
            _write_back(location_now, f"Worked where they stood, on the way to {journey['target']}.", pursuit=_KEEP)
            notes.append(f"{p1} worked in place at {location_now} - still bound for {journey['target']} ('{journey['need']}')")
            return result
        location = _own_routine_roll(p1_char)
        context = resolve_context_for_location(p1_char, location)
        _apply_p1(location, "work", context)
        _write_back(location, f"Worked a {context} routine at {location}.")
        return result

    # Step 4/5 precondition - roll_survival.py's own "no ongoing arc" gate should have already forced
    # "work" above for a character with no ongoing arc; this branch only ever fires for the
    # first-arc/needs-not-yet-authored shape _template.json ships (resolution "ongoing", needs: []),
    # which that gate does NOT catch (an empty needs list is not the same as "no ongoing arc").
    if arc.get("resolution") != "ongoing" or not arc.get("needs"):
        location = _own_routine_roll(p1_char)
        context = resolve_context_for_location(p1_char, location)
        _apply_p1(location, "arc", context)
        last_scene = f"Worked a {context} routine at {location}."
        if not arc.get("needs"):
            result["arc_authoring_needed"] = {"character_slug": p1, "reason": "first"}
            notes.append(f"{p1} chose arc but has no needs authored yet - needs a first arc")
            last_scene += " Needs a new arc authored."
        else:
            notes.append(f"{p1} chose arc but their arc isn't ongoing (unexpected)")
        _write_back(location, last_scene)
        return result

    # ---- the pursuit branch: arc chosen, ongoing, with needs -----------------------------------
    all_characters = load_all_characters()
    needs = arc.get("needs") or []
    need = journey["need"] if journey else needs[0]
    cost = ARC_PAYMENT["arc_need_cost"]
    # Decided before any meeting, so "had the means but did not find them" can be told apart from
    # "could not have paid anyway". Measured after this pass's eating (_apply_p1 updates `afford`),
    # since eating comes out of the same provisions the payment would: the same number the payment
    # gate checks. Every exit of this branch runs _apply_p1 before it reports a stage.

    def _pursuit(stage: str, reason: str | None, place: str | None, supplier: str | None = None,
                 present: list | None = None, **extra) -> None:
        result["pursuit"] = {
            "stage": stage, "reason": reason, "need": need, "place": place, "supplier": supplier,
            "present": present or [], "could_afford": afford["v"], **extra,
        }

    # Step 4 - locally satisfiable. Only for someone standing at a place of their own routines: a
    # visitor at the end of a failed trip is not "home", and the place providing the need is exactly
    # why they came (so it must not read as "satisfied locally" and send them back to their desk).
    is_home = any(r.get("location") == location_now for r in p1_char.get("routines", []))
    if not journey and is_home:
        provides_here = location_context.location_provides(location_now, list(all_characters.values()), CONTEXTS)
        matched_need = next((n for n in needs if n in provides_here), None)
        if matched_need:
            # Prefer (not force) whichever of p1's own routines has a context that provides the need.
            boost_locations = {
                r["location"] for r in p1_char.get("routines", [])
                if matched_need in (CONTEXTS.get(r.get("context")) or {}).get("provides", [])
            }
            location = (
                roll_routine_boosted(p1_char["routines"], boost_locations)
                if boost_locations else _own_routine_roll(p1_char)
            )
            _apply_p1(location, "arc", resolve_context_for_location(p1_char, location))
            need = matched_need
            _pursuit("local_satisfied", "need_provided_here", location)
            notes.append(f"{p1} pursued their arc's need ('{matched_need}') locally at {location}")
            _write_back(location, f"Pursued '{matched_need}' locally at {location}.")
            return result

    # Step 5 - destination. Kept from an earlier pass, or drawn now. Single-need MVP: resolves only
    # the first of arc.needs.
    if len(needs) > 1 and not journey:
        notes.append(f"{p1}'s arc has {len(needs)} needs - resolving only the first ('{need}') this pass")
    encodings_data = load_encodings()
    graph = travel_graph.build_graph(encodings_data)
    path = target = None
    if journey:
        found = travel_graph.shortest_path(graph, location_now, {journey["target"]})
        if found:
            target, path = found
    else:
        options = location_context.destination_options(
            p1_char, need, encodings_data, list(all_characters.values()), CONTEXTS, T.get("pursuit"),
        )
        chosen = draw_destination(p1, need, options) if options else None
        if chosen:
            target, path = chosen["location"], chosen["path"]
            notes.append(
                f"{p1} settled on {target} for '{need}' ({chosen['hops']} hop(s), weight {chosen['weight']} of "
                f"{round(sum(o['weight'] for o in options), 2)})"
            )

    if target is None:
        # Nowhere reachable (or a kept destination the map no longer connects): treat exactly like
        # "not motivated" - the arc doesn't advance, and p1 stays where they are.
        _apply_p1(location_now, "arc", None)
        _pursuit("no_target", "kept_destination_unreachable" if journey else "no_reachable_source", location_now)
        notes.append(f"{p1}'s arc has no reachable target for '{need}' this pass - arc doesn't advance")
        _write_back(location_now, f"Sought '{need}' but found no reachable path from {location_now}.")
        return result

    hop = travel_graph.next_hop(path)

    if hop is not None and hop != target:
        # Mid-journey - mechanical override, no roll_routine.py call, no second participant, no arc
        # advance this pass. The destination is kept in the character's file for the next arc pass.
        effect = _apply_p1(hop, "arc", "route")
        result["travel"] = {"target": target, "path": path, "hop": hop}
        notes.append(f"{p1} is traveling toward {target} for '{need}' - this pass lands at {hop}, still en route")
        if effect["died"]:
            _pursuit("died_en_route", "energy_depleted", hop, destination=target)
            _write_back(hop, f"Died on the road toward {target}, at {hop}.")
        else:
            _pursuit("en_route", "keeping_destination" if journey else "destination_chosen", hop, destination=target)
            _write_back(hop, f"Traveled toward {target}, passing through {hop}.", pursuit={
                "need": need, "target": target, "origin": (journey or {}).get("origin") or location_now,
                "since_pass": (journey or {}).get("since_pass", pass_number),
            })
        return result

    # Arrived (hop == target, or already at target with a length-1 path and hop is None). The
    # journey ends here whatever happens next (the default of _write_back).
    location = target
    result["travel"] = {"target": target, "path": path, "hop": hop}

    # Step 6 - who's about. Living residents with a routine here. Tier-3 (known supplier) favor: if
    # someone in p1's own circle supplies the need here and is a resident, they are favored in the
    # meetable roll, never guaranteed.
    candidates = candidates_at(location, all_characters, exclude=p1)
    supplier_map = location_context.find_supplier_map(p1_char, need, list(all_characters.values()), CONTEXTS)
    favor = next((k for k in supplier_map.get(location, []) if k in candidates), None)

    def _bystander_scene(stage: str, reason: str, excluded: set, wanted: str | None) -> None:
        """Nobody useful: the scene goes to someone else who lives or works here, drawn uniformly. Their
        routine is rolled over the routines they have at this place (the draw already says they are
        here; the roll only says what they are doing). No payment, no arc outcome. An empty pool is a
        solo scene."""
        pool = [c for c in candidates if c not in excluded]
        if not pool:
            _pursuit("arrived_empty", "no_one_else_present", location, supplier=wanted)
            result["scene"] = "solo"
            notes.append(f"{p1} arrived at {location} and found nobody else there - solo scene, arc doesn't advance")
            _write_back(location, f"Arrived at {location} and found no one there.")
            return
        p2 = draw_bystander(p1, pool)
        routine = roll_routine_at(load_char(p2), location)
        result["participant_2"] = p2
        result["context"] = routine["context"]
        result["scene"] = "pair"
        result["survival"].setdefault(p2, {"choice": None, "energy": load_char(p2).get("energy"), "died": False})
        record_partner(p1, p2)
        record_partner(p2, p1)
        _pursuit(stage, reason, location, supplier=wanted, present=[p2])
        notes.append(
            f"{p1} arrived at {location} for '{need}' but {'the person they came for' if wanted else 'no supplier'} "
            f"was not there ({reason}); spent the pass with {p2} instead - arc doesn't advance"
        )
        _write_back(location, f"Arrived at {location}, found no supplier, and spent the pass with {p2}.")

    if not candidates:
        _apply_p1(location, "arc", None)
        _pursuit("arrived_empty", "no_residents", location)
        result["scene"] = "solo"
        notes.append(f"{p1} arrived at {location} but nobody is around this pass - arc doesn't advance")
        _write_back(location, f"Arrived at {location} but no one was around.")
        return result

    meet = roll_meetable(candidates, favor=favor)
    _apply_p1(location, "arc", None)

    if not meet["met"]:
        notes.append(f"{p1} arrived at {location} but missed the connection this pass (odds {meet['odds_used']})")
        _bystander_scene("arrived_nobody", "supplier_absent", {favor} if favor else set(), favor)
        return result

    p2 = meet["chosen"]

    # Step 7 - p2 rolls their own routine. Even having been drawn as present, p2's own roll might not
    # actually land them here doing something that matches the need.
    p2_char = load_char(p2)
    p2_location = roll_routine(p2_char.get("routines") or [])
    p2_context = resolve_context_for_location(p2_char, p2_location)
    p2_provides = set((CONTEXTS.get(p2_context) or {}).get("provides") or [])

    if p2_location != location:
        notes.append(f"{p1} looked for {p2} at {location}, but {p2}'s own routine this pass took them to {p2_location}")
        _bystander_scene("arrived_nobody", "supplier_elsewhere", {p2}, p2)
        return result

    result["participant_2"] = p2
    result["context"] = p2_context
    result["scene"] = "pair"
    result["survival"].setdefault(p2, {"choice": None, "energy": p2_char.get("energy"), "died": False})

    # p1 and p2 verifiably shared this pass - partner tracking fires here (see this module's own
    # section docstring for why this timing was chosen).
    record_partner(p1, p2)
    record_partner(p2, p1)

    if need not in p2_provides:
        _pursuit("met_mismatch", "context_does_not_provide", location, supplier=p2, present=[p2])
        notes.append(f"{p1} met {p2} at {location}, but {p2}'s own routine this pass ({p2_context}) doesn't provide '{need}' - scene, no purchase")
        _write_back(location, f"Met {p2} at {location} but they had nothing to offer this pass.")
        return result

    # Step 8 - payment gate. No arc outcome is rolled unless the purchase goes through.
    payment = arc_payment_gate(p1, p2, arc)
    if not payment["motivated"]:
        _pursuit("met_cannot_pay", payment["reason"], location, supplier=p2, present=[p2])
        notes.append(
            f"{p1} met {p2} at {location} ('{need}' available) but the payment gate failed "
            f"({payment['reason']}, odds {payment['odds_used']}) - scene, no arc outcome"
        )
        _write_back(location, f"Met {p2} at {location} but couldn't afford '{need}'.")
        return result

    result["motivated"] = True
    result["matched_need"] = need
    result["matched_provide"] = need
    _pursuit("met_paid", "paid", location, supplier=p2, present=[p2])
    notes.append(f"{p1} paid {payment['cost']} provisions to {p2} for '{need}' at {location} - motivated")

    # Unchanged chain from here: contested, alignment gate, outcome, tally/threshold - keyed to p1's
    # arc (always primary now - no primacy roll, p1 is definitionally the lead) vs. p2 as peer.
    p1_char = load_char(p1)  # re-sync after apply_survival()/arc_payment_gate()'s own writes
    arc = p1_char.get("arc") or {}
    peer_strength = p2_char.get("partners", {}).get(p1, 0)
    peer_quality = p2_char.get("partners_quality", {}).get(p1, 0)
    contested = roll_contested(strength=peer_strength, quality=peer_quality)
    result["contested"] = contested

    gate_res = check_arc_alignment(arc.get("about", []), arc.get("needs", []), p2_char)
    gate_hit = gate_res["gate"] == "hit"
    result["arc"]["gate"] = "hit" if gate_hit else "miss"
    if not gate_hit:
        _write_back(location, f"Completed a trade with {p2} at {location} for '{need}'.")
        return result

    inclined = gate_res.get("inclined", "neutral")
    result["arc"]["inclined"] = inclined
    quality_delta = BOND_QUALITY_DELTA[inclined]
    if quality_delta:
        record_bond_quality(p2, p1, quality_delta)

    outcome = roll_arc_outcome(inclined, contested=contested)
    result["arc"]["outcome"] = outcome
    arc.setdefault("history", []).append({"pass": pass_number, "outcome": outcome})
    score = tally(arc["history"])

    if score >= ARC_RESOLUTION_THRESHOLD:
        arc["resolution"] = "complete"
        result["arc"]["tally_result"] = "complete"
        notes.append(f"{p1}'s arc completed")
        result["arc_authoring_needed"] = {"character_slug": p1, "reason": "reauthor_complete"}
    elif score <= -ARC_RESOLUTION_THRESHOLD:
        matched_about = gate_res.get("matched_about") or []
        if matched_about:
            arc["about"] = matched_about
            arc["history"][-1]["outcome"] = "transform"
            result["arc"]["tally_result"] = "transform"
            result["arc"]["matched_about"] = matched_about
            notes.append(f"{p1}'s arc transformed -> {matched_about}")
        else:
            arc["resolution"] = "failed"
            result["arc"]["tally_result"] = "failed"
            notes.append(f"{p1}'s arc failed")
            result["arc_authoring_needed"] = {"character_slug": p1, "reason": "reauthor_failed"}
    else:
        result["arc"]["tally_result"] = "ongoing"
        notes.append(f"{p1}'s arc: {outcome}")

    p1_char["arc"] = arc
    save_char(p1, p1_char)

    if contested and inclined == "hinder":
        result["contested_hinder_slot"] = {"traveler": p1, "supplier": p2, "matched_provide": need}

    tally_word = {"advance": "advanced", "stall": "stalled", "reverse": "reversed"}.get(outcome, outcome)
    tally_result = result["arc"]["tally_result"]
    if tally_result == "complete":
        last_scene = f"Completed a trade with {p2} at {location} for '{need}' - arc complete."
    elif tally_result == "transform":
        last_scene = f"Completed a trade with {p2} at {location} for '{need}' - arc transformed."
    elif tally_result == "failed":
        last_scene = f"Completed a trade with {p2} at {location} for '{need}' - arc failed."
    else:
        last_scene = f"Completed a trade with {p2} at {location}, arc {tally_word}."
    _write_back(location, last_scene)

    return result
