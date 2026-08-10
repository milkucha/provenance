"""
Roll whether an already-motivated visit (check_needs_provides.py already matched) is ALSO
contested by someone else's prior claim - a rare, genuine dice roll, not a model deciding a
complication would be dramatically convenient right now.

This is deliberately the only thing that gets rolled here. It does NOT decide who wins a contested
claim - that reuses the inclined value check_arc_alignment.py already computes for the help/hinder
question (see .claude/skills/simulate/SKILL.md's orchestration section for the fixed lookup table:
help -> visitor's claim wins, hinder -> the prior claim holds, mixed/neutral -> split or deferred).
Keeping the resolution as a lookup over an already-computed value, instead of a second free
judgment call, means nothing about a contested outcome is invented in the moment.

No persistent stock/inventory is tracked anywhere - "contested" is a fresh narrative fact each time
this rolls true, never a number that depletes. Same principle as hearsay: never verified or
reconciled against a ledger, just generated and played.

Default odds come from _lore/tuning.json (odds_percent.contested) - override with --odds only for a
one-off test, not to retune the mechanism (change the JSON file for that).

Usage:
    py scripts/lore/roll_contested.py [--odds 15]
"""

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_DEFAULT_ODDS = tuning.load()["odds_percent"]["contested"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--odds", type=float, default=_DEFAULT_ODDS, help=f"Percent chance of a contest firing (default {_DEFAULT_ODDS}, from _lore/tuning.json)")
    args = parser.parse_args()

    contested = random.random() < (args.odds / 100.0)
    print(f"contested: {'true' if contested else 'false'}")


if __name__ == "__main__":
    main()
