"""
Derive a routine-grounded `needs` shortlist for arc authoring/re-authoring - mechanizes the
grounding discipline `.claude/skills/character/SKILL.md` Step 8 already documents ("arc is seeded
from the routine's context + routine_actions + criterion, not restated from criterion.anchor
alone") but never actually enforced. Built 2026-08-31 on user correction after six consecutive arc
re-authorings in one /simulate run, all by the same author, converged on needs=["news"] regardless
of topic - the documented discipline existed only in prose, nothing checked whether an author
actually consulted a character's own routine before picking `needs`. See
.claude/PRINCIPLES.md's "script everything that can be scripted."

For a given character and (optionally) a specific arc `context`, this reuses
check_needs_provides.py's own significant_words() word-overlap logic to rank that context's
registered `provides` vocabulary (_lore/contexts.json) by how much it textually overlaps with the
character's own `routine_actions` text for a routine in that context - the same mechanical
comparison the pass mechanism itself will later use to decide whether a scene actually satisfies an
arc's needs, just run here, at authoring time, to surface which of the FEW valid choices (see
write_arc.py's own hard gate - needs must be drawn from this same provides list) this character's
own concrete activity actually supports.

This does NOT decide the arc's needs for the author - ranking, not choosing, is what's mechanical
here. `write_arc.py` still requires an explicit `--needs` argument and still rejects anything outside
the context's provides list; this script only narrows "which of those few valid options fits this
character" from "guess" to "read off a ranked list."

Usage:
    py scripts/lore/suggest_arc_needs.py mekhaomest
    py scripts/lore/suggest_arc_needs.py mekhaomest --context market
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
CONTEXTS_PATH = ROOT / "_lore" / "contexts.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_needs_provides import significant_words  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key")
    parser.add_argument("--context", default=None, help="Restrict to one of this character's own routines[].context; omit to rank across all of them")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    character = json.loads(char_path.read_text(encoding="utf-8"))
    contexts = json.loads(CONTEXTS_PATH.read_text(encoding="utf-8"))

    routines = character.get("routines", [])
    if args.context:
        routines = [r for r in routines if r.get("context") == args.context]
        if not routines:
            raise SystemExit(f"'{key}' has no routine with context '{args.context}'.")

    if not routines:
        raise SystemExit(f"'{key}' has no routines at all - nothing to ground needs against.")

    for routine in routines:
        ctx = routine.get("context")
        provides = contexts.get(ctx, {}).get("provides", [])
        actions_words = significant_words(routine.get("routine_actions", ""))

        ranked = []
        for p in provides:
            overlap = actions_words & significant_words(p)
            ranked.append((len(overlap), p))
        ranked.sort(key=lambda x: -x[0])

        print(f"context: {ctx}  (routine_actions: {routine.get('routine_actions', '')!r})")
        for score, p in ranked:
            marker = " <- grounded in routine_actions" if score > 0 else ""
            print(f"  {p} (overlap: {score}){marker}")
        print()


if __name__ == "__main__":
    main()
