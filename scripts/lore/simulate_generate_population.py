"""
Fast-forward many passes of /simulate's extended-mode mechanic with NO scene-writing and NO
subagent per pass - built for `/generate`, whose whole point is producing a large,
multi-generation starting population quickly rather than a showcase trail of prose. Every
mechanical sub-step of the interactive skill's Step 3 (.claude/skills/simulate/SKILL.md) that's
already backed by a script or plain arithmetic runs here exactly as documented there, in the same
causal order (rewritten 2026-08-28 - see CHRONICLE.md's matching entry): pairing, lead-followup,
partner tracking, home/visit roll, home-only routine roll, location/context assembly, arc primacy,
needs/provides (keyed to the primacy winner), contested, gate, contested-aware outcome,
tally+threshold (including transform), reproduction eligibility+roll, offspring generation,
life.lived + death + death-legacy.

Three deliberate scope differences from the interactive skill, all confirmed with the user rather
than assumed:

1. No scene prose, and no /enact Steps 5/5b/6 underneath it (hearsay mutation, criterion shock) -
   this mode's whole reason to exist. Criteria stay exactly as inherited/authored; they get tested
   later in real /enact or interactive /simulate scenes.
2. The two things that genuinely need a model's judgment - a child's blended name, and a freshly
   authored arc's about/needs/context/premise content (and a rewritten routine's routine_actions
   line for a child) - are never invented here. Instead
   this script writes a placeholder identity immediately (so the child can exist and participate in
   later passes: reproduce, be visited, die) and queues the real content into `_pending_language.json`
   at the worktree root for a SINGLE batched subagent pass at the very end of the whole run (see
   `.claude/skills/generate/SKILL.md`'s Step 4) - never one dispatch per event.
   The placeholder's SLUG is never renamed later, only the human-facing `name` field and prose that
   quotes it (see `apply_language_layer.py`) - this sidesteps rewriting every cross-file slug
   reference (`parents`, `partners`, `leads`, `lifespans.json`, tale ids) for a cosmetic rename.
3. Step 9's contested-rival mechanic ("a rival only gets named if a character file already exists for
   them") requires inventing a plausible rival identity when none is dictated by the mechanics - that
   is exactly the kind of free content this mode cannot produce without a model. `contested` is still
   rolled and reported for every motivated visit (real bookkeeping, not skipped), but this mode never
   writes the `leads` entry or the attributed rival note that only the "named + hinder" branch
   produces - every contested case here resolves as the ambient/unnamed default instead.

Everything else - pairing, routine/location, needs/provides, the arc gate/outcome/tally machinery,
partner tracking, reproduction, offspring inheritance (including routines, which
`generate_offspring.py` already inherits mechanically from both parents), death, and death-legacy -
runs for real, exactly as it would under a human running the interactive skill by hand.

Every sibling script is invoked by an ABSOLUTE path derived from this script's own `__file__`
(`SCRIPTS_DIR / "<name>.py"`), never a relative one and never dependent on the caller's cwd - this is
what the interactive skill's Step 3 has to defend against by convention (a subagent can mistype or
misresolve a relative path); a single Python process constructing its own sibling paths has no such
failure mode; there is no subagent here to make that mistake, only this file.

The `call()`/`kv()` plumbing and every sibling-script wrapper below now live in simulate_pass_lib.py
(extracted 2026-08-13) so `/enact`'s own mechanical-block drivers (simulate_pass_brief.py,
apply_death_legacy.py) can reuse the exact same tested wrappers instead of a second, subtly
different reimplementation - this file only keeps the parts specific to running N passes with no
subagent at all: State, queue_arc/maybe_admit_children (the deferred-authoring bookkeeping this mode
alone needs), and run_pass() itself.

Usage:
    py scripts/lore/simulate_generate_population.py --pool khaoe farlis khaasan --passes 60
    py scripts/lore/simulate_generate_population.py --pool khaoe farlis --passes 40 --seed 7
    py scripts/lore/simulate_generate_population.py --pool khaoe farlis --passes 40 --living-pool-out .living_pool.json
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
PENDING_PATH = ROOT / "_pending_language.json"
SNAPSHOT_PATH = ROOT / ".simulate_snapshot.json"
LOG_PATH = ROOT / "GENERATION_LOG.md"

sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402
import simulate_pass_reproduction as repro_lib  # noqa: E402
import wealth_lib  # noqa: E402

PARTNER_THRESHOLD = lib.PARTNER_THRESHOLD
PARENT_COOLDOWN_PASSES = lib.PARENT_COOLDOWN_PASSES
CHILD_COOLDOWN_PASSES = lib.CHILD_COOLDOWN_PASSES
LEAD_EXPIRY_PASSES = lib.LEAD_EXPIRY_PASSES
ARC_RESOLUTION_THRESHOLD = lib.ARC_RESOLUTION_THRESHOLD

load_char = lib.load_char
save_char = lib.save_char
call = lib.call
kv = lib.kv
notified_keys = lib.notified_keys
pick_pair = lib.pick_pair
roll_lead_followup = lib.roll_lead_followup
roll_home_visit = lib.roll_home_visit
roll_routine = lib.roll_routine
assemble_location = lib.assemble_location
check_needs_provides = lib.check_needs_provides
roll_arc_primacy = lib.roll_arc_primacy
check_arc_alignment = lib.check_arc_alignment
roll_contested = lib.roll_contested
roll_arc_outcome = lib.roll_arc_outcome
record_partner = lib.record_partner
generate_offspring = lib.generate_offspring
horizon = lib.horizon
record_death = lib.record_death
roll_death_legacy = lib.roll_death_legacy
update_character_lived = lib.update_character_lived
tally = lib.tally
roll_survival = lib.roll_survival
apply_survival = lib.apply_survival
apply_upkeep = lib.apply_upkeep
SURVIVAL = lib.SURVIVAL


# --------------------------------------------------------------------------------------------
# One pass
# --------------------------------------------------------------------------------------------

class State:
    def __init__(self, pool: list):
        self.living = list(dict.fromkeys(pool))
        self.pending_births = []  # (child_slug, eligible_pass)
        self.pending = {"children": [], "arcs": []}
        self.queued_arc_chars = set()
        self.generation = {slug: 0 for slug in pool}
        self.child_counter = 0
        self.log = []
        self.ancestor_cache = {}  # memoizes lib.ancestors_of() across the whole run


def maybe_admit_children(state: State, pass_number: int) -> None:
    still_pending = []
    for slug, eligible_pass in state.pending_births:
        if pass_number >= eligible_pass:
            state.living.append(slug)
        else:
            still_pending.append((slug, eligible_pass))
    state.pending_births = still_pending


def queue_arc(state: State, key: str, character: dict, reason: str, pass_number: int) -> bool:
    if key in state.queued_arc_chars:
        return False
    state.queued_arc_chars.add(key)
    band = horizon(key)["band"]
    state.pending["arcs"].append({
        "character_slug": key,
        "character_name": character.get("name"),
        "reason": reason,
        "queued_at_pass": pass_number,
        "horizon_band": band,
        "origin": character.get("origin", ""),
        "location": character.get("location", ""),
        "backstory": character.get("backstory", ""),
        "criterion": character.get("criterion", {}),
        "routines": character.get("routines", []),
        "prior_arc": character.get("arc") if reason in ("reauthor_failed", "reauthor_complete") else None,
    })
    return True


def run_pass(state: State, pass_number: int) -> str:
    notes = []

    p1, p2 = pick_pair(state.living)
    p1_char, p2_char = load_char(p1), load_char(p2)

    # Step 2 - lead override
    forced_visit = False
    leads = p1_char.get("leads", [])
    fresh_leads = [l for l in leads if pass_number - l["created_pass"] < LEAD_EXPIRY_PASSES]
    if len(fresh_leads) != len(leads):
        p1_char["leads"] = fresh_leads
        save_char(p1, p1_char)
    if fresh_leads:
        res = roll_lead_followup([l["target"] for l in fresh_leads])
        if res["followed"] == "true":
            target = res["lead"]
            if target in state.living and target != p1:
                p2 = target
                p2_char = load_char(p2)
                p1_char["leads"] = [l for l in fresh_leads if l["target"] != target]
                save_char(p1, p1_char)
                forced_visit = True
                notes.append(f"{p1} followed a lead to {p2}")

    # Partner tracking - moved to the front (2026-08-28 reorder), unconditional the moment p1/p2
    # are finalized (after any lead-override reassignment above); has nothing to do with anything
    # decided below.
    record_partner(p1, p2)
    record_partner(p2, p1)
    p1_char, p2_char = load_char(p1), load_char(p2)

    # Survival - rolled BEFORE home/visiting, one per participant, against each one's own home
    # location (not the pass's eventual one, which isn't known yet). See roll_survival.py.
    p1_survival = roll_survival(p1, p1_char.get("location", ""))
    p2_survival = roll_survival(p2, p2_char.get("location", ""))

    # Home/visiting, then (home only) routine, then location/context assembly - no script call
    # left for the location step itself (2026-08-28 reorder: decided BEFORE any routine is rolled,
    # not derived afterward by comparing two independently-rolled routines; only the home
    # participant ever rolls one now). Skewed by the survival choices just rolled.
    if forced_visit:
        home, visiting = p2, p1
    else:
        home, visiting = roll_home_visit(p1, p2, p1_survival["choice"], p2_survival["choice"])
    home_char = p1_char if home == p1 else p2_char
    home_routine = roll_routine(home_char["routines"])
    loc = assemble_location(home, home_routine, visiting, home_char)
    location, home_frame, traveler = loc["location"], loc["home_frame"], loc["traveler"]
    context, provides = loc["context"], loc["provides"]

    # Survival effects apply at the RESOLVED location, not each participant's home - upkeep once
    # for the location (never once per participant), then each participant's own energy/pool delta
    # from the choice already rolled above.
    apply_upkeep(location)
    p1_effect = apply_survival(p1, location, p1_survival["choice"])
    p2_effect = apply_survival(p2, location, p2_survival["choice"])
    if p1_survival["choice"] == "arc":
        notes.append(f"{p1} spent this pass on their arc instead of working ({p1_effect['energy']} energy left)")
    if p2_survival["choice"] == "arc":
        notes.append(f"{p2} spent this pass on their arc instead of working ({p2_effect['energy']} energy left)")

    # Arc primacy - decided next, independently of who's home vs visiting (2026-08-28 reorder: the
    # visiting participant's arc can still be the one that leads the scene).
    primacy = roll_arc_primacy(p1, p2)
    primary_char = p1_char if primacy == p1 else p2_char
    other_char = p2_char if primacy == p1 else p1_char
    arc = primary_char.get("arc")
    primacy_survival_choice = p1_survival["choice"] if primacy == p1 else p2_survival["choice"]

    # Needs/provides - keyed to the primacy winner's own arc, whichever participant that is
    # (2026-08-28 reorder: not "the traveler's" as a fixed role). Gated on the primacy winner
    # having actually chosen "arc" this pass, and on the location being able to afford to provide
    # at all (see simulate_pass_brief.py's matching gate).
    motivated, contested = False, False
    if (arc and arc.get("resolution") == "ongoing" and arc.get("needs")
            and primacy_survival_choice == "arc"
            and wealth_lib.wealth_per_capita(location) >= SURVIVAL["provides_wealth_threshold"]):
        np_res = check_needs_provides(arc["needs"], provides)
        motivated = np_res["match"] == "true"
    elif arc and arc.get("resolution") == "ongoing" and primacy_survival_choice != "arc":
        notes.append(f"{primacy} chose to work this pass - arc untouched regardless of primacy")

    # Contested (only if motivated). Relationship-aware 2026-08-28, same as the interactive path -
    # see roll_contested.py's docstring. Never names a rival (see module docstring point 3) - rolled
    # and reported, but never writes `leads`/a rival note, since that requires an invented identity
    # no script or dice roll here can supply.
    if motivated:
        peer_strength = other_char.get("partners", {}).get(primacy, 0)
        peer_quality = other_char.get("partners_quality", {}).get(primacy, 0)
        contested = roll_contested(strength=peer_strength, quality=peer_quality)

    # Gate + outcome (now contested-aware) + tally
    if not arc:
        if primacy == home_frame and queue_arc(state, primacy, primary_char, "first", pass_number):
            notes.append(f"{primacy} queued for a first arc")
    elif arc.get("resolution") == "ongoing" and primacy_survival_choice == "arc":
        gate_res = check_arc_alignment(arc.get("about", []), arc.get("needs", []), other_char)
        gate_hit = gate_res["gate"] == "hit"
        if gate_hit:
            inclined = gate_res.get("inclined", "neutral")
            other_key = p2 if primacy == p1 else p1
            quality_delta = lib.BOND_QUALITY_DELTA[inclined]
            if quality_delta:
                lib.record_bond_quality(other_key, primacy, quality_delta)
            outcome = roll_arc_outcome(inclined, contested=contested)
            arc.setdefault("history", []).append({"pass": pass_number, "outcome": outcome})
            score = tally(arc["history"])
            if score >= ARC_RESOLUTION_THRESHOLD:
                arc["resolution"] = "complete"
                notes.append(f"{primacy}'s arc completed")
                queue_arc(state, primacy, primary_char, "reauthor_complete", pass_number)
            elif score <= -ARC_RESOLUTION_THRESHOLD:
                matched_about = gate_res.get("matched_about") or []
                if matched_about:
                    arc["about"] = matched_about
                    arc["history"][-1]["outcome"] = "transform"
                    notes.append(f"{primacy}'s arc transformed -> {matched_about}")
                else:
                    arc["resolution"] = "failed"
                    notes.append(f"{primacy}'s arc failed")
                    queue_arc(state, primacy, primary_char, "reauthor_failed", pass_number)
            else:
                notes.append(f"{primacy}'s arc: {outcome}")
            save_char(primacy, primary_char)

    # Reproduction eligibility + roll - shared with the interactive path's own post-scene check
    # (simulate_pass_reproduction.py) rather than a third copy of the same logic; this file's own
    # ancestor_cache still gets threaded through for the same perf reason it always was.
    repro = repro_lib.check_and_roll(p1, p2, pass_number, ancestor_cache=state.ancestor_cache)
    if repro["reproduces"]:
        name_lead = repro["name_lead"]
        other_parent = repro["other_parent"]
        state.child_counter += 1
        # Bounded and fixed-width on purpose: chaining both parents' own slugs into a child's
        # placeholder (the pre-2026-08-17 scheme) compounds every generation, since a
        # placeholder is never renamed and a grandchild's parent slug is already a chain of
        # its own parents' - by generation 5-6 this blew past Windows' 260-char path limit on
        # the birth tale write (confirmed the hard way at pass 561 of a 2000-pass run). The
        # fixed 4-digit width also keeps every placeholder safe against apply_language_layer.py's
        # plain-substring rename (child_0003 is never a substring of child_0037, unlike
        # unpadded 3 vs 37) - lineage is already carried in full in pending["children"]'s own
        # parent_a/parent_b fields, so the slug itself never needed to encode it.
        placeholder = f"placeholder_child_{state.child_counter:04d}"
        birth = generate_offspring(p1, p2, placeholder, pass_number)
        child = load_char(birth["slug"])
        state.pending_births.append((birth["slug"], birth["eligible_pass"]))
        state.generation[birth["slug"]] = 1 + max(
            state.generation.get(p1, 0), state.generation.get(p2, 0)
        )
        lead_char, other_char_ = (p1_char, p2_char) if name_lead == p1 else (p2_char, p1_char)
        state.pending["children"].append({
            "placeholder_slug": birth["slug"],
            "placeholder_name": placeholder,
            "name_lead": name_lead,
            "parent_a": {"slug": name_lead, "name": lead_char.get("name"), "origin": lead_char.get("origin", ""), "location": lead_char.get("location", ""), "backstory": lead_char.get("backstory", "")},
            "parent_b": {"slug": other_parent, "name": other_char_.get("name"), "origin": other_char_.get("origin", ""), "location": other_char_.get("location", ""), "backstory": other_char_.get("backstory", "")},
            "birth_pass": pass_number,
            "routines": child.get("routines", []),
        })
        notes.append(f"{p1}+{p2} had a child ({birth['slug']}, generation {state.generation[birth['slug']]})")

    # Step 15/16 - life.lived, death, death-legacy. Two independent death vectors now: the existing
    # rolled lifespan (horizon.py's "ending"), and energy hitting 0 (survival mechanism, checked
    # second so a natural-lifespan death this same pass always takes priority if somehow both fire).
    survival_effects = {p1: p1_effect, p2: p2_effect}
    for participant in (p1, p2):
        update_character_lived(participant, 1)
        h = horizon(participant)
        natural = h["ending"] == "true"
        starved = (not natural) and survival_effects[participant]["died"]
        if natural or starved:
            cause = "exhaustion/starvation - energy depleted" if starved else None
            death = record_death(participant, cause=cause)
            state.living = [s for s in state.living if s != participant]
            notes.append(f"{participant} died" + (" (starved)" if starved else ""))
            if h["band"] == "established" and death["notified"]:
                legacy = roll_death_legacy(death["notified"])
                if legacy["passes"] == "true":
                    recipient = legacy["recipient"]
                    deceased_char = load_char(participant)
                    deceased_arc = deceased_char.get("arc")
                    if deceased_arc:
                        recipient_char = load_char(recipient)
                        prev_arc = recipient_char.get("arc") or {}
                        context_ = prev_arc.get("context")
                        if not context_:
                            routines = recipient_char.get("routines", [])
                            if routines:
                                context_ = max(routines, key=lambda r: r.get("weight", 0))["context"]
                        recipient_char["arc"] = {
                            "about": list(deceased_arc.get("about", [])),
                            "needs": list(deceased_arc.get("needs", [])),
                            "context": context_ or deceased_arc.get("context"),
                            "premise": deceased_arc.get("premise", ""),
                            "resolution": "ongoing",
                            "history": [],
                        }
                        save_char(recipient, recipient_char)
                        notes.append(f"{participant}'s arc passed to {recipient} (death-legacy)")

    maybe_admit_children(state, pass_number)

    summary = f"pass {pass_number}: {p1} x {p2} (home: {home_frame}"
    if motivated:
        summary += f", motivated{' contested' if contested else ''}"
    summary += ")"
    if notes:
        summary += " - " + "; ".join(notes)
    return summary


# --------------------------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", nargs="+", required=True, help="Starting living participants (must all have routines)")
    parser.add_argument("--passes", type=int, required=True)
    parser.add_argument("--living-pool-out", default=None, help="Also write the ending living pool (JSON array of slugs) to this path - for a caller that wants to feed it straight into a subsequent showcase-trail run without retyping it (see SKILL.md's --pregenerate)")
    args = parser.parse_args()

    lifespans = json.loads((CHAR_DIR / "lifespans.json").read_text(encoding="utf-8"))["lifespans"]

    pool = [s.lower() for s in args.pool]
    for slug in pool:
        path = CHAR_DIR / f"{slug}.json"
        if not path.exists():
            raise SystemExit(f"No character file for '{slug}'.")
        c = json.loads(path.read_text(encoding="utf-8"))
        if c.get("life", {}).get("deceased"):
            raise SystemExit(f"'{slug}' is already deceased - drop them from --pool.")
        if not c.get("routines"):
            raise SystemExit(f"'{slug}' has no routines - generate mode requires every starting participant to have them (a routine-less character can never be paired into the reproduction mechanic).")
        if slug not in lifespans:
            raise SystemExit(f"'{slug}' has no entry in lifespans.json - run scripts/lore/roll_lifespan.py and record it there (/character Step 5) before including them in --pool.")

    call("simulate_tally.py", ["snapshot", *pool, "--out", str(SNAPSHOT_PATH)])

    state = State(pool)
    ran = 0
    for pass_number in range(1, args.passes + 1):
        if len(state.living) < 2:
            print(f"Stopping early after {ran} pass(es) - fewer than 2 living participants remain.")
            break
        summary = run_pass(state, pass_number)
        state.log.append(summary)
        print(summary)
        ran += 1

    PENDING_PATH.write_text(
        json.dumps({"generated_at_pass": ran, **state.pending}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    LOG_PATH.write_text("# Generation log\n\n" + "\n".join(f"- {line}" for line in state.log) + "\n", encoding="utf-8")

    if args.living_pool_out:
        Path(args.living_pool_out).write_text(json.dumps(state.living, indent=2) + "\n", encoding="utf-8")

    max_gen = max(state.generation.values(), default=0)
    print()
    print(f"passes run: {ran}")
    print(f"living pool at end: {len(state.living)}  ({', '.join(state.living)})")
    print(f"children born: {len(state.pending['children'])}")
    print(f"arcs queued for the language layer: {len(state.pending['arcs'])}")
    print(f"max generation depth reached: {max_gen}")
    print(f"pending language manifest: {PENDING_PATH}")
    print(f"log: {LOG_PATH}")
    print(f"snapshot (for simulate_tally.py report): {SNAPSHOT_PATH}")
    if args.living_pool_out:
        print(f"living pool written: {args.living_pool_out}")


if __name__ == "__main__":
    main()
