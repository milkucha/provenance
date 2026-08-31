"""
Apply a death-legacy roll's `passes: true` result - the mechanical half of
`.claude/skills/enact/SKILL.md` Step 8 point 7, called only after `roll_death_legacy.py` itself
has already decided whether the arc passes on at all. This script does the one thing that roll
deliberately leaves undone: the actual arc transfer.

Not a fresh derivation for the recipient - the `about`/`needs` tags and `premise` carry over from
the deceased's own arc directly (same mechanical copy the transform mechanism already uses, see
check_arc_alignment.py's matched_about output), and `resolution` resets to "ongoing" the same way a
transform does, with a clean `history`. The recipient's own `context` wins if they already have an
ongoing arc or a routine to derive one from; only when neither exists does the deceased's own
context carry over as a last resort. `routine` is never touched - only the goal moves.

Usage:
    py scripts/lore/apply_death_legacy.py --deceased bardaglis --recipient character_c
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simulate_pass_lib as lib  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--deceased", required=True)
    parser.add_argument("--recipient", required=True)
    args = parser.parse_args()

    deceased_char = lib.load_char(args.deceased)
    deceased_arc = deceased_char.get("arc")
    if not deceased_arc:
        raise SystemExit(f"{args.deceased} has no arc on file - nothing to pass on.")

    recipient_char = lib.load_char(args.recipient)
    prev_arc = recipient_char.get("arc") or {}
    context = prev_arc.get("context")
    if not context:
        routines = recipient_char.get("routines", [])
        if routines:
            context = max(routines, key=lambda r: r.get("weight", 0))["context"]

    recipient_char["arc"] = {
        "about": list(deceased_arc.get("about", [])),
        "needs": list(deceased_arc.get("needs", [])),
        "context": context or deceased_arc.get("context"),
        "premise": deceased_arc.get("premise", ""),
        "resolution": "ongoing",
        "history": [],
    }
    lib.save_char(args.recipient, recipient_char)
    print(f"death-legacy applied: {args.deceased}'s arc -> {args.recipient}")


if __name__ == "__main__":
    main()
