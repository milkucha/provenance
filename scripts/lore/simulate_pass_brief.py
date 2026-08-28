"""
Run every MECHANICAL decision in one /enact scene between two NPCs - routine roll through the
reproduction roll (minus the three things that genuinely need a model) - and hand the result to
whoever is about to write the scene as a single JSON brief, instead of hand-relaying 12+ sequential
`py scripts/lore/*.py` calls one at a time (design debrief 2026-08-13, following the same
mechanization `/generate`'s simulate_generate_population.py already proved out for the mechanical-
pregeneration case - this is that same pipeline's logic, reused via simulate_pass_lib.py).

Takes an already-fixed `--pair <p1> <p2>` - both participants must already be settled by the time
this runs, either by an author (an ordinary `/enact` call) or by `/simulate`'s own pick_pair.py +
lead-override check before it ever dispatches to `/enact` (see `.claude/skills/simulate/SKILL.md`'s
Step 3). Pairing and lead-override are deliberately NOT this script's job any more (moved 2026-08-27,
alongside folding this whole mechanism into `/enact` itself): they decide *who's* in the scene, which
must already be settled by the time `/enact`'s own eligibility gate (both participants need
`routines`+`arc`) has already checked these exact two slugs - resolving identity here, after that
gate already ran, could hand the scene a participant nobody vetted.

Exactly two things are deliberately left undecided here, flagged in the brief for the subagent to
fill - nothing else in this file's output is the subagent's to decide:
  - `arc_authoring_needed` - the fallback path for a character who reached extended-mode play
    without an arc already on file (as of 2026-08-16, `/character` Step 8 authors `arc` at creation
    time by default): their first arc, or a re-authored one after a failure or after completing the
    prior one (`reauthor_failed`/`reauthor_complete` - completing an arc isn't a reason to stop
    having one). Content (about/needs/context/premise) is composed by the subagent, then written
    with write_arc.py (which also registers the concept in the same call).
  - `contested_hinder_slot` - only present on a contested scene that resolved "hinder" against the
    arc-primacy winner. The subagent may dramatize this against a SPECIFIC existing rival (if one
    plausibly fits and already has a character file) or keep it ambient/unnamed (the default). If
    named, call apply_contested_lead.py with the rival's slug.

Reproduction is deliberately NOT decided here any more (moved 2026-08-28, design debrief: the
eligibility+roll used to run before the scene so a birth could be dramatized inside it; now it runs
strictly AFTER, via the sibling script simulate_pass_reproduction.py, so a birth becomes a short coda
after the scene instead). Partner counts still get bumped here, at the very top, the moment the pair
is fixed - unconditional bookkeeping that has nothing to do with whether a birth happens, and
simulate_pass_reproduction.py reads the counts this call already wrote.

Everything else in the brief is already fixed and written to disk by the time this script returns:
arc gate/outcome/tally (including any transform), partner counts, who's home vs visiting and why,
and whether contested - the subagent's job past this point is /enact Steps 3b, 5, 5b, 6 (the scene
itself, hearsay mutation, shock resolution, drift) plus the two slots above, never re-deciding
anything already settled here.

Writes `.simulate_pass_brief.json` at the worktree root (same location as .simulate_snapshot.json) -
`/enact`'s own Step 5b reads it back to write the scene and resolve the two judgment slots above;
nothing reads it again after that. Post-scene mechanics (horizon re-check, death, death-legacy,
reproduction) are `/enact` Step 8's own concern from there, working off the participant slugs
directly, not this file - this script never touches life.lived.

Usage:
    py "<worktree>/scripts/lore/simulate_pass_brief.py" --pair khaoe farlis --pass-number 12
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402


def run_pre_scene(p1: str, p2: str, pass_number: int, forced_visit: bool = False) -> dict:
    """`forced_visit=True` means the caller already resolved an unexpired lead of p1's toward p2
    (pick_pair.py + roll_lead_followup.py, run by whoever fixed this pair before calling here) -
    p1 is always the traveler in that case, home is fixed to p2 outright, skipping the ordinary
    home-visit coin flip below (roll_home_visit.py) since the lead is a stronger, already-resolved
    signal.

    Causal order rewritten 2026-08-28 design debrief - see CHRONICLE.md's matching entry for the
    full reasoning: home/visiting is now decided BEFORE any routine is rolled (not derived after the
    fact by comparing two independently-rolled routines), only the home participant ever rolls a
    routine at all, and arc primacy is decided AFTER home/visiting and independently of it - the
    visiting participant's arc can still be the one that leads the scene. Needs/provides, contested,
    and the alignment gate all key off whichever arc primacy actually picked, never off "the
    traveler" as a fixed role."""
    notes = []
    p1_char, p2_char = lib.load_char(p1), lib.load_char(p2)

    # Partner tracking - moved to the very top (2026-08-28 reorder): unconditional bookkeeping the
    # moment this pair is fixed, with nothing to do with anything decided below.
    lib.record_partner(p1, p2)
    lib.record_partner(p2, p1)
    p1_char, p2_char = lib.load_char(p1), lib.load_char(p2)

    # Home/visiting, then (home only) routine, then location/context assembly - no script call left
    # for the location step itself, see simulate_pass_lib.assemble_location()'s own docstring.
    if forced_visit:
        home, visiting = p2, p1
        notes.append(f"{p1} followed a lead to {p2}")
    else:
        home, visiting = lib.roll_home_visit(p1, p2)
    home_char = p1_char if home == p1 else p2_char
    home_routine = lib.roll_routine(home_char["routines"])
    loc = lib.assemble_location(home, home_routine, visiting, home_char)
    location, home_frame, traveler = loc["location"], loc["home_frame"], loc["traveler"]
    context, texture, provides = loc["context"], loc["texture"], loc["provides"]

    # Arc primacy - decided next, independently of who's home vs visiting.
    primacy = lib.roll_arc_primacy(p1, p2)
    primary_char = p1_char if primacy == p1 else p2_char
    other_char = p2_char if primacy == p1 else p1_char
    arc = primary_char.get("arc")

    # Needs/provides - keyed to the primacy winner's own arc, whichever participant that is.
    motivated, matched_need, matched_provide = False, None, None
    if arc and arc.get("resolution") == "ongoing" and arc.get("needs"):
        np_res = lib.check_needs_provides(arc["needs"], provides)
        motivated = np_res["match"] == "true"
        if motivated:
            matched_need = np_res.get("matched_need")
            matched_provide = np_res.get("matched_provide")

    # Contested - roll only if motivated, same as always. Relationship-aware 2026-08-28: the peer's
    # own established tie to the primacy winner skews the odds (see roll_contested.py's docstring).
    peer_strength = other_char.get("partners", {}).get(primacy, 0)
    peer_quality = other_char.get("partners_quality", {}).get(primacy, 0)
    contested = lib.roll_contested(strength=peer_strength, quality=peer_quality) if motivated else False

    # Gate, outcome (now contested-aware), tally/threshold (including transform)
    arc_authoring_needed = None
    gate_hit, inclined, arc_outcome, tally_result, matched_about = False, None, None, None, []

    if not arc:
        if primacy == home_frame:
            arc_authoring_needed = {
                "character_slug": primacy, "reason": "first",
                "band": lib.horizon(primacy)["band"],
                "origin": primary_char.get("origin", ""), "location": primary_char.get("location", ""), "backstory": primary_char.get("backstory", ""),
                "criterion": primary_char.get("criterion", {}), "routines": primary_char.get("routines", []),
                "prior_arc": None,
            }
            notes.append(f"{primacy} needs a first arc authored (home_frame, no arc yet)")
    elif arc.get("resolution") == "ongoing":
        gate_res = lib.check_arc_alignment(arc.get("about", []), arc.get("needs", []), other_char)
        gate_hit = gate_res["gate"] == "hit"
        if gate_hit:
            inclined = gate_res.get("inclined", "neutral")
            other_key = p2 if primacy == p1 else p1
            quality_delta = lib.BOND_QUALITY_DELTA[inclined]
            if quality_delta:
                lib.record_bond_quality(other_key, primacy, quality_delta)
            arc_outcome = lib.roll_arc_outcome(inclined, contested=contested)
            arc.setdefault("history", []).append({"pass": pass_number, "outcome": arc_outcome})
            score = lib.tally(arc["history"])
            if score >= lib.ARC_RESOLUTION_THRESHOLD:
                arc["resolution"] = "complete"
                tally_result = "complete"
                notes.append(f"{primacy}'s arc completed")
                arc_authoring_needed = {
                    "character_slug": primacy, "reason": "reauthor_complete",
                    "band": lib.horizon(primacy)["band"],
                    "origin": primary_char.get("origin", ""), "location": primary_char.get("location", ""), "backstory": primary_char.get("backstory", ""),
                    "criterion": primary_char.get("criterion", {}), "routines": primary_char.get("routines", []),
                    "prior_arc": arc,
                }
            elif score <= -lib.ARC_RESOLUTION_THRESHOLD:
                matched_about = gate_res.get("matched_about") or []
                if matched_about:
                    arc["about"] = matched_about
                    arc["history"][-1]["outcome"] = "transform"
                    tally_result = "transform"
                    notes.append(f"{primacy}'s arc transformed -> {matched_about}")
                else:
                    arc["resolution"] = "failed"
                    tally_result = "failed"
                    notes.append(f"{primacy}'s arc failed")
                    arc_authoring_needed = {
                        "character_slug": primacy, "reason": "reauthor_failed",
                        "band": lib.horizon(primacy)["band"],
                        "origin": primary_char.get("origin", ""), "location": primary_char.get("location", ""), "backstory": primary_char.get("backstory", ""),
                        "criterion": primary_char.get("criterion", {}), "routines": primary_char.get("routines", []),
                        "prior_arc": arc,
                    }
            else:
                tally_result = "ongoing"
                notes.append(f"{primacy}'s arc: {arc_outcome}")
            lib.save_char(primacy, primary_char)

    # Consequence slot - only surfaced on a contested scene that resolved "hinder"
    contested_hinder_slot = None
    if contested and gate_hit and inclined == "hinder":
        contested_hinder_slot = {
            "traveler": traveler, "supplier": home_frame, "matched_provide": matched_provide,
        }

    # Reproduction is deliberately NOT decided here (2026-08-28: moved to
    # simulate_pass_reproduction.py, run after the scene) - see this function's own docstring.

    return {
        "pass": pass_number,
        "participant_1": p1, "participant_2": p2,
        "forced_visit": forced_visit,
        "location": location, "home_frame": home_frame, "traveler": traveler,
        "context": context, "texture": texture,
        "motivated": motivated, "matched_need": matched_need, "matched_provide": matched_provide,
        "contested": contested,
        "arc": {
            "primacy_winner": primacy, "gate": "hit" if gate_hit else "miss", "inclined": inclined,
            "outcome": arc_outcome, "tally_result": tally_result, "matched_about": matched_about,
        },
        "arc_authoring_needed": arc_authoring_needed,
        "contested_hinder_slot": contested_hinder_slot,
        "character_files": {
            p1: str(lib.CHAR_DIR / f"{p1}.json"), p2: str(lib.CHAR_DIR / f"{p2}.json"),
        },
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pair", nargs=2, metavar=("P1", "P2"), required=True,
                         help="The two already-fixed participant slugs")
    parser.add_argument("--pass-number", type=int, required=True)
    parser.add_argument("--forced-visit", action="store_true",
                         help="P1 is visiting P2 because of an already-resolved unexpired lead")
    args = parser.parse_args()

    p1, p2 = args.pair[0].lower(), args.pair[1].lower()
    brief = run_pre_scene(p1, p2, args.pass_number, forced_visit=args.forced_visit)

    BRIEF_PATH.write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"pass {brief['pass']}: {brief['participant_1']} x {brief['participant_2']} (home: {brief['home_frame']}, at {brief['location']})")
    if brief["forced_visit"]:
        print(f"  forced visit (lead followup): {brief['participant_1']} sought out {brief['participant_2']}")
    print(f"  context: {brief['context']}  |  motivated: {brief['motivated']}" + (f" ({brief['matched_need']} <-> {brief['matched_provide']})" if brief["motivated"] else ""))
    print(f"  contested: {brief['contested']}")
    arc = brief["arc"]
    print(f"  arc: primacy={arc['primacy_winner']}  gate={arc['gate']}  inclined={arc['inclined']}  outcome={arc['outcome']}  tally={arc['tally_result']}")
    for n in brief["notes"]:
        print(f"  note: {n}")
    print()
    print(f"brief written: {BRIEF_PATH}")
    if brief["arc_authoring_needed"]:
        a = brief["arc_authoring_needed"]
        print(f"JUDGMENT NEEDED - arc authoring: {a['character_slug']} ({a['reason']}, band={a['band']}) - compose about/needs/context/premise, then run write_arc.py")
    if brief["contested_hinder_slot"]:
        c = brief["contested_hinder_slot"]
        print(f"JUDGMENT SLOT - contested hinder: may name an existing rival for {c['traveler']} (supplier: {c['supplier']}, provide: {c['matched_provide']}) - if named, run apply_contested_lead.py; otherwise leave ambient")
    print("(reproduction is no longer decided here - run simulate_pass_reproduction.py after the scene)")


if __name__ == "__main__":
    main()
