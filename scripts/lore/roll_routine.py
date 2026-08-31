"""
Roll which of a character's home routines they're in for this pass - a genuine weighted random
draw, not a model's guess at "which feels right this time" (same reasoning pick_pair.py already
gives for participant selection: a model asked to pick isn't a uniform/weighted random source).

Usage:
    py scripts/lore/roll_routine.py "City A:75" "Festival A:12.5" "Landmark A:12.5"
"""

import argparse
from random import Random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("routine", nargs="+", help='One or more "Name:Weight" pairs')
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible draw")
    args = parser.parse_args()

    names = []
    weights = []
    for entry in args.routine:
        name, _, weight = entry.rpartition(":")
        if not name:
            raise SystemExit(f"Malformed routine entry (expected Name:Weight): {entry!r}")
        names.append(name)
        weights.append(float(weight))

    rng = Random(args.seed)
    choice = rng.choices(names, weights=weights, k=1)[0]
    print(f"routine: {choice}")


if __name__ == "__main__":
    main()
