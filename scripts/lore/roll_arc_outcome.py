"""
Roll whether an arc's attempt this scene advances, stalls, or reverses - a genuine weighted dice
roll, not a model's narrative instinct. From the /simulate design debrief (2026-08-10): alignment
(check_arc_alignment.py) decides who's INCLINED to help or hinder; this script decides separately
whether it actually WORKS. Aligned intent shifts the odds, it doesn't decide the outcome outright -
an arc should be able to fail even with help, and survive even against hindrance, the same way a
criterion can resist a shock instead of always breaking.

`--contested` (design debrief 2026-08-28) extends the same philosophy with a second input: a rival's
prior claim shifts the odds further toward reverse, it never decides the outcome by itself either -
a contested arc should still be able to advance, the same way a helped one can still fail. Applied as
a fixed point-shift from advance to reverse (contested_outcome_shift, _lore/tuning.json), not a
second hardcoded weights table, so retuning it never means editing this file. Whether the visit was
even contested is decided upstream by roll_contested.py, independently - this script only ever reads
the result, never re-rolls it.

MUST run, and its result MUST be known, BEFORE the scene gets written - never the reverse. Rolling
after the fact and then writing dialogue to match risks nothing, but writing the scene first and
rolling after risks the roll contradicting what was already dramatized (a scene that reads as an
obvious win landing on "reverse"). The subagent's job is to dramatize a result that's already
decided, the same way it already dramatizes a criterion break or hold without deciding that itself
mid-scene - not to write freely and have the dice retroactively judge it.

Usage:
    py scripts/lore/roll_arc_outcome.py --inclined help
    py scripts/lore/roll_arc_outcome.py --inclined hinder --contested
    py scripts/lore/roll_arc_outcome.py --inclined neutral
    py scripts/lore/roll_arc_outcome.py --inclined mixed
"""

import argparse
import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

# (advance, stall, reverse) weights per inclination - aligned help/hinder shift the odds, never
# guarantee the result.
WEIGHTS = {
    "help": (60, 30, 10),
    "hinder": (15, 35, 50),
    "mixed": (35, 40, 25),
    "neutral": (40, 40, 20),
}

_CONTESTED_SHIFT = tuning.load()["contested_outcome_shift"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inclined", choices=list(WEIGHTS), required=True)
    parser.add_argument("--contested", action="store_true", help=f"Shifts {_CONTESTED_SHIFT} points from advance to reverse (contested_outcome_shift, _lore/tuning.json)")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    advance, stall, reverse = WEIGHTS[args.inclined]
    if args.contested:
        shift = min(advance, _CONTESTED_SHIFT)
        advance -= shift
        reverse += shift
    rng = Random(args.seed)
    outcome = rng.choices(["advance", "stall", "reverse"], weights=[advance, stall, reverse], k=1)[0]
    print(f"outcome: {outcome}")


if __name__ == "__main__":
    main()
