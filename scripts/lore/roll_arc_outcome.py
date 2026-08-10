"""
Roll whether an arc's attempt this scene advances, stalls, or reverses - a genuine weighted dice
roll, not a model's narrative instinct. From the /simulate design debrief (2026-08-10): alignment
(check_arc_alignment.py) decides who's INCLINED to help or hinder; this script decides separately
whether it actually WORKS. Aligned intent shifts the odds, it doesn't decide the outcome outright -
an arc should be able to fail even with help, and survive even against hindrance, the same way a
criterion can resist a shock instead of always breaking.

MUST run, and its result MUST be known, BEFORE the scene gets written - never the reverse. Rolling
after the fact and then writing dialogue to match risks nothing, but writing the scene first and
rolling after risks the roll contradicting what was already dramatized (a scene that reads as an
obvious win landing on "reverse"). The subagent's job is to dramatize a result that's already
decided, the same way it already dramatizes a criterion break or hold without deciding that itself
mid-scene - not to write freely and have the dice retroactively judge it.

Usage:
    py scripts/lore/roll_arc_outcome.py --inclined help
    py scripts/lore/roll_arc_outcome.py --inclined hinder
    py scripts/lore/roll_arc_outcome.py --inclined neutral
    py scripts/lore/roll_arc_outcome.py --inclined mixed
"""

import argparse
import random

# (advance, stall, reverse) weights per inclination - aligned help/hinder shift the odds, never
# guarantee the result.
WEIGHTS = {
    "help": (60, 30, 10),
    "hinder": (15, 35, 50),
    "mixed": (35, 40, 25),
    "neutral": (40, 40, 20),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inclined", choices=list(WEIGHTS), required=True)
    args = parser.parse_args()

    advance, stall, reverse = WEIGHTS[args.inclined]
    outcome = random.choices(["advance", "stall", "reverse"], weights=[advance, stall, reverse], k=1)[0]
    print(f"outcome: {outcome}")


if __name__ == "__main__":
    main()
