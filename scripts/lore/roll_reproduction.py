"""
Roll whether a pair that just became eligible for reproduction (design debrief, 2026-08-10:
partners[other] >= 5 shared scenes, neither on cooldown) actually reproduces this pass - a genuine
dice roll, not automatic the moment the threshold is crossed. "Rare, selected event" per the
original design sketch (TODO.md point 8): crossing the threshold makes it POSSIBLE, this decides
whether it actually happens right now.

Eligibility itself (the >=5 count, the 10-turn cooldown on each parent, the 10-turn cooldown before
a child enters pick_pair.py's pool) is plain arithmetic over already-known numbers - no roll needed
for that part, only for this one.

When it fires true and both parent keys are given, also rolls which parent's name leads the blend
(`name_lead`) - the model still composes the actual name (see generate_offspring.py's docstring for
why that one step can't be scripted), but it shouldn't also be the model's call which parent's name
starts the blend. That's exactly the kind of small residual choice this system keeps handing to
dice instead.

Default odds come from _lore/tuning.json (odds_percent.reproduction) - override with --odds only
for a one-off test, not to retune the mechanism (change the JSON file for that).

Usage:
    py scripts/lore/roll_reproduction.py [--odds 40]
    py scripts/lore/roll_reproduction.py --p1 khaoe --p2 gondarfolas
"""

import argparse
import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_DEFAULT_ODDS = tuning.load()["odds_percent"]["reproduction"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--odds", type=float, default=_DEFAULT_ODDS, help=f"Percent chance an eligible pair reproduces this pass (default {_DEFAULT_ODDS}, from _lore/tuning.json)")
    parser.add_argument("--p1", default=None, help="First parent key - only needed to also roll name_lead")
    parser.add_argument("--p2", default=None, help="Second parent key - only needed to also roll name_lead")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    rng = Random(args.seed)
    reproduces = rng.random() < (args.odds / 100.0)
    print(f"reproduces: {'true' if reproduces else 'false'}")
    if reproduces and args.p1 and args.p2:
        print(f"name_lead: {rng.choice([args.p1, args.p2])}")


if __name__ == "__main__":
    main()
