"""
Decide whose arc is primary this scene - a plain 50/50 mechanical draw between the two
participants, not a judgment call about whose project "makes more sense" to advance here.

Replaces the earlier host-only rule (only the scene's home_frame character's arc could ever
update) with a fair coin flip between whoever's actually in the scene, so a visitor's own arc gets
a genuine, unbiased chance to be the one engaged - decided 2026-08-10.

Usage:
    py scripts/lore/roll_arc_primacy.py --p1 kristok_jakur --p2 nerkeli
"""

import argparse
import random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    args = parser.parse_args()

    primary = random.choice([args.p1, args.p2])
    print(f"primary: {primary}")


if __name__ == "__main__":
    main()
