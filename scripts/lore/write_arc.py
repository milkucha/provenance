"""
Write a freshly-authored (or re-authored) arc onto a character's own file, and register its concept
tag in the same call - folds what used to be a hand-edited JSON write plus a separate
register_arc_concept.py invocation into one mechanical step (design debrief 2026-08-13).

This script makes NO judgement calls. `--about`/`--needs`/`--context`/`--premise` are content only a
model can compose - a name-blend-shaped problem, not a dice-roll-shaped one, same reasoning
generate_offspring.py's own docstring gives for why it can't script the child's name. What this script
owns is getting that already-decided content into the file correctly (resolution always starts
"ongoing", history always starts empty) and never forgetting the register_arc_concept.py follow-up,
which is exactly the kind of step a human/subagent forgets under load (see register_arc_concept.py's
own docstring: 42 arc concepts from earlier runs had been referenced by hundreds of hearsay claims but
never once existed as a real concepts[] entry, precisely because this was two separate manual steps
before).

`--premise` (added 2026-08-16) is the arc's actual concrete content - see `/character` Step 8 for the
authoring discipline it has to follow (the resolution-moment test, grounding the target in the
character's own known corpus, texture-vs-claim-shaped-content attribution). Without it, an arc was
only ever four bare tags plus a `concept:` entry whose own registered `description` just echoes those
same tags back - nothing about what the project concretely *is* ever persisted anywhere.

Called from three places now: `/character` Step 8 (a character's arc, authored at creation time - the
normal path as of 2026-08-16), and `/simulate`'s extended-mode pass sequence as the fallback for a
character who reached extended-mode play without one yet - either their very first arc (first primacy
win as home_frame with no existing arc), or a re-authored one after the previous one resolved "failed"
or "complete" (both trigger the same re-authoring judgment slot). All three are plain overwrites of
character.arc - there is nothing to preserve from a prior arc (its history stays on record in
encodings.json via whatever it registered, not on the character file itself).

Usage:
    py scripts/lore/write_arc.py khaoe --about "concept: khaoe_banco_colectivo" --about "location: terfila" \\
        --needs "materials" --needs "contacts" --context market \\
        --premise "Khaoe wants the Collective hall roofed before the next rains - real timber, real crews, a real finish date."
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
SCRIPTS_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key whose arc gets (re)written")
    parser.add_argument("--about", action="append", default=[], required=True, help="Arc.about tag(s), repeatable - at least one 'concept: <id>' tag for a genuinely new project")
    parser.add_argument("--needs", action="append", default=[], required=True, help="Arc.needs tag(s), repeatable")
    parser.add_argument("--context", required=True, help="Must be a key already in _lore/contexts.json, ordinarily matching one of this character's own routines[].context")
    parser.add_argument("--premise", required=True, help="The arc's concrete content, one-or-few-sentence prose - see /character Step 8 for the authoring discipline (resolution-moment test, grounding, claim attribution)")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    contexts = json.loads((ROOT / "_lore" / "contexts.json").read_text(encoding="utf-8"))
    if args.context not in contexts:
        raise SystemExit(f"'{args.context}' is not a key in _lore/contexts.json - known: {sorted(contexts)}")

    # Mechanized 2026-08-31, on user correction: `needs` used to be free-typed prose, with no
    # check that it connected to anything the character's own world could plausibly supply -
    # confirmed drifting hard in practice (six consecutive arc re-authorings in one /simulate run,
    # by the same author, all used needs=["news"] regardless of topic, one of them for a
    # materials/labor-shaped project). `needs` must now be drawn from the SAME vocabulary
    # check_needs_provides.py will later match it against - this context's own registered
    # `provides` list in _lore/contexts.json - so a `needs` tag that could never be satisfied by
    # anything in this world is caught here, at authoring time, not discovered as a silently-dead
    # arc later. See scripts/lore/suggest_arc_needs.py for a routine-grounded shortlist within
    # this same vocabulary, and .claude/PRINCIPLES.md's "script everything that can be scripted."
    provides = contexts[args.context].get("provides", [])
    invalid = [n for n in args.needs if n not in provides]
    if invalid:
        raise SystemExit(
            f"needs {invalid} not in _lore/contexts.json['{args.context}']['provides'] "
            f"({provides}) - needs must be drawn from what this context can actually supply, "
            f"not free-typed. Run scripts/lore/suggest_arc_needs.py {key} for a routine-grounded "
            f"shortlist."
        )

    character["arc"] = {
        "about": list(args.about),
        "needs": list(args.needs),
        "context": args.context,
        "premise": args.premise,
        "resolution": "ongoing",
        "history": [],
    }
    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"{key}: arc written (about: {args.about}, needs: {args.needs}, context: {args.context})")
    print(f"{key}: premise: {args.premise}")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "register_arc_concept.py"), key],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"arc written, but register_arc_concept.py failed (exit {result.returncode}):\n{result.stderr}")
    sys.stdout.write(result.stdout)


if __name__ == "__main__":
    main()
