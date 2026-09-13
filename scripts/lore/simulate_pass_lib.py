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
    """Every character key (excluding `exclude`) in `all_characters` (load_all_characters()'s own
    shape - key -> character dict) with a routines[] entry at exactly `location` - Step 6's candidate
    pool for the meetable roll."""
    out = []
    for key, char in all_characters.items():
        if key == exclude:
            continue
        if any(r.get("location") == location for r in (char.get("routines") or [])):
            out.append(key)
    return out


# --------------------------------------------------------------------------------------------
# Survival mechanism (design session 2026-08-28) - roll_survival() against a character's own home
# `location` field; apply_survival()/apply_upkeep() AFTER, once the pass's actual location is
# resolved. See TODO.md's "Survival mechanism" entry for the full math.
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

    p1_char["provisions"] = provisions - cost
    save_char(p1_key, p1_char)
    p2_char = load_char(p2_key)
    p2_char["provisions"] = p2_char.get("provisions", SURVIVAL["starting_provisions_per_capita"]) + cost
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
#   Step 2  roll_survival(p1)                                   - survive vs. arc, unchanged script
#   Step 3  survive -> p1's own routine roll, apply, DONE        - no second participant, ever
#   Step 4  arc, locally satisfiable -> boosted own-routine roll, apply, DONE
#   Step 5  arc, not locally satisfiable -> pathfind (location_context.resolve_arc_target);
#           no target -> DONE (not motivated); mid-journey -> mechanical "route" override, DONE;
#           arrived -> Step 6
#   Step 6  who's meetable at the arrival location (roll_meetable, favoring a known supplier) -
#           miss -> DONE; hit -> p2 fixed, Step 7
#   Step 7  p2's own routine roll - context/location mismatch with the need -> DONE (miss);
#           match -> Step 8
#   Step 8  arc_payment_gate() - fail -> DONE (not motivated); success -> the UNCHANGED
#           contested/alignment/outcome/tally chain, keyed to p1's arc vs. p2 as peer
#
# Partner tracking (record_partner, both directions) fires exactly once, at the point p1 and p2 are
# BOTH confirmed present with matching contexts (end of Step 7/start of Step 8) - the earliest point
# in the new algorithm where two characters have actually, verifiably shared a pass, matching the old
# algorithm's own "the moment the pair is fixed" timing as closely as the new asymmetric model allows.
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

def _known_circle(character: dict) -> set:
    return (
        set((character.get("partners") or {}).keys())
        | set(character.get("social_circle") or [])
        | set(character.get("parents") or [])
    )


def run_pass_mechanics(p1: str, pass_number: int) -> dict:
    """Runs the full Step 2-8 algorithm for one already-picked `p1`. Returns a result dict shared by
    both callers - see this module's own section docstring above for the field-by-field shape used
    by each step. `arc_authoring_needed`, when present, is a minimal `{"character_slug", "reason"}`
    signal only - each caller enriches it with the full authoring context (band/criterion/routines/
    needs_candidates/prior_arc) and, on `reauthor_complete`, writes the completion tale itself, the
    same division of labor the pre-rewrite simulate_pass_brief.py already used for this exact slot."""
    notes: list = []
    p1_char = load_char(p1)
    home_location = p1_char.get("location", "")

    result = {
        "pass": pass_number,
        "participant_1": p1,
        "participant_2": None,
        "location": None,
        "context": None,
        "travel": None,
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

    def _write_back(location: str, last_scene: str) -> None:
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
        same values this already wrote, a harmless no-op."""
        character = load_char(p1)
        character["location"] = location
        visited = character.setdefault("places_visited", [])
        if location not in visited:
            visited.append(location)
        character["last_scene"] = last_scene
        save_char(p1, character)

    def _apply_p1(location: str, choice: str, context: str | None) -> dict:
        """Applies apply_upkeep/apply_survival for p1 at `location` and writes the common result
        fields every branch below needs - `context` is always the caller's own explicit call (a
        routine roll's resolved context, "route" for a mechanical travel override, or None when no
        routine was rolled at all this pass), never guessed here."""
        apply_upkeep(location)
        effect = apply_survival(p1, location, choice)
        result["location"] = location
        result["context"] = context
        result["survival"][p1] = {"choice": choice, "energy": effect["energy"], "died": effect["died"]}
        if effect["died"]:
            notes.append(f"{p1}'s energy hit 0 - exhaustion/starvation, not yet recorded (post-scene step)")
        return effect

    p1_survival = roll_survival(p1, home_location)

    # Step 3 - survive: p1's own routine roll, unweighted, apply at that location, done. No second
    # participant, matching how a "no ongoing arc" survive-only pass already works today.
    if p1_survival["choice"] == "survive":
        location = _own_routine_roll(p1_char)
        context = resolve_context_for_location(p1_char, location)
        _apply_p1(location, "survive", context)
        _write_back(location, f"Worked a {context} routine at {location}.")
        return result

    # Step 4/5 precondition - roll_survival.py's own "no ongoing arc" gate should have already forced
    # "survive" above for a character with no ongoing arc; this branch only ever fires for the
    # first-arc/needs-not-yet-authored shape _template.json ships (resolution "ongoing", needs: []),
    # which that gate does NOT catch (an empty needs list is not the same as "no ongoing arc").
    arc = p1_char.get("arc") or {}
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

    all_characters = load_all_characters()
    needs = arc.get("needs") or []
    provides_here = location_context.location_provides(home_location, list(all_characters.values()), CONTEXTS)
    matched_need = next((n for n in needs if n in provides_here), None)

    if matched_need:
        # Step 4 - locally satisfiable: prefer (not force) whichever of p1's own routines has a
        # context that provides the matched need.
        boost_locations = {
            r["location"] for r in p1_char.get("routines", [])
            if matched_need in (CONTEXTS.get(r.get("context")) or {}).get("provides", [])
        }
        location = (
            roll_routine_boosted(p1_char["routines"], boost_locations)
            if boost_locations else _own_routine_roll(p1_char)
        )
        _apply_p1(location, "arc", resolve_context_for_location(p1_char, location))
        notes.append(f"{p1} pursued their arc's need ('{matched_need}') locally at {location}")
        _write_back(location, f"Pursued '{matched_need}' locally at {location}.")
        return result

    # Step 5 - pathfind. Single-need MVP: resolves only the first of arc.needs (see this rewrite's
    # report for why - a genuine judgment call, not dictated by the spec).
    need = needs[0]
    if len(needs) > 1:
        notes.append(f"{p1}'s arc has {len(needs)} needs - resolving only the first ('{need}') this pass")
    encodings_data = load_encodings()
    target_result = location_context.resolve_arc_target(p1_char, need, encodings_data, list(all_characters.values()), CONTEXTS)

    if target_result is None:
        # No reachable target at all - treat exactly like "not motivated": arc doesn't advance, but
        # p1 didn't go anywhere, so upkeep/survival apply at their own current location.
        _apply_p1(home_location, "arc", None)
        notes.append(f"{p1}'s arc has no reachable target for '{need}' this pass - arc doesn't advance")
        _write_back(home_location, f"Sought '{need}' but found no reachable path from {home_location}.")
        return result

    target, path = target_result
    hop = travel_graph.next_hop(path)

    if hop is not None and hop != target:
        # Mid-journey - mechanical override, no roll_routine.py call, no second participant, no arc
        # advance this pass.
        _apply_p1(hop, "arc", "route")
        result["travel"] = {"target": target, "path": path, "hop": hop}
        notes.append(f"{p1} is traveling toward {target} for '{need}' - this pass lands at {hop}, still en route")
        _write_back(hop, f"Traveled toward {target}, passing through {hop}.")
        return result

    # Arrived (hop == target, or already at target with a length-1 path and hop is None).
    location = target
    result["travel"] = {"target": target, "path": path, "hop": hop}

    # Step 6 - who's meetable. Tier-3 (known supplier) preference: check whether resolve_arc_target's
    # own tier-3 lookup would have succeeded for this need, and if so, whether any actual candidate
    # here is both in p1's own circle AND has a matching routine at this exact location - that
    # specific person is who gets favored in the meetable roll, never guaranteed.
    candidates = candidates_at(location, all_characters, exclude=p1)
    if not candidates:
        _apply_p1(location, "arc", None)
        notes.append(f"{p1} arrived at {location} but nobody is around this pass - arc doesn't advance")
        _write_back(location, f"Arrived at {location} but no one was around.")
        return result

    supplier_targets = location_context.find_supplier_locations(p1_char, need, list(all_characters.values()), CONTEXTS)
    favor = None
    if location in supplier_targets:
        known_circle = _known_circle(p1_char)
        for key in candidates:
            if key not in known_circle:
                continue
            other = all_characters.get(key) or {}
            for r in other.get("routines") or []:
                if r.get("location") == location and need in (CONTEXTS.get(r.get("context")) or {}).get("provides", []):
                    favor = key
                    break
            if favor:
                break

    meet = roll_meetable(candidates, favor=favor)
    _apply_p1(location, "arc", None)

    if not meet["met"]:
        notes.append(f"{p1} arrived at {location} but missed the connection this pass (odds {meet['odds_used']}) - arc doesn't advance")
        _write_back(location, f"Arrived at {location} but missed the connection.")
        return result

    p2 = meet["chosen"]
    result["participant_2"] = p2

    # Step 7 - p2 rolls their own routine. Even having been drawn as present, p2's own roll might not
    # actually land them here doing something that matches the need.
    p2_char = load_char(p2)
    p2_location = roll_routine(p2_char.get("routines") or [])
    p2_context = resolve_context_for_location(p2_char, p2_location)
    p2_provides = set((CONTEXTS.get(p2_context) or {}).get("provides") or [])
    result["survival"].setdefault(p2, {"choice": None, "energy": p2_char.get("energy"), "died": False})

    if p2_location != location or need not in p2_provides:
        result["context"] = p2_context if p2_location == location else None
        notes.append(f"{p1} met {p2} at {location}, but {p2}'s own routine this pass ({p2_context} at {p2_location}) doesn't provide '{need}' - miss")
        _write_back(location, f"Met {p2} at {location} but couldn't align this pass.")
        return result

    result["context"] = p2_context

    # A genuine, mutually-confirmed meeting - partner tracking fires here (see this module's own
    # section docstring for why this timing was chosen).
    record_partner(p1, p2)
    record_partner(p2, p1)

    # Step 8 - payment gate.
    payment = arc_payment_gate(p1, p2, arc)
    if not payment["motivated"]:
        notes.append(
            f"{p1} met {p2} at {location} ('{need}' available) but the payment gate failed "
            f"({payment['reason']}, odds {payment['odds_used']}) - not motivated"
        )
        _write_back(location, f"Met {p2} at {location} but couldn't afford '{need}'.")
        return result

    result["motivated"] = True
    result["matched_need"] = need
    result["matched_provide"] = need
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
