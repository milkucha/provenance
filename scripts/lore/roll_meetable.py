"""
Roll whether anyone worth meeting actually shows up once a character has arrived (or already was) at
a location that can satisfy their arc's need - the "missed connection" mechanic from the 2026-09-13
asymmetric per-pass design conversation (see TODO.md/CHRONICLE.md's matching entries). Two questions
in one call:

  1. **Does anyone useful show up at all?** A genuine, non-trivial chance of a miss -
     `arc_meetable_odds_percent` (`_lore/tuning.json`), not a near-certainty. Nobody being there this
     exact pass is a real, expected outcome, not an edge case.
  2. **If so, who?** A weighted draw over the candidate pool (every character with a routines[] entry
     at this location, per the caller). `--favor` names the known-supplier match (when
     `location_context.resolve_arc_target()`'s tier-3 lookup is the reason this location was even
     reached) - that person's weight is multiplied by `arc_match_boost_factor` over an ordinary
     candidate's, favoring them without ever guaranteeing they're the one drawn (same "skew, never
     decide" discipline as `roll_contested.py`'s relationship-aware shift, just multiplicative on a
     weighted-choice draw instead of additive on a percentage).

Caller's job, not this script's: if the candidate pool is empty entirely, that's an automatic miss
per the design conversation - don't call this script at all in that case, there is nothing to roll.

Usage:
    py scripts/lore/roll_meetable.py --candidates farlis nerkeli
    py scripts/lore/roll_meetable.py --candidates farlis nerkeli khaoe --favor khaoe
"""

import argparse
import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_T = tuning.load()
_DEFAULT_ODDS = _T["arc_meetable_odds_percent"]
_DEFAULT_BOOST = _T["arc_match_boost_factor"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidates", nargs="+", required=True, help="Every character slug present at this location with a matching routine")
    parser.add_argument("--favor", default=None, help="The known-supplier slug (resolve_arc_target's tier-3 match), if any, to weight up")
    parser.add_argument("--odds", type=float, default=_DEFAULT_ODDS, help=f"Percent chance someone useful shows up at all (default {_DEFAULT_ODDS}, from _lore/tuning.json)")
    parser.add_argument("--boost", type=float, default=_DEFAULT_BOOST, help=f"Weight multiplier for --favor over an ordinary candidate (default {_DEFAULT_BOOST}, from _lore/tuning.json)")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    candidates = list(dict.fromkeys(args.candidates))
    rng = Random(args.seed)

    met = rng.random() < (args.odds / 100.0)
    print(f"met: {'true' if met else 'false'}")
    print(f"odds_used: {args.odds}")
    if not met:
        return

    weights = [args.boost if c == args.favor else 1.0 for c in candidates]
    chosen = rng.choices(candidates, weights=weights, k=1)[0]
    print(f"chosen: {chosen}")


if __name__ == "__main__":
    main()
