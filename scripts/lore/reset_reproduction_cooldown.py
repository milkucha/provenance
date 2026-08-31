"""
Clear `last_reproduced_pass` (and `birth_pass`, same reasoning) on every participant at a new
/simulate run's own setup: a `/simulate` run's pass counter always starts at 1 regardless of the
branched-from commit's own history, but `last_reproduced_pass` is an absolute scalar carried over
unreset from whatever earlier run wrote it. Reproduction eligibility checks `this_run_pass_number -
last_reproduced_pass >= parent_cooldown_passes` (simulate_pass_reproduction.py) - a character who had
a child at old-run pass 362 reads, to a new run starting at pass 1, as having had a child 361 passes
in the future, permanently blocking them (in practice: until this run's own pass count happens to
exceed that old absolute number) for no in-fiction reason at all.

`birth_pass` gets the same treatment for the same reason: it's read by `generate_offspring.py` (a
child's own `pool-eligible once current pass number >= birth_pass + child_cooldown_passes` line) and
by nothing else that treats it as a fixed historical fact worth preserving across runs - a stale
`birth_pass` would just as wrongly gate a leftover not-yet-matured child from a PRIOR run's own
numbering.

This does NOT touch anyone's `partners`/`partners_quality` (interaction history - a real fact worth
keeping) or `arc.history` (already scoped correctly, confirmed empirically: reauthored arcs in the
2026-08-31 run only ever accumulated entries under the CURRENT run's own pass numbers, never leaked
old-run numbers - see CHRONICLE.md/LAB_REPORT.md for that diagnosis). Only the two absolute-pass-number
scalars that a fresh run's own pass-1 start makes meaningless.

Wired into /simulate's own Step 1/2 setup (see SKILL.md) - call once, right after the participant pool
is finalized, before Step 3's first pass.

Usage:
    py scripts/lore/reset_reproduction_cooldown.py --pool character_a character_c character_b
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", nargs="+", required=True, help="Participant slugs for this run")
    args = parser.parse_args()

    cleared = []
    for slug in args.pool:
        key = slug.lower()
        path = CHAR_DIR / f"{key}.json"
        if not path.exists():
            raise SystemExit(f"No character file for '{key}'.")
        with open(path, encoding="utf-8") as f:
            character = json.load(f)
        touched = False
        if character.get("last_reproduced_pass") is not None:
            character["last_reproduced_pass"] = None
            touched = True
        if character.get("birth_pass") is not None:
            character["birth_pass"] = None
            touched = True
        if touched:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(character, f, indent=2, ensure_ascii=False)
                f.write("\n")
            cleared.append(key)

    print(f"cleared last_reproduced_pass/birth_pass on {len(cleared)} of {len(args.pool)} participant(s)")
    for k in cleared:
        print(f"  {k}")


if __name__ == "__main__":
    main()
