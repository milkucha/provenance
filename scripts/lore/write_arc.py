"""
Write a freshly-authored (or re-authored) arc onto a character's own file, and register its concept
tag in the same call - folds what used to be a hand-edited JSON write plus a separate
register_arc_concept.py invocation into one mechanical step (design debrief 2026-08-13).

This script makes NO judgement calls. `--about`/`--needs`/`--archetype` are content only a model can
compose - a name-blend-shaped problem, not a dice-roll-shaped one, same reasoning generate_offspring.py's
own docstring gives for why it can't script the child's name. What this script owns is getting that
already-decided content into the file correctly (resolution always starts "ongoing", history always
starts empty) and never forgetting the register_arc_concept.py follow-up, which is exactly the kind of
step a human/subagent forgets under load (see register_arc_concept.py's own docstring: 42 arc concepts
from earlier runs had been referenced by hundreds of hearsay claims but never once existed as a real
concepts[] entry, precisely because this was two separate manual steps before).

Called from two places in /simulate's extended-mode pass sequence: a character's very first arc (their
first primacy win as home_frame with no existing arc), and a re-authored arc after the previous one
resolved "failed". Both are plain overwrites of character.arc - there is nothing to preserve from a
failed arc (its history stays on record in encodings.json via whatever it registered, not on the
character file itself).

Usage:
    py scripts/lore/write_arc.py khaoe --about "concept: khaoe_banco_colectivo" --about "location: terfila" \\
        --needs "materials" --needs "contacts" --archetype market
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
    parser.add_argument("--archetype", required=True, help="Must be a key already in _lore/archetypes.json, ordinarily matching one of this character's own routines[].archetype")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    archetypes = json.loads((ROOT / "_lore" / "archetypes.json").read_text(encoding="utf-8"))
    if args.archetype not in archetypes:
        raise SystemExit(f"'{args.archetype}' is not a key in _lore/archetypes.json - known: {sorted(archetypes)}")

    character["arc"] = {
        "about": list(args.about),
        "needs": list(args.needs),
        "archetype": args.archetype,
        "resolution": "ongoing",
        "history": [],
    }
    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"{key}: arc written (about: {args.about}, needs: {args.needs}, archetype: {args.archetype})")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "register_arc_concept.py"), key],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"arc written, but register_arc_concept.py failed (exit {result.returncode}):\n{result.stderr}")
    sys.stdout.write(result.stdout)


if __name__ == "__main__":
    main()
