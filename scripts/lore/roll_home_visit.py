"""
Roll which of the two participants is home this pass, before anything else about the scene gets
decided - a genuine dice roll, not a model's guess at whose "turn" it feels like. Design debrief
2026-08-28: replaces the old resolve_location.py, which used to derive home-turf-vs-visit by
comparing two INDEPENDENTLY rolled routines after the fact. Now the causality runs the other way -
home is decided first, and only the home participant ever rolls a routine (roll_routine.py); the
visiting participant simply enters whatever context the home participant's own roll produces. That
also retires the old "coincidence" mode entirely: with only one routine ever rolled per pass, there's
no second independent routine left for it to coincide with.

**Survival-weighted as of the survival-mechanism build (same day):** `--p1-choice`/`--p2-choice`
(survive|arc|none) are each participant's own roll_survival.py result for THIS pass, rolled before
this script runs - the hook this file's own prior version flagged ("stay home because leaving is a
risk to upkeep, or go because an arc's need outweighs that risk"). A participant who chose "survive"
skews the coin toward THEM being home (they want to stay and work, not travel); "arc" or "none"
(no ongoing arc to weigh in either direction) contributes no skew. If both leaned survive, or
neither did, the coin stays flat - there's no signal to break the tie with. Omit both flags (or pass
"none"/"none") for the old flat-coin behavior.

Never called at all when the pair was already fixed by a lead-override (forced_visit) - an unexpired
lead is a stronger, already-resolved signal than this roll, and always makes the lead's follower the
traveler outright (see simulate_pass_brief.py's own forced_visit branch).

Usage:
    py scripts/lore/roll_home_visit.py --p1 khaoe --p2 farlis
    py scripts/lore/roll_home_visit.py --p1 khaoe --p2 farlis --p1-choice survive --p2-choice arc
"""

import argparse
import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_SHIFT = tuning.load()["survival"]["home_visit_survival_shift"]
_MIN_ODDS, _MAX_ODDS = 2, 95


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--p1-choice", choices=["survive", "arc", "none"], default="none")
    parser.add_argument("--p2-choice", choices=["survive", "arc", "none"], default="none")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    # Odds that p1 is home, shifted toward whichever participant leaned "survive". If both (or
    # neither) leaned survive, this is a flat 50 and nothing below moves it.
    odds_p1_home = 50.0
    if args.p1_choice == "survive" and args.p2_choice != "survive":
        odds_p1_home += _SHIFT
    elif args.p2_choice == "survive" and args.p1_choice != "survive":
        odds_p1_home -= _SHIFT
    odds_p1_home = max(_MIN_ODDS, min(_MAX_ODDS, odds_p1_home))

    rng = Random(args.seed)
    home = args.p1 if rng.random() < (odds_p1_home / 100.0) else args.p2
    visiting = args.p2 if home == args.p1 else args.p1
    print(f"home: {home}")
    print(f"visiting: {visiting}")
    print(f"odds_p1_home: {odds_p1_home}")


if __name__ == "__main__":
    main()
