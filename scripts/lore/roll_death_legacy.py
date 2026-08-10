"""
Roll whether a character who died early passes their arc on to one of their close people - design
debrief 2026-08-10. Deliberately reuses record_death.py's own notified-circle output as the
candidate pool rather than computing a separate "close" definition - those are already the people
who share scenes with the deceased, per the existing 30%-of-circle sampling logic.

"Early" is decided by the caller, not this script: horizon.py's band can only ever read
`established` or `late` at the exact pass death fires (a rolled span can never sit below the
world-normal range's floor, so `early` is structurally impossible at death) - so "died early" means
band == "established" rather than "late" at that pass. Check that first; only call this script if
it's true.

A legacy arc isn't a fresh derivation for the recipient - the about/needs tags carry over from the
deceased's own arc directly (same mechanical copy the transform mechanism already uses, see
check_arc_alignment.py's matched_about output), and the recipient's own `resolution` resets to
"ongoing" the same way a transform does. Their `archetype`/routine stays their own; only the goal
moves.

Default odds come from _lore/tuning.json (odds_percent.death_legacy) - override with --odds only
for a one-off test, not to retune the mechanism (change the JSON file for that).

Usage:
    py scripts/lore/roll_death_legacy.py --candidates bardaglis farlis nuvilo [--odds 40]
    py scripts/lore/roll_death_legacy.py --candidates bardaglis   # single candidate is still a roll, not automatic
"""

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_DEFAULT_ODDS = tuning.load()["odds_percent"]["death_legacy"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidates", nargs="+", required=True, help="Notified-circle keys, from record_death.py's own output")
    parser.add_argument("--odds", type=float, default=_DEFAULT_ODDS, help=f"Percent chance the arc passes on at all (default {_DEFAULT_ODDS}, from _lore/tuning.json)")
    args = parser.parse_args()

    if random.random() < (args.odds / 100.0):
        recipient = random.choice(args.candidates)
        print("passes: true")
        print(f"recipient: {recipient}")
    else:
        print("passes: false")


if __name__ == "__main__":
    main()
