"""
Run every MECHANICAL decision in one /simulate extended-mode pass - pairing through the reproduction
roll (the old Step 3 points 1-13 in .claude/skills/simulate/SKILL.md, minus the three things that
genuinely need a model) - and hand the result to the pass's subagent as a single JSON brief, instead
of the subagent making 12+ sequential `py scripts/lore/*.py` calls itself and hand-relaying each
result into the next call's arguments (design debrief 2026-08-13, following the same mechanization
`-generate` mode's simulate_generate_population.py already proved out for the mechanical-pregeneration
case - this is that same pipeline's logic, reused via simulate_pass_lib.py, run one pass at a time
instead of N in a row, with three deliberate stopping points left open for the subagent).

Exactly three things are deliberately left undecided here, flagged in the brief for the subagent to
fill - nothing else in this file's output is the subagent's to decide:
  - `arc_authoring_needed` - the fallback path for a character who reached extended-mode play
    without an arc already on file (as of 2026-08-16, `/character` Step 8 authors `arc` at creation
    time by default): their first arc, or a re-authored one after a failure or after completing the
    prior one (`reauthor_failed`/`reauthor_complete` - completing an arc isn't a reason to stop
    having one). Content (about/needs/context/premise) is composed by the subagent, then written
    with write_arc.py (which also registers the concept in the same call).
  - `contested_hinder_slot` - only present on a contested visit that resolved "hinder" homeward. The
    subagent may dramatize this against a SPECIFIC existing rival (if one plausibly fits and already
    has a character file) or keep it ambient/unnamed (the default). If named, call
    apply_contested_lead.py with the rival's slug.
  - `reproduction_slot` - only present when an eligible pair's roll came back true. The subagent
    composes the child's name (a blend leading from `name_lead`'s side) and calls
    generate_offspring.py itself - the one thing about a birth that can't be scripted.

Everything else in the brief is already fixed and written to disk by the time this script returns:
arc gate/outcome/tally (including any transform), partner counts, which participants are even in the
scene, where, why, and whether contested - the subagent's job past this point is /enact Steps 3b, 5,
5b, 6 (the scene itself, hearsay mutation, shock resolution, drift) plus the three slots above, never
re-deciding anything already settled here.

Writes `.simulate_pass_brief.json` at the worktree root (same location as .simulate_snapshot.json) -
simulate_pass_resolve.py reads it back after the scene to run the post-scene mechanics (life.lived
already incremented by /enact's own Step 5b work by then; this script never touches life.lived).

Usage:
    py "<worktree>/scripts/lore/simulate_pass_brief.py" --pool khaoe farlis nerkeli --pass-number 12
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


def run_pre_scene(pool: list, pass_number: int) -> dict:
    notes = []

    p1, p2 = lib.pick_pair(pool)
    p1_char, p2_char = lib.load_char(p1), lib.load_char(p2)

    # Step 2 - lead override (only relevant if participant_1 carries an unexpired lead)
    forced_visit = False
    leads = p1_char.get("leads", [])
    fresh_leads = [l for l in leads if pass_number - l["created_pass"] < lib.LEAD_EXPIRY_PASSES]
    if len(fresh_leads) != len(leads):
        p1_char["leads"] = fresh_leads
        lib.save_char(p1, p1_char)
    if fresh_leads:
        res = lib.roll_lead_followup([l["target"] for l in fresh_leads])
        if res["followed"] == "true":
            target = res["lead"]
            if target in pool and target != p1:
                p2 = target
                p2_char = lib.load_char(p2)
                p1_char["leads"] = [l for l in fresh_leads if l["target"] != target]
                lib.save_char(p1, p1_char)
                forced_visit = True
                notes.append(f"{p1} followed a lead to {p2}")

    # Steps 3/4/5 - routine, location, and context+texture, folded into one call
    p2_routine = lib.roll_routine(p2_char["routines"])
    if forced_visit:
        context = lib.resolve_context_for_location(p2_char, p2_routine)
        loc = {
            "mode": "visit", "location": p2_routine, "home_frame": p2, "traveler": p1,
            "context": context, "texture": lib.CONTEXTS[context]["texture"],
            "provides": lib.CONTEXTS[context]["provides"],
        }
    else:
        p1_routine = lib.roll_routine(p1_char["routines"])
        loc = lib.resolve_location(p1, p1_routine, p1_char, p2, p2_routine, p2_char)

    mode, location, home_frame = loc["mode"], loc["location"], loc["home_frame"]
    traveler = loc["traveler"] if loc["traveler"] != "none" else None
    context, texture, provides = loc["context"], loc["texture"], loc["provides"]

    # Step 6 - needs/provides (visit only, traveler must have an active arc with needs)
    motivated, matched_need, matched_provide = False, None, None
    if mode == "visit" and traveler:
        traveler_char = p1_char if traveler == p1 else p2_char
        t_arc = traveler_char.get("arc")
        if t_arc and t_arc.get("resolution") == "ongoing" and t_arc.get("needs"):
            np_res = lib.check_needs_provides(t_arc["needs"], provides)
            motivated = np_res["match"] == "true"
            if motivated:
                matched_need = np_res.get("matched_need")
                matched_provide = np_res.get("matched_provide")

    # Step 9 (roll only) - contested, only if motivated
    contested = lib.roll_contested() if motivated else False

    # Steps 7/8/10/11 - arc primacy, gate, outcome, tally/threshold (including transform)
    primacy = lib.roll_arc_primacy(p1, p2)
    primary_char = p1_char if primacy == p1 else p2_char
    other_char = p2_char if primacy == p1 else p1_char
    arc = primary_char.get("arc")

    arc_authoring_needed = None
    gate_hit, inclined, arc_outcome, tally_result, matched_about = False, None, None, None, []

    if not arc:
        if primacy == home_frame:
            arc_authoring_needed = {
                "character_slug": primacy, "reason": "first",
                "band": lib.horizon(primacy)["band"],
                "city": primary_char.get("city", ""), "backstory": primary_char.get("backstory", ""),
                "criterion": primary_char.get("criterion", {}), "routines": primary_char.get("routines", []),
                "prior_arc": None,
            }
            notes.append(f"{primacy} needs a first arc authored (home_frame, no arc yet)")
    elif arc.get("resolution") == "ongoing":
        gate_res = lib.check_arc_alignment(arc.get("about", []), arc.get("needs", []), other_char)
        gate_hit = gate_res["gate"] == "hit"
        if gate_hit:
            inclined = gate_res.get("inclined", "neutral")
            arc_outcome = lib.roll_arc_outcome(inclined)
            arc.setdefault("history", []).append({"pass": pass_number, "outcome": arc_outcome})
            score = lib.tally(arc["history"])
            if score >= lib.ARC_RESOLUTION_THRESHOLD:
                arc["resolution"] = "complete"
                tally_result = "complete"
                notes.append(f"{primacy}'s arc completed")
                arc_authoring_needed = {
                    "character_slug": primacy, "reason": "reauthor_complete",
                    "band": lib.horizon(primacy)["band"],
                    "city": primary_char.get("city", ""), "backstory": primary_char.get("backstory", ""),
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
                        "city": primary_char.get("city", ""), "backstory": primary_char.get("backstory", ""),
                        "criterion": primary_char.get("criterion", {}), "routines": primary_char.get("routines", []),
                        "prior_arc": arc,
                    }
            else:
                tally_result = "ongoing"
                notes.append(f"{primacy}'s arc: {arc_outcome}")
            lib.save_char(primacy, primary_char)

    # Step 9 (consequence slot) - only surfaced on a contested visit that resolved "hinder"
    contested_hinder_slot = None
    if contested and gate_hit and inclined == "hinder" and traveler:
        contested_hinder_slot = {
            "traveler": traveler, "supplier": home_frame, "matched_provide": matched_provide,
        }

    # Step 12 - partner tracking, always both directions
    lib.record_partner(p1, p2)
    lib.record_partner(p2, p1)
    p1_char, p2_char = lib.load_char(p1), lib.load_char(p2)

    # Step 13 (eligibility + roll only) - name composition and generate_offspring.py stay with
    # the subagent; this driver deliberately never calls generate_offspring.py itself.
    reproduction_slot = None
    count_ab = p1_char.get("partners", {}).get(p2, 0)
    count_ba = p2_char.get("partners", {}).get(p1, 0)
    eligible = max(count_ab, count_ba) >= lib.PARTNER_THRESHOLD
    cooldown_ok = all(
        c.get("last_reproduced_pass") is None
        or pass_number - c["last_reproduced_pass"] >= lib.PARENT_COOLDOWN_PASSES
        for c in (p1_char, p2_char)
    )
    already_parent_child = p2 in p1_char.get("parents", []) or p1 in p2_char.get("parents", [])
    if eligible and cooldown_ok and not already_parent_child:
        repro = lib.roll_reproduction(p1, p2)
        if repro["reproduces"] == "true":
            name_lead = repro["name_lead"]
            other_parent = p2 if name_lead == p1 else p1
            reproduction_slot = {"parent_a": p1, "parent_b": p2, "name_lead": name_lead, "other_parent": other_parent}
            notes.append(f"{p1}+{p2} eligible and rolled true - name composition needed (lead: {name_lead})")

    return {
        "pass": pass_number,
        "participant_1": p1, "participant_2": p2,
        "forced_visit": forced_visit,
        "mode": mode, "location": location, "home_frame": home_frame, "traveler": traveler,
        "context": context, "texture": texture,
        "motivated": motivated, "matched_need": matched_need, "matched_provide": matched_provide,
        "contested": contested,
        "arc": {
            "primacy_winner": primacy, "gate": "hit" if gate_hit else "miss", "inclined": inclined,
            "outcome": arc_outcome, "tally_result": tally_result, "matched_about": matched_about,
        },
        "arc_authoring_needed": arc_authoring_needed,
        "contested_hinder_slot": contested_hinder_slot,
        "reproduction_slot": reproduction_slot,
        "character_files": {
            p1: str(lib.CHAR_DIR / f"{p1}.json"), p2: str(lib.CHAR_DIR / f"{p2}.json"),
        },
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", nargs="+", required=True, help="Every slug still in the living pool")
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    pool = [s.lower() for s in args.pool]
    brief = run_pre_scene(pool, args.pass_number)

    BRIEF_PATH.write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"pass {brief['pass']}: {brief['participant_1']} x {brief['participant_2']} ({brief['mode']} at {brief['location']})")
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
    if brief["reproduction_slot"]:
        r = brief["reproduction_slot"]
        print(f"JUDGMENT NEEDED - child name: blend for {r['parent_a']}+{r['parent_b']}, leading from {r['name_lead']}'s name, then run generate_offspring.py")


if __name__ == "__main__":
    main()
