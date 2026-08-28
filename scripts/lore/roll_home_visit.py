"""
Roll which of the two participants is home this pass, before anything else about the scene gets
decided - a genuine dice roll, not a model's guess at whose "turn" it feels like. Design debrief
2026-08-28: replaces the old resolve_location.py, which used to derive home-turf-vs-visit by
comparing two INDEPENDENTLY rolled routines after the fact. Now the causality runs the other way -
home is decided first, and only the home participant ever rolls a routine (roll_routine.py); the
visiting participant simply enters whatever context the home participant's own roll produces. That
also retires the old "coincidence" mode entirely: with only one routine ever rolled per pass, there's
no second independent routine left for it to coincide with.

Flat 50/50 for now, on purpose - not yet weighted by anything. The user's stated intent is for a
not-yet-built survival-pressure mechanism to eventually pull this odds one way or another (stay home
because leaving is a risk to upkeep, or go because an arc's need outweighs that risk); until that
mechanism exists, don't fake it with a placeholder heuristic - a flat coin flip is the honest stand-in.
See TODO.md's "survival mechanism" entry for the hook this will eventually plug into.

Never called at all when the pair was already fixed by a lead-override (forced_visit) - an unexpired
lead is a stronger, already-resolved signal than this roll, and always makes the lead's follower the
traveler outright (see simulate_pass_brief.py's own forced_visit branch).

Usage:
    py scripts/lore/roll_home_visit.py --p1 khaoe --p2 farlis
"""

import argparse
import random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    args = parser.parse_args()

    home = random.choice([args.p1, args.p2])
    visiting = args.p2 if home == args.p1 else args.p1
    print(f"home: {home}")
    print(f"visiting: {visiting}")


if __name__ == "__main__":
    main()
