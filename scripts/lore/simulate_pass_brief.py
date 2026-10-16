"""
Run every MECHANICAL decision in one /enact scene starting from one already-picked NPC (`p1`) - the
asymmetric per-pass model (design session 2026-09-13, see TODO.md's "asymmetric per-pass rewrite"
entry and CHRONICLE.md's matching entry). Replaces the old "already-fixed --pair" model: there is no
pre-selected second participant any more. `p1` rolls work-vs-arc, and if arc, the rest of the pass
- whether anyone else is even involved, and who - is discovered over the course of
`simulate_pass_lib.run_pass_mechanics()` (local satisfaction, travel, the "missed connection" roll,
p2's own routine roll, and the payment gate that now decides whether the pass is "motivated"). See
that function's own docstring for the full step-by-step algorithm.

Takes an already-fixed `--p1 <slug>` - who this is has already been decided by the time this runs,
either by an author (an ordinary `/enact` call) or by `/simulate`'s own pick_pair.py before it ever
dispatches here. Identity resolution stays out of this script's job for the same reason it always
was: `/enact`'s own eligibility gate (participant needs `routines`+`arc`) has already checked this
exact slug by the time this runs.

Exactly two things are deliberately left undecided here, flagged in the brief for the subagent to
fill - nothing else in this file's output is the subagent's to decide:
  - `arc_authoring_needed` - the fallback path for a character who reached extended-mode play
    without an arc (or without `needs` on it yet) already on file: their first arc, or a re-authored
    one after a failure or after completing the prior one (`reauthor_failed`/`reauthor_complete`).
    Content (about/needs/context/premise) is composed by the subagent, then written with
    write_arc.py (which also registers the concept in the same call).
  - `contested_hinder_slot` - only present on a motivated scene that resolved "hinder" against p1's
    arc AND rolled contested. The subagent may dramatize this against a SPECIFIC existing rival (if
    one plausibly fits and already has a character file) or keep it ambient/unnamed (the default).
    If named, call apply_contested_lead.py with the rival's slug.

Reproduction is decided post-scene, by the caller (`/enact` Step 8's simulate_pass_reproduction.py),
exactly as before - never here, and only when this brief's own `participant_2` is non-null (a solo
work/travel/no-target/empty-place pass has no second participant to reproduce with at all).

Pursuit redesign (2026-10-17): a pass whose arc choice sends the character after a need now carries a
`pursuit` object ({stage, reason, need, place, supplier, present, could_afford}; the stages are
simulate_pass_lib.PURSUIT_STAGES) and a `scene` flag ("pair" / "solo" / null) saying whether there is
something to dramatize. A failed arrival is a scene, not a dead pass; `motivated` still means only
that the payment went through.

Writes `.simulate_pass_brief.json` at the worktree root (same location as .simulate_snapshot.json) -
`/enact`'s own Step 5b reads it back to write the scene and resolve the two judgment slots above;
nothing reads it again after that. A pass with no `participant_2` (work, travel, no-target, an
empty place) has no second-NPC scene to enact at all under `/enact`'s existing Step 2/4 shape. Post-scene mechanics (horizon
re-check, death, death-legacy, reproduction) are `/enact` Step 8's own concern from there, working off
whichever of `participant_1`/`participant_2` are actually present, not this file.

Usage:
    py "<worktree>/scripts/lore/simulate_pass_brief.py" --p1 khaoe --pass-number 12
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"
CONTEXTS_PATH = ROOT / "_lore" / "contexts.json"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
TALES_DIR = ROOT / "_lore" / "tales"

sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402
import arc_completion  # noqa: E402
from check_needs_provides import significant_words  # noqa: E402


def needs_candidates(routines: list) -> list:
    """Mechanizes the routine-grounding discipline .claude/skills/character/SKILL.md Step 8
    documents but never enforced (found 2026-08-31: six consecutive arc re-authorings in one
    /simulate run, same author, converged on needs=["news"] regardless of the character's actual
    routine). Ranks each of a routine's context's registered `provides` tags
    (_lore/contexts.json - the same vocabulary write_arc.py now hard-requires `needs` to be drawn
    from) by textual overlap with that routine's own `routine_actions` text - same word-overlap
    check check_needs_provides.py itself uses to decide whether a scene satisfies an arc. Returns
    one entry per routine: {"context", "routine_actions", "ranked": [{"tag", "overlap"}, ...]}."""
    contexts = json.loads(CONTEXTS_PATH.read_text(encoding="utf-8"))
    out = []
    for routine in routines:
        ctx = routine.get("context")
        provides = contexts.get(ctx, {}).get("provides", [])
        actions_words = significant_words(routine.get("routine_actions", ""))
        ranked = sorted(
            ({"tag": p, "overlap": len(actions_words & significant_words(p))} for p in provides),
            key=lambda r: -r["overlap"],
        )
        out.append({"context": ctx, "routine_actions": routine.get("routine_actions", ""), "ranked": ranked})
    return out


def git_user_name() -> str:
    try:
        return subprocess.check_output(["git", "config", "user.name"], cwd=ROOT, text=True).strip() or "unknown"
    except Exception:
        return "unknown"


write_arc_completion_tale = arc_completion.write_arc_completion_tale  # moved to arc_completion.py (kept here for old callers)


def enrich_arc_authoring_needed(p1: str, reason: str) -> dict:
    """Fills out the minimal `{"character_slug", "reason"}` signal run_pass_mechanics() returns with
    everything the subagent actually needs to author/reauthor an arc - band, criterion, routines,
    ranked needs candidates, and (on a re-author) the prior arc for continuity/contrast. On
    `reauthor_complete`, the completion itself (tale, reward, telling, the children's inheritance)
    has already run inside run_pass_mechanics via arc_completion.complete(); the caller only reads
    the tale id off `brief["arc_completion"]`."""
    p1_char = lib.load_char(p1)
    prior_arc = p1_char.get("arc") if reason in ("reauthor_failed", "reauthor_complete") else None
    entry = {
        "character_slug": p1, "reason": reason,
        "band": lib.horizon(p1)["band"],
        "origin": p1_char.get("origin", ""), "location": p1_char.get("location", ""), "backstory": p1_char.get("backstory", ""),
        "criterion": p1_char.get("criterion", {}), "routines": p1_char.get("routines", []),
        "needs_candidates": needs_candidates(p1_char.get("routines", [])),
        "prior_arc": prior_arc,
    }
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True, help="The already-fixed participant slug")
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    lib.rng_context.set_current_pass(args.pass_number)
    p1 = args.p1.lower()
    brief = lib.run_pass_mechanics(p1, args.pass_number)

    if brief["arc_authoring_needed"]:
        reason = brief["arc_authoring_needed"]["reason"]
        entry = enrich_arc_authoring_needed(p1, reason)
        if reason == "reauthor_complete":
            # run_pass_mechanics already completed the arc (arc_completion.complete: tale, reward,
            # telling); the brief only carries the tale id for the enacter to tag.
            tale_id = brief["arc_completion"]["tale_id"]
            entry["completion_tale_id"] = tale_id
            brief["notes"].append(
                f"{p1}'s completed arc filed as tale '{tale_id}' - tag the completion-announcement "
                f"hearsay claim 'about: \"tale: {tale_id}\"'"
            )
        brief["arc_authoring_needed"] = entry

    BRIEF_PATH.write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    p2 = brief["participant_2"]
    print(f"pass {brief['pass']}: {p1}" + (f" x {p2}" if p2 else " (solo this pass)") + f" at {brief['location']}")
    if brief["travel"]:
        t = brief["travel"]
        print(f"  travel: target={t['target']} hop={t['hop']} path={t['path']}")
    print(f"  context: {brief['context']}  |  motivated: {brief['motivated']}" + (f" ({brief['matched_need']} <-> {brief['matched_provide']})" if brief["motivated"] else ""))
    pu = brief.get("pursuit")
    if pu:
        print(f"  pursuit: {pu['stage']}" + (f" ({pu['reason']})" if pu.get("reason") else "")
              + f"  need={pu['need']} place={pu['place']} supplier={pu['supplier']} present={pu['present']} could_afford={pu['could_afford']}")
    print(f"  scene: {brief.get('scene')}")
    print(f"  contested: {brief['contested']}")
    surv = brief["survival"]
    p1_surv = surv.get(p1, {})
    line = f"  survival: {p1}={p1_surv.get('choice')} (energy {p1_surv.get('energy')})"
    if p2 and p2 in surv:
        line += f"  {p2}=(energy {surv[p2].get('energy')})"
    print(line)
    arc = brief["arc"]
    print(f"  arc: gate={arc['gate']}  inclined={arc['inclined']}  outcome={arc['outcome']}  tally={arc['tally_result']}")
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
    if p1_surv.get("died"):
        print(f"DEATH - {p1}'s energy hit 0 this pass. Not yet recorded - run record_death.py {p1} --cause \"exhaustion/starvation\" post-scene, same as a horizon-ending death.")
    if p2:
        print("(reproduction is only relevant when participant_2 is present - run simulate_pass_reproduction.py after the scene if so)")


if __name__ == "__main__":
    main()
