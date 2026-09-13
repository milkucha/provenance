"""
Fast-forward many passes of /simulate's extended-mode mechanic with NO scene-writing and NO
subagent per pass - built for `/generate`, whose whole point is producing a large,
multi-generation starting population quickly rather than a showcase trail of prose. Runs the same
asymmetric per-pass algorithm simulate_pass_brief.py runs for `/enact` (design session 2026-09-13 -
see TODO.md's "asymmetric per-pass rewrite" entry and CHRONICLE.md's matching entry), via the shared
`simulate_pass_lib.run_pass_mechanics()`: draw one `p1` (draw_participant(), née pick_pair()'s
draw-two), survive-vs-arc, and - only if arc - local satisfaction or pathfinding, the "missed
connection" roll, `p2`'s own routine roll, the payment gate, then the unchanged contested/alignment/
outcome/tally chain. `p2` is never fixed up front any more; run_pass() below only acts on it when
run_pass_mechanics() actually surfaces one this pass.

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
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
TEST_DIR = ROOT / "scripts" / "test"
CHAR_DIR = ROOT / "_lore" / "characters"
PENDING_PATH = ROOT / "_pending_language.json"
SNAPSHOT_PATH = ROOT / ".simulate_snapshot.json"
LOG_PATH = ROOT / "GENERATION_LOG.md"

sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402
import simulate_pass_reproduction as repro_lib  # noqa: E402
import rng_context  # noqa: E402
import run_manifest  # noqa: E402

load_char = lib.load_char
save_char = lib.save_char
call = lib.call
kv = lib.kv
notified_keys = lib.notified_keys
draw_participant = lib.draw_participant
horizon = lib.horizon
record_death = lib.record_death
roll_death_legacy = lib.roll_death_legacy
update_character_lived = lib.update_character_lived
generate_offspring = lib.generate_offspring
run_pass_mechanics = lib.run_pass_mechanics


def call_test(script_name: str, argv: list) -> str:
    """scripts/test/ siblings are invoked the same absolute-path-always way as scripts/lore/ ones
    (lib.call()) - never a relative one, never dependent on cwd."""
    result = subprocess.run([sys.executable, str(TEST_DIR / script_name), *argv], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} {argv} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


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
    """Asymmetric per-pass model (design session 2026-09-13) - draws only `p1` (draw_participant(),
    née pick_pair()'s draw-two), then runs the entire mechanical algorithm via
    simulate_pass_lib.run_pass_mechanics() (shared verbatim with simulate_pass_brief.py - see that
    function's own docstring for the full step-by-step). `participant_2`, if any, is discovered
    inside that call, never fixed here - a solo survive/travel/no-target/missed-connection pass has
    no second participant at all, so reproduction/death/death-legacy below only ever consider
    whichever of p1/p2 actually took part this pass."""
    p1 = draw_participant(state.living)
    result = run_pass_mechanics(p1, pass_number)
    notes = result["notes"]
    p2 = result["participant_2"]

    if result["arc_authoring_needed"]:
        reason = result["arc_authoring_needed"]["reason"]
        p1_char = load_char(p1)
        if queue_arc(state, p1, p1_char, reason, pass_number):
            notes.append(f"{p1} queued for {'a first arc' if reason == 'first' else reason}")

    # Reproduction eligibility + roll - shared with the interactive path's own post-scene check
    # (simulate_pass_reproduction.py) rather than a third copy of the same logic; this file's own
    # ancestor_cache still gets threaded through for the same perf reason it always was. Only
    # relevant when a genuine p1/p2 meeting happened this pass at all (see module docstring point 3
    # for why this mode never names a contested rival either - same "no invented identity" limit).
    if p2:
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
            p1_char, p2_char = load_char(p1), load_char(p2)
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

    # Step 15/16 - life.lived, death, death-legacy, for whichever of p1/p2 actually took part this
    # pass. Two independent death vectors: the existing rolled lifespan (horizon.py's "ending"), and
    # energy hitting 0 (survival mechanism, checked second so a natural-lifespan death this same
    # pass always takes priority if somehow both fire).
    participants = [p1] + ([p2] if p2 else [])
    for participant in participants:
        update_character_lived(participant, 1)
        h = horizon(participant)
        natural = h["ending"] == "true"
        starved = (not natural) and result["survival"].get(participant, {}).get("died", False)
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

    summary = f"pass {pass_number}: {p1}" + (f" x {p2}" if p2 else " (solo)") + f" (at {result['location']}"
    if result["motivated"]:
        summary += f", motivated{' contested' if result['contested'] else ''}"
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
    parser.add_argument("--seed", type=int, default=None, help="RNG seed - if given, this is a seeded run (the isolation experiment: an identical --seed + identical starting commit reproduces identical mechanical records). Omit for a free/unseeded run (default, today's exact behavior).")
    parser.add_argument("--mode", choices=["simple", "divergence"], default="simple", help="Recorded on the run manifest only - a per-run label, not a different code path.")
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
    run_manifest.write(ROOT, args.mode, args.seed, pool, args.passes)
    if args.seed is not None:
        rng_context.start_seeded_run(ROOT, args.seed)

    state = State(pool)
    ran = 0
    for pass_number in range(1, args.passes + 1):
        if len(state.living) < 2:
            print(f"Stopping early after {ran} pass(es) - fewer than 2 living participants remain.")
            break
        rng_context.set_current_pass(pass_number)
        summary = run_pass(state, pass_number)
        state.log.append(summary)
        print(summary)
        ran += 1

    PENDING_PATH.write_text(
        json.dumps({"generated_at_pass": ran, **state.pending}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Test-suite closing steps - automatic per TESTING_BRIEF.md §4.1/§4.2 ("wire into the run
    # workflow so a run produces it automatically"). Both tools are lean (stdlib-only, read the
    # draw-audit log + character files already on disk) and no-op cleanly if this run was unseeded/
    # free (they still report machinery conformance and derivation coverage either way).
    test_report_lines = []
    conformance_out = call_test("conformance_report.py", ["--root", str(ROOT)])
    test_report_lines.append(conformance_out)
    derivation_out = call_test("measure_derivation.py", ["--root", str(ROOT)])
    test_report_lines.append(derivation_out)
    print(conformance_out)
    print(derivation_out)

    LOG_PATH.write_text(
        "# Generation log\n\n" + "\n".join(f"- {line}" for line in state.log) + "\n\n"
        + "## Test suite\n\n" + "\n\n".join(test_report_lines) + "\n",
        encoding="utf-8",
    )

    if args.living_pool_out:
        Path(args.living_pool_out).write_text(json.dumps(state.living, indent=2) + "\n", encoding="utf-8")

    run_manifest.finalize(ROOT, outputs={"generation_log": str(LOG_PATH), "snapshot": str(SNAPSHOT_PATH)}, passes_actually_run=ran)

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
    print(f"run manifest: {ROOT / run_manifest.MANIFEST_FILENAME}")
    if args.living_pool_out:
        print(f"living pool written: {args.living_pool_out}")


if __name__ == "__main__":
    main()
